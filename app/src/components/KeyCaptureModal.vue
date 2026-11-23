<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import type { ButtonBinding, ControllerControlId } from '../types/keymap';
import type { PlatformLegendMode } from '../types/controllers';
import CosmicIcon from './CosmicIcon.vue';
import ControllerButtonIcon from './ControllerButtonIcon.vue';

const props = withDefaults(
  defineProps<{
    controlId: ControllerControlId;
    platformMode?: PlatformLegendMode;
  }>(),
  {
    platformMode: 'xbox',
  }
);

const emit = defineEmits<{
  (e: 'captured', binding: ButtonBinding): void;
  (e: 'close'): void;
}>();

const capturedLabel = ref('Press any key or mouse button...');
const capturedBinding = ref<ButtonBinding | null>(null);
const selectedMediaCode = ref('');

const MEDIA_ACTIONS = [
  { label: 'Volume Up', code: 'MEDIA_VOLUME_UP' },
  { label: 'Volume Down', code: 'MEDIA_VOLUME_DOWN' },
  { label: 'Mute Audio', code: 'MEDIA_MUTE' },
  { label: 'Play / Pause', code: 'MEDIA_PLAY_PAUSE' },
  { label: 'Next Track', code: 'MEDIA_NEXT_TRACK' },
  { label: 'Previous Track', code: 'MEDIA_PREV_TRACK' },
  { label: 'Brightness Up', code: 'MEDIA_BRIGHTNESS_UP' },
  { label: 'Brightness Down', code: 'MEDIA_BRIGHTNESS_DOWN' },
];

const platformDisplayName = computed(() => {
  if (props.platformMode === 'playstation') return 'PlayStation';
  if (props.platformMode === 'nintendo') return 'Nintendo';
  return 'Xbox';
});

const formattedControlName = computed(() => {
  const id = props.controlId;
  const p = props.platformMode;
  if (p === 'playstation') {
    switch (id) {
      case 'a': return 'Cross (✕)';
      case 'b': return 'Circle (○)';
      case 'x': return 'Square (□)';
      case 'y': return 'Triangle (△)';
      case 'l1': return 'L1 Shoulder';
      case 'r1': return 'R1 Shoulder';
      case 'l2': return 'L2 Trigger';
      case 'r2': return 'R2 Trigger';
      case 'l3': return 'L3 Stick Click';
      case 'r3': return 'R3 Stick Click';
      case 'options': return 'Create / Share';
      case 'menu': return 'Options';
      case 'home': return 'PS Home';
      case 'touchpad': return 'Touchpad';
      case 'dpad_up': return 'D-Pad Up';
      case 'dpad_down': return 'D-Pad Down';
      case 'dpad_left': return 'D-Pad Left';
      case 'dpad_right': return 'D-Pad Right';
      default: return id.toUpperCase().replace('_', ' ');
    }
  } else if (p === 'nintendo') {
    switch (id) {
      case 'a': return 'A Button (Right)';
      case 'b': return 'B Button (Bottom)';
      case 'x': return 'X Button (Top)';
      case 'y': return 'Y Button (Left)';
      case 'l1': return 'L Shoulder';
      case 'r1': return 'R Shoulder';
      case 'l2': return 'ZL Trigger';
      case 'r2': return 'ZR Trigger';
      case 'l3': return 'Left Stick Click';
      case 'r3': return 'Right Stick Click';
      case 'options': return 'Minus (−)';
      case 'menu': return 'Plus (+)';
      case 'home': return 'Home';
      case 'dpad_up': return 'D-Pad Up';
      case 'dpad_down': return 'D-Pad Down';
      case 'dpad_left': return 'D-Pad Left';
      case 'dpad_right': return 'D-Pad Right';
      default: return id.toUpperCase().replace('_', ' ');
    }
  } else {
    // Xbox
    switch (id) {
      case 'a': return 'A Button (Green)';
      case 'b': return 'B Button (Red)';
      case 'x': return 'X Button (Blue)';
      case 'y': return 'Y Button (Yellow)';
      case 'l1': return 'LB (Left Bumper)';
      case 'r1': return 'RB (Right Bumper)';
      case 'l2': return 'LT (Left Trigger)';
      case 'r2': return 'RT (Right Trigger)';
      case 'l3': return 'LS (Left Stick Click)';
      case 'r3': return 'RS (Right Stick Click)';
      case 'options': return 'View Button';
      case 'menu': return 'Menu Button';
      case 'home': return 'Xbox Guide';
      case 'dpad_up': return 'D-Pad Up';
      case 'dpad_down': return 'D-Pad Down';
      case 'dpad_left': return 'D-Pad Left';
      case 'dpad_right': return 'D-Pad Right';
      default: return id.toUpperCase().replace('_', ' ');
    }
  }
});

