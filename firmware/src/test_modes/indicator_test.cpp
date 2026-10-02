#include <Arduino.h>
#include "config.h"
#include "test_result.h"

#ifdef INDICATOR_RED
static constexpr uint8_t INDICATOR_PIN_VALUE = PIN_LED_RED;
static constexpr const char* INDICATOR_LABEL = "RED LED TEST";
#else
static constexpr uint8_t INDICATOR_PIN_VALUE = PIN_LED_GREEN;
static constexpr const char* INDICATOR_LABEL = "GREEN LED TEST";
#endif

void setup() {
    Serial.begin(115200);
    delay(300);
    TestResult result(INDICATOR_LABEL);
    pinMode(INDICATOR_PIN_VALUE, OUTPUT);
    digitalWrite(INDICATOR_PIN_VALUE, LOW);
    Serial.printf("[INFO] GPIO%u: OFF 1s, ON 1s, then three short blinks. Use a series resistor.\n", INDICATOR_PIN_VALUE);
    delay(1000);
    digitalWrite(INDICATOR_PIN_VALUE, HIGH);
    delay(1000);
    digitalWrite(INDICATOR_PIN_VALUE, LOW);
    for (uint8_t i = 0; i < 3; ++i) { digitalWrite(INDICATOR_PIN_VALUE, HIGH); delay(200); digitalWrite(INDICATOR_PIN_VALUE, LOW); delay(300); }
    result.check(true, "Configured GPIO sequence executed");
    result.unverified("Observe the physical LED; firmware cannot sense whether it illuminated.");
    result.finish();
}
void loop() { delay(1000); }
