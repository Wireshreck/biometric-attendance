---
type: reference
area: documentation
status: active
tags:
  - documentation
  - reference
  - legend
  - navigation
---

# 08 - Documentation Library

**HOME** [[00 - Vault Hub]] · **UP** [[00 - Vault Hub]] · **RELATED** [[09 - Decision Room]] [[10 - Workshop]] [[00 - Vault Hub]] · **CANVAS** [[08 - Documentation Library/08 - Documentation Library.canvas]]

The reading room, and the shelf index. This is the note that answers **"which file do I actually read?"**

---

## The rule

> **One subject, one canonical document.**

Vault notes *link*. They never restate a specification. When two documents appear to disagree, the file named in the registry below is authoritative, and the other becomes a redirect stub.

The one existing example of the pattern working: `docs/esp32-pin-map.md` is a 5-line stub that says *"the authoritative map is `docs/final-pin-map.md` … do not maintain a second pin specification here."* That is the correct outcome, not a problem to fix.

---

## Canonical registry

### Project

| Subject | Authoritative file |
|---|---|
| Scope and work breakdown | [[docs/project-plan.md]] |
| Requirements | [[docs/requirements.md]] |
| Requirement → implementation → test traceability | [[docs/requirements-traceability.md]] |
| Architecture and trust boundaries | [[docs/architecture.md]] |
| Technology selection rationale | [[docs/software-stack.md]] |
| Dependency inventory | [[docs/dependencies.md]] |
| Forward roadmap / future ideas | [[10 - Workshop/TODO]] |
| **Task tracker (authoritative)** | [[10 - Workshop/TODO]] |
| **Milestones (authoritative)** | [[10 - Workshop/Milestones]] |
| **Decisions (authoritative)** | [[09 - Decision Room/Decision Log]] |

### Hardware

| Subject | Authoritative file |
|---|---|
| **GPIO / pin map** | [[docs/final-pin-map.md]] |
| Pin map redirect stub | [[docs/esp32-pin-map.md]] |
| **Electrical safety + measurement gate** | [[docs/power-and-safety.md]] |
| Bench wiring record | [[docs/wiring.md]] |
| Physical assembly procedure | [[docs/COMPLETE-BEGINNER-ASSEMBLY-GUIDE.md]] |
| Breadboard placement method | [[docs/complete-breadboard-layout.md]] |
| Component selection and limits | [[docs/hardware.md]] |
| Bill of materials and pricing | [[docs/bill-of-materials.md]] |
| Purchase checklist | [[docs/purchase-checklist.md]] |
| Sensor integration sequence | [[docs/r307s-integration-plan.md]] |
| Hardware evidence log | [[hardware/test-plan.md]] |

### Firmware

| Subject | Authoritative file |
|---|---|
| **Runtime behaviour and limits** | [[docs/production-firmware.md]] |
| Failure behaviour and recovery | [[docs/failure-modes.md]] |
| Code-side configuration | `firmware/include/config.h` |
| Build environments | `firmware/platformio.ini` |
| Environment overview | `firmware/README.md` |

### Backend

| Subject | Authoritative file |
|---|---|
| **API contract + status matrix** | [[docs/api-plan.md]] |
| Database design | [[docs/database-plan.md]] |
| Schema (executable) | `backend/migrations/001_initial_schema.sql` |
| Environment setup | `backend/README.md` |

### Testing

| Subject | Authoritative file |
|---|---|
| **Procedure** — what to run, in what order | [[docs/hardware-test-plan.md]] |
| **Evidence** — what actually happened | [[hardware/test-plan.md]] |
| Component environments | [[docs/component-tests.md]] |
| Integration environments INT-01…INT-10 | [[docs/integration-tests.md]] |
| Test strategy | [[docs/testing-plan.md]] |
| Sensor test matrix HW-01…HW-13 | [[docs/r307s-test-matrix.md]] |
| Test reporter semantics | `firmware/include/test_result.h` |

> Procedure and evidence live in **separate files on purpose**. A plan that gets edited after the fact is not evidence.

### Research

| Subject | Authoritative file |
|---|---|
| R307S hardware research + sources | [[docs/r307s-hardware-research.md]] |
| Troubleshooting decision tree | [[docs/r307s-troubleshooting.md]] |
| USB pad test path | [[docs/r307s-usb-test.md]] |
| Next-session handoff | [[docs/r307s-next-session.md]] |

### Security and privacy

| Subject | Authoritative file |
|---|---|
| Biometric privacy design | [[docs/privacy-security.md]] |
| Vulnerability reporting | `SECURITY.md` |
| Backup and recovery | [[docs/backup-strategy.md]] |
| Optional AI boundary | [[docs/ai-plan.md]] |

### Setup and environment

