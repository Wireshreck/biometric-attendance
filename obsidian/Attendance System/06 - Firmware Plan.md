---
type: project-navigation
status: IN PROGRESS (Phase 0 PASSED)
updated: 2026-10-01
---

# 06 - Firmware Plan

[[00 - Project Overview|⬅️ Hub]] | [[05 - Software Stack|Stack ⬅️]] | [[07 - Backend Plan|Backend ➡️]]

**Status:**
- **ESP32 Baseline Toolchain & Serial (Phase 0):** **VERIFIED (PASSED)**. Firmware compiles, uploads to COM3, and communicates at 115200 baud.
- **R307S Fingerprint Integration (Phases 1–9):** **PREPARATION READY**. Sensor is physically acquired with 6-wire harness (Red, Black, Yellow, Green, Blue, White), but NOT yet connected or powered.
- **Hardware Abstraction Layer:** Defined in `firmware/include/fingerprint_sensor.h` (Phases 4–9 driver API stub).
- **Provisional UART Routing:** GPIO 16 (RX2) and GPIO 17 (TX2). Bounded timeouts ($\le 1000\text{ms}$).

Implement bounded sensor/UI operations first, then RTC validation, device-authenticated event submission, and a crash-safe LittleFS queue with stable event UUIDs. Keep enrollment/deactivation local via USB serial.

- [R307S Integration Plan](../../docs/r307s-integration-plan.md)
- [Firmware implementation sequence](../../firmware/README.md)
- [Electrical-safe wiring](../../docs/wiring.md)
- [Hardware gates](../../hardware/test-plan.md)
