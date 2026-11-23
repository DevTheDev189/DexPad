<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import type { ControllerControlId, ButtonBinding, StickConfig, InputTelemetry } from '../types/keymap';
import type { PlatformLegendMode, ChassisFinish } from '../types/controllers';
import ControllerButtonIcon from './ControllerButtonIcon.vue';

// Base neutral renders
import ps5FrontNeutral from '../assets/ps5/PS5_Front_Neutral.png';
import ps5TopNeutral from '../assets/ps5/PS5_Top_Neutral.png';

// Front highlighted button renders
import ps5Circle from '../assets/ps5/PS5_Circle.png';
import ps5DownDpad from '../assets/ps5/PS5_Down_D-Pad.png';
import ps5LeftDpad from '../assets/ps5/PS5_Left_D-Pad.png';
import ps5LeftThumbstick from '../assets/ps5/PS5_Left_Thumbstick.png';
import ps5Logo from '../assets/ps5/PS5_Logo.png';
import ps5OptionsButton from '../assets/ps5/PS5_Options_Button.png';
import ps5RightDpad from '../assets/ps5/PS5_Right_D-Pad.png';
import ps5RightThumbstick from '../assets/ps5/PS5_Right_ThumbStick.png';
import ps5ShareButton from '../assets/ps5/PS5_Share_Button.png';
import ps5Square from '../assets/ps5/PS5_Square.png';
import ps5Trackpad from '../assets/ps5/PS5_Trackpad.png';
import ps5Triangle from '../assets/ps5/PS5_Triangle.png';
import ps5UpDpad from '../assets/ps5/PS5_Up_D-Pad.png';
import ps5X from '../assets/ps5/PS5_X.png';

// Top highlighted button renders
import ps5L1 from '../assets/ps5/PS5_L1.png';
import ps5L2 from '../assets/ps5/PS5_L2.png';
import ps5R1 from '../assets/ps5/PS5_R1.png';
import ps5R2 from '../assets/ps5/PS5_R2.png';

const props = withDefaults(
  defineProps<{
    selectedControl: ControllerControlId | null;
    buttons: Record<string, ButtonBinding>;
    leftStick?: StickConfig;
    rightStick?: StickConfig;
    telemetry?: InputTelemetry | null;
    platformMode?: PlatformLegendMode;
    chassisFinish?: ChassisFinish;
  }>(),
  {
    platformMode: 'playstation',
    chassisFinish: 'sky_blue',
  }
);

const emit = defineEmits<{
  (e: 'select-control', id: ControllerControlId): void;
  (e: 'update:platformMode', mode: PlatformLegendMode): void;
}>();

const hoveredControl = ref<ControllerControlId | null>(null);
const currentView = ref<'front' | 'top'>('front');

// Preload all high-res renders into browser memory for zero latency switching
onMounted(() => {
  const images = [
    ps5FrontNeutral, ps5TopNeutral,
    ps5Circle, ps5DownDpad, ps5LeftDpad, ps5LeftThumbstick, ps5Logo,
    ps5OptionsButton, ps5RightDpad, ps5RightThumbstick, ps5ShareButton,
    ps5Square, ps5Trackpad, ps5Triangle, ps5UpDpad, ps5X,
    ps5L1, ps5L2, ps5R1, ps5R2,
  ];
  images.forEach((src) => {
    const img = new Image();
    img.src = src;
  });
});

// Auto-switch view when a shoulder/trigger control is selected, or return to front for face controls
watch(
  () => props.selectedControl,
  (newId) => {
    if (!newId) return;
    if (newId === 'l1' || newId === 'l2' || newId === 'r1' || newId === 'r2') {
      currentView.value = 'top';
    } else {
      currentView.value = 'front';
    }
  },
  { immediate: true }
);

