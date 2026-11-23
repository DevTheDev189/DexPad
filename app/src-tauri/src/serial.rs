use crate::models::{ButtonBinding, OutgoingCommand, SerialPortEntry, SticksConfig};
use serialport::{SerialPort, SerialPortType};
use std::collections::HashMap;
use std::io::{BufRead, BufReader, Write};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;
use tauri::{AppHandle, Emitter};

pub struct SerialManager {
    port_name: Option<String>,
    writer: Option<Arc<Mutex<Box<dyn SerialPort>>>>,
    is_connected: Arc<AtomicBool>,
}

impl SerialManager {
    pub fn new() -> Self {
        Self {
            port_name: None,
            writer: None,
            is_connected: Arc::new(AtomicBool::new(false)),
        }
    }

    pub fn is_connected(&self) -> bool {
        self.is_connected.load(Ordering::SeqCst)
    }

    pub fn current_port(&self) -> Option<String> {
        self.port_name.clone()
    }

    pub fn disconnect(&mut self) {
        self.is_connected.store(false, Ordering::SeqCst);
        self.writer = None;
        self.port_name = None;
    }

    pub fn connect(
        &mut self,
        app_handle: AppHandle,
        port_name: String,
        baud_rate: u32,
    ) -> Result<(), String> {
        // Disconnect if previously connected
        self.disconnect();

        let port = serialport::new(&port_name, baud_rate)
            .timeout(Duration::from_millis(100))
            .open()
            .map_err(|e| format!("Failed to open serial port {}: {}", port_name, e))?;

        let port_reader_clone = port
            .try_clone()
            .map_err(|e| format!("Failed to clone serial port handle: {}", e))?;

        let writer_arc = Arc::new(Mutex::new(port));
        let is_connected_flag = Arc::new(AtomicBool::new(true));

        self.writer = Some(writer_arc.clone());
        self.port_name = Some(port_name.clone());
        self.is_connected = is_connected_flag.clone();

        // Spawn background reader thread
        let handle_clone = app_handle.clone();
        let conn_flag = is_connected_flag.clone();
        let port_label = port_name.clone();

        thread::spawn(move || {
            let mut reader = BufReader::new(port_reader_clone);
            let mut line = String::new();

            while conn_flag.load(Ordering::SeqCst) {
                line.clear();
                match reader.read_line(&mut line) {
                    Ok(bytes_read) => {
                        if bytes_read > 0 {
                            let trimmed = line.trim();
                            if !trimmed.is_empty() {
                                // Emit raw message
                                let _ = handle_clone.emit("serial-message", trimmed);

                                // Check if JSON
                                if let Ok(val) = serde_json::from_str::<serde_json::Value>(trimmed) {
                                    if let Some(event) = val.get("event").and_then(|v| v.as_str()) {
                                        if event == "INPUT" {
                                            let _ = handle_clone.emit("serial-telemetry", &val);
                                        } else if event == "HEARTBEAT" {
                                            let _ = handle_clone.emit("serial-heartbeat", &val);
                                        }
                                    } else if let Some(cmd) = val.get("cmd").and_then(|v| v.as_str()) {
                                        if cmd == "PROFILE_DATA" {
                                            let _ = handle_clone.emit("serial-profile-data", &val);
                                        }
                                    } else if let Some(_status) = val.get("status").and_then(|v| v.as_str()) {
                                        let _ = handle_clone.emit("serial-ack", &val);
                                    }
                                }
                            }
                        }
                    }
                    Err(ref e) if e.kind() == std::io::ErrorKind::TimedOut => {
                        // Timeout is normal when no data arrives; continue polling
                        thread::sleep(Duration::from_millis(5));
                    }
                    Err(e) => {
                        // Real disconnection or error
                        eprintln!("Serial read error on {}: {}", port_label, e);
                        conn_flag.store(false, Ordering::SeqCst);
                        let _ = handle_clone.emit(
                            "serial-disconnected",
                            format!("Serial read error: {}", e),
                        );
                        break;
                    }
                }
            }
        });

        // Send PING handshake right after connecting
        let _ = self.write_raw(b"{\"cmd\":\"PING\"}\n");

        Ok(())
    }

    pub fn write_raw(&self, data: &[u8]) -> Result<(), String> {
        if !self.is_connected() {
            return Err("Serial port is not connected".into());
        }

        if let Some(ref writer_arc) = self.writer {
            let mut writer = writer_arc
                .lock()
                .map_err(|e| format!("Lock poisoned: {}", e))?;
            writer
                .write_all(data)
                .map_err(|e| format!("Write failed: {}", e))?;
            writer
                .flush()
                .map_err(|e| format!("Flush failed: {}", e))?;
            Ok(())
        } else {
            Err("No writer available".into())
        }
    }

