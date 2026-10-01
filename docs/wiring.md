# Provisional Wiring and Electrical Bring-Up

**Status: NOT BENCH VERIFIED.**  
**MCU:** ESP32-WROOM-32 DevKit V1 (**Verified on COM3 at 115200 baud**)  
**Fingerprint Sensor:** R307S Optical Fingerprint Sensor (**Acquired; NOT YET CONNECTED OR POWERED**)  
**Display & RTC:** SSD1306 0.96" I2C OLED + DS3231 Precision RTC (Shared I2C bus)  

> [!CAUTION]
> **ELECTRICAL SAFETY WARNING:**
> - ESP32 GPIO pins operate at **3.3V logic levels** and are **NOT 5V tolerant**. Connecting a 5V signal will permanently destroy the ESP32 silicon.
> - The R307S supply voltage and UART TX logic level are **UNVERIFIED — HARDWARE VERIFICATION REQUIRED**.
> - Observed harness wire colors (**1: Red, 2: Black, 3: Yellow, 4: Green, 5: Blue, 6: White**) are an observation only. Never assume wire colors prove the pinout.
> - Disconnect USB power before modifying any breadboard connection.

---

## 1. Provisional Signal Map

| Peripheral Signal | ESP32 Connection | Electrical Level | Notes / Verification Actions |
| :--- | :--- | :---: | :--- |
| **R307S TXD -> ESP UART RX** | **GPIO 16** (provisional) | 3.3V Max In | **UNVERIFIED — TO VERIFY:** Measure R307S TX open-circuit voltage with multimeter before connecting; must be $\le 3.3\text{V}$. If 5V, install level shifter. |
| **ESP UART TX -> R307S RXD** | **GPIO 17** (provisional) | 3.3V Out | **UNVERIFIED — TO VERIFY:** Confirm R307S accepts 3.3V logic input on RXD (standard R307S inputs accept 3.3V TTL). |
| **R307S VCC** | **VIN (5V Rail)** or **3V3 Rail** | 4.2V–6V or 3.3V | **UNVERIFIED — TO VERIFY:** Inspect module silkscreen/regulator. Do not apply 5V to a 3.3V-only pin. |
| **R307S GND** | **ESP32 GND** | Ground Reference | **MANDATORY COMMON GROUND** with ESP32. |
| **OLED SDA & RTC SDA** | **GPIO 21** | 3.3V I2C Bus | Shared I2C; power breakouts at 3.3V so pull-ups do not raise bus above ESP32 logic. |
| **OLED SCL & RTC SCL** | **GPIO 22** | 3.3V I2C Bus | Shared I2C; start bus at 100 kHz standard mode. |
| **Green LED Anode** | **GPIO 18** | 3.3V Out | Series 330Ω–1kΩ current-limiting resistor to GND. |
| **Red LED Anode** | **GPIO 19** | 3.3V Out | Series 330Ω–1kΩ current-limiting resistor to GND. |
| **Active Buzzer Signal** | **GPIO 23** | 3.3V Out | Module must have an onboard NPN driver transistor; never drive buzzer coil directly from GPIO. |
| **All Grounds** | **Common Ground Bus** | 0V Reference | Common reference rail required for UART, I2C, and all actuators. |

---

## 2. R307S Observed 6-Wire Cable Harness Reference

| Cable Position | Observed Wire Color | Candidate Function | Verification Status & Action |
| :---: | :---: | :--- | :---: |
| **1** | **Red** | $V_{CC}$ (Power: 4.2V–6V or 3.3V) | **UNVERIFIED** — Trace to regulator input or silkscreen |
| **2** | **Black** | $GND$ (Ground) | **UNVERIFIED** — Verify continuity to module ground plane |
| **3** | **Yellow** | $TXD$ (Serial Output from sensor) | **UNVERIFIED** — Measure voltage relative to GND ($\le 3.3\text{V}$) |
| **4** | **Green** | $RXD$ (Serial Input to sensor) | **UNVERIFIED** — Verify input logic level compatibility |
| **5** | **Blue** | $TOUCH$ (Finger detect output) | **UNVERIFIED** — Leave unconnected during Phase 2 bring-up |
| **6** | **White** | $3.3V$ / $WAKE$ / $NC$ | **UNVERIFIED** — Leave unconnected during Phase 2 bring-up |

---

## 3. Safe Power-Up and Verification Order

1. **Physical Inspection (Bench Gate HW-01):** With USB disconnected, examine the R307S connector. Use a multimeter in continuity mode to identify the GND pin on the module. Confirm whether the module has an onboard 3.3V regulator (indicating 5V nominal input) or operates directly at 3.3V.
2. **ESP32 Standalone Check (Phase 0):** **COMPLETED.** The ESP32 boots and communicates cleanly over USB COM3 at 115200 baud.
3. **Sensor Supply & Logic Check (Phase 3):** Power the R307S with its verified supply rail (VIN or 3V3) with GND connected. Measure the voltage on the sensor's TX line.
   - If $V_{TX} \approx 3.3\text{V}$: Safe for direct connection to ESP32 GPIO 16.
   - If $V_{TX} \approx 5.0\text{V}$: **DO NOT CONNECT TO ESP32.** Insert a 2-resistor voltage divider (e.g., 2kΩ / 1kΩ) or a logic level shifter.
4. **UART Connection (Phase 4):** Cross-connect the verified data lines:
   - Sensor `TXD` $\rightarrow$ ESP32 `GPIO 16` (`RX2`).
   - Sensor `RXD` $\leftarrow$ ESP32 `GPIO 17` (`TX2`).
5. **I2C Bus Connection:** Connect OLED and RTC to GPIO 21 (SDA) and GPIO 22 (SCL). Power both from ESP32 3V3 rail. Verify that breakout pull-up resistors connect to 3.3V.
6. **Actuators:** Connect Green LED (GPIO 18) and Red LED (GPIO 19) through series 330Ω resistors. Connect Active Buzzer (GPIO 23) module.
7. **RTC Backup Cell:** Inspect the DS3231 breakout charging circuit before inserting a primary CR2032 lithium coin cell to avoid dangerous trickle charging.
