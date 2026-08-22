#!/usr/bin/env python3
"""
Sync Cloudinary Event Mapping

This script compares the cloudinary_event_mapping.json file with all folders 
and files in the cloudinary folder (and subfolders) and updates missing entries.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
import cloudinary
import cloudinary.api

# Configuration
CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME', 'du0lumtob')
MAPPING_FILE = "cloudinary_event_mapping.json"
CLOUDINARY_FOLDER_PREFIX = "archived-events"


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


def fetch_all_cloudinary_folders():
    """Fetch all subfolders in the archived-events folder from Cloudinary."""
    print(f"\n📂 Fetching all folders from Cloudinary prefix: {CLOUDINARY_FOLDER_PREFIX}...")
    
    try:
        folders_data = {}
        next_cursor = None
        all_resources = []
        
        # Fetch all resources in the archived-events prefix
        while True:
            result = cloudinary.api.resources(
                type="upload",
                prefix=CLOUDINARY_FOLDER_PREFIX,
                max_results=500,
                next_cursor=next_cursor
            )
            
            all_resources.extend(result.get('resources', []))
            next_cursor = result.get('next_cursor')
            
            if not next_cursor:
                break
        
        # Extract unique folders from the resource paths
        for resource in all_resources:
            # Extract folder path from the resource path
            # Format: archived-events/folder-name/filename
            parts = resource['public_id'].split('/')
            
            if len(parts) >= 2:
                folder_name = parts[1]
                folder_path = f"{CLOUDINARY_FOLDER_PREFIX}/{folder_name}"
                
                if folder_name not in folders_data:
                    # Count all resources in this folder
                    resource_count = sum(
                        1 for r in all_resources 
                        if r['public_id'].startswith(f"{folder_path}/")
                    )
                    
                    folders_data[folder_name] = {
                        'path': folder_path,
                        'resource_count': resource_count
                    }
        
        print(f"   ✅ Found {len(folders_data)} folders in Cloudinary")
        return folders_data
    
    except Exception as e:
        print(f"❌ Error fetching folders from Cloudinary: {str(e)}")
        sys.exit(1)


def fetch_resources_for_folder(folder_path):
    """Fetch all resources (files) in a specific Cloudinary folder."""
    try:
        resources = []
        next_cursor = None
        
        while True:
            result = cloudinary.api.resources(
                type="upload",
                prefix=folder_path,
                max_results=500,
                next_cursor=next_cursor
            )
            
            resources.extend(result.get('resources', []))
            next_cursor = result.get('next_cursor')
            
            if not next_cursor:
                break
        
        return [resource['secure_url'] for resource in resources]
    
    except Exception as e:
        print(f"   ⚠️  Error fetching resources for {folder_path}: {str(e)}")
        return []


def load_existing_mapping():
    """Load existing event mapping from JSON file."""
    print(f"\n📖 Loading existing mapping from {MAPPING_FILE}...")
    
    try:
        with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
            events = json.load(f)
        print(f"   ✅ Loaded {len(events)} existing events")
        return events
    
    except FileNotFoundError:
        print(f"   ⚠️  {MAPPING_FILE} not found, starting with empty list")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing {MAPPING_FILE}: {str(e)}")
        sys.exit(1)


def get_mapped_folders(events):
    """Extract all cloudinary folders already mapped in the JSON."""
    mapped_folders = set()
    for event in events:
        if 'cloudinary_folder' in event:
            mapped_folders.add(event['cloudinary_folder'])
    return mapped_folders


def create_entry_from_folder(folder_name, folder_path, resources):
    """Create a new event entry for an unmapped folder."""
    event_id = str(int(datetime.now().timestamp() * 1000))
    
    folder_url = f"https://res.cloudinary.com/{CLOUDINARY_CLOUD_NAME}/image/upload/{folder_path}/"
    
    entry = {
        "event_id": event_id,
        "event_name": folder_name.replace('-', ' '),
        "event_date": datetime.now().strftime("%Y-%m-%d"),
        "cloudinary_folder": folder_name,
        "photo_count": len(resources),
        "cloudinary_urls": resources,
        "folder_url": folder_url
    }
    
    return entry


def find_missing_entries(cloudinary_folders, mapped_folders):
    """Find folders in Cloudinary that are not in the mapping JSON."""
    missing = {}
    for folder_name in cloudinary_folders:
        if folder_name not in mapped_folders:
            missing[folder_name] = cloudinary_folders[folder_name]
    return missing


def update_mapping_file(events):
    """Save updated events to the mapping JSON file."""
    print(f"\n💾 Saving updated mapping to {MAPPING_FILE}...")
    
    # Sort events by date (newest first)
    events.sort(key=lambda x: x.get('event_date', ''), reverse=True)
    
    # Save to file
    with open(MAPPING_FILE, 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ Saved {len(events)} events to {MAPPING_FILE}")


def main():
    """Main execution function."""
    print("="*70)
    print("🔄 Sync Cloudinary Event Mapping")
    print("="*70)
    
    # Connect to Cloudinary
    connect_cloudinary()
    
    # Fetch all folders from Cloudinary
    cloudinary_folders = fetch_all_cloudinary_folders()
    
    # Load existing mapping
    existing_events = load_existing_mapping()
    mapped_folders = get_mapped_folders(existing_events)
    
    # Find missing folders
    missing_folders = find_missing_entries(cloudinary_folders, mapped_folders)
    
    if not missing_folders:
        print("\n✅ All Cloudinary folders are already mapped!")
        print(f"   Total events in mapping: {len(existing_events)}")
        return
    
    print(f"\n🔍 Found {len(missing_folders)} unmapped folder(s):")
    for folder_name in sorted(missing_folders.keys()):
        resource_count = missing_folders[folder_name]['resource_count']
        print(f"   • {folder_name} ({resource_count} resources)")
    
    # Auto-proceed with adding entries (non-interactive mode)
    print(f"\n✅ Automatically adding {len(missing_folders)} new entry/entries to the mapping...")
    
    # Process missing folders
    new_entries = []
    print(f"\n⏳ Processing {len(missing_folders)} unmapped folder(s)...")
    
    for idx, (folder_name, folder_info) in enumerate(sorted(missing_folders.items()), 1):
        folder_path = folder_info['path']
        print(f"\n   [{idx}/{len(missing_folders)}] Processing: {folder_name}")
        
        # Fetch all resources for this folder
        resources = fetch_resources_for_folder(folder_path)
        
        if resources:
            # Create new entry
            new_entry = create_entry_from_folder(folder_name, folder_path, resources)
            new_entries.append(new_entry)
            print(f"       ✅ Added {len(resources)} resource(s)")
        else:
            print(f"       ⚠️  No resources found, skipping")
    
    if new_entries:
        # Add new entries to existing events
        existing_events.extend(new_entries)
        
        # Update the mapping file
        update_mapping_file(existing_events)
        
        print("\n" + "="*70)
        print(f"✅ Successfully added {len(new_entries)} new entry/entries!")
        print("="*70)
        print(f"\nSummary:")
        print(f"   📊 New entries added: {len(new_entries)}")
        print(f"   📊 Total events now: {len(existing_events)}")
        
        print(f"\n📝 New entries added:")
        for entry in new_entries:
            print(f"   • {entry['event_name']} ({entry['photo_count']} photos)")
    else:
        print("\n⚠️  No new entries could be created")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()
