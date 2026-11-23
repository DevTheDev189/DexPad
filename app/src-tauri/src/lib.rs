pub mod models;
pub mod serial;

use serial::SerialManager;
use std::sync::{Arc, Mutex};
use tauri::Manager;

pub fn run() {
    let serial_manager = Arc::new(Mutex::new(SerialManager::new()));

    tauri::Builder::default()
        .manage(serial_manager)
        .setup(|app| {
            if let Some(window) = app.get_webview_window("main") {
                // Apply macOS Vibrancy (HudWindow / UnderWindowBackground)
                #[cfg(target_os = "macos")]
                {
                    use window_vibrancy::{apply_vibrancy, NSVisualEffectMaterial, NSVisualEffectState};
                    let _ = apply_vibrancy(
                        &window,
                        NSVisualEffectMaterial::HudWindow,
                        Some(NSVisualEffectState::Active),
                        None,
                    );
                }

                // Apply Windows Mica / Acrylic Translucency
                #[cfg(target_os = "windows")]
                {
                    use window_vibrancy::{apply_acrylic, apply_mica};
                    // Try Mica first (Windows 11), fallback to Acrylic
                    if apply_mica(&window, None).is_err() {
                        let _ = apply_acrylic(&window, Some((15, 23, 42, 140)));
                    }
                }
            }
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            serial::get_ports,
            serial::auto_connect_dongle,
            serial::connect_port,
            serial::disconnect_port,
            serial::is_connected,
            serial::send_profile,
            serial::switch_slot,
            serial::request_profile,
            serial::set_input_stream,
            serial::send_raw_command,
            serial::reboot_to_bootloader,
            serial::detect_pico_bootloader,
            serial::flash_pico_firmware,
        ])
        .run(tauri::generate_context!())
        .expect("error while running Nimbus Cosmic Bridge");
}

