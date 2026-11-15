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
            });
        }
    }
    result
}

// ----------------------------------------------------------------------------
// Tauri Commands
// ----------------------------------------------------------------------------
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
