---
type: decision-log
status: IN PROGRESS
updated: 2026-09-25
---

# Architecture Decision Log

Records below describe accepted **plans**, not implemented or experimentally validated behavior. Update an entry when evidence or requirements change; do not erase the history of superseded decisions.

| ID | Decision / status | Reason and tradeoff | Evidence / revisit trigger |
| --- | --- | --- | --- |
| ADR-001 | Use ESP32-WROOM-32-class terminal — **PROVISIONAL** | Low-cost Wi-Fi MCU with UART/I2C and an established PlatformIO target; clone/module pins and power vary. | `docs/hardware.md`, `docs/wiring.md`; revisit after exact board is identified. |
| ADR-002 | Select AS608 fingerprint module — **PROVISIONAL** | Candidate optical UART module for edge matching and local template slots; exact capacity, logic levels, liveness, and template properties are unverified. | `docs/bill-of-materials.md`; revisit against exact datasheet/unit or if safe interface cannot be established. |
| ADR-003 | Local-first, one-host prototype — **PLANNED** | Avoid cloud dependence and keep demo operation understandable; limits prototype access to a local network and requires explicit firewall handling. | `docs/architecture.md`; revisit only if requirements change. |
| ADR-004 | Keep matching/template operations on sensor; host receives slot result only — **PROVISIONAL** | Minimize host/network biometric data; the project cannot claim the exact sensor firmware enforces this until commands and behavior are verified. | `docs/privacy-security.md`; revisit after module protocol inspection and packet/log review. |
| ADR-005 | FastAPI + SQLite for a single local service — **PLANNED** | Existing Python environment and modest single-host write load suit a simple relational store; SQLite is not treated as a multi-writer server. | `docs/software-stack.md`, `docs/database-plan.md`; revisit if measured workload exceeds the single-host model. |
| ADR-006 | SQLite WAL, ordered migrations, foreign keys, `synchronous=FULL` — **PLANNED** | WAL supports concurrent readers around one writer; transactional migrations and explicit constraints support recovery and integrity. | `docs/database-plan.md`; revisit only with measured durability/performance evidence. |
| ADR-007 | Vanilla HTML/CSS/ES modules served same-origin — **PLANNED** | Avoid a separate frontend build/runtime for a small dashboard; tradeoff is manual discipline and fewer component abstractions. | `frontend/README.md`; revisit if UI scope justifies build tooling. |
| ADR-008 | Suppress same-student scans within 60 seconds; later same-day scans can record — **DECIDED** | Follows FR-04; distinct students with accepted events count once in daily presence; UUID replay returns prior outcome. | `docs/requirements.md`, `docs/database-plan.md`; change only through an explicit requirement decision. |
| ADR-009 | Stable UUID and bounded LittleFS replay queue — **PLANNED** | Durable idempotency key is needed for offline retry without duplicate inserts; queue overflow must fail visibly, never discard silently. | `docs/architecture.md`, `firmware/README.md`; validate through power-cut/retry tests. |
| ADR-010 | Device bearer token + admin HTTP Basic for synthetic isolated demo only — **PLANNED** | Simple MVP separation of device ingestion from admin operations; HTTP exposes credentials on the LAN and is not suitable for real personal data. | `docs/api-plan.md`; production use requires TLS and stronger identity/security design. |
| ADR-011 | Defer optional AI; if added, read-only aggregate reports only — **DEFERRED** | Core attendance must not depend on AI; limits exposure and prevents generated output from changing attendance records. | `docs/ai-plan.md`; reconsider after tested core MVP and privacy review. |

## Change procedure

For a material change, add a new ADR row with context, decision, consequences, evidence, and superseded ID. Update the relevant canonical plan, requirements traceability, affected task, and Canvas edge in the same milestone.
