<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import type { ButtonBinding, ControllerControlId } from '../types/keymap';
import CosmicIcon from './CosmicIcon.vue';

defineProps<{
  controlId: ControllerControlId;
}>();

const emit = defineEmits<{
  (e: 'captured', binding: ButtonBinding): void;
  (e: 'close'): void;
}>();

const capturedLabel = ref('Press any key or mouse button...');
const capturedBinding = ref<ButtonBinding | null>(null);

const handleKeyDown = (e: KeyboardEvent) => {
  e.preventDefault();
  e.stopPropagation();

  // Escape to cancel if not bound
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
    label = 'Command (Cmd)';
  } else if (e.code === 'AltLeft' || e.code === 'AltRight') {
    codeStr = 'KEY_LEFT_ALT';
    label = 'Option (Alt)';
  } else if (e.code === 'ControlLeft' || e.code === 'ControlRight') {
    codeStr = 'KEY_LEFT_CTRL';
    label = 'Control (Ctrl)';
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

  capturedLabel.value = label;
  capturedBinding.value = {
    type: 'key',
    code: codeStr,
  };
};

const handleMouseDown = (e: MouseEvent) => {
  const target = e.target as HTMLElement;
  if (target.closest('.modal-actions') || target.closest('.close-btn')) {
    return;
  }

  e.preventDefault();
  let codeStr = 'MOUSE_LEFT';
  let label = 'Primary Left Click';

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

  capturedLabel.value = label;
  capturedBinding.value = {
    type: 'mouse_button',
    code: codeStr,
    threshold: 40,
  };
};

const handleWheel = (e: WheelEvent) => {
  e.preventDefault();
  if (e.deltaY < 0) {
    capturedLabel.value = 'Mouse Scroll Wheel Up';
    capturedBinding.value = {
      type: 'mouse_scroll',
      delta: 1,
      repeat_ms: 120,
    };
  } else if (e.deltaY > 0) {
    capturedLabel.value = 'Mouse Scroll Wheel Down';
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
      <div class="modal-header">
        <div class="modal-title-row">
          <span class="pulsar-dot"></span>
          <h3 class="modal-title">Live Input Capture</h3>
        </div>
        <button class="close-btn" @click="emit('close')">
          <CosmicIcon name="x" size="14" />
        </button>
      </div>

      <p class="modal-desc">
        Mapping input for: <strong class="target-name">{{ controlId.toUpperCase().replace('_', ' ') }}</strong>
      </p>

      <!-- Visual Capture Area -->
      <div class="capture-visual-box">
        <div class="input-display-badge">
          {{ capturedLabel }}
        </div>
        <p class="hint-text">
          Press any keyboard key, click a mouse button, or roll the scroll wheel.
        </p>
      </div>

      <!-- Actions -->
      <div class="modal-actions">
        <button class="btn-glass-secondary" @click="emit('close')">
          Cancel (Esc)
        </button>
        <button
          class="btn-cosmic"
          :disabled="!capturedBinding"
          @click="confirmBinding"
        >
          <CosmicIcon name="check" size="12" />
          <span>Apply Binding</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.capture-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(3, 5, 10, 0.78);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
  animation: fadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.capture-card {
  width: 440px;
  padding: 24px;
  border-radius: 18px;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.modal-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.pulsar-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--accent-cyan);
  box-shadow: 0 0 12px var(--accent-cyan);
  animation: pulseGlow 1.8s infinite;
}

.modal-title {
  font-size: 15px;
  font-weight: 700;
  color: #fff;
}

.close-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.close-btn:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
}

.modal-desc {
  font-size: 12.5px;
  color: var(--text-secondary);
  margin-bottom: 20px;
}

.target-name {
  color: var(--accent-cyan);
  font-family: var(--font-mono);
}

.capture-visual-box {
  position: relative;
  height: 150px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 14px;
  background: rgba(10, 15, 29, 0.75);
  border: 1px dashed rgba(255, 255, 255, 0.2);
  margin-bottom: 20px;
  padding: 16px;
}

.input-display-badge {
  font-family: var(--font-mono);
  font-size: 15px;
  font-weight: 700;
  color: #ffffff;
  background: rgba(56, 189, 248, 0.18);
  border: 1px solid rgba(56, 189, 248, 0.5);
  padding: 10px 20px;
  border-radius: 10px;
  box-shadow: 0 0 24px rgba(56, 189, 248, 0.3);
  margin-bottom: 12px;
  max-width: 90%;
  text-align: center;
}

.hint-text {
  font-size: 11px;
  color: var(--text-muted);
  text-align: center;
}

.modal-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
}

@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.97); }
  to { opacity: 1; transform: scale(1); }
}
</style>
