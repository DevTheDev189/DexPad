#ifndef _FLASH_STORAGE_H_
#define _FLASH_STORAGE_H_

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define PROFILE_MAGIC           0x38424954 // "8BIT"
#define MAX_PROFILES            4
#define PROFILE_NAME_MAX_LEN    32

typedef enum {
    BIND_NONE = 0,
    BIND_KEY = 1,
    BIND_MOUSE_BUTTON = 2,
    BIND_MOUSE_SCROLL = 3,
    BIND_CONSUMER = 4,
    BIND_GYRO_AIM = 5
} BindingType_t;

typedef enum {
    STICK_NONE = 0,
    STICK_DIGITAL_KEYS = 1,
    STICK_MOUSE = 2
} StickMode_t;

typedef enum {
    CURVE_LINEAR = 0,
    CURVE_EXPONENTIAL = 1,
    CURVE_AGGRESSIVE = 2
} StickCurve_t;

typedef struct {
    uint8_t type;            // BindingType_t
    uint16_t code;           // Keycode or mouse button mask or consumer control code
    int8_t delta;            // Mouse scroll wheel delta
    uint16_t repeat_ms;      // Scroll repeat period
    uint16_t threshold;      // Trigger threshold (for analog triggers)
    uint8_t gyro_axis;       // 0: pitch/yaw, 1: yaw, 2: roll/pitch
    float gyro_sensitivity;  // Sensitivity multiplier for gyro mouse
} ButtonBinding_t;

typedef struct {
    uint8_t mode;            // StickMode_t
    int16_t deadzone;        // 0 - 500
    float sensitivity;       // 0.1 - 4.0
    uint8_t curve;           // StickCurve_t
    bool invert_y;
    uint16_t up;             // Keycode when pushed UP
    uint16_t down;           // Keycode when pushed DOWN
    uint16_t left;           // Keycode when pushed LEFT
    uint16_t right;          // Keycode when pushed RIGHT
} StickConfig_t;

enum {
    CTRL_A = 0,
    CTRL_B,
    CTRL_X,
    CTRL_Y,
    CTRL_L1,
    CTRL_R1,
    CTRL_L2,
    CTRL_R2,
    CTRL_L3,
    CTRL_R3,
    CTRL_L4,             // 8BitDo Ultimate 2C dedicated left bumper
    CTRL_R4,             // 8BitDo Ultimate 2C dedicated right bumper
    CTRL_DPAD_UP,
    CTRL_DPAD_DOWN,
    CTRL_DPAD_LEFT,
    CTRL_DPAD_RIGHT,
    CTRL_MINUS,          // Select / View
    CTRL_PLUS,           // Start / Menu
    CTRL_HOME,           // 8BitDo Heart / Home button
    CTRL_COUNT
};

typedef struct {
    uint32_t magic;
    uint8_t slot;
    char name[PROFILE_NAME_MAX_LEN];
    StickConfig_t left_stick;
    StickConfig_t right_stick;
    ButtonBinding_t buttons[CTRL_COUNT];
    uint32_t crc32;
} Profile_t;

void flash_storage_init(void);
bool flash_storage_load_profile(uint8_t slot, Profile_t* out_profile);
bool flash_storage_save_profile(uint8_t slot, const Profile_t* profile);
uint8_t flash_storage_get_active_slot(void);
void flash_storage_set_active_slot(uint8_t slot);

#ifdef __cplusplus
}
#endif

#endif // _FLASH_STORAGE_H_
