---
type: science-fair
area: science-fair
status: planned
tags:
  - science-fair
  - timeline
---
# Science Fair Timeline and Gates

**Target event:** 2026-10-09. **Status:** high risk (updated 2026-10-02). Firmware test environments and attendance/enrollment/queue/API source are implemented; backend vertical slice is tested. The R307S has no valid owner-reported UART response and component/device integration has no physical pass evidence. Dashboard and remaining reports/API routes are incomplete. Dates below are planning gates, not predictions or completed milestones; do not compress safety/verification.

| Window / target | Work and dependency | Exit evidence / fallback |
| --- | --- | --- |
| Sep 24–25 | Confirm budget, seller/variant, place order if owner chooses; continue source/setup foundation | Receipt and delivery estimate, exact part revisions. If delayed, prepare software-only/mock demo. |
| Sep 25–28 | Extend API with report/query, CSV/SSE and device lifecycle routes; start dashboard work if API contract tests pass; confirm procurement in parallel | API-03 tests and a working software-only trace; if hardware is delayed, prepare a clearly labeled software/mock demonstration. |
| Sep 28–Oct 2 | Build isolated component/integration firmware; record owner-reported R307S UART silence | Firmware matrix builds; physical component tests and electrical measurements remain NOT EXECUTED / UNVERIFIED. |
| Sep 29–Oct 1 (conditional) | Enroll/match synthetic adult tester; RTC and generic local feedback | Repeated physical success, no-match and error evidence. If sensor fails, present only verified components and limitation. |
| Oct 1–3 | Verify offline queue/replay and terminal event client against synthetic API | Unit/API tests plus physical queue restart/replay evidence; no silent loss. Software implementation now exists; physical evidence is outstanding. |
| Oct 3–4 | Dashboard views, SSE and end-to-end join | At least one complete synthetic enrollment→scan→DB→UI trace. If not, show only verified layers. |
| Oct 5–6 | Failure, privacy, restore and timing tests; feature freeze | Report test evidence and deviations; do not promise 50 scans if time/evidence insufficient. |
| Oct 7–8 | Presentation assets, repeatable fallback, restored backup, rehearsal | Demo script matches actual capability; backup restore recorded; final source snapshot. |
| Oct 9 | Science fair | Use synthetic/consented demo only; explain limitations and actual measurements. |

## Critical path and decision gates

- **Gate A — procurement (Sep 25 target):** Procurement status is currently unknown. If hardware is not in hand by Sep 28, switch to mock/software demonstration and stop promising physical recognition results.
- **Gate B — safe hardware (before sensor connection):** Exact module supply and UART logic levels, I2C pull-ups and RTC battery circuit are confirmed; otherwise no powered connection.
- **Gate C — vertical slice (Oct 4 target):** If enrollment→scan→API→database→dashboard cannot be repeated, demonstrate component evidence only; do not present a “working end-to-end system.”
- **Gate D — freeze (Oct 6 target):** Prioritize bugs, backup/restore, and explanation over optional features. AI is deferred.

The original day-by-day schedule assumed confirmed fast shipping, parallel software development, and product scaffolding that did not exist. It is superseded by this dependency-based risk plan. The Oct 9 event date is retained; milestone dates should be updated from actual evidence.
