---
type: reference
area: documentation
status: active
tags:
  - operations
  - reference
  - agent-guide
---

# AI Development Guide

**HOME** [[00 - Vault Hub]] · **UP** [[08 - Documentation Library]] · **RELATED** [[10 - Workshop/AI Project Handoff]] [[00 - Vault Hub]] · **CANVAS** [[08 - Documentation Library/08 - Documentation Library.canvas]]

This file is the operating guide for AI agents and human contributors. **Open the repository root as the project vault** and start at `00 - Vault Hub.md`. The numbered `00`-`10` area folders contain the hubs, canvases, task tracker, decisions, milestones and handoff. Canonical implementation/design files remain in the repository's `firmware/`, `backend/`, `docs/`, and other source directories.

## Project overview

The project is a local-first science-fair attendance demonstrator based on an ESP32 + R307S, local FastAPI service, and SQLite. Firmware implements sensor matching/two-capture enrollment, RTC timestamp gating, OLED/indicator services, a LittleFS append journal/replay, and the backend's authenticated API contract. The runtime builds but has no full physical pass evidence; the owner reports the R307S returns zero UART bytes and its rail/TX level remain unmeasured. The backend vertical slice is tested; browser dashboard and later reports/API features remain planned. Use synthetic identities and consenting adult testers. The optional local AI reporting layer is deferred and must stay read-only and unnecessary for core operation.

## Repository map

| Path | Purpose / current state |
| --- | --- |
| `firmware/` | PlatformIO production runtime, device/network/storage modules, isolated component/integration tests and read-only R307S diagnostic |
| `backend/` | SQLite schema v1, tests, and partial FastAPI app (health, student/enrollment, attendance ingest); reports/CSV/SSE/device lifecycle remain planned |
| `frontend/` | Dashboard plan only; no UI source |
| `hardware/` | Provisional pinout and physical bring-up gates; parts and measurements unconfirmed |
| `docs/` | Canonical requirements, architecture, subsystem designs, setup, security, and test plans |
| `diagrams/` | Canonical Mermaid architecture/data/hardware flow diagrams |
| `scripts/` | Environment validator, backup helper, and guarded GitHub milestone helper |
| `presentation/` | Draft demo script, outline, and judge questions; claims must follow verified evidence |
| `00`–`10` area folders + `00 - Vault Hub.md` | Obsidian navigation, task/decision/milestone control, this guide, and handoff |
| `.github/` | Repository issue templates and CI workflow; GitHub workflow result is not assumed |

## Source of truth

Do not maintain parallel copies of technical specifications. Use these canonical sources:

| Topic | Authoritative file |
| --- | --- |
| Requirements | `docs/requirements.md` |
| Requirement implementation/test traceability | `docs/requirements-traceability.md` |
| Architecture and data/failure flows | `docs/architecture.md`; diagrams in `diagrams/` |
| Hardware, safe wiring, BOM/procurement | `docs/hardware.md`, `docs/wiring.md`, `docs/bill-of-materials.md`, `docs/purchase-checklist.md`; physical gates in `hardware/test-plan.md` |
| Human construction procedure | `docs/COMPLETE-BEGINNER-ASSEMBLY-GUIDE.md`, `docs/complete-breadboard-layout.md`, and `docs/final-pin-map.md`; physical mapping/measurements remain unverified |
| Firmware | `firmware/README.md`, `firmware/platformio.ini`, `docs/production-firmware.md`, and actual sources under `firmware/src/` / `firmware/include/` |
| Backend | `backend/README.md`, `backend/pyproject.toml`, and actual sources/tests under `backend/app/` and `backend/tests/` |
| Database | `docs/database-plan.md` and checked-in migrations under `backend/migrations/` when implemented |
| API | `docs/api-plan.md` status matrix and actual route code/tests in `backend/app/main.py` and `backend/tests/test_api.py` |
| Frontend | `frontend/README.md` and actual UI assets when added |
| Testing | `docs/testing-plan.md`, `docs/requirements-traceability.md`, and executable tests in the owning subsystem |
| Security/privacy | `docs/privacy-security.md` and root `SECURITY.md` |
| Deployment/backup | `docs/deployment-plan.md`, `docs/backup-strategy.md`, and scripts |
| Project status/tasks | `10 - Workshop/TODO.md` (single task tracker) |
| Decisions | `09 - Decision Room/Decision Log.md` |
| Dates/milestone evidence | `10 - Workshop/Milestones.md` links to `docs/science-fair-timeline.md` |
| AI operating instructions / current handoff | This guide and `10 - Workshop/AI Project Handoff.md` |

