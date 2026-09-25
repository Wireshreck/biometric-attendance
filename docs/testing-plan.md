# Test and Acceptance Plan

**Status:** VERIFIED — database migration/constraint tests and the implemented API vertical slice (temporary DBs, synthetic identities). PLANNED — remaining API, UI, firmware, integration, and hardware testing. No recognition accuracy, performance measurements, or reliability results are present. Traceability is in [requirements-traceability.md](requirements-traceability.md); bench sequence is [hardware/test-plan.md](../hardware/test-plan.md). Latest local run: `python -m pytest tests -q` from `backend/`: 10 passed on 2026-09-25.

| Test ID | Level | Setup/action | Acceptance evidence |
| --- | --- | --- | --- |
| TC-HW-01 | Hardware/power | Measure USB, 3V3 rail idle and during Wi-Fi/sensor/buzzer peak | Within exact board/module specifications; record board, meter, values; no reset/heating |
| TC-HW-02 | Hardware/I2C | Scan GPIO21/22 at 100kHz with each module isolated and together | Expected device addresses; bus high <=3.3V; board pull-ups documented |
| TC-HW-03 | Hardware/UART | AS608 handshake after verifying voltage/baud | Repeated response at configured baud; no framing/timeouts |
| TC-HW-04 | Firmware feedback | Exercise recognized, no-match, saved-offline, error state | Correct generic message, LED/buzzer behavior and measured durations; no identity leak |
| TC-HW-05 | RTC | Set known timezone-qualified test time, remove primary power, wait 10m | RTC retains/advances; record drift; invalid/lost time blocks event timestamp |
| TC-ENR-01 | Firmware/API | Enroll two impressions into reserved slot; retry/fail/delete safely | State changes PENDING -> ACTIVE only after device confirms; no template/image crosses API; slot cleanup verified before reuse |
| TC-FP-01 | Biometric | Repeated genuine and consented non-matching scans | Record attempts, rejects, elapsed times; do not infer production FAR/FRR from small sample |
| TC-DB-01 | Database | Migrate empty and prior supported schema; enable foreign keys/WAL | `foreign_key_check` empty, indexes/constraints correct, migration transactional/idempotent |
| TC-API-01 | API/security | Missing, invalid, revoked device/admin credentials and malformed payloads | Reject with documented 401/403/422; no detail leakage or DB write |
| TC-API-02 | API/idempotency | Submit event UUID twice; use two concurrent distinct UUIDs for same slot/time | Same UUID returns stored outcome; only one event in 60s accepted; all request outcomes persisted as specified |
| TC-API-03 | API duplicate boundary | Submit same student at 59s, 60s, 61s, later same day; out-of-order offline replay | Boundary behavior matches chosen inclusive window; later event can record; deterministic replay/order |
| TC-API-04 | Reporting | Use synthetic accepted/suppressed events across timezone date boundary | Reports exclude suppressed events and count distinct students once per local date |
| TC-API-05 | Export | CSV with commas, quotes, formula-leading cells and date boundary | Correct RFC4180 escaping; formula injection neutralized; range/auth limits applied |
| TC-PRIV-01 | Privacy | Inspect serial/network payloads, DB, logs, backup and export | No image/template bytes or credentials; sensitive fields only where intended |
| TC-PRIV-02 | Lifecycle | Deactivate/erase synthetic student; clear sensor slot; restore backup | No new scans for inactive identity; verified slot cleanup; restore and integrity check successful |
| TC-UI-01 | Frontend | Empty/loading/error states, student flow, SSE disconnect/reconnect, mobile viewport | Accessible state feedback; no stale “success”; reconnect does not duplicate table entries |
| TC-INT-01 | End-to-end | Enroll synthetic tester, scan, API commit, dashboard update | End-to-end trace has one event UUID and matching database/UI result; measure latency |
| TC-INT-02 | Failure/recovery | Drop WLAN/API, scan, restart terminal, restore service | Durable FIFO replay, stable UUID, no silent loss, queue removed only after stored acknowledgement |
| TC-FAULT-01 | Firmware resilience | Sensor disconnect/timeout, RTC invalid, queue full, flash error, Wi-Fi loss | Visible safe error; no watchdog reset; never claim queued/recorded when persistence failed |
| TC-BACKUP-01 | Recovery | Online DB backup; restore to isolated temp location; integrity check | Counts/relations match fixture; documented restore time and backup checksum |
| TC-PERF-01 | Performance | Repeat at least 30 scans on stated setup | Report p50/p95 and sample conditions; target local feedback <=1.2s, SSE visibility <=500ms after commit; no fabricated pass |
| TC-STRESS-01 | Stress | 50 synthetic scans, mixed online/offline, inspect heap/queue/DB | No crash/data loss; all event UUIDs reconciled; record any duplicate/suppression behavior |

### Current API evidence and remaining coverage

`backend/tests/test_api.py` currently verifies health/migration readiness, admin authentication and student create/read/list/deactivate/slot-conflict behavior, local provisioning stores only the token hash, device enrollment assignment/completion, event authentication/active-slot checks, timestamp validation, UUID replay, and inclusive 60s suppression versus 61s acceptance. It does not verify concurrent ingest contention, revocation, reports/timezone boundaries, CSV, SSE, deletion/cleanup, firmware, or hardware. Do not mark the full TC-API-01..05 procedures complete based on this partial suite.

## Test-data and reporting rules

- Use synthetic names/roll numbers, dummy device tokens, and consenting adult testers only. Keep no raw fingerprint images/templates in test artifacts.
- Physical tests cannot be claimed complete from firmware compilation. Distinguish compile, simulated integration, bench test, and verified result.
- Record build commit, dependency/platform versions, board and sensor revision, environment, date, sample size, failures, and raw aggregate counts. Do not claim “100% accurate” or production reliability.
- Acceptance thresholds beyond the stated timing and wiring requirements need owner/institution review; especially biometric false-accept/false-reject risk.
