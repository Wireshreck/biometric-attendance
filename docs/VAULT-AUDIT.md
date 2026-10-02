---
type: reference
area: documentation
status: verified
tags:
  - audit
  - vault
  - documentation
  - project
---

# Vault Audit — Pre-Restructuring Repository Survey

**Audit date:** 2026-10-02
**Scope:** complete repository at `6f84eb8` (`docs: finalize firmware and hardware handoff`), branch `main`, clean working tree, in sync with `origin/main`.
**Method:** read-only inspection of every tracked source file, all Markdown, the single existing Canvas, all Mermaid diagrams, Git history, and both build/test toolchains. No technical fact was changed to make the inventory tidier.
**Companion:** [[10 - Workshop]] · [[08 - Documentation Library]]

> [!IMPORTANT]
> This document predates the vault restructure. It is the *before* picture. The *after* picture is [[00 - Vault Hub]] and [[00 - Master Canvas.canvas]].

---

## 1. Current repository structure

Tracked content at audit time (`.git`, `.pio`, `backend/.venv`, `__pycache__` excluded):

```text
biometric-attendance/
├── .github/            CI workflow, issue + PR templates
├── .obsidian/          ignored local app workspace (app/appearance/core-plugins/graph/workspace.json)
├── AI_CONTEXT.md       root agent guide
├── CONTRIBUTING.md  LICENSE  LICENSE.md  README.md  SECURITY.md
├── backend/            FastAPI + SQLite (app/, migrations/, tests/, data/, .env.example)
├── diagrams/           9 Mermaid .mmd sources
├── docs/               46 Markdown documents
├── firmware/           PlatformIO project (include/, src/, .vscode/, data/)
├── frontend/           README-only placeholder (no UI code)
├── hardware/           README.md, pinout.md, test-plan.md (evidence log)
├── obsidian/           25 notes + 1 Canvas ("Attendance System")
├── presentation/       outline.md, demo-script.md, judge-questions.md
├── scripts/            3 PowerShell scripts + README
└── .freebuff/          ignored local agent metadata
```

Findings:

- The **vault was a subdirectory** (`obsidian/Attendance System/`), not the repository root. The root `.obsidian/` folder existed but was explicitly git-ignored, so the "vault" and the "app config" were in two unrelated places.
- `frontend/` contains no application code — a design note only.
- `hardware/` contains prose only — no schematic, no BOM file, no captured test log format beyond a Markdown table.
- `.gitignore` explicitly states: *"Root .obsidian is separate local UI/workspace configuration; the project knowledge base is under obsidian/."* This is the rule that has to change.

## 2. Current documentation structure

46 documents in `docs/`, plus 25 in `obsidian/Attendance System/`, 3 in `presentation/`, 3 component READMEs, and 5 root documents.

The `docs/` set already has good canonical candidates and a real duplication problem:

| Concern | Canonical candidate | Competing / stale documents |
|---|---|---|
| GPIO map | `docs/final-pin-map.md` | `docs/esp32-pin-map.md` (explicit redirect stub), `hardware/pinout.md`, `diagrams/r307s-integration.mmd` |
| Test execution | `docs/hardware-test-plan.md` | `docs/component-tests.md`, `docs/integration-tests.md`, `docs/testing-plan.md`, `hardware/test-plan.md` (evidence log), `docs/r307s-test-matrix.md` |
| Sensor state | `docs/r307s-hardware-research.md`, `docs/r307s-test-matrix.md`, `docs/r307s-next-session.md` | `docs/r307s-integration-plan.md` (10-phase *plan*, partly superseded), `docs/troubleshooting.md` |
| Assembly | `docs/COMPLETE-BEGINNER-ASSEMBLY-GUIDE.md`, `docs/complete-breadboard-layout.md` | `obsidian/…/18 - Complete Build Guide.md` |
| Firmware behaviour | `docs/production-firmware.md`, `docs/failure-modes.md` | `obsidian/…/06 - Firmware Plan.md` |

`docs/esp32-pin-map.md` is already a *deliberate* redirect stub (5 lines) and states it must not become a second pin specification. That is the correct pattern and should be preserved, not deleted.

## 3. Current firmware architecture

