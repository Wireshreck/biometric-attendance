---
type: project-navigation
status: PLANNED
updated: 2026-09-25
---

# 06 - Firmware Plan

[[00 - Project Overview|⬅️ Hub]] | [[05 - Software Stack|Stack ⬅️]] | [[07 - Backend Plan|Backend ➡️]]

**Status:** VERIFIED — toolchain-check sketch compiles for `esp32dev`; no board flash/physical test. Enrollment, identification, RTC, OLED, network, authentication, LittleFS queue, recovery, and watchdog behavior are PLANNED.

Current GPIO16/17 UART values are provisional GPIO-matrix routing, not a UART2 pin requirement. Board and sensor validation still needs exact hardware.

Implement bounded sensor/UI operations first, then RTC validation, device-authenticated event submission, and a crash-safe LittleFS queue with stable event UUIDs. Keep enrollment/deactivation local via USB serial. Do not assume two-core tasking until profiling requires it.

- [Firmware implementation sequence](../../firmware/README.md)
- [Electrical-safe wiring](../../docs/wiring.md)
- [Hardware gates](../../hardware/test-plan.md)
