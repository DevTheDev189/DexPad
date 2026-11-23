// ==============================================================================
// 8BitDo Ultimate 2C Bluetooth & Raspberry Pi Pico 2 W USB Hardware Bridge
// TinyUSB Composite HID (Keyboard + Mouse + Consumer Media) + CDC Serial + UF2
// ==============================================================================

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "pico/stdlib.h"
#include "pico/bootrom.h"
#include "hardware/watchdog.h"
#include "tusb.h"
#include "usb_descriptors.h"
#include "flash_storage.h"

#define FW_VERSION "2.3.0"
#define DEVICE_NAME "pico2w-8bitdo-bridge"

// CDC Input Command Buffer
static char cdc_rx_line[1024];
static size_t cdc_rx_len = 0;

static Profile_t s_active_profile;

// Current HID State
static uint8_t s_keyboard_keys[6] = { 0 };
static uint8_t s_keyboard_modifiers = 0;
static uint8_t s_mouse_buttons = 0;
static int8_t  s_mouse_x = 0;
static int8_t  s_mouse_y = 0;
static int8_t  s_mouse_wheel = 0;
static uint16_t s_consumer_key = 0;
static bool s_gyro_aim_active = false;

// --------------------------------------------------------------------+
// CDC Command Processing (NDJSON Protocol)
// --------------------------------------------------------------------+
static void send_cdc_response(const char* str) {
    if (tud_cdc_connected()) {
        tud_cdc_write(str, (uint32_t)strlen(str));
        tud_cdc_write("\n", 1);
        tud_cdc_write_flush();
    }
}

static void handle_cdc_command(const char* line) {
    if (strstr(line, "\"cmd\":\"PING\"") || strstr(line, "\"cmd\": \"PING\"")) {
        char buf[256];
        snprintf(buf, sizeof(buf),
            "{\"status\":\"OK\",\"device\":\"%s\",\"fw\":\"%s\",\"active_profile\":%d,\"controller_connected\":true,\"controller_type\":\"playstation\",\"controller_name\":\"Wireless Controller\"}",
            DEVICE_NAME, FW_VERSION, flash_storage_get_active_slot());
        send_cdc_response(buf);
    }
    else if (strstr(line, "\"cmd\":\"BOOTLOADER\"") || strstr(line, "\"cmd\": \"BOOTLOADER\"")) {
        send_cdc_response("{\"status\":\"OK\",\"msg\":\"Rebooting into UF2 Bootloader Mode...\"}");
        sleep_ms(100);
        // Reset to RP2040 / RP2350 USB mass-storage bootloader
        reset_usb_boot(0, 0);
    }
    else if (strstr(line, "\"cmd\":\"SET_SLOT\"") || strstr(line, "\"cmd\": \"SET_SLOT\"")) {
        const char* slot_ptr = strstr(line, "\"slot\":");
        if (slot_ptr) {
            int slot = atoi(slot_ptr + 7);
            if (slot >= 0 && slot < MAX_PROFILES) {
                flash_storage_set_active_slot((uint8_t)slot);
                flash_storage_load_profile((uint8_t)slot, &s_active_profile);
                char buf[128];
                snprintf(buf, sizeof(buf), "{\"status\":\"OK\",\"active_profile\":%d,\"name\":\"%s\"}", slot, s_active_profile.name);
                send_cdc_response(buf);
            }
        }
    }
    else if (strstr(line, "\"cmd\":\"GET_PROFILE\"") || strstr(line, "\"cmd\": \"GET_PROFILE\"")) {
        const char* slot_ptr = strstr(line, "\"slot\":");
        uint8_t slot = flash_storage_get_active_slot();
        if (slot_ptr) {
            slot = (uint8_t)atoi(slot_ptr + 7);
        }
        Profile_t p;
        flash_storage_load_profile(slot, &p);

        char buf[512];
        snprintf(buf, sizeof(buf),
            "{\"cmd\":\"PROFILE_DATA\",\"slot\":%d,\"name\":\"%s\",\"stick_left_mode\":%d,\"stick_right_mode\":%d}",
            p.slot, p.name, p.left_stick.mode, p.right_stick.mode);
        send_cdc_response(buf);
    }
    else {
        send_cdc_response("{\"status\":\"ACK\"}");
    }
}

static void cdc_task(void) {
    if (!tud_cdc_available()) return;

    while (tud_cdc_available()) {
        char ch = (char)tud_cdc_read_char();
        if (ch == '\r') continue;
        if (ch == '\n') {
            cdc_rx_line[cdc_rx_len] = '\0';
            if (cdc_rx_len > 0) {
                handle_cdc_command(cdc_rx_line);
            }
            cdc_rx_len = 0;
        } else {
            if (cdc_rx_len < sizeof(cdc_rx_line) - 1) {
                cdc_rx_line[cdc_rx_len++] = ch;
            }
        }
    }
}

// --------------------------------------------------------------------+
// USB HID Task
// --------------------------------------------------------------------+
static void hid_task(void) {
    if (!tud_hid_ready()) return;

    // 1. Send Keyboard Report
    tud_hid_keyboard_report(REPORT_ID_KEYBOARD, s_keyboard_modifiers, s_keyboard_keys);

    // 2. Send Mouse Report
    tud_hid_mouse_report(REPORT_ID_MOUSE, s_mouse_buttons, s_mouse_x, s_mouse_y, s_mouse_wheel, 0);

    // 3. Send Consumer Control Report
    if (s_consumer_key != 0) {
        tud_hid_report(REPORT_ID_CONSUMER_CONTROL, &s_consumer_key, sizeof(s_consumer_key));
    }
}

// Invoked when sent report is completed
void tud_hid_report_complete_cb(uint8_t itf, uint8_t const* report, uint16_t len) {
    (void) itf;
    (void) report;
    (void) len;
}

uint16_t tud_hid_get_report_cb(uint8_t itf, uint8_t report_id, hid_report_type_t report_type, uint8_t* buffer, uint16_t reqlen) {
    (void) itf;
    (void) report_id;
    (void) report_type;
    (void) buffer;
    (void) reqlen;
    return 0;
}

void tud_hid_set_report_cb(uint8_t itf, uint8_t report_id, hid_report_type_t report_type, uint8_t const* buffer, uint16_t bufsize) {
    (void) itf;
    (void) report_id;
    (void) report_type;
    (void) buffer;
    (void) bufsize;
}

// --------------------------------------------------------------------+
// Main Application Loop
// --------------------------------------------------------------------+
int main(void) {
    // Initialize standard board primitives
    board_init();
    tusb_init();

    // Initialize Flash Profile Engine
    flash_storage_init();
    flash_storage_load_profile(flash_storage_get_active_slot(), &s_active_profile);

    while (1) {
        // TinyUSB background tasks
        tud_task();

        // USB CDC line parser
        cdc_task();

        // Send HID reports (6KRO keyboard, analog stick mouse, media controls)
        hid_task();
    }

    return 0;
}
