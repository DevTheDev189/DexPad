# IMPLEMENTATION_PLAN.md — 8BitDo Ultimate 2C + Pico 2 W Sky Glass Ecosystem

## 1. Executive Summary & Hardware Vision
A next-generation, high-performance controller remapping and hardware bridge ecosystem designed for macOS and Windows. 
This build replaces the legacy prototype with a production-grade industrial design and modern software architecture:

- **Target Controller:** **8BitDo Ultimate 2C Bluetooth (Blue)**
  - Precision Hall Effect magnetic analog sticks (zero stick drift forever).
  - Tactile microswitch bumpers and digital quick-throw triggers.
  - Dedicated **L4 and R4** extra top shoulder bumpers.
  - 6-Axis motion gyroscope (Switch Pro controller protocol).
  - Dual linear rumble vibration motors.
  - Authentic pastel Sky Blue & Cloud White two-tone colorway with soft Periwinkle accents.
- **Hardware Bridge:** **Raspberry Pi Pico 2 W (RP2350)** / **Pico W (RP2040)**
  - Infineon CYW43439 dual-band wireless chip supporting **both Bluetooth Classic (BR/EDR) and BLE**.
  - High-performance dual-core processor with ample SRAM and XIP flash headroom.
  - Native USB 1.1/2.0 OTG peripheral.
  - Drag-and-drop `.uf2` firmware flashing via mass-storage bootloader (`reset_usb_boot`), eliminating COM port locking and physical button dependence.
- **Enclosure & Interconnect:**
  - JLC3DP SLA resin enclosure (LEDO 6060 / 9600 resin) with factory **Matte Sky Blue** spray-paint finish.
  - Captive flexible 4-wire USB-C male pigtail soldered directly to underside test pads:
    - `VBUS` (Pin 40) -> 5V (Red)
    - `TP1` (Underside GND pad) -> GND (Black)
    - `TP2` (Underside D- pad) -> D- (White)
    - `TP3` (Underside D+ pad) -> D+ (Green)
  - Mechanical Strain Relief: Internal 2mm nylon zip-tie collar pocket anchor + compression clamp rib protecting all solder joints from tension and bending.
  - Snap-fit / M2 screw assembly with discrete 2mm BOOTSEL pinhole and light-pipe window for the onboard LED.
- **Desktop Companion App:**
  - Tauri v2 + Rust + Vue 3 + Three.js.
  - **"Cerulean Sky Glass / Horizon Aero"** daylight aesthetic inspired by modern 2026 design systems (Apple visionOS, Linear, and Adobe Creative Cloud).
  - Interactive Three.js PBR render of the 8BitDo Ultimate 2C with Front and Top camera views.
  - Dynamic electric cyan glowing tracer ribbon connecting the active 3D controller button to its row in the mapping table.
  - Floating pill-capsule mapping rows with keyboard, mouse, gyro aim, and **Consumer Control (media & brightness)** key bindings.
  - App-aware auto-switching watching foreground windows to activate game-specific profiles automatically.
  - One-click in-app `.uf2` firmware flasher.

---

## 2. System Architecture & Repository Layout

```text
Dexter_Controller_Project/
├── IMPLEMENTATION_PLAN.md                  # This file
├── OLD_IMPLEMENTATION_PLAN.md              # Archived prototype plan
├── controller_cc_credits.txt               # 3D Model attribution (CC-BY 4.0 Sketchfab)
├── firmware/
│   ├── pico_bridge/                        # Modern Pico SDK CMake Project
│   │   ├── CMakeLists.txt                  # Dual-target build: pico2_w and pico_w
│   │   ├── pico_sdk_import.cmake           # Official Pico SDK v2.3+ hook
│   │   ├── include/
│   │   │   ├── tusb_config.h               # TinyUSB Composite HID + CDC descriptors
│   │   │   ├── bridge_types.h              # Profile, binding, and stick configurations
│   │   │   ├── protocol.h                  # NDJSON serial command definitions
│   │   │   ├── storage.h                   # Flash sector NVS persistence API
│   │   │   └── gyro.h                      # 6-Axis motion processing & mouse aim
│   │   └── src/
│   │       ├── main.c                      # Core 0 event loop (TinyUSB + CDC commands)
│   │       ├── controller.c                # Core 1 Bluepad32 Bluetooth host & mappings
│   │       ├── storage.c                   # Safe flash execution (flash_safe_execute)
│   │       ├── protocol.c                  # Fast streaming JSON parser/serializer
│   │       └── gyro.c                      # Pitch/yaw sensor fusion & aim accumulation
│   └── nimbus_bridge/                      # Archived ESP32-S3 Arduino sketch
└── app/
    ├── public/
    │   └── models/
    │       └── 8bitdo_ultimate_2c.glb      # Optimized ~6.1k triangle 8BitDo 2C 3D model
    ├── src/
    │   ├── assets/
    │   │   └── theme.css                   # Cerulean Sky Glass design tokens & aero blur
    │   ├── types/
    │   │   ├── keymap.ts                   # Extended: L4, R4, Gyro, Media/Brightness keys
    │   │   └── controllers.ts              # 8BitDo 2C node mappings & button coordinates
    │   ├── composables/
    │   │   ├── useSerial.ts                # Auto-connect daemon, NDJSON RPC, .uf2 trigger
    │   │   ├── useProfiles.ts              # Profile manager & hardware flash sync
    │   │   └── useAppWatcher.ts            # Frontend reactive hook for active app profile
    │   └── components/
    │       ├── AmbientBackground.vue       # Abstract procedural volumetric sky & sunbeams
    │       ├── HeaderBar.vue               # Profile pills, Nintendo/Xbox toggle, status dot
    │       ├── Controller3DCanvas.vue      # Three.js 8BitDo 2C PBR viewer + tracer ribbon
    │       ├── MappingTable.vue            # Floating pill-capsule mapping rows
    │       ├── DpadConfigModal.vue         # 8-Way D-pad configuration dialog
    │       ├── StickConfigModal.vue        # Deadzone, sensitivity, and curve visualizer
    │       ├── FirmwareModal.vue           # 1-Click .uf2 firmware updater dialog
    │       └── KeyCaptureModal.vue         # Keystroke, mouse, and media key recorder
    └── src-tauri/
        └── src/
            ├── lib.rs                      # Tauri command registration & window vibrancy
            ├── models.rs                   # Serde data contracts for NDJSON messages
            ├── serial.rs                   # Port enumeration, CDC auto-discovery, hotplug
            ├── app_watcher.rs              # macOS NSWorkspace / Windows active app watcher
            └── updater.rs                  # Mass-storage drive detector & .uf2 writer
```

