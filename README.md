# Nimbus+ Cosmic Bridge 🌌🎮

An open-source, driverless hardware-and-software controller bridge for **macOS** (with complete cross-platform support for Windows development):
- **Hardware Bridge (`firmware/`):** An ESP32-S3 dongle running Bluepad32 + TinyUSB Composite HID & CDC Serial. Wirelessly pairs with a **SteelSeries Nimbus+** controller over Bluetooth and presents itself to macOS as a native USB keyboard and mouse—bypassing DriverKit entitlements and background daemon hurdles.
- **Desktop Configurator (`app/`):** A sleek Tauri v2 + Rust + Vue 3 application crafted with a deep-space **Galaxy Glassmorphic + Liquid Metaball** aesthetic (cyan, cobalt, indigo, violet, and obsidian glass). Configures custom bindings and persists profiles to the ESP32-S3's Non-Volatile Storage (NVS) over USB CDC serial.
- **CI/CD (`.github/workflows/`):** Automated GitHub Actions pipeline generating universal macOS `.dmg` bundles (Apple Silicon & Intel) and verifying Windows builds.

---

## 🏛️ System Architecture

```text
┌─────────────────────────┐          Bluetooth
│  SteelSeries Nimbus+    │ ───────────────────────────────► ┌─────────────────────────┐
│  (MFi Wireless Gamepad) │                                  │  ESP32-S3 USB Dongle    │
└─────────────────────────┘                                  │  - Bluepad32 Host       │
                                                             │  - TinyUSB Composite    │
┌─────────────────────────┐   USB CDC Serial (115200 baud)   │    Keyboard + Mouse     │
│  Tauri v2 + Vue 3 App   │ ◄──────────────────────────────► │  - ArduinoJson + NVS    │
│  (Galaxy Configurator)  │    Profiles / Telemetry / Slots  └───────────┬─────────────┘
└─────────────────────────┘                                              │ Native USB HID
                                                                         ▼
                                                             ┌─────────────────────────┐
                                                             │  macOS / Windows Host   │
                                                             │  (Native HID Inputs)    │
                                                             └─────────────────────────┘
```

---

## 🚀 Features

- **Driverless macOS Operation:** Acts as a standard USB Keyboard and Optical Mouse. No accessibility daemon prompts, kexts, or macOS DriverKit entitlement headaches.
- **4 Onboard Profile Slots:** Persisted directly to ESP32 Flash memory via NVS (`Preferences`).
- **Hardware Profile Switcher:** Hold **Home** and tap **D-Pad Left / Right** on the Nimbus+ to switch slots standalone without opening the Mac app. Controller player LEDs update in real time.
- **125Hz Throttled Mouse Engine:** Right stick analog motion is throttled to 8ms intervals with sub-pixel remainder accumulation and selectable acceleration curves (*Linear*, *Exponential*, *Aggressive*).
- **Edge-Triggered Keyboard Transitions:** Clean keydown and keyup events with zero repeating packet spam.
- **3-Layer Interactive Controller UI:**
  1. *Liquid Plasma Goo Layer:* Organic metaball SVG filter (`#nebula-goo`) that merges adjacent button hover glows.
  2. *Obsidian Glass Shell:* Chamfered contours, textured palm grips, and live 4-LED slot indicator.
  3. *High-Precision Hit-Zones:* 19 clickable controls with live keycap callout badges and real-time 30Hz input telemetry indicators.
- **Interactive Live Input Recorder:** Press any physical keyboard key or mouse button in the app to bind it immediately.

---

## 🔌 Shared JSON Serial Protocol (115200 Baud)

All serial communication occurs over the ESP32-S3's native USB CDC interface (`/dev/cu.usbmodem*` on macOS, `COM*` on Windows) formatted as newline-delimited JSON (`\n`).

### 1. Handshake / Ping
```json
// Host -> ESP32
{ "cmd": "PING" }

// ESP32 -> Host
{ "status": "ok", "device": "nimbus-s3-bridge", "fw": "2.0.0", "active_profile": 0 }
```

