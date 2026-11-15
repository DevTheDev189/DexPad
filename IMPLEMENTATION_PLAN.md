# IMPLEMENTATION_PLAN.md — Nimbus+ Cosmic Bridge

## 1. Project Overview
An open-source, cross-platform hardware-and-software controller remapping ecosystem for macOS (with full local development support on Windows):
- **Hardware Bridge (`firmware/`):** An ESP32-S3 dongle running Bluepad32 + TinyUSB Composite HID & CDC Serial. Connects wirelessly to a SteelSeries Nimbus+ controller via Bluetooth and presents itself to macOS as a native USB keyboard and mouse—eliminating macOS DriverKit entitlements and background accessibility daemons.
- **Desktop Configurator (`app/`):** A sleek Tauri v2 + Rust + Vue 3 application styled with a deep-space **Galaxy Glassmorphic + Liquid Metaball** aesthetic (light blue, cobalt, indigo, violet, and obsidian black). Sends profile configurations as newline-delimited JSON over USB CDC serial to the ESP32-S3, which persists them to Non-Volatile Storage (NVS).
- **CI/CD (`.github/workflows/`):** Automated GitHub Actions workflow compiling universal macOS `.dmg` releases on `macos-latest` runners (and verifying Windows builds on `windows-latest`).

---

## 2. Repository Structure
```text
nimbus-cosmic-bridge/
├── IMPLEMENTATION_PLAN.md
├── README.md
├── .github/
│   └── workflows/
│       └── build-release.yml       # macOS Universal .dmg + Windows build checks
├── firmware/
│   └── nimbus_bridge/
│       └── nimbus_bridge.ino       # Refactored Bluepad32 + TinyUSB + ArduinoJson + Preferences (NVS)
└── app/
    ├── package.json
    ├── vite.config.ts
    ├── tsconfig.json
    ├── index.html
    ├── src/
    │   ├── main.ts
    │   ├── App.vue
    │   ├── assets/
    │   │   └── theme.css           # Galaxy palette tokens, starfield keyframes, glass utilities
    │   ├── types/
    │   │   └── keymap.ts           # TypeScript interfaces matching Rust & ESP32 JSON schema
    │   ├── composables/
    │   │   ├── useSerial.ts        # Tauri IPC wrappers for port discovery, connect, send/receive JSON
    │   │   └── useProfiles.ts      # Local & device profile state management + default presets
    │   └── components/
    │       ├── CosmicBackground.vue      # Parallax CSS starfield + reactive cursor/selection nebula orb
    │       ├── MetaballDefs.vue          # Shared SVG <filter id="nebula-goo"> (feGaussianBlur + feColorMatrix)
    │       ├── NimbusControllerSvg.vue   # 3-layer interactive SteelSeries Nimbus+ SVG (plasma + shell + controls)
    │       ├── BindingInspector.vue      # Glassmorphic panel to bind keys, mouse clicks, scroll, or stick curves
    │       ├── KeyCaptureModal.vue       # "Press any key or mouse button" listener overlay
    │       └── ProfilePillBar.vue        # Liquid metaball tab switcher for saved profiles
    └── src-tauri/
        ├── Cargo.toml
        ├── tauri.conf.json
        └── src/
            ├── main.rs
            ├── lib.rs              # Window vibrancy setup (NSVisualEffectView on macOS, Mica/Acrylic on Win)
            ├── serial.rs           # USB CDC port enumeration, background reader thread, JSON framing
            └── models.rs           # Serde structs mirroring the ESP32 JSON profile schema
```

---

## 3. Shared JSON Over USB CDC Protocol
Communication uses **115200 baud** newline-delimited JSON (`\n` terminated) over the ESP32-S3's native USB CDC port (`/dev/cu.usbmodem*` on macOS, `COM*` on Windows). Debug `dumpGamepad()` serial spam is completely removed so the serial channel remains clean for structured commands.

### 3.1 Host $\rightarrow$ ESP32-S3 Commands
1. **Ping / Handshake:**
   ```json
   { "cmd": "PING" }
   ```
   *Response:* `{"status":"ok","device":"nimbus-s3-bridge","fw":"2.0.0","active_profile":0}`

