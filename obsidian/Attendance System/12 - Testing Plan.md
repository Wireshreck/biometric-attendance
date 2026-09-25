---
type: project-navigation
status: PLANNED
updated: 2026-09-25
---

# 12 - Testing Plan

[[00 - Project Overview|⬅️ Back to Hub]] | [[11 - Privacy & Security|⬅️ Privacy]] | [[13 - GitHub & Development|Next: Development ➡️]]

**Status:** IMPLEMENTED — database migration/constraint tests; API, firmware, dashboard, and integration tests are PLANNED. Canonical plan: [Testing plan](../../docs/testing-plan.md). Hardware checks: [bench test plan](../../hardware/test-plan.md).

Verification is expected across firmware, backend, dashboard, and integrated operation. Priority cases include sensor/RTC failures, invalid and duplicate events, network loss and replay, database recovery, authorization, and protection of sensitive data. Record test evidence and distinguish simulated checks from physical bench results.
