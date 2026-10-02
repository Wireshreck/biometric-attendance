---
type: project
area: project
status: active
tags:
  - project
  - entry-point
---
# Biometric School Attendance System

> **Open-source, local-first biometric attendance demonstrator for schools.**
> Core implementation: ESP32 + R307S fingerprint module + FastAPI + SQLite. Production firmware and backend software compile/test, but the R307S currently returns no UART response in owner-reported diagnostics and has unmeasured supply/logic levels. Full physical attendance operation is not verified.
> Science Fair Exhibition: **9 October 2026**

---

## Project Status: `IN PROGRESS`

| Milestone | Status |
| :--- | :---: |
| Python/backend environment smoke check | VERIFIED |
| Git history | VERIFIED (baseline preserved; branch tracks configured `origin/main`; see `git log` for current milestone) |
| GitHub and CI | VERIFIED locally; Actions run `36148997541` passed firmware build and backend smoke/tests on commit `06f7713` |
| Hardware selection and BOM | IMPLEMENTED (planning docs; procurement unconfirmed) |
| Purchase/delivery confirmation | BLOCKED (owner status unknown) |
| Firmware component/integration test builds | VERIFIED (25 test environments compile/link; hardware execution NEEDS HARDWARE) |
| Production firmware | IMPLEMENTED (matching/enrollment, RTC gate, journal, Wi-Fi/API); physical operation NEEDS HARDWARE |
| Backend API vertical slice | VERIFIED (10 software tests; physical integration unverified) |
| Remaining API (reports/CSV/SSE/device lifecycle) | PLANNED |
| Obsidian project workspace | VERIFIED (repository root is the vault; `00 - Vault Hub.md`, 10 area hubs and 12 canvases; see [00 - Vault Hub](00%20-%20Vault%20Hub.md)) |
| Architecture documentation | VERIFIED (dashboard remains planned; firmware workflows are implemented) |
| Hardware bench tests | NEEDS HARDWARE |
| Attendance event recording | IMPLEMENTED in firmware/backend; end-to-end NEEDS HARDWARE |
| Database schema v1 migration | VERIFIED (6 temporary-database migration/constraint tests passed) |
| Dashboard | PLANNED |
| End-to-end integration | NEEDS HARDWARE; no physical pass evidence |
| Science-fair demo | PLANNED |

---

## 🗓️ Science Fair Countdown

Dates below are planning targets from the project timeline, not confirmed purchases, delivery commitments, or completed milestones.

| Date | Deadline |
| :--- | :--- |
| **Sep 25** | ⚠️ **Hardware order placed by 12:00 noon** |
| **Sep 28** | Hardware arrives — bench bring-up |
| **Oct 01** | Standalone biometric prototype |
| **Oct 04** | First working end-to-end demo |
| **Oct 06** | Testing & code freeze |
| **Oct 08** | Final backup & presentation rehearsal |
| **Oct 09** | 🏆 **Science Fair** |

---

## 🔩 System Architecture

```
┌─────────────────────────────────┐
│     Edge Terminal (ESP32)       │
│  R307S ─ UART ─ ESP32 ─ OLED   │
│              │                  │
│           DS3231 RTC            │
│    Green/Red LED  Buzzer        │
│    LittleFS offline journal     │
└──────────────┬──────────────────┘
               │ Wi-Fi (2.4 GHz)
               ▼
┌─────────────────────────────────┐
│  Local Laptop (Python server)   │
│  FastAPI ──► SQLite3 (WAL)      │
│  Web Dashboard (planned)        │
└──────────────┬──────────────────┘
               │ Optional
               ▼
┌─────────────────────────────────┐
│  Local LLM Tool-Calling Layer   │
│  (Read-only, offline, Ollama)   │
└─────────────────────────────────┘
```

Firmware creates attendance events, queues them before transmission, and retries using stable UUIDs. R307S response and physical integration remain unverified, and the browser dashboard remains planned. See [firmware status](firmware/README.md), [hardware test environments](docs/component-tests.md), and [production behavior](docs/production-firmware.md).

---

## 🔑 Key Design Principles

- **Local-first design:** API, database and device client can run on a private local network; public-network deployment is unsupported.
- **Biometric minimization:** Firmware sends only template slot, event UUID, timestamp and synchronization state; no fingerprint image/template is sent.
- **Offline resilience:** LittleFS journal and replay logic are implemented; persistence across actual power loss needs hardware verification.
- **Open source:** MIT License — free for any school to use and modify.
- **Affordable target:** Current planning envelope is ~₹2,399 before any unpriced conditional RTC cell; verify the actual cart.

---

## 📁 Repository Structure

