---
type: hardware
area: hardware
status: deprecated
tags:
  - hardware
  - pinout
  - redirect
---
# ESP32 pin map — superseded navigation

The authoritative current component/pin/voltage/breadboard table is [final-pin-map.md](final-pin-map.md). Use it with [power-and-safety.md](power-and-safety.md) and the [recommended breadboard layout](complete-breadboard-layout.md).

The GPIO assignments remain GPIO32/33 for the owner-reported R307S UART, GPIO21/22 I2C, and GPIO23 buzzer control. The green/red LEDs and the SSD1306 OLED were removed from this project; GPIO18 and GPIO19 are now unused/reserved. This short reference is retained because existing audit notes link to it. Update those notes only when reviewing their historical context; do not maintain a second pin specification here. The authoritative current table is [final-pin-map.md](final-pin-map.md).
