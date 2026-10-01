/**
 * @file fingerprint_sensor.h
 * @brief Hardware Abstraction Layer Interface for R307S Optical Fingerprint Sensor
 * @project Biometric School Attendance System
 * 
 * IMPORTANT ARCHITECTURAL NOTICE:
 * This header defines the planned hardware abstraction interface for the R307S sensor.
 * Implementation is BLOCKED until physical verification gates (Phases 1-3 in
 * docs/r307s-integration-plan.md) are completed.
 * 
 * DO NOT IMPLEMENT UNVERIFIED PROTOCOL LOGIC HERE.
 */

#ifndef FINGERPRINT_SENSOR_H
#define FINGERPRINT_SENSOR_H

#include <Arduino.h>
#include <Adafruit_Fingerprint.h>
#include "config.h"

/**
 * @brief Operational states of the fingerprint subsystem
 */
enum class FingerprintState {
    UNINITIALIZED,      ///< Sensor has not been probed or configured
    HARDWARE_CHECK,     ///< Checking electrical and UART connectivity
    COMM_ERROR,         ///< UART handshake failed or timed out
    READY,              ///< Sensor initialized and standing by for finger
    SCANNING,           ///< Optical capture in progress
    MATCH_FOUND,        ///< 1:N match succeeded (slot ID returned)
    NO_MATCH,           ///< Fingerprint not found in onboard template database
    ENROLL_STEP1,       ///< Capturing first impression for enrollment
    ENROLL_STEP2,       ///< Capturing second impression for model creation
    ENROLL_SUCCESS,     ///< Template saved to flash slot
    ENROLL_FAILED       ///< Enrollment rejected (poor quality or mismatched impressions)
};

/**
 * @brief Hardware parameters reported by sensor during Phase 6 status query
 */
struct R307S_Parameters {
    uint16_t status_reg;        ///< Status register content
    uint16_t system_id;         ///< Sensor system identifier code
    uint16_t capacity;          ///< Fingerprint template capacity (expected: 1000)
    uint16_t security_level;    ///< Security/matching threshold level (1-5)
    uint32_t device_address;    ///< Default 32-bit device address (0xFFFFFFFF)
    uint16_t packet_size;       ///< Data packet payload size (32, 64, 128, 256 bytes)
    uint16_t baud_rate;         ///< Configured UART baud rate setting
    bool parameters_valid;      ///< True if successfully queried from module
};

/**
 * @brief Result structure returned from a 1:N biometric search
 */
struct FingerprintMatchResult {
    bool matched;               ///< True if finger recognized in internal flash
    uint16_t slot_id;           ///< 1-based template slot ID (1..capacity)
    uint16_t confidence_score;  ///< Match confidence score reported by sensor
    FingerprintState status;    ///< Execution status outcome
};

/*
 * Planned Hardware Driver Interface (Phases 4 - 9)
 * -------------------------------------------------------------------
 * The following function prototypes outline the planned driver API.
 * Implementation will be written once Phase 1 (pinout/voltage) is verified.
 */

// Phase 4 & 5: Hardware initialization and communication verification
bool fingerprint_init_uart(uint32_t baud_rate = R307S_BAUD_RATE);
bool fingerprint_verify_connection(void);

// Phase 6: System parameter query
bool fingerprint_query_parameters(R307S_Parameters* out_params);

// Phase 7: Biometric enrollment (2-pass capture into specified slot)
bool fingerprint_enroll_slot(uint16_t target_slot_id, void (*progress_cb)(FingerprintState));

// Phase 8: Biometric search (1:N matching)
FingerprintMatchResult fingerprint_scan_and_match(void);

// Maintenance
bool fingerprint_delete_slot(uint16_t slot_id);
bool fingerprint_clear_database(void);

#endif // FINGERPRINT_SENSOR_H