---

## 3. Design System: "Cerulean Sky Glass"

### Color Tokens
- **Atmospheric Gradient:** Deep oceanic twilight to bright cerulean (`#0a1526` -> `#0284c7` -> `#38bdf8` -> `#f0f9ff`)
- **Sunbeam Glow:** Warm solar brilliance (`rgba(254, 240, 138, 0.25)`)
- **Glass Panel Surface:** Translucent cloud aerogel (`rgba(255, 255, 255, 0.45)` with `backdrop-filter: blur(32px) saturate(180%)`)
- **Specular Border Rim:** 1px top directional light (`rgba(255, 255, 255, 0.85)` top edge fading to `rgba(56, 189, 248, 0.20)`)
- **Primary Ink:** High-contrast deep slate (`#0f172a` on light cards, `#f8fafc` on dark accents)
- **Secondary Ink:** Muted slate blue (`#334155` / `#64748b`)
- **Interactive Halo:** Neon electric cyan (`#22d3ee` / `#38bdf8`) with box-shadow glow
- **Tracer Ribbon:** Luminous curved cyan bezier curve (`#38bdf8` to `#22d3ee`) with soft blur aura

### Typography Hierarchy (Geist Sans + Geist Mono)
- **Interface Base:** `Geist Sans`, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif
- **Data & Telemetry:** `Geist Mono`, "JetBrains Mono", monospace with tabular figures (`font-feature-settings: "tnum" 1`)
- **Section Eyebrows:** 11px, font-weight 600, letter-spacing 0.08em, uppercase
- **Button Titles:** 13.5px, font-weight 500, letter-spacing -0.01em
- **Key Binding Chips:** 11.5px, font-weight 600, monospace, padding 4px 10px, rounded-md

---

## 4. Hardware & Firmware Specifications

### USB Composite Descriptors (TinyUSB)
1. **HID Keyboard:** Standard 6-key rollover + modifier keys (Ctrl, Shift, Alt, Cmd/Win).
2. **HID Mouse:** 125 Hz throttled sub-pixel mouse movement, 5 buttons, and vertical/horizontal scroll wheel.
3. **HID Consumer Control:** macOS and Windows media controls:
   - Volume Up (`0x00E9`), Volume Down (`0x00EA`), Mute (`0x00E2`)
   - Play / Pause (`0x00CD`), Next Track (`0x00B5`), Previous Track (`0x00B6`)
   - Brightness Increment (`0x006F`), Brightness Decrement (`0x0070`)
4. **USB CDC Serial:** 115,200 baud NDJSON communication channel for configuration, telemetry streaming, and bootloader triggers.

### Flash Memory Layout
- The top 64KB sector of Pico flash (`0x101F0000` on 2MB flash, or top sector on 4MB Pico 2 W) stores up to 8 JSON profile slots.
- Writes are guarded by `flash_safe_execute()` to safely pause Core 1 and interrupts during the 20ms write cycle, preventing BTstack wireless crashes.

### Hardware Gestures & Feedback
- **Profile Switch Rumble:**
  - Slot 0: 1 short pulse (100ms)
  - Slot 1: 2 short pulses
  - Slot 2: 3 short pulses
  - Slot 3: 4 short pulses
