#include "ble_service.h"

#include <ArduinoJson.h>
#include <cstring>

#include "attendance_store.h"
#include "ble_protocol.h"
#include "config.h"
#include "device_services.h"

#ifdef ARDUINO_ARCH_ESP32
#include <BLE2902.h>
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
        // Fast-path only: stage for the loop task. Heavy work (JSON,
        // sensor UART, LittleFS) here overflows the BLE task stack and
        // crashes the device. See BleService::poll().
        if (!gActive->stageRequest(v.c_str(), v.size(), c)) {
            c->setValue("{\"status\":\"busy\",\"code\":\"busy\"}");
        } else {
            c->setValue("{\"status\":\"busy\",\"code\":\"processing\"}");
        }
        // NOTE: no notify() here. Issuing a notification from inside the
        // write callback breaks the ATT Write Response on some centrals
        // (Windows WinRT cancels the transaction). Clients use the
        // write-then-read pattern served by poll().
    }
};
CommandCallbacks gCallbacks;

class ServerCallbacks : public BLEServerCallbacks {
public:
    // A central that drops without a clean disconnect (common with the
    // Windows BLE stack) must not silence the device: resume advertising
    // so the next client can always find it.
    void onDisconnect(BLEServer* s) override {
        if (s) s->getAdvertising()->start();
    }
};
ServerCallbacks gServerCallbacks;
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
        const EnrollResult outcome = fp_->enroll((uint16_t)slot, [](const char* t, const char* d) {
            Serial.printf("[ENROLL] %s: %s\n", t ? t : "?", d ? d : "");
            if (gActive) gActive->emit("{\"state\":\"ENROLL_PROGRESS\"}");
        });
        switch (outcome) {
            case EnrollResult::OK: break;
            case EnrollResult::NO_SENSOR:
                errResp(responseOut, responseSize, ERR_SENSOR_UNAVAILABLE, "Fingerprint sensor not connected");
                return true;
            case EnrollResult::BAD_SLOT:
                errResp(responseOut, responseSize, ERR_INVALID_ID, "Invalid enrollment slot");
                return true;
            case EnrollResult::STORAGE_FULL:
                errResp(responseOut, responseSize, ERR_STORAGE_FULL, "Fingerprint database is full");
                return true;
            case EnrollResult::CANCELLED:
                errResp(responseOut, responseSize, ERR_TIMEOUT, "Enrollment cancelled");
                return true;
            case EnrollResult::TIMEOUT_FIRST:
                errResp(responseOut, responseSize, ERR_NO_FINGER, "No finger detected within timeout");
                return true;
            case EnrollResult::BAD_IMAGE_FIRST:
                errResp(responseOut, responseSize, ERR_BAD_IMAGE, "First capture was unreadable");
                return true;
            case EnrollResult::DUPLICATE:
                errResp(responseOut, responseSize, ERR_DUPLICATE, "Fingerprint already enrolled");
                return true;
            case EnrollResult::TIMEOUT_REMOVAL:
                errResp(responseOut, responseSize, ERR_TIMEOUT, "Finger was not removed in time");
                return true;
            case EnrollResult::TIMEOUT_SECOND:
                errResp(responseOut, responseSize, ERR_NO_FINGER, "Second capture timed out waiting for finger");
                return true;
            case EnrollResult::BAD_IMAGE_SECOND:
                errResp(responseOut, responseSize, ERR_BAD_IMAGE, "Second capture was unreadable");
                return true;
            case EnrollResult::MISMATCH:
                errResp(responseOut, responseSize, ERR_IMAGE_MISMATCH, "Second impression did not match first");
                return true;
            case EnrollResult::STORE_FAILED:
                errResp(responseOut, responseSize, ERR_WRITE_FAILED, "Template storage failed");
                return true;
        }
        if (outcome != EnrollResult::OK) {
            errResp(responseOut, responseSize, ERR_BAD_IMAGE,
                    "Enrollment failed: no finger, bad image, mismatch, duplicate, or storage error");
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
    // ATTENDANCE_READ (paginated: BLE attribute values stay small)
    if (strcmp(cmd, CMD_ATTENDANCE_READ) == 0) {
        if (!store_ || !store_->healthy()) {
            errResp(responseOut, responseSize, ERR_COMMUNICATION, "Storage unavailable");
            return true;
        }
        long limit = req["limit"] | 5;
        long offset = req["offset"] | 0;
        if (limit < 1) limit = 1;
        if (limit > 50) limit = 50;
        if (offset < 0) offset = 0;
        // Heap-allocated: a 50-record stack array overflows the loop task.
        AttendanceEvent* items = new (std::nothrow) AttendanceEvent[50];
        if (!items) {
            errResp(responseOut, responseSize, ERR_COMMUNICATION, "Out of memory");
            return true;
        }
        size_t count = 0;
        const bool readOk = store_->readAll(items, 50, count);
        if (readOk) {
            JsonDocument doc;
            doc[KEY_STATUS] = STATUS_OK;
            doc[KEY_CODE] = "attendance";
            doc[KEY_DATA]["total"] = (int)count;
            JsonArray arr = doc[KEY_DATA]["records"].to<JsonArray>();
            for (size_t i = (size_t)offset; i < count && arr.size() < (size_t)limit; ++i) {
                JsonObject o = arr.add<JsonObject>();
                o["slot"] = items[i].slot;
                o["captured_at"] = items[i].capturedAt;
                o["status"] = "recorded";
            }
            serializeJson(doc, responseOut, responseSize);
        }
        delete[] items;
        if (!readOk) {
            errResp(responseOut, responseSize, ERR_COMMUNICATION, "Storage unavailable");
        }
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
    server->setCallbacks(&gServerCallbacks);
    // 1 service decl + 8 characteristics x (decl + value + CCCD) + margin.
    BLEService* svc = server->createService(BLEUUID(BLE_SERVICE_UUID), 40);
    for (int i = 0; i < 8; ++i) {
        BLECharacteristic* c = svc->createCharacteristic(
            kCharUuids[i], BLECharacteristic::PROPERTY_READ |
                           BLECharacteristic::PROPERTY_WRITE |
                           BLECharacteristic::PROPERTY_NOTIFY);
        c->setCallbacks(&gCallbacks);
        c->setValue("{}");
        c->addDescriptor(new BLE2902());
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
#ifdef ARDUINO_ARCH_ESP32
    if (!stagedPending_) return;
    stagedPending_ = false;
    stagedReq_[stagedLen_] = '\0';
    if (handleCommand(stagedReq_, respBuf_, sizeof(respBuf_))) {
        // GATT attribute reads stall above a few hundred bytes on this
        // stack/central combination (observed: ~713 B never surfaces while
        // ~470 B works). Never publish an unservable response; paginated
        // commands (ATTENDANCE_READ) keep payloads small by design.
        if (strlen(respBuf_) > 500) {
            snprintf(respBuf_, sizeof(respBuf_),
                     "{\"status\":\"error\",\"code\":\"%s\",\"message\":"
                     "\"Response too large; retry with a smaller page\"}",
                     ERR_COMMUNICATION);
        }
        BLECharacteristic* target = static_cast<BLECharacteristic*>(stagedTarget_);
        if (target) target->setValue(respBuf_);
    }
    stagedTarget_ = nullptr;
    stagedLen_ = 0;
#else
    (void)0;
#endif
}

bool BleService::stageRequest(const char* requestJson, size_t length, void* target) {
    if (!requestJson || !target || length == 0 || length >= REQ_MAX) return false;
    if (stagedPending_) return false;
    memcpy(stagedReq_, requestJson, length);
    stagedLen_ = length;
    stagedTarget_ = target;
    stagedPending_ = true;
    return true;
}
