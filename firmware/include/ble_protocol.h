#pragma once

#include "config.h"

// Shared BLE command IDs used by web, mobile, Windows, test.exe.
// Messages are UTF-8 JSON on the BLE characteristics defined in config.h.

static const char* const CMD_DEVICE_INFO     = "DEVICE_INFO";
static const char* const CMD_DEVICE_STATUS   = "DEVICE_STATUS";
static const char* const CMD_PING           = "PING";

static const char* const CMD_RTC_GET        = "RTC_GET";
static const char* const CMD_RTC_SET        = "RTC_SET";

static const char* const CMD_FINGERPRINT_STATUS   = "FINGERPRINT_STATUS";
static const char* const CMD_FINGERPRINT_COUNT    = "FINGERPRINT_COUNT";
static const char* const CMD_FINGERPRINT_ENROLL   = "FINGERPRINT_ENROLL";
static const char* const CMD_FINGERPRINT_SEARCH   = "FINGERPRINT_SEARCH";
static const char* const CMD_FINGERPRINT_DELETE   = "FINGERPRINT_DELETE";
static const char* const CMD_FINGERPRINT_DELETE_ALL = "FINGERPRINT_DELETE_ALL";

static const char* const CMD_BUZZER_TEST     = "BUZZER_TEST";
static const char* const CMD_FULL_DIAGNOSTIC = "FULL_DIAGNOSTIC";

static const char* const CMD_ATTENDANCE_STATUS = "ATTENDANCE_STATUS";
static const char* const CMD_ATTENDANCE_READ   = "ATTENDANCE_READ";
static const char* const CMD_ATTENDANCE_CLEAR  = "ATTENDANCE_CLEAR";

// Standard response envelope fields
static const char* const KEY_STATUS  = "status";
static const char* const KEY_CODE    = "code";
static const char* const KEY_MESSAGE = "message";
static const char* const KEY_DATA    = "data";

// status values
static const char* const STATUS_OK      = "ok";
static const char* const STATUS_ERROR   = "error";
static const char* const STATUS_BUSY    = "busy";
static const char* const STATUS_UNREACHABLE = "unreachable";
static const char* const STATUS_NOT_SUPPORTED = "not_supported";

// error codes
static const char* const ERR_UNKNOWN            = "UNKNOWN";
static const char* const ERR_SENSOR_UNAVAILABLE = "SENSOR_UNAVAILABLE";
static const char* const ERR_NO_FINGER          = "NO_FINGER";
static const char* const ERR_BAD_IMAGE          = "BAD_IMAGE";
static const char* const ERR_IMAGE_MISMATCH     = "IMAGE_MISMATCH";
static const char* const ERR_DUPLICATE          = "DUPLICATE";
static const char* const ERR_INVALID_ID         = "INVALID_ID";
static const char* const ERR_STORAGE_FULL       = "STORAGE_FULL";
static const char* const ERR_TIMEOUT            = "TIMEOUT";
static const char* const ERR_COMMUNICATION      = "COMMUNICATION";
static const char* const ERR_WRITE_FAILED       = "WRITE_FAILED";
static const char* const ERR_RTC_INVALID        = "RTC_INVALID";
static const char* const ERR_RTC_LOST_POWER     = "RTC_LOST_POWER";
static const char* const ERR_NOT_IMPLEMENTED    = "NOT_IMPLEMENTED";

// Enrollment workflow states published on FINGERPRINT_CONTROL characteristic
static const char* const ENROLL_PLACE_FINGER     = "ENROLL_PLACE_FINGER";
static const char* const ENROLL_REMOVE_FINGER    = "ENROLL_REMOVE_FINGER";
static const char* const ENROLL_PLACE_FINGER_AGAIN = "ENROLL_PLACE_FINGER_AGAIN";
static const char* const ENROLL_SUCCESS          = "ENROLL_SUCCESS";
static const char* const ENROLL_FAILED           = "ENROLL_FAILED";

// Diagnostic test names returned by FULL_DIAGNOSTIC
static const char* const DIAG_ESP32        = "ESP32";
static const char* const DIAG_BLE         = "BLE";
static const char* const DIAG_R307S_UART  = "R307S_UART";
static const char* const DIAG_R307S_SENSOR= "R307S_SENSOR";
static const char* const DIAG_FINGERPRINT_DB = "FINGERPRINT_DB";
static const char* const DIAG_DS3231      = "DS3231";
static const char* const DIAG_RTC         = "RTC";
static const char* const DIAG_BUZZER      = "BUZZER";
static const char* const DIAG_STORAGE     = "STORAGE";
static const char* const DIAG_ATTENDANCE  = "ATTENDANCE";

// Diagnostic result values
static const char* const DIAG_PASS   = "PASS";
static const char* const DIAG_FAIL   = "FAIL";
static const char* const DIAG_WARN   = "WARN";
static const char* const DIAG_SKIPPED= "SKIPPED";
