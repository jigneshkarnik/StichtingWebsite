---
name: git-commit-push
user-invocable: true
description: "Use when the user asks to stage all changes, commit them, and push to git on the main branch."
---

# Git Commit and Push

Use this skill when the user wants the current workspace changes committed and pushed to the `main` branch.

## Workflow

1. Check the current branch and git status.
2. Review the changed files to make sure only the intended changes are included.
3. Stage the relevant files, usually all tracked edits for the requested task.
4. Create a clear commit message that summarizes the actual change.
5. Commit the staged changes on the current branch.
6. Push the commit to `origin` on `main` only when the repository is already on `main` and the user explicitly requested a main-branch push.
7. Confirm the push succeeded.

## Guardrails

- Do not use force push.
- Do not rewrite history unless the user explicitly asks for it.
- If the branch is not `main`, stop and report that before pushing to `main`.
- If unrelated files are modified, leave them untouched unless the user asked to include them.
- If git reports a push conflict or remote rejection, stop and report the blocker instead of guessing.
