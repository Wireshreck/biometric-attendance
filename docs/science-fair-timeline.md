# Science Fair Timeline and Gates

**Target event:** 2026-10-09. **Status:** high risk. As of 2026-09-25 SQLite schema v1 and a tested partial FastAPI vertical slice exist; remaining API, firmware, dashboard, and integration are incomplete, and hardware order/delivery is not confirmed. Dates below are planning gates, not predictions or completed milestones. Replan after procurement status is known; do not silently compress safety/verification.

| Window / target | Work and dependency | Exit evidence / fallback |
| --- | --- | --- |
| Sep 24–25 | Confirm budget, seller/variant, place order if owner chooses; continue source/setup foundation | Receipt and delivery estimate, exact part revisions. If delayed, prepare software-only/mock demo. |
| Sep 25–28 | Extend API with report/query, CSV/SSE and device lifecycle routes; start dashboard work if API contract tests pass; confirm procurement in parallel | API-03 tests and a working software-only trace; if hardware is delayed, prepare a clearly labeled software/mock demonstration. |
| Sep 28–29 (conditional on delivery) | Inspect components; power, I2C, outputs, AS608 UART checks | Completed hardware gates with measured values; stop on voltage uncertainty or overheating. |
| Sep 29–Oct 1 (conditional) | Enroll/match synthetic adult tester; RTC and generic local feedback | Repeated physical success, no-match and error evidence. If sensor fails, present only verified components and limitation. |
| Oct 1–3 | Offline queue/replay and terminal event client; complete student workflow against API | Unit/API tests plus queue restart/replay evidence; no silent loss. |
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
