#include <Arduino.h>
#include "config.h"
#include "test_result.h"
void setup() {
    Serial.begin(115200);
    delay(300);
    TestResult result("ACTIVE BUZZER TEST");
    pinMode(PIN_BUZZER, OUTPUT);
    digitalWrite(PIN_BUZZER, LOW);
    Serial.println("[INFO] GPIO23: quiet 1s, two short 80ms beeps with 300ms gap.");
    delay(1000);
    for (uint8_t i = 0; i < 2; ++i) { digitalWrite(PIN_BUZZER, HIGH); delay(80); digitalWrite(PIN_BUZZER, LOW); delay(300); }
    result.check(true, "Configured buzzer output sequence executed");
    result.unverified("Listen for the physical buzzer; firmware cannot sense acoustic output.");
    result.finish();
}
void loop() { digitalWrite(PIN_BUZZER, LOW); delay(1000); }