    pub fn send_command(&self, cmd: OutgoingCommand) -> Result<(), String> {
        let mut json_str = serde_json::to_string(&cmd)
            .map_err(|e| format!("Failed to serialize command: {}", e))?;
        json_str.push('\n');
        self.write_raw(json_str.as_bytes())
    }
}

pub fn enumerate_ports() -> Vec<SerialPortEntry> {
    let mut result = Vec::new();
    if let Ok(ports) = serialport::available_ports() {
        for p in ports {
            let mut vid = None;
            let mut pid = None;
            let mut manufacturer = None;
            let mut product = None;
            let mut port_type_str = "Unknown".to_string();

            match &p.port_type {
                SerialPortType::UsbPort(info) => {
                    vid = Some(info.vid);
                    pid = Some(info.pid);
                    manufacturer = info.manufacturer.clone();
                    product = info.product.clone();
                    port_type_str = "USB".to_string();
                }
                SerialPortType::PciPort => {
                    port_type_str = "PCI".to_string();
                }
                SerialPortType::BluetoothPort => {
                    port_type_str = "Bluetooth".to_string();
                }
                _ => {}
            }

            // Detect Raspberry Pi Pico 2 W / Pico W (Raspberry Pi VID is 0x2E8A)
            let is_pico = vid == Some(0x2E8A)
                || manufacturer
                    .as_ref()
                    .map(|m| m.to_lowercase().contains("raspberry"))
                    .unwrap_or(false)
                || product
                    .as_ref()
                    .map(|pr| pr.to_lowercase().contains("pico") || pr.to_lowercase().contains("rp2"))
                    .unwrap_or(false);

            // Detect ESP32-S3 (Espressif VID is 0x303A)
            let is_esp32 = vid == Some(0x303A)
                || p.port_name.to_lowercase().contains("usbmodem")
                || manufacturer
                    .as_ref()
                    .map(|m| m.to_lowercase().contains("espressif"))
                    .unwrap_or(false)
                || product
                    .as_ref()
                    .map(|pr| pr.to_lowercase().contains("esp32"))
                    .unwrap_or(false);

            result.push(SerialPortEntry {
                name: p.port_name,
                port_type: port_type_str,
                vid,
                pid,
                manufacturer,
                product,
                is_esp32,
                is_pico,
            });
        }
    }
    result
}

// ----------------------------------------------------------------------------
// Tauri Commands
// ----------------------------------------------------------------------------
#[tauri::command]
pub fn auto_connect_dongle(
    app_handle: AppHandle,
    manager_state: tauri::State<Arc<Mutex<SerialManager>>>,
) -> Result<Option<String>, String> {
    let mut manager = manager_state
        .lock()
        .map_err(|e| format!("Manager lock error: {}", e))?;

    if manager.is_connected() {
        return Ok(manager.current_port());
    }

    let ports = enumerate_ports();
    // Prioritize Pico 2 W / Pico W, then ESP32
    if let Some(target_port) = ports.iter().find(|p| p.is_pico).or_else(|| ports.iter().find(|p| p.is_esp32)) {
        let name = target_port.name.clone();
        manager.connect(app_handle, name.clone(), 115200)?;
        return Ok(Some(name));
    }

    Ok(None)
}

#[tauri::command]
pub fn get_ports() -> Result<Vec<SerialPortEntry>, String> {
    Ok(enumerate_ports())
}

#[tauri::command]
pub fn connect_port(
    app_handle: AppHandle,
    manager_state: tauri::State<Arc<Mutex<SerialManager>>>,
    port_name: String,
    baud_rate: Option<u32>,
) -> Result<(), String> {
    let mut manager = manager_state
        .lock()
        .map_err(|e| format!("Manager lock error: {}", e))?;
    manager.connect(app_handle, port_name, baud_rate.unwrap_or(115200))
}

#[tauri::command]
pub fn disconnect_port(
    manager_state: tauri::State<Arc<Mutex<SerialManager>>>,
) -> Result<(), String> {
    let mut manager = manager_state
        .lock()
        .map_err(|e| format!("Manager lock error: {}", e))?;
    manager.disconnect();
    Ok(())
}

