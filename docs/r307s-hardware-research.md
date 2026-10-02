# R307S Hardware Research

**Document:** `docs/r307s-hardware-research.md`
**Date:** 2026-10-01
**Scope:** R307S optical fingerprint sensor (GROW / Hangzhou Grow Technology), the module wired to this repository's ESP32 terminal.
**Evidence tags:** **[OWNER-REPORTED]** = current assembled setup/results reported by the project owner; not independently repeated in this session. **[DOC]** = published datasheet/manual fact. **[INF]** = deduction; reasoning shown. Historical bench-log details in §8 are retained as provenance and should not be mistaken for new measurements.

> **R307 vs R307S:** the R307S is the compact sibling of the R307 in GROW's R30X series. Core electrical/protocol data is documented at family level; where a value is R307-only documentation, that is stated explicitly and not silently applied to the R307S.

---

## 1. Reported Harness and Wiring (electrical mapping unverified)

Harness wire colors are this unit's observed order; colors must never be trusted alone over silkscreen/continuity.

| Pin | Wire (observed) | Function | Electrical requirement | Connected to | Source |
| :-- | :-- | :-- | :-- | :-- | :-- |
| 1 | Red | Candidate VCC | Exact unit/revision must be checked; family docs are not proof of this board's wiring | ESP32 **VIN**, owner-reported connection; voltage/current not measured | [OWNER-REPORTED][DOC][1][2] |
| 2 | Black | Candidate GND | Common ground expected | ESP32 **GND**, owner-reported connection; continuity not independently measured | [OWNER-REPORTED][DOC][1][2] |
| 3 | Yellow | Candidate sensor TX | Candidate UART output | ESP32 **GPIO32 (RX)**, owner-reported connection; function not verified at board pad | [OWNER-REPORTED][DOC][1][2] |
| 4 | Green | Candidate sensor RX | Candidate UART input | ESP32 **GPIO33 (TX)**, owner-reported connection; function not verified at board pad | [OWNER-REPORTED][DOC][1][2] |
| 5 | Blue | Unknown on this exact unit | Family sources describe touch function; exact mapping unverified | Disconnected per owner report | [OWNER-REPORTED][DOC][1][3] |
| 6 | White | Unknown on this exact unit | Family sources describe touch supply; exact mapping unverified | Disconnected per owner report | [OWNER-REPORTED][DOC][1][3] |

**No verified six-wire pinout is established for this exact unit.** Treat the table's functions as candidates from family/retailer documentation, not measured identification. Project owner reports this wiring has been physically assembled and the diagnostic returned zero bytes; do not infer the module is powered or healthy.

Board also carries a **3.3V solder jumper** (§5) and, on this variant family, **USB interface pads** (see `docs/r307s-usb-test.md`).

## 2. Power Requirements

- **Supply voltage:** DC 4.2–6.0 V [DOC][1]. Several distributor listings for the R307S state 3.6–6.0 V [DOC][2]; the conservative, family-datasheet figure is used here. The module contains an onboard 3.3 V LDO that feeds the AS606 controller [DOC][1].
- **Operating current:** ~50 mA typical, **80 mA peak** (R307 datasheet) [DOC][1]. R307S listings commonly repeat 50 mA / 80 mA [DOC][2]. This is far below the ESP32 DevKit VIN rail capability from USB (≥500 mA typical), so **VIN powering is electrically adequate on paper**.
- **ESP32 VIN suitability:** VIN is the 5 V USB rail before the DevKit's 3.3 V regulator — correct rail for this module. A breadboard/shared-rail sag under simultaneous loads is not excluded by documentation and was not measurable here (no multimeter).
- **USB-power considerations:** while powered through USB, the ESP32's VIN rail is derived from the PC's 5 V. Brownout during optical capture (LED + DSP surge) is the classic failure documented in the family; a 100 µF capacitor near the sensor is the standard mitigation [DOC — integration plan §5; community-corroborated].

## 3. UART Requirements

