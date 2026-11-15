/**
 * ============================================================================
 * Nimbus+ Cosmic Bridge - ESP32-S3 Firmware
 * ============================================================================
 * Hardware: ESP32-S3 (Dual-core, Native USB OTG CDC + HID)
 * Controller: SteelSeries Nimbus+ (Apple MFi / Bluetooth Gamepad)
 * Features:
 *   - Bluepad32 Bluetooth Gamepad Host (zero-config auto-reconnect)
 *   - Native USB Composite Keyboard + Mouse (No macOS drivers or daemons needed)
 *   - ArduinoJson v7 / Preferences (NVS) persistence for 4 custom profile slots
 *   - 115200 Baud Newline-delimited JSON Serial Control Protocol
 *   - 125Hz throttled sub-pixel mouse movement with curve smoothing
 *   - Hardware profile switching shortcut: Home + D-Pad Left / Right
 *   - Optional 30Hz live input telemetry streaming
 * ============================================================================
 */

#include <Arduino.h>
#include <Bluepad32.h>
#include <Preferences.h>
#include <ArduinoJson.h>

// ESP32 Native USB HID
#if defined(CONFIG_TINYUSB_ENABLED) || defined(USE_TINYUSB)
  #include <Adafruit_TinyUSB.h>
#else
  #include "USB.h"
  #include "USBHIDKeyboard.h"
  #include "USBHIDMouse.h"
  USBHIDKeyboard Keyboard;
  USBHIDMouse Mouse;
#endif

// ============================================================================
// Constants & Enums
// ============================================================================
#define FIRMWARE_VERSION       "2.0.0"
#define DEVICE_NAME            "nimbus-s3-bridge"
#define MAX_PROFILES           4
#define SERIAL_BAUD            115200
#define SERIAL_BUF_SIZE        2048
#define MOUSE_POLL_INTERVAL_MS 8      // 125 Hz mouse update rate
#define TELEMETRY_INTERVAL_MS  33     // ~30 Hz telemetry stream rate

// Binding Types
enum BindingType {
  BIND_NONE = 0,
  BIND_KEY,
  BIND_MOUSE_BUTTON,
  BIND_MOUSE_SCROLL
};

// Stick Modes
enum StickMode {
  STICK_MODE_NONE = 0,
  STICK_MODE_DIGITAL_KEYS,
  STICK_MODE_MOUSE
};

// Stick Curves
enum StickCurve {
  CURVE_LINEAR = 0,
  CURVE_EXPONENTIAL,
  CURVE_AGGRESSIVE
};

// Button IDs
enum ControllerButtonId {
  BTN_A = 0,
  BTN_B,
  BTN_X,
  BTN_Y,
  BTN_L1,
  BTN_R1,
  BTN_L2,
  BTN_R2,
  BTN_L3,
  BTN_R3,
  BTN_DPAD_UP,
  BTN_DPAD_DOWN,
  BTN_DPAD_LEFT,
  BTN_DPAD_RIGHT,
  BTN_MENU,
  BTN_OPTIONS,
  BTN_HOME,
  TOTAL_BUTTONS
};

const char* BUTTON_NAMES[TOTAL_BUTTONS] = {
  "a", "b", "x", "y",
  "l1", "r1", "l2", "r2",
  "l3", "r3",
  "dpad_up", "dpad_down", "dpad_left", "dpad_right",
  "menu", "options", "home"
};

// ============================================================================
// Data Structures
// ============================================================================
struct ButtonBinding {
  BindingType type;
  uint8_t hidCode;          // Keyboard keycode or mouse button mask
  int8_t scrollDelta;       // For mouse_scroll (+1 or -1)
  uint16_t repeatMs;        // Cooldown for scroll repeat (default 120ms)
  uint16_t threshold;       // Analog trigger activation threshold (0..1023)
  char codeStr[32];         // Original keycode label for JSON export
};

struct StickDigitalConfig {
  uint8_t upCode;
  uint8_t downCode;
  uint8_t leftCode;
  uint8_t rightCode;
  char upStr[16];
  char downStr[16];
  char leftStr[16];
  char rightStr[16];
};

struct StickMouseConfig {
  float sensitivity;
  StickCurve curve;
  bool invertY;
};

struct StickConfig {
  StickMode mode;
  int16_t deadzone;
  StickDigitalConfig digital;
  StickMouseConfig mouse;
};

struct Profile {
  char name[32];
  StickConfig leftStick;
  StickConfig rightStick;
  ButtonBinding buttons[TOTAL_BUTTONS];
};

// ============================================================================
// Global State
// ============================================================================
Preferences prefs;
Profile currentProfile;
uint8_t activeSlot = 0;
bool telemetryEnabled = false;

GamepadPtr connectedGamepad = nullptr;

// Live input tracking for transitions
bool rawButtonState[TOTAL_BUTTONS] = {false};
bool prevButtonState[TOTAL_BUTTONS] = {false};
unsigned long lastScrollTime[TOTAL_BUTTONS] = {0};

// Mouse movement sub-pixel accumulators
float mouseSubX = 0.0f;
float mouseSubY = 0.0f;
unsigned long lastMouseUpdate = 0;
unsigned long lastTelemetryUpdate = 0;

// Shortcut debounce for Home + D-Pad slot switching
bool shortcutTriggered = false;

// Serial RX buffer
char serialRxBuffer[SERIAL_BUF_SIZE];
size_t serialRxIndex = 0;