**Firmware is no longer the validation sketch described by the earlier audit.** It is now a real, modular, local-first attendance runtime.

```text
firmware/src/main.cpp                       12 lines — delegates to attendance_app_*
firmware/src/app/attendance_app.cpp        248 lines — lifecycle, state machine, serial operator
                                                 commands, event creation, dispatch, retry
firmware/src/app/attendance_state.cpp      17 lines — state-name table
firmware/src/hardware/device_services.cpp  160 lines — OLED, DS3231, LED/buzzer, R307S wrapper
firmware/src/network/network_service.cpp   92 lines — Wi-Fi, HTTP, bearer auth, contract payloads
firmware/src/storage/attendance_store.cpp  150 lines — LittleFS CRC32 JSONL journal, acks, compaction
firmware/src/r307s_uart_diag.cpp          560 lines — read-only bring-up diagnostic
firmware/src/test_modes/*.cpp             505 lines — 14 isolated component/integration entry points
```

State machine: `BOOT → SELF_TEST → READY | WAITING_FOR_FINGER → IDENTIFYING → ATTENDANCE_RECORDED → SYNCING`, with `ERROR`, `OFFLINE`, `RECOVERY`.

Key architectural properties discovered in source:

- **Fingerprint service is `FingerprintService` in `device_services.h`**, wrapping `Adafruit_Fingerprint` on `HardwareSerial(2)` at 57600 8-N-1 on RX32/TX33.
- `firmware/include/fingerprint_sensor.h` is now an **11-line DEPRECATED notice**. It declares nothing. No production source includes it. This is the correct resolution of the earlier "interface with no implementation" problem — and it is easy to mistake for live code during a vault build.
- `firmware/platformio.ini` `[env:production]` `build_src_filter` still lists `+<fingerprint/*.cpp>`. **No `firmware/src/fingerprint/` directory exists.** PlatformIO ignores the unmatched filter, so the build passes, but the filter is a leftover.
- `firmware/include/config.h` is the single code-side source of truth: `PIN_R307S_RX 32`, `PIN_R307S_TX 33`, `R307S_BAUD_RATE 57600`, I2C `21/22`, OLED `0x3C`, RTC `0x68`, green `18`, red `19`, buzzer `23`, `ATTENDANCE_ENDPOINT "/api/v1/attendance"`, `LOCAL_TIMEZONE_OFFSET "+05:30"`, queue bounds 48 KiB / 100 pending. The obsolete `PIN_R703_*` aliases noted by the earlier audit are **already gone**.
- Credentials flow through ignored `firmware/include/local_config.h`; the tracked example contains only empty strings.

## 4. Current backend architecture

```text
backend/app/main.py             345 lines — app factory, lifespan, 3 exception handlers, 8 routes
backend/app/database.py         171 lines — aiosqlite connect, WAL, contiguous transactional migrations
backend/app/schemas.py           58 lines — bounded Pydantic models (extra="forbid")
backend/app/auth.py              61 lines — require_admin (HTTP Basic), require_device (Bearer + SHA-256)
backend/app/config.py            42 lines — env settings with fail-fast validation
backend/app/dependencies.py      23 lines — request-scoped connection/settings
backend/app/provision_device.py  58 lines — one-time CLI, prints token once, stores only its hash
backend/migrations/001_initial_schema.sql — 4 tables, 6 indexes, CHECK/UNIQUE/FK constraints
```

**Implemented routes (all present in `main.py`):** `GET /health`, `GET/POST /api/v1/students`, `GET /api/v1/students/{uuid}`, `POST /api/v1/students/{uuid}/deactivate`, `GET /api/v1/devices/{device_uuid}/enrollment/{student_uuid}`, `POST …/enrollment/{student_uuid}/complete`, `POST /api/v1/attendance`.

Every one of the seven is listed as VERIFIED in `docs/api-plan.md`. The routes are genuinely implemented, not aspirational. Everything else in that document (device list, cleanup, heartbeat, attendance query, reports, CSV, SSE) is PLANNED with no code.

Firmware → backend coupling, read directly from `network_service.cpp`:
`sendAttendance` POSTs to `ATTENDANCE_ENDPOINT`; `enrollmentAssignment` GETs `/api/v1/devices/{uuid}/enrollment/{student}`; `enrollmentComplete` POSTs `…/complete`. All three match `main.py` exactly. This is a real, checked contract — the one integration in the repo that is code-verified on both sides.

