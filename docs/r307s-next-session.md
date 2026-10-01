# R307S Debugging Handoff — Next Session

**Document:** `docs/r307s-next-session.md`
**Date:** 2026-10-01
**Written so that someone who has never seen the previous conversation can continue the debugging immediately.**

---

## Current hardware

- **MCU:** ESP32-WROOM-32 DevKit V1, working, on USB now. **Serial port is COM4** (CH340, VID:PID 1A86:7523). ⚠️ It was COM3 in earlier sessions; the port renumbered on replug. Always re-check with `pio device list`.
- **Sensor:** GROW R307S optical fingerprint module, 6-wire harness.
- **Wiring (installed and user-verified; do not re-litigate):**
  - Pin 1 RED → ESP32 VIN (5 V rail)
  - Pin 2 BLACK → ESP32 GND
  - Pin 3 YELLOW (sensor TXD) → ESP32 GPIO32 (UART2 RX)
  - Pin 4 GREEN (sensor RXD) → ESP32 GPIO33 (UART2 TX)
  - Pin 5 BLUE (TOUCH) and pin 6 WHITE (touch power) → disconnected (documented: irrelevant to UART, ~5 µA circuit)
- **Board features to physically inspect when possible:** the **3.3V solder jumper** (open = LDO/5 V input; shorted = 3.3 V direct — a factory-shorted jumper under 5 V would explain a dead module) and the **four USB pads** (see `docs/r307s-usb-test.md`).
- **No multimeter available.**

## Current firmware

- `firmware/src/main.cpp` — toolchain-check sketch (banner, chip/heap prints) + one call to `r307s_uart_diag_run()` after a 2 s settle. Idle `loop()`.
- `firmware/src/r307s_uart_diag.{h,cpp}` — the read-only diagnostic suite (line probe → activity monitor → 12-baud scan → swapped-routing probes → command suite → classification). Strictly read-only: VerifyPassword (0x13), ReadSysPara (0x0F), TemplateCount (0x1D) only. No enrollment/matching/writes anywhere.
- Pins/baud come from `firmware/include/config.h` (`PIN_R307S_RX 32`, `PIN_R307S_TX 33`, `R307S_BAUD_RATE 57600`).
- Builds clean (`pio run`), uploads clean, runs. `firmware/test/` is empty — no firmware unit tests exist.

## What has been PROVEN

1. ESP32 hardware, toolchain, upload path, and USB serial all work (COM4 @ 115200).
2. The diagnostic firmware executes correctly end-to-end and terminates (never hangs).
3. The sensor-side wire on GPIO32 is **actively driven HIGH** (~2822 mV ADC estimate; HIGH 200/200 with internal pull-down *and* pull-up). A floating wire cannot do that.
4. The silence is **not** a baud mismatch: 0 bytes at **all 12 documented rates** (9600×N, N=1..12).
5. The silence is **not** crossed TX/RX: software-swapped UART routing (GPIO matrix, no wire movement) also yields 0 bytes.
6. No unsolicited data ever appears on the line (0 transitions in 1.5 s monitor).
7. Pins 5/6 being disconnected cannot cause this (datasheet: touch circuit only).

## What has NOT been proven

1. **That the sensor is actually powered** (no voltage/current measurement possible without a meter).
2. **That the ESP32→sensor wire (GPIO33→pin 4) is intact** — a driven-high TXD says nothing about the opposite direction. A broken RXD path produces exactly the observed signature.
3. **That the module's device address is 0xFFFFFFFF** — a changed address makes the module silently ignore every packet.
4. **The module's fundamental aliveness** (controller booting, flash OK).
5. The exact TXD logic voltage (ADC estimate ≈ 2.8 V is consistent with 3.3 V-class logic but is NOT a measurement).
6. The state of the 3.3V solder jumper on this physical unit.

## Tests already performed (2026-10-01)

| # | Test | Result |
| :-- | :-- | :-- |
| 1 | TX-line idle-state probe (software) | DRIVEN HIGH (~2822 mV est., HIGH with both pull modes) |
| 2 | RX activity monitor (1.5 s) | 0 transitions |
| 3 | VerifyPassword @ 57600, normal routing | 0 bytes |
| 4 | VerifyPassword @ 9600, 19200, 28800, 38400, 48000, 67200, 76800, 86400, 96000, 105600, 115200 | 0 bytes each |
| 5 | VerifyPassword @ 57600 and 9600, swapped routing | 0 bytes each |
| 6 | Command suite (ReadSysPara / TemplateCount) | NOT EXECUTED — gated on any valid ACK |

**Verbatim classification printed by the firmware:** `RESULT: COMPLETELY SILENT - 0 bytes at every baud, both routings.` — with the driven-high line-state context above it.

Full raw log: captured to Windows temp as `r307s_capture.txt` during the session; regenerate any time with the commands below.

