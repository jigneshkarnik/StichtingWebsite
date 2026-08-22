#!/usr/bin/env python3
"""
Sync Cloudinary Event Mapping - FIXED VERSION

Uses Cloudinary REST API with urllib (built-in) to fetch ACCURATE image counts.
Reads total_count from API response instead of counting returned URLs.
"""

import json
import os
import sys
import base64
import time
from urllib import request
from urllib.error import HTTPError
from datetime import datetime

# Configuration
CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME', 'du0lumtob')
CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')
MAPPING_FILE = "cloudinary_event_mapping.json"


def get_auth_header():
    """Return Authorization header for Cloudinary API."""
    if not CLOUDINARY_API_KEY or not CLOUDINARY_API_SECRET:
        print("❌ Missing Cloudinary credentials in environment variables")
        print("   Required: CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET")
        sys.exit(1)
    
    credentials = f"{CLOUDINARY_API_KEY}:{CLOUDINARY_API_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"


def api_request(url, max_retries=5):
    """Make HTTP request to Cloudinary API with retry logic."""
    auth_header = get_auth_header()
    headers = {
        'Authorization': auth_header,
        'Content-Type': 'application/json'
    }
    
    for attempt in range(max_retries):
        try:
            req = request.Request(url, headers=headers)
            with request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                return data
        except HTTPError as e:
            if e.code == 420:
                if attempt < max_retries - 1:
                    wait_time = 30 * (attempt + 1)
                    print(f"   ⚠️  Rate limited. Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"   ❌ Rate limited after {max_retries} retries")
                    return None
            else:
                print(f"   ❌ HTTP Error {e.code}: {e.reason}")
                return None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None
    
    return None


def fetch_folders_with_ids():
    """Fetch all subfolders in archived-events with their external IDs."""
    print("\n📂 Fetching all subfolders with IDs from archived-events...")
    
    url = f"https://api.cloudinary.com/v1_1/{CLOUDINARY_CLOUD_NAME}/folders/archived-events"
    
    data = api_request(url)
    if not data:
        return []
    
    folders = data.get('folders', [])
    print(f"✅ Found {len(folders)} subfolders")
    return folders


def get_folder_resources_count(external_id):
    """
    Fetch total resource count for a folder using folder_id query.
    Returns: total_count (using API's total_count field, not counted URLs)
    """
    url = f"https://api.cloudinary.com/v1_1/{CLOUDINARY_CLOUD_NAME}/resources/search?query=folder_id:{external_id}&max_results=1"
    
    data = api_request(url)
    if not data:
        return 0
    
    # CRITICAL: Use total_count from API response, NOT the returned URLs
    total_count = data.get('total_count', 0)
    
    return total_count


def load_existing_mapping():
    """Load existing mapping from JSON."""
    try:
        with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


def create_entry(folder_name, folder_path, external_id, total_count):
    """Create a mapping entry for a folder."""
    # Try to extract date from folder name
    event_date = ""
    
    # Parse date patterns like "2024-02-", "2025-01-", etc.
    for word in folder_name.split('-'):
        if len(word) == 4 and word.isdigit():  # Year
            event_date = word
            break
    
    entry = {
        'event_id': external_id,
        'event_name': folder_name,
        'event_date': event_date,
        'cloudinary_folder': folder_name,
        'photo_count': total_count,
        'cloudinary_urls': [],  # Empty - we only store counts now
        'folder_url': f"https://console.cloudinary.com/console/c-{CLOUDINARY_CLOUD_NAME}/media_library/folders/{folder_path}"
    }
    
    return entry


def main():
    """Main execution function."""
    print("="*70)
    print("🔄 Sync Cloudinary Event Mapping (ACCURATE COUNTS)")
    print("="*70)
    
    # Fetch all folders
    folders = fetch_folders_with_ids()
    if not folders:
        print("❌ No folders found")
        return
    
    print(f"\n📂 Fetching resource counts using folder IDs...\n")
    
    entries = []
    total_images = 0
    empty_folders = []
    
    for idx, folder in enumerate(folders, 1):
        folder_name = folder.get('name', '')
        folder_path = folder.get('path', '')
        external_id = folder.get('external_id', '')
        
        # Fetch resource COUNT for this folder using API's total_count
        total_count = get_folder_resources_count(external_id)
        
        # Create entry
        entry = create_entry(folder_name, folder_path, external_id, total_count)
        entries.append(entry)
        
        total_images += total_count
        
        # Status indicator
        status = "❌" if total_count == 0 else "✅"
        folder_display = folder_name[:50] if len(folder_name) <= 50 else folder_name[:47] + "..."
        print(f"[{idx:2d}/{len(folders)}] {folder_display:<50} {status} {total_count:5d} images")
        
        if total_count == 0:
            empty_folders.append(folder_name)
    
    # Save to JSON
    print(f"\n💾 Saving mapping to {MAPPING_FILE}...")
    with open(MAPPING_FILE, 'w', encoding='utf-8') as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
    
    # Summary
    print("\n" + "="*70)
    print("✅ Accurate mapping saved!")
    print("="*70)
    print(f"📊 Summary:")
    print(f"   • Total folders: {len(entries)}")
    print(f"   • Total images: {total_images}")
    print(f"   • Empty folders: {len(empty_folders)}")
    
    if empty_folders:
        print(f"\n📂 Empty folders ({len(empty_folders)} total):")
        for folder in empty_folders:
            print(f"   • {folder}")
    
    print("="*70)


if __name__ == "__main__":
    main()

