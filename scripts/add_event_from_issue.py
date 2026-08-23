#!/usr/bin/env python3
"""
Add Event from GitHub Issue

Parses a GitHub issue (created from the "Add New Event" template),
fetches all photos from the named Cloudinary folder, and updates:
  - events_data.json          (source-of-truth list used by sync scripts)
  - cloudinary_event_mapping.json  (gallery mapping with full URL list)
  - events.html               (re-embeds the updated mapping JSON)

Run by GitHub Actions when the `new-event` label is applied to an issue.
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
import cloudinary
import cloudinary.api

CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME', 'du0lumtob')
MAPPING_FILE = "cloudinary_event_mapping.json"
EVENTS_DATA_FILE = "events_data.json"
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def _field(issue_body, label):
    """Extract the value following a GitHub Forms field heading."""
    m = re.search(
        rf'###\s+{re.escape(label)}\s*\n+([^\n#][^\n]*(?:\n(?!###)[^\n]*)*)',
        issue_body
    )
    if not m:
        return None
    value = m.group(1).strip()
    if value.lower() in ('no response', '_no response_', ''):
        return None
    return value


def parse_issue_body(issue_body):
    print("📋 Parsing issue body...")

    data = {
        'event_name':        _field(issue_body, 'Event Name'),
        'cloudinary_folder': _field(issue_body, 'Cloudinary Folder Name'),
        'event_date':        _field(issue_body, 'Event Date'),
        'event_time':        _field(issue_body, 'Event Time'),
        'venue':             _field(issue_body, 'Venue / Location'),
        'description':       _field(issue_body, 'Short Description'),
        'img1':              _field(issue_body, 'Hero Image (img1)'),
        'img2':              _field(issue_body, 'Second Image (img2)'),
        'img3':              _field(issue_body, 'Third Image (img3)'),
    }

    required = ['event_name', 'cloudinary_folder', 'event_date', 'venue', 'description', 'img1']
    missing = [f for f in required if not data.get(f)]
    if missing:
        print(f"❌ Missing required fields: {', '.join(missing)}")
        sys.exit(1)

    for k, v in data.items():
        if v:
            print(f"   ✅ {k}: {v[:80]}")

    return data


# ---------------------------------------------------------------------------
# Cloudinary
# ---------------------------------------------------------------------------

def connect_cloudinary():
    print("\n🔌 Connecting to Cloudinary...")
    api_key    = os.environ.get('CLOUDINARY_API_KEY')
    api_secret = os.environ.get('CLOUDINARY_API_SECRET')
    if not api_key or not api_secret:
        print("❌ Missing CLOUDINARY_API_KEY / CLOUDINARY_API_SECRET")
        sys.exit(1)
    cloudinary.config(cloud_name=CLOUDINARY_CLOUD_NAME,
                      api_key=api_key, api_secret=api_secret, secure=True)
    print(f"   ✅ Connected (cloud: {CLOUDINARY_CLOUD_NAME})")


def fetch_cloudinary_photos(folder_name):
    print(f"\n📸 Fetching photos from archived-events/{folder_name} …")
    full_path = f"archived-events/{folder_name}"
    resources, cursor = [], None
    while True:
        kwargs = dict(type="upload", prefix=full_path, max_results=500)
        if cursor:
            kwargs['next_cursor'] = cursor
        result = cloudinary.api.resources(**kwargs)
        resources.extend(result.get('resources', []))
        cursor = result.get('next_cursor')
        if not cursor:
            break

    if not resources:
        print(f"❌ No photos found in {full_path} — check the folder name")
        sys.exit(1)

    urls = [r['secure_url'] for r in resources]
    print(f"   ✅ {len(urls)} photos found")
    return urls, full_path


# ---------------------------------------------------------------------------
# File updates
# ---------------------------------------------------------------------------

def next_sno(events):
    """Return max Sno + 1 (or 1 if list is empty)."""
    if not events:
        return 1
    return max((e.get('Sno', 0) for e in events), default=0) + 1


def update_events_data(data, photo_urls):
    print(f"\n📝 Updating {EVENTS_DATA_FILE} …")
    try:
        with open(EVENTS_DATA_FILE, encoding='utf-8') as f:
            events = json.load(f)
        print(f"   Loaded {len(events)} existing entries")
    except FileNotFoundError:
        events = []

    # Avoid duplicates: check if folder already present
    folder = data['cloudinary_folder']
    for e in events:
        for img_key in ('img1', 'img2', 'img3'):
            url = e.get(img_key, '')
            if url and folder in url:
                print(f"   ⚠️  Folder already in events_data.json (Sno {e['Sno']}) — skipping")
                return events

    new_entry = {
        "Sno":   next_sno(events),
        "date":  data['event_date'],
        "Year":  int(data['event_date'][:4]),
        "name":  data['event_name'],
        "img1":  data['img1'],
        "img2":  data.get('img2') or photo_urls[1] if len(photo_urls) > 1 else data['img1'],
        "img3":  data.get('img3') or photo_urls[2] if len(photo_urls) > 2 else data['img1'],
        "venue": data['venue'],
        "desc":  data['description'],
    }
    if data.get('event_time'):
        new_entry['time'] = data['event_time']

    events.append(new_entry)
    # Keep sorted newest-first by date string
    events.sort(key=lambda x: str(x.get('date', '')), reverse=True)

    with open(EVENTS_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    print(f"   ✅ Saved {len(events)} entries (new Sno: {new_entry['Sno']})")
    return events


def update_mapping(data, photo_urls, folder_path):
    print(f"\n📝 Updating {MAPPING_FILE} …")
    try:
        with open(MAPPING_FILE, encoding='utf-8') as f:
            mapping = json.load(f)
        print(f"   Loaded {len(mapping)} existing events")
    except FileNotFoundError:
        mapping = []

    folder = data['cloudinary_folder']

    # Avoid duplicates
    for e in mapping:
        if e.get('cloudinary_folder') == folder:
            print(f"   ⚠️  Folder already in mapping — skipping")
            return mapping

    # Hero image first, then remaining gallery images
    hero = data['img1']
    rest = [u for u in photo_urls if u != hero]
    all_urls = [hero] + rest

    event_id = str(int(datetime.now().timestamp()))
    entry = {
        "event_id":          event_id,
        "event_name":        data['event_name'],
        "event_name_ref":    data['event_name'],
        "event_date":        data['event_date'],
        "venue":             data['venue'],
        "description":       data['description'],
        "cloudinary_folder": folder,
        "photo_count":       len(all_urls),
        "cloudinary_urls":   all_urls,
        "folder_url":        f"https://res.cloudinary.com/{CLOUDINARY_CLOUD_NAME}/image/upload/{folder_path}/",
        "event_details":     {},
    }
    if data.get('event_time'):
        entry['event_time'] = data['event_time']

    # Prepend so it appears first (newest)
    mapping.insert(0, entry)

    with open(MAPPING_FILE, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)
    print(f"   ✅ Saved {len(mapping)} events (new event_id: {event_id})")
    return mapping


def rebuild_events_html():
    print(f"\n⚡ Rebuilding events.html …")
    script = os.path.join(SCRIPTS_DIR, 'update_events_html.py')
    result = subprocess.run([sys.executable, script], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"   ❌ update_events_html.py failed:\n{result.stderr}")
        sys.exit(1)
    for line in result.stdout.splitlines():
        print(f"   {line}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("🚀 Add Event from GitHub Issue")
    print("=" * 70)

    issue_body = os.environ.get('ISSUE_BODY', '')
    if not issue_body:
        print("❌ ISSUE_BODY environment variable is not set")
        sys.exit(1)

    data = parse_issue_body(issue_body)
    connect_cloudinary()
    photo_urls, folder_path = fetch_cloudinary_photos(data['cloudinary_folder'])

    update_events_data(data, photo_urls)
    update_mapping(data, photo_urls, folder_path)
    rebuild_events_html()

    print("\n" + "=" * 70)
    print("✅ Done!")
    print("=" * 70)
    print(f"\n   📌 {data['event_name']}")
    print(f"   📅 {data['event_date']}  📍 {data['venue']}")
    print(f"   📷 {len(photo_urls)} photos")
    print("\n📁 Files updated:")
    print(f"   • {EVENTS_DATA_FILE}")
    print(f"   • {MAPPING_FILE}")
    print(f"   • events.html")
    print("\n🎉 PR is ready for review!")
    print("=" * 70)


if __name__ == "__main__":
    main()



def parse_issue_body(issue_body):
    """Parse the GitHub issue body to extract event details."""
    print("📋 Parsing issue body...")
    
    # Patterns to match form fields
    patterns = {
        'event_name': r'### Event Name\s*\n\s*(.+)',
        'location': r'### Location\s*\n\s*(.+)',
        'event_date': r'### Event Date\s*\n\s*(.+)',
        'cloudinary_folder': r'### Cloudinary Folder Name\s*\n\s*(.+)',
        'photo_count': r'### Number of Photos\s*\n\s*(.+)',
        'video_links': r'### Video Links \(Optional\)\s*\n\s*(.+?)(?=\n###|\Z)',
    }
    
    event_data = {}
    
    for key, pattern in patterns.items():
        match = re.search(pattern, issue_body, re.MULTILINE | re.DOTALL)
        if match:
            value = match.group(1).strip()
            # Handle "No response" or "_No response_" placeholders
            if value.lower() in ['no response', '_no response_', '']:
                event_data[key] = None
            else:
                event_data[key] = value
        else:
            event_data[key] = None
    
    # Validate required fields
    required_fields = ['event_name', 'location', 'event_date', 'cloudinary_folder']
    missing_fields = [f for f in required_fields if not event_data.get(f)]
    
    if missing_fields:
        print(f"❌ Missing required fields: {', '.join(missing_fields)}")
        sys.exit(1)
    
    print(f"   ✅ Event Name: {event_data['event_name']}")
    print(f"   ✅ Location: {event_data['location']}")
    print(f"   ✅ Event Date: {event_data['event_date']}")
    print(f"   ✅ Cloudinary Folder: {event_data['cloudinary_folder']}")
    
    return event_data


def connect_cloudinary():
    """Initialize Cloudinary connection using environment variables."""
    print("\n🔌 Connecting to Cloudinary...")
    
    api_key = os.environ.get('CLOUDINARY_API_KEY')
    api_secret = os.environ.get('CLOUDINARY_API_SECRET')
    
    if not api_key or not api_secret:
        print("❌ Missing Cloudinary credentials in environment variables")
        print("   Required: CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET")
        sys.exit(1)
    
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=api_key,
        api_secret=api_secret,
        secure=True
    )
    
    print(f"   ✅ Connected to Cloudinary (Cloud: {CLOUDINARY_CLOUD_NAME})")


def fetch_cloudinary_photos(folder_name):
    """Fetch all photos from the specified Cloudinary folder."""
    print(f"\n📸 Fetching photos from Cloudinary folder...")
    
    # Add archived-events prefix
    full_folder_path = f"archived-events/{folder_name}"
    
    try:
        # Fetch resources from folder with pagination
        resources = []
        next_cursor = None
        
        while True:
            result = cloudinary.api.resources(
                type="upload",
                prefix=full_folder_path,
                max_results=500,
                next_cursor=next_cursor
            )
            
            resources.extend(result.get('resources', []))
            next_cursor = result.get('next_cursor')
            
            if not next_cursor:
                break
        
        if not resources:
            print(f"❌ No photos found in folder: {full_folder_path}")
            print(f"   Please verify the folder exists in Cloudinary")
            sys.exit(1)
        
        # Extract secure URLs
        photo_urls = [resource['secure_url'] for resource in resources]
        
        print(f"   ✅ Found {len(photo_urls)} photos in {full_folder_path}")
        
        return photo_urls, full_folder_path
    
    except Exception as e:
        print(f"❌ Error fetching photos from Cloudinary: {str(e)}")
        sys.exit(1)


def parse_video_links(video_text):
    """Parse video links from the text, one per line."""
    if not video_text:
        return []
    
    # Split by newlines and filter out empty lines
    links = [line.strip() for line in video_text.split('\n') if line.strip()]
    
    # Filter valid URLs (basic validation)
    valid_links = [
        link for link in links 
        if link.startswith('http://') or link.startswith('https://')
    ]
    
    return valid_links


def create_event_entry(event_data, photo_urls, folder_path):
    """Create a new event entry for the mapping file."""
    print("\n🆕 Creating event entry...")
    
    # Generate unique event ID based on timestamp
    event_id = str(int(datetime.now().timestamp()))
    
    # Parse video links
    video_links = parse_video_links(event_data.get('video_links'))
    
    # Build folder URL
    folder_url = f"https://res.cloudinary.com/{CLOUDINARY_CLOUD_NAME}/image/upload/{folder_path}/"
    
    # Create event entry
    event_entry = {
        "event_id": event_id,
        "event_name": event_data['event_name'],
        "event_date": event_data['event_date'],
        "cloudinary_folder": event_data['cloudinary_folder'],
        "photo_count": len(photo_urls),
        "cloudinary_urls": photo_urls,
        "folder_url": folder_url
    }
    
    # Add video links if present
    if video_links:
        event_entry["video_links"] = video_links
        print(f"   ✅ Added {len(video_links)} video link(s)")
    
    print(f"   ✅ Event ID: {event_id}")
    print(f"   ✅ Photo Count: {len(photo_urls)}")
    
    return event_entry


def update_mapping_file(new_event):
    """Update the cloudinary_event_mapping.json file with the new event."""
    print(f"\n📝 Updating {MAPPING_FILE}...")
    
    # Load existing mapping
    try:
        with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
            events = json.load(f)
        print(f"   ✅ Loaded {len(events)} existing events")
    except FileNotFoundError:
        print(f"   ⚠️  {MAPPING_FILE} not found, creating new file")
        events = []
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing {MAPPING_FILE}: {str(e)}")
        sys.exit(1)
    
    # Add new event
    events.append(new_event)
    
    # Sort events by date (newest first)
    # Note: Dates are in YYYY-MM-DD format which sorts correctly as strings
    events.sort(key=lambda x: x['event_date'], reverse=True)
    print(f"   ✅ Events sorted by date (newest first)")
    
    # Save updated mapping
    with open(MAPPING_FILE, 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ Saved {len(events)} events to {MAPPING_FILE}")


def update_gallery_js(events):
    """Update gallery.js with the new event mapping.
    
    This function finds the EVENT_MAPPING constant and replaces its value.
    The pattern expects: const EVENT_MAPPING = [...];
    """
    print(f"\n⚡ Updating {GALLERY_JS_FILE}...")
    
    try:
        with open(GALLERY_JS_FILE, 'r', encoding='utf-8') as f:
            js_content = f.read()
    except FileNotFoundError:
        print(f"❌ {GALLERY_JS_FILE} not found")
        sys.exit(1)
    
    # Find the EVENT_MAPPING constant and replace its value
    # Pattern matches: const EVENT_MAPPING = [...];
    # Note: This assumes the constant is declared in this exact format
    pattern = r'(const EVENT_MAPPING = )\[.*?\];'
    
    # Create the new mapping value
    new_mapping = json.dumps(events, indent=2)
    replacement = f'\\1{new_mapping};'
    
    # Replace in the file
    updated_content = re.sub(
        pattern,
        replacement,
        js_content,
        flags=re.DOTALL
    )
    
    if updated_content == js_content:
        print(f"   ⚠️  EVENT_MAPPING constant not found in {GALLERY_JS_FILE}")
        print(f"   The file may need manual update")
    else:
        with open(GALLERY_JS_FILE, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print(f"   ✅ Updated EVENT_MAPPING in {GALLERY_JS_FILE}")


def main():
    """Main execution function."""
    print("="*70)
    print("🚀 Add Event from GitHub Issue")
    print("="*70)
    
    # Get issue body from environment variable (set by GitHub Actions)
    issue_body = os.environ.get('ISSUE_BODY', '')
    
    if not issue_body:
        print("❌ ISSUE_BODY environment variable not set")
        print("   This script should be run by GitHub Actions")
        sys.exit(1)
    
    # Parse issue
    event_data = parse_issue_body(issue_body)
    
    # Connect to Cloudinary
    connect_cloudinary()
    
    # Fetch photos
    photo_urls, folder_path = fetch_cloudinary_photos(event_data['cloudinary_folder'])
    
    # Create event entry
    new_event = create_event_entry(event_data, photo_urls, folder_path)
    
    # Update mapping file
    update_mapping_file(new_event)
    
    # Load updated events for gallery.js
    with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
        all_events = json.load(f)
    
    # Update gallery.js
    update_gallery_js(all_events)
    
    print("\n" + "="*70)
    print("✅ Event added successfully!")
    print("="*70)
    print(f"\nEvent Details:")
    print(f"   📌 Event: {new_event['event_name']}")
    print(f"   📅 Date: {new_event['event_date']}")
    print(f"   📷 Photos: {new_event['photo_count']}")
    print(f"   🆔 ID: {new_event['event_id']}")
    
    if 'video_links' in new_event:
        print(f"   🎥 Videos: {len(new_event['video_links'])}")
    
    print("\n📁 Files Updated:")
    print(f"   • {MAPPING_FILE}")
    print(f"   • {GALLERY_JS_FILE}")
    
    print("\n🎉 Ready to commit and create PR!")
    print("="*70)


if __name__ == "__main__":
    main()
