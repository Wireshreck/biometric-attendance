# Backup and Recovery Plan

**Status:** The helper creates an unencrypted content ZIP and includes a verified Git bundle when a commit exists; this repository currently has no commit. A restore has not been verified. The helper can optionally snapshot a synthetic demo DB through SQLite's online backup API. Do not use it for real personal/biometric data.

## What to preserve

- Git history (bundle) and working-tree source snapshot: firmware, backend, frontend, docs, diagrams, hardware, scripts, presentation, `.github`, README/license, and Obsidian vault.
- Runtime database only when using synthetic demo data and explicitly requested. Use SQLite online backup API to capture a consistent snapshot; never copy only an active WAL database file.
- Local secrets are excluded. Back up configuration templates (`.env.example`, `local_config.example.h`) only; re-enter local secrets after recovery.
- Exclude `.venv`, `.pio`, `node_modules`, caches, and generated build outputs; these can be rebuilt.

## Frequency and storage

Before a schema migration, after meaningful source milestones, and before travel/demo, create a content backup. A future operational system needs an institution-approved retention/access scheme. Apply the 3-2-1 rule only after selecting two independent media and one off-site location; the repository currently has no remote, and the helper does not automate external copies. Encrypt any backup containing personal data before it leaves the protected host. Do not rely on the ZIP helper for encryption.

## Create and restore

Create a source snapshot outside the repository:

```powershell
pwsh .\scripts\backup-project.ps1 -Destination 'D:\Backups'
```

Restore a ZIP to a new empty folder (never over the active workspace), inspect the manifest, create a fresh venv, install dependencies, build firmware, and run the environment checks. If Git history was bundled, verify it with `git bundle verify` and clone from the bundle into a separate folder.

For a synthetic demo DB, make a consistent SQLite online backup before zipping. Restore it to a temporary copy, run `PRAGMA integrity_check;` and `PRAGMA foreign_key_check;`, and compare expected synthetic record counts. Record restore date/result. A backup is not verified until this recovery test passes.

## Recovery limits

No production DB exists in this project. If hardware is lost, rebuild from source/BOM; fingerprint templates remain sensor-local and cannot be reconstructed from source backups. Re-enroll only consenting synthetic test fingers after hardware recovery. Lost tokens/passwords must be regenerated locally and device tokens revoked/reprovisioned.
