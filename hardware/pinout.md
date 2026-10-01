# Hardware Pinout & GPIO Allocation Guide

**Target Controller:** ESP32-WROOM-32 DevKit V1 (Confirmed working on COM3)  
**Target Sensor:** R307S Optical Fingerprint Sensor  
**Status:** ESP32 SERIAL TEST PASSED · R307S UNVERIFIED (NOT YET CONNECTED OR POWERED)  

The provisional map and electrical safety checks are maintained in [docs/wiring.md](../docs/wiring.md) and [docs/r307s-integration-plan.md](../docs/r307s-integration-plan.md). Pin assignments for the R307S have **not** been physically verified. Do not treat sensor wire colors, breakout pull-ups, or supply/logic-voltage claims as verified until exact module labels/manuals are inspected.

---

## 1. Provisional ESP32 GPIO Assignment Table

| Function | ESP32 GPIO | Electrical Level | Verification Status | Notes |
| :--- | :---: | :---: | :---: | :--- |
| **USB Serial (Console)** | `GPIO 1 / 3` (UART0) | 3.3V Logic | **VERIFIED (PASSED)** | Confirmed working on **COM3** at 115200 baud |
| **R307S UART RX** | `GPIO 16` (U2_RXD) | 3.3V Max In | **UNVERIFIED (PROVISIONAL)** | Connects to R307S TXD after level verification ($\le 3.3\text{V}$) |
| **R307S UART TX** | `GPIO 17` (U2_TXD) | 3.3V Out | **UNVERIFIED (PROVISIONAL)** | Connects to R307S RXD |
| **OLED + RTC SDA** | `GPIO 21` (I2C SDA) | 3.3V Bus | **UNVERIFIED** | Shared I2C bus; requires 3.3V pull-ups |
| **OLED + RTC SCL** | `GPIO 22` (I2C SCL) | 3.3V Bus | **UNVERIFIED** | Shared I2C bus (100 kHz initial scan) |
| **Green LED (Match)** | `GPIO 18` | 3.3V Out | **UNVERIFIED** | Series 330Ω–1kΩ current-limiting resistor |
| **Red LED (Reject)** | `GPIO 19` | 3.3V Out | **UNVERIFIED** | Series 330Ω–1kΩ current-limiting resistor |
| **Active Buzzer** | `GPIO 23` | 3.3V Out | **UNVERIFIED** | Active buzzer module with NPN driver |

---

## 2. R307S Observed 6-Wire Cable Harness

> [!WARNING]
> **DO NOT ASSUME WIRE COLORS PROVE THE PINOUT.**
> The following order is an observational record of the user's cable harness only. It must be confirmed against the physical module connector before making connections.

| Cable Position | Observed Wire Color | Common R307/R307S Candidate Signal | Verification Status | Bench Verification Action |
| :---: | :---: | :--- | :---: | :--- |
| **Pin 1** | **Red** | Power Input ($V_{CC}$: 4.2V–6V or 3.3V) | **UNVERIFIED** | Trace to onboard LDO or silkscreen label |
| **Pin 2** | **Black** | Ground ($GND$) | **UNVERIFIED** | Multimeter continuity test to ground plane/shield |
| **Pin 3** | **Yellow** | Serial Data Out ($TXD$) | **UNVERIFIED** | Check open-circuit voltage relative to GND ($\le 3.3\text{V}$) |
| **Pin 4** | **Green** | Serial Data In ($RXD$) | **UNVERIFIED** | Verify logic level acceptance |
| **Pin 5** | **Blue** | Touch / Wakeup ($TOUCH$) | **UNVERIFIED** | Leave unconnected during initial UART testing |
| **Pin 6** | **White** | 3.3V Power / NC / Reserved | **UNVERIFIED** | Leave unconnected during initial UART testing |

---

## 3. Bootstrapping & Peripheral Pin Constraints

* **GPIO 0, 2, 12, 15:** Strapping pins. Left unconnected to prevent flash boot or voltage brownout issues.
* **GPIO 6–11:** Connected internally to the 4MB SPI Flash memory. **STRICTLY NOT CONNECTED**.
* **GPIO 34–39:** Input-only pins. Cannot output signals for LEDs, buzzer, or UART TX.
* **UART Routing:** On classic ESP32, UART2 pins are freely routable via the GPIO matrix. If GPIO 16/17 conflict with board-specific memory or traces, alternative pins (e.g., GPIO 25/26) can be configured in firmware.
