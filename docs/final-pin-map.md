# Final firmware pin map (current hardware)

**Status:** GPIO assignments are selected and firmware-configured; external electrical interfaces are not fully verified. R307S power and UART voltage are **UNVERIFIED — REQUIRES MULTIMETER**. Exact board/module revisions have not been independently identified.

This is the source of truth for GPIO assignments. ESP32 board is assumed to be a classic ESP32-WROOM DevKit with USB-UART on GPIO1/3. Confirm the board silk and module marking before assembly. The user-reported R307S wiring stays in place; this map does not instruct rewiring it.

| Component | Component pin | ESP32 connection | Direction | Voltage / notes | Breadboard coordinate | Status |
|---|---|---|---|---|---|---|
| R307S | 1 red (reported) | VIN | supply | Reported assembled. Rail voltage/current unknown. Do not use CR2032. | Existing assembly | UNVERIFIED electrically |
| R307S | 2 black (reported) | GND | return | Common ground reported | Existing assembly | Owner-reported |
| R307S | 3 yellow (reported TX) | GPIO32 / UART2 RX | input | Sensor TX must be measured safe for ESP32 first | P-row bearing GPIO32 silk | Connected; no valid response reported |
| R307S | 4 green (reported RX) | GPIO33 / UART2 TX | output | ESP32 UART is 3.3 V logic; exact sensor RX tolerance unknown | P-row bearing GPIO33 silk | Connected; no valid response reported |
| R307S | 5 blue | Open | — | Leave disconnected until exact board manual identifies it | Insulate loose end | NOT CONNECTED |
| R307S | 6 white | Open | — | Leave disconnected until exact board manual identifies it | Insulate loose end | NOT CONNECTED |
| SSD1306 module | VCC | ESP32 3V3, only if module label/spec accepts 3.3 V | supply | Do not use 5 V unless exact board documentation confirms I2C pull-ups remain 3.3 V-safe | 3V3 rail | NEEDS MODULE CHECK |
| SSD1306 module | GND | GND | return | Shared ground | ground rail | NEEDS TESTING |
| SSD1306 module | SDA | GPIO21 | bidirectional open-drain | 3.3 V pull-up domain; shared with RTC | P-row bearing GPIO21 | NEEDS TESTING |
| SSD1306 module | SCL | GPIO22 | output/open-drain | 3.3 V pull-up domain; shared with RTC | P-row bearing GPIO22 | NEEDS TESTING |
| DS3231 breakout | VCC | ESP32 3V3 only if exact breakout supports it | supply | Check breakout markings; verify coin-cell charging circuit before primary CR2032 installation | 3V3 rail | NEEDS MODULE CHECK |
| DS3231 breakout | GND | GND | return | Shared ground | ground rail | NEEDS TESTING |
| DS3231 breakout | SDA/SCL | GPIO21/GPIO22 | bidirectional open-drain | Shared I2C bus; scan addresses; avoid 5 V pull-ups | P-rows for 21/22 | NEEDS TESTING |
| Green indicator | anode through series resistor | GPIO18 | output | 3.3 V GPIO; resistor selected for LED/module current | P-row bearing GPIO18 | NEEDS COMPONENT CHECK |
| Green indicator | cathode | GND | return | No bare LED directly across GPIO and ground | ground rail | NEEDS COMPONENT CHECK |
| Red indicator | anode through series resistor | GPIO19 | output | 3.3 V GPIO; resistor selected for LED/module current | P-row bearing GPIO19 | NEEDS COMPONENT CHECK |
| Red indicator | cathode | GND | return | No bare LED directly across GPIO and ground | ground rail | NEEDS COMPONENT CHECK |
| Active buzzer | IN/+ | GPIO23 if module is 3.3 V GPIO-compatible; otherwise driver | output | Check module voltage/current. Do not power an unknown load from GPIO | P-row bearing GPIO23 | NEEDS COMPONENT CHECK |
| Active buzzer | GND/- | GND | return | Common ground | ground rail | NEEDS COMPONENT CHECK |

## ESP32-only pins

GPIO1/3 remain USB serial. GPIO25/26 are reserved for isolated UART loopback tests. Do not attach another circuit to them during that test. Current production assignments have no intended GPIO collision. Avoid GPIO0/2/5/12/15 strap pins, GPIO6–11 flash pins, and GPIO34–39 for outputs. See [Espressif's ESP32 DevKit guide](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html) and [ESP32 datasheet](https://documentation.espressif.com/esp32_datasheet_en.pdf?hkey=EF798316E3902B6ED9A73243A3159BB0).

## R307S uncertainty

The owner's harness positions/colors and 32/33 route are recorded as reported assembly. An R307S quick-start gives 5 V/GND/TXD/RXD examples, while family materials describe voltage and jumper variants. These do not verify this sensor's PCB pads or logic voltage. Keep its current arrangement documented; before electrical reconnection or production use, establish connector pin numbering and measure VIN and TX high level. See [power safety](power-and-safety.md) and [R307S research](r307s-hardware-research.md).
