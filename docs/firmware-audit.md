---
type: reference
area: documentation
status: active
tags:
  - audit
  - firmware
  - history
---
# Firmware and Hardware Takeover Audit

**Audit date:** 2026-10-02
**Scope:** Existing repository, firmware, R307S investigation, hardware assumptions, backend contract, tests, Git state, and project handoff notes.
**Change policy:** This report was written only after the read-only inspection phase. It records repository evidence separately from the owner’s current bench report.

> [!NOTE]
> **Historical document.** This audit records the repository as it stood on the date above. It is kept for provenance and is deliberately **not** updated as the project moves on. For the current structure see [[docs/VAULT-AUDIT.md]] and [[00 - Vault Hub]]; for the current task state see [[10 - Workshop/TODO]].

## Executive status

The repository is an established project on `main`, with an existing GitHub remote and history through `d8df140` (`feat(r307s): add UART diagnostics and document hardware investigation`). The working tree was clean at audit start. No history was rewritten and no commit or push was performed.

The firmware currently builds, but it is a validation sketch that runs a read-only R307S UART diagnostic and then idles. It is not an attendance application. Backend API/database software exists and its 10 tests pass in the ignored backend virtual environment. No standalone component-test environments, integration firmware, or production firmware modules exist yet.

The latest user-provided bench state for this task is: R307S wired red/VIN, black/GND, yellow/GPIO32 RX, green/GPIO33 TX; blue/white disconnected; the UART diagnostic returns zero bytes at tested rates/routings. This current report supersedes stale repository prose saying the sensor is disconnected and unpowered. It does **not** establish that the supply rail, sensor input voltage, UART logic level, exact PCB routing, or sensor health is electrically verified. Supply and logic measurements remain **UNVERIFIED — REQUIRES MULTIMETER**.

## A. Repository and Git

- Repository: `C:\Users\user\projects\fair\biometric-attendance`.
- Branch: `main`, tracking `origin/main` at audit time; remote is the existing GitHub repository.
- Latest history inspected: 20 commits. Relevant hardware sequence is R703 migration (`b92e9fd`), R307S integration (`e9b501f`), then read-only R307S diagnostics (`d8df140`). Prior project milestones include database and backend vertical slice commits.
- Initial `git status --short --branch`: clean (`main...origin/main`). No uncommitted tracked work was present.
- No Git initialization, reset, commit, or push was performed.
- Ignored local material includes `.obsidian/`, `.freebuff/`, PlatformIO build output, backend venv/cache, Python caches, and `backend/data/api-smoke.db`. These did not appear as tracked files.
- `.gitignore` excludes secrets/config files, virtual environments, `.pio`, SQLite runtime files, caches, logs, and the root Obsidian UI workspace. It allows example configs. No obvious secret was found in tracked source; one credential-pattern search hit was in backend test fixtures and was not a live credential.

## B. Repository contents and project structure

The repository contains `backend/`, `firmware/`, `frontend/`, `hardware/`, `docs/`, `diagrams/`, `scripts/`, `presentation/`, and the nested Obsidian knowledge base at `obsidian/Attendance System/`. It also has root documentation, CI/issue templates, and a separate root `.obsidian/` local workspace configuration. The nested knowledge base contains the planned numbered notes, build guide, AI guide/handoff, task tracker, milestone log, decision log, and Canvas.

No backend implementation is present in `frontend/`; it currently contains a status README. The firmware has no test directory or component-specific environments. `hardware/` contains documentation and test procedures, not a hardware schematic or measured test-result log.

## C. Current firmware and build

### What exists

- `firmware/platformio.ini` defines only one environment, `esp32dev`, targeting `esp32dev` / Arduino with pinned ESP32 platform and libraries. LittleFS is selected but no queue exists.
- `firmware/src/main.cpp` is labelled a pre-development toolchain check. It prints chip/CPU/heap data, initializes the proposed indicators low, waits, invokes the UART diagnostic once, and idles.
- `firmware/src/r307s_uart_diag.cpp` is a substantial finite-timeout, read-only probe. It tests a baud ladder, packet construction/checksums, response parsing, raw receive data, a line-state probe, and swapped GPIO-matrix routing. It only sends VerifyPassword, ReadSysPara, and TemplateCount; no enrollment/delete/write commands are sent.
- `firmware/include/fingerprint_sensor.h` is an interface declaration only; it has no implementation.
- `firmware/include/config.h` is the current code-side pin/config source. It selects R307S UART RX 32/TX 33 at 57600, I2C 21/22, OLED 0x3C, RTC 0x68, green 18, red 19, buzzer 23, and an HTTP attendance path. Most assigned peripherals are still untested. Local credentials are optional through ignored `local_config.h`; the example is blank.
- Dependencies include the Adafruit fingerprint library, SSD1306/GFX, RTClib, and ArduinoJson. The current sketch includes those libraries but does not exercise the peripherals.

