# R307S USB Test Path (Pads on the Module)

**Document:** `docs/r307s-usb-test.md`
**Date:** 2026-10-01
**Status:** RESEARCH ONLY — nothing has been soldered or connected to the USB pads. This document separates what is documented from what requires physical action.

---

## 1. What the documentation says

- The R307/R307S family exposes **two independent interfaces simultaneously**: a TTL UART ("RS232") and a **USB 2.0 device port** [DOC][1][2][6].
- "USB2.0 interface can connect to the computer" [DOC][2][6]. On the full-size R307 this is a physical micro-USB/micro-B connector; on the compact R307S the same USB signals appear as **unpopulated solder pads** on the PCB (this matches the four pads visible on this unit; the owner has photographed them but silkscreen labels have not been confirmed).
- When connected to a PC, the module enumerates as a **virtual COM port** — no external USB-UART chip is needed; the AS606 controller implements USB itself [DOC][3][4].
- The vendor's own Windows demo tools (SYNO Demo / SFG Demo) open that virtual COM port and talk the same packet protocol as the UART [DOC][3].

**Inference [INF]:** the four pads almost certainly are **VBUS (5 V), D−, D+, GND** in some order — the minimal USB device set. The exact order on this unit is **UNVERIFIED**; connecting them wrongly can damage the module and/or the PC's USB port.

## 2. Why this matters for the current failure

The UART diagnostic shows the sensor TX line **driven high but completely silent** at every documented baud. A PC-over-USB test is the single strongest **independent** discriminator available without a multimeter, because it bypasses the ESP32, the harness, and all wiring hypotheses:

| PC-over-USB result | Meaning |
| :-- | :-- |
| Virtual COM port appears | USB PHY + controller + flash boot are alive → module is **powered and substantially functional**; the UART-side silence is then most likely an address/wiring/UART-specific issue, not a dead module. |
| No COM port, module draws current, no LED | Module power path or controller is dead → consistent with a DOA/overvolted unit. |
| No COM port, LED lights | USB pads misidentified, or USB-specific failure with a working module. |

## 3. SAFE procedure — NO soldering (preferred)

**Do not connect unknown pads to USB power** (explicit user rule). The only no-solder options:

1. **Inspect, don't connect.** Photograph the pads and any nearby silkscreen at maximum zoom. Family boards typically print `5V / D- / D+ / GND` or `VBUS / DM / DP / GND` beside the pads. Do this first — it costs nothing and may make the pad order verifiable.
2. **Look for the 3.3V jumper position while you are there** (see `docs/r307s-hardware-research.md` §5). A factory-shorted jumper with 5 V VIN power would explain a dead module with no visual trace.
3. **If — and only if — the pads are clearly labeled** and a **micro-USB breakout board with pogo pins / contact springs** (a generic "pogo pin USB test jig", sold for phone repair, requires no soldering onto the module) can be held against the pads, that adapter can be used. Risk note: intermittent pogo contact during enumeration is common; a failed enumeration is then **inconclusive**, not proof of a dead module.
4. Any USB connection attempt must use a **powered hub** between the PC and the module so that a short or miswiring on the module side cannot back-power the PC's port.

## 4. Procedure WITH soldering (only if documentation-supported)

Soldering is documented-supported in the sense that the family USB interface is real and intended for PC connection [DOC][2][3][6]. The procedure, for a future session with equipment:

1. Confirm the four pads' identities from silkscreen or continuity (GND pad → module GND wire is a continuity check).
2. Solder a 4-wire pigtail to `VBUS, D−, D+, GND` per the identified order.
3. Connect the pigtail to a **USB breakout/lead** through a powered hub.
4. Plug into the PC; check Device Manager for a new COM port (`USB Serial Device` or vendor-named).
5. Open the port at 57600 8-N-1 and run the SYNO Demo / SFG tool, or `pio device monitor --port <COMx> --baud 57600` and press reset... note: the module may emit nothing until it receives a packet — use the SYNO Demo "Open Device" which sends a handshake automatically.

**Power note:** over USB, VBUS supplies the module's 5 V input — the same rail as ESP32 VIN. Do **not** have both USB-VBUS and ESP32 VIN connected at the same time unless the module GND and ESP32 GND are already common and you accept two supplies on one rail; the safe sequence is USB-only testing with the harness unplugged from VIN.

## 5. Verdict for the current bench

- USB pads are a **real, documented, independent test path** for this module family.
- Safe execution requires either **confirmed pad labels** or **soldering equipment**; neither is available in this session.
- Until then, the USB path stays **NOT EXECUTED** (see `docs/r307s-test-matrix.md` HW-10) and the module's aliveness remains unresolved by software alone.

## 6. Sources

1. R307 family datasheet (Mantech MD0652-240817B): https://www.mantech.co.za/datasheets/products/MD0652-240817B.pdf — "Upper computer interface: UART \ USB 1.1"; dual-interface statement.
2. R307S quick-start (Mantech MD0652-240817C): https://www.mantech.co.za/Datasheets/Products/md0652-240817c.pdf
3. Circuitstate R307 teardown — USB virtual COM port, SYNO/SFG demo tools: https://www.circuitstate.com/tutorials/interfacing-r307-optical-fingerprint-scanner-with-arduino-boards-for-biometric-authentication/
4. EngineersGarage R30X article — virtual COM over USB: https://www.engineersgarage.com/arduino-adafruit-r30x-r307-fingerprint-scanner/
5. Cirkit Designer R307S documentation (dual-interface listing): https://docs.cirkitdesigner.com/component/771b9270-e39f-44e7-90b0-6e22051fea15/r307s-fingerprint-scanner
6. AliExpress GROW R307S listing — "RS232 and USB2.0 at the same time. USB2.0 interface can connect to the computer": https://www.aliexpress.com/item/1005003767546644.html