// ============================================================================
// Keycode Resolver Table
// ============================================================================
uint8_t resolveKeycode(const char* name) {
  if (!name || strlen(name) == 0) return 0;

  // Single characters
  if (strlen(name) == 1) {
    char c = name[0];
    if (c >= 'a' && c <= 'z') return c;
    if (c >= 'A' && c <= 'Z') return c + 32; // Standardize lowercase
    if (c >= '0' && c <= '9') return c;
    return (uint8_t)c;
  }

  // Common Key definitions
  if (strcasecmp(name, "KEY_SPACE") == 0 || strcasecmp(name, "SPACE") == 0) return ' ';
  if (strcasecmp(name, "KEY_RETURN") == 0 || strcasecmp(name, "RETURN") == 0 || strcasecmp(name, "ENTER") == 0) return 0xB0; // KEY_RETURN
  if (strcasecmp(name, "KEY_ESC") == 0 || strcasecmp(name, "ESCAPE") == 0) return 0xB1; // KEY_ESC
  if (strcasecmp(name, "KEY_BACKSPACE") == 0) return 0xB2;
  if (strcasecmp(name, "KEY_TAB") == 0) return 0xB3;
  
  // Modifiers
  if (strcasecmp(name, "KEY_LEFT_CTRL") == 0 || strcasecmp(name, "LCTRL") == 0) return 0x80;
  if (strcasecmp(name, "KEY_LEFT_SHIFT") == 0 || strcasecmp(name, "LSHIFT") == 0) return 0x81;
  if (strcasecmp(name, "KEY_LEFT_ALT") == 0 || strcasecmp(name, "LALT") == 0 || strcasecmp(name, "OPTION") == 0) return 0x82;
  if (strcasecmp(name, "KEY_LEFT_GUI") == 0 || strcasecmp(name, "LGUI") == 0 || strcasecmp(name, "COMMAND") == 0 || strcasecmp(name, "CMD") == 0) return 0x83;
  if (strcasecmp(name, "KEY_RIGHT_CTRL") == 0) return 0x84;
  if (strcasecmp(name, "KEY_RIGHT_SHIFT") == 0) return 0x85;
  if (strcasecmp(name, "KEY_RIGHT_ALT") == 0) return 0x86;
  if (strcasecmp(name, "KEY_RIGHT_GUI") == 0) return 0x87;

  // Arrow keys
  if (strcasecmp(name, "KEY_UP_ARROW") == 0 || strcasecmp(name, "UP") == 0) return 0xDA;
  if (strcasecmp(name, "KEY_DOWN_ARROW") == 0 || strcasecmp(name, "DOWN") == 0) return 0xD9;
  if (strcasecmp(name, "KEY_LEFT_ARROW") == 0 || strcasecmp(name, "LEFT") == 0) return 0xD8;
  if (strcasecmp(name, "KEY_RIGHT_ARROW") == 0 || strcasecmp(name, "RIGHT") == 0) return 0xD7;

  // Function keys F1 - F12
  if (strcasecmp(name, "KEY_F1") == 0 || strcasecmp(name, "F1") == 0) return 0xC2;
  if (strcasecmp(name, "KEY_F2") == 0 || strcasecmp(name, "F2") == 0) return 0xC3;
  if (strcasecmp(name, "KEY_F3") == 0 || strcasecmp(name, "F3") == 0) return 0xC4;
  if (strcasecmp(name, "KEY_F4") == 0 || strcasecmp(name, "F4") == 0) return 0xC5;
  if (strcasecmp(name, "KEY_F5") == 0 || strcasecmp(name, "F5") == 0) return 0xC6;
  if (strcasecmp(name, "KEY_F6") == 0 || strcasecmp(name, "F6") == 0) return 0xC7;
  if (strcasecmp(name, "KEY_F7") == 0 || strcasecmp(name, "F7") == 0) return 0xC8;
  if (strcasecmp(name, "KEY_F8") == 0 || strcasecmp(name, "F8") == 0) return 0xC9;
  if (strcasecmp(name, "KEY_F9") == 0 || strcasecmp(name, "F9") == 0) return 0xCA;
  if (strcasecmp(name, "KEY_F10") == 0 || strcasecmp(name, "F10") == 0) return 0xCB;
  if (strcasecmp(name, "KEY_F11") == 0 || strcasecmp(name, "F11") == 0) return 0xCC;
  if (strcasecmp(name, "KEY_F12") == 0 || strcasecmp(name, "F12") == 0) return 0xCD;

  return 0;
}

uint8_t resolveMouseButton(const char* name) {
  if (!name) return 1; // Default MOUSE_LEFT
  if (strcasecmp(name, "MOUSE_RIGHT") == 0 || strcasecmp(name, "RIGHT") == 0) return 2; // MOUSE_RIGHT
  if (strcasecmp(name, "MOUSE_MIDDLE") == 0 || strcasecmp(name, "MIDDLE") == 0) return 4; // MOUSE_MIDDLE
  return 1; // MOUSE_LEFT
}

