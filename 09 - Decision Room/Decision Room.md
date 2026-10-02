---
type: decision
area: decisions
status: active
tags:
  - decisions
  - adr
  - architecture
---

# 09 - Decision Room

**HOME** [[00 - Vault Hub]] · **UP** [[00 - Vault Hub]] · **RELATED** [[01 - Project HQ]] [[06 - Research Archive]] [[08 - Documentation Library]] · **CANVAS** [[09 - Decision Room/09 - Decision Room.canvas]]

Where the arguments are kept. Fourteen architecture decisions, why each was taken, what was rejected, and what would make us change our mind.

> **History is extended, never rewritten.** A superseded decision keeps its row and gains a successor. Deleting an ADR destroys the only record of why a plausible alternative was rejected.

---

## The record

**[[09 - Decision Room/Decision Log|Decision Log]]** is the authoritative decision log — ADR-001 through ADR-014, migrated unchanged from the previous vault.

Each row carries four things the format demands:

```text
DECISION  →  REASON (and the trade-off accepted)  →  ALTERNATIVES  →  RESULT & AFFECTED SYSTEMS
                                                            ↳ revisit trigger (evidence that would change it)
```

The **revisit trigger** is the part that makes an ADR useful rather than decorative. ADR-001 says "revisit after the exact board is identified." That is falsifiable. "We chose the best option" is not.

---

## Index

| ADR | Decision | Status | Affects |
|---|---|---|---|
| [001](Decision%20Log.md) | ESP32-WROOM-32-class terminal | **PROVISIONAL** | Hardware Lab, Firmware Lab |
| [002](Decision%20Log.md) | AS608 fingerprint module | **SUPERSEDED** → ADR-013 | Research Archive |
| [003](Decision%20Log.md) | Local-first, one-host prototype | **PLANNED** | Whole system |
| [004](Decision%20Log.md) | Match on sensor; host gets slot only | **PROVISIONAL** | Privacy boundary |
| [005](Decision%20Log.md) | FastAPI + SQLite, single local service | **DECIDED · IMPLEMENTED** | Backend Server Room |
| [006](Decision%20Log.md) | WAL, ordered migrations, FK, `synchronous=FULL` | **DECIDED · VERIFIED** | Backend Server Room |
| [007](Decision%20Log.md) | Vanilla HTML/CSS/ES modules, same origin | **PLANNED** | Frontend |
| [008](Decision%20Log.md) | 60-second same-student suppression | **DECIDED · VERIFIED** | API, database, demo |
| [009](Decision%20Log.md) | Stable UUID + bounded LittleFS replay queue | **IMPLEMENTED · NEEDS HARDWARE** | Firmware Lab, Testing Lab |
| [010](Decision%20Log.md) | Device bearer + admin Basic, synthetic demo only | **DECIDED · IMPLEMENTED** | Backend Server Room, Science Fair |
| [011](Decision%20Log.md) | Defer AI; if added, read-only aggregates only | **DEFERRED** | Documentation Library |
| [012](Decision%20Log.md) | Migrate to provisional R703 | **SUPERSEDED** → ADR-013 | Research Archive |
| [013](Decision%20Log.md) | Canonical sensor is **R307S** | **DECIDED** | Hardware Lab, Research Archive |
| [014](Decision%20Log.md) | Record bench wiring, preserve GPIO32/33 | **IN PROGRESS · electrical checks unverified** | Hardware Lab, Testing Lab |
| **015** | **Repository root becomes the Obsidian vault** | **DECIDED** | This vault |
| **016** | **`fingerprint_sensor.h` retired to a deprecation notice** | **DECIDED** | Firmware Lab |
| **017** | **26 environments build; zero physical results recorded** | **DECIDED** | Testing Lab, Workshop |

ADR-015 to ADR-017 were added during the vault restructure itself and are recorded in [[09 - Decision Room/Decision Log|Decision Log]].

---

## How decisions flow

```text
Research finding          Decision              Implementation          Test that would verify it
──────────────            ────────              ───────────────          ─────────────────────────
R307S family datasheet ──▶ ADR-013 R307S ──────▶ config.h 32/33 ───────▶ r307s env, HW-02/03/04
Capacity disagreement ───▶ defer provisioning ──▶ ReadSysPara gate ─────▶ HW-05 (NOT EXECUTED)
Latch-depth 60 s rule ───▶ ADR-008 ────────────▶ main.py transaction ──▶ test_api.py (PASS)
Offline requirement ─────▶ ADR-009 ────────────▶ attendance_store.cpp ─▶ INT-10 (never run)
Privacy boundary ────────▶ ADR-004 ────────────▶ schemas.py slot only ─▶ test_api.py (PASS)
```

Every row ends in something that can be *run*. A decision whose verification is a vibe is not a decision.

---

## Change procedure

1. Append a new ADR row with decision, reason, alternatives, result, evidence, and revisit trigger.
2. Mark the superseded row `SUPERSEDED by ADR-NNN` — do not delete it.
3. Update the affected canonical document in the same milestone.
4. Update the affected task in [[10 - Workshop/TODO]].
5. Update the relevant edge on [[09 - Decision Room/09 - Decision Room.canvas]].

---

## Documents

**[[09 - Decision Room/Decision Log|Decision Log]]** · [[docs/architecture.md]] · [[docs/privacy-security.md]] · [[docs/software-stack.md]] · [[docs/VAULT-AUDIT.md]] · [[docs/firmware-audit.md]]

**HOME** [[00 - Vault Hub]] · **UP** [[00 - Vault Hub]] · **RELATED** [[01 - Project HQ]] [[06 - Research Archive]] [[08 - Documentation Library]] · **CANVAS** [[09 - Decision Room/09 - Decision Room.canvas]]
