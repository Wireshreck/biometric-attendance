# Hardware Pinout

The provisional map and electrical safety checks are maintained in [docs/wiring.md](../docs/wiring.md). Pin assignments have **not** been physically verified. Do not treat sensor wire colors, breakout pull-ups, or supply/logic-voltage claims as verified until exact module labels/manuals are inspected.

| Function | Provisional ESP32 pin | Verification status |
| --- | --- | --- |
| AS608 UART RX/TX | GPIO16 / GPIO17 | Unverified; confirm exact module (WROOM vs WROVER), board exposure, and UART voltage; UART routing is configurable |
| I2C SDA/SCL (OLED + RTC) | GPIO21 / GPIO22 | Unverified; confirm 3.3V pull-ups and addresses |
| Green / red LED | GPIO18 / GPIO19 through series resistors | Unverified |
| Active buzzer input | GPIO23 through driver module | Unverified |

Update this file and [docs/wiring.md](../docs/wiring.md) together after bench validation.
