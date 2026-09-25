# Git and GitHub Setup

**Current state (checked 2026-09-25):** local repository root is on `main`; baseline `9bb5801` (`Initial project baseline`) is preserved. The current database/Obsidian milestone `310559e` is one local commit ahead of `origin/main` at `https://github.com/Wireshreck/biometric-attendance.git` and has not been pushed. A local author identity is configured; `gh auth status` reports an authenticated `Wireshreck` account. No claim is made that CI has run successfully.

## Local workflow

1. Review `git status --short --ignored`; `.gitignore` excludes virtualenvs, `.pio`, databases, local configs, credentials and Obsidian workspace layout while tracking markdown/canvas notes.
2. Confirm the configured author identity is yours before creating commits; change it locally if needed:
   ```powershell
   git config user.name "Your Name"
   git config user.email "you@example.com"
   ```
3. Review changes, stage only the paths for this milestone, inspect `git diff --cached`, then commit. Adapt this example to the completed milestone:
   ```powershell
   git add README.md docs/database-plan.md backend/app backend/migrations backend/tests
   git status --short
   git diff --cached --check
   git diff --cached
   git commit -m "feat(database): add transactional schema v1"
   ```
4. Use a short-lived `feature/<topic>` branch; make focused commits. Merge through a reviewed pull request to `main`. Keep `main` releasable. A separate `develop` branch is not required for this small project.
5. Tag a demonstrated/verified milestone only after recording the tested commit and results, e.g. `v0.1.0-demo`; do not tag planning work as a release.

Before staging, scan for private config and personal data. Confirm ignored artifacts with `git check-ignore -v <path>`. Never commit `backend/.env`, `firmware/include/local_config.h`, SQLite files, student data, biometric data, or unencrypted sensitive backups.

## Remote and GitHub workflow

The existing `origin` remote points to the project repository. Do not recreate it. Before pushing, inspect the branch and staged diff, run relevant checks, and confirm the destination. Do not force-push or rewrite shared history.

The script `scripts/create-github-milestones-and-issues.ps1` currently provisions milestones only despite its filename; it does not create issues. It requires an authenticated CLI and a configured repository remote. Run only after reviewing the due dates and target. GitHub issue templates and PR template are present. CI is configured to compile firmware, run the backend environment/SQLite smoke check, and run database migration/constraint tests; no successful hosted CI result is recorded.

The repository URL and authenticated CLI were checked locally. No issue tracker/milestone provisioning, release, or successful CI result is claimed unless recorded separately.
