# Hardware Bring-Up and Verification Plan

**Status: PLANNED.** No physical bench results are recorded. Tests below are gates; enter date, board revision, instrument, measured result, and pass/fail before proceeding.

| ID | Gate | Method | Pass criterion / record |
| --- | --- | --- | --- |
| HW-01 | Board and supply identification | Read exact ESP32 board/module labels; check USB cable data capability; inspect supply | Record board revision, USB-UART bridge, input and regulator labels; no visibly damaged part |
| HW-02 | Power rails | No peripherals first; multimeter; then add one load at a time | 5V and 3V3 stable within selected board spec at idle and peak activity; no heating, brownout, or reversed polarity |
| HW-03 | RTC battery safety | Inspect exact DS3231 board charging circuit and datasheet before inserting cell | Battery type matches board; primary CR2032 is never connected to a charging circuit |
| HW-04 | I2C | Power OLED/RTC at 3V3; scan bus at 100 kHz on GPIO21/22 | Expected addresses respond; bus high never exceeds 3.3V; record pull-up resistance/board details |
| HW-05 | LED and buzzer | Test one output at a time with current limit/resistors | Correct state/polarity; buzzer has suitable transistor driver; no ESP32 pin overcurrent |
| HW-06 | AS608 UART | Confirm exact VCC and TX/RX level from module evidence; common ground; UART2 GPIO16/17 at documented baud | Sensor handshake succeeds repeatedly; TX high <=3.3V; record supply current and firmware/baud |
| HW-07 | Combined load | Enable display, RTC, sensor, buzzer, Wi-Fi; observe serial and rail | No brownout, reset, excessive rail drop, or warm connector; log peak current if instrument available |
| HW-08 | RTC persistence | Set test time with explicit timezone convention, remove USB for 10 minutes, restore | Clock advances and retains time; compare measured drift; no network required |
| HW-09 | Fingerprint operation | Enroll/delete synthetic test finger using consented tester | Repeated enroll, identify, delete/re-enroll works; record exact capacity and failures; do not claim FAR/FRR from this check |

## Bring-up sequence

1. Photograph and label exact board/module revisions; inspect for solder bridges and damaged connectors.
2. Use [provisional wiring](../docs/wiring.md); leave AS608, RTC cell, LEDs, and buzzer disconnected for initial board power test.
3. Add OLED/RTC with 3.3V pull-ups verified; run I2C scan.
4. Add indicators through resistors and a driver-equipped buzzer module.
5. Add AS608 only after supply and UART logic levels are verified; start at module-recommended baud (configured plan: 57600).
6. Run combined load and RTC backup checks. Stop if rail sags, a component heats, or the ESP32 repeatedly resets.
7. Only then proceed to firmware/application integration.

No test sketches listed in old planning documents are present in the repository. The initial tests should be added as explicit PlatformIO environments or documented one-off sketches before they are claimed to exist.