#[tauri::command]
pub fn is_connected(
    manager_state: tauri::State<Arc<Mutex<SerialManager>>>,
) -> Result<bool, String> {
    let manager = manager_state
        .lock()
        .map_err(|e| format!("Manager lock error: {}", e))?;
    Ok(manager.is_connected())
}

#[tauri::command]
pub fn send_profile(
    manager_state: tauri::State<Arc<Mutex<SerialManager>>>,
    slot: u8,
    name: String,
    sticks: SticksConfig,
    buttons: HashMap<String, ButtonBinding>,
) -> Result<(), String> {
    let manager = manager_state
        .lock()
        .map_err(|e| format!("Manager lock error: {}", e))?;
    manager.send_command(OutgoingCommand::WriteProfile {
        slot,
        name,
        sticks,
        buttons,
    })
}

#[tauri::command]
pub fn switch_slot(
    manager_state: tauri::State<Arc<Mutex<SerialManager>>>,
    slot: u8,
) -> Result<(), String> {
    let manager = manager_state
        .lock()
        .map_err(|e| format!("Manager lock error: {}", e))?;
    manager.send_command(OutgoingCommand::SetSlot { slot })
}

#[tauri::command]
pub fn request_profile(
    manager_state: tauri::State<Arc<Mutex<SerialManager>>>,
    slot: u8,
) -> Result<(), String> {
    let manager = manager_state
        .lock()
        .map_err(|e| format!("Manager lock error: {}", e))?;
    manager.send_command(OutgoingCommand::GetProfile { slot })
}

#[tauri::command]
pub fn set_input_stream(
    manager_state: tauri::State<Arc<Mutex<SerialManager>>>,
    enabled: bool,
) -> Result<(), String> {
    let manager = manager_state
        .lock()
        .map_err(|e| format!("Manager lock error: {}", e))?;
    manager.send_command(OutgoingCommand::StreamInputs { enabled })
}

#[tauri::command]
pub fn reboot_to_bootloader(
    manager_state: tauri::State<Arc<Mutex<SerialManager>>>,
) -> Result<(), String> {
    let manager = manager_state
        .lock()
        .map_err(|e| format!("Manager lock error: {}", e))?;
    manager.send_command(OutgoingCommand::Bootloader)
}

#[tauri::command]
pub fn send_raw_command(
    manager_state: tauri::State<Arc<Mutex<SerialManager>>>,
    command: String,
) -> Result<(), String> {
    let manager = manager_state
        .lock()
        .map_err(|e| format!("Manager lock error: {}", e))?;
    let mut data = command;
    if !data.ends_with('\n') {
        data.push('\n');
    }
    manager.write_raw(data.as_bytes())
}

// ----------------------------------------------------------------------------
// Raspberry Pi Pico Bootloader Detection & 1-Click Firmware Flasher
// ----------------------------------------------------------------------------

#[derive(serde::Serialize, serde::Deserialize, Clone, Debug)]
pub struct PicoBootloaderDevice {
    pub mount_path: String,
    pub volume_name: String,
    pub board_id: String,
    pub model: String,
    pub is_pico_2: bool,
}

const FIRMWARE_PICO2W_BYTES: &[u8] = include_bytes!("../firmware/dexpad_pico2w.uf2");
const FIRMWARE_PICOW_BYTES: &[u8] = include_bytes!("../firmware/dexpad_picow.uf2");