// Helper to determine if a button is physically pressed via telemetry bitmask
const isTelemetryPressed = (id: ControllerControlId): boolean => {
  if (!props.telemetry) return false;
  const b = props.telemetry.buttons;
  const d = props.telemetry.dpad;
  switch (id) {
    case 'a': return (b & 0x01) !== 0; // Cross
    case 'b': return (b & 0x02) !== 0; // Circle
    case 'x': return (b & 0x04) !== 0; // Square
    case 'y': return (b & 0x08) !== 0; // Triangle
    case 'l1': return (b & 0x10) !== 0;
    case 'r1': return (b & 0x20) !== 0;
    case 'l3': return (b & 0x40) !== 0;
    case 'r3': return (b & 0x80) !== 0;
    case 'menu': return (b & 0x100) !== 0;
    case 'options': return (b & 0x200) !== 0;
    case 'home': return (b & 0x400) !== 0;
    case 'dpad_up': return d === 1 || d === 2 || d === 8;
    case 'dpad_down': return d === 4 || d === 5 || d === 6;
    case 'dpad_left': return d === 7 || d === 8 || d === 6;
    case 'dpad_right': return d === 2 || d === 3 || d === 4;
    default: return false;
  }
};

// Front Render Map
const frontRenderMap: Record<string, string> = {
  a: ps5X,
  b: ps5Circle,
  x: ps5Square,
  y: ps5Triangle,
  dpad_up: ps5UpDpad,
  dpad_down: ps5DownDpad,
  dpad_left: ps5LeftDpad,
  dpad_right: ps5RightDpad,
  left_stick: ps5LeftThumbstick,
  l3: ps5LeftThumbstick,
  right_stick: ps5RightThumbstick,
  r3: ps5RightThumbstick,
  home: ps5Logo,
  options: ps5ShareButton,
  menu: ps5OptionsButton,
  touchpad: ps5Trackpad,
};

// Top Render Map
const topRenderMap: Record<string, string> = {
  l1: ps5L1,
  l2: ps5L2,
  r1: ps5R1,
  r2: ps5R2,
};

// Compute which control is actively highlighted on the front render
const activeFrontControl = computed<string | null>(() => {
  if (hoveredControl.value && frontRenderMap[hoveredControl.value]) {
    return hoveredControl.value;
  }
  if (props.selectedControl && frontRenderMap[props.selectedControl]) {
    return props.selectedControl;
  }
  if (props.telemetry) {
    const list: ControllerControlId[] = [
      'a', 'b', 'x', 'y',
      'dpad_up', 'dpad_down', 'dpad_left', 'dpad_right',
      'l3', 'r3', 'menu', 'options', 'home',
    ];
    const pressed = list.find((id) => isTelemetryPressed(id));
    if (pressed) return pressed;
  }
  return null;
});

const currentFrontImage = computed(() => {
  if (activeFrontControl.value && frontRenderMap[activeFrontControl.value]) {
    return frontRenderMap[activeFrontControl.value];
  }
  return ps5FrontNeutral;
});

// Compute which control is actively highlighted on the top render
const activeTopControl = computed<string | null>(() => {
  if (hoveredControl.value && topRenderMap[hoveredControl.value]) {
    return hoveredControl.value;
  }
  if (props.selectedControl && topRenderMap[props.selectedControl]) {
    return props.selectedControl;
  }
  if (props.telemetry) {
    if (isTelemetryPressed('l1')) return 'l1';
    if (isTelemetryPressed('r1')) return 'r1';
    if ((props.telemetry.l2 ?? 0) > 30) return 'l2';
    if ((props.telemetry.r2 ?? 0) > 30) return 'r2';
  }
  return null;
});

const currentTopImage = computed(() => {
  if (activeTopControl.value && topRenderMap[activeTopControl.value]) {
    return topRenderMap[activeTopControl.value];
  }
  return ps5TopNeutral;
});

