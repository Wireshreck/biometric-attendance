---
type: project-navigation
status: IN PROGRESS
updated: 2026-09-29
---

# Biometric School Attendance System — Project Home

Welcome to the project workspace for the **local-first Biometric School Attendance demonstrator**. Open the repository root as the Obsidian vault so this workspace can navigate the actual source, plans, configuration, and tests.

> [!NOTE]
> **Current Status:** `IN PROGRESS` — ESP32 bring-up verified on COM3; R307S integration plan prepared; sensor NOT yet connected or powered; backend API vertical slice software-verified; dashboard and hardware integration pending
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
| Repository-root Obsidian workspace and AI handoff | VERIFIED | Guide, handoff, decision log, task tracker and file-backed Canvas |
| Git baseline / GitHub remote / CLI auth | VERIFIED | Preserved baseline and configured `origin/main`; see current hash/state in [[AI Project Handoff]] |
| Python environment and SQLite smoke check | VERIFIED | `backend/test_env.py` passed in `backend/.venv` |
| SQLite schema v1 migration | VERIFIED | Six temporary-database migration/constraint tests passed |
| Firmware toolchain & serial test | VERIFIED (Phase 0 PASSED) | ESP32 serial communication confirmed on COM3 at 115200 baud; firmware compiles cleanly |
| FastAPI vertical slice | VERIFIED (software tests) | Health, admin student lifecycle, enrollment assignment/completion, attendance ingestion; remaining routes tracked in [[TODO]] |
| Attendance firmware and dashboard | PLANNED | R307S integration plan prepared; sensor driver, browser UI and full event pipeline pending |
| Procurement / physical hardware | IN PROGRESS / BLOCKED ON BENCH | R307S fingerprint sensor in hand with 6-wire harness (Red, Black, Yellow, Green, Blue, White); pinout & electrical ratings UNVERIFIED — HARDWARE VERIFICATION REQUIRED; sensor NOT yet connected |
| Integrated science-fair demo | PLANNED | Requires application work and hardware evidence |

> Dates remain targets. Hardware order/arrival is unconfirmed. Product features are planned unless their implementation and evidence are explicitly recorded. Use [[TODO|the authoritative task tracker]], [[Milestones]], and the [canonical project plan](../../docs/project-plan.md).
