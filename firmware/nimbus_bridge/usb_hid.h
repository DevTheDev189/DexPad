#pragma once
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

void initUSBHID();
void usbKeyboardPress(uint8_t key);
void usbKeyboardRelease(uint8_t key);
void usbKeyboardReleaseAll();
void usbMousePress(uint8_t buttons);
void usbMouseRelease(uint8_t buttons);
void usbMouseMove(int8_t x, int8_t y, int8_t wheel);

#ifdef __cplusplus
}
#endif
