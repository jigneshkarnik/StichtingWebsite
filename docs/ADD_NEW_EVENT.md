# Adding New Events to the Gallery

This guide explains how to add new events to the Sanskriti & Sanskar website gallery using our automated system.

## Table of Contents

- [Quick Start](#quick-start)
- [Automated Process (Recommended)](#automated-process-recommended)
- [Manual Fallback](#manual-fallback)
- [Cloudinary Upload Guide](#cloudinary-upload-guide)
- [Setup Instructions](#setup-instructions)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites

1. ✅ Photos uploaded to Cloudinary in a dedicated folder
2. ✅ Event details ready (name, location, date)
3. ✅ Thumbnail image selected
4. ✅ GitHub account with access to the repository

### 5-Minute Process

1. Go to [New Event Issue](../../issues/new?template=add-event.yml)
2. Fill in the event details
3. Add the `new-event` label
4. Wait for automation to create a PR
5. Review and merge the PR

That's it! 🎉

---

## Automated Process (Recommended)

The automated process uses GitHub Issues and GitHub Actions to streamline event addition.

### Step 1: Upload Photos to Cloudinary

1. Log in to [Cloudinary](https://cloudinary.com/)
2. Navigate to **Media Library**
3. Create a new folder: `archived-events/YOUR-EVENT-NAME`
   - Example: `archived-events/2025-06-Vrouwen-Middag-Uithoorn`
4. Upload all event photos to this folder
5. Note the folder name (without the `archived-events/` prefix)

**Naming Convention:**
```
YYYY-MM-Event-Name-Location
```

Examples:
- `2025-06-Vrouwen-Middag-Uithoorn`
- `2025-05-Literary-Fest-Almere`
- `2024-12-The-Rythms-of-India-Eindhoven`

### Step 2: Create GitHub Issue

1. Go to the repository's **Issues** tab
2. Click **New Issue**
3. Select the **"Add New Event"** template
4. Fill in the required fields (see template for details)
5. Check all boxes in the **Completion Checklist**
6. Click **Submit new issue**

### Step 3: Trigger Automation

1. On the issue page, add the **`new-event`** label
2. The GitHub Action will automatically start

### Step 4: Review Generated PR

1. Wait for automation to complete (~1-2 minutes)
2. Review the automatically created Pull Request
3. Verify the changes look correct

### Step 5: Merge and Publish

1. Click **Merge pull request**
2. The event will be live on the website!
3. Close the original issue

---

## Manual Fallback

If automation fails, you can add events manually by editing `cloudinary_event_mapping.json` and `gallery.js`. See the full documentation in this file for detailed instructions.

---

## Cloudinary Upload Guide

### Best Practices

1. **Image Format:** Use JPEG, optimize to < 2MB per image
2. **File Names:** Use descriptive names with hyphens
3. **Folder Organization:** `archived-events/YYYY-MM-Event-Name-Location`

---

## Setup Instructions

### For Repository Administrators

Add these GitHub Secrets:

1. **Settings** → **Secrets and variables** → **Actions**
2. Add secrets:
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`

### Workflow Permissions

1. **Settings** → **Actions** → **General**
2. Enable:
   - ✅ Read and write permissions
   - ✅ Allow GitHub Actions to create and approve pull requests

---

## Troubleshooting

### Workflow doesn't trigger
- Check if GitHub Actions are enabled
- Verify `.github/workflows/add-event.yml` exists
- Check Actions tab for errors

### "No photos found in folder"
- Verify folder name is correct
- Ensure photos are uploaded to Cloudinary
- Check folder path

### "Missing Cloudinary credentials"
- Add GitHub Secrets (see Setup Instructions)
- Verify secret names match exactly

### PR not created
- Check workflow permissions
- Look for existing PR
- Check Actions logs for errors

---

## Need More Help?

1. Check [GitHub Actions logs](../../actions)
2. Review existing events in `cloudinary_event_mapping.json`
3. Open an issue with label `help wanted`
4. Contact repository maintainers

---

**Happy event adding! 🎉**
