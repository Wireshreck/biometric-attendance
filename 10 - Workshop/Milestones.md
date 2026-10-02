---
type: project
area: workshop
status: active
tags:
  - milestones
  - status
  - active-work
---

# Milestones

**HOME** [[00 - Vault Hub]] · **UP** [[10 - Workshop]] · **RELATED** [[10 - Workshop/TODO|TODO]] [[10 - Workshop/AI Project Handoff|AI Project Handoff]] [[09 - Decision Room/Decision Log]] · **CANVAS** [[10 - Workshop/10 - Workshop.canvas]]

This is a status index, not a second schedule or task tracker. Individual tasks and completion evidence live in [[10 - Workshop/TODO|TODO]]. Target dates, dependency gates, and fair contingency live in `docs/science-fair-timeline.md`.

| Milestone | Status | Exit evidence / source |
| --- | --- | --- |
| Foundation and repository baseline | VERIFIED | Baseline `9bb5801` preserved; current milestone `310559e`; source-of-truth map is in [[10 - Workshop/AI Project Handoff|AI Project Handoff]] |
| Obsidian workspace and handoff | VERIFIED | Repository root is the vault; `00 - Vault Hub.md`, `00 - Master Canvas.canvas`, 10 area hubs, 12 canvases, ADR, task tracker and AI guide/handoff — see [[00 - Vault Hub]] and [[docs/VAULT-AUDIT.md]] |
| Database foundation | VERIFIED | Schema v1, transactional migrations, temporary database constraints/rollback tests; 6 tests passed; milestone commit `310559e`, see DB-01 in [[10 - Workshop/TODO|TODO]] |
| Backend/API vertical slice | VERIFIED (local and CI software tests) | 10 backend tests pass; implementation/fix commits `42c0849` and `a7aa14e`; GitHub Actions `36148997541` passed; see API-01/API-02 |
| Remaining API: reports, CSV, SSE, device lifecycle | PLANNED | Contract and security tests; see API-03 |
| Reproducible human build guide | IN PROGRESS | Software setup recorded; hardware/procurement and product integration gates remain; see `docs/COMPLETE-BEGINNER-ASSEMBLY-GUIDE.md`, `docs/complete-breadboard-layout.md`, [[02 - Hardware Lab]] and BUILD-01 |
| Firmware test infrastructure | VERIFIED (build-only) | Production/runtime and 25 isolated component/integration environments compile; see FW-01 in [[10 - Workshop/TODO|TODO]] and `docs/component-tests.md` |
| Production firmware workflow | IMPLEMENTED (build-only) | Matching/enrollment, RTC gate, journal/replay and API client in `docs/production-firmware.md`; hardware/API device integration remains NEEDS HARDWARE |
| Beginner setup documentation | IMPLEMENTED; NEEDS HARDWARE | `docs/COMPLETE-BEGINNER-ASSEMBLY-GUIDE.md`, `docs/complete-breadboard-layout.md`, `docs/COMPLETE-SOFTWARE-SETUP.md`, `docs/SCIENCE-FAIR-SETUP.md` |
| Hardware/firmware physical validation | NEEDS HARDWARE | Exact parts and safe bench evidence; R307S supply/UART state unverified; see `hardware/test-plan.md` |
| Dashboard | PLANNED | Accessible UI with real API/SSE behavior; see UI-01/UI-02 |
| Integrated demo and verification | NEEDS HARDWARE | Repeatable enrollment-to-dashboard trace, outage recovery and restore evidence; see INT-01/DEMO-01 |

Only change a milestone to VERIFIED after recording the exit evidence and the commit that contains it. AI remains deferred and is not a release gate.