### Build evidence from this audit

- `pio run -d firmware`: **PASS**, current checkout; PlatformIO Core 6.2.x, ESP32 platform 6.5.0, Arduino framework 2.0.14. This is compilation only; no upload or device execution was performed in this audit.
- `python -m pytest tests -q` using system Python: collection **BLOCKED** because backend dependencies are not installed there.
- `backend/.venv/Scripts/python.exe -m pytest tests -q`: **PASS**, 10 tests; one upstream Starlette deprecation warning.
- Existing project notes report an earlier successful ESP32 build/upload/USB serial check on COM3, and the owner reports the latest firmware runs while the sensor returns no bytes. Those are repository/user-reported bench evidence, not a physical execution performed by this audit.

## D. Hardware and pin map audit

### Owner-reported current state

| Component | Owner-reported/current documented state | Audit classification |
|---|---|---|
| ESP32-WROOM-class dev board | Prior compile/upload/USB serial works; current firmware diagnostic runs | **VERIFIED (reported; not retested here)** |
| R307S | 6-wire harness observed; user reports assembled connection and attempted UART probes with no response | **CONNECTED / NO UART RESPONSE (reported)**; health unknown |
| R307S supply from ESP32 VIN | User reports this wiring; voltage/current not independently measured | **UNVERIFIED — REQUIRES MULTIMETER** |
| R307S TX logic level and exact six-position electrical mapping | Not measured or confirmed from this physical board during this audit | **UNVERIFIED — REQUIRES MULTIMETER / physical marking evidence** |
| OLED SSD1306 | Planned/available in docs, no current test evidence | **NOT VERIFIED** |
| DS3231 RTC | Planned/available in docs, no current test evidence; CR2032 cautions appear in docs | **NOT VERIFIED** |
| Green/red LEDs, active buzzer | Planned, pins documented; physical connection/test evidence absent | **NOT VERIFIED** |
| Wi-Fi/backend link | API exists; no ESP32 Wi-Fi client implementation | **NOT IMPLEMENTED** |
| CR2032 | RTC backup candidate only; not a sensor main supply | Must not be treated as R307S supply |

### Current assignments and conflicts

`config.h` selects 32/33 for R307S UART, while `hardware/pinout.md`, `docs/wiring.md`, and the integration plan still name 16/17. The latest diagnostic source uses 32/33, and the current user-provided assembly also uses 32/33. Preserve 32/33 as the current bench assignment and update the authoritative pin map/docs; do not rewire based on stale 16/17 prose.

For a classic ESP32-WROOM-32, GPIO32/33 are available input/output GPIOs, with ADC1 functions; they are not boot-strapping pins, flash GPIOs, or input-only pins. GPIO21/22, 18/19/23 are also ordinary usable GPIOs in the stated mapping. UART2 uses the GPIO matrix. Confirm the exact dev-board/module variant if the hardware is later changed. Avoid ESP32 strap pins GPIO0/2/5/12/15 for fixed peripherals, GPIO6–11 for flash, and GPIO34–39 for outputs. The UART0 console uses GPIO1/3; retain it for programming/logging.

### External source check

- The R307S-titled quick-start identifies 5V, GND, TXD, and RXD in its example and an R307-family datasheet describes TTL UART, 4.2–6.0 V supply for the R307, typical/peak current, and the `9600 × N` baud family. This supports general protocol expectations but does not prove this unit’s wire-color mapping, jumper state, or voltage.
- The family datasheet is not a substitute for the exact R307S board revision. The R307S quick-start does not identify all six connector positions. The existing research note’s pin 5/6 touch circuit and jumper descriptions depend on third-party/family evidence and should remain qualified until matched to the physical board/manual revision.
- Espressif’s ESP32 datasheet describes the strap, input-only, and flash/memory pin restrictions. The WROOM module and dev-board revision still matter for board-specific availability.