// ============================================================================
// Default Profiles
// ============================================================================
void loadDefaultProfile(uint8_t slot, Profile* p) {
  memset(p, 0, sizeof(Profile));

  if (slot == 0) {
    // Slot 0: Minecraft Preset
    strncpy(p->name, "Minecraft", sizeof(p->name) - 1);
    
    // Left Stick -> WASD
    p->leftStick.mode = STICK_MODE_DIGITAL_KEYS;
    p->leftStick.deadzone = 180;
    p->leftStick.digital.upCode = 'w';
    p->leftStick.digital.downCode = 's';
    p->leftStick.digital.leftCode = 'a';
    p->leftStick.digital.rightCode = 'd';
    strcpy(p->leftStick.digital.upStr, "w");
    strcpy(p->leftStick.digital.downStr, "s");
    strcpy(p->leftStick.digital.leftStr, "a");
    strcpy(p->leftStick.digital.rightStr, "d");

    // Right Stick -> Smooth Mouse
    p->rightStick.mode = STICK_MODE_MOUSE;
    p->rightStick.deadzone = 45;
    p->rightStick.mouse.sensitivity = 1.35f;
    p->rightStick.mouse.curve = CURVE_EXPONENTIAL;
    p->rightStick.mouse.invertY = false;

    // Buttons
    p->buttons[BTN_A] = { BIND_KEY, ' ', 0, 0, 0, "KEY_SPACE" };
    p->buttons[BTN_B] = { BIND_KEY, 0x81, 0, 0, 0, "KEY_LEFT_SHIFT" };
    p->buttons[BTN_X] = { BIND_KEY, 'q', 0, 0, 0, "q" };
    p->buttons[BTN_Y] = { BIND_KEY, 'e', 0, 0, 0, "e" };
    p->buttons[BTN_L1] = { BIND_MOUSE_SCROLL, 0, 1, 120, 0, "SCROLL_UP" };
    p->buttons[BTN_R1] = { BIND_MOUSE_SCROLL, 0, -1, 120, 0, "SCROLL_DOWN" };
    p->buttons[BTN_L2] = { BIND_MOUSE_BUTTON, 2, 0, 0, 40, "MOUSE_RIGHT" };
    p->buttons[BTN_R2] = { BIND_MOUSE_BUTTON, 1, 0, 0, 40, "MOUSE_LEFT" };
    p->buttons[BTN_L3] = { BIND_KEY, 0x80, 0, 0, 0, "KEY_LEFT_CTRL" };
    p->buttons[BTN_R3] = { BIND_KEY, 'f', 0, 0, 0, "f" };
    p->buttons[BTN_DPAD_UP] = { BIND_KEY, 0xC6, 0, 0, 0, "KEY_F5" };
    p->buttons[BTN_DPAD_DOWN] = { BIND_KEY, 0xC4, 0, 0, 0, "KEY_F3" };
    p->buttons[BTN_DPAD_LEFT] = { BIND_KEY, '1', 0, 0, 0, "1" };
    p->buttons[BTN_DPAD_RIGHT] = { BIND_KEY, 't', 0, 0, 0, "t" };
    p->buttons[BTN_MENU] = { BIND_KEY, 0xB1, 0, 0, 0, "KEY_ESC" };
    p->buttons[BTN_OPTIONS] = { BIND_KEY, 0xB0, 0, 0, 0, "KEY_RETURN" };
    p->buttons[BTN_HOME] = { BIND_KEY, 0xB3, 0, 0, 0, "KEY_TAB" };
  } else if (slot == 1) {
    // Slot 1: Hollow Knight / 2D Platformer
    strncpy(p->name, "2D Platformer", sizeof(p->name) - 1);
    p->leftStick.mode = STICK_MODE_DIGITAL_KEYS;
    p->leftStick.deadzone = 150;
    p->leftStick.digital.upCode = 0xDA; // UP
    p->leftStick.digital.downCode = 0xD9; // DOWN
    p->leftStick.digital.leftCode = 0xD8; // LEFT
    p->leftStick.digital.rightCode = 0xD7; // RIGHT
    strcpy(p->leftStick.digital.upStr, "KEY_UP_ARROW");
    strcpy(p->leftStick.digital.downStr, "KEY_DOWN_ARROW");
    strcpy(p->leftStick.digital.leftStr, "KEY_LEFT_ARROW");
    strcpy(p->leftStick.digital.rightStr, "KEY_RIGHT_ARROW");

    p->rightStick.mode = STICK_MODE_NONE;
    p->buttons[BTN_A] = { BIND_KEY, 'z', 0, 0, 0, "z" }; // Jump
    p->buttons[BTN_X] = { BIND_KEY, 'x', 0, 0, 0, "x" }; // Attack
    p->buttons[BTN_Y] = { BIND_KEY, 'a', 0, 0, 0, "a" }; // Focus / Cast
    p->buttons[BTN_B] = { BIND_KEY, 'c', 0, 0, 0, "c" }; // Dash
    p->buttons[BTN_R2] = { BIND_KEY, 0x81, 0, 0, 40, "KEY_LEFT_SHIFT" };
    p->buttons[BTN_MENU] = { BIND_KEY, 0xB1, 0, 0, 0, "KEY_ESC" };
    p->buttons[BTN_HOME] = { BIND_KEY, 0xB3, 0, 0, 0, "KEY_TAB" };
  } else if (slot == 2) {
    // Slot 2: Desktop Mouse Mode
    strncpy(p->name, "Desktop Mouse", sizeof(p->name) - 1);
    p->leftStick.mode = STICK_MODE_NONE;
    p->rightStick.mode = STICK_MODE_MOUSE;
    p->rightStick.deadzone = 30;
    p->rightStick.mouse.sensitivity = 1.6f;
    p->rightStick.mouse.curve = CURVE_EXPONENTIAL;
    p->rightStick.mouse.invertY = false;

    p->buttons[BTN_A] = { BIND_MOUSE_BUTTON, 1, 0, 0, 0, "MOUSE_LEFT" };
    p->buttons[BTN_B] = { BIND_MOUSE_BUTTON, 2, 0, 0, 0, "MOUSE_RIGHT" };
    p->buttons[BTN_X] = { BIND_MOUSE_BUTTON, 4, 0, 0, 0, "MOUSE_MIDDLE" };
    p->buttons[BTN_L1] = { BIND_MOUSE_SCROLL, 0, 1, 100, 0, "SCROLL_UP" };
    p->buttons[BTN_R1] = { BIND_MOUSE_SCROLL, 0, -1, 100, 0, "SCROLL_DOWN" };
    p->buttons[BTN_HOME] = { BIND_KEY, 0x83, 0, 0, 0, "COMMAND" }; // macOS Mission Control / App Switch
  } else {
    // Slot 3: Action / FPS
    strncpy(p->name, "Action FPS", sizeof(p->name) - 1);
    p->leftStick.mode = STICK_MODE_DIGITAL_KEYS;
    p->leftStick.deadzone = 160;
    p->leftStick.digital.upCode = 'w';
    p->leftStick.digital.downCode = 's';
    p->leftStick.digital.leftCode = 'a';
    p->leftStick.digital.rightCode = 'd';
    strcpy(p->leftStick.digital.upStr, "w");
    strcpy(p->leftStick.digital.downStr, "s");
    strcpy(p->leftStick.digital.leftStr, "a");
    strcpy(p->leftStick.digital.rightStr, "d");

    p->rightStick.mode = STICK_MODE_MOUSE;
    p->rightStick.deadzone = 40;
    p->rightStick.mouse.sensitivity = 1.5f;
    p->rightStick.mouse.curve = CURVE_LINEAR;
    p->rightStick.mouse.invertY = false;

    p->buttons[BTN_A] = { BIND_KEY, ' ', 0, 0, 0, "KEY_SPACE" };
    p->buttons[BTN_B] = { BIND_KEY, 'c', 0, 0, 0, "c" };
    p->buttons[BTN_X] = { BIND_KEY, 'r', 0, 0, 0, "r" }; // Reload
    p->buttons[BTN_Y] = { BIND_KEY, 'f', 0, 0, 0, "f" }; // Interact
    p->buttons[BTN_L2] = { BIND_MOUSE_BUTTON, 2, 0, 0, 40, "MOUSE_RIGHT" }; // Aim
    p->buttons[BTN_R2] = { BIND_MOUSE_BUTTON, 1, 0, 0, 40, "MOUSE_LEFT" };  // Shoot
    p->buttons[BTN_L3] = { BIND_KEY, 0x81, 0, 0, 0, "KEY_LEFT_SHIFT" }; // Sprint
  }
}