```
biometric-attendance/
├── firmware/            ESP32 source code (PlatformIO / Arduino)
├── backend/             FastAPI + SQLite backend (Python 3.13)
├── frontend/            Dashboard placeholder (UI not implemented)
├── hardware/            Pinout, bench test plans
├── docs/                Project documentation
├── diagrams/            Mermaid diagrams
├── scripts/             Automation and backup scripts
├── presentation/        Demo script, judge Q&A, outline
├── 00 - Vault Hub.md    Vault entrance (repository root is the Obsidian vault)
├── 00 - Master Canvas.canvas
├── 01..10 - *Lab/        Area hubs + Canvases, plus migrated TODO / Milestones / Decision Log
├── .obsidian/            Vault configuration (app, graph, workspace)
└── .github/             Issue templates, CI workflows
```

---

## 🚀 Current Development Checks

These commands build firmware and run implemented backend tests. They do **not** flash hardware or demonstrate attendance recording; use [component-test instructions](docs/component-tests.md) for isolated physical diagnostics.

```powershell
# Build production firmware (build only)
pio run -d firmware -e production

# Build read-only R307S diagnostic; do not upload before the electrical safety gate
pio run -d firmware -e r307s

# Run backend API/database tests with project dependencies
Push-Location backend
try { & .\.venv\Scripts\python.exe -m pytest tests -q } finally { Pop-Location }
```

---

## 📖 Documentation Index

**Open the repository root as the Obsidian vault.** Start at [`00 - Vault Hub.md`](00%20-%20Vault%20Hub.md), then open [`00 - Master Canvas.canvas`](00%20-%20Master%20Canvas.canvas) for the facility map. The AI operating notes are the [development guide](08%20-%20Documentation%20Library/AI%20Development%20Guide.md) and the [handoff](10%20-%20Workshop/AI%20Project%20Handoff.md). Vault notes are navigation and status pages; every technical specification remains authoritative in `docs/`, `firmware/`, `backend/`, `hardware/` and `diagrams/`.

| Document | Description |
| :--- | :--- |
| [`docs/project-plan.md`](docs/project-plan.md) | Overall project scope and WBS |
| [`docs/requirements.md`](docs/requirements.md) | Functional & non-functional requirements |
| [`docs/requirements-traceability.md`](docs/requirements-traceability.md) | Requirement priorities, status, component and planned verification mapping |
| [`docs/architecture.md`](docs/architecture.md) | System architecture & topology |
| [`docs/hardware.md`](docs/hardware.md) | Component datasheets & specs |
| [`docs/bill-of-materials.md`](docs/bill-of-materials.md) | Full BOM with Indian pricing |
| [`docs/final-pin-map.md`](docs/final-pin-map.md) | Authoritative firmware GPIO map and electrical gates |
| [`docs/COMPLETE-BEGINNER-ASSEMBLY-GUIDE.md`](docs/COMPLETE-BEGINNER-ASSEMBLY-GUIDE.md) | Beginner physical assembly and inspection |
| [`docs/complete-breadboard-layout.md`](docs/complete-breadboard-layout.md) | Recommended coordinate layout; exact board dimensions unverified |
| [`docs/COMPLETE-SOFTWARE-SETUP.md`](docs/COMPLETE-SOFTWARE-SETUP.md) | Windows setup, backend, build and upload |
| [`docs/SCIENCE-FAIR-SETUP.md`](docs/SCIENCE-FAIR-SETUP.md) | Packing, startup, demonstration and recovery |
| [`docs/software-stack.md`](docs/software-stack.md) | Technology selection rationale |
| [`docs/database-plan.md`](docs/database-plan.md) | SQLite schema design |
| [`docs/api-plan.md`](docs/api-plan.md) | REST API endpoint specification |
| [`docs/privacy-security.md`](docs/privacy-security.md) | Biometric privacy architecture |
| [`docs/science-fair-timeline.md`](docs/science-fair-timeline.md) | 15-day development schedule |
| [`docs/purchase-checklist.md`](docs/purchase-checklist.md) | Hardware purchase checklist |
| [`docs/github-setup.md`](docs/github-setup.md) | GitHub authentication guide |

---

## ⚡ Hardware Bill of Materials Summary

| Component | Est. Price |
| :--- | :---: |
| ESP32-WROOM-32 DevKit V1 | ₹349 |
| R307S Fingerprint Module (acquired; electrical state unverified) | record from receipt |
| SSD1306 0.96" I2C OLED | ₹163 (listing, ex GST) |
| DS3231 High Precision RTC | ₹189 |
| Active Buzzer, LEDs, Resistors | ₹105 |
| Breadboard + Jumper Wires + USB Cable | ₹344 |
| **Planning estimate incl. tax/shipping reserve** | **~₹2,399 (verify current cart; not a quote)** |

---

## 📄 License

MIT License — See [`LICENSE`](LICENSE)

## 🤝 Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md)

## 🔒 Security

See [`SECURITY.md`](SECURITY.md) and [`docs/privacy-security.md`](docs/privacy-security.md)