### 2. Write & Save Profile (`WRITE_PROFILE`)
```json
// Host -> ESP32
{
  "cmd": "WRITE_PROFILE",
  "slot": 0,
  "name": "Minecraft",
  "sticks": {
    "left": {
      "mode": "digital_keys",
      "deadzone": 180,
      "up": "w", "down": "s", "left": "a", "right": "d"
    },
    "right": {
      "mode": "mouse",
      "deadzone": 45,
      "sensitivity": 1.35,
      "curve": "exponential",
      "invert_y": false
    }
  },
  "buttons": {
    "a": { "type": "key", "code": "KEY_SPACE" },
    "b": { "type": "key", "code": "KEY_LEFT_SHIFT" },
    "x": { "type": "key", "code": "q" },
    "y": { "type": "key", "code": "e" },
    "l1": { "type": "mouse_scroll", "delta": 1, "repeat_ms": 120 },
    "r1": { "type": "mouse_scroll", "delta": -1, "repeat_ms": 120 },
    "l2": { "type": "mouse_button", "code": "MOUSE_RIGHT", "threshold": 40 },
    "r2": { "type": "mouse_button", "code": "MOUSE_LEFT", "threshold": 40 },
    "l3": { "type": "key", "code": "KEY_LEFT_CTRL" },
    "r3": { "type": "key", "code": "f" },
    "dpad_up": { "type": "key", "code": "KEY_F5" },
    "dpad_down": { "type": "key", "code": "KEY_F3" },
    "dpad_left": { "type": "key", "code": "1" },
    "dpad_right": { "type": "key", "code": "t" },
    "menu": { "type": "key", "code": "KEY_ESC" },
    "options": { "type": "key", "code": "KEY_RETURN" },
    "home": { "type": "key", "code": "KEY_TAB" }
  }
}

// ESP32 -> Host
{ "status": "ok", "msg": "profile_saved", "slot": 0, "name": "Minecraft" }
```

### 3. Switch Profile Slot (`SET_SLOT`)
```json
// Host -> ESP32
{ "cmd": "SET_SLOT", "slot": 1 }

// ESP32 -> Host
{ "status": "ok", "msg": "slot_changed", "active_profile": 1, "name": "2D Platformer" }
```

### 4. Read Stored Profile (`GET_PROFILE`)
```json
// Host -> ESP32
{ "cmd": "GET_PROFILE", "slot": 0 }

// ESP32 -> Host
{ "status": "ok", "cmd": "PROFILE_DATA", "slot": 0, "name": "Minecraft", ... }
```

### 5. Live Telemetry Stream (`STREAM_INPUTS`)
```json
// Host -> ESP32
{ "cmd": "STREAM_INPUTS", "enabled": true }

// ESP32 -> Host (Streamed at 30Hz)
{ "event": "INPUT", "buttons": 1, "dpad": 0, "lx": 0, "ly": -412, "rx": 120, "ry": -30, "l2": 0, "r2": 1023 }
```

---

## 🛠️ Flashing the ESP32-S3 Firmware

1. Install [Arduino IDE 2.x](https://www.arduino.cc/en/software).
2. Add ESP32 board support via Boards Manager: `esp32 by Espressif Systems` (v2.0.14+ or v3.0+).
3. Install required libraries from Library Manager:
   - `Bluepad32` (by Ricardo Quesada)
   - `ArduinoJson` (v7.x by Benoît Blanchon)
4. Open `firmware/nimbus_bridge/nimbus_bridge.ino`.
5. Under **Tools**, configure:
   - **Board:** `ESP32S3 Dev Module`
   - **USB CDC On Boot:** `Enabled`
   - **USB Mode:** `Hardware CDC and JTAG` (or `USB-OTG (TinyUSB)`)
   - **Flash Size:** `4MB` or `8MB`
   - **Upload Mode:** `UART0 / Hardware CDC`
6. Connect the ESP32-S3 via the native USB port and click **Upload**.
7. Put the SteelSeries Nimbus+ into Bluetooth pairing mode (hold the pairing button on top until the 4 LEDs flash rapidly). The ESP32 will pair automatically.

---

## 💻 Running the Desktop Configurator

### Prerequisites
- Node.js 20+ & npm
- Rust 1.75+ (`rustup default stable`)
- On macOS: Xcode Command Line Tools (`xcode-select --install`)
- On Windows: Visual Studio C++ Build Tools

### Development
```bash
# Navigate to the app directory
cd app

# Install dependencies
npm install

# Run frontend only in browser (includes built-in simulation mode)
npm run dev

# Run desktop application with Tauri
npm run tauri dev
```

### Building for Release
```bash
cd app
npm run tauri build
```

---

## 📄 License
MIT License. Free and open source for all makers, gamers, and developers.
