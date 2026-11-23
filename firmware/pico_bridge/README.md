# 8BitDo Ultimate 2C & Raspberry Pi Pico 2 W Bridge Firmware

Production-grade firmware stack for the Raspberry Pi Pico 2 W (RP2350) and Pico W (RP2040) bridge board.

## Architecture

- **Bluetooth Stack**: Bluepad32 + BTstack running on CYW43439 radio, supporting both Bluetooth Classic (BR/EDR) and BLE.
- **USB Stack**: TinyUSB Composite Device:
  - **HID Keyboard**: 6-key rollover (6KRO) + modifiers.
  - **HID Mouse**: Analog stick mouse emulation + 5 mouse buttons + scroll wheel.
  - **HID Consumer Control**: macOS & Windows media keys (Volume Up/Down, Mute, Play/Pause, Brightness).
  - **CDC Serial Channel**: Bidirectional NDJSON protocol for configuration, real-time telemetry, and 1-click bootloader jumps.
- **Flash Storage**: Non-volatile storage of up to 4 configuration profiles in the upper flash sector (`PICO_FLASH_SIZE_BYTES - 16 * FLASH_SECTOR_SIZE`), protected with CRC32 verification and `flash_safe_execute()` to prevent bus contention.
- **One-Click UF2 Updates**: CDC command `{"cmd":"BOOTLOADER"}` triggers `reset_usb_boot(0, 0)` in `pico/bootrom.h`, mounting the board directly as a USB drive (`RP2350` or `RPI-RP2`) without holding the physical BOOTSEL button.

---

## Hardware Pinout (Captive USB-C Pigtail)

Solder a 4-conductor USB 2.0 cable directly to the Pico 2 W:

| Wire Color | Signal | Pico 2 W Connection Point |
|------------|--------|----------------------------|
| **Red**    | 5V     | **Pin 40 (VBUS)**          |
| **Black**  | GND    | **TP1** (Underside USB Ground Pad) |
| **White**  | D-     | **TP2** (Underside USB D- Pad) |
| **Green**  | D+     | **TP3** (Underside USB D+ Pad) |

Keep stripped D+/D- leads under 1.5 cm to maintain clean USB signal integrity.

---

## Building the Firmware

### Prerequisites

1. Install CMake (v3.13+) and `arm-none-eabi-gcc`.
2. Clone the official Pico SDK (v2.3.0+):
   ```bash
   git clone https://github.com/raspberrypi/pico-sdk.git
   cd pico-sdk
   git submodule update --init
   export PICO_SDK_PATH=/path/to/pico-sdk
   ```

### Compile for Pico 2 W (RP2350 Flagship Target)

```bash
mkdir build
cd build
cmake -DPICO_BOARD=pico2_w ..
cmake --build .
```

This generates `pico_8bitdo_bridge.uf2`.

### Compile for Pico W (RP2040 Target)

```bash
mkdir build_picow
cd build_picow
cmake -DPICO_BOARD=pico_w ..
cmake --build .
```

---

## Flashing the Firmware

1. **First-time flash**: Hold the white **BOOTSEL** button on the Pico board while plugging it in. It mounts as a USB drive (`RP2350` or `RPI-RP2`). Drag and drop `pico_8bitdo_bridge.uf2`.
2. **Subsequent updates**: In the desktop app, click **Update Firmware** or send `{"cmd":"BOOTLOADER"}` over USB CDC. The board reboots directly into the bootloader drive without physical button access.
