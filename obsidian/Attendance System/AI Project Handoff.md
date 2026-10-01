---
type: project-handoff
status: IN PROGRESS (ESP32 Serial Test PASSED, R307S Integration Prepared)
updated: 2026-10-01
---

# AI Project Handoff

## Project and Vault Overview

Biometric School Attendance System: a local-first biometric school attendance terminal and data platform for a science-fair demonstration. The **repository root is the Obsidian vault**; open `C:\Users\user\projects\fair\biometric-attendance` in Obsidian. Start at [[00 - Project Overview]], use [[Architecture.canvas]] for an interactive color-coded map, and review [[AI Development Guide]] before making changes.

---

## 🚨 CRITICAL CURRENT-STATE SUMMARY (2026-10-01)

An incoming AI agent must strictly understand the following verified facts and boundaries:

1. **ESP32 Serial Test: PASSED**
   - The ESP32-WROOM-32 DevKit V1 has been connected and physically tested on the workbench.
   - **COM3 communication PASSED:** USB-UART communication is confirmed functional on port `COM3` at `115200` baud.
   - **PlatformIO build PASSED:** Firmware builds cleanly under `espressif32@6.5.0` with the Arduino framework.
   - **ESP32 firmware upload PASSED:** The baseline toolchain validation sketch was flashed to the board, booting successfully and emitting valid system telemetry (chip revision, CPU clock, free heap).

2. **R307S Hardware Status:**
   - **Target Sensor:** The canonical fingerprint hardware target is the **R307S optical fingerprint sensor** (superseding earlier AS608 and provisional R703 designations; see [[Decision Log]] ADR-013).
   - **R307S hardware NOT YET CONNECTED:** The sensor is physically in hand but has not been connected to the ESP32.
   - **R307S power NOT YET APPLIED:** No electrical voltage has been applied to the module.
   - **R307S pinout NOT YET VERIFIED:** Pin assignments, supply requirements (5V vs 3.3V), and UART signal levels are **UNVERIFIED — HARDWARE VERIFICATION REQUIRED**.
   - **Observed Harness Order:** The physical cable harness has 6 wires in the order:
     `1: Red, 2: Black, 3: Yellow, 4: Green, 5: Blue, 6: White`.
   - **CRITICAL WARNING:** **DO NOT ASSUME WIRE COLORS PROVE THE PINOUT.** Many low-cost Chinese cable assemblies use arbitrary color sequences. Verify ground continuity and PCB silkscreen before connecting.
   - **Next immediate action:** Verification of R307S electrical and pinout information (Phase 1 in `docs/r307s-integration-plan.md`).

> [!WARNING]
> **MANDATORY INSTRUCTION FOR FUTURE AI AGENTS:**  
> Do not assume AS608 compatibility with the R307S. Verify the R307S variant, electrical interface, pinout, and protocol before physical wiring or firmware assumptions. Never connect a 5V UART signal to an ESP32 GPIO pin (ESP32 is strictly 3.3V logic and NOT 5V tolerant).

---

## Verified Subsystem Summary

- **Firmware Environment:** PlatformIO Core 6.2.0 + `espressif32@6.5.0` + Arduino framework. PlatformIO monitor configuration is documented in `firmware/platformio.ini` (`monitor_speed = 115200`, `upload_speed = 921600`, exception decoder filter). Hardware abstraction layer interface is defined in `firmware/include/fingerprint_sensor.h`.
- **Backend Environment:** Python 3.13 + FastAPI 0.115.0 + SQLite3 (WAL mode) in `backend/.venv`.
- **Database & API Verification:** 10 pytest tests pass (6 database migration/constraint tests and 4 API vertical-slice tests). Coverage includes 60-second duplicate suppression, 61-second acceptance, UUID replay, validation/auth/slot errors, and hash-only device provisioning.
- **Frontend Subsystem:** Zero-build modern vanilla HTML5/CSS3/JavaScript architecture decided; implementation pending.
- **Documentation & Canvas:**
  - Full 10-phase bring-up sequence: [`docs/r307s-integration-plan.md`](../../docs/r307s-integration-plan.md)
  - Color-coded Canvas: [[Architecture.canvas]] (Green = Verified, Yellow = Needs Verification, Blue = Planned, Red = Warning/Risk, Purple = Reference).
  - Pinout & Wiring: [`hardware/pinout.md`](../../hardware/pinout.md) and [`docs/wiring.md`](../../docs/wiring.md).

---

## 10-Phase Hardware Integration Sequence

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

## Next Concrete Actions

1. **Human Action:** Physically inspect the R307S connector. Check if silkscreen pin labels exist. Use a multimeter in continuity mode to identify which pin connects to the ground plane/shield. Check whether power input is marked 5V or 3.3V.
2. **Software Action:** Once Phase 1 is confirmed by the human, write the Phase 4/5 diagnostic test sketch in `firmware/src/` to send a minimal handshake packet over UART2 at 57600 baud.
