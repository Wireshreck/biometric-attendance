# Git and GitHub Setup

**Current state (2026-09-24):** local Git repository is initialized, has no commit or remote. Git author identity is not configured. GitHub CLI is installed but unauthenticated. No repository destination/owner is established. GitHub actions/workflow files exist but have not run on GitHub.

## Local workflow

1. Review `git status --short --ignored`; `.gitignore` excludes virtualenvs, `.pio`, databases, local configs, credentials and Obsidian workspace layout while tracking markdown/canvas notes.
2. Set your actual local author identity (do not use the project placeholder as a personal identity):
   ```powershell
   git config user.name "Your Name"
   git config user.email "you@example.com"
   ```
3. Review changes, stage an intentional baseline, inspect `git diff --cached`, then commit:
   ```powershell
   git add .
   git status --short
   git diff --cached --check
   git diff --cached
   git commit -m "chore: establish project foundation"
   ```
4. Use a short-lived `feature/<topic>` branch; make focused commits. Merge through a reviewed pull request to `main`. Keep `main` releasable. A separate `develop` branch is not required for this small project.
5. Tag a demonstrated/verified milestone only after recording the tested commit and results, e.g. `v0.1.0-demo`; do not tag planning work as a release.

Before staging, scan for private config and personal data. Confirm ignored artifacts with `git check-ignore -v <path>`. Never commit `backend/.env`, `firmware/include/local_config.h`, SQLite files, student data, biometric data, or unencrypted sensitive backups.

## Optional GitHub remote (not configured)

Only after choosing the account, repository name, visibility, and owner, authenticate with `gh auth login`, verify `gh auth status`, create or select that exact repository, inspect the destination, then add a remote and push only the intended branch. Do not run repository-creation or push commands until those choices are explicit.

The script `scripts/create-github-milestones-and-issues.ps1` currently provisions milestones only despite its filename; it does not create issues. It requires an authenticated CLI and a configured repository remote. Run only after reviewing the due dates and target. GitHub issue templates and PR template are present. CI currently compiles firmware and runs a backend dependency/SQLite smoke check; it does not run product tests because none exist.

No remote, repository URL, issue tracker, milestone state, release, or CI result is claimed as configured.