## E. R307S diagnostic findings and preservation

Preserve `r307s_uart_diag.{h,cpp}` as useful read-only diagnostic code. It is not obsolete merely because it has not established a valid response. Its result supports the limited conclusion “no valid response was received under tested assumptions,” not “sensor is dead.” The current task confirms the user’s latest observed condition is connected/wired and silent; power quality, signal voltage, address, sensor health, and actual wire-to-pad mapping remain possible unknowns.

The newest repository diagnostic report (`docs/r307s-hardware-research.md` and `docs/r307s-next-session.md`) captures extensive UART test output and concludes that baud/routing hypotheses were tested. Older `AI_CONTEXT.md`, `docs/r307s-integration-plan.md`, `hardware/pinout.md`, `hardware/test-plan.md`, Obsidian TODO, decision log, and build notes still state “not connected or powered” or use GPIO16/17. Those statements are stale against this task’s current hardware report and must be synchronized. Do not discard previous diagnostic evidence or convert it into an unsupported hardware-failure claim.

## F. Backend and API boundary

Backend source has SQLite migrations/connection handling, configuration/authentication, device provisioning, Pydantic schemas, and FastAPI routes. Implemented software routes include health, authenticated student creation/list/read/deactivation, device enrollment assignment/completion, and authenticated attendance ingestion. Ingestion accepts the fingerprint slot, UUID, capture time, and sync status; it uses idempotency and suppresses distinct accepted scans within 60 seconds. It does not receive raw fingerprint images/templates.

No firmware HTTP client exists. The code-side endpoint `/api/v1/attendance` and testable contract are present, but the firmware still needs to match the exact schema and device bearer-token scheme from backend source/docs. Current prototype uses local HTTP and is documented as synthetic data on an isolated demo LAN only. Do not transmit test records to a real deployment; future connectivity tests need a local mock or the isolated project backend with synthetic fixtures.

## G. Documentation, plans, and Obsidian

Existing documentation is substantial: requirements/traceability, architecture, API/database, privacy/security, firmware/hardware plans, R307S research and test notes, troubleshooting, build steps, BOM, schedule, environment audits, and presentation material. It describes a local-first ESP32 → sensor/RTC/display → Wi-Fi → FastAPI → SQLite flow, with frontend and optional read-only AI still planned.

The nested Obsidian note collection is the knowledge/navigation workspace. Root `.obsidian/` is an ignored local app workspace and distinct from the nested note folder. The Canvas already links project subsystems. No destructive restructuring is warranted for this firmware task.

Important synchronization defects found:

- Current bench status is contradicted by stale “never connected/powered” language across multiple docs and Obsidian notes.
- GPIO32/33 in source/latest evidence conflicts with stale GPIO16/17 wiring and test docs.
- Several docs refer to R703/AS608 historically; those are superseded and must not be presented as current hardware.
- The firmware README still includes R703 in current test instructions in at least one place.
- The GPIO names in `config.h` still provide `PIN_R703_*` and `R703_BAUD_RATE` aliases, which are obsolete compatibility clutter with no current source use.
- Build guides sometimes state exact vendor-family touch/USB/jumper information more strongly than current unit verification warrants.
- `docs/requirements-traceability.md` and the backend source correctly distinguish implemented software behavior from unbuilt firmware/UI features; keep that distinction.

## H. Security and credential handling

- Source config uses empty defaults; `local_config.example.h` contains placeholders/empty strings only, and the real local config path is ignored.
- Backend settings and device auth are implemented, and `.env` files are ignored except `.env.example`.
- No obvious committed private key or live credential was found in the basic tracked-source scan. This is a practical source review, not a formal secret scanner or security certification.
- The diagnostic prints packet bytes/parameters but does not intentionally print credentials or biometric payloads. Production serial logs must not emit names, tokens, fingerprint images, or templates.
- Hardware/API transport and demo-network restrictions are adequately flagged in docs, though broader security verification remains planned.

## I. What works, incomplete, obsolete, and uncertain