const handleMediaSelect = (e: Event) => {
  const code = (e.target as HTMLSelectElement).value;
  selectedMediaCode.value = code;
  const item = MEDIA_ACTIONS.find((m) => m.code === code);
  if (item) {
    capturedLabel.value = `Media: ${item.label}`;
    capturedBinding.value = {
      type: 'consumer_control',
      code: item.code,
    };
  }
};

const handleKeyDown = (e: KeyboardEvent) => {
  // If user is inside the select element, let them use keyboard to browse
  if ((e.target as HTMLElement)?.tagName === 'SELECT') return;

  e.preventDefault();
  e.stopPropagation();

  if (e.key === 'Escape' && !capturedBinding.value) {
    emit('close');
    return;
  }

  let codeStr = '';
  let label = '';

  if (e.code === 'Space') {
    codeStr = 'KEY_SPACE';
    label = 'Space';
  } else if (e.code === 'Enter') {
    codeStr = 'KEY_RETURN';
    label = 'Return / Enter';
  } else if (e.code === 'Escape') {
    codeStr = 'KEY_ESC';
    label = 'Escape';
  } else if (e.code === 'Tab') {
    codeStr = 'KEY_TAB';
    label = 'Tab';
  } else if (e.code === 'Backspace') {
    codeStr = 'KEY_BACKSPACE';
    label = 'Delete / Backspace';
  } else if (e.code === 'MetaLeft' || e.code === 'MetaRight') {
    codeStr = 'KEY_LEFT_GUI';
    label = 'Command / Win';
  } else if (e.code === 'AltLeft' || e.code === 'AltRight') {
    codeStr = 'KEY_LEFT_ALT';
    label = 'Alt / Option';
  } else if (e.code === 'ControlLeft' || e.code === 'ControlRight') {
    codeStr = 'KEY_LEFT_CTRL';
    label = 'Ctrl';
  } else if (e.code === 'ShiftLeft' || e.code === 'ShiftRight') {
    codeStr = 'KEY_LEFT_SHIFT';
    label = 'Shift';
  } else if (e.code.startsWith('Key')) {
    const char = e.code.replace('Key', '').toLowerCase();
    codeStr = char;
    label = char.toUpperCase();
  } else if (e.code.startsWith('Digit')) {
    const digit = e.code.replace('Digit', '');
    codeStr = digit;
    label = digit;
  } else if (e.code.startsWith('F') && !isNaN(Number(e.code.substring(1)))) {
    codeStr = `KEY_${e.code}`;
    label = e.code;
  } else if (e.code === 'ArrowUp') {
    codeStr = 'KEY_UP_ARROW';
    label = 'Arrow Up';
  } else if (e.code === 'ArrowDown') {
    codeStr = 'KEY_DOWN_ARROW';
    label = 'Arrow Down';
  } else if (e.code === 'ArrowLeft') {
    codeStr = 'KEY_LEFT_ARROW';
    label = 'Arrow Left';
  } else if (e.code === 'ArrowRight') {
    codeStr = 'KEY_RIGHT_ARROW';
    label = 'Arrow Right';
  } else {
    codeStr = e.key.toLowerCase();
    label = e.key;
  }

  selectedMediaCode.value = '';
  capturedLabel.value = `Key: ${label}`;
  capturedBinding.value = {
    type: 'key',
    code: codeStr,
  };
};

