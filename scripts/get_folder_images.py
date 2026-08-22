#!/usr/bin/env python3
"""
Extract image links from a Cloudinary folder
Returns only the image URLs (one per line) for easy parsing
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
        print("❌ Missing Cloudinary credentials", file=sys.stderr)
        sys.exit(1)
    
    credentials = f"{CLOUDINARY_API_KEY}:{CLOUDINARY_API_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"


def extract_images_from_folder(folder_path, verbose=False):
    """Extract all image links from a folder."""
    if verbose:
        print(f"📂 Fetching images from: {folder_path}\n", file=sys.stderr)
    
    auth_header = get_auth_header()
    headers = {
        'Authorization': auth_header,
        'Content-Type': 'application/json'
    }
    
    all_images = []
    next_cursor = None
    page = 1
    
    while True:
        # Query using folder_path
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
            next_cursor = data.get('next_cursor')
            
            if verbose:
                print(f"[Page {page}] Retrieved {len(resources)} images", file=sys.stderr)
            
            # Extract image links
            for resource in resources:
                secure_url = resource.get('secure_url', '')
                if secure_url:
                    all_images.append(secure_url)
                    print(secure_url)  # Output to stdout
            
            if not next_cursor:
                break
            
            page += 1
        
        except HTTPError as e:
            print(f"❌ HTTP Error {e.code}: {e.reason}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"❌ Error: {e}", file=sys.stderr)
            return False
    
    if verbose:
        print(f"\n✅ Found {len(all_images)} image links", file=sys.stderr)
    
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 get_folder_images.py <folder_path> [-v]")
        print("\nExample:")
        print("  python3 get_folder_images.py 'archived-events/2023-6-EU_UK Poetry Idol August'")
        print("  python3 get_folder_images.py 'archived-events/2024 Philips Yoga Day' -v")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    verbose = '-v' in sys.argv or '--verbose' in sys.argv
    
    success = extract_images_from_folder(folder_path, verbose=verbose)
    sys.exit(0 if success else 1)
