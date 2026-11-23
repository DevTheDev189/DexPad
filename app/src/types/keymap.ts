export type StickMode = 'digital_keys' | 'mouse' | 'none';
export type StickCurve = 'linear' | 'exponential' | 'aggressive';
export type ButtonBindingType = 'key' | 'mouse_button' | 'mouse_scroll' | 'consumer_control' | 'gyro_aim' | 'none';

export interface StickConfig {
  mode: StickMode;
  deadzone: number;
  up?: string;
  down?: string;
  left?: string;
  right?: string;
  sensitivity?: number;
  curve?: StickCurve;
  invert_y?: boolean;
}

export interface SticksConfig {
  left: StickConfig;
  right: StickConfig;
}

export interface ButtonBinding {
  type: ButtonBindingType;
  code?: string;
  delta?: number;
  repeat_ms?: number;
  threshold?: number;
  gyro_axis?: 'pitch_yaw' | 'yaw' | 'roll_pitch';
  gyro_sensitivity?: number;
}

export interface Profile {
  slot: number;
  name: string;
  gameTitle?: string;
  coverUrl?: string;
  genre?: string;
  description?: string;
  sticks: SticksConfig;
  buttons: Record<string, ButtonBinding>;
}

export interface GameSearchResult {
  id: number;
  name: string;
  background_image: string;
  released?: string;
  genres?: { name: string }[];
}

export interface SerialPortEntry {
  name: string;
  port_type: string;
  vid?: number;
  pid?: number;
  manufacturer?: string;
  product?: string;
  is_esp32: boolean;
  is_pico?: boolean;
}

export interface InputTelemetry {
  event: string;
  buttons: number;
  dpad: number;
  lx: number;
  ly: number;
  rx: number;
  ry: number;
  l2: number;
  r2: number;
}

export type ControllerControlId =
  | 'a'
  | 'b'
  | 'x'
  | 'y'
  | 'l1'
  | 'r1'
  | 'l2'
  | 'r2'
  | 'l4'
  | 'r4'
  | 'l3'
  | 'r3'
  | 'dpad'
  | 'dpad_up'
  | 'dpad_down'
  | 'dpad_left'
  | 'dpad_right'
  | 'menu'
  | 'options'
  | 'home'
  | 'touchpad'
  | 'left_stick'
  | 'right_stick';

export interface KeyOption {
  code: string;
  label: string;
  category: 'mac' | 'alphanumeric' | 'navigation' | 'function' | 'mouse' | 'consumer' | 'special';
}