## Most useful next test

**In order of value:**

1. **Multimeter checks (5 minutes, resolves the most):**
   - Voltage pin 1↔pin 2 while powered (expect ~5 V). If ~0 V → power path/wire fault, done.
   - Voltage on sensor TXD (pin 3)↔GND (expect ~3.3 V idle). Confirms/refutes the ADC estimate.
   - Continuity: each harness wire end-to-end, especially **GPIO33→pin 4** (the unproven direction).
   - Visual: is the **3.3V jumper** open?
2. **USB pads aliveness test** (no ESP32 involved): see `docs/r307s-usb-test.md`. Requires confirmed pad labels (photo/zoom first) or a soldering session. A virtual COM port appearing on the PC = module alive.
3. **Standalone USB-UART bridge** (CP2102/CH340) straight onto sensor TXD/RXD from the PC — bypasses the ESP32 and both harness directions at once.

## Equipment needed

- Any multimeter (unblocks tests 1a–1d) — highest priority.
- Optional: micro-USB breakout or pogo-pin jig + powered hub (USB test).
- Optional: standalone USB-UART adapter.

## Exact commands

```bash
# 0) Which port is the ESP32 on today? (COM3 historically, COM4 on 2026-10-01)
pio device list

# 1) Build
pio run -d firmware

# 2) Upload (substitute today's port)
pio run -d firmware -t upload --upload-port COM4

# 3) Monitor interactively, then press the ESP32 EN/RST button to rerun the suite
pio device monitor --port COM4 --baud 115200

# 3b) Non-interactive capture with automatic reset (pyserial, system Python has it):
python - <<'PY'
import serial, time, sys
ser = serial.Serial(); ser.port='COM4'; ser.baudrate=115200; ser.timeout=0.05
ser.open(); ser.dtr=False; ser.rts=False; time.sleep(0.2)
ser.rts=True; time.sleep(0.15); ser.rts=False   # clean reset via EN
t0=time.time()
while time.time()-t0 < 24:
    d = ser.read(4096)
    if d: sys.stdout.write(d.decode('utf-8','replace')); sys.stdout.flush()
ser.close()
PY
# (the suite takes ~13 s after boot; 24 s of capture covers it)
```

## Files involved

- `firmware/src/main.cpp` — modified (includes config.h + diag call; stale 16/17 defines removed)
- `firmware/src/r307s_uart_diag.h` / `.cpp` — the diagnostic suite (deletable once sensor works)
- `firmware/include/config.h` — pin/baud source of truth (unchanged this session)
- `firmware/include/fingerprint_sensor.h` — HAL prototypes, unimplemented (unchanged)
- `docs/r307s-hardware-research.md` — datasheet facts + evidence + sources
- `docs/r307s-test-matrix.md` — HW-01..HW-13 status
- `docs/r307s-troubleshooting.md` — decision tree
- `docs/r307s-usb-test.md` — USB pads procedure
- `docs/r307s-integration-plan.md` — 10-phase plan (Phases 1–5 now effectively exercised)
- `docs/wiring.md`, `hardware/pinout.md`, `hardware/test-plan.md` — still contain older "NOT YET CONNECTED" language (superseded by this session's reality; queued for the next doc-sync commit)

## Important warnings

- **ESP32 GPIOs are not 5 V tolerant.** Do not connect anything to GPIO32/33 before knowing its voltage. The driven-high ADC estimate (~2.8 V) is consistent with safe 3.3 V logic, but it is not a measurement.
- **Do not short or "test" the 3.3V jumper while 5 V is applied.** If the jumper is shorted, pin 1 must be 3.3 V, not 5 V.
- **Do not blind-swap wires.** The swapped-routing hypothesis is already tested in software; physical swapping only adds variables.
- **Do not connect unknown USB pads to the PC** before identifying them (`docs/r307s-usb-test.md` §3–4).
- **The diagnostic is strictly read-only** — keep it that way: no SetSysPara/SetAddr/baud/password writes, no enrollment, until the module responds and Phase 6 gates open.
- **Do not treat a future ACK at a weird configuration as "fine"** — a module that answers only after config surgery may have been reprogrammed; record its address/baud/password immediately.
- **Session hygiene:** do not commit/push until the owner says so; keep changes limited to the diagnostic files + the five `docs/r307s-*.md` documents.

## Bottom line for the next session

Software has exhausted what software can prove: **the UART link is dead at every documented baud in both routing directions, while the sensor TXD wire is driven high.** The remaining causes are physical (power, the RXD-direction wire, jumper state, changed address, dead module) and require a multimeter or the USB-pads path to discriminate. The single most valuable purchase is a cheap multimeter; the single most valuable zero-cost action is photographing the module's pads/silkscreen and jumper state.