## 5. Current hardware architecture

Authoritative map is `docs/final-pin-map.md` (35 lines). `config.h` matches it. `hardware/pinout.md`, `docs/wiring.md`, and `docs/power-and-safety.md` all repeat the same owner-reported table and all carry the same UNVERIFIED markers.

| Component | Interface | ESP32 pins | Evidence class |
|---|---|---|---|
| R307S sensor | UART2, 57600 8-N-1 | RX 32, TX 33 | Assembled per owner report; **0 valid bytes received**; rail/logic UNVERIFIED |
| SSD1306 OLED 128×64 | I2C `0x3C` | SDA 21, SCL 22 | Mapped, never executed |
| DS3231 RTC | I2C `0x68` | SDA 21, SCL 22 | Mapped, never executed |
| Green LED | GPIO out via resistor | 18 | Mapped, never executed |
| Red LED | GPIO out via resistor | 19 | Mapped, never executed |
| Active buzzer | GPIO in / driver | 23 | Mapped, never executed; module identity unknown |
| Power | USB 5 V in, 3V3 out | — | Unmeasured rails; CR2032 is **not** a sensor supply |

ESP32 restrictions documented and honoured: GPIO1/3 reserved for USB serial, GPIO25/26 reserved for loopback-only, strap pins 0/2/5/12/15 avoided, flash pins 6–11 avoided, 34–39 never outputs.

**Stale-hardware reconciliation already performed** by the previous work: GPIO16/17, "not connected or powered", `PIN_R703_*` aliases, and the R703/AS608 identification are all explicitly marked superseded. `docs/esp32-pin-map.md`, `docs/final-pin-map.md`, `docs/wiring.md`, `docs/power-and-safety.md`, `hardware/pinout.md`, and `hardware/test-plan.md` are all current. The remaining stale references are confined to `obsidian/`, `README.md`, and `AI_CONTEXT.md`, which all still tell the reader to *open `obsidian/` as the vault*.

## 6. Current test architecture

**27 PlatformIO environments** in `firmware/platformio.ini`:

- 2 build targets: `production` (default) and `esp32dev` (compatibility alias extending `production`).
- 15 component environments: `esp32_core`, `uart1_loopback`, `uart2_loopback`, `r307s`, `i2c_scan`, `oled`, `rtc`, `green_led`, `red_led`, `buzzer`, `gpio_sanity`, `wifi_diag`, `backend_http`, `json`, `storage`, `power_reset`.
- 9 integration environments: `int_oled`, `int_rtc`, `int_outputs`, `int_r307s`, `int_r307s_oled`, `int_r307s_rtc`, `int_wifi`, `int_backend`, `int_full`, selected by `-D INTEGRATION_CASE=1..9` against one `integration_test.cpp`.

Design pattern worth preserving: each environment uses `build_src_filter = -<*> +<one file>`, so exactly one `setup()/loop()` entry point compiles. `include/test_result.h` is a shared reporter whose `finish()` cannot return `PASS` when checks were skipped or marked unverified — the code itself enforces the "build ≠ hardware" discipline.

Backend: 10 tests in `backend/tests/` (`test_api.py` 164 lines, `test_database.py` 167 lines), plus `backend/test_env.py` (54 lines). **Re-run during this audit: 10 passed, 1 upstream Starlette deprecation warning, 0.79 s.**

Firmware: `pio run -d firmware -e production` re-run during this audit — see [[10 - Workshop]] for the recorded result. Build evidence establishes compile/link only.

## 7. Current science-fair structure

- `docs/science-fair.md` (33 lines) — engineering question, experiment table with *measurement and sample size to define before running*, booth plan.
- `docs/science-fair-timeline.md` (24 lines) — target gates Sep 25 → Oct 09 2026.
- `docs/SCIENCE-FAIR-SETUP.md` (53 lines) — pack list, pre-departure checks, venue startup, recovery.
- `presentation/outline.md` — 3-minute talk + 2-minute demo, with an explicit "claims gate".
- `presentation/demo-script.md` — conditional live sequence with a labelled fallback for **every** stage.
- `presentation/judge-questions.md` — 10 anticipated questions, each answered with "not measured" where that is the truth.