// ============================================================================
// NVS Storage Persistence
// ============================================================================
void saveProfileToNVS(uint8_t slot, const Profile& p) {
  if (slot >= MAX_PROFILES) return;
  char key[16];
  snprintf(key, sizeof(key), "prof_%u", slot);
  prefs.putBytes(key, &p, sizeof(Profile));
}

bool loadProfileFromNVS(uint8_t slot, Profile* p) {
  if (slot >= MAX_PROFILES) return false;
  char key[16];
  snprintf(key, sizeof(key), "prof_%u", slot);
  size_t bytesRead = prefs.getBytes(key, p, sizeof(Profile));
  if (bytesRead == sizeof(Profile)) {
    return true;
  }
  return false;
}

void switchActiveSlot(uint8_t slot) {
  if (slot >= MAX_PROFILES) slot = 0;
  activeSlot = slot;
  prefs.putUChar("active_slot", activeSlot);

  if (!loadProfileFromNVS(activeSlot, &currentProfile)) {
    loadDefaultProfile(activeSlot, &currentProfile);
    saveProfileToNVS(activeSlot, currentProfile);
  }

  // Update controller LED indicator if connected
  if (connectedGamepad) {
    // Light up 1..4 LEDs according to slot (slot 0 -> 1 LED, etc.)
    connectedGamepad->setPlayerLEDs(1 << activeSlot);
  }
}

// ============================================================================
// JSON Serialization / Deserialization
// ============================================================================
void serializeProfileToJson(const Profile& p, uint8_t slot, JsonDocument& doc) {
  doc["slot"] = slot;
  doc["name"] = p.name;

  // Sticks
  JsonObject sticks = doc["sticks"].to<JsonObject>();
  
  // Left Stick
  JsonObject left = sticks["left"].to<JsonObject>();
  left["mode"] = (p.leftStick.mode == STICK_MODE_DIGITAL_KEYS) ? "digital_keys" :
                 (p.leftStick.mode == STICK_MODE_MOUSE) ? "mouse" : "none";
  left["deadzone"] = p.leftStick.deadzone;
  if (p.leftStick.mode == STICK_MODE_DIGITAL_KEYS) {
    left["up"] = p.leftStick.digital.upStr;
    left["down"] = p.leftStick.digital.downStr;
    left["left"] = p.leftStick.digital.leftStr;
    left["right"] = p.leftStick.digital.rightStr;
  }

  // Right Stick
  JsonObject right = sticks["right"].to<JsonObject>();
  right["mode"] = (p.rightStick.mode == STICK_MODE_MOUSE) ? "mouse" :
                  (p.rightStick.mode == STICK_MODE_DIGITAL_KEYS) ? "digital_keys" : "none";
  right["deadzone"] = p.rightStick.deadzone;
  if (p.rightStick.mode == STICK_MODE_MOUSE) {
    right["sensitivity"] = p.rightStick.mouse.sensitivity;
    right["curve"] = (p.rightStick.mouse.curve == CURVE_LINEAR) ? "linear" :
                     (p.rightStick.mouse.curve == CURVE_EXPONENTIAL) ? "exponential" : "aggressive";
    right["invert_y"] = p.rightStick.mouse.invertY;
  }

  // Buttons
  JsonObject btns = doc["buttons"].to<JsonObject>();
  for (int i = 0; i < TOTAL_BUTTONS; i++) {
    const ButtonBinding& b = p.buttons[i];
    JsonObject btnObj = btns[BUTTON_NAMES[i]].to<JsonObject>();

    if (b.type == BIND_KEY) {
      btnObj["type"] = "key";
      btnObj["code"] = b.codeStr;
    } else if (b.type == BIND_MOUSE_BUTTON) {
      btnObj["type"] = "mouse_button";
      btnObj["code"] = b.codeStr;
      if (b.threshold > 0) btnObj["threshold"] = b.threshold;
    } else if (b.type == BIND_MOUSE_SCROLL) {
      btnObj["type"] = "mouse_scroll";
      btnObj["delta"] = b.scrollDelta;
      btnObj["repeat_ms"] = b.repeatMs;
    } else {
      btnObj["type"] = "none";
    }
  }
}

