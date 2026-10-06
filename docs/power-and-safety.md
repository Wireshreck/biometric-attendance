---
type: hardware
area: hardware
status: blocked
tags:
  - hardware
  - safety
  - gates
---
# Power and Electrical Safety

**Status:** The reported R307S connection is assembled, but measured voltage/current evidence is absent. Sensor main rail and UART levels are **UNVERIFIED — REQUIRES MULTIMETER**.

## Current reported wiring

| R307S harness wire | Reported connection | Status |
|---|---|---|
| Red | ESP32 VIN | Owner-reported; exact PCB pin assignment/jumper path not measured |
| Black | ESP32 GND | Owner-reported common ground |
| Yellow | ESP32 GPIO32 RX | Owner-reported sensor TX to ESP32 RX |
| Green | ESP32 GPIO33 TX | Owner-reported ESP32 TX to sensor RX |
| Blue | Disconnected | Owner-reported |
| White | Disconnected | Owner-reported |

The R307S quick-start gives 5V/GND/TXD/RXD as its example wiring; the R307-family datasheet gives 4.2–6.0 V for that family and discusses a 3.3 V board jumper. Neither document verifies this unit's exact PCB variant, six-wire mapping, jumper state, or measured rail. Pin 5/6 touch-function claims in existing research are family/third-party based and not required for UART operation according to that research; leave them disconnected during diagnostics unless the exact R307S manual/board confirms otherwise.

## Mandatory cautions

- ESP32 GPIO inputs are not 5 V tolerant. Do not connect a sensor TX line to GPIO until its high voltage has been measured and is safe for ESP32.
- Verify module connector/pad labels and jumper configuration against the exact physical board. Wire colors are observations only.
- Do not short GPIOs, connect unknown USB pads, bridge unknown solder links, or apply an unverified supply.
- Do not use the Panasonic CR2032 as the R307S main supply. It is only a possible RTC backup cell, and the DS3231 board's charging circuit must be checked before installing a primary coin cell.
- No multimeter is currently available per project context. Mark supply/logic checks **UNVERIFIED — REQUIRES MULTIMETER**; software line probing is not a substitute.
- Do not add a capacitor, level shifter, or external supply until the failure is characterized and the exact component specifications are known.
- Drive buzzer modules through a transistor/driver if their current exceeds GPIO capability. The SSD1306 OLED, the green/red LEDs, and their series resistors were removed from this project; there are no indicator LEDs to protect and no indicator-resistor requirement for the current configuration.
- For Wi-Fi/backend tests, use synthetic values on the isolated local demo network. Never use live student data or expose the API to the public internet.

## Measurement gate

Before future R307S electrical diagnosis, document the exact board marking/revision, connector orientation, jumper state, and continuity-ground result. With suitable equipment and safe probe access, record VIN at sensor, sensor TX idle high, current draw, and ESP32 rail during idle/capture/Wi-Fi load. Do not proceed if pin identity or voltage safety is uncertain.

References: [R307S quick-start](https://www.mantech.co.za/Datasheets/Products/md0652-240817c.pdf), [R307 family datasheet](https://www.mantech.co.za/datasheets/products/MD0652-240817B.pdf), [Espressif ESP32 datasheet](https://documentation.espressif.com/esp32_datasheet_en.pdf?hkey=EF798316E3902B6ED9A73243A3159BB0).
