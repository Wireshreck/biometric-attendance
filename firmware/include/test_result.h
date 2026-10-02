#pragma once

#include <Arduino.h>

class TestResult {
public:
    explicit TestResult(const char* title) : title_(title) {
        Serial.println("========================================");
        Serial.println(title_);
        Serial.println("========================================");
    }

    void info(const char* message) {
        Serial.printf("[INFO] %s\n", message);
    }

    void check(bool passed, const char* label, const char* detail = "") {
        Serial.printf("[%s] %s", passed ? "PASS" : "FAIL", label);
        if (detail[0] != '\0') Serial.printf(": %s", detail);
        Serial.println();
        if (!passed) ++failures_;
        ++checks_;
    }

    void skip(const char* label, const char* reason) {
        Serial.printf("[NOT EXECUTED] %s: %s\n", label, reason);
        ++skipped_;
    }

    void unverified(const char* reason) {
        Serial.printf("[UNVERIFIED] %s\n", reason);
        unverified_ = true;
    }

    bool finish() const {
        const char* status = failures_ > 0 ? "FAIL" :
                             checks_ == 0 ? "NOT EXECUTED" :
                             (unverified_ || skipped_ > 0) ? "UNVERIFIED" : "PASS";
        Serial.printf("\nRESULT: %s (%u checks, %u failures, %u skipped)\n",
                      status,
                      static_cast<unsigned>(checks_),
                      static_cast<unsigned>(failures_),
                      static_cast<unsigned>(skipped_));
        return checks_ > 0 && failures_ == 0;
    }

private:
    const char* title_;
    unsigned checks_ = 0;
    unsigned failures_ = 0;
    unsigned skipped_ = 0;
    bool unverified_ = false;
};
