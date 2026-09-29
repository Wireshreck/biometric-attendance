---
type: project-navigation
status: NEEDS HARDWARE
updated: 2026-09-29
---

# 03 - Hardware

[[00 - Project Overview|⬅️ Hub]] | [[02 - Architecture|Architecture ⬅️]] | [[04 - Bill of Materials|BOM ➡️]]

**Status:** NEEDS HARDWARE — the fingerprint module is physically in hand (R703, acquired 2026-09-29) but its exact variant, electrical specifications, and pinout are **UNVERIFIED — HARDWARE VERIFICATION REQUIRED**; no authoritative R703 datasheet was located as of 2026-09-29. Other parts: order/delivery and bench behavior unconfirmed.

Provisional system: classic ESP32-WROOM-32 DevKit, **R703 UART fingerprint module (in hand; specs unverified)**, SSD1306 128×64 I2C OLED, DS3231 RTC, LEDs/resistors, driver-equipped active buzzer, breadboard/jumpers and data USB cable. GPIO assignments are unverified. Do not assume R703 supply voltage, logic level, or pinout — identify them from the unit itself before any powered connection; also do not assume RTC cell charging or clone board pinout from wire colors/product name.

> [!WARNING]
> **AS608 → R703 migration:** the original plan named an AS608. All active instructions now target the acquired R703; remaining AS608 mentions in the vault/docs are historical (decision log, BOM history). See [[Decision Log]] ADR-012.

- [Hardware selection and limits](../../docs/hardware.md)
- [Electrical-safe provisional wiring](../../docs/wiring.md)
- [Bench bring-up gates](../../hardware/test-plan.md)
