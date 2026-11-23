import type { Profile, ControllerControlId, ButtonBinding } from '../types/keymap';

/**
 * Key normalization map from Steam VDF key strings to DexPad key codes
 */
const VDF_KEY_MAP: Record<string, string> = {
  SPACE: 'KEY_SPACE',
  LEFTSHIFT: 'KEY_LEFT_SHIFT',
  LSHIFT: 'KEY_LEFT_SHIFT',
  LEFTCONTROL: 'KEY_LEFT_CTRL',
  LCTRL: 'KEY_LEFT_CTRL',
  LEFTALT: 'KEY_LEFT_ALT',
  LALT: 'KEY_LEFT_ALT',
  TAB: 'KEY_TAB',
  ESCAPE: 'KEY_ESC',
  ESC: 'KEY_ESC',
  RETURN: 'KEY_RETURN',
  ENTER: 'KEY_RETURN',
  BACKSPACE: 'KEY_BACKSPACE',
  UP: 'KEY_UP_ARROW',
  DOWN: 'KEY_DOWN_ARROW',
  LEFT: 'KEY_LEFT_ARROW',
  RIGHT: 'KEY_RIGHT_ARROW',
  F1: 'KEY_F1',
  F2: 'KEY_F2',
  F3: 'KEY_F3',
  F4: 'KEY_F4',
  F5: 'KEY_F5',
  F6: 'KEY_F6',
  F7: 'KEY_F7',
  F8: 'KEY_F8',
  F9: 'KEY_F9',
  F10: 'KEY_F10',
  F11: 'KEY_F11',
  F12: 'KEY_F12',
};

/**
 * Parses a raw Steam Input VDF text into a DexPad Partial<Profile>
 */
export function parseSteamVdfToProfile(vdfText: string): Partial<Profile> {
  const buttons: Partial<Record<ControllerControlId, ButtonBinding>> = {};

  let hasMouseStick = false;
  let hasWasdStick = false;

  // Check for mouse right stick
  if (vdfText.includes('"mode"\t\t"mouse_joystick"') || vdfText.includes('"feature_mouse"')) {
    hasMouseStick = true;
  }

  // Regex patterns to match Steam Input input blocks
  // e.g. "button_a" ... "binding" "key_press SPACE, , "
  const inputBlockRegex = /"((?:button_|dpad_|left_|right_|shoulder_|trigger_|touch_)[^"]+)"\s*\{([^}]+(?:\{[^}]+\}[^}]+)*)\}/gi;
  let match: RegExpExecArray | null;

  while ((match = inputBlockRegex.exec(vdfText)) !== null) {
    const inputName = match[1].toLowerCase();
    const blockBody = match[2];

    const bindingMatch = blockBody.match(/"binding"\s+"([^",]+)/i);
    if (!bindingMatch) continue;

    const rawBinding = bindingMatch[1].trim();

    // Map to DexPad Control ID
    let controlId: ControllerControlId | null = null;
    if (inputName.includes('button_a')) controlId = 'a';
    else if (inputName.includes('button_b')) controlId = 'b';
    else if (inputName.includes('button_x')) controlId = 'x';
    else if (inputName.includes('button_y')) controlId = 'y';
    else if (inputName.includes('left_bumper') || inputName.includes('shoulder_l')) controlId = 'l1';
    else if (inputName.includes('right_bumper') || inputName.includes('shoulder_r')) controlId = 'r1';
    else if (inputName.includes('left_trigger') || inputName.includes('trigger_l')) controlId = 'l2';
    else if (inputName.includes('right_trigger') || inputName.includes('trigger_r')) controlId = 'r2';
    else if (inputName.includes('left_stick_click') || inputName.includes('joystick_left')) controlId = 'l3';
    else if (inputName.includes('right_stick_click') || inputName.includes('joystick_right')) controlId = 'r3';
    else if (inputName.includes('dpad_up')) controlId = 'dpad_up';
    else if (inputName.includes('dpad_down')) controlId = 'dpad_down';
    else if (inputName.includes('dpad_left')) controlId = 'dpad_left';
    else if (inputName.includes('dpad_right')) controlId = 'dpad_right';
    else if (inputName.includes('start') || inputName.includes('menu')) controlId = 'options';
    else if (inputName.includes('select') || inputName.includes('back')) controlId = 'menu';
    else if (inputName.includes('trackpad') || inputName.includes('touchpad')) controlId = 'touchpad';

    if (!controlId) continue;

    // Parse binding type
    if (rawBinding.startsWith('key_press')) {
      const rawKey = rawBinding.replace(/^key_press\s+/i, '').trim().toUpperCase();
      const mappedCode = VDF_KEY_MAP[rawKey] || rawKey.toLowerCase();
      buttons[controlId] = { type: 'key', code: mappedCode };
    } else if (rawBinding.startsWith('mouse_button')) {
      const btn = rawBinding.replace(/^mouse_button\s+/i, '').trim().toUpperCase();
      if (btn.includes('LEFT')) {
        buttons[controlId] = { type: 'mouse_button', code: 'MOUSE_LEFT' };
      } else if (btn.includes('RIGHT')) {
        buttons[controlId] = { type: 'mouse_button', code: 'MOUSE_RIGHT' };
      } else if (btn.includes('MIDDLE')) {
        buttons[controlId] = { type: 'mouse_button', code: 'MOUSE_MIDDLE' };
      }
    } else if (rawBinding.startsWith('mouse_wheel')) {
      const dir = rawBinding.includes('UP') ? 1 : -1;
      buttons[controlId] = { type: 'mouse_scroll', delta: dir, repeat_ms: 120 };
    }
  }

  // If left stick has WASD bindings or is a standard movement stick, set digital_keys WASD
  if (Object.keys(buttons).length > 0 || hasMouseStick) {
    hasWasdStick = true;
  }

  return {
    sticks: {
      left: hasWasdStick
        ? { mode: 'digital_keys', deadzone: 160, up: 'w', down: 's', left: 'a', right: 'd' }
        : { mode: 'none', deadzone: 160 },
      right: hasMouseStick
        ? { mode: 'mouse', deadzone: 40, sensitivity: 1.45, curve: 'exponential', invert_y: false }
        : { mode: 'mouse', deadzone: 45, sensitivity: 1.35, curve: 'linear', invert_y: false },
    },
    buttons: buttons as any,
  };
}
