# Requirements Traceability

**Status:** Baseline mapping of the pre-development SRS. Requirements are planned; none of the product behaviors below are implemented or verified. Source: [requirements.md](requirements.md).

Priority: **P0** required for the MVP; **P1** quality target; **P2** deferred/optional. A named test is a planned verification, not evidence of a passing test.

| ID | Requirement | Priority | Source | Status | Component | Verification / planned test |
| --- | --- | --- | --- | --- | --- | --- |
| FR-01 | Authorized local admin can enroll two impressions and save template in a unique sensor slot. | P0 | SRS FR-01 | PLANNED | Firmware, API, sensor | TC-ENR-01; physical two-pass enrollment and slot readback |
| FR-02 | Identify matching fingerprint within 1.0 s after capture begins. | P0 | SRS FR-02 | PLANNED | Sensor, firmware | TC-FP-01; timed bench trials; report measured distribution, not assumed accuracy |
| FR-03 | Generic success/offline/failure prompt and LED/buzzer feedback follow specified behavior; no student name on public display. | P1 | SRS FR-03 | PLANNED | Firmware, OLED, GPIO | TC-HW-04; observe each state/duration and verify no identity leak |
| FR-04 | Suppress and flag same-student scans within 60 s; later scans may be recorded. | P0 | SRS FR-04; clarified by [database design](database-plan.md) | PLANNED | Backend, SQLite, device | TC-API-03; boundary at 59/60/61 s, concurrent requests, replay idempotency |
| FR-05 | Use battery-backed RTC time independent of internet. | P0 | SRS FR-05 | PLANNED | RTC, firmware | TC-HW-05; set time, power-cycle, compare offset-qualified timestamp |
| FR-06 | Queue events offline and replay chronologically without loss or duplicate insertion. | P0 | SRS FR-06 | PLANNED | Firmware LittleFS, API, DB | TC-INT-02; disconnect, restart, recover, verify event UUIDs/outcomes |
| FR-07 | Validate and atomically ingest authenticated device events. | P0 | SRS FR-07 | PLANNED | FastAPI, SQLite | TC-API-01/02; schema rejection, auth failure, transaction rollback |
| FR-08 | Display attendance feed, daily metrics, and student directory. | P0 | SRS FR-08 | PLANNED | API, frontend | TC-UI-01; empty/loading/error and update behavior |
| FR-09 | Export attendance for selected date range as CSV. | P1 | SRS FR-09 | PLANNED | API, frontend | TC-API-05; date bounds, escaping, authorization, synthetic fixture comparison |
| NFR-01 | Finger-to-feedback <=1.2 s; dashboard update <=500 ms on demo LAN. | P1 | SRS NFR-01 | PLANNED | Firmware, API, frontend | TC-PERF-01; define start/end markers and report p50/p95 over repeated runs |
| NFR-02 | Sensor/network failure must not crash or watchdog-reset the terminal. | P0 | SRS NFR-02 | PLANNED | Firmware | TC-FAULT-01; timeout, disconnect, restart and recovery trials |
| NFR-03 | Core system works without internet/cloud services. | P0 | SRS NFR-03 | PLANNED | Whole system | TC-INT-02; isolate WAN and exercise local scan/report flow |
| NFR-04 | Raw fingerprint images are not stored in backend/database or sent over network. | P0 | SRS NFR-04 | PLANNED | Sensor, firmware, API, DB | TC-PRIV-01; inspect payloads, logs, DB, exports and network capture |
| NFR-05 | Core physical BOM stays below ₹3,000 using available components. | P1 | SRS NFR-05 | PLANNED | Hardware/procurement | TC-COST-01; record actual receipts and total including delivery/tax |
| NFR-06 | Terminal can use a suitable 5V USB supply. | P1 | SRS NFR-06 | PLANNED | Power/hardware | TC-HW-01; measure rail under peak Wi-Fi/sensor operation |
| NFR-07 | Device/admin routes require appropriate authentication. | P0 | SRS NFR-07 | PLANNED | API, configuration | TC-SEC-01; missing, invalid, revoked credentials rejected |
| NFR-08 | Minimize biometric data and define retention/deletion behavior. | P0 | SRS NFR-08 | PLANNED | Firmware, API, DB, backup | TC-PRIV-01/02; inspect payload, DB, logs, exports, backup, deletion |

## Coverage gaps and notes

- No test suite or tests directory currently exists. Every TC above is a plan and must be implemented with its component.
- FR-01 says “authorized” but the MVP authorization procedure is local physical access to the USB serial console; this is a prototype control, not production admin authentication.
- FR-02 and NFR-01 are measurable targets, not measured results. Accuracy/FAR/FRR has no acceptance threshold in the SRS; collect honest results and do not claim a performance guarantee.
- FR-04 now has one consistent interpretation in the database plan: scans are suppressed only within the 60-second interval; a later same-day scan is recordable. Daily presence counts distinct students with an accepted event.
- NFR-01's <=500 ms dashboard target requires a Server-Sent Events stream; interval polling alone does not meet it.
- The SRS does not define enrollment cancellation, database deletion authorization, retention duration, device provisioning, clock-skew bounds, or report timezone. See [privacy/security](privacy-security.md) and [database design](database-plan.md); live-school deployment remains out of scope.
