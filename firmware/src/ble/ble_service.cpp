#include "ble_service.h"

#include <ArduinoJson.h>
#include <cstring>

#include "attendance_store.h"
#include "ble_protocol.h"
#include "config.h"
#include "device_services.h"

#ifdef ARDUINO_ARCH_ESP32
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#endif

namespace {

BleService* gActive = nullptr;

void writeResponse(char* out, size_t size, const char* status, const char* code,
                   const char* message, std::function<void(JsonDocument&)> fillData) {
    JsonDocument doc;
    doc[KEY_STATUS] = status;
    doc[KEY_CODE] = code;
    if (message && message[0]) doc["message"] = message;
    if (fillData) {
        JsonObject data = doc[KEY_DATA].to<JsonObject>();
        (void)data;
        fillData(doc);
    }
    serializeJson(doc, out, size);
}

void okWithData(char* out, size_t size, const char* code,
                std::function<void(JsonDocument&)> fillData, const char* message = "") {
    writeResponse(out, size, STATUS_OK, code, message, fillData);
}

void errResp(char* out, size_t size, const char* code, const char* message) {
    writeResponse(out, size, STATUS_ERROR, code, message, nullptr);
}

#ifdef ARDUINO_ARCH_ESP32
BLECharacteristic* gChars[8] = {nullptr};
const char* kCharUuids[8] = {
    BLE_CHAR_DEVICE_INFO_UUID, BLE_CHAR_DEVICE_STATUS_UUID, BLE_CHAR_PING_UUID,
    BLE_CHAR_RTC_UUID, BLE_CHAR_FINGERPRINT_STATUS_UUID,
    BLE_CHAR_FINGERPRINT_CONTROL_UUID, BLE_CHAR_DIAGNOSTIC_UUID,
    BLE_CHAR_ATTENDANCE_UUID};

class CommandCallbacks : public BLECharacteristicCallbacks {
public:
    void onWrite(BLECharacteristic* c) override {
        if (!gActive) return;
        std::string v = c->getValue();
        if (v.empty()) return;
        char resp[2048];
        if (!gActive->handleCommand(v.c_str(), resp, sizeof(resp))) return;
        c->setValue(resp);
        c->notify();
    }
};
CommandCallbacks gCallbacks;
#endif

}  // namespace

void BleService::configure(RtcService* rtc, FingerprintService* fp,
                           IndicatorService* buzzer, AttendanceStore* store) {
    rtc_ = rtc;
    fp_ = fp;
    buzzer_ = buzzer;
    store_ = store;
    bootMs_ = millis();
}

void BleService::emit(const char* json) {
    if (notify_) notify_(json);
}

