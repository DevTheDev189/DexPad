import { ref, computed } from 'vue';
import type { Profile, ControllerControlId, ButtonBinding, StickConfig } from '../types/keymap';

const DEFAULT_PROFILES: Profile[] = [
  // Slot 0: Minecraft
  {
    slot: 0,
    name: 'Minecraft',
    sticks: {
      left: {
        mode: 'digital_keys',
        deadzone: 180,
        up: 'w',
        down: 's',
        left: 'a',
        right: 'd',
      },
      right: {
        mode: 'mouse',
        deadzone: 45,
        sensitivity: 1.35,
        curve: 'exponential',
        invert_y: false,
      },
    },
    buttons: {
      a: { type: 'key', code: 'KEY_SPACE' },
      b: { type: 'key', code: 'KEY_LEFT_SHIFT' },
      x: { type: 'key', code: 'q' },
      y: { type: 'key', code: 'e' },
      l1: { type: 'mouse_scroll', delta: 1, repeat_ms: 120 },
      r1: { type: 'mouse_scroll', delta: -1, repeat_ms: 120 },
      l2: { type: 'mouse_button', code: 'MOUSE_RIGHT', threshold: 40 },
      r2: { type: 'mouse_button', code: 'MOUSE_LEFT', threshold: 40 },
      l3: { type: 'key', code: 'KEY_LEFT_CTRL' },
      r3: { type: 'key', code: 'f' },
      dpad_up: { type: 'key', code: 'KEY_F5' },
      dpad_down: { type: 'key', code: 'KEY_F3' },
      dpad_left: { type: 'key', code: '1' },
      dpad_right: { type: 'key', code: 't' },
      menu: { type: 'key', code: 'KEY_ESC' },
      options: { type: 'key', code: 'KEY_RETURN' },
      home: { type: 'key', code: 'KEY_TAB' },
    },
  },
  // Slot 1: 2D Platformer
  {
    slot: 1,
    name: '2D Platformer',
    sticks: {
      left: {
        mode: 'digital_keys',
        deadzone: 150,
        up: 'KEY_UP_ARROW',
        down: 'KEY_DOWN_ARROW',
        left: 'KEY_LEFT_ARROW',
        right: 'KEY_RIGHT_ARROW',
      },
      right: {
        mode: 'none',
        deadzone: 45,
        sensitivity: 1.0,
      },
    },
    buttons: {
      a: { type: 'key', code: 'z' },
      x: { type: 'key', code: 'x' },
      y: { type: 'key', code: 'a' },
      b: { type: 'key', code: 'c' },
      r2: { type: 'key', code: 'KEY_LEFT_SHIFT', threshold: 40 },
      menu: { type: 'key', code: 'KEY_ESC' },
      home: { type: 'key', code: 'KEY_TAB' },
    },
  },
  // Slot 2: Desktop Mouse Mode
  {
    slot: 2,
    name: 'Desktop Mouse',
    sticks: {
      left: {
        mode: 'none',
        deadzone: 100,
      },
      right: {
        mode: 'mouse',
        deadzone: 30,
        sensitivity: 1.6,
        curve: 'exponential',
        invert_y: false,
      },
    },
    buttons: {
      a: { type: 'mouse_button', code: 'MOUSE_LEFT' },
      b: { type: 'mouse_button', code: 'MOUSE_RIGHT' },
      x: { type: 'mouse_button', code: 'MOUSE_MIDDLE' },
      l1: { type: 'mouse_scroll', delta: 1, repeat_ms: 100 },
      r1: { type: 'mouse_scroll', delta: -1, repeat_ms: 100 },
      home: { type: 'key', code: 'KEY_LEFT_GUI' }, // ⌘ macOS Mission Control
    },
  },
  // Slot 3: Action FPS
  {
    slot: 3,
    name: 'Action FPS',
    sticks: {
      left: {
        mode: 'digital_keys',
        deadzone: 160,
        up: 'w',
        down: 's',
        left: 'a',
        right: 'd',
      },
      right: {
        mode: 'mouse',
        deadzone: 40,
        sensitivity: 1.5,
        curve: 'linear',
        invert_y: false,
      },
    },
    buttons: {
      a: { type: 'key', code: 'KEY_SPACE' },
      b: { type: 'key', code: 'c' },
      x: { type: 'key', code: 'r' },
      y: { type: 'key', code: 'f' },
      l2: { type: 'mouse_button', code: 'MOUSE_RIGHT', threshold: 40 },
      r2: { type: 'mouse_button', code: 'MOUSE_LEFT', threshold: 40 },
      l3: { type: 'key', code: 'KEY_LEFT_SHIFT' },
    },
  },
];

export function useProfiles() {
  const profiles = ref<Profile[]>(JSON.parse(JSON.stringify(DEFAULT_PROFILES)));
  const activeSlot = ref(0);
  const selectedControl = ref<ControllerControlId | null>('a');
  const hoveredControl = ref<ControllerControlId | null>(null);
  const isDirty = ref(false);

  const activeProfile = computed<Profile>(() => {
    return profiles.value[activeSlot.value] || profiles.value[0];
  });

  const selectSlot = (slot: number) => {
    if (slot >= 0 && slot < profiles.value.length) {
      activeSlot.value = slot;
    }
  };

  const renameProfile = (slot: number, name: string) => {
    if (profiles.value[slot]) {
      profiles.value[slot].name = name;
      isDirty.value = true;
    }
  };

  const updateButtonBinding = (controlId: string, binding: ButtonBinding) => {
    if (!activeProfile.value.buttons) {
      activeProfile.value.buttons = {};
    }
    activeProfile.value.buttons[controlId] = { ...binding };
    isDirty.value = true;
  };

  const updateStickConfig = (stick: 'left' | 'right', config: StickConfig) => {
    activeProfile.value.sticks[stick] = { ...config };
    isDirty.value = true;
  };

  const markClean = () => {
    isDirty.value = false;
  };

  const exportCurrentProfileJson = (): string => {
    return JSON.stringify(activeProfile.value, null, 2);
  };

  const importProfileJson = (jsonStr: string): boolean => {
    try {
      const parsed = JSON.parse(jsonStr);
      if (parsed && typeof parsed.name === 'string' && parsed.sticks && parsed.buttons) {
        profiles.value[activeSlot.value] = {
          ...parsed,
          slot: activeSlot.value,
        };
        isDirty.value = true;
        return true;
      }
      return false;
    } catch {
      return false;
    }
  };

  return {
    profiles,
    activeSlot,
    activeProfile,
    selectedControl,
    hoveredControl,
    isDirty,
    selectSlot,
    renameProfile,
    updateButtonBinding,
    updateStickConfig,
    markClean,
    exportCurrentProfileJson,
    importProfileJson,
  };
}
