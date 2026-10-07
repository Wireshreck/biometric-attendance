---
type: science-fair
area: science-fair
status: planned
tags:
  - science-fair
  - presentation
  - demo
  - timeline
---

# 07 - Science Fair

**HOME** [[00 - Vault Hub]] · **UP** [[00 - Vault Hub]] · **RELATED** [[01 - Project HQ]] [[02 - Hardware Lab]] [[05 - Testing Lab]] · **CANVAS** [[07 - Science Fair/07 - Science Fair.canvas]]

The public face of the project. **Target: 9 October 2026.** Everything here is a draft that is explicitly gated on evidence.

> [!IMPORTANT] The single rule of this room
> Demonstrate only what has been physically demonstrated. Every presentation file already says so. Do not soften it to sound more impressive — a demonstrator that admits its limits is a better exhibit than one caught overstating them.

---

## The talk

**3 minutes of explanation, up to 2 minutes of live demo.**

| Segment | Time | Content |
|---|---|---|
| Problem | 30 s | The engineering question. No claims about school time saved or vendor pricing |
| Design | 40 s | Edge matching, metadata-only events, local API/SQLite, offline journal |
| Privacy | 30 s | On-sensor matching is a *design boundary*, not a verified guarantee of irreversibility |
| Build & experiment | 40 s | State exactly which component gates passed — no more |
| Results | 30 s | Measured numbers **with** setup and sample size, or say "not measured" |
| Limits & next | 20 s | Sensor liveness, transport security, queue recovery, retention |
| Demo | ≤ 2 min | Only if every gate passed; otherwise the static fallback |

Canonical: [[presentation/outline.md]]

---

## The demo

Seven stages, each with a **labelled fallback** so a failure becomes a talking point instead of a dead end.

1. **Start** — power up, show health, show date/time
2. **Enroll** — synthetic student, two impressions over USB serial, API activates only after the sensor confirms
3. **Scan** — one consenting adult, generic terminal prompt, event located by UUID
4. **Duplicate** — scan again inside 60 s, show `DUPLICATE_SUPPRESSED`
5. **Report** — authorised daily aggregate / CSV
6. **Failure & recovery** — disconnect the network, scan, restore, confirm the same UUID reconciles exactly once
7. **Close** — state limitations, clear the temporary template

**Today, none of stages 1–6 can be run.** Stage 2 onward depends on the R307S, which is silent. That is not a reason to fake it — it is the reason the fallback exists.

Canonical: [[presentation/demo-script.md]]

---

## Judges

Ten anticipated questions, each already answered honestly. The three that decide the project:

**"Where is the biometric data stored?"**
> The design keeps capture, matching and template storage inside the sensor; only a slot number leaves it. The exact sensor capabilities and template properties are not independently verified. We do not claim templates are mathematically irreversible.

**"What results have you measured?"**
> Only dated results with setup, sample count and method from the test log. Recognition accuracy, FAR/FRR, latency and reliability are currently **not measured**.

**"Is this secure / ready for schools?"**
> No. It is an early-stage science-fair prototype. HTTP bearer traffic is not encrypted end-to-end, sensor spoof resistance is unknown, retention and compliance are unresolved.

Canonical: [[presentation/judge-questions.md]]

---

## The experiments we said we would run

Defined in advance so results cannot be reverse-engineered after the fact.

| Experiment | Measurement | Must define first |
|---|---|---|
| Enrollment success | successes / attempts | consenting adults; module firmware; failure modes |
| Recognition reliability | genuine accept, genuine reject, impostor accept/reject | consent and safety protocol |
| Response latency | finger→feedback; API commit→UI | timestamp method, ≥30 trials, p50/p95 |
| Duplicate boundary | outcomes at 59 / 60 / 61 s; UUID replay | fixed synthetic identities |
| Offline resilience | queued UUIDs vs stored UUIDs after outage | separate Wi-Fi and API loss tests |
| Power interruption | DB integrity and queue recovery | controlled removal only |
| Backup recovery | restore duration, integrity, row counts | separate restore destination |

**Every one of these is currently "not measured."**

Canonical: [[docs/science-fair.md]] · [[docs/science-fair-timeline.md]]

---

## Transport and venue

Pack: ESP32, USB data cable, R307S with blue/white insulated, DS3231, buzzer, breadboard, jumpers, laptop, spare **known-good** cable, printed pin map + assembly guide + test plan, and a **multimeter if one can be found**. (OLED/LEDs removed from this project.) Synthetic roster only.

Venue startup: nonconductive table, inspect with USB disconnected, verify ground and I2C pull-ups, leave an uncertain CR2032 out, connect USB only, then run `esp32_core` → `i2c_scan` → RTC → buzzer → loopback **with the sensor disconnected** → and the R307S probe only if its electrical safety gate is satisfied. OLED/LEDs were removed from this project.

Canonical: [[docs/SCIENCE-FAIR-SETUP.md]]

---

## Timeline

| Target | Gate |
|---|---|
| Sep 25 | Hardware order confirmation |
| Sep 28 | Bench bring-up |
| Oct 01 | Standalone biometric prototype |
| Oct 04 | First working end-to-end demo |
| Oct 06 | Testing and code freeze |
| Oct 08 | Backup and rehearsal |
| **Oct 09** | **Science fair** |

Dates are targets, not evidence. Canonical: [[docs/science-fair-timeline.md]]

---

## Documents

[[docs/science-fair.md]] · [[docs/science-fair-timeline.md]] · [[docs/SCIENCE-FAIR-SETUP.md]] · [[presentation/outline.md]] · [[presentation/demo-script.md]] · [[presentation/judge-questions.md]] · [[docs/backup-strategy.md]]

**HOME** [[00 - Vault Hub]] · **UP** [[00 - Vault Hub]] · **RELATED** [[01 - Project HQ]] [[02 - Hardware Lab]] [[05 - Testing Lab]] · **CANVAS** [[07 - Science Fair/07 - Science Fair.canvas]]