- **Hardware Shortcut:** `Home + D-Pad Left/Right` cycles profiles standalone without the desktop app open.
- **Hold-to-Gyro Aim:** Binding any trigger or button (e.g. `L2`) to `GYRO_AIM` enables continuous 6-axis IMU mouse input while held.

---

## 5. Phased Implementation Roadmap

### Phase 1: Sky Glass Design System Overhaul (Desktop App)
- [ ] Refactor `app/src/assets/theme.css` to the daylight Cerulean Sky Glass token palette.
- [ ] Redesign `app/src/components/AmbientBackground.vue` into an abstract volumetric sky with procedural drifting cloud orbs and sunlight caustics.
- [ ] Update `app/src/components/HeaderBar.vue` with centered profile pills, Sky Blue glowing active indicator, and Nintendo ↔ Xbox layout switcher.
- [ ] Transform `app/src/components/MappingTable.vue` into floating pill capsules matching the reference mockup.

### Phase 2: 8BitDo Ultimate 2C 3D Model Integration
- [ ] Load `app/public/models/8bitdo_ultimate_2c.glb` into `app/src/components/Controller3DCanvas.vue`.
- [ ] Apply custom PBR materials:
  - Pastel Sky Blue body shell (`#c5dcf7`).
  - Cloud White underside (`#f8fafc`).
  - Soft Periwinkle thumbsticks, D-pad, and face buttons (`#9cb8ed`).
- [ ] Map all individual mesh nodes: `Main_LP`, `X,_Y_A_B_buttons`, `LP_Arrow`, `JoySticks_LP`, `LP_Button_R4.001`, `LP_Button_RT`, `LP_Button_RB`, `TopMiddleButton_LP`.
- [ ] Implement raycast hover, click selection, and luminous cyan glowing outlines.
- [ ] Implement dynamic camera transitions: **Front View** (ABXY, sticks, D-pad) and **Top View** (L1, R1, L2, R2, L4, R4).
- [ ] Build the interactive electric cyan glowing bezier tracer ribbon connecting the clicked 3D button directly to the mapping table row.

### Phase 3: Data Models, Keymap Types & Remapping Engine
- [ ] Extend `app/src/types/keymap.ts` and `controllers.ts`:
  - Add `BTN_L4` and `BTN_R4`.
  - Add `BIND_CONSUMER_CONTROL` (Volume, Mute, Play/Pause, Brightness).
  - Add `BIND_GYRO_AIM`.
  - Add `layout_mode: 'nintendo' | 'xbox'`.
- [ ] Update default presets:
  - **Minecraft:** Left stick WASD, Right stick Mouse, L4 Sprint, R4 Jump/Interact.
  - **2D Platformer:** D-pad movement, B Jump, Y Attack, L4 Dash, R4 Focus.
  - **Desktop Mouse:** Right stick mouse, L2 Right Click, R2 Left Click, L1/R1 Scroll, L4 Volume Down, R4 Volume Up.
- [ ] Update modal editors (`KeyCaptureModal.vue`, `DpadConfigModal.vue`, `StickConfigModal.vue`) to the Sky Glass aesthetic.

### Phase 4: Pico SDK Firmware Architecture (`firmware/pico_bridge`)
- [ ] Set up CMakeLists.txt for Raspberry Pi Pico 2 W (`pico2_w` / RP2350) and Pico W (`pico_w` / RP2040).
- [ ] Configure `tusb_config.h` with Composite Keyboard + Mouse + Consumer Control + CDC Serial descriptors.
- [ ] Implement Bluepad32 Bluetooth host driver for 8BitDo Ultimate 2C (reading sticks, triggers, L4/R4, gyro, and rumble feedback).
- [ ] Implement safe flash storage persistence using `flash_safe_execute()`.
- [ ] Implement NDJSON serial command parser for profile updates, telemetry streaming, and `reset_usb_boot(0, 0)` bootloader trigger.

### Phase 5: Tauri Desktop Native Capabilities
- [ ] Implement macOS `NSWorkspace` / Windows foreground app watcher in Rust to auto-switch profile on active window focus change.
- [ ] Implement 1-click `.uf2` flashing: detect mounted `RPI-RP2` / `RP2350` USB storage volume and copy binary directly.
- [ ] Wire up live stick/trigger telemetry to animate the 3D model with subtle physical tilt and lighting reactions.

---

## 6. Verification & Delivery Criteria
1. **Visual Fidelity:** Desktop app matches the light, airy Cerulean Sky Glass mockup with floating pills, translucent blur, and high text contrast.
2. **Interactive 3D Controller:** 8BitDo Ultimate 2C renders at 120 FPS, responds to clicks on all buttons (including L4 and R4), switches Front/Top views, and draws the glowing tracer ribbon to the active table row.
3. **Typography & Polish:** Crisp Geist-style typography with tabular numerical metrics and strictly zero emojis.
4. **Pico Firmware:** Clean CMake build producing `.uf2` binaries for both Pico 2 W and Pico W.
5. **Zero Friction Flashing:** Firmware updates trigger via in-app button, booting the Pico directly into mass storage mode without touching physical pins or buttons.