const getControlLabel = (id: ControllerControlId): string => {
  if (id === 'touchpad') return 'Touchpad';
  const p = props.platformMode;
  if (p === 'xbox') {
    switch (id) {
      case 'a': return 'A Button';
      case 'b': return 'B Button';
      case 'x': return 'X Button';
      case 'y': return 'Y Button';
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
      case 'left_stick': return 'Left Analog Stick';
      case 'right_stick': return 'Right Analog Stick';
      default: return String(id).toUpperCase();
    }
  } else if (p === 'nintendo') {
    switch (id) {
      case 'a': return 'A Button';
      case 'b': return 'B Button';
      case 'x': return 'X Button';
      case 'y': return 'Y Button';
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
      case 'left_stick': return 'Left Analog Stick';
      case 'right_stick': return 'Right Analog Stick';
      default: return String(id).toUpperCase();
    }
  } else {
    // playstation
    switch (id) {
      case 'a': return 'Cross (✕)';
      case 'b': return 'Circle (○)';
      case 'x': return 'Square (□)';
      case 'y': return 'Triangle (△)';
      case 'l1': return 'L1 Bumper';
      case 'r1': return 'R1 Bumper';
      case 'l2': return 'L2 Trigger';
      case 'r2': return 'R2 Trigger';
      case 'l3': return 'L3 Stick Click';
      case 'r3': return 'R3 Stick Click';
      case 'options': return 'Share / Create';
      case 'menu': return 'Options';
      case 'home': return 'PS Button';
      case 'dpad_up': return 'D-Pad Up';
      case 'dpad_down': return 'D-Pad Down';
      case 'dpad_left': return 'D-Pad Left';
      case 'dpad_right': return 'D-Pad Right';
      case 'left_stick': return 'Left Analog Stick';
      case 'right_stick': return 'Right Analog Stick';
      default: return String(id).toUpperCase();
    }
  }
};

// When clicked on the controller, just select it to scroll & highlight that row in the table
const handleControlClick = (id: ControllerControlId) => {
  emit('select-control', id);
};
</script>

