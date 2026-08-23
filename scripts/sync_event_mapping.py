#!/usr/bin/env python3
"""
sync_event_mapping.py
---------------------
Syncs cloudinary_event_mapping.json with events_data_23Aug2026_v3.json:

1. SEQUENCE    - orders cloudinary_event_mapping.json entries to match the
                 order (Sno) defined in events_data_23Aug2026_v3.json
2. METADATA    - updates date, venue, description on matched entries
3. FIRST IMAGE - sets cloudinary_urls[0] to the img1 value from
                 events_data_23Aug2026_v3.json
4. Unmatched cloudinary entries are appended after the ordered ones.

Folder matching strategy (tried in order):
  a) Extract 'archived-events/<folder>/' path from img1
  b) Same from img2, then img3
  c) Manual SNO_TO_FOLDER override table (for events whose images live
     outside the archived-events tree)

Run:
    python3 scripts/sync_event_mapping.py

After running, regenerate events.html:
    python3 scripts/generate_events_html.py   (if it exists)
"""

import json
import re
import os
from datetime import datetime


# ── paths ─────────────────────────────────────────────────────────────────────
BASE_DIR          = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVENTS_REF_PATH   = os.path.join(BASE_DIR, "events_data_23Aug2026_v3.json")
MAPPING_PATH      = os.path.join(BASE_DIR, "cloudinary_event_mapping.json")
MAPPING_OUT_PATH  = MAPPING_PATH   # overwrite in-place


# ── manual Sno → cloudinary_folder overrides ──────────────────────────────────
# Used when none of img1/img2/img3 contain an 'archived-events/<folder>/' path.
# Key = Sno value (as it appears in events_data JSON, may be int or str).
SNO_TO_FOLDER: dict = {
    5:  "Radio Poetry",
    9:  "2023-6-EU_UK Poetry Idol August",
    16: "April-2024-Ramnavami",
    22: "2024 Consular Camp",
    24: "The Tulips Lounge",
    27: "2024 Philips Yoga Day",
    31: "2024, 2025, 2026 Sahitya Chaupal",
    39: "International-Womens-Day",          # IWD 2025 maps to same gallery folder
    40: "2024-18-Nov-prasadam distribution",
    43: "2024-25-Aug- Connecting culture",
    45: "2025-7--May Vouwen-Mmiddag Brain Jamming",
    47: "2025 international Yoga Day",
    48: "2025-24-June Vrouwen Middag session on health issue",
    49: "2025 August Janamastami",
    50: "2025-5-September Vrouwen Vrijdag Teachers Day",
    51: "2025-12-September Vrouwen Middag Garba Workshop",
    52: "2025-17-September Hindi Diwas Denhaag",
    53: "2025-BhartiyaFirst",
    54: "2025-31-october Vrouwen-Middag zumba workshop",
    55: "2025-28-Diwali Philips October",
    56: "2025-28-Vrouwen Vrijdag painting workshop November",
    58: "2026-ITF",
    59: "2026-10- Hindi Diwas January",
    60: "2026-Holi",
    61: "2025-5-April Vrouwen Vrijdag Poetic Fairytale",
    62: "2026-LiteraryFest",
    63: "2026-21- International Yoga Day",
    64: "Bharat Dutch Times_June 2026",
    65: "Bharat Dutch Times_July 2026",
    66: "Uithoorn Desk",
    67: "2026 DE OPENING",   # closest match; GEN B has no dedicated folder yet
    68: "2026 DE OPENING",
}


# ── helpers ───────────────────────────────────────────────────────────────────

def extract_folder_from_url(url: str) -> str | None:
    """Extract cloudinary archived-events folder name from a URL."""
    m = re.search(r"archived-events/([^/]+)/", url or "")
    return m.group(1) if m else None


def resolve_folder(ref: dict) -> str | None:
    """
    Return the cloudinary_folder for a reference event row.
    Tries img1, img2, img3, then the manual override table.
    """
    for key in ("img1", "img2", "img3"):
        folder = extract_folder_from_url(ref.get(key, ""))
        if folder:
            return folder

    # normalise Sno to int for dict lookup
    sno_raw = ref.get("Sno")
    try:
        sno = int(sno_raw)
    except (TypeError, ValueError):
        sno = sno_raw

    return SNO_TO_FOLDER.get(sno)


