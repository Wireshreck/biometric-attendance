---
type: project-handoff
status: IN PROGRESS
updated: 2026-09-25
---

# AI Project Handoff

## Project and vault

Biometric School Attendance System: a science-fair local attendance demonstrator. The **repository root is the Obsidian vault**; open `C:\Users\user\projects\fair\biometric-attendance` in Obsidian. The root `.obsidian/` is local UI/workspace state and is ignored. Start at [[00 - Project Overview]], use [[Architecture.canvas]] to navigate actual repo files, and follow [[AI Development Guide]] before changing code.

## Current verified repository state (2026-09-25)

- Git: API implementation milestone is commit `42c0849` on existing `main`; baseline and prior history are preserved. `origin` remains configured. Run `git status --short --branch`, `git log --oneline --decorate -5`, and `git rev-list --left-right --count origin/main...HEAD` for current synchronization; never reset or rewrite shared history. Check the latest GitHub Actions run directly for CI status.
- Firmware: only a toolchain-check sketch and configuration; `pio run -d firmware` compiled successfully on 2026-09-25. No board flash or physical test, sensor enrollment, attendance loop, RTC integration, display behavior, networking, authentication, or offline queue.
- Backend: schema v1 and migrations; FastAPI implements `/health`, admin student list/create/read/deactivate, authenticated device enrollment assignment/completion, and authenticated atomic attendance ingestion. Student creation assigns an available slot only after a single active device has reported capacity. Device bearer tokens are SHA-256 hashed in SQLite; admin Basic credentials come from `.env`. Reports, attendance query, CSV, SSE, device heartbeat/status/cleanup/deletion, frontend/static serving, and integration are not implemented.
- API verification: 10 pytest tests pass (6 migration/constraint and 4 API/provisioning tests). Coverage includes 60-second duplicate suppression, 61-second acceptance, UUID replay, validation/auth/slot errors, enrollment/deactivation state, and hash-only device provisioning. Temporary databases and synthetic identities only; no physical sensor or firmware was exercised.
- Frontend: plan only; no HTML/CSS/JS implementation.
- Hardware: planning and provisional wiring only. Procurement, arrival, exact variants, and measurements are unknown.
- Build instructions: [[18 - Complete Build Guide]] is an honest in-progress guide. The software setup is executable; physical wiring and full-system procedure have hardware/implementation stop gates because component revisions and verified electrical data are unknown.
- Docs: canonical requirements, architecture, API/database, security/privacy, testing, hardware, deployment, backup, and presentation plans exist. Use their status labels; treat remaining API/UI/hardware plans as plans.
- CI/GitHub: workflow files exist; do not assume a successful run.

## Decisions and constraints

See [[Decision Log]] for decision rationale and status. Key constraints: synthetic demo records only; no live-school use; local HTTP is unencrypted; sensor template/liveness properties are unverified; no raw fingerprint/template payload is designed to leave the sensor; enrollment/deactivation uses local USB serial in the MVP; duplicate events within 60 seconds of an accepted event are suppressed, later same-day scans may record; event UUID replay is idempotent; AI is deferred/read-only.

## Current blockers and next work

1. **API-03:** implement report/query, CSV-safe export, SSE, device management/heartbeat and cleanup/delete operations according to `docs/api-plan.md`.
2. **HW-01:** purchase/delivery and exact module revisions need owner confirmation; do not infer from dates or provisional BOMs.
3. **Hardware-dependent work:** electrical checks, pinout, sensor, RTC and display tests require exact parts and safe bench measurements.
4. Continue with frontend/API and firmware integration after API-03, following [[TODO]] and `docs/project-plan.md`.

## Checks run during the current handoff

- Backend environment smoke check passed under `backend/.venv`; `python -m pytest tests -q` passed 10 tests on 2026-09-25 (6 DB + 4 API/provisioning). One third-party Starlette/AnyIO deprecation warning remains.
- PowerShell scripts and `backend/pyproject.toml` parsed; authored Markdown relative links and the Canvas JSON were checked.
- `pio run -d firmware` passed on 2026-09-25. It emitted one warning from the pinned Arduino framework's `uartSetPins` implementation; the validation sketch itself compiled. No firmware was flashed or hardware behavior verified.
- The database migration/constraint and API vertical-slice suites pass. No UI, full firmware/attendance, end-to-end integration, or hardware test has passed.

## Git workflow

Review status, branch, and `git log --oneline` before work. Stage intentional paths, inspect the staged diff, run checks, and create a focused milestone commit using the verified local identity. Do not reinitialize Git, remove history, force-push, or push unless the user asks.

## Where to continue

- Project tasks: [[TODO]]
- Visual map of file-backed nodes/dependencies: [[Architecture.canvas]]
- Requirements/design: `docs/requirements.md`, `docs/architecture.md`
- Database/API: `docs/database-plan.md`, `docs/api-plan.md`
- Implementation state: `firmware/README.md`, `backend/README.md`, `frontend/README.md`
- Tests/evidence: `docs/testing-plan.md`, `hardware/test-plan.md`
- Project workflow: `docs/github-setup.md`