const handleMouseDown = (e: MouseEvent) => {
  const target = e.target as HTMLElement;
  if (target.closest('.modal-actions') || target.closest('.close-btn') || target.closest('.media-dropdown-row')) {
    return;
  }

  e.preventDefault();
  let codeStr = 'MOUSE_LEFT';
  let label = 'Left Click';

  if (e.button === 0) {
    codeStr = 'MOUSE_LEFT';
    label = 'Left Click';
  } else if (e.button === 1) {
    codeStr = 'MOUSE_MIDDLE';
    label = 'Middle Click';
  } else if (e.button === 2) {
    codeStr = 'MOUSE_RIGHT';
    label = 'Right Click';
  }

  selectedMediaCode.value = '';
  capturedLabel.value = `Mouse: ${label}`;
  capturedBinding.value = {
    type: 'mouse_button',
    code: codeStr,
    threshold: 40,
  };
};

const handleWheel = (e: WheelEvent) => {
  const target = e.target as HTMLElement;
  if (target.closest('.modal-actions') || target.closest('.media-dropdown-row')) {
    return;
  }
  e.preventDefault();
  selectedMediaCode.value = '';
  if (e.deltaY < 0) {
    capturedLabel.value = 'Mouse Scroll Up';
    capturedBinding.value = {
      type: 'mouse_scroll',
      delta: 1,
      repeat_ms: 120,
    };
  } else if (e.deltaY > 0) {
    capturedLabel.value = 'Mouse Scroll Down';
    capturedBinding.value = {
      type: 'mouse_scroll',
      delta: -1,
      repeat_ms: 120,
    };
  }
};

const confirmBinding = () => {
  if (capturedBinding.value) {
    emit('captured', capturedBinding.value);
  }
};

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown);
  window.addEventListener('mousedown', handleMouseDown);
  window.addEventListener('wheel', handleWheel, { passive: false });
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown);
  window.removeEventListener('mousedown', handleMouseDown);
  window.removeEventListener('wheel', handleWheel);
});
</script>

<template>
  <div class="capture-backdrop" @click.self="emit('close')">
    <div class="capture-card glass-panel-elevated">
      <!-- Modal Header with Large Big 3 Platform Icon -->
      <div class="modal-header">
        <div class="modal-title-row">
          <div class="platform-icon-box">
            <ControllerButtonIcon :control-id="controlId" :platform-mode="platformMode" size="28" />
          </div>
          <div class="header-titles">
            <h3 class="modal-title">
              Mapping for <span class="control-name-highlight">{{ formattedControlName }}</span>
            </h3>
            <span class="platform-subtag">{{ platformDisplayName }} Profile Binding</span>
          </div>
        </div>
        <button class="close-btn" @click="emit('close')" aria-label="Close">
          <CosmicIcon name="close" size="14" />
        </button>
      </div>

      <!-- Visual Capture Area -->
      <div class="capture-visual-box">
        <div class="input-display-badge" :class="{ assigned: !!capturedBinding }">
          {{ capturedLabel }}
        </div>
        <p class="hint-text">
          Press any keyboard key or mouse button
        </p>
      </div>

      <!-- Small Neat Consumer Media Controls Dropdown -->
      <div class="media-dropdown-row">
        <label for="media-select" class="media-label">
          <span>Media Controls</span>
        </label>
        <select
          id="media-select"
          class="media-select"
          :value="selectedMediaCode"
          @change="handleMediaSelect"
        >
          <option value="">Select shortcut (Volume, Play/Pause, Brightness)...</option>
          <option v-for="item in MEDIA_ACTIONS" :key="item.code" :value="item.code">
            {{ item.label }}
          </option>
        </select>
      </div>

      <!-- Polished Glass Cancel and Apply Buttons -->
      <div class="modal-actions">
        <button class="btn-cancel" @click="emit('close')">
          Cancel
        </button>
        <button
          class="btn-apply"
          :disabled="!capturedBinding"
          @click="confirmBinding"
        >
          <CosmicIcon name="check" size="13" />
          <span>Apply</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.capture-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(3, 7, 18, 0.40);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.18s cubic-bezier(0.16, 1, 0.3, 1);
  padding: 20px;
}

