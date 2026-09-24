# 08 - Database Plan

[[00 - Project Overview|⬅️ Back to Hub]] | [[09 - API Plan|Next: API ➡️]]

**Status:** Planned; schema not implemented. Canonical specification: [Database plan](../../docs/database-plan.md).

The planned store is local SQLite in WAL mode with `students`, `devices`, `attendance`, and `configuration` tables. The laptop database stores a sensor slot reference, not fingerprint templates. Backups, retention, migration behavior, and access controls need to be implemented and verified before any real student data is used.

**Decision to resolve before implementation:** FR-04 specifies suppression within 60 seconds, but the proposed schema has `UNIQUE(student_id, date_local)`, which permits only one record per student per day. Choose the intended attendance policy and align requirements, API behavior, and constraints.

Related: [Privacy and security](../../docs/privacy-security.md), [backup strategy](../../docs/backup-strategy.md).
