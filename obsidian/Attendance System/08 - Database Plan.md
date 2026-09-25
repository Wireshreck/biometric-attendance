---
type: project-navigation
status: VERIFIED
updated: 2026-09-25
---

# 08 - Database Plan

[[00 - Project Overview|⬅️ Back to Hub]] | [[09 - API Plan|Next: API ➡️]]

**Status:** VERIFIED — schema v1 migration/connection setup plus transactional attendance ingest are API-tested (10 total DB/API/provisioning tests pass). Reports, exports, physical slot cleanup/deletion, and full integration remain PLANNED. Canonical specification: [Database plan](../../docs/database-plan.md).

SQLite schema v1 uses `students`, `devices`, `attendance_events`, and `admin_audit_log`; operational settings stay in environment variables. It stores sensor slot references, not templates. The 60-second policy is resolved in FR-04: suppress scans within the interval, permit later same-day records, and count distinct present students daily. Migration tests cover schema integrity, not attendance behavior.

Related: [Privacy and security](../../docs/privacy-security.md), [backup strategy](../../docs/backup-strategy.md).
