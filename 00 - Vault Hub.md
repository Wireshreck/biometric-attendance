---
type: project
area: hub
status: active
tags:
  - project
  - hub
  - navigation
---

# 00 - Vault Hub

> **You are standing at the entrance of the BIOMETRIC ATTENDANCE LAB.**
> Ten rooms. One map. Every room has a hub note, a canvas, and a way back to this door.

---

## Identity

| | |
|---|---|
| **Project** | Biometric School Attendance System — local-first biometric attendance demonstrator |
| **Stack** | ESP32-WROOM-32 · R307S fingerprint module · FastAPI · SQLite |
| **Shape** | Open-source science-fair demonstrator, MIT licensed, designed to be built by a school |
| **Exhibition** | 9 October 2026 |
| **Repo** | `github.com/Wireshreck/biometric-attendance` · branch `main` |

The engineering question: *can a low-cost ESP32 terminal record attendance with biometric matching kept at the edge, send only event metadata to a local service, and survive a network outage — without ever shipping a fingerprint image or template off the sensor?*

---

## ⚠️ Read this before trusting any status

Three rules govern every claim in this vault.

1. **The R307S is UNVERIFIED.** The owner reports it assembled and silent: zero valid UART bytes at all 12 documented baud rates and both software routing options. That is **not** proof the module is dead. Its supply rail, TX logic level, exact PCB pin mapping and jumper state are **UNVERIFIED — REQUIRES MULTIMETER**.
2. **A successful build is not a working device.** Firmware compiles and links. GPIO code cannot sense an LED, a buzzer, or a fingerprint sensor. Only a person who watched the thing happen may write PASS.
3. **No number here was invented.** No measurement, capacity, accuracy, latency or reliability figure appears in this vault unless it is quoted from a dated evidence document.

Evidence vocabulary used throughout: `VERIFIED` · `UNVERIFIED` · `NOT EXECUTED` · `BLOCKED` · `BUILD PASS`.

---

## Current status by area

| Area | Status | Evidence | Room |
|---|---|---|---|
| **Vault** | **ACTIVE** | 10 area hubs, 12 canvases, 12-colour legend, link-audited | *you are here* |
| **Project HQ** | ACTIVE | Scope, architecture, requirements, traceability | [[01 - Project HQ/Project HQ|01 - Project HQ]] |
| **Hardware Lab** | **UNVERIFIED** | DS3231 on GPIO25/26; every rail unmeasured; R307S silent | [[02 - Hardware Lab/Hardware Lab|02 - Hardware Lab]] |
| **Firmware Lab** | BUILD PASS | `production` builds — RAM 13.3%, Flash 66.0%; no physical pass | [[03 - Firmware Lab/Firmware Lab|03 - Firmware Lab]] |
| **Backend Server Room** | **VERIFIED (software)** | 10/10 pytest green against synthetic fixtures | [[04 - Backend Server Room/Backend Server Room|04 - Backend Server Room]] |
| **Testing Lab** | **NOT EXECUTED** | 27 environments build; 0 physical results recorded | [[05 - Testing Lab/Testing Lab|05 - Testing Lab]] |
| **Research Archive** | ACTIVE | R307S protocol, power, jumper, USB research with sources | [[06 - Research Archive/Research Archive|06 - Research Archive]] |
| **Science Fair** | PLANNED | Script, outline, judge Q&A, transport — every claim gated | [[07 - Science Fair/Science Fair|07 - Science Fair]] |
| **Documentation Library** | ACTIVE | 47 canonical docs, one subject → one authority | [[08 - Documentation Library/Documentation Library|08 - Documentation Library]] |
| **Decision Room** | ACTIVE | ADR-001…ADR-014 preserved verbatim, nothing rewritten | [[09 - Decision Room/Decision Room|09 - Decision Room]] |
| **Workshop** | **BLOCKED** | 24 tracked tasks; P0 hardware evidence is the gate | [[10 - Workshop/Workshop|10 - Workshop]] |

---

## The facility map

Open the whole building at once:

**[[00 - Master Canvas.canvas|00 - Master Canvas]]**

---

## Rooms

