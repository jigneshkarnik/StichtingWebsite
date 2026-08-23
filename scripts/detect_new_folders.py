#!/usr/bin/env python3
"""
detect_new_folders.py
─────────────────────
Step 1 of the new-event workflow.

What it does:
  1. Fetches ALL sub-folders under archived-events/ from the Cloudinary API
  2. Compares with cloudinary_event_mapping.json
  3. For every NEW folder:
       • Fetches all image URLs from that folder
       • Prepends a skeleton entry at the TOP of cloudinary_event_mapping.json
         (newest folders appear first in the list)
  4. Writes the updated cloudinary_event_mapping.json
  5. Prints a TODO list of entries that still need manual metadata

The skeleton entry looks like:
  {
    "event_id":       "<cloudinary folder external_id>",
    "event_name":     "<folder name>",          ← human-readable placeholder
    "event_name_ref": "",                        ← fill in manually
    "event_date":     "",                        ← fill in manually  e.g. 2025-06-15
    "venue":          "",                        ← fill in manually  e.g. Eindhoven
    "description":    "",                        ← fill in manually
    "cloudinary_folder": "<folder name>",
    "photo_count":    <n>,
    "cloudinary_urls": [ ... ],
    "folder_url":     "https://console.cloudinary.com/..."
  }

Usage:
    python3 scripts/detect_new_folders.py

Environment variables required:
    CLOUDINARY_API_KEY
    CLOUDINARY_API_SECRET
    CLOUDINARY_CLOUD_NAME   (default: du0lumtob)

After running:
  1. Open cloudinary_event_mapping.json
  2. Fill in event_name_ref, event_date, venue, description for each NEW entry
     (they appear at the top with empty strings)
  3. Run:  python3 scripts/update_events_html.py
  4. Commit and push
"""

import os, sys, json, base64, time
import urllib.parse
from urllib import request
from urllib.error import HTTPError, URLError

# ── config ────────────────────────────────────────────────────────────────────
CLOUD_NAME   = os.environ.get('CLOUDINARY_CLOUD_NAME', 'du0lumtob')
API_KEY      = os.environ.get('CLOUDINARY_API_KEY')
API_SECRET   = os.environ.get('CLOUDINARY_API_SECRET')
FOLDER_ROOT  = 'archived-events'
MAPPING_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                            'cloudinary_event_mapping.json')


# ── helpers ───────────────────────────────────────────────────────────────────

def auth_header() -> str:
    if not API_KEY or not API_SECRET:
        print('❌  CLOUDINARY_API_KEY / CLOUDINARY_API_SECRET not set')
        sys.exit(1)
    creds = f"{API_KEY}:{API_SECRET}"
    return 'Basic ' + base64.b64encode(creds.encode()).decode()


def api_get(url: str, retries: int = 4) -> dict:
    """GET a Cloudinary API URL with retry on rate-limit (429)."""
    headers = {'Authorization': auth_header()}
    for attempt in range(retries):
        try:
            req = request.Request(url, headers=headers)
            with request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except HTTPError as e:
            if e.code == 429:
                wait = 30 * (attempt + 1)
                print(f'   ⏳ Rate limited — waiting {wait}s …')
                time.sleep(wait)
            else:
                raise
        except URLError as e:
            print(f'   ⚠️  Network error: {e} — retrying …')
            time.sleep(10)
    raise RuntimeError(f'Failed after {retries} retries: {url}')


def fetch_all_folders() -> list[dict]:
    """Return list of all sub-folder dicts under FOLDER_ROOT."""
    print(f'\n📂 Fetching folders under {FOLDER_ROOT}/ …')
    folders, cursor = [], None
    while True:
        params = {'max_results': 500}
        if cursor:
            params['next_cursor'] = cursor
        qs  = urllib.parse.urlencode(params)
        url = f'https://api.cloudinary.com/v1_1/{CLOUD_NAME}/folders/{FOLDER_ROOT}?{qs}'
        data   = api_get(url)
        batch  = data.get('folders', [])
        folders.extend(batch)
        cursor = data.get('next_cursor')
        print(f'   fetched {len(batch)} folders  (total so far: {len(folders)})')
        if not cursor:
            break
    print(f'   ✅ {len(folders)} folders found in Cloudinary')
    return folders


