---
type: setup
area: hardware
status: unverified
tags:
  - setup
  - assembly
  - beginner
---
# Complete beginner assembly guide

**Status:** Instructions for the current prototype. Hardware module variants and R307S supply/signal levels remain unverified. Do not power a connection whose labels or voltage are uncertain.

## What the parts do

- **ESP32 DevKit:** small computer running firmware. USB supplies power and provides programming/serial communication during development.
- **R307S:** optical fingerprint sensor. It stores templates inside its module and reports a slot number over UART; the firmware sends no image or template to the backend. Its current response is unverified.
- **OLED:** display using SDA/SCL I2C signals.
- **DS3231 RTC:** keeps date/time with backup power. Firmware refuses to create an attendance timestamp if the clock is invalid.
- **LEDs:** visual success/failure indicators. A resistor in series limits LED current.
- **Active buzzer module:** makes sound when its input is activated. Exact module voltage/current varies.
- **Breadboard:** temporary connection board. Power rails distribute power; five-hole groups in the terminal field are connected horizontally on each side of the center trench.
- **Jumper wires:** insulated wires joining distinct breadboard groups and device pins.

## Identify pins before wiring

1. Read the small labels printed beside the ESP32 header. Board clones can differ, so use the label, not a remembered left/right drawing.
2. Identify R307S connector pin-1 marker or board silkscreen. The recorded red/black/yellow/green mapping is owner-reported, not independently verified. Keep the current assembly unchanged unless a specific electrical check requires a change.
3. Read the exact OLED and RTC breakout labels (`VCC`, `GND`, `SDA`, `SCL`). Some modules accept 5 V on VCC but pull I2C up to VCC, which could put 5 V on ESP32 GPIO. Use 3V3 only after confirming module support.
4. An LED's long leg is usually its anode and short/flat side its cathode. Check markings when available; leg length may have been trimmed.
5. Read the buzzer voltage/current/input labels. The exact module is not identified, so GPIO23 compatibility is not proven.

## Place the ESP32

Follow [recommended breadboard layout](complete-breadboard-layout.md). With USB unplugged, place the ESP32 across the center trench only if both header rows fit naturally into separate holes. The layout's P01–P15 are custom labels, not printed coordinates. Match each row to the actual ESP32 silk. Do not force a board that is too wide.

## Incremental wiring order

Do not power the circuit while adding wires. Add one subsystem at a time and compare each lead to the table below: (0) unplug all power; (1) place ESP32; (2) place OLED; (3) place RTC; (4) place LEDs and resistors; (5) place buzzer; (6) connect only verified power/ground; (7) add I2C; (8) add indicators; (9) preserve/document the existing R307S UART; (10) inspect all connections; (11) run core test; (12) scan I2C; (13) OLED test; (14) RTC test; (15) LED and buzzer tests; (16) UART loopback with R307S disconnected; (17) R307S diagnostic only after its electrical safety gate; (18) Wi-Fi test; (19) backend health test; (20) full integration only after each prerequisite passes. See `docs/component-tests.md` for the exact environment names and results each test proves.

## Connection list

