---
type: test
area: testing
status: active
tags:
  - r307s
  - testing
  - evidence
---
# R307S Hardware Test Matrix

**Document:** `docs/r307s-test-matrix.md`
**Date:** 2026-10-01
**Bench state:** wiring per `docs/r307s-hardware-research.md` §1; ESP32 on USB (**COM4** — renumbered from COM3); diagnostic suite `firmware/src/r307s_uart_diag.cpp` uploaded and executed 2026-10-01.
**Result symbols:** PASS / FAIL / NOT EXECUTED / INCONCLUSIVE. No result is fabricated; every "actual" row cites the captured diagnostic log (archived in session handoff `docs/r307s-next-session.md`).

| Test ID | Test | Purpose | Expected result | Actual result | Interpretation | Confidence |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| HW-01 | Power configuration (pin 1 = VIN 5 V, pin 2 = GND) | Confirm supply wiring matches datasheet requirement | 4.2–6.0 V on pin 1; common ground | WIRED as specified [user-confirmed]. **Voltage not measured — no multimeter.** | Wiring topology correct per datasheet; actual rail voltage UNPROVEN | Medium (topology) / None (voltage) |
| HW-02 | UART at default baud 57600 | Baseline handshake (VerifyPassword 0x13, normal routing) | ACK `EF 01 FF FF FF FF 07 00 03 00 00 0A` | **TX 16 B → RX 0 bytes** [LAB log] | No response at default baud | High (executed) |
| HW-03 | UART baud ladder scan | Rule out non-default baud: all 12 documented rates (9600×N, N=1..12) | ACK at exactly one baud | **0 bytes at all 12 bauds** [LAB log] | Baud mismatch EXCLUDED as the cause (per documented ladder) | High |
| HW-04 | VerifyPassword command | Read-only handshake with provisional password 0x00000000 | conf 0x00 | **0 bytes received** [LAB log] | Command sent correctly (checksum computed); no answer — cannot test password itself | High |
| HW-05 | ReadSysPara (0x0F) | Read capacity/security/baud/address block | ACK + 16-byte data packet | **NOT EXECUTED** — gated on HW-02/03/04 producing any valid ACK | Blocked by total silence | — |
| HW-06 | TemplateCount (0x1D) | Read stored-template count | ACK + 2-byte count | **NOT EXECUTED** — same gate as HW-05 | Blocked by total silence | — |
| HW-07 | UART checksum validation | Prove parser validates and can reject corrupted frames | Checksums computed TX-side; RX validated before acceptance | TX checksum `0x001B` verified against documented packet [code review + LAB]; no RX data existed to validate | Parser correct; unexercised on RX | High (TX) / n.a. (RX) |
| HW-08 | Startup timing / unsolicited data | Detect boot chatter or LED-era activity on RX | Possibly unsolicited bytes after power-on | **0 transitions in 1500 ms monitor** [LAB log] | No unsolicited UART activity | High |
| HW-09 | Touch circuit relevance | Confirm pins 5/6 disconnection cannot silence the module | Module UART independent of touch power | Datasheet: touch circuit = ~5 µA, pin 5 output only, UART unaffected [DOC][1] | Pins 5/6 disconnection is NOT a plausible cause of the failure | High (documented) |
| HW-10 | USB interface research | Independent aliveness test via module's USB pads | Virtual COM on PC if module alive | **NOT EXECUTED** — pad order unverified; no soldering/pogo equipment; see `docs/r307s-usb-test.md` | Highest-value remaining test | — |
| HW-11 | Alternate UART routing (software swap) | Rule out crossed TX/RX without touching wires | ACK if wires were reversed | **0 bytes with swapped routing at 57600 and 9600** [LAB log] | Crossed-wire hypothesis EXCLUDED (software-side); also means the sensor does not answer on either wire | High |
| HW-12 | Independent power requirement | Determine whether VIN-from-USB is adequate | 50 mA typ / 80 mA peak within VIN capability | Datasheet figures [DOC]; no current measurement possible | Adequate on paper; brownout/sag cannot be excluded without measurement | Medium |
| HW-13 | RX-line idle-state probe (added) | Software "voltmeter": distinguish floating vs driven-high wire | Floating → unpowered/dead path; driven-high → live TXD | **~2822 mV ADC estimate; HIGH 200/200 with pull-down AND pull-up → DRIVEN HIGH** [LAB log] | The GPIO32 wire is actively driven (most plausibly a powered sensor TXD); NOT proof of correct supply voltage | High (line driven) / None (supply voltage) |

## Test-chain logic

```
HW-02 fail ─→ HW-03 (baud) fail ─→ HW-11 (routing) fail ─→ HW-13 (line state)
                                                        └─→ HW-10 (USB, next session)
HW-05/06 gated on any valid ACK anywhere in the chain
```

## Sources

1. R307 family datasheet (Mantech MD0652-240817B): https://www.mantech.co.za/datasheets/products/MD0652-240817B.pdf
2. Full evidence chain and citations: `docs/r307s-hardware-research.md` §8–9.
