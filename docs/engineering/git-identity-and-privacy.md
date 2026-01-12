# Git Identity & Email Privacy Policy

This repository uses a consistent Git identity and protects contributor email privacy.

## Scope

This policy covers:

- Commit author identity (`user.name`, `user.email`)
- Email privacy on GitHub (noreply addresses)
- When (not) to rewrite Git history
- Recommended settings for local Git clients (CLI, VSCode, SourceTree)

## Canonical Identity

Use a single, stable identity for all commits to this repository:

- **Author name:** `Jinsie`
- **Author email:** `2735286+AnneLau@users.noreply.github.com` (GitHub noreply)

### Why noreply

- Prevents exposing a personal email address in public Git history.
- Keeps commit attribution stable across different tools (CLI / IDE / web UI).
- Aligns with common open-source and enterprise privacy practices.

## Required Local Git Configuration

Set **global** identity (recommended):

- `git config --global user.name "Jinsie"`
- `git config --global user.email "2735286+AnneLau@users.noreply.github.com"`

Verify:

- `git config --global --get user.name`
- `git config --global --get user.email`
- `git log -1 --pretty=fuller`

### Repo-specific override (optional)

If you only want this identity for this repo:

- `git config --local user.name "Jinsie"`
- `git config --local user.email "2735286+AnneLau@users.noreply.github.com"`

## GitHub Settings: Keep Email Private

Recommended GitHub settings:

- **Keep my email addresses private**: ON  
  (GitHub uses a noreply address for web-based operations.)
- **Block command line pushes that expose my email**: ON  
  (Rejects pushes if your commits use a non‑noreply email that would reveal a private address.)

## Tooling Notes

### VSCode

VSCode uses your local Git configuration for authoring commits. Ensure:

- Your Git global config is set to the canonical identity.
- You do not have a repo-local identity overriding it unexpectedly.

Check where identity is coming from:

- `git config --show-origin --get-regexp '^user\.(name|email)$'`

### SourceTree

SourceTree can override author identity. Recommended:

- Do not hardcode a different author in SourceTree.
- Prefer “Use System Git” / “Use global Git config” author settings when available.

## History Rewrite Rules

### Do NOT rewrite history by default

Avoid rewriting commit history in shared branches (e.g., `dev`, `main`) because it can:

- Break existing PR references
- Require force-push, which is risky
- Confuse collaborators and CI

### When rewriting may be acceptable

Only consider rewriting if **all** are true:

- Commits are local-only (not pushed), or
- You are on a private branch with no consumers, and
- You fully understand force-push impact

## Compatibility & Mixed Authors

It is normal to see mixed author names/emails in older commits if identity settings changed over time.
Going forward, new commits should follow the canonical identity above.

## Quick Checklist

- Global Git identity is set to `Jinsie` + GitHub noreply
- GitHub “Keep email private” is ON
- GitHub “Block command line pushes that expose my email” is ON
- VSCode / SourceTree are not overriding author identity
- No history rewrite on shared branches
