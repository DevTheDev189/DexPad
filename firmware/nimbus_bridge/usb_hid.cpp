#include "usb_hid.h"
#include <Arduino.h>
#include "USB.h"
#include "USBHIDKeyboard.h"
#include "USBHIDMouse.h"

static USBHIDKeyboard sKeyboard;
static USBHIDMouse sMouse;

extern "C" {

void initUSBHID() {
  USB.begin();
  sKeyboard.begin();
  sMouse.begin();
}

void usbKeyboardPress(uint8_t key) {
  sKeyboard.press(key);
}

void usbKeyboardRelease(uint8_t key) {
  sKeyboard.release(key);
}

void usbKeyboardReleaseAll() {
  sKeyboard.releaseAll();
}

void usbMousePress(uint8_t buttons) {
  sMouse.press(buttons);
}

void usbMouseRelease(uint8_t buttons) {
  sMouse.release(buttons);
}

void usbMouseMove(int8_t x, int8_t y, int8_t wheel) {
  sMouse.move(x, y, wheel);
}

}
