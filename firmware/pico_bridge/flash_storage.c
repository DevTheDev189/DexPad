#include "flash_storage.h"
#include "hardware/flash.h"
#include "hardware/sync.h"
#include <string.h>

// Reserve upper 16KB of flash (4 sectors)
#ifndef PICO_FLASH_SIZE_BYTES
#define PICO_FLASH_SIZE_BYTES (2 * 1024 * 1024)
#endif

#define FLASH_PROFILE_OFFSET  (PICO_FLASH_SIZE_BYTES - (16 * FLASH_SECTOR_SIZE))
#define FLASH_PROFILE_ADDR    ((const uint8_t *)(XIP_BASE + FLASH_PROFILE_OFFSET))

static uint8_t s_active_slot = 0;

static uint32_t compute_crc32(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < length; i++) {
        crc ^= data[i];
        for (int j = 0; j < 8; j++) {
            crc = (crc >> 1) ^ (0xEDB88320 & (-(crc & 1)));
        }
    }
    return ~crc;
}

static void populate_default_profile(uint8_t slot, Profile_t* p) {
    memset(p, 0, sizeof(Profile_t));
    p->magic = PROFILE_MAGIC;
    p->slot = slot;

    if (slot == 0) {
        // Slot 0: Minecraft
        strncpy(p->name, "Minecraft", sizeof(p->name) - 1);
        p->left_stick.mode = STICK_DIGITAL_KEYS;
        p->left_stick.deadzone = 180;
        p->left_stick.up = 0x1A;    // 'w'
        p->left_stick.down = 0x16;  // 's'
        p->left_stick.left = 0x04;  // 'a'
        p->left_stick.right = 0x07; // 'd'

        p->right_stick.mode = STICK_MOUSE;
        p->right_stick.deadzone = 45;
        p->right_stick.sensitivity = 1.35f;
        p->right_stick.curve = CURVE_EXPONENTIAL;

        // Face buttons & bumpers
        p->buttons[CTRL_A].type = BIND_KEY; p->buttons[CTRL_A].code = 0x2C; // Space (Jump)
        p->buttons[CTRL_B].type = BIND_KEY; p->buttons[CTRL_B].code = 0xE1; // Left Shift (Sneak)
        p->buttons[CTRL_X].type = BIND_KEY; p->buttons[CTRL_X].code = 0x14; // 'q' (Drop)
        p->buttons[CTRL_Y].type = BIND_KEY; p->buttons[CTRL_Y].code = 0x08; // 'e' (Inventory)

        p->buttons[CTRL_L1].type = BIND_MOUSE_SCROLL; p->buttons[CTRL_L1].delta = 1;  p->buttons[CTRL_L1].repeat_ms = 120;
        p->buttons[CTRL_R1].type = BIND_MOUSE_SCROLL; p->buttons[CTRL_R1].delta = -1; p->buttons[CTRL_R1].repeat_ms = 120;

        // 8BitDo Ultimate 2C Dedicated Bumpers:
        p->buttons[CTRL_L4].type = BIND_KEY; p->buttons[CTRL_L4].code = 0xE0; // Left Ctrl (Sprint)
        p->buttons[CTRL_R4].type = BIND_KEY; p->buttons[CTRL_R4].code = 0x2C; // Space (Jump)

        p->buttons[CTRL_L2].type = BIND_MOUSE_BUTTON; p->buttons[CTRL_L2].code = 0x02; // Right Click
        p->buttons[CTRL_R2].type = BIND_MOUSE_BUTTON; p->buttons[CTRL_R2].code = 0x01; // Left Click

        p->buttons[CTRL_DPAD_UP].type = BIND_KEY;    p->buttons[CTRL_DPAD_UP].code = 0x3E; // F5 (Perspective)
        p->buttons[CTRL_DPAD_DOWN].type = BIND_KEY;  p->buttons[CTRL_DPAD_DOWN].code = 0x3C; // F3 (Debug)
        p->buttons[CTRL_MINUS].type = BIND_KEY;      p->buttons[CTRL_MINUS].code = 0x2B; // Tab (Player List)
        p->buttons[CTRL_PLUS].type = BIND_KEY;       p->buttons[CTRL_PLUS].code = 0x29; // Esc (Pause)
    } else if (slot == 1) {
        // Slot 1: 2D Platformer (Hollow Knight)
        strncpy(p->name, "2D Platformer", sizeof(p->name) - 1);
        p->left_stick.mode = STICK_DIGITAL_KEYS;
        p->left_stick.deadzone = 150;
        p->left_stick.up = 0x52;    // Up Arrow
        p->left_stick.down = 0x51;  // Down Arrow
        p->left_stick.left = 0x50;  // Left Arrow
        p->left_stick.right = 0x4F; // Right Arrow

        p->buttons[CTRL_A].type = BIND_KEY; p->buttons[CTRL_A].code = 0x1D; // 'z' (Jump)
        p->buttons[CTRL_X].type = BIND_KEY; p->buttons[CTRL_X].code = 0x1B; // 'x' (Slash)
        p->buttons[CTRL_Y].type = BIND_KEY; p->buttons[CTRL_Y].code = 0x04; // 'a' (Cast)
        p->buttons[CTRL_B].type = BIND_KEY; p->buttons[CTRL_B].code = 0x06; // 'c' (Dash)
        p->buttons[CTRL_L4].type = BIND_KEY; p->buttons[CTRL_L4].code = 0x06; // 'c' (Quick Dash)
        p->buttons[CTRL_R4].type = BIND_KEY; p->buttons[CTRL_R4].code = 0x04; // 'a' (Quick Cast)
    } else if (slot == 2) {
        // Slot 2: Desktop Mouse & Media
        strncpy(p->name, "Desktop Mouse", sizeof(p->name) - 1);
        p->right_stick.mode = STICK_MOUSE;
        p->right_stick.deadzone = 30;
        p->right_stick.sensitivity = 1.6f;
        p->right_stick.curve = CURVE_EXPONENTIAL;

        p->buttons[CTRL_A].type = BIND_MOUSE_BUTTON; p->buttons[CTRL_A].code = 0x01; // Left Click
        p->buttons[CTRL_B].type = BIND_MOUSE_BUTTON; p->buttons[CTRL_B].code = 0x02; // Right Click
        p->buttons[CTRL_X].type = BIND_MOUSE_BUTTON; p->buttons[CTRL_X].code = 0x04; // Middle Click

        p->buttons[CTRL_L1].type = BIND_MOUSE_SCROLL; p->buttons[CTRL_L1].delta = 1;  p->buttons[CTRL_L1].repeat_ms = 100;
        p->buttons[CTRL_R1].type = BIND_MOUSE_SCROLL; p->buttons[CTRL_R1].delta = -1; p->buttons[CTRL_R1].repeat_ms = 100;

        // Consumer Control Media Keys
        p->buttons[CTRL_L4].type = BIND_CONSUMER; p->buttons[CTRL_L4].code = 0x00EA; // Volume Down
        p->buttons[CTRL_R4].type = BIND_CONSUMER; p->buttons[CTRL_R4].code = 0x00E9; // Volume Up
        p->buttons[CTRL_Y].type = BIND_CONSUMER;  p->buttons[CTRL_Y].code = 0x00CD; // Play / Pause
        p->buttons[CTRL_L2].type = BIND_CONSUMER; p->buttons[CTRL_L2].code = 0x00B6; // Prev Track
        p->buttons[CTRL_R2].type = BIND_CONSUMER; p->buttons[CTRL_R2].code = 0x00B5; // Next Track
    } else {
        // Slot 3: Action FPS with Gyro Aim
        strncpy(p->name, "Action FPS", sizeof(p->name) - 1);
        p->left_stick.mode = STICK_DIGITAL_KEYS;
        p->left_stick.deadzone = 160;
        p->left_stick.up = 0x1A; p->left_stick.down = 0x16; p->left_stick.left = 0x04; p->left_stick.right = 0x07;

        p->right_stick.mode = STICK_MOUSE;
        p->right_stick.deadzone = 40;
        p->right_stick.sensitivity = 1.5f;

        p->buttons[CTRL_A].type = BIND_KEY; p->buttons[CTRL_A].code = 0x2C; // Space
        p->buttons[CTRL_B].type = BIND_KEY; p->buttons[CTRL_B].code = 0x06; // 'c' (Crouch)
        p->buttons[CTRL_X].type = BIND_KEY; p->buttons[CTRL_X].code = 0x15; // 'r' (Reload)
        p->buttons[CTRL_Y].type = BIND_KEY; p->buttons[CTRL_Y].code = 0x09; // 'f' (Interact)
        p->buttons[CTRL_L2].type = BIND_MOUSE_BUTTON; p->buttons[CTRL_L2].code = 0x02; // Aim Down Sights
        p->buttons[CTRL_R2].type = BIND_MOUSE_BUTTON; p->buttons[CTRL_R2].code = 0x01; // Fire

        // Hold L4 for Gyro Aiming!
        p->buttons[CTRL_L4].type = BIND_GYRO_AIM;
        p->buttons[CTRL_L4].gyro_axis = 0; // pitch/yaw
        p->buttons[CTRL_L4].gyro_sensitivity = 1.2f;

        p->buttons[CTRL_R4].type = BIND_KEY; p->buttons[CTRL_R4].code = 0xE1; // Left Shift (Sprint)
    }

    p->crc32 = compute_crc32((const uint8_t*)p, sizeof(Profile_t) - sizeof(uint32_t));
}