<template>
  <div class="ps5-showcase-panel glass-panel">
    <!-- Clean Minimalist Header: Two Pills Only -->
    <div class="controller-toolbar">
      <!-- Pill 1: View Switcher (Front View vs Top View) -->
      <div class="view-switcher-pill">
        <button
          class="view-tab"
          :class="{ active: currentView === 'front' }"
          title="Front Controller View"
          @click="currentView = 'front'"
        >
          <span>Front View</span>
        </button>
        <button
          class="view-tab"
          :class="{ active: currentView === 'top' }"
          title="Top View (Triggers & Bumpers)"
          @click="currentView = 'top'"
        >
          <span>Top View</span>
        </button>
      </div>

      <!-- Pill 2: Highlighted / Selected Button Name Pill -->
      <div class="active-callout-pill" :class="{ 'has-selection': hoveredControl || selectedControl }">
        <template v-if="hoveredControl || selectedControl">
          <ControllerButtonIcon
            :control-id="(hoveredControl || selectedControl!) as ControllerControlId"
            :platform-mode="platformMode"
            size="16"
          />
          <span class="callout-name">{{ getControlLabel(hoveredControl || selectedControl!) }}</span>
        </template>
        <template v-else>
          <span class="callout-idle">Hover or click a button</span>
        </template>
      </div>
    </div>

    <!-- PS5 High-Resolution Render Stage -->
    <div class="dualsense-stage">
      <div class="render-stage-wrapper">
        <!-- ================================================================
             FRONT CONTROLLER VIEW
             ================================================================ -->
        <div v-show="currentView === 'front'" class="render-view front-view">
          <img
            :src="currentFrontImage"
            alt="PS5 Controller Front Render"
            class="controller-render-img"
            draggable="false"
          />

          <!-- Invisible Hotspot Overlay (Hit areas only - no bounding box outlines) -->
          <svg
            class="hotspot-overlay-svg"
            viewBox="0 0 794 794"
            xmlns="http://www.w3.org/2000/svg"
          >
            <!-- D-PAD UP -->
            <rect
              x="156" y="228" width="40" height="52" rx="8"
              class="invisible-hotspot"
              @click.stop="handleControlClick('dpad_up')"
              @mouseenter="hoveredControl = 'dpad_up'"
              @mouseleave="hoveredControl = null"
            />

            <!-- D-PAD DOWN -->
            <rect
              x="155" y="296" width="40" height="52" rx="8"
              class="invisible-hotspot"
              @click.stop="handleControlClick('dpad_down')"
              @mouseenter="hoveredControl = 'dpad_down'"
              @mouseleave="hoveredControl = null"
            />

            <!-- D-PAD LEFT -->
            <rect
              x="116" y="268" width="52" height="40" rx="8"
              class="invisible-hotspot"
              @click.stop="handleControlClick('dpad_left')"
              @mouseenter="hoveredControl = 'dpad_left'"
              @mouseleave="hoveredControl = null"
            />

            <!-- D-PAD RIGHT -->
            <rect
              x="183" y="269" width="52" height="40" rx="8"
              class="invisible-hotspot"
              @click.stop="handleControlClick('dpad_right')"
              @mouseenter="hoveredControl = 'dpad_right'"
              @mouseleave="hoveredControl = null"
            />

            <!-- ACTION: TRIANGLE (y) -->
            <circle
              cx="614" cy="237" r="24"
              class="invisible-hotspot"
              @click.stop="handleControlClick('y')"
              @mouseenter="hoveredControl = 'y'"
              @mouseleave="hoveredControl = null"
            />

            <!-- ACTION: CIRCLE (b) -->
            <circle
              cx="665.5" cy="289" r="24"
              class="invisible-hotspot"
              @click.stop="handleControlClick('b')"
              @mouseenter="hoveredControl = 'b'"
              @mouseleave="hoveredControl = null"
            />

            <!-- ACTION: CROSS / X (a) -->
            <circle
              cx="614" cy="340" r="24"
              class="invisible-hotspot"
              @click.stop="handleControlClick('a')"
              @mouseenter="hoveredControl = 'a'"
              @mouseleave="hoveredControl = null"
            />

            <!-- ACTION: SQUARE (x) -->
            <circle
              cx="562" cy="288.5" r="24"
              class="invisible-hotspot"
              @click.stop="handleControlClick('x')"
              @mouseenter="hoveredControl = 'x'"
              @mouseleave="hoveredControl = null"
            />

            <!-- LEFT THUMBSTICK (left_stick / l3) -->
            <circle
              cx="281" cy="385" r="44"
              class="invisible-hotspot"
              @click.stop="handleControlClick('left_stick')"
              @mouseenter="hoveredControl = 'left_stick'"
              @mouseleave="hoveredControl = null"
            />

            <!-- RIGHT THUMBSTICK (right_stick / r3) -->
            <circle
              cx="507.5" cy="385.5" r="44"
              class="invisible-hotspot"
              @click.stop="handleControlClick('right_stick')"
              @mouseenter="hoveredControl = 'right_stick'"
              @mouseleave="hoveredControl = null"
            />

            <!-- SHARE / CREATE (options) -->
            <rect
              x="218" y="193" width="26" height="38" rx="8"
              class="invisible-hotspot"
              @click.stop="handleControlClick('options')"
              @mouseenter="hoveredControl = 'options'"
              @mouseleave="hoveredControl = null"
            />

            <!-- OPTIONS / MENU (menu) -->
            <rect
              x="546" y="193" width="26" height="38" rx="8"
              class="invisible-hotspot"
              @click.stop="handleControlClick('menu')"
              @mouseenter="hoveredControl = 'menu'"
              @mouseleave="hoveredControl = null"
            />

            <!-- PS LOGO / HOME (home) -->
            <rect
              x="372" y="362" width="46" height="36" rx="10"
              class="invisible-hotspot"
              @click.stop="handleControlClick('home')"
              @mouseenter="hoveredControl = 'home'"
              @mouseleave="hoveredControl = null"
            />

            <!-- TOUCHPAD -->
            <polygon
              points="268,162 523,162 536,200 508,310 282,310 256,200"
              class="invisible-hotspot"
              @click.stop="handleControlClick('touchpad')"
              @mouseenter="hoveredControl = 'touchpad'"
              @mouseleave="hoveredControl = null"
            />
          </svg>
        </div>

        <!-- ================================================================
             TOP CONTROLLER VIEW (L1, L2, R1, R2 TRIGGERS & BUMPERS)
             ================================================================ -->
        <div v-show="currentView === 'top'" class="render-view top-view">
          <img
            :src="currentTopImage"
            alt="PS5 Controller Top Render"
            class="controller-render-img"
            draggable="false"
          />

          <!-- Invisible Hotspot Overlay for Top View (Hit areas only - no bounding box outlines) -->
          <svg
            class="hotspot-overlay-svg"
            viewBox="0 0 794 794"
            xmlns="http://www.w3.org/2000/svg"
          >
            <!-- L1 BUMPER -->
            <rect
              x="105" y="395" width="108" height="86" rx="14"
              class="invisible-hotspot"
              @click.stop="handleControlClick('l1')"
              @mouseenter="hoveredControl = 'l1'"
              @mouseleave="hoveredControl = null"
            />

            <!-- L2 TRIGGER -->
            <rect
              x="111" y="299" width="106" height="98" rx="14"
              class="invisible-hotspot"
              @click.stop="handleControlClick('l2')"
              @mouseenter="hoveredControl = 'l2'"
              @mouseleave="hoveredControl = null"
            />

            <!-- R1 BUMPER -->
            <rect
              x="584" y="394" width="108" height="86" rx="14"
              class="invisible-hotspot"
              @click.stop="handleControlClick('r1')"
              @mouseenter="hoveredControl = 'r1'"
              @mouseleave="hoveredControl = null"
            />

            <!-- R2 TRIGGER -->
            <rect
              x="581" y="299" width="106" height="98" rx="14"
              class="invisible-hotspot"
              @click.stop="handleControlClick('r2')"
              @mouseenter="hoveredControl = 'r2'"
              @mouseleave="hoveredControl = null"
            />
          </svg>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ps5-showcase-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  position: relative;
  background-color: var(--glass-surface);
  background-image: linear-gradient(
    135deg,
    rgba(var(--accent-custom-rgb, 125, 211, 252), calc(var(--glass-tint-val, 0.14) * 0.40)) 0%,
    rgba(var(--accent-custom-rgb, 125, 211, 252), calc(var(--glass-tint-val, 0.14) * 0.08)) 40%,
    transparent 85%
  );
  backdrop-filter: blur(var(--glass-blur-val, 28px)) saturate(190%);
  -webkit-backdrop-filter: blur(var(--glass-blur-val, 28px)) saturate(190%);
  border: 1px solid var(--glass-border);
  border-radius: 24px;
  overflow: hidden;
  box-shadow: none;
}

