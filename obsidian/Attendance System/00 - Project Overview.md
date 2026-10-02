---
type: project-navigation
status: IN PROGRESS
updated: 2026-09-29
---

# Biometric School Attendance System — Project Home

Welcome to the project workspace for the **local-first Biometric School Attendance demonstrator**. Open the `obsidian/` directory as the Obsidian vault. The root `.obsidian/` directory is separate local app configuration; source, plans, configuration and tests remain in their repository directories.

> [!NOTE]
> **Current Status:** `IN PROGRESS` — production attendance/enrollment/queue/API firmware implemented and builds; backend API tests pass; R307S owner report is 0 UART bytes with power/logic unmeasured; component/full hardware integration and dashboard remain pending
> **Exhibition Date:** 09 October 2026
> **Target Platform:** ESP32-WROOM-32 + R307S + FastAPI + SQLite

---

## 📌 Project Navigation Index

- [[AI Development Guide|AI / contributor operating guide]] · [[AI Project Handoff|Current project handoff]] · [[Decision Log|Architecture decision log]] · [[Milestones|Milestone status]]
- [R307S Integration Plan](../../docs/r307s-integration-plan.md) · [[18 - Complete Build Guide|Human build guide]]

* 📋 **Specifications & Goals:**
  * [[01 - Requirements|System Requirements (Functional & Non-Functional)]]
  * [[02 - Architecture|System Architecture & Topology]]
  * [[11 - Privacy & Security|Biometric Privacy & Legal Disclaimers]]
  * [Requirements-to-test traceability](../../docs/requirements-traceability.md)

* ⚡ **Hardware & Procurement:**
  * [[03 - Hardware|Component Specifications & Datasheets]]
  * [[04 - Bill of Materials|Bill of Materials & Indian Pricing]]
  * [[16 - Purchase Checklist|Physical Hardware Purchase Checklist]]
  * Wiring schematics & pin mapping details are documented in the main docs.

* 💻 **Software & Engineering Plans:**
  * [[05 - Software Stack|Technology Stack Selection & Rationale]]
  * [[06 - Firmware Plan|ESP32 Firmware Plan]]
  * [[07 - Backend Plan|FastAPI Backend & Service Architecture]]
  * [[08 - Database Plan|SQLite3 Relational Schema & WAL Mode]]
  * [[09 - API Plan|REST API Endpoint Specifications]]
  * [[10 - AI Plan|Optional Read-Only Tool-Calling AI Adapter]]

* 🧪 **Testing, Timeline & Execution:**
  * [[12 - Testing Plan|Hardware & Software Test Matrix]]
  * [[13 - GitHub & Development|Git Milestones & Issue Management]]
  * [[14 - Science Fair|Exhibition Master Plan & Judge Strategy]]
  * [[15 - Timeline|15-Day Science Fair Critical Path Timeline]]
  * [[TODO|Master Project Task & Defect Tracker]]
  * [[17 - Future Ideas|Future Roadmap & Expansion Concepts]]

* 🗺️ **Visual Canvas:**
  * [[Architecture.canvas|Open Interactive Architecture Canvas]]

---

## System Status Dashboard

| Area | Status | Evidence / remaining work |
| --- | --- | --- |
| Obsidian vault under `obsidian/` and AI handoff | VERIFIED | Guide, handoff, decision log, task tracker and Canvas; root `.obsidian/` is separate local configuration |
| Git baseline / GitHub remote / CLI auth | VERIFIED | Preserved baseline and configured `origin/main`; see current hash/state in [[AI Project Handoff]] |
| Python environment and SQLite smoke check | VERIFIED | `backend/test_env.py` passed in `backend/.venv` |
| SQLite schema v1 migration | VERIFIED | Six temporary-database migration/constraint tests passed |
| Firmware build matrix | VERIFIED (build only) | Production, compatibility and 25 component/integration environments compile; no firmware was flashed in this work |
| FastAPI vertical slice | VERIFIED (software tests) | Health, admin student lifecycle, enrollment assignment/completion, attendance ingestion; remaining routes tracked in [[TODO]] |
| Attendance event runtime and dashboard | IMPLEMENTED / PLANNED | Firmware event pipeline/queue/API client exists but is not physically verified; browser UI is not implemented |
| Procurement / physical hardware | IN PROGRESS / BLOCKED ON BENCH | R307S fingerprint sensor in hand; owner-reported harness wiring and zero-byte diagnostic; PCB pin mapping, supply and signal levels UNVERIFIED — REQUIRES MULTIMETER / board inspection |
| Integrated science-fair demo | PLANNED | Requires application work and hardware evidence |

> Dates remain targets. Hardware order/arrival is unconfirmed. Product features are planned unless their implementation and evidence are explicitly recorded. Use [[TODO|the authoritative task tracker]], [[Milestones]], and the [canonical project plan](../../docs/project-plan.md).
