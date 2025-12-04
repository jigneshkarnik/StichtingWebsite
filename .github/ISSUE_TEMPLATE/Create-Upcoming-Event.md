---
name: Upcoming event
about: Request adding an upcoming event to the website
title: ''
labels: 'event'
assignees: ''
---

## Event name
Please provide the official event name.

## Event date & time
- Date (required): YYYY-MM-DD
- Time (optional; include timezone): e.g. 18:30 CET

## Event description
Provide a short description (1–3 paragraphs) suitable for the website. Include any important speakers, schedule highlights, or notes.

## Ticket link
Provide the URL for buying or reserving tickets, or write "N/A" if not applicable.

## Dedicated page needed?
- [ ] Yes — please create a dedicated event page
- [ ] No — show as an item on the events list only

If "Yes", briefly describe the page content or sections required (e.g., agenda, speakers, registration form).

## Poster image link
Provide a publicly accessible URL to the poster image, or upload the image to the repo and provide the path. Include image alt text:
- Image URL / path:
- Alt text:

## Additional optional info
- Organizer / contact person:
- Accessibility notes:
- Tags / categories:

## Acceptance criteria (what we need before publishing)
- [ ] Event details are verified (date, time, venue)
- [ ] Ticket link works
- [ ] Poster image is available and sized appropriately
- [ ] If dedicated page required: page content ready and reviewed

Please include any attachments (images, PDFs) or external links below.

---

## Copilot instructions — DO NOT REMOVE
These lines are required and must not be removed or modified by the issue author. Automated helpers (e.g., Copilot or an action) will read this exact section to implement the event.

Instruction for Copilot / implementer:
- Take the Event name, Event date & time, Event description, Ticket link, and Poster image link from this issue and create a new entry in the site's "upcoming events" HTML (or the events data source used by the site).
- If "Dedicated page needed" is checked "Yes", create a dedicated event page (HTML/MD as appropriate for this repo) using the provided description, poster, and ticket link, and then add a link from the upcoming events page to this dedicated page.
- Ensure the poster image is reachable and add alt text from the "Poster image link" section.
- Add metadata (date/time, ticket link, poster URL, canonical title) in the same format used by other event pages in the repo.
- Create a branch named following the pattern: issue/<issue-number>-<short-title> and implement the changes there.
- Open a PR from that branch to `main`, include "Closes #<issue-number>" in the PR description, and request review per CODEOWNERS.

DO NOT REMOVE these Copilot instructions. They are used to automate or guide the implementation and must remain in the issue body.
