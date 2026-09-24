# Bill of Materials (BOM) & Hardware Specifications

**Project:** Biometric School Attendance System  
**Pricing Currency:** Indian Rupee (INR / ₹)  
**Price review:** 24 September 2026 (online listings; not a purchase quote)  
**Supplier Region:** India (ElectronicsComp.com, Robu.in, Amazon.in)  

> [!NOTE]
> Prices and stock change. The AS608 (₹799), DS3231 (₹189), and 4-pin SSD1306 OLED (₹163) were visible in ElectronicsComp listings on 24 September 2026, before GST; shipping and local-store prices are not included. Other values are carry-forward planning estimates and must be checked at purchase. See the [phone-friendly purchase checklist](purchase-checklist.md). Do not treat prices as guaranteed or place an order based only on this plan.

---

## 1. Required Components (Core Minimum Viable System)

| Component | Exact Recommended Part | Qty | Purpose | Voltage | Interface | Approx. Price (INR) | Reputable Purchase Source / Direct Link | Required? |
| :--- | :--- | :---: | :--- | :---: | :---: | :---: | :--- | :---: |
| **Microcontroller** | ESP32-WROOM-32 DevKit V1 (30-pin or 38-pin, CP2102 or CH340) | 1 | System CPU, Wi-Fi client, local event coordinator | 3.3V Logic / 5V USB | Wi-Fi / UART / I2C / GPIO | ₹349.00 | [ElectronicsComp - ESP32 Dev Board](https://www.electronicscomp.com/esp32-development-board) | **YES** |
| **Fingerprint Sensor** | AS608 Optical Fingerprint Module (verify connector supplied) | 1 | Sensor-side capture/matching | Selected listing states 3.3V supply; verify exact module and UART level | UART (default baud must be confirmed) | ₹799 listing, ex GST | [ElectronicsComp AS608 EC-5060](https://www.electronicscomp.com/sensors-module/sensors/as608-optical-fingerprint-sensor-module?limit=75) | **YES** |
| **OLED Display** | 0.96 inch SSD1306 128×64 Monochrome OLED, 4-pin I2C | 1 | Local user feedback | 3.3V signal/power when powered from 3V3 | I2C (commonly 0x3C; verify) | ₹163 listing, ex GST | [ElectronicsComp 4-pin SSD1306 OLED](https://www.electronicscomp.com/display-devices/0.96-inch-i2c-iic-128x64-oled-display-module-4-pin-blue-color?limit=100) | **YES** |
| **Real-Time Clock** | DS3231 I2C breakout; verify battery holder/charging design | 1 | Battery-backed offline timekeeping | Power at 3V3; verify exact breakout/pull-ups | I2C (0x68) | ₹189 listing, ex GST | [ElectronicsComp DS3231 module](https://www.electronicscomp.com/ds3231-rtc-module-india) | **YES** |
| **Buzzer** | 5V Active Buzzer Module (with onboard transistor driver) | 1 | Audible transaction feedback (success chime / error buzz) | 3.3V – 5.0V | GPIO (Digital High/Low) | ₹35.00 | [ElectronicsComp - 5V Active Buzzer Module](https://www.electronicscomp.com/5v-active-buzzer-module) | **YES** |
| **Green LED** | 5mm Diffused Green LED (Pack of 5) | 1 pk | Visual indicator for successful fingerprint verification | 2.1V – 2.4V | GPIO (via 330Ω resistor) | ₹25.00 | [ElectronicsComp - 5mm Green LED 5pcs](https://www.electronicscomp.com/5mm-green-led) | **YES** |
| **Red LED** | 5mm Diffused Red LED (Pack of 5) | 1 pk | Visual indicator for unrecognized finger or network error | 1.8V – 2.0V | GPIO (via 330Ω resistor) | ₹25.00 | [ElectronicsComp - 5mm Red LED 5pcs](https://www.electronicscomp.com/5mm-red-led) | **YES** |
| **Current Limiting Resistors** | 330Ω 1/4W Metal Film Resistors (Pack of 20) | 1 pk | Protect LEDs and ESP32 GPIOs from overcurrent | Pass-through | Passive | ₹20.00 | [ElectronicsComp - 330 Ohm Resistors](https://www.electronicscomp.com/330-ohm-resistor-pack) | **YES** |
| **Prototyping Board** | MB-102 830-Point Solderless Breadboard | 1 | Solderless component wiring and power rail distribution | Up to 30V | 2.54mm pitch | ₹125.00 | [ElectronicsComp - MB-102 Breadboard](https://www.electronicscomp.com/mb-102-830-points-solderless-breadboard) | **YES** |
| **Jumper Wires (M-M)** | 40-pin Male-to-Male DuPont Jumper Cables (20cm) | 1 pk | Connecting ESP32, LEDs, and buzzer on breadboard | 30V max | 2.54mm DuPont | ₹65.00 | [ElectronicsComp - 40pcs M-to-M Wires](https://www.electronicscomp.com/40-pcs-male-to-male-jumper-wire-20cm) | **YES** |
| **Jumper Wires (M-F)** | 40-pin Male-to-Female DuPont Jumper Cables (20cm) | 1 pk | Connecting OLED, RTC, and AS608 to ESP32/breadboard | 30V max | 2.54mm DuPont | ₹65.00 | [ElectronicsComp - 40pcs M-to-F Wires](https://www.electronicscomp.com/40-pcs-male-to-female-jumper-wire-20cm) | **YES** |
| **USB Data Cable** | High-Quality Micro-USB Data & Power Cable (1.0 meter) | 1 | 5V power supply to ESP32 and serial programming | 5V / 2A | Micro-USB to USB-A | ₹89.00 | [ElectronicsComp - Micro USB Cable](https://www.electronicscomp.com/micro-usb-cable-1m) | **YES** |
| **RTC Backup Cell** | Exact type specified by the selected DS3231 board; buy only after checking its charge circuit | 1 | RTC backup | Board-dependent | Battery | Price not set | Buy matched to exact module after inspection | **CONDITIONAL** |

---

## 2. Recommended Components (Presentation, Stability & Convenience)

| Component | Exact Recommended Part | Qty | Purpose | Approx. Price (INR) | Purchase Source |
| :--- | :--- | :---: | :--- | :---: | :--- |
| **Breadboard Power Supply** | MB-102 3.3V/5V Dual Power Supply Module | 1 | Dedicated clean power rails for sensor and displays | ₹110.00 | [ElectronicsComp - MB102 Power Module](https://www.electronicscomp.com/mb102-breadboard-power-supply-module) |
| **5V 2A USB Wall Adapter** | Standard 5V 2A USB Power Adapter | 1 | Reliable power source during live science fair presentation | ₹180.00 | [Robu.in - 5V 2A Adapter](https://robu.in/product/5v-2a-power-adapter/) |
| **Acrylic Mounting Stand** | Transparent Acrylic Base Plate or Project Box | 1 | Clean exhibition mounting for ESP32, sensor, and OLED | ₹199.00 | Local stationary / acrylic supplier |

---

## 3. Spares & Contingency Budget (Crucial for Science Fair)

| Component | Recommended Spare Part | Qty | Risk Mitigated | Approx. Price (INR) |
| :--- | :--- | :---: | :--- | :---: |
| **Backup ESP32** | ESP32-WROOM-32 DevKit V1 | 1 | ESD damage, blown GPIO, or failed USB port | ₹349.00 |
| **Spare AS608 Cable** | 6-pin 1.25mm/1.0mm JST ribbon cable | 1 | Broken ribbon crimp wire from repeated handling | ₹45.00 |
| **Spare OLED Display** | 0.96 inch SSD1306 I2C OLED | 1 | Cracked glass screen during transport to science fair | ₹188.00 |
| **Spare Buzzer & LEDs** | Pack of 5 buzzers & mixed LEDs | 1 | Burned out LED or buzzer lead fatigue | ₹60.00 |

---

## 4. Cost Breakdown & Budget Summary

| Category | Description | Total (INR) |
| :--- | :--- | :---: |
| **Core item estimate** | Listed item estimates (including current OLED listing); excludes battery, taxes, shipping | **~₹1,949.00** |
| **Tax/shipping reserve** | Planning allowance only; confirm actual cart/local store cost | **~₹450.00** |
| **Planning envelope** | Not a quote; conditional RTC cell may change cost | **~₹2,399.00** |
| **Recommended Accessories** | Dedicated power module, adapter, presentation mounting | **₹489.00** |
| **Recommended Spares (Contingency)** | 1 Spare ESP32, 1 Spare OLED, spare wiring | **₹642.00** |
| **Total Recommended Project Budget** | Core planning envelope + accessories + spares; estimates only | **₹3,530.00** |

---

## 5. Detailed Component Specifications & Constraints

### 1. ESP32-WROOM-32 DevKit V1
* **Core:** Dual-core Xtensa 32-bit LX6, 240 MHz, 520 KB SRAM, 4 MB Flash.
* **Wi-Fi:** 802.11 b/g/n (2.4 GHz).
* **Current Draw:** 80 mA typical idle; up to 240 mA during active Wi-Fi TX burst.
* **Logic Level:** Strictly 3.3V. **5V on GPIO will permanently damage the silicon.**
* **Pin Constraints:**
  - Pins 6–11 are connected to internal SPI flash memory. **Never connect external hardware to GPIO 6–11.**
  - Strapping pins: GPIO 0 (boot mode), GPIO 2 (download mode / onboard LED), GPIO 12 (flash voltage), GPIO 15 (silence boot messages).
  - Input-only pins: GPIO 34, 35, 36, 39 (no internal pull-up/down resistors; cannot output signals).

### 2. AS608 Optical Fingerprint Module
* **Optical Engine:** CMOS imaging array with green/blue illumination ring.
* **Resolution:** 500 DPI.
* **Storage Capacity:** Up to 120 or 300 fingerprint templates stored in onboard flash memory.
* **Privacy boundary:** Firmware is planned to request a match result/slot only. Do not request image/template transfer commands. Exact template properties are proprietary and unverified; do not claim mathematical irreversibility.
* **Electrical:** Selected retailer listing states a 3.3V module supply and <60mA draw; confirm the exact module manual/label and UART logic high before wiring. Power rating does not establish signal-level safety.
* **UART configuration candidate:** 57,600 bps (8-N-1) is configured as a provisional starting point; confirm the exact module default before use.

### 3. SSD1306 0.96" OLED Display
* **Resolution:** 128 × 64 pixels.
* **Driver IC:** SSD1306 with built-in charge pump.
* **Interface:** 4-pin I2C (`GND`, `VCC`, `SCL`, `SDA`).
* **I2C Address:** Default `0x3C` (selectable to `0x3D` via 0Ω solder resistor on back).
* **Current Draw:** ~20 mA with typical text display.

### 4. DS3231 High-Precision RTC
* **Oscillator:** Temperature-Compensated Crystal Oscillator (TCXO) with ±2 ppm accuracy (less than 1 minute drift per year).
* **Interface:** I2C (Address `0x68`). Shares the same I2C bus with SSD1306 without conflict.
* **Battery caution:** DS3231 breakout charge circuits vary. Never install a primary CR2032 in a board that can charge it. Identify the exact board circuit and use the specified rechargeable cell or a documented non-charging breakout. Do not modify charging components unless qualified and guided by the board documentation.
