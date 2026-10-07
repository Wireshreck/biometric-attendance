#include <Arduino.h>
#include <Wire.h>
#include "config.h"
#include "test_result.h"

void setup() {
    Serial.begin(115200);
    delay(300);
    TestResult result("I2C BUS SCAN");
    const bool initialized = Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL, 100000);
    result.check(initialized, "I2C controller initialized");
    uint8_t count = 0;
    for (uint8_t address = 1; address < 127; ++address) {
        Wire.beginTransmission(address);
        if (Wire.endTransmission() == 0) {
            ++count;
            Serial.printf("[INFO] I2C device 0x%02X detected\n", address);
        }
    }
    Serial.printf("[INFO] SDA=GPIO%u SCL=GPIO%u speed=100kHz devices=%u\n",
                  PIN_I2C_SDA, PIN_I2C_SCL, count);

    result.check(count > 0, "At least one I2C device acknowledged", "expected RTC 0x68; OLED was removed from this project");
    result.info("An ACK does not verify pull-up voltage or prove both expected devices are present.");
    result.finish();
}

void loop() { delay(1000); }