### Works / verified by available evidence

- Existing Git history/remote and project structure are intact.
- PlatformIO current firmware build passes.
- Backend tests pass in the project virtual environment (10 passed).
- Backend vertical slice and schema are implemented and test-covered as software.
- Existing R307S UART diagnostic is bounded and read-only; it builds as part of the firmware.
- ESP32 upload/serial and current diagnostic runtime are reported by owner/history; not re-executed in this audit.

### Partially complete

- R307S hardware path is physically assembled per current user report and probes have been attempted, but there is no valid sensor ACK and supply/logic levels have not been measured.
- Firmware config and an interface sketch exist, but there is no actual sensor abstraction implementation or attendance state machine.
- Hardware procedures and R307S investigative notes exist, but no systematic isolated test firmware suite exists.
- Backend works for a vertical slice; there is no dashboard or firmware integration.

### Not started / not implemented

- Individual environments for core, loopback, I2C, OLED, RTC, LEDs, buzzer, Wi-Fi, HTTP, JSON, storage, and reset tests.
- Integration test firmwares.
- Production attendance firmware, enrollment/matching state flow, RTC validation, offline LittleFS queue, HTTP client/retry, dashboard, and end-to-end integration.
- Physical test evidence for OLED/RTC/indicators/network or R307S enrollment/matching.

### Obsolete

- R703 migration references and AS608 selection records are historical only; do not remove ADR history, but clearly label superseded status.
- GPIO16/17 sensor wiring is stale for current 32/33 bench setup.
- Any statement that R307S is definitely dead, powered correctly, electrically safe, or has a verified six-wire mapping is unsupported by current evidence.

### Software uncertainties

- ESP32 build environment compiler flags and library pins are inherited bootstrap choices; multi-environment dependency filter behavior must be validated.
- PlatformIO source filtering must ensure exactly one firmware `setup()/loop()` entry point per selected environment.
- Sensor protocol behavior and exact hardware revision remain unverified because no valid R307S response exists.
- RTC invalid-time behavior and queue durability have no implementation yet.

## Previous handoff milestone: test infrastructure (2026-10-02)

After the read-only audit and architecture proposal, this task added:

- `docs/esp32-pin-map.md` and current-state/safety/test architecture documents linked below.
- Independent PlatformIO builds for 14 component diagnostics and 9 integration cases, plus ESP32 UART1 and UART2 loopback variants (25 test environments total).
- A modular runtime skeleton with explicit state vocabulary, display/RTC/indicator services and R307S probe/match wrapper. Attendance submission, enrollment workflow, and durable offline queue intentionally remain unimplemented.
- Updates to the pin map/config and previously stale R307S connection/GPIO documentation and Obsidian handoff/tracker.
- The shared test reporter distinguishes PASS/FAIL/NOT EXECUTED/UNVERIFIED; OLED and output tests stay UNVERIFIED until a person confirms the physical result, and skipped optional checks cannot produce an overall PASS.

Verification after the changes:

- Firmware component/integration matrix: **25/25 environments compile and link**; `production` and backward-compatible `esp32dev` also build. These are build-only results, not hardware passes. An Espressif Arduino framework UART compiler warning remains in framework source.
- Backend suite: **10 passed** using `backend/.venv/Scripts/python.exe -m pytest tests -q`.
- No firmware upload, physical peripheral test, sensor voltage/current measurement, or attendance network POST was performed here.
- Runtime result remains a skeleton, not an attendance system: it does not create/send/queue attendance events.

New authoritative follow-up documents: `docs/esp32-pin-map.md`, `docs/hardware-test-plan.md`, `docs/component-tests.md`, `docs/integration-tests.md`, `docs/production-firmware.md`, `docs/failure-modes.md`, `docs/power-and-safety.md`, and `docs/next-steps.md`.

## Production implementation follow-up (2026-10-02)

The active implementation phase has superseded the historical “runtime skeleton” status above. It added a modular production path in `firmware/src/app/`, `hardware/`, `network/`, and `storage/`: sensor inventory/search and explicit two-capture enrollment; operator-set DS3231 local time; generic OLED/indicator states; UUIDv4 event generation; CRC32 JSONL journal with torn-tail recovery, bounded pending count/size, acknowledgements and compaction; Wi-Fi reconnect; device bearer-authenticated attendance POST; and chronological offline replay. Enrollment completion intent is persisted in NVS and retried. The R307S read-only diagnostic and every standalone test environment remain intact.

