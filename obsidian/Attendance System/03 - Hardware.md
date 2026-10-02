---
type: project-navigation
status: NEEDS HARDWARE VERIFICATION
updated: 2026-10-02
---

# 03 - Hardware

[[00 - Project Overview|⬅️ Hub]] | [[02 - Architecture|Architecture ⬅️]] | [[04 - Bill of Materials|BOM ➡️]]

**Status:** IN PROGRESS — firmware diagnostics/builds exist; physical component tests are not verified in this session.
- **ESP32 DevKit V1:** USB upload/serial was reported working previously; current exact port is not established here.
- **R307S Fingerprint Sensor:** Physically acquired with a 6-wire harness (Observed order: 1: Red, 2: Black, 3: Yellow, 4: Green, 5: Blue, 6: White).
  - **Connection State:** Owner reports harness assembled red→VIN, black→GND, yellow→GPIO32, green→GPIO33; blue/white disconnected.
  - **Observed communication:** zero response bytes in prior diagnostic; exact power, PCB pin functions, jumper, and logic levels remain **UNVERIFIED — REQUIRES MULTIMETER / exact-board inspection**.
  - Do not treat wire colors or family documentation as proof of this board's pinout.

Provisional system: classic ESP32-WROOM-32 DevKit, **R307S optical fingerprint sensor (in hand; pinout/voltage unverified)**, SSD1306 128×64 I2C OLED, DS3231 RTC, LEDs/resistors, driver-equipped active buzzer, breadboard/jumpers and data USB cable. GPIO assignments are provisional.

> [!WARNING]
> **ELECTRICAL INTEGRATION BOUNDARY:** ESP32 GPIO is 3.3V and not 5V tolerant. The reported GPIO32/33 assembly is not electrically characterized. Refer to [pin map](../../docs/esp32-pin-map.md), [power and safety](../../docs/power-and-safety.md), and [R307S Integration Plan](../../docs/r307s-integration-plan.md).

- [R307S Integration Plan](../../docs/r307s-integration-plan.md)
- [Hardware selection and limits](../../docs/hardware.md)
- [Electrical-safe provisional wiring](../../docs/wiring.md)
- [Bench bring-up gates](../../hardware/test-plan.md)
