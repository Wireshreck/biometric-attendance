#include "device_services.h"

#include <Wire.h>
#include <cstring>
#include "config.h"

bool RtcService::begin() {
    if (!rtc_.begin()) return false;
    ready_ = true;
    const DateTime now = rtc_.now();
    valid_ = !rtc_.lostPower() && now.year() >= 2024 && now.year() <= 2099;
    return valid_;
}

bool RtcService::read(DateTime& out) {
    if (!ready_ || !valid_) return false;
    out = rtc_.now();
    return out.year() >= 2024 && out.year() <= 2099;
}

bool RtcService::lostPower() {
    if (!ready_) return true;
    return rtc_.lostPower();
}

bool RtcService::timestamp(char* out, size_t size) {
    DateTime now;
    if (!out || !size || !read(now)) return false;
    snprintf(out, size, "%04u-%02u-%02uT%02u:%02u:%02u%s", now.year(), now.month(), now.day(), now.hour(), now.minute(), now.second(), LOCAL_TIMEZONE_OFFSET);
    return true;
}

bool RtcService::setLocalTime(uint16_t year, uint8_t month, uint8_t day, uint8_t hour, uint8_t minute, uint8_t second) {
    if (!ready_ || year < 2024 || year > 2099 || month < 1 || month > 12 || hour > 23 || minute > 59 || second > 59) return false;
    static const uint8_t days[] = {31,28,31,30,31,30,31,31,30,31,30,31};
    uint8_t maxDay = days[month-1];
    if (month == 2 && ((year % 4 == 0 && year % 100 != 0) || year % 400 == 0)) ++maxDay;
    if (day < 1 || day > maxDay) return false;
    rtc_.adjust(DateTime(year, month, day, hour, minute, second));
    valid_ = true;
    return true;
}

void IndicatorService::begin() {
    pinMode(PIN_BUZZER, OUTPUT);
    digitalWrite(PIN_BUZZER, LOW);
}

void IndicatorService::setReport(void (*report)(const char*)) {
    report_ = report;
}

void IndicatorService::successPulse() {
    if (report_) report_("buzzer:success");
    digitalWrite(PIN_BUZZER, HIGH); delay(90);
    digitalWrite(PIN_BUZZER, LOW); delay(50);
    digitalWrite(PIN_BUZZER, HIGH); delay(90); digitalWrite(PIN_BUZZER, LOW);
}

void IndicatorService::shortBeep() {
    if (report_) report_("buzzer:short");
    digitalWrite(PIN_BUZZER, HIGH); delay(80); digitalWrite(PIN_BUZZER, LOW);
}

bool IndicatorService::selfTest() {
    if (report_) report_("buzzer:test");
    digitalWrite(PIN_BUZZER, HIGH); delay(80); digitalWrite(PIN_BUZZER, LOW); delay(120);
    digitalWrite(PIN_BUZZER, HIGH); delay(80); digitalWrite(PIN_BUZZER, LOW);
    return true;
}

void IndicatorService::failurePulse() {
    if (report_) report_("buzzer:failure");
    digitalWrite(PIN_BUZZER, HIGH); delay(300);
    digitalWrite(PIN_BUZZER, LOW); delay(300);
}

void IndicatorService::twoBeep() {
    if (report_) report_("buzzer:two_beep");
    digitalWrite(PIN_BUZZER, HIGH); delay(120);
    digitalWrite(PIN_BUZZER, LOW); delay(120);
    digitalWrite(PIN_BUZZER, HIGH); delay(120);
    digitalWrite(PIN_BUZZER, LOW); delay(60);
}

FingerprintService::FingerprintService() : serial_(2), sensor_(&serial_) {}

bool FingerprintService::begin() {
    serial_.begin(R307S_BAUD_RATE, SERIAL_8N1, PIN_R307S_RX, PIN_R307S_TX);
    sensor_.begin(R307S_BAUD_RATE);
    ready_ = sensor_.verifyPassword();
    if (ready_) {
        const bool parametersOk = sensor_.getParameters() == FINGERPRINT_OK;
        const bool countOk = sensor_.getTemplateCount() == FINGERPRINT_OK;
        if (!parametersOk || !countOk) Serial.println("[WARN] Sensor answered but inventory parameters/count were not available.");
    }
    return ready_;
}