| Subject | Authoritative file |
|---|---|
| Full Windows software setup | [[docs/COMPLETE-SOFTWARE-SETUP.md]] |
| Development environment | [[docs/environment.md]] |
| Installed tool record | [[docs/installed-tools.md]] |
| Environment audit | [[docs/environment-audit.md]] |
| Deployment plan | [[docs/deployment-plan.md]] |
| Git and GitHub workflow | [[docs/github-setup.md]] |
| Maintenance scripts | `scripts/README.md` |
| Frontend (plan only) | `frontend/README.md` |
| CI | `.github/workflows/ci.yml` |
| General troubleshooting matrix | [[docs/troubleshooting.md]] |
| Hardware subsystem index | [[hardware/README.md]] |
| Licence | [[LICENSE.md]] (MIT) |

### Diagrams

Nine Mermaid sources in `diagrams/`, all referenced from canonical docs: `architecture` · `data-flow` · `attendance-flow` · `enrollment-flow` · `offline-sync` · `hardware` · `database` · `r307s-integration` · `ai-tool-calling`.

> `diagrams/r307s-integration.mmd` still carries `[TO VERIFY]` on every harness and pin, and titles the ESP32 group "Verified on COM3". Honest but dated — prefer [[docs/r307s-hardware-research.md]].

---

## Colour and status legend

The same twelve colours mean the same thing in every canvas, badge and node in this vault. Nothing is coloured arbitrarily.

| Colour | Hex | Means | Never used for |
|---|---|---|---|
| **PROJECT / HUB** | `#1d3557` | Vault entrance, project-wide | Any other area |
| **HARDWARE** | `#c2410c` | Physical parts, benches, wiring | Software |
| **FIRMWARE** | `#15803d` | Device runtime, embedded code | Backend |
| **BACKEND** | `#6d28d9` | API, database, server-side | Firmware |
| **TESTING** | `#0f766e` | Test environments and evidence | Implementation |
| **RESEARCH** | `#a16207` | Investigation, sources, unknowns | Decisions |
| **SCIENCE FAIR** | `#be185d` | Exhibition, presentation, demo | Engineering |
| **DOCUMENTATION** | `#475569` | Documents, diagrams, records | Live status |
| **DECISIONS** | `#b91c1c` | ADRs, trade-offs, rationale | Research |
| **WORKSHOP / ACTIVE** | `#0891b2` | In-progress work, current bench | Settled decisions |
| **VERIFIED** | `#15803d` | Evidence exists and was observed | — |
| **UNVERIFIED** | `#92400e` | Mapped but unmeasured — dashed border | A failure |
| **NOT EXECUTED** | `#525252` | Never run on hardware — dashed border | A pass |
| **BLOCKED** | `#b91c1c` | A prerequisite prevents progress | A result |
| **DEPRECATED** | `#525252` | Superseded, kept for history | Current truth |

**Text badges are authoritative.** Colour reinforces them; it never carries meaning alone. `[[docs/r307s-test-matrix.md]]` statuses are always written out, because a colour-blind reader and a screen reader must get the same answer.

---

## Documentation rules

1. **No duplicate technical truth.** If a fact lives in `docs/`, a vault note links to it. It does not restate it.
2. **No metadata on source files.** `.cpp` `.h` `.py` `.sql` `.mmd` `.ps1` `.yml` `.json` get no YAML frontmatter. Adding `type:` to a Python file helps nobody and breaks nothing usefully.
3. **Frontmatter is consistent** where it exists — `type`, `area`, `status`, `tags`, using the vocabularies in [[00 - Vault Hub]] and the legend above.
4. **Status words mean evidence.** `IMPLEMENTED` ≠ `VERIFIED`. `BUILD PASS` ≠ `PASS`.
5. **Never delete history.** Superseded notes get a `DEPRECATED` marker and a pointer, not removal. See [[09 - Decision Room/Decision Log]].

---

## Vault maintenance

| Practice | How |
|---|---|
| New document | Add it to the registry above, then to [[08 - Documentation Library/08 - Documentation Library.canvas]] |
| New area | Add a folder, a hub, a canvas, a colour, and a Master Canvas node |
| Link audit | Every wikilink must resolve; no note may be an orphan |
| Redirection | Replace stale prose with a one-line pointer to the canonical file, never a second copy |

---

## Documents

[[docs/VAULT-AUDIT.md]] · [[docs/firmware-audit.md]] · [[AI_CONTEXT.md]] · [[CONTRIBUTING.md]] · [[README.md]]

**HOME** [[00 - Vault Hub]] · **UP** [[00 - Vault Hub]] · **RELATED** [[09 - Decision Room]] [[10 - Workshop]] · **CANVAS** [[08 - Documentation Library/08 - Documentation Library.canvas]]
