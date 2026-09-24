# 06 - Firmware Plan

[[00 - Project Overview|⬅️ Hub]] | [[05 - Software Stack|Stack ⬅️]] | [[07 - Backend Plan|Backend ➡️]]

**Status:** Toolchain-check sketch only. Enrollment, identification, RTC, OLED, network, authentication, LittleFS queue, recovery, and watchdog behavior are not implemented.

Implement bounded sensor/UI operations first, then RTC validation, device-authenticated event submission, and a crash-safe LittleFS queue with stable event UUIDs. Keep enrollment/deactivation local via USB serial. Do not assume two-core tasking until profiling requires it.

- [Firmware implementation sequence](../../firmware/README.md)
- [Electrical-safe wiring](../../docs/wiring.md)
- [Hardware gates](../../hardware/test-plan.md)
