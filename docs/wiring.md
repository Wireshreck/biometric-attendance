# Provisional Wiring and Electrical Bring-Up

**Status: NOT BENCH VERIFIED.** This is a proposed map for the selected ESP32-WROOM-32 DevKit, generic AS608, SSD1306 I2C OLED, and DS3231 breakout. Clone pinouts and modules vary. Identify exact board labels and verify each module manual before applying power.

> **Safety:** ESP32 GPIO is 3.3V logic and is not 5V tolerant. Never connect a signal that can exceed 3.3V. Do not power the RTC cell until its exact charge circuit and cell type are known. Disconnect USB before moving wires.

## Provisional signal map

| Peripheral signal | ESP32 | Notes / checks |
| --- | --- | --- |
| AS608 TX -> ESP UART RX | GPIO16 (provisional) | Confirm exact ESP32 module/board exposes GPIO16 and sensor TX high level <=3.3V; add a proper level shifter if not. |
| ESP UART TX -> AS608 RX | GPIO17 (provisional) | Confirm exact module/board exposes GPIO17 and sensor accepts 3.3V logic. |
| OLED SDA and RTC SDA | GPIO21 | Shared I2C; power breakouts at 3.3V so pull-ups cannot raise bus above ESP32 logic. |
| OLED SCL and RTC SCL | GPIO22 | Confirm addresses by scan; expected OLED 0x3C (some 0x3D), RTC 0x68. |
| Green LED | GPIO18 through 330–1kΩ resistor | Resistor in series; verify polarity and current. |
| Red LED | GPIO19 through 330–1kΩ resistor | Resistor in series; verify polarity and current. |
| Active buzzer module input | GPIO23 | Use a module with a driver transistor; never drive a bare/high-current buzzer directly from GPIO. |
| All grounds | ESP32 GND/common rail | Common reference required for UART/I2C and any external supply. |

UART pin mapping is configurable on classic ESP32 through its GPIO matrix; UART2 does not inherently require GPIO16/17. Those pins are commonly usable on WROOM-32 DevKit boards but are connected to PSRAM on some WROVER modules. Confirm the exact module marking, board schematic/pin exposure, and selected board before wiring; if uncertain, select other safe exposed pins and update firmware config and this map together. Keep GPIO6–11, 0, 2, 5, 12, and 15 unconnected in the prototype. GPIO34–39 are input-only.

## Power-up order

1. With USB disconnected, identify the sensor VCC/GND/TX/RX from its printed labels or exact datasheet; wire colors are not reliable evidence.
2. Initially power the ESP32 and each low-voltage module separately. Measure the board's 3V3 rail and inspect for shorts.
3. Confirm OLED/RTC pull-ups terminate at 3V3. Many RTC/OLED clones contain pull-ups; do not assume their rail or resistor value.
4. Determine whether the AS608 variant supports 3.3V or 5V supply and what its UART output high voltage is. Start at its documented supply. A “5V tolerant” supply rating does not mean 5V-safe UART output.
5. Inspect the buzzer board for an onboard transistor. If absent or uncertain, use a transistor driver and base/gate resistor.
6. Connect common ground, then test peripherals one at a time. Measure 5V and 3V3 rails during Wi-Fi transmission and sensor illumination.
7. Test RTC battery backup only after identifying the breakout's charging circuit. Use only the battery type specified for that exact board. Never charge a primary CR2032.

Use short breadboard leads for I2C; start at 100 kHz, not 400 kHz, until the bus and pull-ups are verified. Record actual board/module revisions and measured values in `hardware/test-plan.md`.