void parseProfileFromJson(const JsonDocument& doc, Profile* p) {
  if (doc["name"].is<const char*>()) {
    strncpy(p->name, doc["name"], sizeof(p->name) - 1);
  }

  // Sticks
  if (doc["sticks"].is<JsonObjectConst>()) {
    JsonObjectConst sticks = doc["sticks"];
    if (sticks["left"].is<JsonObjectConst>()) {
      JsonObjectConst l = sticks["left"];
      const char* mode = l["mode"] | "digital_keys";
      if (strcmp(mode, "digital_keys") == 0) {
        p->leftStick.mode = STICK_MODE_DIGITAL_KEYS;
      } else if (strcmp(mode, "mouse") == 0) {
        p->leftStick.mode = STICK_MODE_MOUSE;
      } else {
        p->leftStick.mode = STICK_MODE_NONE;
      }
      p->leftStick.deadzone = l["deadzone"] | 180;
      if (l["up"].is<const char*>()) {
        strncpy(p->leftStick.digital.upStr, l["up"], sizeof(p->leftStick.digital.upStr) - 1);
        p->leftStick.digital.upCode = resolveKeycode(p->leftStick.digital.upStr);
      }
      if (l["down"].is<const char*>()) {
        strncpy(p->leftStick.digital.downStr, l["down"], sizeof(p->leftStick.digital.downStr) - 1);
        p->leftStick.digital.downCode = resolveKeycode(p->leftStick.digital.downStr);
      }
      if (l["left"].is<const char*>()) {
        strncpy(p->leftStick.digital.leftStr, l["left"], sizeof(p->leftStick.digital.leftStr) - 1);
        p->leftStick.digital.leftCode = resolveKeycode(p->leftStick.digital.leftStr);
      }
      if (l["right"].is<const char*>()) {
        strncpy(p->leftStick.digital.rightStr, l["right"], sizeof(p->leftStick.digital.rightStr) - 1);
        p->leftStick.digital.rightCode = resolveKeycode(p->leftStick.digital.rightStr);
      }
    }

    if (sticks["right"].is<JsonObjectConst>()) {
      JsonObjectConst r = sticks["right"];
      const char* mode = r["mode"] | "mouse";
      if (strcmp(mode, "mouse") == 0) {
        p->rightStick.mode = STICK_MODE_MOUSE;
      } else if (strcmp(mode, "digital_keys") == 0) {
        p->rightStick.mode = STICK_MODE_DIGITAL_KEYS;
      } else {
        p->rightStick.mode = STICK_MODE_NONE;
      }
      p->rightStick.deadzone = r["deadzone"] | 45;
      p->rightStick.mouse.sensitivity = r["sensitivity"] | 1.35f;
      const char* curveStr = r["curve"] | "exponential";
      if (strcmp(curveStr, "linear") == 0) p->rightStick.mouse.curve = CURVE_LINEAR;
      else if (strcmp(curveStr, "aggressive") == 0) p->rightStick.mouse.curve = CURVE_AGGRESSIVE;
      else p->rightStick.mouse.curve = CURVE_EXPONENTIAL;
      p->rightStick.mouse.invertY = r["invert_y"] | false;
    }
  }

  // Buttons
  if (doc["buttons"].is<JsonObjectConst>()) {
    JsonObjectConst btns = doc["buttons"];
    for (int i = 0; i < TOTAL_BUTTONS; i++) {
      const char* bName = BUTTON_NAMES[i];
      if (btns[bName].is<JsonObjectConst>()) {
        JsonObjectConst bObj = btns[bName];
        const char* typeStr = bObj["type"] | "none";
        if (strcmp(typeStr, "key") == 0) {
          p->buttons[i].type = BIND_KEY;
          const char* code = bObj["code"] | "";
          strncpy(p->buttons[i].codeStr, code, sizeof(p->buttons[i].codeStr) - 1);
          p->buttons[i].hidCode = resolveKeycode(code);
        } else if (strcmp(typeStr, "mouse_button") == 0) {
          p->buttons[i].type = BIND_MOUSE_BUTTON;
          const char* code = bObj["code"] | "MOUSE_LEFT";
          strncpy(p->buttons[i].codeStr, code, sizeof(p->buttons[i].codeStr) - 1);
          p->buttons[i].hidCode = resolveMouseButton(code);
          p->buttons[i].threshold = bObj["threshold"] | 40;
        } else if (strcmp(typeStr, "mouse_scroll") == 0) {
          p->buttons[i].type = BIND_MOUSE_SCROLL;
          p->buttons[i].scrollDelta = bObj["delta"] | 1;
          p->buttons[i].repeatMs = bObj["repeat_ms"] | 120;
          snprintf(p->buttons[i].codeStr, sizeof(p->buttons[i].codeStr), "%s", (p->buttons[i].scrollDelta > 0) ? "SCROLL_UP" : "SCROLL_DOWN");
        } else {
          p->buttons[i].type = BIND_NONE;
          p->buttons[i].codeStr[0] = '\0';
          p->buttons[i].hidCode = 0;
        }
      }
    }
  }
}