.capture-card {
  width: 100%;
  max-width: 440px;
  padding: 22px 24px;
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background-color: var(--glass-surface-elevated);
  background-image: linear-gradient(
    135deg,
    rgba(var(--accent-custom-rgb, 125, 211, 252), calc(var(--glass-tint-val, 0.14) * 0.45)) 0%,
    transparent 80%
  );
  backdrop-filter: blur(var(--glass-blur-val, 28px)) saturate(190%);
  -webkit-backdrop-filter: blur(var(--glass-blur-val, 28px)) saturate(190%);
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-glass-elevated);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.platform-icon-box {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: rgba(var(--accent-custom-rgb, 125, 211, 252), 0.16);
  border: 1px solid var(--accent-custom);
  color: var(--accent-custom);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 14px rgba(var(--accent-custom-rgb, 125, 211, 252), 0.28);
}

.header-titles {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.modal-title {
  font-size: 14.5px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.25;
}

.control-name-highlight {
  color: var(--accent-custom);
}

.platform-subtag {
  font-size: 11px;
  color: var(--text-muted);
}

.close-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 6px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.close-btn:hover {
  color: var(--text-primary);
  background: var(--btn-bg);
}

.capture-visual-box {
  height: 98px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 14px;
  background: var(--glass-surface-pill);
  border: 1.5px dashed var(--glass-border);
  padding: 14px;
  gap: 8px;
}

.input-display-badge {
  font-family: var(--font-mono);
  font-size: 13.5px;
  font-weight: 700;
  color: var(--text-primary);
  background: var(--glass-surface-elevated);
  border: 1px solid var(--glass-border-subtle);
  padding: 7px 16px;
  border-radius: 9px;
  text-align: center;
  max-width: 90%;
  transition: all 0.2s ease;
}

.input-display-badge.assigned {
  border-color: var(--accent-custom);
  box-shadow: 0 0 16px rgba(var(--accent-custom-rgb, 125, 211, 252), 0.35);
  color: var(--accent-custom);
}

.hint-text {
  font-size: 11px;
  color: var(--text-muted);
  text-align: center;
}

/* Compact Media Dropdown */
.media-dropdown-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.media-label {
  font-size: 11px;
  font-weight: 700;
  color: var(--text-secondary);
  letter-spacing: 0.02em;
}

.media-select {
  width: 100%;
  padding: 8px 12px;
  border-radius: 10px;
  background: var(--input-bg);
  color: var(--text-primary);
  border: 1px solid var(--glass-border-subtle);
  font-size: 12px;
  font-family: var(--font-sans);
  outline: none;
  cursor: pointer;
  transition: all 0.2s ease;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.media-select:focus,
.media-select:hover {
  border-color: var(--accent-custom);
  box-shadow: 0 0 12px rgba(var(--accent-custom-rgb, 125, 211, 252), 0.25);
}

.media-select option {
  background: var(--bg-sky-deep, #0c1220);
  color: var(--text-primary, #ffffff);
}

/* Polished Modal Actions */
.modal-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  border-top: 1px solid var(--glass-border-subtle);
  padding-top: 14px;
}

.btn-cancel {
  padding: 8px 16px;
  border-radius: 9px;
  font-size: 12px;
  font-weight: 600;
  font-family: var(--font-sans);
  background: var(--btn-bg);
  border: 1px solid var(--glass-border-subtle);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.btn-cancel:hover {
  background: var(--glass-surface-elevated);
  border-color: var(--glass-border);
  color: var(--text-primary);
  transform: translateY(-1px);
}

.btn-apply {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 18px;
  border-radius: 9px;
  font-size: 12px;
  font-weight: 700;
  font-family: var(--font-sans);
  background: linear-gradient(
    135deg,
    rgba(var(--accent-custom-rgb, 125, 211, 252), 0.95) 0%,
    rgba(var(--accent-custom-rgb, 125, 211, 252), 0.75) 100%
  );
  border: 1px solid rgba(255, 255, 255, 0.4);
  color: var(--text-on-accent);
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(var(--accent-custom-rgb, 125, 211, 252), 0.35);
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.btn-apply:hover:not(:disabled) {
  filter: brightness(1.08);
  box-shadow: 0 6px 20px rgba(var(--accent-custom-rgb, 125, 211, 252), 0.48);
  transform: translateY(-1px);
}

.btn-apply:disabled {
  opacity: 0.45;
  cursor: not-allowed;
  filter: grayscale(0.5);
  box-shadow: none;
}

@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.97); }
  to { opacity: 1; transform: scale(1); }
}
</style>
