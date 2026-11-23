use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PingResponse {
    pub status: String,
    pub device: String,
    pub fw: String,
    pub active_profile: u8,
    #[serde(default)]
    pub controller_connected: Option<bool>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HeartbeatEvent {
    pub event: String,
    pub device: String,
    pub fw: String,
    pub active_profile: u8,
    pub controller_connected: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StickConfig {
    pub mode: String, // "digital_keys" | "mouse" | "none"
    pub deadzone: i16,
    #[serde(default)]
    pub up: Option<String>,
    #[serde(default)]
    pub down: Option<String>,
    #[serde(default)]
    pub left: Option<String>,
    #[serde(default)]
    pub right: Option<String>,
    #[serde(default)]
    pub sensitivity: Option<f32>,
    #[serde(default)]
    pub curve: Option<String>,
    #[serde(default)]
    pub invert_y: Option<bool>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SticksConfig {
    pub left: StickConfig,
    pub right: StickConfig,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ButtonBinding {
    #[serde(rename = "type")]
    pub binding_type: String, // "key" | "mouse_button" | "mouse_scroll" | "consumer_control" | "gyro_aim" | "none"
    #[serde(default)]
    pub code: Option<String>,
    #[serde(default)]
    pub delta: Option<i8>,
    #[serde(default)]
    pub repeat_ms: Option<u16>,
    #[serde(default)]
    pub threshold: Option<u16>,
    #[serde(default)]
    pub gyro_axis: Option<String>,
    #[serde(default)]
    pub gyro_sensitivity: Option<f32>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Profile {
    pub slot: u8,
    pub name: String,
    pub sticks: SticksConfig,
    pub buttons: HashMap<String, ButtonBinding>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SerialPortEntry {
    pub name: String,
    pub port_type: String,
    pub vid: Option<u16>,
    pub pid: Option<u16>,
    pub manufacturer: Option<String>,
    pub product: Option<String>,
    pub is_esp32: bool,
    #[serde(default)]
    pub is_pico: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InputTelemetry {
    pub event: String,
    pub buttons: u32,
    pub dpad: u8,
    pub lx: i32,
    pub ly: i32,
    pub rx: i32,
    pub ry: i32,
    pub l2: i32,
    pub r2: i32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "cmd")]
pub enum OutgoingCommand {
    #[serde(rename = "PING")]
    Ping,
    #[serde(rename = "GET_PROFILE")]
    GetProfile { slot: u8 },
    #[serde(rename = "SET_SLOT")]
    SetSlot { slot: u8 },
    #[serde(rename = "WRITE_PROFILE")]
    WriteProfile {
        slot: u8,
        name: String,
        sticks: SticksConfig,
        buttons: HashMap<String, ButtonBinding>,
    },
    #[serde(rename = "STREAM_INPUTS")]
    StreamInputs { enabled: bool },
    #[serde(rename = "BOOTLOADER")]
    Bootloader,
}