The numbered notes `00`–`17` are entry points/status summaries. Keep them short and link to the canonical file rather than duplicating its specification.

## Status vocabulary

Use only these status labels in project status fields and task tracking:

- **PLANNED** — specified but implementation has not started.
- **IN PROGRESS** — implementation or a defined work item is actively underway.
- **IMPLEMENTED** — code/artifact exists; it has not passed its required verification.
- **VERIFIED** — the stated check passed; record the command/evidence and scope.
- **BLOCKED** — an external decision or prerequisite prevents progress.
- **DEPRECATED** — superseded; link to the replacement and preserve rationale.
- **NEEDS HARDWARE** — requires physical parts or bench access.
- **NEEDS TESTING** — implementation exists, but the relevant test/evidence is outstanding.
- **DEFERRED** — intentionally postponed, optional scope that is not a current release dependency.
- **DECIDED**, **PROVISIONAL**, and **DEFERRED** may appear in ADR decision fields only: accepted project choices, choices awaiting hardware/evidence, and intentionally postponed scope.

An existing plan or note is not evidence that its product feature is implemented. A passing environment smoke check is not an API test; a compile is not a hardware test. Scope statuses explicitly (e.g., “DB migrations: IMPLEMENTED; API: PLANNED”).

## Development workflow

1. Read [[00 - Vault Hub]], this guide, [[10 - Workshop/TODO|TODO]], and [[10 - Workshop/AI Project Handoff|AI Project Handoff]].
2. Check `git status`, branch, recent commits, remotes, and existing local changes before editing. Do not reset, reinitialize, or overwrite the user's work.
3. Read the relevant requirement, canonical plan, decision records, and implementation/configuration files. Search for existing partial work and tests.
4. Confirm the task's dependency and status in `TODO.md`; choose the smallest coherent milestone.
5. Implement only what the contract supports. If the contract is ambiguous, inspect the source requirement and record an ADR for a lasting decision.
6. Update implementation, tests, canonical docs, subsystem navigation note, `TODO.md`, and the Canvas relationships when relevant.
7. Run checks appropriate to the change. Report exact commands and results; label hardware-dependent checks **NEEDS HARDWARE**.
8. Review `git diff --check`, full diff, secrets/ignored files, and status. Stage only intended files and inspect the staged diff.
9. Make a focused commit at a coherent milestone with a clear message. Do not push unless explicitly requested. Do not force-push or rewrite shared history.
10. Push a milestone only when explicitly requested; otherwise leave the reviewed commit local. Update the handoff/status so the next agent has current context.

## Rules for agents

- Inspect actual source before saying functionality exists. Never infer implementation from diagrams or plans.
- Keep docs synchronized with behavior and distinguish planned, implemented, and verified scope.
- Do not invent sensor behavior, template properties, voltage tolerance, purchases, measurements, test outcomes, or security guarantees. The exact R307S unit's electrical state is unverified; do not alter wiring on assumptions or claim library/protocol compatibility until a bench handshake succeeds.
- Protect credentials, local config, student identity, attendance data, and biometric data. Use synthetic data. Never add secrets to examples or Git.
- Do not casually move/delete existing files, duplicate specifications, change architecture, or add dependencies/frameworks without a concrete need.
- Do not send biometric images/templates to cloud services. The planned prototype HTTP transport is unencrypted and is restricted to synthetic demo data on an isolated network.
- Update the vault home/tracker/Canvas after major structure, status, or architecture changes. Record durable design choices in the decision log.
- Do not claim CI, hardware, or product tests passed unless you ran them and captured the evidence.

## Safe local checks

From the repository root in PowerShell:

```powershell
& .\backend\.venv\Scripts\python.exe .\backend\test_env.py
Push-Location .\backend
try { & .\.venv\Scripts\python.exe -m pytest .\tests } finally { Pop-Location }
pio run -d .\firmware
git diff --check
git status --short
```

`test_env.py` is an environment/SQLite smoke check, not an API test. Pytest includes database and API tests for the implemented slice; it does not verify physical sensor behavior or full integration. PlatformIO may need network access to fetch its pinned toolchain; flashing and sensor checks require hardware. Use the exact commands in each subsystem README and test plan.
