---
type: hardware
area: hardware
status: unverified
tags:
  - hardware
  - components
---
# Hardware Selection and Verification

**Status:** NEEDS HARDWARE — the project owner identifies the acquired unit as R307S and reports it assembled to ESP32 VIN/GND/GPIO32/33. The UART diagnostic has reportedly returned zero bytes. Exact board pin functions, supply voltage/current, jumper state, and logic levels remain **UNVERIFIED — REQUIRES MULTIMETER / exact-board inspection**. See [R307S research](r307s-hardware-research.md), the [BOM](bill-of-materials.md), [wiring](wiring.md), [pin map](final-pin-map.md), and [bring-up gates](../hardware/test-plan.md).

## Selected MVP hardware

| Part | Interface/use | Evidence/status |
| --- | --- | --- |
| Classic ESP32-WROOM-32 DevKit | Wi-Fi, configurable UART, I2C, GPIO, USB serial | Target selected; 30/38-pin clones differ. Verify exact board and exposed pins. |
| R307S optical fingerprint module (**in hand; reported connected**) | Intended sensor-side image processing/match; UART slot result to ESP32 | Owner reports red→VIN, black→GND, yellow→GPIO32, green→GPIO33; blue/white open. Zero response reported across diagnostic probes. Exact electrical mapping and power remain unverified; do not claim working or dead. |
| DS3231 breakout | GPIO25/26 I2C, address 0x68; offline time | Breakout, EEPROM, pull-ups, battery holder and charging path vary. Identify board before cell installation. |
| Active buzzer module | GPIO27 output | Audible feedback; verify module voltage/current and use a driver if needed. |
| LEDs, series resistors | Removed from this project (OLED damaged; no resistors available) | Former GPIO18/GPIO19 output indicators; those GPIOs are unused/reserved. |
| Breadboard, jumper sets, data USB cable | prototype assembly/programming | Verify compatibility, sound contacts, and USB data lines. |

## Constraints and decisions

- Classic ESP32-WROOM GPIO is 3.3V logic and not 5V tolerant. Current roles are GPIO32/33 for UART, 25/26 for I2C (DS3231 only; OLED removed), and 27 for buzzer. GPIO18/19 are unused/reserved. See the authoritative [pin map](final-pin-map.md). Confirm exact board/module before additions.
- Do not connect any 5V pull-up or signal to ESP32 GPIO. Power I2C modules at 3V3 when supported. The R307S exact supply and UART TX level are unverified; no additional wiring changes before safe meter/board inspection.
- Do not install a primary CR2032 in a charger-equipped RTC board. Match the cell to the exact module circuit/documentation.  - USB 5V is the proposed source. Measure rail stability with Wi-Fi bursts and buzzer active; sensor illumination is not applicable because the OLED was removed. The 3V3 regulator headroom is board-dependent.

- Use 2.4GHz Wi-Fi. Keep the demonstration network isolated; the planned local HTTP link is not end-to-end encrypted.
- Enclosure/mounting, cable strain relief, power budget under load, and exact sensor slot capacity are unresolved until hardware arrival.

No physical button is in the selected BOM. MVP enrollment/deactivation starts from the locally attached USB serial console; add a button only if a tested UX need justifies its BOM/wiring change.