This is unusually disciplined material. Every one of these files refuses to present a target as a result. The vault must not soften that.

## 8. Existing Obsidian structure

`obsidian/Attendance System/` — 24 notes + 1 Canvas, all tracked in Git.

| Group | Files | Disposition |
|---|---|---|
| Navigation pages | `00`–`18` (19 notes) | Thin status pages that duplicate `docs/`. Superseded by area hubs; each already links to its canonical doc. |
| Operational | `TODO.md`, `Decision Log.md`, `Milestones.md`, `AI Project Handoff.md` | **Genuinely unique content.** Task IDs (FND/HW/FW/API/UI/INT/SEC/BUILD/DEMO/AI), ADR-001…ADR-014, milestone gates. Must be migrated, not deleted. |
| Canvas | `Architecture.canvas` (37 nodes, 23 edges, 22 file nodes, 6 groups, 9 text labels) | Old architecture map. Superseded by the new facility canvases; content preserved where still true. |
| Guides | `AI Development Guide.md`, `18 - Complete Build Guide.md` | Build guide is superseded by `docs/COMPLETE-BEGINNER-ASSEMBLY-GUIDE.md` + `docs/complete-breadboard-layout.md` + `docs/final-pin-map.md`, which it already defers to. |

Frontmatter in the old vault uses `type: project-navigation` / `status: IN PROGRESS` / `updated:` — a *third* vocabulary alongside the `docs/` free-text bold status lines and the old TODO's 9-value status vocabulary. Three status vocabularies in one repository is a real navigation defect.

## 9. New files discovered

Since the last vault work, these appeared and are the reason the old vault is stale:

**Firmware (all new):** `attendance_state.h/.cpp`, `attendance_store.h/.cpp`, `device_services.h/.cpp`, `network_service.h/.cpp`, `attendance_app.cpp`, `test_result.h`, the 14 `test_modes/*.cpp` files, and the rewritten `platformio.ini`. `main.cpp` shrank from a 24-line diagnostic sketch to a 12-line delegator.

**Documentation (all new):** `COMPLETE-BEGINNER-ASSEMBLY-GUIDE.md`, `COMPLETE-SOFTWARE-SETUP.md`, `SCIENCE-FAIR-SETUP.md`, `complete-breadboard-layout.md`, `component-tests.md`, `esp32-pin-map.md`, `failure-modes.md`, `final-pin-map.md`, `firmware-audit.md`, `hardware-test-plan.md`, `integration-tests.md`, `next-steps.md`, `power-and-safety.md`, `production-firmware.md`. Plus the five R307S evidence documents.

**Behaviour change:** the old vault's `00 - Project Overview` says firmware is a "runtime skeleton … it does not create/send/queue attendance events." That is now false. The old vault would actively mislead a reader.

## 10. Duplicated documentation

Confirmed duplication classes, in descending severity:

1. **Firmware status prose** — stated independently in `README.md`, `AI_CONTEXT.md`, `obsidian/…/00`, `obsidian/…/06`, `docs/firmware-audit.md`, `docs/production-firmware.md`, `docs/architecture.md`, `docs/next-steps.md`, and the old TODO. Nine copies; all currently agree, which is lucky rather than designed.
2. **R307S wiring table** — `docs/final-pin-map.md`, `docs/wiring.md`, `docs/power-and-safety.md`, `hardware/pinout.md`, `hardware/README.md`, `obsidian/…/03`. Six copies.
3. **Pin map** — see §2.
4. **Test matrices** — `docs/hardware-test-plan.md` (procedure), `hardware/test-plan.md` (evidence), `docs/r307s-test-matrix.md` (sensor evidence), `docs/component-tests.md` (build matrix), `docs/integration-tests.md` (INT-01..10), `docs/testing-plan.md` (strategy). These are *complementary*, not duplicate — they must stay separate files.
5. **Build instructions** — `docs/COMPLETE-SOFTWARE-SETUP.md`, `obsidian/…/18 - Complete Build Guide.md`, `README.md`, `backend/README.md`, `firmware/README.md`, `docs/environment.md`, `docs/installed-tools.md`, `docs/environment-audit.md`.

