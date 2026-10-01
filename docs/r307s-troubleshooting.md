# R307S Troubleshooting Decision Tree

**Document:** `docs/r307s-troubleshooting.md`
**Date:** 2026-10-01
**Scope:** R307S optical fingerprint module on this bench. Aligned with `docs/r307s-hardware-research.md` (datasheet facts) and the actual 2026-10-01 diagnostic results. The generic matrix in `docs/troubleshooting.md` remains valid for other subsystems.

---

## Decision tree

```
R307S completely dark / silent
        |
        +-- Is correct main power confirmed?
        |       |
        |       +-- NO  -> measure/verify power first (multimeter or USB test).
        |       |         Everything below is meaningless without this.
        |       |         [THIS BENCH: NOT CONFIRMED - no multimeter.
        |       |          Wiring topology is correct per datasheet;
        |       |          actual rail voltage is unknown.]
        |       |
        |       +-- YES (supply verified)
        |               |
        +-- RX-line idle-state probe (run diagnostic; software "voltmeter")
                |
                +-- FLOATING line (reads HIGH only with pull-up, ~random ADC)
                |       |
                |       +-- Nothing is driving the TXD wire:
                |             unpowered module / broken wire / wire is not
                |             TXD / dead module. -> Check harness seating,
                |             then USB test (HW-10) to isolate module vs wires.
                |
                +-- DRIVEN HIGH line  [THIS BENCH: THIS BRANCH]
                        |
                        +-- UART returns 0 bytes at ALL documented bauds
                        |   (9600 x N, N = 1..12)?
                        |       |
                        |       +-- YES  [THIS BENCH: YES]
                        |       |       |
                        |       +-- (software) swapped routing probe
                        |       |       |
                        |       |       +-- still 0 bytes [THIS BENCH: YES]
                        |       |       |
                        |       |       +-- Remaining hypotheses, in cost order:
                        |       |             1. Command never reaches pin 4:
                        |       |                the GREEN->GPIO33 path is broken
                        |       |                or pin 4 is not RXD.
                        |       |                (TXD driven-high says nothing
                        |       |                about the sensor->RXD wire.)
                        |       |             2. Module address != 0xFFFFFFFF:
                        |       |                silently ignores every packet.
                        |       |                Unverifiable without responding
                        |       |                module or datasheet/backdoor.
                        |       |             3. Controller hung (brownout at
                        |       |                power-on) - module alive enough
                        |       |                to drive TXD but firmware dead.
                        |       |             4. Wire on GPIO32 is not the sensor
                        |       |                TXD at all (harness confusion).
                        |       |             5. Module dead with coincidentally
                        |       |                pinned-high output (least likely).
                        |       |             -> Best next test: USB pads (HW-10)
                        |       |                to prove aliveness independently
                        |       |                of UART and harness.
                        |       |
                        |       +-- NO (some bytes arrive)
                        |               |
                        |               +-- parse packet
                        |                       |
                        |                       +-- valid ACK (checksum OK)
                        |                       |       |
                        |                       |       +-- conf 0x00 ->
                        |                       |       |     COMMUNICATION CONFIRMED.
                        |                       |       |     Proceed to ReadSysPara (HW-05).
                        |                       |       |
                        |                       |       +-- conf != 0x00 ->
                        |                       |             command rejected (e.g. 0x13
                        |                       |             wrong password / 0x21 password
                        |                       |             not verified). Command layer OK.
                        |                       |
                        |                       +-- malformed ->
                        |                             baud at ladder edge, changed
                        |                             address, 5 V logic corrupting
                        |                             RX, damaged module.
                        |
                        +-- bytes at an unexpected baud? All N=1..12 were
                            already scanned - an off-ladder baud (module
                            reprogrammed by vendor tool) is possible but
                            outside the documented set.
```

## What the 2026-10-01 results mean (bench-specific)

- **The failure is NOT baud** (12 documented rates scanned, all silent) and **NOT crossed wires** (software-swapped routing also silent).
- **The GPIO32 wire is driven high** — evidence that *something powered* holds that line. Most plausibly the sensor's TXD at UART idle.
- **A driven-high TXD does not prove the module is correctly powered**, and says **nothing** about the opposite wire (ESP32 TX → sensor RXD). The single most probable remaining fault class is **the RXD path / command delivery**, followed by **changed device address** and **hung/dead controller**.
- **Whether the module is truly powered cannot be determined without measuring voltage or current, or a USB test.** This is the honest boundary of software diagnostics on this bench.

## Equipment that unlocks the next tier

| Tool | Unlocks |
| :-- | :-- |
| Multimeter (any cheap DMM) | Rail voltages (pin 1, TXD, RXD), jumper state check, continuity of each wire — resolves HW-01/HW-13 conclusively |
| USB micro-breakout + powered hub (or pogo jig) | Independent aliveness test via module's USB pads (`docs/r307s-usb-test.md`) |
| USB-UART bridge (CP2102/CH340 standalone) | Talk to the sensor UART directly from the PC, bypassing ESP32 entirely |
| Second known-good R307/R307S | Discriminates DOA vs environment |

## Related documents

- `docs/r307s-hardware-research.md` — facts, evidence, sources
- `docs/r307s-test-matrix.md` — test-by-test status
- `docs/r307s-usb-test.md` — the USB pads path
- `docs/r307s-next-session.md` — handoff with exact commands
- `docs/troubleshooting.md` — generic project troubleshooting matrix
