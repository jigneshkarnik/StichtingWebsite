#!/usr/bin/env python3
"""
update_events_html.py
─────────────────────
Step 3 of the new-event workflow (after detect_new_folders.py and manual edits).

What it does:
  • Reads cloudinary_event_mapping.json
  • Replaces the embedded JSON block inside events.html
  • Prints a summary of what was updated

Usage:
    python3 scripts/update_events_html.py

No environment variables needed.
"""

import json, re, os

BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAPPING_PATH  = os.path.join(BASE_DIR, 'cloudinary_event_mapping.json')
HTML_PATH     = os.path.join(BASE_DIR, 'events.html')


def main() -> None:
    # Load mapping
    with open(MAPPING_PATH, encoding='utf-8') as f:
        data: list[dict] = json.load(f)

    # Basic completeness check — warn about missing metadata
    incomplete = [
        e for e in data
        if not e.get('event_date') or not e.get('description') or not e.get('venue')
    ]
    if incomplete:
        print(f'⚠️   {len(incomplete)} event(s) still have incomplete metadata:')
        for e in incomplete[:10]:
            missing = [k for k in ('event_date', 'venue', 'description') if not e.get(k)]
            print(f'     • {e["cloudinary_folder"]}  (missing: {", ".join(missing)})')
        if len(incomplete) > 10:
            print(f'     … and {len(incomplete) - 10} more')
        print()

    # Load events.html
    with open(HTML_PATH, encoding='utf-8') as f:
        html = f.read()

    new_json = json.dumps(data, indent=2, ensure_ascii=False)

    # Replace the embedded JSON block
    pattern = r'(<script type="application/json" id="eventsData">\s*)\[.*?\](\s*</script>)'
    html_new, count = re.subn(pattern, lambda m: m.group(1) + new_json + m.group(2),
                               html, flags=re.DOTALL)

    if count == 0:
        print('❌  Could not find the embedded JSON block in events.html')
        print('    Expected: <script type="application/json" id="eventsData">')
        return

    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(html_new)

    # Verify
    m2 = re.search(r'<script type="application/json" id="eventsData">\s*(\[.*?\])\s*</script>',
                   html_new, re.DOTALL)
    if m2:
        check = json.loads(m2.group(1))
        no_desc = sum(1 for e in check if not e.get('description', ''))
        no_date = sum(1 for e in check if not e.get('event_date', ''))
        print(f'✅  events.html updated — {len(check)} events embedded')
        print(f'   Missing description: {no_desc}')
        print(f'   Missing date:        {no_date}')
    else:
        print('✅  events.html updated')

    print()
    print('Next:  git add events.html cloudinary_event_mapping.json')
    print('       git commit -m "Update events" && git push origin main')


if __name__ == '__main__':
    main()
