# Authoritative Project Task Tracker

[[00 - Project Overview|⬅️ Back to Hub]]

This is the sole project task tracker. Detailed requirements/test cases stay in [traceability](../../docs/requirements-traceability.md); procurement tick marks stay in [purchase checklist](../../docs/purchase-checklist.md). Status reflects inspected workspace as of 2026-09-24. `DONE` means the named planning/configuration artifact exists or the stated check was performed; product behavior remains unimplemented.

Status meanings: **BLOCKED** = external prerequisite; **NEXT** = immediate action; **IN PROGRESS** = actively underway; **READY** = unblocked planned task; **DONE** = evidence recorded; **OPTIONAL** = deferred and non-blocking.

| ID | Task | Phase | Priority | Status | Depends on | Related source/component | Completion criteria |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FND-01 | Inventory repository, environment, plans, source and vault; record implementation status | Foundation | P0 | DONE | — | This tracker, README, docs | Current file inventory and missing app code recorded |
| FND-02 | Establish requirements-to-test traceability and align duplicate rule/schema | Foundation | P0 | DONE | FND-01 | requirements, database, testing plans | FR/NFR map exists; 60s semantics consistent; verification IDs assigned |
| FND-03 | Remove hard-coded demo password; ignore generated caches/local secrets | Foundation | P0 | DONE | FND-01 | firmware config, `.gitignore` | Defaults empty; local config ignored; `.pio` and `.venv` ignored |
| FND-04 | Create numbered vault notes 00–17 and architecture canvas; cross-link canonical plans | Foundation | P1 | DONE | FND-01 | `obsidian/Attendance System/` | All notes and canvas exist; JSON canvas parses |
| HW-01 | Confirm purchase/delivery status and exact board/module revisions; update receipt/price ledger | Procurement | P0 | NEXT | Owner purchase decision | purchase checklist, BOM | Each item has exact variant, seller, paid cost, order/delivery status |
| GIT-01 | Set actual local Git author identity; inspect/stage/commit foundation baseline | Development | P0 | BLOCKED | Owner identity | Git, github setup | User name/email configured; staged diff reviewed; baseline commit exists |
| HW-02 | Bring up power, safe I2C, LEDs/buzzer and AS608 UART individually | Hardware | P0 | BLOCKED | HW-01 (hardware received) | wiring, hardware test plan | Record module IDs/voltage measurements; pass HW-01..07 gates |
| FW-01 | Add explicit PlatformIO diagnostic environments and pass board/peripheral checks | Firmware | P0 | READY | HW-02 | firmware | Reproducible compile plus physical I2C/UART/output evidence |
| DB-01 | Implement schema migrations, connection pragmas, synthetic fixtures and migration tests | Backend | P0 | READY | FND-02 | database-plan, backend | Clean DB and migration tests pass; foreign keys/WAL checked |
| API-01 | Implement config/auth/health/student create/list/deactivate and enrollment state routes | Backend | P0 | READY | DB-01 | api-plan, backend | Contract tests cover validation, access control and transitions |
| API-02 | Implement attendance ingest, event UUID idempotency, 60s suppression, timestamp/timezone policy | Backend | P0 | READY | DB-01, API-01 | api-plan, database-plan | Boundary/concurrency/replay tests pass |
| FW-02 | Implement local sensor enrollment/match, generic feedback, RTC validation and safe errors | Firmware | P0 | BLOCKED | HW-02, FW-01 | firmware, requirements | Enrollment/match/delete verified; performance measured; no PII on OLED |
| FW-03 | Implement bounded durable LittleFS queue and acknowledged chronological replay | Firmware | P0 | READY | FW-02, API-02 | firmware, data-flow diagram | Power-cut/retry/full-queue tests; stable event UUID; no silent loss |
| UI-01 | Implement student, attendance/report, export and system/device views in vanilla web stack | Frontend | P0 | READY | API-01, API-02 | frontend, api-plan | Empty/error/loading/accessibility states covered by UI tests |
| UI-02 | Implement authenticated SSE and reconnect/resume without duplicate display | Frontend/backend | P1 | READY | API-02, UI-01 | API, frontend | `Last-Event-ID` and <=500ms visibility measured |
| INT-01 | Run synthetic-data enrollment-to-dashboard and offline recovery end-to-end | Integration | P0 | BLOCKED | HW-02, API-02, FW-03, UI-01 | testing-plan | All linked test IDs pass with event/accounting evidence |
| SEC-01 | Review network exposure, retention/deletion, backups, secrets and threat limitations | Security | P0 | READY | API/firmware implementation | privacy-security, SECURITY | Review recorded; no secrets; demo remains synthetic-only |
| DEMO-01 | Prepare honest demo, fallback screenshots/mock sequence, restore-tested backup and rehearsal | Delivery | P1 | READY | INT-01 | science-fair plan/presentation | Claims limited to measured results; backup restored successfully |
| AI-01 | Consider local aggregate-only read-only assistant | Optional | P2 | OPTIONAL | Tested core MVP and explicit privacy review | ai-plan | Remains off unless separate decision and tests justify it |

## Current blockers

- The physical purchase/arrival state is unknown; hardware tests and firmware bring-up depend on actual parts.
- Git author identity is absent. The local repository is initialized, but has no commit, remote, or GitHub login.
- No backend application, UI, attendance firmware, migrations, or product test suite exists yet.

## Milestone outlook

Dates in the existing fair schedule are targets, not evidence or commitments. With hardware order/delivery unconfirmed and product code absent, Oct 1/4/6 gates are high-risk. Re-plan actual dates after HW-01 and keep a no-hardware mock/software demo fallback. See [timeline](../../docs/science-fair-timeline.md).
