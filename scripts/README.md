# Maintenance Scripts

Scripts use paths relative to this checkout except where a destination is explicitly supplied. Review them before use.

| Script | Behavior | Current limit |
| --- | --- | --- |
| `validate-environment.ps1` | Checks tool presence, backend environment/WAL smoke check if venv exists, PlatformIO build, serial ports, and Git identity/status | Not application/product tests; missing GitHub CLI is informational |
| `backup-project.ps1` | Makes a content ZIP outside repo; excludes secrets, DB, caches and build outputs; adds verified Git bundle when a commit exists | Unencrypted; no restore is claimed; optional DB switch is explicitly only for synthetic data; currently no commit exists |
| `create-github-milestones-and-issues.ps1` | Legacy filename; creates missing milestones for configured `origin` | Does not create issues; requires authenticated `gh`, intended remote and schedule review |

Usage and restore limits: [backup plan](../docs/backup-strategy.md). GitHub prerequisites: [setup guide](../docs/github-setup.md).