// ============================================================================
// Serial Command Processing
// ============================================================================
void processSerialLine(const char* line) {
  JsonDocument doc;
  DeserializationError err = deserializeJson(doc, line);
  if (err) {
    Serial.printf("{\"status\":\"error\",\"msg\":\"json_parse_failed: %s\"}\n", err.c_str());
    return;
  }

  const char* cmd = doc["cmd"] | "";

  if (strcasecmp(cmd, "PING") == 0) {
    Serial.printf("{\"status\":\"ok\",\"device\":\"%s\",\"fw\":\"%s\",\"active_profile\":%u}\n",
                  DEVICE_NAME, FIRMWARE_VERSION, activeSlot);
    return;
  }

  if (strcasecmp(cmd, "GET_PROFILE") == 0) {
    uint8_t slot = doc["slot"] | activeSlot;
    if (slot >= MAX_PROFILES) slot = activeSlot;
    Profile tempProf;
    if (!loadProfileFromNVS(slot, &tempProf)) {
      loadDefaultProfile(slot, &tempProf);
    }
    JsonDocument resp;
    resp["status"] = "ok";
    resp["cmd"] = "PROFILE_DATA";
    serializeProfileToJson(tempProf, slot, resp);
    serializeJson(resp, Serial);
    Serial.println();
    return;
  }

  if (strcasecmp(cmd, "SET_SLOT") == 0) {
    uint8_t slot = doc["slot"] | 0;
    if (slot < MAX_PROFILES) {
      switchActiveSlot(slot);
      Serial.printf("{\"status\":\"ok\",\"msg\":\"slot_changed\",\"active_profile\":%u,\"name\":\"%s\"}\n",
                    activeSlot, currentProfile.name);
    } else {
      Serial.printf("{\"status\":\"error\",\"msg\":\"invalid_slot\"}\n");
    }
    return;
  }

  if (strcasecmp(cmd, "WRITE_PROFILE") == 0) {
    uint8_t slot = doc["slot"] | activeSlot;
    if (slot < MAX_PROFILES) {
      Profile newProf;
      loadDefaultProfile(slot, &newProf); // base defaults
      parseProfileFromJson(doc, &newProf);
      saveProfileToNVS(slot, newProf);
      if (slot == activeSlot) {
        currentProfile = newProf;
      }
      Serial.printf("{\"status\":\"ok\",\"msg\":\"profile_saved\",\"slot\":%u,\"name\":\"%s\"}\n",
                    slot, newProf.name);
    } else {
      Serial.printf("{\"status\":\"error\",\"msg\":\"invalid_slot\"}\n");
    }
    return;
  }

  if (strcasecmp(cmd, "STREAM_INPUTS") == 0) {
    telemetryEnabled = doc["enabled"] | false;
    Serial.printf("{\"status\":\"ok\",\"msg\":\"stream_toggled\",\"enabled\":%s}\n",
                  telemetryEnabled ? "true" : "false");
    return;
  }

  Serial.printf("{\"status\":\"error\",\"msg\":\"unknown_cmd\"}\n");
}

void handleSerial() {
  while (Serial.available()) {
    char c = (char)Serial.read();
    if (c == '\r') continue;
    if (c == '\n') {
      serialRxBuffer[serialRxIndex] = '\0';
      if (serialRxIndex > 0) {
        processSerialLine(serialRxBuffer);
      }
      serialRxIndex = 0;
    } else {
      if (serialRxIndex < SERIAL_BUF_SIZE - 1) {
        serialRxBuffer[serialRxIndex++] = c;
      }
    }
  }
}

// ============================================================================
// Bluepad32 Callbacks
// ============================================================================
void onConnectedGamepad(GamepadPtr ctl) {
  if (connectedGamepad == nullptr) {
    connectedGamepad = ctl;
    // Set Nimbus+ Player LED to indicate current active slot
    connectedGamepad->setPlayerLEDs(1 << activeSlot);
    // Optional light rumble feedback on connect
    connectedGamepad->setRumble(0x40, 0x40);
    delay(150);
    connectedGamepad->setRumble(0, 0);
  }
}

void onDisconnectedGamepad(GamepadPtr ctl) {
  if (connectedGamepad == ctl) {
    connectedGamepad = nullptr;
    // Release any currently pressed keys or mouse buttons
    Keyboard.releaseAll();
    Mouse.release(1 | 2 | 4);
    memset(prevButtonState, 0, sizeof(prevButtonState));
    memset(rawButtonState, 0, sizeof(rawButtonState));
  }
}

