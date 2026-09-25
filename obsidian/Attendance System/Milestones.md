---
type: milestone-index
status: IN PROGRESS
updated: 2026-09-25
---

# Milestones

This is a status index, not a second schedule or task tracker. Individual tasks and completion evidence live in [[TODO]]. Target dates, dependency gates, and fair contingency live in `docs/science-fair-timeline.md`.

| Milestone | Status | Exit evidence / source |
| --- | --- | --- |
| Foundation and repository baseline | VERIFIED | Baseline `9bb5801` preserved; current milestone `310559e`; source-of-truth map is in [[AI Project Handoff]] |
| Obsidian workspace and handoff | VERIFIED | Root vault, file-backed [[Architecture.canvas]], AI guide/handoff, ADR, and task tracker cross-links reviewed |
| Database foundation | VERIFIED | Schema v1, transactional migrations, temporary database constraints/rollback tests; 6 tests passed; milestone commit `310559e`, see DB-01 in [[TODO]] |
| Backend/API vertical slice | VERIFIED (software tests) | Authenticated student/enrollment/attendance slice; 10 backend tests pass; see API-01/API-02 |
| Remaining API: reports, CSV, SSE, device lifecycle | PLANNED | Contract and security tests; see API-03 |
| Reproducible human build guide | IN PROGRESS | Software setup recorded; hardware/procurement and product integration gates remain; see [[18 - Complete Build Guide]] and BUILD-01 |
| Hardware/firmware | NEEDS HARDWARE | Exact parts and safe bench evidence; see `hardware/test-plan.md` |
| Dashboard | PLANNED | Accessible UI with real API/SSE behavior; see UI-01/UI-02 |
| Integrated demo and verification | NEEDS HARDWARE | Repeatable enrollment-to-dashboard trace, outage recovery and restore evidence; see INT-01/DEMO-01 |

Only change a milestone to VERIFIED after recording the exit evidence and the commit that contains it. AI remains deferred and is not a release gate.
