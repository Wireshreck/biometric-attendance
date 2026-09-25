---
type: project-handoff
status: VERIFIED
updated: 2026-09-25
---

# AI Project Handoff

## Project and vault

Biometric School Attendance System: a science-fair local attendance demonstrator. The **repository root is the Obsidian vault**; open `C:\Users\user\projects\fair\biometric-attendance` in Obsidian. The root `.obsidian/` is local UI/workspace state and is ignored. Start at [[00 - Project Overview]], use [[Architecture.canvas]] to navigate actual repo files, and follow [[AI Development Guide]] before changing code.

## Current verified repository state (2026-09-25)

- Git: branch `main`; baseline commit `9bb5801` (`Initial project baseline`) is preserved. The completed milestone is `310559e` (`feat: add SQLite schema v1 and Obsidian handoff workspace`), one local commit ahead of `origin/main` (`https://github.com/Wireshreck/biometric-attendance.git`); it has not been pushed. Author identity is configured; `gh auth status` reported `Wireshreck` authenticated.
- Firmware: only a toolchain-check sketch and configuration; `pio run -d firmware` compiled successfully on 2026-09-25. No board flash or physical test, sensor enrollment, attendance loop, RTC integration, display behavior, networking, authentication, or offline queue.
- Backend: dependency manifests, `.env.example`, environment/SQLite smoke check, schema v1 migration/connection setup, and migration tests. No FastAPI app or routes exist.
- Frontend: plan only; no HTML/CSS/JS implementation.
- Hardware: planning and provisional wiring only. Procurement, arrival, exact variants, and measurements are unknown.
- Docs: canonical requirements, architecture, API/database, security/privacy, testing, hardware, deployment, backup, and presentation plans exist. Treat plans as plans.
- CI/GitHub: workflow files exist; do not assume a successful run.

## Decisions and constraints

See [[Decision Log]] for decision rationale and status. Key constraints: synthetic demo records only; no live-school use; local HTTP is unencrypted; sensor template/liveness properties are unverified; no raw fingerprint/template payload is designed to leave the sensor; enrollment/deactivation uses local USB serial in the MVP; duplicate events within 60 seconds of an accepted event are suppressed, later same-day scans may record; event UUID replay is idempotent; AI is deferred/read-only.

## Current blockers and next work

1. **API-01 — backend vertical slice:** use the database module to implement configuration, health, authentication, and student state. Schema v1 is the current independent implementation milestone.
2. **HW-01 — procurement facts:** owner must confirm purchase/delivery and exact module revisions; do not infer from old target dates.
3. **Hardware-dependent work:** physical voltage, pinout, sensor, RTC, and display tests require exact parts and safe bench measurements.
4. After DB-01, implement API configuration/auth/health and student state; then attendance ingestion; then firmware/UI integration per [[TODO]] and `docs/project-plan.md`.

## Checks run during the current handoff

- Backend environment smoke check passed under `backend/.venv`: pinned dependency imports and a temporary SQLite file/WAL/foreign-key/CRUD check. Database migration/constraint tests: 6 passed with pytest on 2026-09-25.
- PowerShell scripts and `backend/pyproject.toml` parsed; authored Markdown relative links and the Canvas JSON were checked.
- `pio run -d firmware` passed on 2026-09-25. It emitted one warning from the pinned Arduino framework's `uartSetPins` implementation; the validation sketch itself compiled. No firmware was flashed or hardware behavior verified.
- The database migration/constraint suite passes; no API/attendance/UI/integration suite or hardware test has passed.

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
