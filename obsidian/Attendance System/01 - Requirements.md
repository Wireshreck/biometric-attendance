---
type: project-navigation
status: PLANNED
updated: 2026-09-25
---

# 01 - Requirements

[[00 - Project Overview|⬅️ Hub]] | [[02 - Architecture|Architecture ➡️]]

**Status:** PLANNED — baseline requirements are documented; attendance behavior remains unimplemented.

The MVP target is a local attendance demonstrator: two-impression enrollment, local fingerprint match, safe feedback, RTC timestamp, 60-second duplicate suppression, offline delivery, authenticated API, local dashboard, and CSV export. Sensor capacity must be confirmed for the exact unit. Targets are not measured results.

- [Full requirements](../../docs/requirements.md)
- [Requirement-to-test traceability](../../docs/requirements-traceability.md)
- [Test strategy](../../docs/testing-plan.md)

Important clarified rule: different scans for the same student within 60 seconds are flagged/suppressed; later same-day scans may be stored. Daily presence counts each student once. Replaying the same event UUID never inserts twice.
