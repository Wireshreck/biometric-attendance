#include <Arduino.h>
#include <Wire.h>
#include <RTClib.h>
#include "config.h"
#include "test_result.h"

static RTC_DS3231 rtc;
void setup() {
    Serial.begin(115200);
    delay(300);
    TestResult result("DS3231 RTC TEST (NO TIME WRITE)");
    Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL, 100000);
    const bool found = rtc.begin();
    result.check(found, "RTC acknowledged on I2C", "expected 0x68");
    if (found) {
        const bool stopped = rtc.lostPower();
        const DateTime a = rtc.now();
        delay(1100);
        const DateTime b = rtc.now();
        char first[24], second[24];
        snprintf(first, sizeof(first), "%04d-%02d-%02d %02d:%02d:%02d", a.year(), a.month(), a.day(), a.hour(), a.minute(), a.second());
        snprintf(second, sizeof(second), "%04d-%02d-%02d %02d:%02d:%02d", b.year(), b.month(), b.day(), b.hour(), b.minute(), b.second());
        Serial.printf("[INFO] first=%s second=%s oscillator_lost_power=%s\n", first, second, stopped ? "yes" : "no");
        const bool plausible = a.year() >= 2024 && a.year() <= 2099;
        result.check(plausible, "RTC time is in plausible range", "time not set by this test");
        result.check(a.unixtime() != b.unixtime(), "RTC advances between reads");
        result.check(!stopped, "RTC does not report oscillator stop", "if failed, set time only with explicit operator action");
    }
    result.info("This test never sets the clock and does not prove accuracy or battery backup.");
    result.finish();
}
void loop() { delay(1000); }