pub fn scan_pico_bootloaders() -> Vec<PicoBootloaderDevice> {
    let mut found = Vec::new();

    #[cfg(target_os = "windows")]
    {
        for letter in b'D'..=b'Z' {
            let drive_str = format!("{}:\\", letter as char);
            let info_file = format!("{}INFO_UF2.TXT", drive_str);
            let p = std::path::Path::new(&info_file);
            if p.exists() {
                if let Ok(content) = std::fs::read_to_string(p) {
                    let is_pico_2 = content.contains("RP2350") || content.contains("Pico 2");
                    let model = if is_pico_2 {
                        "Raspberry Pi Pico 2 / 2 W (RP2350)".to_string()
                    } else if content.contains("Pico W") {
                        "Raspberry Pi Pico W (RP2040)".to_string()
                    } else {
                        "Raspberry Pi Pico (RP2040)".to_string()
                    };
                    let board_id = if is_pico_2 {
                        "RP2350".to_string()
                    } else {
                        "RPI-RP2".to_string()
                    };
                    found.push(PicoBootloaderDevice {
                        mount_path: drive_str.clone(),
                        volume_name: if is_pico_2 { "RP2350".to_string() } else { "RPI-RP2".to_string() },
                        board_id,
                        model,
                        is_pico_2,
                    });
                }
            }
        }
    }

    #[cfg(target_os = "macos")]
    {
        let volumes = std::path::Path::new("/Volumes");
        if let Ok(entries) = std::fs::read_dir(volumes) {
            for entry in entries.flatten() {
                let path = entry.path();
                let info_file = path.join("INFO_UF2.TXT");
                if info_file.exists() {
                    if let Ok(content) = std::fs::read_to_string(&info_file) {
                        let is_pico_2 = content.contains("RP2350") || content.contains("Pico 2");
                        let model = if is_pico_2 {
                            "Raspberry Pi Pico 2 / 2 W (RP2350)".to_string()
                        } else if content.contains("Pico W") {
                            "Raspberry Pi Pico W (RP2040)".to_string()
                        } else {
                            "Raspberry Pi Pico (RP2040)".to_string()
                        };
                        let board_id = if is_pico_2 {
                            "RP2350".to_string()
                        } else {
                            "RPI-RP2".to_string()
                        };
                        let vol_name = path
                            .file_name()
                            .and_then(|n| n.to_str())
                            .unwrap_or("RPI-RP2")
                            .to_string();
                        found.push(PicoBootloaderDevice {
                            mount_path: path.to_string_lossy().to_string(),
                            volume_name: vol_name,
                            board_id,
                            model,
                            is_pico_2,
                        });
                    }
                }
            }
        }
    }

    found
}

#[tauri::command]
pub fn detect_pico_bootloader() -> Result<Option<PicoBootloaderDevice>, String> {
    let list = scan_pico_bootloaders();
    Ok(list.into_iter().next())
}

#[tauri::command]
pub fn flash_pico_firmware(mount_path: String, target: Option<String>) -> Result<String, String> {
    let dest_dir = std::path::Path::new(&mount_path);
    if !dest_dir.exists() {
        return Err(format!("Mount path '{}' does not exist or device was unmounted.", mount_path));
    }

    // Determine target based on parameter or reading INFO_UF2.TXT
    let info_path = dest_dir.join("INFO_UF2.TXT");
    let is_pico_2 = if let Some(ref t) = target {
        t.to_lowercase().contains("2") || t.to_lowercase().contains("rp2350")
    } else if info_path.exists() {
        let content = std::fs::read_to_string(&info_path).unwrap_or_default();
        content.contains("RP2350") || content.contains("Pico 2")
    } else {
        true
    };

    let fw_bytes = if is_pico_2 {
        FIRMWARE_PICO2W_BYTES
    } else {
        FIRMWARE_PICOW_BYTES
    };

    let target_file = dest_dir.join("dexpad_firmware.uf2");
    std::fs::write(&target_file, fw_bytes)
        .map_err(|e| format!("Failed to write UF2 firmware to {}: {}", target_file.display(), e))?;

    let board_label = if is_pico_2 { "Raspberry Pi Pico 2 W" } else { "Raspberry Pi Pico W" };
    Ok(format!("Firmware successfully written to {}. Board is flashing and rebooting into DexPad Dongle mode...", board_label))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_list_ports() {
        let ports = enumerate_ports();
        println!("FOUND {} PORTS:", ports.len());
        for p in &ports {
            println!("  Port: {} | Type: {} | VID: {:04X?} | PID: {:04X?} | Mfr: {:?} | Prod: {:?} | ESP32: {}",
                p.name, p.port_type, p.vid, p.pid, p.manufacturer, p.product, p.is_esp32);
        }

        // Test opening each port at 115200 and checking for ping/heartbeat
        for p in &ports {
            println!("\nTesting connection to {}...", p.name);
            match serialport::new(&p.name, 115200).timeout(std::time::Duration::from_millis(500)).open() {
                Ok(mut s) => {
                    println!("  Successfully OPENED {}", p.name);
                    let _ = s.write_all(b"{\"cmd\":\"PING\"}\n");
                    let _ = s.flush();
                    let mut buf = [0u8; 1024];
                    match s.read(&mut buf) {
                        Ok(n) => {
                            let resp = String::from_utf8_lossy(&buf[..n]);
                            println!("  Received from {}: {:?}", p.name, resp);
                        }
                        Err(e) => {
                            println!("  Read timeout/error from {}: {}", p.name, e);
                        }
                    }
                }
                Err(e) => {
                    println!("  Failed to open {}: {}", p.name, e);
                }
            }
        }
    }
}
