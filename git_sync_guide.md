# Git Sync Guide: Local Branch + Remote Workflow

This document helps you understand and operate Git safely in a multi-branch project, especially when working with `main` and a feature/dev branch like `aws-dev`.

---

## ✅ When to Use
Any time you:
- Start a new development task
- Finish a PR and want to continue developing
- See messages like "diverged", "conflict", or "out of date"

---

## 📚 Branch Definitions
| Name | Type | Meaning |
|------|------|---------|
| `main` | Local | Your local main branch |
| `origin/main` | Remote | GitHub main branch (remote-tracking) |
| `aws-dev` | Local | Your feature or dev branch |
| `origin/aws-dev` | Remote | GitHub version of your dev branch |

---

## 🚀 Standard Daily Development Workflow
```bash
# 1. Checkout your working branch
git checkout aws-dev

# 2. Fetch latest from GitHub
git fetch origin

# 3. Merge latest main into your dev branch
git merge origin/main

# (Optional) Resolve merge conflicts, then:
git add .
git commit
```

---

## ⚡️ Use Temporary Backup Branch Before Risky Merge
```bash
# Before merging main or remote changes:
git checkout aws-dev
git checkout -b aws-dev-backup

# Then go back and merge
git checkout aws-dev
git merge origin/main
```
If anything breaks:
```bash
git checkout aws-dev-backup
git checkout -b aws-dev
```

---

## ♻️ After PR Merged to Main
```bash
# 1. Sync your local main
git checkout main
git pull origin main

# 2. Bring changes into dev branch
git checkout aws-dev
git merge main
```

---

## 🔍 `merge origin/xxx` vs `merge xxx`

| Command | Merges From | To | Use When |
|---------|-------------|----|----------|
| `git merge origin/aws-dev` | Remote GitHub aws-dev | Local aws-dev | Others pushed to GitHub aws-dev |
| `git merge main` | Local main (must pull first) | Local aws-dev | You just merged a PR to GitHub main |

### Rule of Thumb
> "别人动了 GitHub 的 aws-dev → merge origin/aws-dev"
>
> "我自己合并了 PR 到 main → merge main"

---

## 🔎 `origin` means REMOTE (GitHub)
- `origin` is the name of GitHub as your remote
- `origin/main` is the version of main on GitHub
- `origin/aws-dev` is the version of aws-dev on GitHub

These are read-only snapshots, updated via:
```bash
git fetch origin
```
You must merge manually to apply them.

---

## 💼 Optional Recovery
```bash
# Undo a broken merge
git merge --abort

# Reset to previous commit (use with care)
git reset --hard HEAD~1
```

---

## 🚮 How to Delete a Temporary Backup Branch

### Delete local backup branch only:
```bash
git branch -d aws-dev-backup       # Safe delete (if merged)
git branch -D aws-dev-backup       # Force delete (use with caution)
```

### Delete remote backup branch from GitHub:
```bash
git push origin --delete aws-dev-backup
```

### Delete both:
```bash
git push origin --delete aws-dev-backup
git branch -d aws-dev-backup
```

### Check what branches you have:
```bash
git branch        # List local branches
git branch -r     # List remote branches
```

---

## 🎓 Learn More
- [Git merge vs rebase (Atlassian)](https://www.atlassian.com/git/tutorials/merging-vs-rebasing)
- [Understanding origin and upstream](https://stackoverflow.com/a/9257901)
- [GitHub CLI PR management](https://cli.github.com/manual/gh_pr)

---

## 🚀 Git Mermaid Flow Diagram Available in `git_sync_flow.md`
