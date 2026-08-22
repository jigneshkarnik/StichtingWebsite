#!/usr/bin/env python3
"""
Extract image links from a Cloudinary folder using FOLDER PATH
This is the correct approach - use the folder path, not folder_id
"""

import json
import os
import sys
import base64
import urllib.parse
from urllib import request
from urllib.error import HTTPError

CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME', 'du0lumtob')
CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')


def get_auth_header():
    """Return Authorization header for Cloudinary API."""
    if not CLOUDINARY_API_KEY or not CLOUDINARY_API_SECRET:
        print("❌ Missing Cloudinary credentials")
        sys.exit(1)
    
    credentials = f"{CLOUDINARY_API_KEY}:{CLOUDINARY_API_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"


def extract_images_from_folder_path(folder_path):
    """Extract all image links from a folder using folder PATH (not ID)."""
    print(f"\n📂 Fetching images from folder: {folder_path}\n")
    
    auth_header = get_auth_header()
    headers = {
        'Authorization': auth_header,
        'Content-Type': 'application/json'
    }
    
    all_images = []
    next_cursor = None
    page = 1
    total_count = 0
    
    while True:
        # Query using folder_path with exact match
        query = f'folder_path:"{folder_path}"'
        params = {
            'query': query,
            'max_results': 500
        }
        
        if next_cursor:
            params['next_cursor'] = next_cursor
        
        query_string = urllib.parse.urlencode(params)
        url = f"https://api.cloudinary.com/v1_1/{CLOUDINARY_CLOUD_NAME}/resources/search?{query_string}"
        
        try:
            req = request.Request(url, headers=headers)
            with request.urlopen(req) as response:
                data = json.loads(response.read().decode())
            
            resources = data.get('resources', [])
            total_count = data.get('total_count', 0)
            next_cursor = data.get('next_cursor')
            
            print(f"[Page {page}] Retrieved {len(resources)} resources (total in folder: {total_count})\n")
            
            # Extract image links
            for idx, resource in enumerate(resources, 1):
                secure_url = resource.get('secure_url', '')
                public_id = resource.get('public_id', '')
                print(f"[{len(all_images) + idx}] {public_id}")
                print(f"    🔗 {secure_url}\n")
                all_images.append({
                    'public_id': public_id,
                    'url': secure_url
                })
            
            if not next_cursor:
                break
            
            page += 1
        
        except HTTPError as e:
            print(f"❌ HTTP Error {e.code}: {e.reason}")
            print(f"   URL: {url}")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    return {
        'folder_path': folder_path,
        'total_count': total_count,
        'returned': len(all_images),
        'images': all_images
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 extract_folder_images.py <folder_path>")
        print("\nExample:")
        print("  python3 extract_folder_images.py 'archived-events/2023-6-EU_UK Poetry Idol August'")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    result = extract_images_from_folder_path(folder_path)
    
    if result:
        print(f"\n{'='*70}")
        print(f"Summary:")
        print(f"  • Folder: {result['folder_path']}")
        print(f"  • Total images in folder: {result['total_count']}")
        print(f"  • Retrieved: {result['returned']}")
        print(f"{'='*70}")