- **Default baud:** 57600 (N = 6) [DOC][1].
- **Supported baud set:** **exactly 9600 × N for N = 1…12** → 9600, 19200, 28800, 38400, 48000, 57600, 67200, 76800, 86400, 96000, 105600, 115200 [DOC][1]. Baud values outside this set (e.g. 250000, 14400) are **not valid**. The multiplier is stored in the system-parameter block and can be changed only by a write command (not used here).
- **Frame format:** 8 data bits, no parity, 1 stop bit (8-N-1); 10-bit frames [DOC][1].
- **Direction:** sensor pin 3 TXD → host RX; sensor pin 4 RXD ← host TX [DOC][1].
- **Logic levels:** TTL. Family documentation treats the interface as 3.3 V logic with 5 V-tolerant behavior implied by "interfaced with 5V controller" wording [DOC][1][2]; the **exact TXD output level of this unit is not independently verified** (no multimeter). The current lab evidence is consistent with a ~3.3 V-class idle level [LAB — §8.1].
- **ESP32 compatibility:** direct connection to 3.3 V ESP32 GPIO is the standard, documented practice for this family (multiple ESP32+R307 guides exist) [DOC][5]. No level shifting is indicated for 5 V-rail powering with the default (open) 3.3V jumper.
- **Protocol:** packets = header `EF 01` + 32-bit address + packet ID (`01` cmd, `02` data, `07` ACK, `08` end) + 2-byte length + content + 2-byte checksum (sum of PID+length+content, mod 2^16) [DOC][1]. The module **silently ignores packets whose 32-bit address does not match its own** [DOC][1].

## 4. Touch Circuit