/* Minimalist Top Toolbar with Exactly Two Pills */
.controller-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px 10px 20px;
  gap: 12px;
  z-index: 5;
}

/* Pill 1: View Switcher */
.view-switcher-pill {
  display: flex;
  align-items: center;
  background: var(--glass-surface-pill);
  border: 1px solid var(--glass-border-subtle);
  border-radius: 12px;
  padding: 3px;
  gap: 3px;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}

.view-tab {
  padding: 6px 14px;
  border-radius: 9px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-family: var(--font-sans);
  font-size: 11.5px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.view-tab:hover {
  color: var(--text-primary);
  background: var(--btn-bg);
}

.view-tab.active {
  background: var(--glass-surface-elevated);
  border: 1px solid var(--accent-custom);
  color: var(--accent-custom);
  box-shadow: 0 2px 8px rgba(var(--accent-custom-rgb, 125, 211, 252), 0.25);
  font-weight: 700;
}

/* Pill 2: Highlighted Button Name Pill */
.active-callout-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 12px;
  background-color: var(--glass-surface-pill);
  background-image: linear-gradient(
    135deg,
    rgba(var(--accent-custom-rgb, 125, 211, 252), calc(var(--glass-tint-val, 0.14) * 0.35)) 0%,
    transparent 80%
  );
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid var(--glass-border-subtle);
  min-height: 36px;
  transition: all 0.25s ease;
}

.active-callout-pill.has-selection {
  border-color: var(--glass-border);
  box-shadow: 0 2px 10px rgba(var(--accent-custom-rgb, 125, 211, 252), 0.15);
}

.callout-name {
  font-weight: 700;
  color: var(--text-primary);
  font-size: 12.5px;
  letter-spacing: 0.01em;
}

.callout-idle {
  color: var(--text-muted);
  font-size: 11.5px;
}

/* DualSense Render Stage */
.dualsense-stage {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  padding: 16px 24px;
  overflow: hidden;
}

.render-stage-wrapper {
  position: relative;
  width: 100%;
  max-width: 620px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.render-view {
  position: relative;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.controller-render-img {
  width: 100%;
  height: auto;
  max-height: 480px;
  object-fit: contain;
  user-select: none;
  filter: drop-shadow(0 20px 28px rgba(0, 0, 0, 0.40));
  transition: filter 0.2s ease;
}

/* Invisible Hotspot Overlay SVG */
.hotspot-overlay-svg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.invisible-hotspot {
  fill: transparent;
  stroke: none;
  cursor: pointer;
  pointer-events: auto;
}
</style>