void flash_storage_init(void) {
    // Check if slot 0 is valid in flash
    Profile_t test_p;
    if (!flash_storage_load_profile(0, &test_p)) {
        // Flash uninitialized: write default profiles to flash
        for (uint8_t i = 0; i < MAX_PROFILES; i++) {
            Profile_t def;
            populate_default_profile(i, &def);
            flash_storage_save_profile(i, &def);
        }
    }
}

bool flash_storage_load_profile(uint8_t slot, Profile_t* out_profile) {
    if (slot >= MAX_PROFILES || !out_profile) return false;

    const Profile_t* stored = (const Profile_t*)(FLASH_PROFILE_ADDR + (slot * FLASH_SECTOR_SIZE));
    if (stored->magic != PROFILE_MAGIC) {
        populate_default_profile(slot, out_profile);
        return false;
    }

    uint32_t expected_crc = compute_crc32((const uint8_t*)stored, sizeof(Profile_t) - sizeof(uint32_t));
    if (expected_crc != stored->crc32) {
        populate_default_profile(slot, out_profile);
        return false;
    }

    memcpy(out_profile, stored, sizeof(Profile_t));
    return true;
}

bool flash_storage_save_profile(uint8_t slot, const Profile_t* profile) {
    if (slot >= MAX_PROFILES || !profile) return false;

    // Buffer one full sector (4KB)
    uint8_t sector_buf[FLASH_SECTOR_SIZE];
    memset(sector_buf, 0xFF, sizeof(sector_buf));

    Profile_t p_copy;
    memcpy(&p_copy, profile, sizeof(Profile_t));
    p_copy.magic = PROFILE_MAGIC;
    p_copy.slot = slot;
    p_copy.crc32 = compute_crc32((const uint8_t*)&p_copy, sizeof(Profile_t) - sizeof(uint32_t));

    memcpy(sector_buf, &p_copy, sizeof(Profile_t));

    uint32_t target_offset = FLASH_PROFILE_OFFSET + (slot * FLASH_SECTOR_SIZE);

    // Disable interrupts safely while writing SPI flash
    uint32_t ints = save_and_disable_interrupts();
    flash_range_erase(target_offset, FLASH_SECTOR_SIZE);
    flash_range_program(target_offset, sector_buf, FLASH_SECTOR_SIZE);
    restore_interrupts(ints);

    return true;
}

uint8_t flash_storage_get_active_slot(void) {
    return s_active_slot;
}

void flash_storage_set_active_slot(uint8_t slot) {
    if (slot < MAX_PROFILES) {
        s_active_slot = slot;
    }
}