The implementation follows the existing API schema and its idempotency/duplicate policy. It stores only slot/event/time/sync metadata; no image/template or student name is included in a firmware request or local queue. Local HTTP remains demonstration-only because the bearer token is not encrypted in transit. The queue itself is not encrypted and fails closed rather than formatting or overwriting when unavailable/full/corrupt.

Added assembly, breadboard, software setup and science-fair setup guides. The breadboard drawing is explicitly recommended rather than a reconstruction of a missing photograph or exact board variant. `docs/final-pin-map.md` is the single current GPIO map; `docs/esp32-pin-map.md` is retained as a navigation redirect.

**Verification boundary:** production/compatibility compile and backend tests can establish software evidence only. No firmware flash or physical test was performed in this phase. R307S rail/TX voltage, exact board mapping/jumper, health, OLED/RTC/LED/buzzer operation, LittleFS behavior under actual reset, Wi-Fi/API integration, sensor enrollment/matching, and full attendance flow remain unverified. The owner-reported zero-byte sensor result remains unresolved and is not proof of a dead module.

## J. Recommended implementation order

1. Keep the read-only R307S diagnostic intact; synchronize source-of-truth pin/current-state docs and publish a pin map based on actual 32/33 wiring plus ESP32 restrictions.
2. Add shared test-result formatting and independent PlatformIO environments, beginning with core and physical loopback (no sensor dependency), then I2C/OLED/RTC, GPIO/actuators, R307S, Wi-Fi/backend, JSON/storage, and reset diagnostics.
3. Build every software-only environment; document physical prerequisites and report **NOT EXECUTED / UNVERIFIED** until run on hardware.
4. Add integration environments with explicit wiring/prerequisites and no fabricated pass results.
5. Add production modules/state machine only after diagnostic environments compile independently; gracefully represent absent peripherals, avoid fake timestamps, and retain R307S unavailability as an explicit state.
6. Implement backend client only from `backend/app/schemas.py`, `backend/app/auth.py`, `docs/api-plan.md`, and `docs/requirements.md`; use isolated synthetic local test mode.
7. Run firmware builds plus backend tests, check docs/Canvas and Git diff. Leave commits/pushes to the owner.

## Audit evidence references

- Current code: `firmware/src/main.cpp`, `firmware/src/r307s_uart_diag.cpp`, `firmware/include/config.h`, `firmware/platformio.ini`.
- R307S notes: `docs/r307s-hardware-research.md`, `docs/r307s-next-session.md`, `docs/r307s-test-matrix.md`, `docs/r307s-usb-test.md`.
- Older conflicting state: `AI_CONTEXT.md`, `docs/r307s-integration-plan.md`, `docs/wiring.md`, `hardware/pinout.md`, `hardware/test-plan.md`, Obsidian TODO/Decision Log/build guide.
- Backend contract: `backend/app/main.py`, `backend/app/schemas.py`, `backend/app/auth.py`, `backend/tests/`.
- GPIO references: [Espressif ESP32 datasheet](https://documentation.espressif.com/esp32_datasheet_en.pdf?hkey=EF798316E3902B6ED9A73243A3159BB0), [ESP32-WROOM-32 datasheet](https://documentation.espressif.com/esp32-wroom-32_datasheet_en.html).
- Sensor-family references: [R307S quick-start](https://www.mantech.co.za/Datasheets/Products/md0652-240817c.pdf), [R307 family datasheet](https://www.mantech.co.za/datasheets/products/MD0652-240817B.pdf). Exact module-revision behavior remains subject to unit inspection.


## Final verification update (2026-10-02)

After production implementation, production and compatibility sp32dev both build. Each of the 25 component/integration environments builds and links. Backend suite: 10 tests passed using the repository virtual environment. Markdown relative-link and Canvas JSON/file-reference checks passed in this work session. No firmware was uploaded and no physical hardware test was executed. The build evidence establishes compile/link only; the next engineering step is safe electrical measurement and isolated physical verification before exercising production enrollment or attendance.
