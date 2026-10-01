# AI_CONTEXT.md — Biometric Attendance System

**Last Updated:** 2026-10-01  
**Project:** Biometric School Attendance System (`biometric-attendance`)  
**Target Exhibition:** Science Fair (9 October 2026)  

---

## 🚨 CRITICAL HARDWARE & INTEGRATION STATE

This document must be read by any AI agent before proposing, modifying, or executing code or hardware actions.

### 1. Verified Facts (Do NOT Re-test or Question)
- **MCU Platform:** ESP32-WROOM-32 DevKit V1.
- **ESP32 Serial Test: PASSED.** USB serial communication is confirmed functional on **COM3** at **115200 baud**.
- **PlatformIO Build: PASSED.** PlatformIO Core 6.2.0 + `espressif32@6.5.0` compiles cleanly (`pio run -d firmware`).
- **ESP32 Firmware Upload: PASSED.** Validation sketch was successfully flashed over COM3 and telemetry confirmed.
- **Backend Environment: PASSED.** Python 3.13 + FastAPI 0.115.0 + SQLite3 (WAL mode) verified via 10 passed pytest tests.
- **Acquired Fingerprint Module:** **R307S optical fingerprint sensor** (superseding earlier AS608 / provisional R703 notes; see `obsidian/Attendance System/Decision Log.md` ADR-013).
- **Physical Cable Harness Observed:** 6-wire ribbon with order:
  `1: Red, 2: Black, 3: Yellow, 4: Green, 5: Blue, 6: White`.

### 2. Unverified Facts & Active Blockers (Do NOT Assume or Invent)
- **R307S hardware NOT YET CONNECTED.**
- **R307S power NOT YET APPLIED.**
- **R307S pinout NOT YET VERIFIED.** Wire colors alone must **NEVER** be assumed to indicate pinout or polarity.
- **Operating Voltage & UART Levels UNVERIFIED.** Must determine whether sensor requires 5V or 3.3V, and confirm sensor TX output voltage does not exceed 3.3V (ESP32 GPIO is **NOT 5V tolerant**).
- **Next immediate action:** Physical verification of R307S pinout and electrical ratings (Phase 1).

### 3. Explicit Warning for AI Agents
> "Do not assume AS608 compatibility with the R307S. Verify the R307S variant, electrical interface, pinout, and protocol before physical wiring or firmware assumptions."

---

## 10-Phase Hardware Integration Sequence

Refer to [`docs/r307s-integration-plan.md`](docs/r307s-integration-plan.md) for full phase gates:
- **Phase 0:** ESP32 baseline toolchain & USB serial test — **PASSED on COM3 (115200 baud)**.
- **Phase 1:** R307S physical inspection, silkscreen, ground continuity, voltage check — **NEXT IMMEDIATE ACTION**.
- **Phase 2:** Minimum wiring connection (GND, VCC, TX, RX only; touch disconnected).
- **Phase 3:** Power-on sanity check (monitor rails, check sensor thermals, check TX voltage $\le 3.3\text{V}$).
- **Phase 4:** Establish UART communication on GPIO 16/17 (57600 baud default).
- **Phase 5:** Minimal command & response (send verifyPassword packet, receive ACK `0x00`).
- **Phase 6:** Read sensor system parameters (confirm capacity = 1000, security level, baud).
- **Phase 7:** Test 2-pass biometric enrollment to template slot 1.
- **Phase 8:** Test 1:N fingerprint search and matching.
- **Phase 9:** Attendance application integration (OLED, RTC, LittleFS, FastAPI).

---

## Key File Locations

- **Integration Plan:** [`docs/r307s-integration-plan.md`](docs/r307s-integration-plan.md)
- **Wiring & Safety:** [`docs/wiring.md`](docs/wiring.md)
- **Pinout Guide:** [`hardware/pinout.md`](hardware/pinout.md)
- **Hardware Bring-Up Gates:** [`hardware/test-plan.md`](hardware/test-plan.md)
- **Firmware Config:** [`firmware/include/config.h`](firmware/include/config.h)
- **Hardware Abstraction Layer:** [`firmware/include/fingerprint_sensor.h`](firmware/include/fingerprint_sensor.h)
- **Interactive Canvas:** [`obsidian/Attendance System/Architecture.canvas`](obsidian/Attendance%20System/Architecture.canvas)
- **Master Task Tracker:** [`obsidian/Attendance System/TODO.md`](obsidian/Attendance%20System/TODO.md)
- **Architecture Decisions:** [`obsidian/Attendance System/Decision Log.md`](obsidian/Attendance%20System/Decision%20Log.md)