// ============================================================================
// Controller Processing & Mapping Engine
// ============================================================================
float applyCurve(float normVal, StickCurve curve, float sensitivity) {
  float absVal = fabs(normVal);
  float sign = (normVal >= 0.0f) ? 1.0f : -1.0f;

  if (curve == CURVE_EXPONENTIAL) {
    return sign * powf(absVal, 1.6f) * sensitivity;
  } else if (curve == CURVE_AGGRESSIVE) {
    return sign * powf(absVal, 2.2f) * sensitivity;
  }
  // Linear
  return normVal * sensitivity;
}

void processControllerInputs(GamepadPtr ctl) {
  unsigned long now = millis();

  // Read button bitmask and analog values
  uint32_t buttons = ctl->buttons();
  uint8_t dpad = ctl->dpad();
  uint8_t misc = ctl->miscButtons();
  int32_t throttle = ctl->throttle(); // L2 (0..1023)
  int32_t brake = ctl->brake();       // R2 (0..1023)

  int32_t axisLX = ctl->axisX();
  int32_t axisLY = ctl->axisY();
  int32_t axisRX = ctl->axisRX();
  int32_t axisRY = ctl->axisRY();

  // Raw state evaluation
  rawButtonState[BTN_A] = (buttons & BUTTON_A) != 0;
  rawButtonState[BTN_B] = (buttons & BUTTON_B) != 0;
  rawButtonState[BTN_X] = (buttons & BUTTON_X) != 0;
  rawButtonState[BTN_Y] = (buttons & BUTTON_Y) != 0;
  rawButtonState[BTN_L1] = (buttons & BUTTON_SHOULDER_L) != 0;
  rawButtonState[BTN_R1] = (buttons & BUTTON_SHOULDER_R) != 0;
  rawButtonState[BTN_L3] = (buttons & BUTTON_THUMB_L) != 0;
  rawButtonState[BTN_R3] = (buttons & BUTTON_THUMB_R) != 0;

  // D-Pad bitmask check (supports simultaneous diagonals)
  rawButtonState[BTN_DPAD_UP] = (dpad & DPAD_UP) != 0;
  rawButtonState[BTN_DPAD_DOWN] = (dpad & DPAD_DOWN) != 0;
  rawButtonState[BTN_DPAD_LEFT] = (dpad & DPAD_LEFT) != 0;
  rawButtonState[BTN_DPAD_RIGHT] = (dpad & DPAD_RIGHT) != 0;

  // Triggers with configurable threshold
  rawButtonState[BTN_L2] = (throttle >= currentProfile.buttons[BTN_L2].threshold) || ((buttons & BUTTON_TRIGGER_L) != 0);
  rawButtonState[BTN_R2] = (brake >= currentProfile.buttons[BTN_R2].threshold) || ((buttons & BUTTON_TRIGGER_R) != 0);

  // Misc buttons: Home / Options / Menu
  rawButtonState[BTN_HOME] = (misc & 0x01) != 0;
  rawButtonState[BTN_OPTIONS] = (misc & 0x02) != 0;
  rawButtonState[BTN_MENU] = (misc & 0x04) != 0 || (misc & 0x08) != 0;

  // --------------------------------------------------------------------------
  // Hardware Shortcut: Home + D-Pad Left / Right to cycle slots standalone
  // --------------------------------------------------------------------------
  if (rawButtonState[BTN_HOME]) {
    if (rawButtonState[BTN_DPAD_LEFT] && !shortcutTriggered) {
      uint8_t nextSlot = (activeSlot == 0) ? (MAX_PROFILES - 1) : (activeSlot - 1);
      switchActiveSlot(nextSlot);
      shortcutTriggered = true;
    } else if (rawButtonState[BTN_DPAD_RIGHT] && !shortcutTriggered) {
      uint8_t nextSlot = (activeSlot + 1) % MAX_PROFILES;
      switchActiveSlot(nextSlot);
      shortcutTriggered = true;
    } else if (!rawButtonState[BTN_DPAD_LEFT] && !rawButtonState[BTN_DPAD_RIGHT]) {
      shortcutTriggered = false;
    }
  } else {
    shortcutTriggered = false;
  }

  // --------------------------------------------------------------------------
  // Button State Transitions & Output Handling
  // --------------------------------------------------------------------------
  for (int i = 0; i < TOTAL_BUTTONS; i++) {
    bool isDown = rawButtonState[i];
    bool wasDown = prevButtonState[i];
    const ButtonBinding& b = currentProfile.buttons[i];

    if (b.type == BIND_KEY && b.hidCode != 0) {
      if (isDown && !wasDown) {
        Keyboard.press(b.hidCode);
      } else if (!isDown && wasDown) {
        Keyboard.release(b.hidCode);
      }
    } else if (b.type == BIND_MOUSE_BUTTON && b.hidCode != 0) {
      if (isDown && !wasDown) {
        Mouse.press(b.hidCode);
      } else if (!isDown && wasDown) {
        Mouse.release(b.hidCode);
      }
    } else if (b.type == BIND_MOUSE_SCROLL && b.scrollDelta != 0) {
      if (isDown) {
        uint16_t cooldown = (b.repeatMs > 20) ? b.repeatMs : 120;
        if (!wasDown || (now - lastScrollTime[i] >= cooldown)) {
          // Send wheel scroll (+1: up, -1: down)
          #if defined(CONFIG_TINYUSB_ENABLED) || defined(USE_TINYUSB)
            // TinyUSB scroll delta
            Mouse.move(0, 0, b.scrollDelta);
          #else
            // ESP32 USBHIDMouse scroll
            Mouse.move(0, 0, b.scrollDelta);
          #endif
          lastScrollTime[i] = now;
        }
      }
    }

    prevButtonState[i] = isDown;
  }

  // --------------------------------------------------------------------------
  // Left Stick: Digital WASD or Mouse
  // --------------------------------------------------------------------------
  if (currentProfile.leftStick.mode == STICK_MODE_DIGITAL_KEYS) {
    int16_t dz = currentProfile.leftStick.deadzone;
    bool wDown = (axisLY < -dz);
    bool sDown = (axisLY > dz);
    bool aDown = (axisLX < -dz);
    bool dDown = (axisLX > dz);

    static bool prevW = false, prevS = false, prevA = false, prevD = false;
    uint8_t uKey = currentProfile.leftStick.digital.upCode;
    uint8_t dKey = currentProfile.leftStick.digital.downCode;
    uint8_t lKey = currentProfile.leftStick.digital.leftCode;
    uint8_t rKey = currentProfile.leftStick.digital.rightCode;

    if (uKey) { if (wDown && !prevW) Keyboard.press(uKey); if (!wDown && prevW) Keyboard.release(uKey); }
    if (dKey) { if (sDown && !prevS) Keyboard.press(dKey); if (!sDown && prevS) Keyboard.release(dKey); }
    if (lKey) { if (aDown && !prevA) Keyboard.press(lKey); if (!aDown && prevA) Keyboard.release(lKey); }
    if (rKey) { if (dDown && !prevD) Keyboard.press(rKey); if (!dDown && prevD) Keyboard.release(rKey); }

    prevW = wDown; prevS = sDown; prevA = aDown; prevD = dDown;
  }

  // --------------------------------------------------------------------------
  // Right Stick: 125Hz Throttled Sub-Pixel Mouse Movement
  // --------------------------------------------------------------------------
  if (currentProfile.rightStick.mode == STICK_MODE_MOUSE) {
    if (now - lastMouseUpdate >= MOUSE_POLL_INTERVAL_MS) {
      lastMouseUpdate = now;

      int16_t dz = currentProfile.rightStick.deadzone;
      float mag = sqrtf((float)(axisRX * axisRX + axisRY * axisRY));

      if (mag > dz) {
        // Normalize 0.0 to 1.0 past deadzone
        float normX = (float)axisRX / 512.0f;
        float normY = (float)axisRY / 512.0f;
        if (currentProfile.rightStick.mouse.invertY) normY = -normY;

        float sens = currentProfile.rightStick.mouse.sensitivity * 7.5f;
        float moveX = applyCurve(normX, currentProfile.rightStick.mouse.curve, sens);
        float moveY = applyCurve(normY, currentProfile.rightStick.mouse.curve, sens);

        mouseSubX += moveX;
        mouseSubY += moveY;

        int stepX = (int)mouseSubX;
        int stepY = (int)mouseSubY;

        if (stepX != 0 || stepY != 0) {
          Mouse.move(stepX, stepY);
          mouseSubX -= stepX;
          mouseSubY -= stepY;
        }
      } else {
        mouseSubX = 0.0f;
        mouseSubY = 0.0f;
      }
    }
  }

  // --------------------------------------------------------------------------
  // Live Input Telemetry (Throttled to 30Hz)
  // --------------------------------------------------------------------------
  if (telemetryEnabled && (now - lastTelemetryUpdate >= TELEMETRY_INTERVAL_MS)) {
    lastTelemetryUpdate = now;
    Serial.printf("{\"event\":\"INPUT\",\"buttons\":%u,\"dpad\":%u,\"lx\":%d,\"ly\":%d,\"rx\":%d,\"ry\":%d,\"l2\":%d,\"r2\":%d}\n",
                  buttons, dpad, axisLX, axisLY, axisRX, axisRY, throttle, brake);
  }
}

