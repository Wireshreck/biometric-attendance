---
type: project
area: workshop
status: blocked
tags:
  - workshop
  - tasks
  - active-work
  - blockers
---

# 10 - Workshop

**HOME** [[00 - Vault Hub]] · **UP** [[00 - Vault Hub]] · **RELATED** [[05 - Testing Lab]] [[02 - Hardware Lab]] [[09 - Decision Room]] · **CANVAS** [[10 - Workshop/10 - Workshop.canvas]]

The bench where work actually happens. Task tracker, milestones, the current blocker, and the next three actions.

---

## The board

**[[10 - Workshop/TODO|TODO]]** — 24 tasks, IDs `FND-01`…`AI-01`, with a dependency and a verification method per row. The single authoritative task list. Status reflects *evidence*, not intention.

**[[10 - Workshop/Milestones|Milestones]]** — gate-by-gate status with the commit or test that would close each one.

**[[10 - Workshop/AI Project Handoff|AI Project Handoff]]** — the state a new agent or a new day starts from.

---

## DONE — closed by evidence

| | Evidence |
|---|---|
| SQLite schema v1, transactional migrations, constraints | 6 temporary-DB tests pass |
| Backend vertical slice: health, students, enrollment, attendance ingest | 10/10 pytest green |
| Firmware test infrastructure: 27 environments | all compile and link |
| Production runtime: state machine, enrollment, journal, network client | **BUILD PASS** — `production` compiles/links, RAM 13.3%, Flash 66.0%. **0 physical results** |
| R307S read-only diagnostic suite | runs, bounded, sends no destructive command |
| Beginner assembly / software / science-fair documentation | written, honestly hedged |

---

## IN PROGRESS

- `FW-02` … `FW-04` — production driver, queue, API client: **implemented, never run on a device**
- `BUILD-01` — reproducible assembly guide: written; bench evidence still missing
- `HW-01` — read-only R307S diagnostic + UART loopback isolation: environment exists, never flashed

---

## BLOCKED — the real gate

> ### 🔴 R307S fingerprint sensor — UNVERIFIED
> **Assembled** per owner report: red→`VIN`, black→`GND`, yellow→`GPIO32` (sensor TX), green→`GPIO33` (sensor RX); blue/white open and insulated.
> **Result:** 0 bytes at all 12 documented baud rates, normal *and* software-swapped routing. 0 unsolicited transitions in 1.5 s.
> **Line state:** GPIO32 reads as actively **driven high** under both internal pull-down and pull-up — consistent with a live TXD, but *not* a calibrated voltage and *not* proof of supply.
> **Blocked on:** a multimeter. `ReadSysPara` and `TemplateCount` were gated on receiving any valid ACK, so they were **never executed**.
>
> The 3.3 V solder jumper is the leading unmeasured suspect: 5 V into a shorted jumper kills the module silently. Software cannot see it.

```text
BLOCKED ──▶ HW-00  measure rail, TX level, ground continuity, jumper state
          ──▶ HW-01  uart1/uart2 loopback with sensor detached
          ──▶ HW-10  USB pad path, only once pad order is positively identified
          ──▶ HW-05/06  ReadSysPara / TemplateCount, once any ACK is received
          ──▶ resolve sensor capacity ──▶ then, and only then, provision the backend device
```

Also blocked: `HW-03` (rails/reset under load) on the same missing instrument.

---

## UNVERIFIED — everything else on the bench

DS3231 · buzzer · LittleFS reboot behaviour · Wi-Fi reconnect · HTTP sync · queue replay · full attendance flow. (OLED/green LED/red LED removed from this project.)

Not one of these has a physical result. Not one is suspected broken. They are simply unknown.

---

## NEXT — in this order

1. **Identify the module.** Photograph the markings, read the connector orientation and the solder-jumper state. Do not infer the pinout from wire colour.
2. **Measure** ground continuity, `VIN` rail at the sensor, and TX idle high level. Record the numbers *before* changing any connection. Stop if voltage safety is unclear.
3. **Isolate the UART.** With the sensor detached, run `uart1_loopback` / `uart2_loopback` on a GPIO25 TX → GPIO26 RX jumper. This separates "the ESP32 UART is broken" from "the sensor is silent" — a question no software-only test has answered.
4. **Prove the cheap parts.** `i2c_scan`, `oled`, `rtc`, `green_led`, `red_led`, `buzzer` — none depend on the sensor, and all are currently `NOT EXECUTED`.
5. **Then** run `storage`, `wifi_diag`, `backend_http` on an isolated synthetic network.
6. **Then** exercise `production` end to end with synthetic records: enrollment, live POST, outage, reboot, replay — and confirm the replayed UUID appears exactly once in the local database.

Full detail: [[docs/next-steps.md]] · [[docs/r307s-next-session.md]] · [[docs/r307s-troubleshooting.md]]

---

## Stop writing code

The implementation is complete enough to be tested and not complete enough to be *trusted*. The gap is evidence, not functionality. More feature code now raises the cost of every future physical session and proves nothing.

---

## Documents

**[[10 - Workshop/TODO|TODO]]** · **[[10 - Workshop/Milestones|Milestones]]** · [[10 - Workshop/AI Project Handoff|AI Project Handoff]] · [[docs/next-steps.md]] · [[AI_CONTEXT.md]]

**HOME** [[00 - Vault Hub]] · **UP** [[00 - Vault Hub]] · **RELATED** [[05 - Testing Lab]] [[02 - Hardware Lab]] [[09 - Decision Room]] · **CANVAS** [[10 - Workshop/10 - Workshop.canvas]]