bool FingerprintService::readInventory(uint16_t& capacity, uint16_t& usedTemplates) {
    if (!ready_ || sensor_.getParameters() != FINGERPRINT_OK || sensor_.getTemplateCount() != FINGERPRINT_OK) return false;
    capacity = sensor_.capacity; usedTemplates = sensor_.templateCount;
    return capacity > 0 && usedTemplates <= capacity;
}

bool FingerprintService::identify(uint16_t& slotId, uint16_t& confidence) {
    return scan(slotId, confidence) == FingerprintScan::MATCH;
}

FingerprintScan FingerprintService::scan(uint16_t& slotId, uint16_t& confidence) {
    if (!ready_) return FingerprintScan::SENSOR_ERROR;
    const uint8_t image = sensor_.getImage();
    if (image == FINGERPRINT_NOFINGER) return FingerprintScan::NO_FINGER;
    if (image != FINGERPRINT_OK) { ready_ = false; return FingerprintScan::SENSOR_ERROR; }
    if (sensor_.image2Tz() != FINGERPRINT_OK) return FingerprintScan::NO_MATCH;
    const uint8_t result = sensor_.fingerFastSearch();
    if (result == FINGERPRINT_NOTFOUND) return FingerprintScan::NO_MATCH;
    if (result != FINGERPRINT_OK) { ready_ = false; return FingerprintScan::SENSOR_ERROR; }
    slotId = sensor_.fingerID; confidence = sensor_.confidence;
    return FingerprintScan::MATCH;
}

bool FingerprintService::enroll(uint16_t slotId, void (*prompt)(const char*, const char*)) {
    if (!ready_ || slotId == 0 || sensor_.getParameters() != FINGERPRINT_OK || slotId > sensor_.capacity) return false;
    cancelEnroll_ = false;
    enrolling_ = true;
    auto waitForImage = [this](uint32_t timeout) -> uint8_t {
        const uint32_t start = millis();
        while (millis() - start < timeout) {
            if (cancelEnroll_) return 0xFE;
            const uint8_t r = sensor_.getImage();
            if (r == FINGERPRINT_OK) return r;
            if (r != FINGERPRINT_NOFINGER) {
                // Invalid packet / bad image surfaces as non-OK capture code.
                // Keep waiting for a clean capture until timeout.
            }
            delay(50);
        }
        return 0xFF;
    };
    auto waitRemoval = [this](uint32_t timeout) -> bool {
        const uint32_t start = millis();
        while (millis() - start < timeout) {
            if (cancelEnroll_) return false;
            if (sensor_.getImage() == FINGERPRINT_NOFINGER) return true;
            delay(100);
        }
        return false;
    };
    if (prompt) prompt("ENROLL", "Place finger");
    uint8_t first = waitForImage(45000);
    if (first == 0xFE) { enrolling_ = false; return false; }
    if (first != FINGERPRINT_OK || sensor_.image2Tz(1) != FINGERPRINT_OK) { enrolling_ = false; return false; }
    if (sensor_.fingerFastSearch() == FINGERPRINT_OK) {
        if (prompt) prompt("ENROLL", "Finger already enrolled");
        waitRemoval(20000);
        enrolling_ = false;
        return false;
    }
    if (prompt) prompt("ENROLL", "Remove finger");
    if (!waitRemoval(20000)) { enrolling_ = false; return false; }
    if (prompt) prompt("ENROLL", "Place same finger");
    uint8_t second = waitForImage(45000);
    if (second == 0xFE) { enrolling_ = false; return false; }
    if (second != FINGERPRINT_OK || sensor_.image2Tz(2) != FINGERPRINT_OK) { enrolling_ = false; return false; }
    if (sensor_.createModel() != FINGERPRINT_OK) { enrolling_ = false; return false; }
    const bool stored = sensor_.storeModel(slotId) == FINGERPRINT_OK;
    enrolling_ = false;
    cancelEnroll_ = false;
    return stored;
}

void FingerprintService::cancelEnroll() {
    cancelEnroll_ = true;
}

bool FingerprintService::getCount(uint16_t& capacity, uint16_t& used) {
    return readInventory(capacity, used);
}

bool FingerprintService::deleteModel(uint16_t slotId) {
    if (!ready_ || slotId == 0) return false;
    return sensor_.deleteModel(slotId) == FINGERPRINT_OK;
}

bool FingerprintService::deleteAll() {
    if (!ready_) return false;
    return sensor_.emptyDatabase() == FINGERPRINT_OK;
}
