#!/usr/bin/env python3
"""
Create enhanced Cloudinary event mapping JSON
Combines folder structure with event details from reference JSON
"""

import json
import re
from collections import defaultdict
from datetime import datetime

# Load reference events JSON
with open('/Users/jigneshkarnik/Downloads/SSS_EVENTS_2022_2026.json', 'r') as f:
    reference_events = json.load(f)

# Load cloudinary folder list
with open('cloudinary_event_mapping.json', 'r') as f:
    cloudinary_folders = json.load(f)

# Load image links
with open('folder_images.txt', 'r') as f:
    image_links = [line.strip() for line in f if line.strip()]

print(f"📊 Loaded {len(reference_events)} reference events")
print(f"📊 Loaded {len(cloudinary_folders)} Cloudinary folders")
print(f"📊 Loaded {len(image_links)} image links\n")

# Extract folder paths from image links
folder_images = defaultdict(list)
for link in image_links:
    # Match: /archived-events/FOLDER_NAME/
    match = re.search(r'/archived-events/([^/]+)/', link)
    if match:
        folder_name = match.group(1)
        folder_images[folder_name].append(link)

print(f"✅ Extracted {len(folder_images)} unique folders from image links\n")

# Create mapping of reference events by folder name (normalize both)
def normalize_name(name):
    """Normalize name for matching"""
    return name.lower().replace(' ', '-').replace('_', '-')

reference_by_folder = {}
for event in reference_events:
    # Try to extract folder name from image URLs
    for key in ['img1', 'img2', 'img3']:
        if key in event and event[key]:
            match = re.search(r'/archived-events/([^/]+)/', event[key])
            if match:
                folder = match.group(1)
                reference_by_folder[folder] = event
                break

print(f"✅ Mapped {len(reference_by_folder)} reference events to folders\n")

# Create enhanced mapping
enhanced_mapping = []

for folder in cloudinary_folders:
    folder_name = folder.get('event_name', '')
    folder_path = folder.get('cloudinary_folder', '')
    event_id = folder.get('event_id', '')
    
    # Get images for this folder
    images = folder_images.get(folder_name, [])
    
    # Try to find matching reference event
    reference = reference_by_folder.get(folder_name)
    
    # Build enhanced entry
    entry = {
        'event_id': event_id,
        'event_name': folder_name,
        'cloudinary_folder': folder_path,
        'image_count': len(images),
        'cloudinary_urls': images[:50],  # First 50 image links as sample
        'folder_url': f"https://console.cloudinary.com/console/c-du0lumtob/media_library/folders/{folder_path}"
    }
    
    # Add reference event details if available
    if reference:
        entry['reference_event'] = {
            'name': reference.get('name', ''),
            'date': reference.get('date', ''),
            'year': reference.get('Year', ''),
            'venue': reference.get('venue', ''),
            'description': reference.get('desc', '')
        }
    else:
        # Try to extract year from folder name
        year_match = re.search(r'(202\d|20\d\d)', folder_name)
        entry['reference_event'] = {
            'name': folder_name,
            'date': '',
            'year': int(year_match.group(1)) if year_match else '',
            'venue': '',
            'description': ''
        }
    
    enhanced_mapping.append(entry)

print(f"✅ Created enhanced mapping for {len(enhanced_mapping)} events\n")

# Save enhanced mapping
output_file = 'cloudinary_event_mapping_enhanced.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(enhanced_mapping, f, indent=2, ensure_ascii=False)

print(f"💾 Saved to {output_file}")
print(f"\n📊 Summary:")
print(f"  • Total events: {len(enhanced_mapping)}")
print(f"  • Events with reference data: {sum(1 for e in enhanced_mapping if e['reference_event'].get('venue'))}")
print(f"  • Total image links stored: {sum(e['image_count'] for e in enhanced_mapping)}")

# Show sample
print(f"\n📋 Sample entry:")
if enhanced_mapping:
    sample = enhanced_mapping[0]
    print(json.dumps(sample, indent=2, ensure_ascii=False)[:500])