| Wire | From | To | Purpose | Notes |
|---:|---|---|---|---|
| 1 | ESP32 GND | breadboard ground rail | shared return | Sensor ground is owner-reported connected here |
| 2 | ESP32 3V3 | 3.3 V rail | module logic supply | Only for modules confirmed to accept it; never bridge to GND |
| 3 | OLED GND | ground rail | common return | Verify module labels |
| 4 | OLED VCC | 3.3 V rail | OLED supply | Exact module must support 3.3 V |
| 5 | OLED SDA | ESP32 GPIO21 | I2C data | Pull-up must be 3.3 V-safe |
| 6 | OLED SCL | ESP32 GPIO22 | I2C clock | Pull-up must be 3.3 V-safe |
| 7 | DS3231 GND | ground rail | common return | Verify module labels |
| 8 | DS3231 VCC | 3.3 V rail | RTC supply | Confirm board supports it and inspect charging circuit |
| 9 | DS3231 SDA | ESP32 GPIO21 | shared I2C data | Same bus as OLED |
| 10 | DS3231 SCL | ESP32 GPIO22 | shared I2C clock | Same bus as OLED |
| 11 | ESP32 GPIO18 | green LED anode through series resistor | success light | LED cathode to ground; do not omit resistor |
| 12 | ESP32 GPIO19 | red LED anode through series resistor | error light | LED cathode to ground; do not omit resistor |
| 13 | ESP32 GPIO23 | buzzer module input | audible feedback | Only if voltage/current are GPIO-safe; else use driver |
| 14 | buzzer module GND | ground rail | common return | Verify polarity |
| 15 | R307S red, reported pin 1 | ESP32 VIN (existing assembly) | reported sensor supply | Rail/current unmeasured; not powered from CR2032 |
| 16 | R307S black, reported pin 2 | ESP32 GND (existing assembly) | reported return | Owner-reported existing connection |
| 17 | R307S yellow, reported pin 3/TX | ESP32 GPIO32 / UART2 RX (existing) | sensor serial output | No valid response reported; voltage is unmeasured |
| 18 | ESP32 GPIO33 / UART2 TX | R307S green, reported pin 4/RX (existing) | serial command | Owner-reported existing connection |
| — | R307S blue/white, reported pins 5/6 | nowhere; insulate separately | unused in current assembly | Exact function depends on board variant |

The [final pin map](final-pin-map.md) is the single GPIO source of truth. Harness color alone does not prove sensor contact function. R307S VIN and TX signal are **UNVERIFIED — REQUIRES MULTIMETER**. See [power safety](power-and-safety.md).

## Inspect before powering

Before USB:

- [ ] ESP32 orientation correct and headers fit without bending
- [ ] No wire crosses/join power rails accidentally
- [ ] Common GND connections checked while unpowered
- [ ] No 5 V / 3.3 V short or 5 V GPIO path
- [ ] R307S board/jumper mapping documented (currently unverified)
- [ ] R307S VIN and TX level measured safe (currently requires multimeter; do not claim checked)
- [ ] OLED power and pull-up voltage verified
- [ ] RTC power/battery charging circuit verified
- [ ] Both LEDs have series resistors
- [ ] Buzzer voltage/current and driver verified
- [ ] Blue/white sensor leads insulated separately
- [ ] No exposed wire strands touch adjacent rows

Only after each applicable checklist item is confirmed should USB be connected.

1. Unplug USB and external supplies.
2. Confirm ESP32 and module labels, LED polarity/resistors, and buzzer requirements.
3. Check for accidental 3V3-to-GND connections, any 5 V-to-GPIO path, and direct LED connection without a resistor.
4. Verify that the RTC board will not charge the installed primary CR2032. If unsure, leave the coin cell out until the board is identified.
5. Keep loose sensor blue/white leads separated. Never use the CR2032 for its main supply.
6. Connect USB to the ESP32 alone. Do not inject another voltage into VIN/5V or 3V3 at the same time.
7. Begin with I2C scan and standalone component tests. Only mark a hardware test passed after observing it physically and recording the result.

## Software and enrollment

Install Git, Python, PlatformIO Core, and a USB serial driver if Windows does not create a COM port. From the repository root, build with `pio run -d firmware -e production`. Copy `firmware/include/local_config.example.h` to ignored `firmware/include/local_config.h`; fill only local demo Wi-Fi values, server address, device UUID, and the one-time provisioned token. Never commit that file. Upload with `pio run -d firmware -e production -t upload --upload-port COMx`; monitor with `pio device monitor -d firmware --port COMx --baud 115200`.

Configure a local backend and create a pending student through its authenticated admin API first. Connect the ESP32 USB serial monitor and enter `ENROLL <student-uuid>`. The device fetches the slot assignment and asks for two captures. Normal attendance scans never enroll a finger. Backend confirmation retries after reboot using a durable NVS intent. R307S has not responded in the current hardware report, so enrollment is implemented but not physically verified.

See [firmware instructions](../firmware/README.md), [API plan](api-plan.md), [failure modes](failure-modes.md), and [test plan](hardware-test-plan.md) for test order and setup. Use synthetic students in a local test database, never real attendance records for demonstration tests.