2. **Apply & Save Profile (`WRITE_PROFILE`):**
   ```json
   {
     "cmd": "WRITE_PROFILE",
     "slot": 0,
     "name": "Minecraft",
     "sticks": {
       "left": {
         "mode": "digital_keys",
         "deadzone": 180,
         "up": "w",
         "down": "s",
         "left": "a",
         "right": "d"
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
   ```

3. **Switch Active Slot (`SET_SLOT`):**
   ```json
   { "cmd": "SET_SLOT", "slot": 1 }
   ```

4. **Read Stored Profile (`GET_PROFILE`):**
   ```json
   { "cmd": "GET_PROFILE", "slot": 0 }
   ```

5. **Live Input Telemetry Toggle (`STREAM_INPUTS`):**
   ```json
   { "cmd": "STREAM_INPUTS", "enabled": true }
   ```
   *Streamed Frame (throttled to 30Hz when enabled):*
   ```json
   { "event": "INPUT", "buttons": 1, "dpad": 0, "lx": 0, "ly": -412, "rx": 120, "ry": -30, "l2": 0, "r2": 1023 }
   ```

---

## 4. Visual & UI Architecture (Galaxy + Metaball Glassmorphism)

### 4.1 Color System (`app/src/assets/theme.css`)
- `--bg-void: #05060d` (Deep space background)
- `--bg-nebula-1: #0f172a` (Midnight blue)
- `--bg-nebula-2: #1e1035` (Deep cosmic purple)
- `--glass-surface: rgba(15, 20, 42, 0.48)`
- `--glass-border: rgba(147, 197, 253, 0.18)`
- `--accent-cyan: #38bdf8` (Light blue glow)
- `--accent-cobalt: #3b82f6` (Electric blue)
- `--accent-indigo: #6366f1` (Indigo core)
- `--accent-violet: #8b5cf6` (Violet plasma)
- `--accent-magenta: #c084fc` (Nebula highlight)

### 4.2 Cosmic & Metaball Effects
1. **Starfield + Dynamic Nebula Spotlight (`CosmicBackground.vue`):**
   - Two CSS radial-gradient / box-shadow star layers animating slowly with `transform: translate3d(...)` on GPU compositing layers.
   - A large blurred nebula orb (`width: 480px; height: 480px; filter: blur(95px)`) positioned behind the controller SVG. Hovering or selecting any control on the SVG smoothly interpolates the orb's `(x, y)` coordinates and radial gradient colors (`cyan` $\rightarrow$ `indigo` $\rightarrow$ `violet`) directly behind that button.
2. **SVG Liquid Metaball Layer (`MetaballDefs.vue` + `NimbusControllerSvg.vue`):**
   - Define an SVG filter `<filter id="nebula-goo">` using `<feGaussianBlur in="SourceGraphic" stdDeviation="10" result="blur" />` followed by `<feColorMatrix in="blur" mode="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 22 -9" result="goo" />`.
   - Render glowing plasma circles for adjacent buttons (e.g., `A/B/X/Y` and `D-Pad`) inside a `<g filter="url(#nebula-goo)">` layer *beneath* the frosted glass controller shell so hover glows merge organically like liquid plasma while keeping button icons and keycap labels razor-sharp above.
3. **Native Window Translucency (`window-vibrancy`):**
   - On macOS: apply `NSVisualEffectMaterial::HudWindow` (or `UnderWindowBackground`) with `TitleBarStyle::Overlay` so traffic lights float cleanly over the starfield.
   - On Windows (local dev): apply `apply_mica` / `apply_acrylic` fallback so glassmorphic panels look cohesive during Windows testing.

---

## 5. Step-by-Step Build Phases

### Phase 1: Scaffold Tauri v2 + Rust + Vue App (Windows Local Dev Ready)
1. Initialize the Tauri v2 + Vue 3 + TypeScript project inside `app/`.
2. Add Rust dependencies in `app/src-tauri/Cargo.toml`:
   - `tauri = { version = "2", features = ["macos-private-api"] }`
   - `serialport = "4"`
   - `serde = { version = "1", features = ["derive"] }`
   - `serde_json = "1"`
   - `window-vibrancy = "0.5"`
