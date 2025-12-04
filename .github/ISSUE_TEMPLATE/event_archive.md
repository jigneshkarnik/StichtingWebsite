---
name: Event archive
about: Add or archive an event in the site's events archive
title: ''
labels: 'archive'
assignees: ''
---

## Event name
Provide the official event name.

## Event date
- Date (required): YYYY-MM-DD

## Event time
- Time (optional; include timezone): e.g. 18:30 CET

## Location / Venue
Provide the event location or venue details.

## Event description
Short description (1–3 paragraphs) suitable for the archive page.

## Media (image or video)
- Image URL (public) or path if already in repo: 
- Video link (YouTube) or write "N/A":

If you provide both, indicate which to prefer for the archive entry.

## Remove from upcoming events?
- [ ] Yes — this event should be removed from the upcoming events page
- [ ] No — leave as-is on upcoming events

If "Yes", reference the upcoming event to remove (provide event title, issue number, or link to the upcoming event page): 

## Additional notes / contacts
- Organizer / contact:
- Tags / categories:

## Acceptance criteria
- [ ] Archive entry is created on the events archive page (events.html)
- [ ] Media is reachable and displays correctly (image or YouTube embed)
- [ ] If removal requested: upcoming events page updated to remove the referenced event
- [ ] PR opened referencing this issue (Closes #<issue-number>)

---

## Copilot instructions — DO NOT REMOVE
These exact lines are required and must not be removed or modified by the issue author. Automated helpers (e.g., Copilot or an action) will read this exact section to implement the archive entry.

Instruction for Copilot / implementer:
- Create an entry for this event on the events archive page (events.html) using Event name, Event date, Event time, Location, Event description, and selected Media.
- If an Image URL is provided:
  - Download or add the image into the repository under the images folder (create the folder if it does not exist).
  - Use the repository-relative path (e.g., images/<filename>) in the archive entry.
  - Add alt text using the event name or provided alt text.
- If a YouTube link is provided (and preferred), embed or link the YouTube URL directly in the archive entry without downloading media.
- If "Remove from upcoming events?" is checked "Yes" and a reference to an upcoming event is provided:
  - Update upcoming-events.html to remove the corresponding upcoming-event entry (match by title).
  - Ensure no broken links remain on the upcoming events page.
- Follow the repository's existing event entry format and metadata conventions (date/time format, CSS classes, front-matter, or JSON data structure used by the project).
- Create a branch named: issue/<issue-number>-<short-title> and implement changes there.
- Commit with a message referencing the issue (e.g., "Add archived event: <Event name> — closes #<issue-number>").
- Open a PR from that branch to main, include "Closes #<issue-number>" in the PR description, and request review per CODEOWNERS.

DO NOT REMOVE these Copilot instructions. They are used to automate or guide the implementation and must remain in the issue body.
