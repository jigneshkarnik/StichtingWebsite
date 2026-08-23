# Adding a New Event — Step-by-Step Workflow

This document describes how to publish a new event to the Sanskriti & Sanskar website archive using the issue-driven automation.

---

## Overview

```
Upload photos to Cloudinary
        ↓
Create a GitHub Issue (template)
        ↓
Apply the `new-event` label
        ↓
GitHub Actions runs automatically
        ↓
Pull Request is created for your review
        ↓
Merge PR → event goes live
```

---

## Step 1 — Upload photos to Cloudinary

1. Log in to [Cloudinary](https://cloudinary.com).
2. Navigate to **Media Library → archived-events**.
3. Create a new sub-folder with a descriptive, hyphen-separated name, for example:
   ```
   2025-08-Janmashtami-Utrecht
   ```
4. Upload all event photos into that folder.
5. Note the **exact folder name** — you will need it in the issue.

---

## Step 2 — Create a GitHub Issue

1. Go to the repository on GitHub.
2. Click **Issues → New issue**.
3. Select the **"Add New Event to Archive"** template.
4. Fill in **all required fields**:

   | Field | Description | Example |
   |-------|-------------|---------|
   | **Event Name** | Full display name | `Janmashtami Celebration @Utrecht` |
   | **Cloudinary Folder Name** | Exact folder (no prefix) | `2025-08-Janmashtami-Utrecht` |
   | **Event Date** | YYYY-MM-DD | `2025-08-16` |
   | **Event Time** | Optional, with timezone | `18:30 CET` |
   | **Venue / Location** | City or venue name | `Utrecht` |
   | **Short Description** | 1–3 sentences for the card | `An evening of devotional music…` |
   | **Hero Image (img1)** | Full Cloudinary URL of cover photo | `https://res.cloudinary.com/…jpg` |
   | **Second Image (img2)** | Optional second photo URL | `https://res.cloudinary.com/…jpg` |
   | **Third Image (img3)** | Optional third photo URL | `https://res.cloudinary.com/…jpg` |

   > **Tip:** Copy photo URLs from Cloudinary → select a photo → click **Copy URL** (use the "Original" or highest-quality variant).

5. Check all boxes in the pre-submission checklist.
6. Click **Submit new issue**.

---

## Step 3 — Trigger the automation

The automation starts when the `new-event` label is applied to the issue.

- **If you submitted the issue yourself**, apply the label immediately:
  1. Open the issue.
  2. On the right sidebar, click **Labels → new-event**.

- **If someone else submitted the issue**, review the details first, then apply the label when satisfied.

---

## Step 4 — Wait for the Pull Request

Within about 60–90 seconds, GitHub Actions will:

1. Parse the issue fields.
2. Connect to Cloudinary and fetch **all photos** from the named folder.
3. Add a new entry (newest-first) to **`events_data.json`**.
4. Prepend a full entry (with all image URLs) to **`cloudinary_event_mapping.json`**.
5. Re-embed the updated mapping into **`events.html`**.
6. Open a **Pull Request** and post a comment on the issue with the PR link.

You will receive a GitHub notification when the PR is ready.

---

## Step 5 — Review and merge

1. Open the Pull Request.
2. Check the **Review checklist** items in the PR description:
   - Event name, date, venue look correct
   - Hero image (img1) is the intended card thumbnail
   - Photo count is as expected
   - Description reads well
   - Event appears at the top of the archive
3. Optionally open `events.html` locally to preview.
4. Click **Merge pull request** → **Confirm merge**.
5. The branch is deleted automatically.

The event is now **live on the website**. 🎉

---

## What each file stores

| File | Purpose |
|------|---------|
| `events_data.json` | Lightweight reference list (Sno, date, name, venue, desc, img1/2/3). Used by sync scripts. |
| `cloudinary_event_mapping.json` | Full gallery mapping — all image URLs, metadata, photo count. Single source of truth for the website. |
| `events.html` | The public archive page — JSON is embedded inside `<script id="eventsData">` and rendered dynamically. |

---

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| Workflow does not start | `new-event` label not applied | Apply the label manually on the issue |
| "No photos found" error | Folder name is wrong or photos not yet uploaded | Check spelling in Cloudinary; re-trigger by removing and re-applying the label |
| PR not created | Event already exists (duplicate folder) | Check `cloudinary_event_mapping.json`; edit manually if needed |
| Wrong hero image | `img1` URL not entered correctly | Edit `cloudinary_event_mapping.json` → move correct URL to index 0, then run `python3 scripts/update_events_html.py` |
| Description missing on card | `description` field left blank in issue | Edit `cloudinary_event_mapping.json` directly and re-run `update_events_html.py` |

---

## Manual fallback (without an issue)

If you prefer to work locally:

```bash
# 1. Detect new folders automatically
python3 scripts/detect_new_folders.py

# 2. Edit cloudinary_event_mapping.json — fill in the new entry at the top
#    Fields to set: event_name_ref, event_date, venue, description

# 3. Re-embed the JSON into events.html
python3 scripts/update_events_html.py

# 4. Commit and push
git add cloudinary_event_mapping.json events_data.json events.html
git commit -m "Add event: <name>"
git push origin main
```

---

## Key scripts

| Script | What it does |
|--------|-------------|
| `scripts/add_event_from_issue.py` | Triggered by the GitHub Action; parses the issue, fetches Cloudinary photos, updates all three files |
| `scripts/detect_new_folders.py` | Scans Cloudinary for folders not yet in the mapping; adds skeleton entries |
| `scripts/update_events_html.py` | Re-embeds `cloudinary_event_mapping.json` into `events.html` |
| `scripts/sync_event_mapping.py` | Full re-sync — sequences and enriches the mapping from `events_data.json` |

---

*Last updated: August 2026*
