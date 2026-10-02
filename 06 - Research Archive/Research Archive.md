---
type: research
area: research
status: active
tags:
  - research
  - r307s
  - protocol
  - hardware-investigation
---

# 06 - Research Archive

**HOME** [[00 - Vault Hub]] · **UP** [[00 - Vault Hub]] · **RELATED** [[02 - Hardware Lab]] [[05 - Testing Lab]] [[09 - Decision Room]] · **CANVAS** [[06 - Research Archive/06 - Research Archive.canvas]]

What we know, how we know it, and how confident we are. The R307S is the most investigated object in this project and the one we understand least.

---

## The R307S: identity

**R307S** — a member of the GROW / Hangzhou Grow **R30X** family, a sibling of the R307. Optical fingerprint module with a **6-wire harness** and an onboard **Synochip AS606** controller.

> [!WARNING] Everything below describes the *family*, not *this board*.
> The exact PCB revision, connector order, jumper state and pad labels of the unit on the bench have never been confirmed against a datasheet, because the unit has never spoken.

---

## Pinout (family-level)

| Pin | Function | Note |
|---|---|---|
| 1 | VCC | **4.2 – 6.0 V** DC. One listing claims 3.6 V min |
| 2 | GND | |
| 3 | TXD | out of the module |
| 4 | RXD | into the module |
| 5 | TOUCH out | HIGH when a finger is present — **only if pin 6 is powered** |
| 6 | touch-sense power | 3.3–5 V, ~5 µA |

Current: ~50 mA typical, ~80 mA peak. Onboard 3.3 V LDO plus a TTP233D touch IC. **No dedicated power LED** — the blue illumination LEDs are the only visible indicator.

### The jumper that can silently kill it

The board has a **3.3 V solder jumper**:

- **open** (factory default) → pin 1 feeds the onboard LDO, 5 V input expected
- **shorted** → LDO bypassed, pin 1 **must** be 3.3 V

**5 V into a shorted jumper is a silent death.** This is the single most likely physical explanation for total silence and it cannot be checked from software.

---

## Protocol (family-level)

UART 8-N-1. Default baud **57600** (= 9600 × 6). The documented valid set is exactly **9600 × N, N = 1…12**.

```text
 0xEF 0x01 │ 32-bit address │ PID │ length (2B) │ content │ checksum (2B)
           └ default 0xFFFFFFFF ─┘
```

- PID: `01` command · `02` data · `07` ACK · `08` end
- Checksum: sum of PID + length + content, mod 2¹⁶
- Default password `0x00000000`
- **A mismatched address is ignored in complete silence** — indistinguishable from a dead sensor over the wire
- The module also exposes USB 2.0 and enumerates as a virtual COM port. On the R307S it appears as **4 unpopulated solder pads in UNVERIFIED order** → [[docs/r307s-usb-test.md]]

Touch circuitry is irrelevant to UART operation.

### Open disagreement

Capacity is reported as **1000** (datasheet) and **300** (one retail listing). Only `ReadSysPara` from the actual unit settles it. **Do not provision a backend device capacity from either number.**

---

## The evidence chain

This is the most honest body of work in the repository. Full matrix: [[docs/r307s-test-matrix.md]]

```text
HW-01  power wiring topology          WIRED per owner report; voltage NOT measured
HW-02  UART @ 57600, normal routing   TX 16 B → RX 0 B
HW-03  all 12 documented bauds        0 bytes at every one          → baud EXCLUDED
HW-04  VerifyPassword                 0 bytes                        → command correct, no answer
HW-11  software-swapped routing       0 bytes @ 57600 and 9600      → crossed wires EXCLUDED
HW-13  RX idle-state probe            ~2822 mV ADC estimate,
                                      HIGH 200/200 with pull-down
                                      AND pull-up                    → line is DRIVEN
HW-08  unsolicited activity           0 transitions in 1.5 s
HW-05  ReadSysPara (0x0F)             NOT EXECUTED — gated on an ACK
HW-06  TemplateCount (0x1D)           NOT EXECUTED — same gate
HW-10  USB pad path                   NOT EXECUTED — pads unverified, no equipment
```

### What HW-13 actually means

The GPIO32 line is *actively driven high* — under an internal pull-**down** and an internal pull-**up**, 200/200 samples read HIGH. That rules out a floating wire and is consistent with a live sensor TXD idling high.

It does **not** measure a calibrated voltage, does not identify the driver, and says **nothing** about the supply rail. A sensor with a dead UART but a working output stage, or an external pull-up, would look identical.

### What is still open

1. Is the module powered? (needs a meter on pin 1)
2. Is the 3.3 V jumper open or shorted?
3. Is the TX high level safe for a 3.3 V, non-5 V-tolerant GPIO?
4. Does the harness actually contact the pads the owner believes it does?
5. Is the ESP32-TX → sensor-RX conductor intact? *(untested — that direction has never been exercised independently)*
6. Does the module boot, and with what address/password?

---

## Sources

1. R307 family datasheet (Mantech MD0652-240817B) — https://www.mantech.co.za/datasheets/products/MD0652-240817B.pdf
2. R307S quick-start (Mantech MD0652-240817C) — https://www.mantech.co.za/Datasheets/Products/md0652-240817c.pdf
3. Circuitstate R307 teardown — https://www.circuitstate.com/tutorials/interfacing-r307-optical-fingerprint-scanner-with-arduino-boards-for-biometric-authentication/
4. EngineersGarage R30X/R307 — https://www.engineersgarage.com/arduino-adafruit-r30x-r307-fingerprint-scanner/
5. Cirkit Designer R307S — https://docs.cirkitdesigner.com/component/771b9270-e39f-44e7-90b0-6e22051fea15/r307s-fingerprint-scanner
6. Robu R307S manual (image PDF) — https://robu-prod-media.s3.ap-south-1.amazonaws.com/uploads/2024/08/R307S-fingerprint-module-user-manual.pdf
7. Sigmanortec (300-capacity claim) — https://sigmanortec.ro/en/optical-fingerprint-sensor-module-r307s-33-5v
8. Arduino dead-R307 thread — https://forum.arduino.cc/t/r307-fingerprint-sensor-not-working-with-arduino-uno-need-help-troubleshooting/1396194

---

## Other research threads

| Topic | Where |
|---|---|
| ESP32 strap / flash / input-only GPIO restrictions | [[docs/final-pin-map.md]] · [Espressif datasheet](https://documentation.espressif.com/esp32_datasheet_en.pdf) |
| I2C addressing and pull-up domains | [[docs/component-tests.md]] |
| RTC validity gating and oscillator health | [[docs/production-firmware.md]] |
| Power, rails, current budget, brownout | [[docs/power-and-safety.md]] |
| Offline synchronisation semantics | [[docs/production-firmware.md]] · [[diagrams/offline-sync.mmd]] |
| Biometric privacy boundary | [[docs/privacy-security.md]] |
| Architecture and trust boundaries | [[docs/architecture.md]] |
| Security controls and their limits | [[SECURITY.md]] · [[docs/privacy-security.md]] |

---

## Documents

[[docs/r307s-hardware-research.md]] · [[docs/r307s-test-matrix.md]] · [[docs/r307s-troubleshooting.md]] · [[docs/r307s-usb-test.md]] · [[docs/r307s-integration-plan.md]] · [[docs/r307s-next-session.md]]

**HOME** [[00 - Vault Hub]] · **UP** [[00 - Vault Hub]] · **RELATED** [[02 - Hardware Lab]] [[05 - Testing Lab]] [[09 - Decision Room]] · **CANVAS** [[06 - Research Archive/06 - Research Archive.canvas]]