- **Pin 5 (TOUCH):** output of a TTP233D capacitive touch IC; HIGH when a finger is on the window [DOC][1][3].
- **Pin 6 (touch power):** supply input for that touch IC, DC 3.3–5 V, **~5 µA** [DOC][1][3].
- **Relevance to UART operation: none.** The touch circuit only enables finger-presence signaling for host-initiated wake-up. The main controller (AS606), the optical stack, and the UART run from pin 1 power regardless of pins 5/6. By itself, the sensor "starts looking for a scan after a few seconds from power-up" even with touch unpowered [DOC][3].
- **[LAB corroboration:** pins 5/6 are disconnected on this bench, and the family datasheet's ~5 µA touch draw rules them out as a cause of a totally dead module.]

## 5. 3.3V Jumper

Documented for the R307 family [DOC][1][3]; the same jumper/pads are visible on R307S boards [DOC][2 community-consistent].

| Jumper state | Meaning | Use case |
| :-- | :-- | :-- |
| **Open (factory default)** | Pin 1 supply feeds the onboard 3.3 V LDO; the controller runs from the LDO. Pin 1 must be 4.2–6 V. | 5 V-rail powering (ESP32 VIN) — **this project's configuration** |
| **Shorted (solder bridge)** | Pin 1 supply **bypasses the LDO** and feeds the controller directly. Pin 1 must then be 3.3 V. | 3.3 V-only systems (e.g. supply pins 1+6 from 3.3 V) |

**What the jumper does NOT do:** it does not change the UART logic level as a separate setting, and it does not affect only a side circuit — it selects whether the **main controller supply** comes from the LDO or directly from pin 1. Applying 5 V to pin 1 **while the jumper is shorted** would overvolt the controller (damage risk); applying 3.3 V with the jumper open leads to LDO brownout (module dead or unstable).

**Consequence for this bench:** if this unit's jumper had been factory-shipped shorted (non-default, but seen in some batches), powering pin 1 from 5 V VIN would put ~5 V on the controller rail — a possible explanation for a dead module that leaves **no visual trace**. Physical inspection of the pads is required to exclude this; it has not yet been done.

## 6. Startup Behavior

- **Expected power-on sequence [DOC][1][3]:** module boots its AS606 controller; the **blue illumination LEDs behind the window light** (this is the only standard visible indicator — the module has no dedicated power LED [DOC — community-corroborated][6]); after a few seconds the module begins looking for a finger even with the touch circuit unpowered.
- **UART idle:** TXD idles high at the module's logic level.
- **Initialization time:** no hard figure is published; the diagnostic allows ~2 s settle plus per-probe windows, and waits for byte-gap silence before parsing. **[LAB:** the ESP32 side settled in ~2 s; the sensor produced no unsolicited bytes in a 1.5 s monitor window**]**

## 7. Failure Modes

Plausible causes by symptom, cross-referenced to evidence:

**No visible activity (dark window / no LED flash):**
1. No power reaching pin 1 (broken wire, wrong harness position, breadboard contact).
2. Jumper shorted + 5 V input → controller rail overvoltage (§5) — possible permanent damage, invisible from outside.
3. Dead module (DOA or damaged).
4. LED circuit failure only — module alive but dark (rare; unverifiable without UART success or a meter).
- **[INF]** A module drawing 50 mA from VIN that is *properly wired* would usually show at least a power-on LED flash; absence is evidence toward (1)/(2)/(3), but **cannot be confirmed without current measurement**.

**No UART response (0 bytes) despite power:**
1. Module unpowered (supply path broken) — line probe would read floating [LAB discriminator].
2. TXD wire not actually connected to GPIO32 (broken wire / wrong position) — floating line.
3. Module hung at boot (brownout during power-up, e.g. supply sag) — line driven but silent.
4. **Device address changed** from `0xFFFFFFFF` — module silently ignores all packets [DOC][1]. Line stays driven-high; scan shows 0 bytes.
5. Baud outside the documented ladder — excluded here by scanning all 12 [LAB].
6. RXD path broken (ESP32 TX not reaching pin 4) — sensor never hears the command; identical signature to (4).
7. Touch-power pin misidentified as main supply (harness confusion) — module starved.

**Malformed UART response:** baud mismatch at the edge of tolerance, 5 V logic on the ESP32 RX (signal corruption), damaged sensor, or partial wiring (TXD connected, GND open).

**Response at unexpected baud:** module's baud multiplier N was changed by a previous owner/program (any N in 1…12 is legal [DOC][1]). The ladder scan covers every legal value.

## 8. Historical Evidence vs Inference — bench results reported 2026-10-01

The following results were recorded in the prior session via USB serial (reported COM4, 115200); the current task owner also confirms the broad outcome (ESP32 TX active, R307S returned 0 bytes across baud/routing probes). This session did not independently flash or run that hardware diagnostic. Full prior log details are in `docs/r307s-next-session.md`.

1. **[LAB] TX-line idle-state probe (GPIO32, sensor TXD wire):**
   - ADC estimate ≈ **2822 mV** (uncalibrated; ESP32 ADC1, eFuse Vref 1163).
   - Digital reads: **HIGH 200/200 with internal pull-down**, **HIGH 200/200 with internal pull-up**.
   - **Classification: DRIVEN HIGH** — the wire is actively held at a UART-idle-like level by a push-pull output. A floating wire would read high only with the pull-up.
   - [INF] Consistent with a powered R307-family TXD idling at ~3.3 V. **Not** a calibrated voltage measurement — it cannot prove the supply is 5 V, nor measure the exact TXD voltage.
2. **[LAB] RX activity monitor:** **0 transitions in 1500 ms** — no unsolicited/boot bytes from the sensor at any time.
3. **[LAB] Baud ladder scan:** VerifyPassword (0x13) probe at **all 12 documented baud rates**, normal routing: **RX = 0 bytes at every baud**.
4. **[LAB] Swapped-routing probes** (ESP32 UART matrix RX↔TX swap at 57600 and 9600; no wire movement): **0 bytes**. The sensor cannot be hearing the command on the alternate wire either.
5. **[LAB] Overall classification:** **COMPLETELY SILENT on UART, with a driven-high TXD line.**
6. **[INF — strongest conclusion available without a multimeter]:** the wire on GPIO32 is being driven by *something* (most plausibly the sensor's TXD, powered). A powered, healthy module that receives a correctly addressed command at its baud must answer [DOC][1]. Since baud and routing hypotheses are software-exhausted, the remaining hypotheses are: (a) the command never reaches the module (RXD path broken — **the driven-high TXD result says nothing about the sensor→RXD wire**), (b) the module's address is not `0xFFFFFFFF`, (c) the module is hung or dead despite a live TXD output, or (d) the driven wire is not the sensor's TXD at all.
7. **[HONEST LIMIT:** whether the module is actually powered **cannot be determined without measuring voltage or current**. The line probe shows the *wire* is driven, not that the *module* is healthy.]

## 9. Sources

1. R307 Fingerprint Identification Module datasheet (GROW family; Mantech MD0652-240817B PDF): https://www.mantech.co.za/datasheets/products/MD0652-240817B.pdf — parameters table (4.2–6.0 V, 50/80 mA, capacity 1000, baud 9600×N N=1…12 default N=6, dual UART/USB 2.0 interface, "module circuit board is marked with 2 contacts; short circuit of 3.3V means DC 3.3V is adopted").
2. R307S quick-start sheet (Mantech MD0652-240817C PDF): https://www.mantech.co.za/Datasheets/Products/md0652-240817c.pdf — R307S-titled Arduino wiring sheet (5 V supply; TXD/RXD to host UART).
3. Circuitstate — "Interfacing R307 Optical Fingerprint Scanner" (family teardown: pin table incl. pin 5/6 functions, jumper open/short behavior, AS606 controller, TTP233D touch IC, USB virtual-COM, packet protocol, ACK formats): https://www.circuitstate.com/tutorials/interfacing-r307-optical-fingerprint-scanner-with-arduino-boards-for-biometric-authentication/
4. EngineersGarage — "How optical fingerprint scanners work using Adafruit and R30x" (pin 6 = finger-detection supply; jumper short/open = 3.3 V/5 V controller; registers incl. baud multiplier): https://www.engineersgarage.com/arduino-adafruit-r30x-r307-fingerprint-scanner/
5. Cirkit Designer R307S component documentation (R307S-specific listing; 3.6–6.0 V, 50/80 mA, default 57600, 6-pin table): https://docs.cirkitdesigner.com/component/771b9270-e39f-44e7-90b0-6e22051fea15/r307s-fingerprint-scanner
6. AliExpress GROW R307S listing ("R307S fingerprint module has RS232 and USB2.0 at the same time; USB2.0 interface can connect to the computer; RS232 interface is TTL level, default baud..."): https://www.aliexpress.com/item/1005003767546644.html
7. Robu — R307S User Manual PDF (image-based; 33 pp; title confirmed "Thank you for your selection of R307S Fingerprint Identification Module (Module) of GROW"): https://robu-prod-media.s3.ap-south-1.amazonaws.com/uploads/2024/08/R307S-fingerprint-module-user-manual.pdf
8. Hubtronics GROW R307S product page (R307S dual-interface text): https://hubtronics.in/grow-r307s-fingerprint-module
9. Sigmanortec R307S page (**capacity listed as 300** — disagrees with family 1000; documented as a source disagreement): https://sigmanortec.ro/en/optical-fingerprint-sensor-module-r307s-33-5v
10. Arduino Forum thread — dead R307 (no LED, no response; community confirms module has no power LED): https://forum.arduino.cc/t/r307-fingerprint-sensor-not-working-with-arduino-uno-need-help-troubleshooting/1396194

**Source disagreements, documented rather than resolved:**
- Capacity: family datasheet 1000 [1] vs. one R307S retail listing 300 [9]. To be settled definitively by ReadSysPara once the module responds.
- Supply range: 4.2–6.0 V [1] vs 3.6–6.0 V [2][5]. Conservative 4.2 V lower bound used in this project.
