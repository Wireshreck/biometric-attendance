# System Requirements Specification (SRS)

**Project:** Biometric School Attendance System  
**Version:** 1.0 (Pre-Development Baseline)  
**Date:** 24 September 2026  

---

## 1. Functional Requirements (FR)

* **FR-01: Biometric Enrollment:** The terminal shall allow an authorized administrator to enroll student fingerprints, capturing two consecutive impressions to verify consistency and storing the template in a free slot supported by the exact sensor. Sensor capacity must be measured/confirmed; do not assume 300 slots.
* **FR-02: Fingerprint Identification:** The system shall capture a scanned fingerprint and search the internal template database within 1.0 second.
* **FR-03: Real-Time Audio-Visual Feedback:** On a local successful match, show a generic “Attendance recorded” prompt, illuminate the green LED for 1000ms, and emit the short double-beep (100ms on, 50ms off, 100ms on). Offline, show “Saved offline” only after durable queue write. On an unrecognized finger, show “Not recognized / Try again”, illuminate the red LED for 1500ms, and emit the warning beep (600ms). Do not display another person’s name on a publicly visible terminal.
* **FR-04: Duplicate Scan Suppression:** The system shall suppress and flag another accepted scan for the same student if its capture time is within 60 seconds of an accepted scan. A later scan, including one later the same day, may be recorded. Daily presence counts distinct students with at least one accepted event. Replaying the same `event_uuid` shall return its original result without a second database insert.
* **FR-05: Real-Time Clock Timekeeping:** The terminal shall query the DS3231 RTC over I2C to obtain accurate, battery-backed timestamps independent of network NTP availability.
* **FR-06: Offline Buffering & Automatic Sync:** If local Wi-Fi connectivity is lost, attendance events shall be buffered in ESP32 LittleFS flash storage. When connectivity is re-established, the buffer shall automatically drain and replay records to the backend in chronological order.
* **FR-07: REST API Ingestion:** The FastAPI backend shall validate incoming attendance payloads, resolve student metadata from SQLite, and record the event atomically.
* **FR-08: Live Web Dashboard:** The system shall provide an in-browser interface displaying live incoming scans, daily summary statistics, attendance percentages, and a student management directory.
* **FR-09: Data Export:** The web interface shall allow downloading attendance data for any selected date range in standard CSV format.

---

## 2. Non-Functional Requirements (NFR)

* **NFR-01: Performance & Latency:** Target latency from finger placement through local match/feedback shall be $\le 1.2\text{ seconds}$; dashboard event visibility after backend commit shall be $\le 500\text{ ms}$ on the local network. These are targets to measure, not achieved results.
* **NFR-02: Reliability & Durability:** The ESP32 firmware shall handle unexpected Wi-Fi disconnects and sensor communication timeouts without crashing or triggering watchdog resets.
* **NFR-03: Local-First Autonomy:** The core attendance pipeline must function with zero internet connectivity and zero cloud server dependencies.
* **NFR-04: Data Privacy:** No raw biometric images shall be transmitted over the network or stored in the SQLite database.
* **NFR-05: Low Cost & Accessibility:** Total bill of materials for the hardware terminal shall remain under ₹3,000 INR using standard off-the-shelf components.
* **NFR-06: Portability:** The terminal shall be operable from standard 5V USB wall adapters, laptop USB ports, or portable 5V power banks.
* **NFR-07: Access Control:** Device ingestion and enrollment completion shall require an active device credential; student management, records, and exports shall require administrator authentication. Prototype authentication over HTTP is permitted only for synthetic data on an isolated demo network; it is not acceptable for live student data.
* **NFR-08: Data Minimization:** Fingerprint images/templates shall not be sent to the backend, logs, exports, or AI layer. Database and backup retention must be documented; live deployment requires an institution-approved policy.

See [requirements traceability](requirements-traceability.md) for priorities, status, components, verification methods, and planned test IDs.