export const MAC_KEY_OPTIONS: KeyOption[] = [
  // Special macOS modifier keys
  { code: 'KEY_LEFT_GUI', label: 'Command (Left)', category: 'mac' },
  { code: 'KEY_RIGHT_GUI', label: 'Command (Right)', category: 'mac' },
  { code: 'KEY_LEFT_ALT', label: 'Option / Alt (Left)', category: 'mac' },
  { code: 'KEY_RIGHT_ALT', label: 'Option / Alt (Right)', category: 'mac' },
  { code: 'KEY_LEFT_CTRL', label: 'Control (Left)', category: 'mac' },
  { code: 'KEY_RIGHT_CTRL', label: 'Control (Right)', category: 'mac' },
  { code: 'KEY_LEFT_SHIFT', label: 'Shift (Left)', category: 'mac' },
  { code: 'KEY_RIGHT_SHIFT', label: 'Shift (Right)', category: 'mac' },
  { code: 'KEY_SPACE', label: 'Space', category: 'navigation' },
  { code: 'KEY_RETURN', label: 'Return / Enter', category: 'navigation' },
  { code: 'KEY_ESC', label: 'Escape', category: 'navigation' },
  { code: 'KEY_TAB', label: 'Tab', category: 'navigation' },
  { code: 'KEY_BACKSPACE', label: 'Delete / Backspace', category: 'navigation' },

  // Consumer Media & Brightness Controls
  { code: 'MEDIA_VOLUME_UP', label: 'Volume Up', category: 'consumer' },
  { code: 'MEDIA_VOLUME_DOWN', label: 'Volume Down', category: 'consumer' },
  { code: 'MEDIA_MUTE', label: 'Mute Audio', category: 'consumer' },
  { code: 'MEDIA_PLAY_PAUSE', label: 'Play / Pause', category: 'consumer' },
  { code: 'MEDIA_NEXT', label: 'Next Track', category: 'consumer' },
  { code: 'MEDIA_PREV', label: 'Previous Track', category: 'consumer' },
  { code: 'MEDIA_BRIGHTNESS_UP', label: 'Display Brightness Up', category: 'consumer' },
  { code: 'MEDIA_BRIGHTNESS_DOWN', label: 'Display Brightness Down', category: 'consumer' },

  // Gyro Aim Action
  { code: 'GYRO_AIM', label: 'Hold for Gyro Precision Aim', category: 'special' },

  // Arrows
  { code: 'KEY_UP_ARROW', label: 'Arrow Up', category: 'navigation' },
  { code: 'KEY_DOWN_ARROW', label: 'Arrow Down', category: 'navigation' },
  { code: 'KEY_LEFT_ARROW', label: 'Arrow Left', category: 'navigation' },
  { code: 'KEY_RIGHT_ARROW', label: 'Arrow Right', category: 'navigation' },

  // Common Alphanumeric
  { code: 'w', label: 'W', category: 'alphanumeric' },
  { code: 'a', label: 'A', category: 'alphanumeric' },
  { code: 's', label: 'S', category: 'alphanumeric' },
  { code: 'd', label: 'D', category: 'alphanumeric' },
  { code: 'q', label: 'Q', category: 'alphanumeric' },
  { code: 'e', label: 'E', category: 'alphanumeric' },
  { code: 'r', label: 'R', category: 'alphanumeric' },
  { code: 'f', label: 'F', category: 'alphanumeric' },
  { code: 'c', label: 'C', category: 'alphanumeric' },
  { code: 'z', label: 'Z', category: 'alphanumeric' },
  { code: 'x', label: 'X', category: 'alphanumeric' },
  { code: 't', label: 'T', category: 'alphanumeric' },
  { code: '1', label: '1', category: 'alphanumeric' },
  { code: '2', label: '2', category: 'alphanumeric' },
  { code: '3', label: '3', category: 'alphanumeric' },
  { code: '4', label: '4', category: 'alphanumeric' },
  { code: '5', label: '5', category: 'alphanumeric' },

  // Function Keys
  { code: 'KEY_F1', label: 'F1', category: 'function' },
  { code: 'KEY_F2', label: 'F2', category: 'function' },
  { code: 'KEY_F3', label: 'F3', category: 'function' },
  { code: 'KEY_F4', label: 'F4', category: 'function' },
  { code: 'KEY_F5', label: 'F5', category: 'function' },
  { code: 'KEY_F6', label: 'F6', category: 'function' },
  { code: 'KEY_F7', label: 'F7', category: 'function' },
  { code: 'KEY_F8', label: 'F8', category: 'function' },
  { code: 'KEY_F9', label: 'F9', category: 'function' },
  { code: 'KEY_F10', label: 'F10', category: 'function' },
  { code: 'KEY_F11', label: 'F11', category: 'function' },
  { code: 'KEY_F12', label: 'F12', category: 'function' },

  // Mouse Actions
  { code: 'MOUSE_LEFT', label: 'Primary Left Click', category: 'mouse' },
  { code: 'MOUSE_RIGHT', label: 'Secondary Right Click', category: 'mouse' },
  { code: 'MOUSE_MIDDLE', label: 'Middle Mouse Click', category: 'mouse' },
  { code: 'SCROLL_UP', label: 'Mouse Scroll Wheel Up', category: 'mouse' },
  { code: 'SCROLL_DOWN', label: 'Mouse Scroll Wheel Down', category: 'mouse' },
];
