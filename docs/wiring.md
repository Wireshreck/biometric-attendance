---
type: hardware
area: hardware
status: unverified
tags:
  - hardware
  - wiring
---
# Wiring and Current Bench Record

**Status:** Current wiring below is owner-reported as physically assembled and UART-tested; electrical measurements remain incomplete. See the authoritative [final pin map](final-pin-map.md), [recommended breadboard layout](complete-breadboard-layout.md), and mandatory [power and safety](power-and-safety.md).

## Reported R307S connections

| R307S harness position/color | Reported connection | Status |
|---|---|---|
| 1 / red | ESP32 VIN | Assembled per owner; rail not measured |
| 2 / black | ESP32 GND | Assembled per owner |
| 3 / yellow | ESP32 GPIO32 (UART2 RX) | Assembled per owner; no valid response |
| 4 / green | ESP32 GPIO33 (UART2 TX) | Assembled per owner; no valid response |
| 5 / blue | disconnected | Assembled per owner |
| 6 / white | disconnected | Assembled per owner |

Harness color/position is an observation, not proof of the physical PCB contact function. R307S main rail, TX logic level, and jumper state are **UNVERIFIED — REQUIRES MULTIMETER / exact-board inspection**. GPIO16/17 directions in older notes are obsolete for the present bench routing; the current wiring uses GPIO32/33 and is documented in config.h and final-pin-map.md.

## Expected I2C assignment (DS3231 only)

- DS3231 SDA/SCL uses GPIO25/26 at 100 kHz. No other I2C device is currently attached. The SSD1306 OLED was removed from this project; do not route GPIO25/26 to any display until the new device's 3.3 V pull-ups are verified.
- Active buzzer uses GPIO23; use a driver if the module current exceeds the GPIO rating.
- UART loopback test environments use a GPIO25 TX to GPIO26 RX jumper. Disconnect the DS3231 from GPIO25/26 before running that test.

## Removed assignments

- Green LED (GPIO18) and red LED (GPIO19) were removed along with their series resistors. Those GPIOs are unused/reserved. Do not add new hardware there without updating this document, config.h, and final-pin-map.md.
- SSD1306 OLED (I2C) was removed. GPIO25/26 remain assigned to DS3231 only.

## Safe procedure

Do not alter the existing assembly solely because old documents disagree. If a connection must be removed/rebuilt, power down first, verify the exact module labels and pin contacts, verify common ground and the jumper state, and measure the supply/TX logic levels before reconnecting to ESP32 GPIO. Do not use a CR2032 for the sensor main supply or connect unidentified USB/solder pads.

The current R307S test is read-only. Do not issue enroll/delete/configuration writes as part of troubleshooting.