def parse_iso_date(date_str: str) -> str:
    """Convert ISO-8601 timestamp to YYYY-MM-DD.  Returns '' on failure."""
    if not date_str:
        return ""
    try:
        dt = datetime.fromisoformat(str(date_str).replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return str(date_str)


def is_cloudinary_url(value: str) -> bool:
    return bool(value and "cloudinary.com" in value)


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    with open(EVENTS_REF_PATH, encoding="utf-8") as f:
        events_ref: list[dict] = json.load(f)

    with open(MAPPING_PATH, encoding="utf-8") as f:
        mapping: list[dict] = json.load(f)

    # index by folder name for O(1) lookup
    mapping_by_folder: dict[str, dict] = {
        e["cloudinary_folder"]: e for e in mapping
    }

    ordered_output: list[dict] = []
    matched_folders: set[str]  = set()

    for ref in events_ref:
        # skip blank placeholder rows
        if not ref.get("Sno") and not ref.get("name"):
            continue

        sno  = ref.get("Sno", "?")
        name = ref.get("name", "")

        folder = resolve_folder(ref)

        if not folder:
            print(f"  ⚠️  Sno {sno:>3}: no folder resolved → skipped  [{name}]")
            continue

        cm_entry = mapping_by_folder.get(folder)
        if not cm_entry:
            print(f"  ❌  Sno {sno:>3}: folder not in mapping → skipped  [{folder}]")
            continue

        # avoid adding the same folder twice (e.g. Sno 67 & 68 both map to DE OPENING)
        if folder in matched_folders:
            print(f"  ↩️  Sno {sno:>3}: folder already used, skipping duplicate  [{folder}]")
            continue

        matched_folders.add(folder)

        # ── update metadata ────────────────────────────────────────────────
        date_val = parse_iso_date(ref.get("date", ""))
        if date_val:
            cm_entry["event_date"] = date_val

        venue_val = ref.get("venue", "")
        if venue_val and not is_cloudinary_url(venue_val):
            cm_entry["venue"] = venue_val

        desc_val = ref.get("desc", "")
        if desc_val:
            cm_entry["description"] = desc_val

        name_val = ref.get("name", "")
        if name_val:
            cm_entry["event_name_ref"] = name_val  # human-readable name; keep original too

        # ── first image: prepend img1 so cloudinary_urls[0] is the hero img ─
        img1 = ref.get("img1", "")
        current_urls: list[str] = cm_entry.get("cloudinary_urls", [])
        if img1 and is_cloudinary_url(img1):
            current_urls = [u for u in current_urls if u != img1]
            cm_entry["cloudinary_urls"] = [img1] + current_urls
        else:
            cm_entry["cloudinary_urls"] = current_urls

        ordered_output.append(cm_entry)
        source = "img" if extract_folder_from_url(ref.get("img1","")) or \
                          extract_folder_from_url(ref.get("img2","")) or \
                          extract_folder_from_url(ref.get("img3","")) else "manual"
        print(f"  ✅  Sno {sno:>3} [{source}]: matched → [{folder}]")

    # ── append unmatched cloudinary entries at the end ─────────────────────
    unmatched = [e for e in mapping if e["cloudinary_folder"] not in matched_folders]
    if unmatched:
        print(f"\n  ℹ️  {len(unmatched)} cloudinary entries had no match (appended at end):")
        for e in unmatched:
            print(f"       • {e['cloudinary_folder']}")
    ordered_output.extend(unmatched)

    with open(MAPPING_OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(ordered_output, f, indent=2, ensure_ascii=False)

    print(f"\n✅  Done!  {len(ordered_output)} entries written to {MAPPING_OUT_PATH}")
    print(f"    • {len(matched_folders)} entries matched & sequenced")
    print(f"    • {len(unmatched)} entries appended (unmatched)")


if __name__ == "__main__":
    main()