3. Configure `tauri.conf.json` with transparent window support (`"transparent": true`, `"titleBarStyle": "Overlay"` on macOS, minimum dimensions `1120x740`).
4. Verify `npm run tauri dev` compiles and launches cleanly on Windows.

### Phase 2: Build the Galaxy + Metaball Controller UI
1. Create `theme.css` and `CosmicBackground.vue` with deep blue/indigo/violet/black gradients, twinkling CSS stars, and reactive hover glow tracking.
2. Build `NimbusControllerSvg.vue` using the circular button geometry from `ControllerButtons.svg` as a starting template, expanding into a complete, sleek SteelSeries Nimbus+ vector layout with 19 clickable hit-zones (`A`, `B`, `X`, `Y`, `L1`, `R1`, `L2`, `R2`, `L3`, `R3`, `DPAD_UP/DOWN/LEFT/RIGHT`, `Menu`, `Options`, `Home`, `Left Stick`, `Right Stick`) and live keycap badges.
3. Implement `ProfilePillBar.vue` with a sliding liquid metaball active indicator and preset starter templates (*Minecraft*, *Hollow Knight / 2D Platformer*, *Desktop Mouse Mode*).
4. Build `BindingInspector.vue` and `KeyCaptureModal.vue` so clicking any control on the SVG lets the user either press a physical keyboard/mouse input to bind it or pick from a structured macOS keycode dropdown (including `Command`, `Option`, `Control`, `Shift`, `Space`, `F1–F12`, mouse clicks, scroll wheel, and stick curve/deadzone sliders).

### Phase 3: Rust USB CDC Serial Backend (`serial.rs`)
1. Implement `list_serial_ports()` filtering for ESP32-S3 USB CDC devices (VID `0x303A` / `usbmodem` / `COM` ports) while still allowing manual port selection.
2. Spawn a dedicated background thread using `serialport::open` at `115200` baud with a `BufReader` reading newline-delimited JSON responses (`ACK`, `PROFILE_DATA`, and `INPUT` telemetry events) and emitting them to Vue via `app_handle.emit(...)`.
3. Expose `#[tauri::command]` handlers: `get_ports`, `connect_port`, `disconnect_port`, `send_profile`, `switch_slot`, `request_profile`, and `set_input_stream`.

### Phase 4: Refactor ESP32-S3 Firmware (`firmware/nimbus_bridge/nimbus_bridge.ino`)
1. **Fix Legacy Bugs from Prototype:**
   - Remove stray diff markers (`-`) and fix pointer syntax (`const char*`, `const uint8_t*`).
   - Fix single-quoted hex bug (`ctl->miscButtons() == '0x02'`) $\rightarrow$ bitwise mask (`ctl->miscButtons() & 0x02`).
   - Fix D-Pad equality check (`dpad == DPAD_UP`) $\rightarrow$ bitwise mask (`dpad & DPAD_UP`) so diagonal presses work.
   - Remove `BP32.forgetBluetoothKeys()` from `setup()` so the Nimbus+ auto-reconnects immediately on boot.
   - Throttle right-stick `Mouse.move(dx, dy)` to a fixed `8ms` (125Hz) timer with sub-pixel remainder accumulation instead of running unthrottled in `loop()`.
   - Add edge-detection and configurable repeat cooldown (`repeat_ms`) for scroll wheel bindings (`L1`/`R1`) and state-change tracking so `Keyboard.press`/`release` only fire on transitions.
2. **Add Dynamic JSON + NVS Persistence:**
   - Parse incoming newline-delimited JSON from `Serial` using `ArduinoJson` (v7).
   - Store up to 4 JSON profiles in ESP32 flash using the built-in `Preferences` (NVS) library so custom layouts survive power cycles.
   - Support hardware shortcut (`Home + D-Pad Left/Right`) to cycle active NVS profile slots standalone without the Mac app open.

### Phase 5: GitHub Actions macOS Universal Build Pipeline
1. Create `.github/workflows/build-release.yml` triggered on pushes to `main` and version tags (`v*`).
2. Configure a `macos-latest` job using `tauri-apps/tauri-action@v0` with `--target universal-apple-darwin` to produce an Apple Silicon + Intel universal `.dmg` and `.app` bundle.
3. Add a parallel `windows-latest` job running `cargo check` and `npm run build` to ensure Windows local builds never regress.