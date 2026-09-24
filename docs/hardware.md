# Hardware Selection and Verification

**Status:** Parts researched; no physical module revisions or bench results confirmed. See the [BOM](bill-of-materials.md), [shopping checklist](purchase-checklist.md), [provisional wiring](wiring.md), [pinout](../hardware/pinout.md), and [bring-up gates](../hardware/test-plan.md).

## Selected MVP hardware

| Part | Interface/use | Evidence/status |
| --- | --- | --- |
| Classic ESP32-WROOM-32 DevKit | Wi-Fi, configurable UART, I2C, GPIO, USB serial | Target selected; 30/38-pin clones differ. Verify exact board and exposed pins. |
| AS608 optical module | Sensor-side image processing/match; UART slot result to ESP32 | Selected listing reports 500 dpi, UART/USB, <60mA and 3.3V supply. Exact module, template capacity, logic levels, command support, liveness, FAR/FRR are unverified. |
| SSD1306 128×64 4-pin I2C OLED | GPIO21/22 provisional shared bus | Exact module and address must be verified; power at 3V3 and inspect pull-ups. |
| DS3231 breakout | GPIO21/22 I2C, address 0x68; offline time | Breakout, EEPROM, pull-ups, battery holder and charging path vary. Identify board before cell installation. |
| LEDs, series resistors, active buzzer module | GPIO18/19/23 provisional outputs | Use series resistors and a transistor-driver buzzer module; verify polarity/current. |
| Breadboard, jumper sets, data USB cable | prototype assembly/programming | Verify compatibility, sound contacts, and USB data lines. |

## Constraints and decisions

- Classic ESP32-WROOM GPIO is 3.3V logic and not 5V tolerant. GPIO16/17, 21/22, 18/19, 23 are provisional for the selected board. Do not assume every ESP32 variant exposes equivalent pins.
- Do not connect any 5V pull-up or signal to ESP32 GPIO. Power I2C modules at 3V3 when supported. Verify the AS608 TX level before direct UART; use level shifting if needed.
- Do not install a primary CR2032 in a charger-equipped RTC board. Match the cell to the exact module circuit/documentation.
- USB 5V is the proposed source. Measure rail stability with Wi-Fi bursts, sensor illumination and buzzer active; the 3V3 regulator headroom is board-dependent.
- Use 2.4GHz Wi-Fi. Keep the demonstration network isolated; the planned local HTTP link is not end-to-end encrypted.
- Enclosure/mounting, cable strain relief, power budget under load, and exact sensor slot capacity are unresolved until hardware arrival.

No physical button is in the selected BOM. MVP enrollment/deactivation starts from the locally attached USB serial console; add a button only if a tested UX need justifies its BOM/wiring change.
