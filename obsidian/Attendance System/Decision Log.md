---
type: decision-log
status: IN PROGRESS
updated: 2026-09-29
---

# Architecture Decision Log

Records below preserve rationale and decision state. They do not prove every behavior is implemented or production-verified; code and test evidence remain authoritative. Update entries when evidence or requirements change without erasing superseded history.

| ID | Decision / status | Reason and tradeoff | Evidence / revisit trigger |
| --- | --- | --- | --- |
| ADR-001 | Use ESP32-WROOM-32-class terminal — **PROVISIONAL** | Low-cost Wi-Fi MCU with UART/I2C and an established PlatformIO target; clone/module pins and power vary. | `docs/hardware.md`, `docs/wiring.md`; revisit after exact board is identified. |
| ADR-002 | Select AS608 fingerprint module — **SUPERSEDED by ADR-012 (2026-09-29)** | Historical: candidate optical UART module for edge matching and local template slots; exact capacity, logic levels, liveness, and template properties were unverified. The physically acquired module is an R703 instead. | `docs/bill-of-materials.md`; superseded — see ADR-012. |
| ADR-003 | Local-first, one-host prototype — **PLANNED** | Avoid cloud dependence and keep demo operation understandable; limits prototype access to a local network and requires explicit firewall handling. | `docs/architecture.md`; revisit only if requirements change. |
| ADR-004 | Keep matching/template operations on sensor; host receives slot result only — **PROVISIONAL** | Minimize host/network biometric data; the project cannot claim the exact sensor firmware enforces this until commands and behavior are verified. | `docs/privacy-security.md`; revisit after module protocol inspection and packet/log review. |
| ADR-005 | FastAPI + SQLite for a single local service — **DECIDED; IMPLEMENTED (API/DB subset)** | Existing Python environment and modest single-host write load suit a simple relational store; SQLite is not treated as a multi-writer server. | API/DB slice exists in `backend/app/`; dashboard, reports and full service remain incomplete. Revisit if measured workload exceeds the single-host model. |
| ADR-006 | SQLite WAL, ordered migrations, foreign keys, `synchronous=FULL` — **DECIDED; VERIFIED (database setup)** | WAL supports concurrent readers around one writer; transactional migrations and explicit constraints support recovery and integrity. | `docs/database-plan.md`; migration tests pass. Revisit only with measured durability/performance evidence. |
| ADR-007 | Vanilla HTML/CSS/ES modules served same-origin — **PLANNED** | Avoid a separate frontend build/runtime for a small dashboard; tradeoff is manual discipline and fewer component abstractions. | `frontend/README.md`; revisit if UI scope justifies build tooling. |
| ADR-008 | Suppress same-student scans within 60 seconds; later same-day scans can record — **DECIDED; VERIFIED (API tests)** | Follows FR-04; distinct students with accepted events count once in daily presence; UUID replay returns prior outcome. | `docs/requirements.md`, `docs/database-plan.md`, `backend/tests/test_api.py`; software boundary/replay test only, no terminal evidence. Change only through an explicit requirement decision. |
| ADR-009 | Stable UUID and bounded LittleFS replay queue — **PLANNED** | Durable idempotency key is needed for offline retry without duplicate inserts; queue overflow must fail visibly, never discard silently. | `docs/architecture.md`, `firmware/README.md`; validate through power-cut/retry tests. |
| ADR-010 | Device bearer token + admin HTTP Basic for synthetic isolated demo only — **DECIDED; IMPLEMENTED (API subset)** | Simple MVP separation of device ingestion from admin operations; HTTP exposes credentials on the LAN and is not suitable for real personal data. | Limited API checks exist in `backend/app/auth.py`; no independent audit, TLS, stronger identity or production suitability. |
| ADR-011 | Defer optional AI; if added, read-only aggregate reports only — **DEFERRED** | Core attendance must not depend on AI; limits exposure and prevents generated output from changing attendance records. | `docs/ai-plan.md`; reconsider after tested core MVP and privacy review. |
| ADR-012 | Fingerprint hardware migration to provisional R703 — **SUPERSEDED by ADR-013 (2026-10-01)** | Provisional migration based on label; superseded by definitive identification of the acquired unit as R307S. | See ADR-013. |
| ADR-013 | Canonical Fingerprint Sensor defined as **R307S** with 10-Phase Bring-Up Plan — **DECIDED; HARDWARE INTEGRATION PREPARATION** | The owner confirmed the acquired physical module is the **R307S** with a 6-wire harness (observed order: Red, Black, Yellow, Green, Blue, White). ESP32 baseline serial test PASSED on COM3 (115200 baud). Sensor has NOT yet been connected or powered. Pinout, supply voltage (5V vs 3.3V), and UART logic level remain UNVERIFIED until physical PCB inspection / meter checks. Structured 10-phase bring-up sequence established to prevent hardware damage. | Supersedes ADR-012 and ADR-002. See `docs/r307s-integration-plan.md`, `hardware/pinout.md`, `hardware/test-plan.md`, `firmware/include/config.h`, and `firmware/include/fingerprint_sensor.h`. |

## Change procedure

For a material change, add a new ADR row with context, decision, consequences, evidence, and superseded ID. Update the relevant canonical plan, requirements traceability, affected task, and Canvas edge in the same milestone.
