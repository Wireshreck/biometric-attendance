---
type: hardware
area: hardware
status: unverified
tags:
  - hardware
  - breadboard
  - assembly
---
# Recommended breadboard layout

**Status:** RECOMMENDED LAYOUT, not a record of the user's exact breadboard. This workspace has no recoverable breadboard/ESP32 photo or board revision. Use the generic coordinates below as a placement method; do not treat illustrative row numbers as observed. Confirm that the actual ESP32 header spacing fits before powering.

## Coordinate system

For a common solderless breadboard, label terminal columns `A B C D E | F G H I J`, with the center trench between E and F. Give the horizontal ESP32-pin rows custom names `P01` through `P15`, counting from the USB end down along the board pins. These are custom labels; breadboard numbering varies by product.

Each five-hole group (A–E and F–J) is internally connected across that row; the two groups are separated by the trench. Side power rails are separate unless board markings say otherwise.

## Top-down placement (illustrative, not to scale)

```text
                     USB end
        left power rail              right power rail
        +3V3   GND                    +3V3   GND
         |      |                       |      |
       =============================================
         A   B   C   D   E   ||   F   G   H   I   J
       ---------------------------------------------
 P01   [ESP32 left header]   ||  [ESP32 right header]
 P02   [ESP32 left header]   ||  [ESP32 right header]
  ...  [ESP32 body spans the center trench]
 P15   [ESP32 left header]   ||  [ESP32 right header]
       ---------------------------------------------
       A-D are free if the header pin occupies E
       G-J are free if the header pin occupies F
       ---------------------------------------------
 P16-P20: OLED / RTC bus jumpers on spare terminal rows
 P21-P24: LED + series resistor circuits
 P25-P28: buzzer module only after current/voltage check
       =============================================
                    bottom
```

This is a logical layout, not a fitted drawing. DevKit boards vary in width, pin count, header spacing, and USB overhang. If the headers do not land in E/F without bending, do not force the board or bridge the headers with wires; use another placement across adjacent breadboards or a stable jumper harness. Map the silk label beside every actual header pin to its matching P-row. The workspace contains no usable photo to establish physical printed row numbers.

## Placement and power rules

1. Unplug USB. Place ESP32 across the trench, USB toward the top, only if both header rows fit naturally into separate holes.
2. Use a ground rail for common ground and a separate 3V3 rail. Connect ESP32 GND to ground. Connect ESP32 3V3 only to modules confirmed to support 3.3 V and whose I2C pull-ups remain 3.3 V-safe.
3. USB powers the ESP32 during development. Do not inject voltage into VIN/5V or 3V3 at the same time. Never put 5 V on GPIO or I2C.
4. Keep the currently assembled R307S wires as documented in [the pin map](final-pin-map.md). Its rail and UART high level are unmeasured; this redraw is not electrical verification.
5. Put OLED and RTC in separate rows. Join SDA to GPIO21 and SCL to GPIO22; confirm each breakout's pull-ups. Share the bus signals, not accidental five-hole rows.
6. Put each LED in a separate terminal group with a resistor in series. Do not put both LED legs in the same internally connected five-hole group. A 1 kΩ resistor is a conservative starting point for indicator LEDs; check the LED/module current and polarity.
7. GPIO23 drives a buzzer input only if that input is 3.3 V compatible and current is within board limits. An unknown/high-current buzzer needs a driver. The exact module is not identified.
8. Keep R307S blue/white leads insulated and apart. Avoid loose jumpers near USB and power rails.

## Connections and inspection

See [final pin map](final-pin-map.md) for every signal. Current owner-reported sensor assembly is red→VIN, black→GND, yellow→GPIO32, green→GPIO33, blue/white open. I2C is 21/22; green LED is 18 through a resistor; red LED is 19 through a resistor; buzzer control is 23 if module-compatible. OLED/RTC supply depends on exact breakout revisions. R307S power and TX logic remain **UNVERIFIED — REQUIRES MULTIMETER**.

Before powering, inspect for any 3V3-to-GND bridge, any 5 V-to-GPIO path, missing LED resistors, reversed module polarity, unverified RTC charging circuit, and exposed sensor leads. The Panasonic CR2032 is not the R307S main supply. Do not combine USB with another ESP32 supply rail.

References: [ESP32 DevKitC guide](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html), [ESP32 datasheet](https://documentation.espressif.com/esp32_datasheet_en.pdf?hkey=EF798316E3902B6ED9A73243A3159BB0), and [power/safety notes](power-and-safety.md).
