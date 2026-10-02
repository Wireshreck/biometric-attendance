#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "config.h"
#include "test_result.h"

static Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);
void setup() {
    Serial.begin(115200);
    delay(300);
    TestResult result("SSD1306 OLED TEST");
    Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL, 100000);
    const bool initialized = display.begin(SSD1306_SWITCHCAPVCC, OLED_I2C_ADDR);
    result.check(initialized, "OLED initialized", "check I2C scan, power, address 0x3C and wiring");
    if (initialized) {
        display.clearDisplay();
        display.setTextColor(SSD1306_WHITE);
        display.setTextSize(1);
        display.setCursor(0, 0);
        display.println("OLED TEST");
        display.println("PASS");
        display.drawPixel(120, 10, SSD1306_WHITE);
        display.drawLine(0, 20, 127, 20, SSD1306_WHITE);
        display.display();
        delay(1500);
        display.clearDisplay();
        display.setCursor(0, 0);
        display.println("Repeated refresh");
        display.display();
        result.check(true, "Text/pixel/line/clear/refresh commands completed");
        result.unverified("Visually confirm the panel shows OLED TEST and PASS; I2C ACK alone cannot verify emitted pixels.");
    }
    result.finish();
}
void loop() { delay(1000); }
