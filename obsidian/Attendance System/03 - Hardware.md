---
type: project-navigation
status: NEEDS HARDWARE VERIFICATION
updated: 2026-10-01
---

# 03 - Hardware

[[00 - Project Overview|⬅️ Hub]] | [[02 - Architecture|Architecture ⬅️]] | [[04 - Bill of Materials|BOM ➡️]]

**Status:** IN PROGRESS (Phase 0 PASSED, Phase 1 IN PROGRESS)
- **ESP32 DevKit V1:** Confirmed working on **COM3** at 115200 baud via PlatformIO validation upload.
- **R307S Fingerprint Sensor:** Physically acquired with a 6-wire harness (Observed order: 1: Red, 2: Black, 3: Yellow, 4: Green, 5: Blue, 6: White).
  - **Connection State:** NOT YET CONNECTED OR POWERED.
  - **Electrical & Pinout:** **UNVERIFIED — HARDWARE VERIFICATION REQUIRED**.
  - Do NOT assume wire colors prove the pinout.
  - Operating voltage (5V vs 3.3V) and UART TX level ($\le 3.3\text{V}$) must be verified from the physical module before wiring.

Provisional system: classic ESP32-WROOM-32 DevKit, **R307S optical fingerprint sensor (in hand; pinout/voltage unverified)**, SSD1306 128×64 I2C OLED, DS3231 RTC, LEDs/resistors, driver-equipped active buzzer, breadboard/jumpers and data USB cable. GPIO assignments are provisional.

> [!WARNING]
> **ELECTRICAL INTEGRATION BOUNDARY:**
> The ESP32 is strictly 3.3V logic and is **NOT 5V tolerant**. Exposing GPIO 16 to 5V will destroy the microcontroller. Refer to [R307S Integration Plan](../../docs/r307s-integration-plan.md) for the 10-phase bring-up protocol.

- [R307S Integration Plan](../../docs/r307s-integration-plan.md)
- [Hardware selection and limits](../../docs/hardware.md)
- [Electrical-safe provisional wiring](../../docs/wiring.md)
- [Bench bring-up gates](../../hardware/test-plan.md)