None of this duplication is *wrong*. It is unmanaged. The vault's job is to make one canonical document authoritative per subject and point at it, not to rewrite the documents.

## 11. Canonical documentation candidates

| Subject | Canonical file | Everything else links here |
|---|---|---|
| Vault entry point | `00 - Vault Hub.md` (new) | README, AI_CONTEXT |
| GPIO / pin map | `docs/final-pin-map.md` | `docs/esp32-pin-map.md` already redirects |
| Electrical safety | `docs/power-and-safety.md` | wiring, pin map, troubleshooting |
| Breadboard layout | `docs/complete-breadboard-layout.md` | assembly guide |
| Human assembly | `docs/COMPLETE-BEGINNER-ASSEMBLY-GUIDE.md` | `obsidian/…/18` |
| Component tests | `docs/component-tests.md` | hardware-test-plan |
| Integration tests | `docs/integration-tests.md` | hardware-test-plan |
| Test procedure vs evidence | `docs/hardware-test-plan.md` (procedure) + `hardware/test-plan.md` (evidence) | Testing Lab |
| Sensor research | `docs/r307s-hardware-research.md` | Research Archive |
| Sensor evidence | `docs/r307s-test-matrix.md` | hardware/test-plan |
| Sensor decision tree | `docs/r307s-troubleshooting.md` | Workshop |
| Sensor session handoff | `docs/r307s-next-session.md` | Workshop |
| Sensor USB path | `docs/r307s-usb-test.md` | Research Archive |
| Firmware behaviour | `docs/production-firmware.md` | architecture, failure-modes |
| Firmware failure modes | `docs/failure-modes.md` | production-firmware |
| API contract | `docs/api-plan.md` | network_service.cpp reality |
| Database | `docs/database-plan.md` + `migrations/001_initial_schema.sql` | api-plan |
| Privacy | `docs/privacy-security.md` | SECURITY.md |
| Tasks | `10 - Workshop/TODO.md` (migrated) | hub |
| Decisions | `09 - Decision Room/Decision Log.md` (migrated) | hub |
| Milestones | `10 - Workshop/Milestones.md` (migrated) | hub |
| Repository audit | `docs/firmware-audit.md` + this file | Decision Room |

## 12. Broken / missing links

Audited, with results:

- **`obsidian/` references in tracked files: present and now harmful.** `README.md` ("Open `obsidian/` as the Obsidian vault"), `AI_CONTEXT.md` (5 links), `docs/next-steps.md` (`[[TODO]]`), `docs/r307s-integration-plan.md`, `presentation/outline.md`, and 25 notes inside `obsidian/` itself that use `../../docs/…` relative paths. All become dead or wrong once the directory is removed.
- **`[[TODO]]` from `docs/next-steps.md`:** an unqualified wikilink that only resolves inside the old vault. Dead outside it.
- **Broken markdown links inside `docs/`: none found.** Every relative link in `docs/*.md` resolves.
- **`firmware/README.md`: still references R703** in at least one test instruction (flagged by the previous audit; not re-verified here in full).
- **Serial port drift:** `docs/r307s-next-session.md` commands use `COM3`; the current port is **COM4** (VID:PID `1A86:7523`). The document already instructs the reader to re-enumerate, but the literal examples are stale.
- **Mermaid `diagrams/r307s-integration.mmd`:** still shows `[TO VERIFY]` on every harness and pin, and titles the ESP32 group "Verified on COM3". Honest but doubly stale.
- **Canvas file nodes:** the old `Architecture.canvas` has 22 file nodes; several target documents that have since been renamed or added. Requires re-validation after migration.
- **No orphan-by-construction plan yet:** 25 old notes would become orphans the moment `obsidian/` is deleted unless they are migrated or given inbound links.

## 13. Existing Canvas files

Exactly one: `obsidian/Attendance System/Architecture.canvas`.

- 16 KB, valid Obsidian JSON Canvas.
- 37 nodes / 23 edges / 6 groups / 9 text labels / 22 file nodes.
- Node IDs and edges are hand-authored; colour is applied per node, not semantically standardised.
- It is a *subsystem* map (edge → network → service → storage), not a facility map, and it predates the entire production firmware.