// ============================================================================
// Arduino Setup & Main Loop
// ============================================================================
void setup() {
  Serial.begin(SERIAL_BAUD);

  // Initialize Native USB HID
  #if defined(CONFIG_TINYUSB_ENABLED) || defined(USE_TINYUSB)
    // TinyUSB initialization if configured
  #else
    USB.begin();
    Keyboard.begin();
    Mouse.begin();
  #endif

  // Initialize NVS storage
  prefs.begin("nimbus_cfg", false);
  activeSlot = prefs.getUChar("active_slot", 0);
  if (activeSlot >= MAX_PROFILES) activeSlot = 0;

  // Load active profile from NVS or set default
  if (!loadProfileFromNVS(activeSlot, &currentProfile)) {
    loadDefaultProfile(activeSlot, &currentProfile);
    saveProfileToNVS(activeSlot, currentProfile);
  }

  // Initialize Bluepad32
  // DO NOT call BP32.forgetBluetoothKeys() so controller auto-reconnects on boot
  BP32.setup(&onConnectedGamepad, &onDisconnectedGamepad);

  // Send ready message
  Serial.printf("{\"status\":\"ok\",\"device\":\"%s\",\"fw\":\"%s\",\"active_profile\":%u}\n",
                DEVICE_NAME, FIRMWARE_VERSION, activeSlot);
}

void loop() {
  // 1. Process incoming USB CDC commands from host app
  handleSerial();

  // 2. Poll Bluetooth stack
  BP32.update();

  // 3. Process controller inputs if connected
  if (connectedGamepad && connectedGamepad->isConnected()) {
    processControllerInputs(connectedGamepad);
  }

  // Brief yield for RTOS task scheduling
  vTaskDelay(1 / portTICK_PERIOD_MS);
}