bool BleService::handleCommand(const char* requestJson, char* responseOut, size_t responseSize) {
    if (!requestJson || !responseOut || responseSize == 0) return false;
    JsonDocument req;
    if (deserializeJson(req, requestJson) != DeserializationError::Ok) {
        errResp(responseOut, responseSize, ERR_UNKNOWN, "Invalid JSON request");
        return true;
    }
    const char* cmd = req["cmd"] | req["command"] | "";
    if (!cmd[0]) {
        errResp(responseOut, responseSize, ERR_UNKNOWN, "Missing cmd field");
        return true;
    }

    // DEVICE_INFO
    if (strcmp(cmd, CMD_DEVICE_INFO) == 0) {
        okWithData(responseOut, responseSize, "device_info", [&](JsonDocument& doc) {
            doc[KEY_DATA]["device"] = DEVICE_NAME;
            doc[KEY_DATA]["firmware"] = FIRMWARE_VERSION;
            doc[KEY_DATA]["hardware"] = HARDWARE_NAME;
            doc[KEY_DATA]["uptime_seconds"] = (uint32_t)((millis() - bootMs_) / 1000UL);
            doc[KEY_DATA]["ble_service"] = BLE_SERVICE_UUID;
        });
        return true;
    }
    // DEVICE_STATUS
    if (strcmp(cmd, CMD_DEVICE_STATUS) == 0) {
        char stamp[40] = "";
        bool rtcValid = rtc_ && rtc_->valid();
        bool lostPower = rtc_ ? rtc_->lostPower() : true;
        if (rtcValid) rtc_->timestamp(stamp, sizeof(stamp));
        uint16_t cap = 0, used = 0;
        bool invOk = fp_ && fp_->ready() && fp_->readInventory(cap, used);
        okWithData(responseOut, responseSize, "device_status", [&](JsonDocument& doc) {
            doc[KEY_DATA]["rtc_ok"] = rtcValid;
            doc[KEY_DATA]["rtc_lost_power"] = lostPower;
            doc[KEY_DATA]["rtc_valid"] = rtcValid;
            doc[KEY_DATA]["rtc_time"] = stamp;
            doc[KEY_DATA]["sensor_ready"] = fp_ && fp_->ready();
            doc[KEY_DATA]["sensor_connected"] = fp_ && fp_->ready();
            doc[KEY_DATA]["template_count"] = invOk ? used : 0;
            doc[KEY_DATA]["template_capacity"] = invOk ? cap : 0;
            doc[KEY_DATA]["storage_ok"] = store_ && store_->healthy();
            doc[KEY_DATA]["storage_used_bytes"] = 0;
            doc[KEY_DATA]["buzzer_pin"] = PIN_BUZZER;
            doc[KEY_DATA]["i2c_bus"] = "GPIO25/GPIO26";
            doc[KEY_DATA]["r307s_uart"] = "GPIO32/GPIO33 @ 57600 8N1";
        });
        return true;
    }
    // PING
    if (strcmp(cmd, CMD_PING) == 0) {
        okWithData(responseOut, responseSize, "pong", nullptr, "pong");
        return true;
    }
    // RTC_GET
    if (strcmp(cmd, CMD_RTC_GET) == 0) {
        char stamp[40] = "";
        bool valid = false;
        bool lost = true;
        if (rtc_) {
            DateTime now;
            lost = rtc_->lostPower();
            valid = rtc_->read(now);
            if (valid) rtc_->timestamp(stamp, sizeof(stamp));
        }
        if (!valid) {
            okWithData(responseOut, responseSize, "rtc", [&](JsonDocument& doc) {
                doc[KEY_DATA]["time"] = "";
                doc[KEY_DATA]["valid"] = false;
                doc[KEY_DATA]["lost_power"] = lost;
            });
            return true;
        }
        okWithData(responseOut, responseSize, "rtc", [&](JsonDocument& doc) {
            doc[KEY_DATA]["time"] = stamp;
            doc[KEY_DATA]["valid"] = true;
            doc[KEY_DATA]["lost_power"] = lost;
        });
        return true;
    }
    // RTC_SET
    if (strcmp(cmd, CMD_RTC_SET) == 0) {
        long year = req["year"] | 0;
        long month = req["month"] | 0;
        long day = req["day"] | 0;
        long hour = req["hour"] | 0;
        long minute = req["minute"] | 0;
        long second = req["second"] | 0;
        if (!rtc_ || !rtc_->setLocalTime((uint16_t)year, (uint8_t)month, (uint8_t)day,
                                         (uint8_t)hour, (uint8_t)minute, (uint8_t)second)) {
            errResp(responseOut, responseSize, ERR_RTC_INVALID, "Invalid date/time or RTC unavailable");
            return true;
        }
        okWithData(responseOut, responseSize, "rtc_set", nullptr, "RTC set");
        return true;
    }
    // FINGERPRINT_STATUS
    if (strcmp(cmd, CMD_FINGERPRINT_STATUS) == 0) {
        uint16_t cap = 0, used = 0;
        bool ok = fp_ && fp_->ready() && fp_->readInventory(cap, used);
        if (!ok) {
            okWithData(responseOut, responseSize, "fingerprint_status", [&](JsonDocument& doc) {
                doc[KEY_DATA]["ready"] = false;
                doc[KEY_DATA]["connected"] = false;
                doc[KEY_DATA]["capacity"] = 0;
                doc[KEY_DATA]["used"] = 0;
                doc[KEY_DATA]["note"] = "sensor did not respond";
            });
            return true;
        }
        okWithData(responseOut, responseSize, "fingerprint_status", [&](JsonDocument& doc) {
            doc[KEY_DATA]["ready"] = true;
            doc[KEY_DATA]["connected"] = true;
            doc[KEY_DATA]["capacity"] = cap;
            doc[KEY_DATA]["used"] = used;
        });
        return true;
    }
    // FINGERPRINT_COUNT
    if (strcmp(cmd, CMD_FINGERPRINT_COUNT) == 0) {
        uint16_t cap = 0, used = 0;
        if (!fp_ || !fp_->ready() || !fp_->readInventory(cap, used)) {
            errResp(responseOut, responseSize, ERR_SENSOR_UNAVAILABLE, "Fingerprint sensor not connected");
            return true;
        }
        okWithData(responseOut, responseSize, "fingerprint_count", [&](JsonDocument& doc) {
            doc[KEY_DATA]["capacity"] = cap;
            doc[KEY_DATA]["used"] = used;
        });
        return true;
    }
    // FINGERPRINT_ENROLL
    if (strcmp(cmd, CMD_FINGERPRINT_ENROLL) == 0) {
        long slot = req["slot"] | 0;
        if (!fp_ || !fp_->ready()) {
            errResp(responseOut, responseSize, ERR_SENSOR_UNAVAILABLE, "Fingerprint sensor not connected");
            return true;
        }
        if (slot <= 0 || slot > 1000) {
            errResp(responseOut, responseSize, ERR_INVALID_ID, "Invalid enrollment slot");
            return true;
        }
        uint16_t cap = 0, used = 0;
        if (fp_->readInventory(cap, used)) {
            if (used >= cap) {
                errResp(responseOut, responseSize, ERR_STORAGE_FULL, "Fingerprint database is full");
                return true;
            }
            if (slot > cap) {
                errResp(responseOut, responseSize, ERR_INVALID_ID, "Invalid enrollment slot");
                return true;
            }
        }
        emit("{\"state\":\"ENROLL_PLACE_FINGER\"}");
        bool enrolled = fp_->enroll((uint16_t)slot, [](const char* t, const char* d) {
            (void)t; (void)d;
            if (gActive) gActive->emit("{\"state\":\"ENROLL_PROGRESS\"}");
        });
        if (!enrolled) {
            if (fp_->isEnrolling()) {
                errResp(responseOut, responseSize, ERR_TIMEOUT, "Enrollment cancelled or timed out");
            } else {
                errResp(responseOut, responseSize, ERR_BAD_IMAGE,
                        "Enrollment failed: no finger, bad image, mismatch, duplicate, or storage error");
            }
            return true;
        }
        JsonDocument doc;
        doc[KEY_STATUS] = STATUS_OK;
        doc[KEY_CODE] = "enroll_success";
        doc["slot"] = (int)slot;
        serializeJson(doc, responseOut, responseSize);
        return true;
    }
    // FINGERPRINT_SEARCH
    if (strcmp(cmd, CMD_FINGERPRINT_SEARCH) == 0) {
        if (!fp_ || !fp_->ready()) {
            errResp(responseOut, responseSize, ERR_SENSOR_UNAVAILABLE, "Fingerprint sensor not connected");
            return true;
        }
        // Bounded single-shot search: honest NO_FINGER / no_match / match.
        uint16_t slot = 0, conf = 0;
        FingerprintScan r = fp_->scan(slot, conf);
        if (r == FingerprintScan::NO_FINGER) {
            errResp(responseOut, responseSize, ERR_NO_FINGER, "No finger detected");
            return true;
        }
        if (r == FingerprintScan::SENSOR_ERROR) {
            errResp(responseOut, responseSize, ERR_COMMUNICATION, "Sensor communication error");
            return true;
        }
        if (r == FingerprintScan::NO_MATCH) {
            okWithData(responseOut, responseSize, "no_match", nullptr, "No match");
            return true;
        }
        okWithData(responseOut, responseSize, "match", [&](JsonDocument& doc) {
            doc["slot"] = slot;
            doc["confidence"] = conf;
        });
        return true;
    }
    // FINGERPRINT_DELETE
    if (strcmp(cmd, CMD_FINGERPRINT_DELETE) == 0) {
        long slot = req["slot"] | 0;
        if (!fp_ || !fp_->ready()) {
            errResp(responseOut, responseSize, ERR_SENSOR_UNAVAILABLE, "Fingerprint sensor not connected");
            return true;
        }
        if (slot <= 0 || slot > 1000) {
            errResp(responseOut, responseSize, ERR_INVALID_ID, "Invalid slot");
            return true;
        }
        if (!fp_->deleteModel((uint16_t)slot)) {
            errResp(responseOut, responseSize, ERR_COMMUNICATION, "Delete failed or unknown slot");
            return true;
        }
        JsonDocument doc;
        doc[KEY_STATUS] = STATUS_OK;
        doc[KEY_CODE] = "deleted";
        doc["slot"] = (int)slot;
        serializeJson(doc, responseOut, responseSize);
        return true;
    }
    // FINGERPRINT_DELETE_ALL
    if (strcmp(cmd, CMD_FINGERPRINT_DELETE_ALL) == 0) {
        if (!fp_ || !fp_->ready()) {
            errResp(responseOut, responseSize, ERR_SENSOR_UNAVAILABLE, "Fingerprint sensor not connected");
            return true;
        }
        uint16_t cap = 0, used = 0;
        uint16_t before = 0;
        if (fp_->readInventory(cap, used)) before = used;
        if (!fp_->deleteAll()) {
            errResp(responseOut, responseSize, ERR_COMMUNICATION, "Delete-all failed");
            return true;
        }
        JsonDocument doc;
        doc[KEY_STATUS] = STATUS_OK;
        doc[KEY_CODE] = "deleted_all";
        doc["deleted"] = before;
        serializeJson(doc, responseOut, responseSize);
        return true;
    }
    // BUZZER_TEST
    if (strcmp(cmd, CMD_BUZZER_TEST) == 0) {
        if (!buzzer_) {
            errResp(responseOut, responseSize, ERR_UNKNOWN, "Buzzer unavailable");
            return true;
        }
        buzzer_->twoBeep();
        JsonDocument doc;
        doc[KEY_STATUS] = STATUS_OK;
        doc[KEY_CODE] = "buzzer_test";
        doc["pin"] = PIN_BUZZER;
        serializeJson(doc, responseOut, responseSize);
        return true;
    }
    // FULL_DIAGNOSTIC
    if (strcmp(cmd, CMD_FULL_DIAGNOSTIC) == 0) {
        JsonDocument doc;
        doc[KEY_STATUS] = STATUS_OK;
        doc[KEY_CODE] = "diagnostic";
        JsonArray results = doc[KEY_DATA]["results"].to<JsonArray>();
        auto add = [&](const char* test, const char* result, const char* reason = "") {
            JsonObject o = results.add<JsonObject>();
            o["test"] = test;
            o["result"] = result;
            if (reason && reason[0]) o["reason"] = reason;
        };
        add(DIAG_ESP32, DIAG_PASS);
        add(DIAG_BLE, running_ ? DIAG_PASS : DIAG_WARN, running_ ? "" : "BLE stack not advertising");
        bool sensorReady = fp_ && fp_->ready();
        if (!sensorReady) {
            add(DIAG_R307S_UART, DIAG_FAIL, "No sensor response");
            add(DIAG_R307S_SENSOR, DIAG_SKIPPED, "UART check failed");
            add(DIAG_FINGERPRINT_DB, DIAG_SKIPPED, "Sensor unavailable");
        } else {
            uint16_t cap = 0, used = 0;
            if (fp_->readInventory(cap, used)) {
                add(DIAG_R307S_UART, DIAG_PASS);
                add(DIAG_R307S_SENSOR, DIAG_PASS);
                add(DIAG_FINGERPRINT_DB, DIAG_PASS);
            } else {
                add(DIAG_R307S_UART, DIAG_WARN, "Sensor answered but inventory unreadable");
                add(DIAG_R307S_SENSOR, DIAG_WARN, "Inventory unreadable");
                add(DIAG_FINGERPRINT_DB, DIAG_WARN, "Inventory unreadable");
            }
        }
        bool rtcValid = rtc_ && rtc_->valid();
        if (!rtc_ || !rtc_->ready()) {
            add(DIAG_DS3231, DIAG_FAIL, "No I2C device at 0x68");
            add(DIAG_RTC, DIAG_SKIPPED, "DS3231 unavailable");
        } else if (!rtcValid) {
            add(DIAG_DS3231, DIAG_WARN, "DS3231 present but time invalid or lost power");
            add(DIAG_RTC, DIAG_FAIL, "RTC time invalid");
        } else {
            add(DIAG_DS3231, DIAG_PASS);
            add(DIAG_RTC, DIAG_PASS);
        }
        if (buzzer_) {
            buzzer_->shortBeep();
            add(DIAG_BUZZER, DIAG_PASS);
        } else {
            add(DIAG_BUZZER, DIAG_FAIL, "Buzzer service unavailable");
        }
        if (store_ && store_->healthy()) {
            add(DIAG_STORAGE, DIAG_PASS);
            add(DIAG_ATTENDANCE, DIAG_PASS);
        } else {
            add(DIAG_STORAGE, DIAG_FAIL, "Storage unhealthy");
            add(DIAG_ATTENDANCE, DIAG_SKIPPED, "Storage unhealthy");
        }
        serializeJson(doc, responseOut, responseSize);
        return true;
    }
    // ATTENDANCE_STATUS
    if (strcmp(cmd, CMD_ATTENDANCE_STATUS) == 0) {
        size_t n = store_ ? store_->pendingCount() : 0;
        okWithData(responseOut, responseSize, "attendance_status", [&](JsonDocument& doc) {
            doc[KEY_DATA]["records"] = (int)n;
            doc[KEY_DATA]["storage_ok"] = store_ && store_->healthy();
        });
        return true;
    }
    // ATTENDANCE_READ
    if (strcmp(cmd, CMD_ATTENDANCE_READ) == 0) {
        if (!store_ || !store_->healthy()) {
            errResp(responseOut, responseSize, ERR_COMMUNICATION, "Storage unavailable");
            return true;
        }
        AttendanceEvent items[50];
        size_t count = 0;
        store_->readAll(items, 50, count);
        JsonDocument doc;
        doc[KEY_STATUS] = STATUS_OK;
        doc[KEY_CODE] = "attendance";
        JsonArray arr = doc[KEY_DATA]["records"].to<JsonArray>();
        for (size_t i = 0; i < count; ++i) {
            JsonObject o = arr.add<JsonObject>();
            o["slot"] = items[i].slot;
            o["captured_at"] = items[i].capturedAt;
            o["status"] = "recorded";
        }
        serializeJson(doc, responseOut, responseSize);
        return true;
    }
    // ATTENDANCE_CLEAR
    if (strcmp(cmd, CMD_ATTENDANCE_CLEAR) == 0) {
        if (!store_ || !store_->clear()) {
            errResp(responseOut, responseSize, ERR_WRITE_FAILED, "Clear failed");
            return true;
        }
        JsonDocument doc;
        doc[KEY_STATUS] = STATUS_OK;
        doc[KEY_CODE] = "cleared";
        doc["records"] = 0;
        serializeJson(doc, responseOut, responseSize);
        return true;
    }

    errResp(responseOut, responseSize, ERR_NOT_IMPLEMENTED, "Unknown command");
    return true;
}

bool BleService::begin(const char* deviceName) {
#ifndef ARDUINO_ARCH_ESP32
    (void)deviceName;
    running_ = false;
    return false;
#else
    gActive = this;
    BLEDevice::init(deviceName ? deviceName : DEVICE_NAME);
    BLEServer* server = BLEDevice::createServer();
    BLEService* svc = server->createService(BLE_SERVICE_UUID);
    for (int i = 0; i < 8; ++i) {
        BLECharacteristic* c = svc->createCharacteristic(
            kCharUuids[i], BLECharacteristic::PROPERTY_READ |
                           BLECharacteristic::PROPERTY_WRITE |
                           BLECharacteristic::PROPERTY_NOTIFY);
        c->setCallbacks(&gCallbacks);
        c->setValue("{}");
        gChars[i] = c;
    }
    svc->start();
    BLEAdvertising* adv = BLEDevice::getAdvertising();
    adv->addServiceUUID(BLE_SERVICE_UUID);
    adv->setScanResponse(true);
    adv->start();
    running_ = true;
    return true;
#endif
}

void BleService::poll() {
    // GATT callbacks are interrupt-driven; nothing to poll on ESP32 Arduino.
}