## 14. Missing Canvas coverage

Zero coverage exists for: the facility itself, hardware assembly/breadboard, the test matrix, the sensor research chain, the decision log, the science-fair chain, and the documentation library. Only the subsystem map exists, and it is out of date.

Required coverage after restructure: 1 master facility map, 1 per area (10), 1 dedicated hardware assembly map, and a colour legend. Twelve canvases.

## 15. Recommended vault structure

Make the **repository root** the vault. Rationale: the vault must be an index *over* the code; a vault in a subdirectory cannot be an index over files outside it without ugly `../../` paths — which is exactly why the old vault accumulated them.

```text
/
├── .obsidian/                       app, appearance, core-plugins, graph, workspace, bookmarks
├── 00 - Vault Hub.md                the entrance
├── 00 - Master Canvas.canvas        the facility map
├── 01 - Project HQ/                 hub + canvas
├── 02 - Hardware Lab/               hub + canvas + 02 - Hardware Assembly.canvas
├── 03 - Firmware Lab/
├── 04 - Backend Server Room/
├── 05 - Testing Lab/
├── 06 - Research Archive/
├── 07 - Science Fair/
├── 08 - Documentation Library/
├── 09 - Decision Room/
├── 10 - Workshop/                   hub + canvas + migrated TODO/Milestones
├── docs/  firmware/  backend/  hardware/  diagrams/  presentation/  frontend/  scripts/
└── obsidian/                        DELETED
```

Ten areas, mapped to the physical-facility metaphor the project actually has: Project HQ, Hardware Lab, Firmware Lab, Backend Server Room, Testing Lab, Research Archive, Science Fair, Documentation Library, Decision Room, Workshop.

Two rules make this an index rather than a fork:

1. **Area hubs never restate technical truth.** They carry status, navigation, and links. The pin map stays in `docs/final-pin-map.md`.
2. **One colour vocabulary, defined once.** Every canvas and every status badge uses the same ten semantic colours.

## 16. Migration plan

| Step | Action | Guard |
|---|---|---|
| 1 | Write this audit | Done — before any change |
| 2 | Create `00 - Vault Hub.md` | — |
| 3 | Create `01`–`10` folders, hub note + canvas each | Every hub links back to the hub and to its canvas |
| 4 | Create `00 - Master Canvas.canvas` | Facility map, not a hairball |
| 5 | Create `02 - Hardware Assembly.canvas` | Mirrors `docs/complete-breadboard-layout.md` coordinates; marks unverified items |
| 6 | Migrate `TODO.md`, `Milestones.md`, `Decision Log.md` into `10 - Workshop/` and `09 - Decision Room/` | Preserve every ID and every ADR row verbatim |
| 7 | Create a new Decision Log row for the R307S identity correction and for the vault restructure itself | History is extended, never rewritten |
| 8 | Retarget every `obsidian/`-relative link in tracked files | Full-text search for `obsidian/` must return only the audit's own description |
| 9 | Track `.obsidian/` config so the vault configuration travels with the repo | Un-ignore config JSON, keep cache/transient ignored |
| 10 | Delete `obsidian/` | Only after step 8 shows zero remaining inbound references |
| 11 | Add frontmatter to major docs | Source files (`.cpp/.h/.py/.sql/.mmd/.ps1/.yml`) get **no** frontmatter |
| 12 | Colour legend + graph colour groups | Native Obsidian `graph.json` only |
| 13 | Link audit: every wikilink resolves; no orphans; no `obsidian/` strings | Automated check |
| 14 | Validation: `pio run -e production`, backend `pytest`, `git diff --check` | — |
| 15 | Commit and push | — |

**What must not change:** the R307S stays UNVERIFIED. Zero bytes is not a dead sensor. A successful compile is not a working device. No measurement, wire, capacity, latency or accuracy claim may be invented anywhere in the vault.

---

## Audit outcome

The repository is in better shape than its knowledge system. The firmware went from sketch to working local-first runtime; the backend vertical slice is real and tested; the sensor investigation is the most honest body of evidence in the project. What is missing is not content — it is a map. That is what this restructure adds, and nothing else.
