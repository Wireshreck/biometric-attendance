---
type: hardware
area: hardware
status: unverified
tags:
  - hardware
  - pinout
  - canonical
---
# Final firmware pin map (current hardware)

**Status:** GPIO assignments are selected and firmware-configured; external electrical interfaces are not fully verified. R307S power and UART voltage are **UNVERIFIED — REQUIRES MULTIMETER**. Exact board/module revisions have not been independently identified.

This is the source of truth for GPIO assignments. ESP32 board is assumed to be a classic ESP32-WROOM DevKit with USB-UART on GPIO1/3. Confirm the board silk and module marking before assembly. The user-reported R307S wiring stays in place; this map does not instruct rewiring it.

Removed from this project: SSD1306 OLED and green/red LEDs (no resistors available). The peer I2C device on GPIO25/26 is now only the DS3231; do not attach any other I2C device until its 3.3 V pull-ups are verified.

| Component | Component pin | ESP32 connection | Direction | Voltage / notes | Breadboard coordinate | Status |
|---|---|---|---|---|---|---|
| R307S | 1 red (reported) | VIN | supply | Reported assembled. Rail voltage/current unknown. Do not use CR2032. | Existing assembly | UNVERIFIED electrically |
| R307S | 2 black (reported) | GND | return | Common ground reported | Existing assembly | Owner-reported |
| R307S | 3 yellow (reported TX) | GPIO32 / UART2 RX | input | Sensor TX must be measured safe for ESP32 first | P-row bearing GPIO32 silk | Connected; no valid response reported |
| R307S | 4 green (reported RX) | GPIO33 / UART2 TX | output | ESP32 UART is 3.3 V logic; exact sensor RX tolerance unknown | P-row bearing GPIO33 silk | Connected; no valid response reported |
| R307S | 5 blue | Open | — | Leave disconnected until exact board manual identifies it | Insulate loose end | NOT CONNECTED |
| R307S | 6 white | Open | — | Leave disconnected until exact board manual identifies it | Insulate loose end | NOT CONNECTED |
| SSD1306 module | — | not connected | — | OLED removed from this project (damaged). Do not route GPIO25/26 to any display. | — | REMOVED |
| DS3231 breakout | VCC | ESP32 3V3 only if exact breakout supports it | supply | Check breakout markings; verify coin-cell charging circuit before primary CR2032 installation | 3V3 rail | NEEDS MODULE CHECK |
| DS3231 breakout | GND | GND | return | Shared ground | ground rail | NEEDS TESTING |
| DS3231 breakout | SDA/SCL | GPIO25/GPIO26 | bidirectional open-drain | Shared I2C bus with no other device; scan addresses; avoid 5 V pull-ups | P-rows for 25/26 | NEEDS TESTING |
| Green indicator | — | not connected | — | LED + series resistor removed from this project (no resistors available). GPIO18 is unused/reserved. | — | REMOVED |
| Red indicator | — | not connected | — | LED + series resistor removed from this project (no resistors available). GPIO19 is unused/reserved. | — | REMOVED |
| Active buzzer | IN/+ | GPIO23 if module is 3.3 V GPIO-compatible; otherwise driver | output | Check module voltage/current. Do not power an unknown load from GPIO | P-row bearing GPIO23 | NEEDS COMPONENT CHECK |
| Active buzzer | GND/- | GND | return | Common ground | ground rail | NEEDS COMPONENT CHECK |

## ESP32-only pins

GPIO1/3 remain USB serial. GPIO25/26 are used by the DS3231 I2C bus and by the isolated UART loopback test. Do not attach another circuit to them during that test. Current production assignments have no intended GPIO collision. Avoid GPIO0/2/5/12/15 strap pins, GPIO6–11 flash pins, and GPIO34–39 for outputs. See [Espressif's ESP32 DevKit guide](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html) and [ESP32 datasheet](https://documentation.espressif.com/esp32_datasheet_en.pdf?hkey=EF798316E3902B6ED9A73243A3159BB0).

## Unused/reserved GPIOs

GPIO18 and GPIO19 are currently unused. They were previously assigned to green/red indicator LEDs with series resistors; both the LEDs and the resistors were removed from this project. Do not assume they are available for new hardware without updating this pin map, config.h, and the wiring docs.

## R307S uncertainty

The owner's harness positions/colors and 32/33 route are recorded as reported assembly. An R307S quick-start gives 5 V/GND/TXD/RXD examples, while family materials describe voltage and jumper variants. These do not verify this sensor's PCB pads or logic voltage. Keep its current arrangement documented; before electrical reconnection or production use, establish connector pin numbering and measure VIN and TX high level. See [power safety](power-and-safety.md) and [R307S research](r307s-hardware-research.md).
