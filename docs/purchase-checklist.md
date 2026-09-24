# Hardware Shopping Checklist

**Order/delivery state:** Not confirmed in project records. **Budget target:** core terminal under ₹3,000; carry-forward planning envelope ~₹2,429 before any conditional RTC battery adjustment. Prices are estimates, not quotes. Three current pre-GST listings were checked 2026-09-24; verify stock, GST, shipping, and local alternatives before paying. See [detailed BOM](bill-of-materials.md) and [wiring safety notes](wiring.md).

Use the status column while shopping: `NOT CONFIRMED` until purchased/received and checked. Do not substitute by name alone; match interface, voltage, and physical connector.

## MUST BUY — one working terminal

| Item / qty | Required spec to show the seller | Why / acceptable alternative | Budget estimate | Status / notes |
| --- | --- | --- | --- | --- |
| ESP32 dev board ×1 | Classic ESP32-WROOM-32, DevKit-style, USB-UART bridge (CP2102/CH340 or equivalent), header pins expose GPIO16/17/18/19/21/22/23; USB connector/cable included or compatible | Core controller; equivalent ESP32-WROOM-32 board only if pinout and PlatformIO board target are confirmed | ₹349 carry-forward estimate; recheck | NOT CONFIRMED — do not buy ESP32-S3/C3 without revising target/config |
| AS608 fingerprint module ×1 | AS608 UART module, exact connector and pin labels documented, matched sensor cable included, module voltage stated | Biometric capture/matching; do not substitute R307/other model without driver and wiring review | ₹799 listing, ex GST | NOT CONFIRMED — retailer page lists 3.3V supply; verify exact package and UART logic before wiring |
| OLED ×1 | SSD1306, 128×64, **4-pin I2C** (VCC/GND/SCL/SDA), 3.3V-safe I2C | Local status prompts; another SSD1306 4-pin module at 0x3C/0x3D is acceptable after scan | ₹163 listing, ex GST | NOT CONFIRMED — listing: ElectronicsComp EC-6769 |
| RTC ×1 | DS3231 I2C breakout, 3V3-compatible supply/bus, battery holder/circuit identified | Battery-backed clock; DS3231 equivalent board only if I2C and backup are supported | ₹189 listing, ex GST | NOT CONFIRMED — module listing: ElectronicsComp EC-2117; inspect cell charge circuit |
| RTC backup cell ×1 | Exact cell type required by the specific RTC breakout | Maintains clock through USB loss | Price not set | CONDITIONAL — do not buy/install CR2032 until you know the board does not charge it; use a specified rechargeable cell if charging is present |
| Active buzzer module ×1 | 3.3V-compatible logic input, onboard transistor driver; note module VCC current | Audible feedback; alternative buzzer plus transistor driver and resistors | ₹35 carry-forward estimate | NOT CONFIRMED — never connect a bare/high-current buzzer directly to GPIO |
| LEDs ×1 red pack + ×1 green pack | Standard 3mm/5mm LEDs; separate colors | Visual status | ₹50 carry-forward combined estimate | NOT CONFIRMED |
| Resistors ×1 assorted pack | Includes 330Ω–1kΩ, ¼W | One series resistor per LED; other values useful for safe signal conditioning | ₹20 carry-forward estimate | NOT CONFIRMED |
| Breadboard ×1 | 830-point solderless, intact power rails | First prototype | ₹125 carry-forward estimate | NOT CONFIRMED |
| Jumper wires ×1 pack each | M-M and M-F Dupont, ~20cm; sensor cable must match actual connector | Breadboard links | ₹130 carry-forward estimate | NOT CONFIRMED — do not force incompatible AS608 connector |
| USB cable ×1 | Data-capable cable matching board connector; ~1m | Programming, serial monitor, initial power | ₹55–89 estimate | NOT CONFIRMED — charge-only cable will not flash firmware |

**Already available per environment audit:** Windows development laptop and USB host. Recheck physically before checkout. A separate supply is not needed to start if a suitable laptop USB port is available, but verify current/voltage during bring-up.

## NICE TO HAVE — stability/demo

| Item / qty | Spec | Why / alternative | Estimate | Status |
| --- | --- | --- | --- | --- |
| USB adapter ×1 | Reputable regulated 5V, 2A supply; compatible data/power cable | Standalone demo power | ₹180 carry-forward estimate | NOT CONFIRMED |
| Base/enclosure ×1 | Non-conductive project box or acrylic plate with mounting space | Prevent breadboard movement and accidental shorts | ₹150–200 estimate | NOT CONFIRMED — do not mount until wiring passes bench checks |
| Foam tape / standoffs ×1 set | Non-conductive mounting hardware | Secure sensor/display | ₹60 estimate | NOT CONFIRMED |
| MB-102 rail supply ×1 | Regulated 3.3V/5V module only if rails verified | Optional alternate power distribution | ₹110 estimate | OPTIONAL — not needed if board rails are sufficient |

## SPARES — only if budget allows

- [ ] ESP32-WROOM-32 board ×1; same pinout/USB-UART variant — estimate ₹349.
- [ ] SSD1306 4-pin I2C display ×1 — estimate ₹163–188.
- [ ] Matching AS608 cable ×1 — confirm connector pitch/pinout before purchase; price unknown.
- [ ] Resistor/LED assortment ×1 — use existing excess pack contents first.

## Checkout checks

- [ ] Compare package labels/connector/pinout with the required spec above.
- [ ] Confirm module supply voltage, UART logic voltage, included sensor cable, RTC cell compatibility, stock, return policy, tax, and delivery estimate.
- [ ] Record seller, exact part/variant, actual paid price, receipt, and delivery date in the BOM after purchase.
- [ ] Keep the receipt and packaging until each component passes its hardware gate.
- [ ] Never power an uncertain connection. Follow the one-module-at-a-time sequence in [hardware test plan](../hardware/test-plan.md).

## Do not buy for the MVP

- Cloud AI credits/subscriptions, a second biometric modality, Arduino Uno/Nano, or a custom PCB before breadboard validation.
- A rechargeable RTC cell or CR2032 by assumption; first identify the RTC module's charge circuit and supported cell.
