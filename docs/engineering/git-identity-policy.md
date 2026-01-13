# Git Identity Policy (SSH + noreply)

This document defines the **canonical Git identity policy** for this repository to ensure consistent author attribution, privacy protection, and predictable commit metadata across different tools (CLI, VSCode, SourceTree, GitHub Web).

---

## Goals

This policy aims to prevent the following issues:

- Inconsistent commit author names
- Personal email exposure
- Mismatch between CLI / GUI / Web-based commits
- Mixed authentication methods (HTTPS / PAT / OAuth / SSH)
- Confusing attribution caused by UI display names

---

## Canonical Identity Lock

This repository enforces the following identity standard:

| Field | Value |
|------|------|
| Transport protocol | SSH |
| Author name | Jinsie |
| Author email | GitHub noreply |
| GitHub Profile Name | Not enforced (display-only) |

> GitHub Profile Name is a presentation-layer value and does not affect Git metadata.

---

## What Determines the Commit Author?

Git stores two independent identity fields:

### Author
The person who originally wrote the code.

### Committer
The person or system that finalized the commit (e.g. GitHub merge bot, web UI).

These values are resolved from:

- Local Git configuration
- The tool used to perform the commit (CLI, SourceTree, VSCode, GitHub Web)

---

## Canonical Configuration

### Global

```bash
git config --global user.name "Jinsie"
git config --global user.email "YOUR_ID@users.noreply.github.com"
```

### Repository-Level Lock

```bash
git config --local user.name "Jinsie"
git config --local user.email "YOUR_ID@users.noreply.github.com"
```

---

## Verification

```bash
git config --show-origin --get-regexp '^user\.(name|email)$'
git log -1 --pretty=fuller
```

Expected:

```
Author: Jinsie <...@users.noreply.github.com>
Commit: Jinsie <...@users.noreply.github.com>
```

---

## SSH Enforcement

```bash
git remote -v
```

Expected:

```
git@github.com:ORG/REPO.git
```

If not:

```bash
git remote set-url origin git@github.com:ORG/REPO.git
```

---

## GitHub Email Privacy Settings

Enable the following:

- Keep my email addresses private
- Block command line pushes that expose my email

---

## About Display Names

GitHub UI may show:

- Profile Name
- Username
- Commit author name

These are presentation-layer values.

The source of truth is always:

```
git log
```

---

## Final Rule

All future commits to this repository must comply with:

- SSH transport
- Author name: Jinsie
- Email: GitHub noreply
