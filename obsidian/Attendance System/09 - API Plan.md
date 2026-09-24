# 09 - API Plan

[[00 - Project Overview|⬅️ Back to Hub]] | [[08 - Database Plan|⬅️ Database]] | [[10 - AI Plan|Next: AI ➡️]]

**Status:** Planned; endpoints are not implemented. Canonical contract: [API plan](../../docs/api-plan.md).

The proposed FastAPI interface covers student administration, attendance queries, statistics, and device event ingestion. Device ingestion is intended to authenticate with a device token and validate slot IDs and timestamps. Implement authentication, authorization for administrative routes, input limits, idempotency/replay handling, and secure transport as part of the API rather than treating the draft contract as production-ready.

Related: [Backend plan](07 - Backend Plan.md), [database plan](08 - Database Plan.md).