* 🏢 [[01 - Project HQ/Project HQ|01 - Project HQ]] — what this is, what it must do, what it must never do
* 🔌 [[02 - Hardware Lab/Hardware Lab|02 - Hardware Lab]] — the parts, the pin map, the breadboard, the safety gates
* ⚙️ [[03 - Firmware Lab/Firmware Lab|03 - Firmware Lab]] — the terminal runtime, state machine, journal, network client
* 🖥️ [[04 - Backend Server Room/Backend Server Room|04 - Backend Server Room]] — FastAPI, SQLite, auth, the API contract
* 🧪 [[05 - Testing Lab/Testing Lab|05 - Testing Lab]] — every environment, and exactly what each one proves
* 🔬 [[06 - Research Archive/Research Archive|06 - Research Archive]] — what we know, what we inferred, and from which source
* 🎪 [[07 - Science Fair/Science Fair|07 - Science Fair]] — the booth, the demo, the judges, the honest fallbacks
* 📚 [[08 - Documentation Library/Documentation Library|08 - Documentation Library]] — the shelf: which file is authoritative for what
* ⚖️ [[09 - Decision Room/Decision Room|09 - Decision Room]] — ADR-001…ADR-014, reasons, alternatives, consequences
* 🔧 [[10 - Workshop/Workshop|10 - Workshop]] — the bench: what is done, what is blocked, what is next

---

## The one-blocker summary

> **R307S fingerprint sensor — UNVERIFIED.**
> Connected per owner report (red→VIN, black→GND, yellow→GPIO32 RX, green→GPIO33 TX; blue/white open).
> Diagnostic result: 0 bytes at every documented baud, both routings. RX line reads as *driven high*, which suggests a live TXD but proves nothing about supply voltage.
> Cannot be resolved in software. Needs a multimeter and the exact board in hand.
>
> Start at [[docs/r307s-troubleshooting.md|R307S troubleshooting decision tree]] · [[10 - Workshop/TODO]] HW-00.

---

## Next actions

1. **Measure.** R307S VIN, TX idle high level, ground continuity. No multimeter available today — [[10 - Workshop/TODO]] HW-00 is `BLOCKED` on that alone.
2. **Isolate the UART.** Run `uart1_loopback` / `uart2_loopback` with a GPIO25→GPIO26 jumper and the sensor disconnected, to prove the ESP32 UART peripheral before blaming the sensor.
3. **Prove the cheap parts first.** `i2c_scan`, `oled`, `rtc`, `green_led`, `red_led`, `buzzer` — none of these depend on the sensor, and every one of them is currently `NOT EXECUTED`.
4. **Do not write more feature code.** The implementation is complete enough; the missing thing is evidence. See [[docs/next-steps.md]].

---

## Start here if you are…

| You are… | Go to |
|---|---|
| New to the project | [[01 - Project HQ/Project HQ|01 - Project HQ]] then [[00 - Master Canvas.canvas]] |
| Holding a multimeter | [[02 - Hardware Lab/Hardware Lab|02 - Hardware Lab]] → [[02 - Hardware Lab/02 - Hardware Assembly.canvas|02 - Hardware Assembly.canvas]] |
| About to flash firmware | [[05 - Testing Lab/Testing Lab|05 - Testing Lab]] → [[docs/power-and-safety.md]] |
| An AI agent picking this up | [[AI_CONTEXT.md]] · [[10 - Workshop/AI Project Handoff]] |
| Presenting at a fair | [[07 - Science Fair/Science Fair|07 - Science Fair]] |
| Looking for the source of truth on a topic | [[08 - Documentation Library/Documentation Library|08 - Documentation Library]] |
| Asking "why is it built this way?" | [[09 - Decision Room/Decision Log]] |

---

## House conventions

- **One subject, one canonical document.** Vault notes link; they never restate a spec. If two documents disagree, the one named in [[08 - Documentation Library/Documentation Library|08 - Documentation Library]] wins and the other becomes a redirect stub.
- **Status means evidence, not intention.** `IMPLEMENTED` and `VERIFIED` are different words and the vault never uses them interchangeably.
- **Colour is a vocabulary**, defined once in [[08 - Documentation Library/Documentation Library|colour and status legend]] and used identically on every canvas and badge.
- **Every hub has four exits**: HOME · UP · RELATED · CANVAS. No note should ever be a dead end.

**HOME** [[00 - Vault Hub]] · **UP** *(this is the top)* · **RELATED** [[01 - Project HQ/Project HQ|01 - Project HQ]] [[10 - Workshop/Workshop|10 - Workshop]] · **CANVAS** [[00 - Master Canvas.canvas]]
