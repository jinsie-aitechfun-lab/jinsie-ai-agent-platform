# How to Check Whether a Remote Feature Branch Exists

This document explains **how to check whether a feature branch exists on the remote repository (origin)**.
It is intended as a **public, engineering-reference guide** for daily Git workflows.

---

## 1. Refresh Remote References (Recommended)

Before checking, always refresh local references to the remote repository:

```bash
git fetch --prune
```

This ensures your local view of remote branches is up to date and removes stale references.

---

## 2. List All Remote Branches

```bash
git branch -r
```

Example output:

```text
origin/dev
origin/main
origin/feature/add-base-prompts
```

### How to interpret
- If you see `origin/feature/add-base-prompts`  
  → the branch **exists on the remote repository**
- If you do not see it  
  → the branch **only exists locally**

---

## 3. Check a Specific Branch (Recommended)

To check for a specific branch only:

```bash
git branch -r | grep add-base-prompts
```

- Output exists → remote branch exists
- No output → remote branch does not exist

This is the most commonly used method in daily development.

---

## 4. Authoritative Check (Remote Source of Truth)

To query the remote repository directly (not affected by local cache):

```bash
git ls-remote --heads origin
```

Or filter for a specific branch:

```bash
git ls-remote --heads origin | grep add-base-prompts
```

If a result is returned, the branch exists on the remote.

---

## 5. What to Do Based on the Result

### Case A: Remote Branch Exists

```text
origin/feature/add-base-prompts
```

- The branch has already been pushed
- You can continue development or open a Pull Request

No further action required.

---

### Case B: Remote Branch Does Not Exist

- The branch exists only locally
- Push it to the remote when ready:

```bash
git push -u origin feature/add-base-prompts
```

After this:
- The remote branch will exist
- Future `git push` / `git pull` commands will not require specifying the branch name

---

## Summary

- Always `git fetch --prune` before checking
- Use `git branch -r | grep <branch>` for quick checks
- Use `git ls-remote --heads origin` for authoritative confirmation
- Only delete feature branches **after** they have been merged

This workflow helps keep branch management clean, predictable, and professional.