def fetch_images_for_folder(folder_path: str) -> list[str]:
    """Return all secure_url strings for images inside folder_path."""
    urls, cursor = [], None
    while True:
        query  = f'folder_path:"{folder_path}"'
        params = {'query': query, 'max_results': 500}
        if cursor:
            params['next_cursor'] = cursor
        qs  = urllib.parse.urlencode(params)
        url = f'https://api.cloudinary.com/v1_1/{CLOUD_NAME}/resources/search?{qs}'
        data  = api_get(url)
        batch = data.get('resources', [])
        urls.extend(r['secure_url'] for r in batch if r.get('secure_url'))
        cursor = data.get('next_cursor')
        if not cursor:
            break
    return urls


# ── main ──────────────────────────────────────────────────────────────────────

def main(dry_run: bool = False) -> None:
    if dry_run:
        print('🔍  DRY RUN — no files will be written\n')

    # Load current mapping
    with open(MAPPING_PATH, encoding='utf-8') as f:
        mapping: list[dict] = json.load(f)

    known_folders = {e['cloudinary_folder'] for e in mapping}

    # Fetch all Cloudinary folders
    cf_folders = fetch_all_folders()

    # Find genuinely new ones
    new_folders = [
        cf for cf in cf_folders
        if cf.get('name') and cf['name'] not in known_folders
    ]

    if not new_folders:
        print('\n✅  No new folders detected. Nothing to do.')
        return

    print(f'\n🆕  {len(new_folders)} new folder(s) found:')
    for cf in new_folders:
        print(f'   • {cf["name"]}')

    if dry_run:
        print('\n🔍  Dry run complete — no changes written.')
        return

    # For each new folder, fetch images and build a skeleton entry
    new_entries: list[dict] = []
    for cf in new_folders:
        folder_name = cf['name']
        folder_path = f'{FOLDER_ROOT}/{folder_name}'
        print(f'\n   📸 Fetching images for [{folder_name}] …')

        try:
            urls = fetch_images_for_folder(folder_path)
        except Exception as e:
            print(f'   ⚠️  Could not fetch images: {e}')
            urls = []

        print(f'      → {len(urls)} image(s)')

        entry = {
            'event_id':          cf.get('external_id', cf.get('id', '')),
            'event_name':        folder_name,
            'event_name_ref':    '',                 # ← FILL IN: human-readable event name
            'event_date':        '',                 # ← FILL IN: YYYY-MM-DD
            'venue':             '',                 # ← FILL IN: e.g. Eindhoven
            'description':       '',                 # ← FILL IN: 1-2 sentence description
            'cloudinary_folder': folder_name,
            'photo_count':       len(urls),
            'cloudinary_urls':   urls,
            'folder_url':        (
                f'https://console.cloudinary.com/console/c-{CLOUD_NAME}'
                f'/media_library/folders/{FOLDER_ROOT}/{folder_name}'
            ),
        }
        new_entries.append(entry)

    # Prepend new entries (newest first) and write
    updated = new_entries + mapping
    with open(MAPPING_PATH, 'w', encoding='utf-8') as f:
        json.dump(updated, f, indent=2, ensure_ascii=False)

    print(f'\n✅  cloudinary_event_mapping.json updated — {len(new_entries)} new entry/entries added at top')

    # Print TODO list
    print('\n' + '═' * 60)
    print('📝  NEXT STEPS — fill in metadata for each new entry:')
    print('═' * 60)
    for entry in new_entries:
        print(f'\n  Folder: {entry["cloudinary_folder"]}')
        print(f'    "event_name_ref": "..."   ← human-readable name')
        print(f'    "event_date":     "..."   ← YYYY-MM-DD')
        print(f'    "venue":          "..."   ← city / venue name')
        print(f'    "description":    "..."   ← 1-2 sentence description')
    print('\n' + '═' * 60)
    print('Then run:  python3 scripts/update_events_html.py')
    print('Then:      git add -A && git commit -m "Add new events" && git push')


if __name__ == '__main__':
    dry_run = '--dry-run' in sys.argv or os.environ.get('DRY_RUN') == 'true'
    main(dry_run=dry_run)
