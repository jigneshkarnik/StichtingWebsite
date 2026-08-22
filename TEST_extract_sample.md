# Sample Script: Extract Images from Cloudinary Folder

## Overview
This script extracts image links from a specific Cloudinary folder using the folder path.

## Usage
```bash
export CLOUDINARY_CLOUD_NAME="du0lumtob"
export CLOUDINARY_API_KEY="your_api_key"
export CLOUDINARY_API_SECRET="your_api_secret"

python3 scripts/extract_folder_images.py "archived-events/2023-6-EU_UK Poetry Idol August"
```

## What It Does
1. Connects to Cloudinary REST API using Basic Auth
2. Queries resources using `folder_path:"..."` search
3. Paginates through all results (max 500 per page)
4. Extracts and displays image URLs
5. Returns total count from API response

## Current Limitation
**IMPORTANT**: Cloudinary's `/resources/search` endpoint appears to have a limitation:
- It returns a `total_count` that may not reflect actual folder contents
- All results show `folder: None` (folder info is not included in search results)
- The query may be matching resources beyond just the specified folder

## Next Steps
To fix this properly, we need to:
1. Use Cloudinary's folder management API to list subfolders and their actual structure
2. OR manually tag resources with folder metadata when they're uploaded
3. OR use a different Cloudinary API method that returns accurate folder information
