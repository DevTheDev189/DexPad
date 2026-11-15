<script setup lang="ts">
import { computed } from 'vue';
import type { ControllerControlId, Profile, InputTelemetry } from '../types/keymap';

const props = defineProps<{
  profile: Profile;
  selectedControl: ControllerControlId | null;
  hoveredControl: ControllerControlId | null;
  telemetry?: InputTelemetry | null;
  activeSlot: number;
}>();

const emit = defineEmits<{
  (e: 'select', id: ControllerControlId): void;
  (e: 'hover', id: ControllerControlId | null, pos?: { x: number; y: number }): void;
}>();

// Helper to determine active state from live telemetry
const isHardwareActive = (id: ControllerControlId): boolean => {
  if (!props.telemetry) return false;
  const t = props.telemetry;
  const b = t.buttons;
  const d = t.dpad;

  switch (id) {
    case 'a': return (b & (1 << 0)) !== 0;
    case 'b': return (b & (1 << 1)) !== 0;
    case 'x': return (b & (1 << 2)) !== 0;
    case 'y': return (b & (1 << 3)) !== 0;
    case 'l1': return (b & (1 << 4)) !== 0;
    case 'r1': return (b & (1 << 5)) !== 0;
    case 'l2': return (t.l2 > 80) || ((b & (1 << 6)) !== 0);
    case 'r2': return (t.r2 > 80) || ((b & (1 << 7)) !== 0);
    case 'l3': return (b & (1 << 8)) !== 0;
    case 'r3': return (b & (1 << 9)) !== 0;
    case 'dpad_up': return (d & 1) !== 0;
    case 'dpad_down': return (d & 2) !== 0;
    case 'dpad_left': return (d & 8) !== 0;
    case 'dpad_right': return (d & 4) !== 0;
    case 'left_stick': return Math.abs(t.lx) > 100 || Math.abs(t.ly) > 100;
    case 'right_stick': return Math.abs(t.rx) > 100 || Math.abs(t.ry) > 100;
    default: return false;
  }
};

// Check if a control is highlighted (selected, hovered, or hardware active)
const isControlHighlighted = (id: ControllerControlId): boolean => {
  return props.selectedControl === id || props.hoveredControl === id || isHardwareActive(id);
};

// Resolve badge label for a button
const getBadgeLabel = (id: ControllerControlId): string => {
  if (id === 'left_stick') {
    return props.profile.sticks.left.mode === 'digital_keys' ? 'WASD' : 'Stick';
  }
  if (id === 'right_stick') {
    return props.profile.sticks.right.mode === 'mouse' ? 'Mouse' : 'Stick';
  }
  const btn = props.profile.buttons[id];
  if (!btn || btn.type === 'none') return '';
  if (btn.type === 'key') {
    const c = btn.code || '';
    if (c.startsWith('KEY_')) return c.replace('KEY_', '');
    return c.toUpperCase();
  }
  if (btn.type === 'mouse_button') {
    if (btn.code === 'MOUSE_LEFT') return 'M.Left';
    if (btn.code === 'MOUSE_RIGHT') return 'M.Right';
    if (btn.code === 'MOUSE_MIDDLE') return 'M.Mid';
    return 'Mouse';
  }
  if (btn.type === 'mouse_scroll') {
    return (btn.delta && btn.delta > 0) ? 'Scroll▲' : 'Scroll▼';
  }
  return '';
};

// Coordinates for click / hover events
const handleControlClick = (id: ControllerControlId) => {
  emit('select', id);
};

const handleControlMouseEnter = (id: ControllerControlId, x: number, y: number) => {
  emit('hover', id, { x, y });
};

const handleControlMouseLeave = () => {
  emit('hover', null);
};

// Live stick tilt calculations for SVG rendering
const leftStickOffset = computed(() => {
  if (!props.telemetry) return { x: 0, y: 0 };
  return {
    x: Math.max(-18, Math.min(18, (props.telemetry.lx / 512) * 16)),
    y: Math.max(-18, Math.min(18, (props.telemetry.ly / 512) * 16)),
  };
});

const rightStickOffset = computed(() => {
  if (!props.telemetry) return { x: 0, y: 0 };
  return {
    x: Math.max(-18, Math.min(18, (props.telemetry.rx / 512) * 16)),
    y: Math.max(-18, Math.min(18, (props.telemetry.ry / 512) * 16)),
  };
});
</script>

<template>
  <div class="controller-viewport">
    <svg
      viewBox="0 0 900 560"
      class="controller-svg"
      xmlns="http://www.w3.org/2000/svg"
    >
      <!-- ================================================================== -->
      <!-- LAYER 1: Liquid Plasma Goo (Glow Underlay) -->
      <!-- ================================================================== -->
      <g class="plasma-layer" filter="url(#nebula-goo)">
        <!-- ABXY Plasma Cluster -->
        <circle
          v-if="isControlHighlighted('y')"
          cx="630" cy="218" r="32"
          fill="url(#plasma-violet)"
        />
        <circle
          v-if="isControlHighlighted('x')"
          cx="588" cy="260" r="32"
          fill="url(#plasma-violet)"
        />
        <circle
          v-if="isControlHighlighted('b')"
          cx="672" cy="260" r="32"
          fill="url(#plasma-violet)"
        />
        <circle
          v-if="isControlHighlighted('a')"
          cx="630" cy="302" r="32"
          fill="url(#plasma-cyan)"
        />

        <!-- D-Pad Plasma Cluster -->
        <circle
          v-if="isControlHighlighted('dpad_up')"
          cx="270" cy="222" r="28"
          fill="url(#plasma-cyan)"
        />
        <circle
          v-if="isControlHighlighted('dpad_down')"
          cx="270" cy="298" r="28"
          fill="url(#plasma-cyan)"
        />
        <circle
          v-if="isControlHighlighted('dpad_left')"
          cx="232" cy="260" r="28"
          fill="url(#plasma-cyan)"
        />
        <circle
          v-if="isControlHighlighted('dpad_right')"
          cx="308" cy="260" r="28"
          fill="url(#plasma-cyan)"
        />

        <!-- Left / Right Stick Plasma Orbs -->
        <circle
          v-if="isControlHighlighted('left_stick') || isControlHighlighted('l3')"
          cx="360" cy="375" r="50"
          fill="url(#plasma-cyan)"
        />
        <circle
          v-if="isControlHighlighted('right_stick') || isControlHighlighted('r3')"
          cx="540" cy="375" r="50"
          fill="url(#plasma-violet)"
        />

        <!-- Shoulder / Trigger Glows -->
        <circle
          v-if="isControlHighlighted('l1') || isControlHighlighted('l2')"
          cx="270" cy="95" r="45"
          fill="url(#plasma-cyan)"
        />
        <circle
          v-if="isControlHighlighted('r1') || isControlHighlighted('r2')"
          cx="630" cy="95" r="45"
          fill="url(#plasma-cyan)"
        />
      </g>

      <!-- ================================================================== -->
      <!-- LAYER 2: Frosted Glass Controller Shell & Accents -->
      <!-- ================================================================== -->
      <g class="shell-layer">
        <!-- Controller Drop Shadow -->
        <path
          d="M 230 65 Q 270 50 310 65 L 340 135 Q 450 145 560 135 L 590 65 Q 630 50 670 65 L 725 150 C 785 240 820 370 780 470 C 755 520 705 525 660 480 L 580 425 Q 450 460 320 425 L 240 480 C 195 525 145 520 120 470 C 80 370 115 240 175 150 Z"
          fill="none"
          stroke="rgba(0,0,0,0.6)"
          stroke-width="18"
          filter="blur(16px)"
          opacity="0.8"
        />

        <!-- Main Controller Body -->
        <path
          d="M 230 65 Q 270 50 310 65 L 340 135 Q 450 145 560 135 L 590 65 Q 630 50 670 65 L 725 150 C 785 240 820 370 780 470 C 755 520 705 525 660 480 L 580 425 Q 450 460 320 425 L 240 480 C 195 525 145 520 120 470 C 80 370 115 240 175 150 Z"
          fill="url(#shell-gradient)"
          stroke="url(#shell-stroke)"
          stroke-width="2.5"
          class="shell-body"
        />

        <!-- Ergonomic Palm Grip Textures -->
        <path
          d="M 145 280 C 130 350 140 420 170 460"
          fill="none"
          stroke="rgba(147, 197, 253, 0.12)"
          stroke-width="12"
          stroke-linecap="round"
        />
        <path
          d="M 755 280 C 770 350 760 420 730 460"
          fill="none"
          stroke="rgba(147, 197, 253, 0.12)"
          stroke-width="12"
          stroke-linecap="round"
        />

        <!-- Center Inset Bevel -->
        <path
          d="M 370 190 Q 450 180 530 190 L 565 310 Q 450 340 335 310 Z"
          fill="rgba(10, 15, 30, 0.55)"
          stroke="rgba(147, 197, 253, 0.1)"
          stroke-width="1.5"
        />

        <!-- Nimbus+ 4 Battery / Player Slot LEDs -->
        <g class="slot-leds" transform="translate(0, 0)">
          <circle
            v-for="i in 4"
            :key="i"
            :cx="415 + (i - 1) * 23.3"
            cy="275"
            r="3.5"
            :class="['slot-led', { active: activeSlot === i - 1 }]"
          />
        </g>

        <!-- Brand Text / Logo -->
        <text
          x="450"
          y="180"
          text-anchor="middle"
          class="brand-logo"
        >
          STEELSERIES
        </text>
        <text
          x="450"
          y="298"
          text-anchor="middle"
          class="brand-subtext"
        >
          NIMBUS+
        </text>
      </g>

      <!-- ================================================================== -->
      <!-- LAYER 3: Razor-Sharp Interactive Controls -->
      <!-- ================================================================== -->
      <g class="controls-layer">
        <!-- ---------------------------------------------------------------- -->
        <!-- Triggers L2 / R2 -->
        <!-- ---------------------------------------------------------------- -->
        <g
          class="interactive-control trigger"
          :class="{ selected: selectedControl === 'l2', active: isHardwareActive('l2') }"
          @click="handleControlClick('l2')"
          @mouseenter="handleControlMouseEnter('l2', 270, 75)"
          @mouseleave="handleControlMouseLeave"
        >
          <rect x="230" y="55" width="80" height="36" rx="8" class="control-cap trigger-cap" />
          <text x="270" y="78" text-anchor="middle" class="cap-label">L2</text>
        </g>

        <g
          class="interactive-control trigger"
          :class="{ selected: selectedControl === 'r2', active: isHardwareActive('r2') }"
          @click="handleControlClick('r2')"
          @mouseenter="handleControlMouseEnter('r2', 630, 75)"
          @mouseleave="handleControlMouseLeave"
        >
          <rect x="590" y="55" width="80" height="36" rx="8" class="control-cap trigger-cap" />
          <text x="630" y="78" text-anchor="middle" class="cap-label">R2</text>
        </g>

        <!-- ---------------------------------------------------------------- -->
        <!-- Bumpers L1 / R1 -->
        <!-- ---------------------------------------------------------------- -->
        <g
          class="interactive-control bumper"
          :class="{ selected: selectedControl === 'l1', active: isHardwareActive('l1') }"
          @click="handleControlClick('l1')"
          @mouseenter="handleControlMouseEnter('l1', 270, 115)"
          @mouseleave="handleControlMouseLeave"
        >
          <rect x="225" y="100" width="90" height="28" rx="10" class="control-cap bumper-cap" />
          <text x="270" y="119" text-anchor="middle" class="cap-label">L1</text>
        </g>

        <g
          class="interactive-control bumper"
          :class="{ selected: selectedControl === 'r1', active: isHardwareActive('r1') }"
          @click="handleControlClick('r1')"
          @mouseenter="handleControlMouseEnter('r1', 630, 115)"
          @mouseleave="handleControlMouseLeave"
        >
          <rect x="585" y="100" width="90" height="28" rx="10" class="control-cap bumper-cap" />
          <text x="630" y="119" text-anchor="middle" class="cap-label">R1</text>
        </g>

        <!-- ---------------------------------------------------------------- -->
        <!-- D-Pad Base & Directional Buttons -->
        <!-- ---------------------------------------------------------------- -->
        <g class="dpad-group">
          <!-- Center disc -->
          <circle cx="270" cy="260" r="54" class="dpad-backplate" />

          <!-- D-Pad Up -->
          <g
            class="interactive-control dpad-arm"
            :class="{ selected: selectedControl === 'dpad_up', active: isHardwareActive('dpad_up') }"
            @click="handleControlClick('dpad_up')"
            @mouseenter="handleControlMouseEnter('dpad_up', 270, 222)"
            @mouseleave="handleControlMouseLeave"
          >
            <path d="M 256 242 L 256 215 Q 270 208 284 215 L 284 242 Z" class="control-cap dpad-cap" />
            <polygon points="270,218 264,228 276,228" class="dpad-arrow" />
          </g>

          <!-- D-Pad Down -->
          <g
            class="interactive-control dpad-arm"
            :class="{ selected: selectedControl === 'dpad_down', active: isHardwareActive('dpad_down') }"
            @click="handleControlClick('dpad_down')"
            @mouseenter="handleControlMouseEnter('dpad_down', 270, 298)"
            @mouseleave="handleControlMouseLeave"
          >
            <path d="M 256 278 L 256 305 Q 270 312 284 305 L 284 278 Z" class="control-cap dpad-cap" />
            <polygon points="270,302 264,292 276,292" class="dpad-arrow" />
          </g>

          <!-- D-Pad Left -->
          <g
            class="interactive-control dpad-arm"
            :class="{ selected: selectedControl === 'dpad_left', active: isHardwareActive('dpad_left') }"
            @click="handleControlClick('dpad_left')"
            @mouseenter="handleControlMouseEnter('dpad_left', 232, 260)"
            @mouseleave="handleControlMouseLeave"
          >
            <path d="M 252 246 L 225 246 Q 218 260 225 274 L 252 274 Z" class="control-cap dpad-cap" />
            <polygon points="228,260 238,254 238,266" class="dpad-arrow" />
          </g>

          <!-- D-Pad Right -->
          <g
            class="interactive-control dpad-arm"
            :class="{ selected: selectedControl === 'dpad_right', active: isHardwareActive('dpad_right') }"
            @click="handleControlClick('dpad_right')"
            @mouseenter="handleControlMouseEnter('dpad_right', 308, 260)"
            @mouseleave="handleControlMouseLeave"
          >
            <path d="M 288 246 L 315 246 Q 322 260 315 274 L 288 274 Z" class="control-cap dpad-cap" />
            <polygon points="312,260 302,254 302,266" class="dpad-arrow" />
          </g>
        </g>

        <!-- ---------------------------------------------------------------- -->
        <!-- ABXY Diamond Buttons -->
        <!-- ---------------------------------------------------------------- -->
        <g class="abxy-group">
          <!-- Button Y (Top - Yellow/Amber in classic, Cosmic Violet) -->
          <g
            class="interactive-control abxy-btn"
            :class="{ selected: selectedControl === 'y', active: isHardwareActive('y') }"
            @click="handleControlClick('y')"
            @mouseenter="handleControlMouseEnter('y', 630, 218)"
            @mouseleave="handleControlMouseLeave"
          >
            <circle cx="630" cy="218" r="20" class="control-cap circular-cap btn-y" />
            <text x="630" y="225" text-anchor="middle" class="abxy-letter">Y</text>
          </g>

          <!-- Button X (Left - Blue/Cyan) -->
          <g
            class="interactive-control abxy-btn"
            :class="{ selected: selectedControl === 'x', active: isHardwareActive('x') }"
            @click="handleControlClick('x')"
            @mouseenter="handleControlMouseEnter('x', 588, 260)"
            @mouseleave="handleControlMouseLeave"
          >
            <circle cx="588" cy="260" r="20" class="control-cap circular-cap btn-x" />
            <text x="588" y="267" text-anchor="middle" class="abxy-letter">X</text>
          </g>

          <!-- Button B (Right - Red/Magenta) -->
          <g
            class="interactive-control abxy-btn"
            :class="{ selected: selectedControl === 'b', active: isHardwareActive('b') }"
            @click="handleControlClick('b')"
            @mouseenter="handleControlMouseEnter('b', 672, 260)"
            @mouseleave="handleControlMouseLeave"
          >
            <circle cx="672" cy="260" r="20" class="control-cap circular-cap btn-b" />
            <text x="672" y="267" text-anchor="middle" class="abxy-letter">B</text>
          </g>

          <!-- Button A (Bottom - Green/Emerald) -->
          <g
            class="interactive-control abxy-btn"
            :class="{ selected: selectedControl === 'a', active: isHardwareActive('a') }"
            @click="handleControlClick('a')"
            @mouseenter="handleControlMouseEnter('a', 630, 302)"
            @mouseleave="handleControlMouseLeave"
          >
            <circle cx="630" cy="302" r="20" class="control-cap circular-cap btn-a" />
            <text x="630" y="309" text-anchor="middle" class="abxy-letter">A</text>
          </g>
        </g>

        <!-- ---------------------------------------------------------------- -->
        <!-- Center Cluster: Options, Home, Menu -->
        <!-- ---------------------------------------------------------------- -->
        <!-- Options (Back) -->
        <g
          class="interactive-control small-btn"
          :class="{ selected: selectedControl === 'options', active: isHardwareActive('options') }"
          @click="handleControlClick('options')"
          @mouseenter="handleControlMouseEnter('options', 395, 230)"
          @mouseleave="handleControlMouseLeave"
        >
          <circle cx="395" cy="230" r="13" class="control-cap circular-cap" />
          <path d="M 390 227 L 400 227 M 390 230 L 400 230 M 390 233 L 400 233" stroke="#94a3b8" stroke-width="1.5" stroke-linecap="round" />
        </g>

        <!-- Home / Apple Guide Button -->
        <g
          class="interactive-control home-btn"
          :class="{ selected: selectedControl === 'home', active: isHardwareActive('home') }"
          @click="handleControlClick('home')"
          @mouseenter="handleControlMouseEnter('home', 450, 222)"
          @mouseleave="handleControlMouseLeave"
        >
          <circle cx="450" cy="222" r="19" class="control-cap circular-cap home-cap" />
          <circle cx="450" cy="222" r="12" fill="none" stroke="var(--accent-cyan)" stroke-width="2" class="home-ring" />
          <circle cx="450" cy="222" r="4" fill="var(--accent-cyan)" />
        </g>

        <!-- Menu (Forward) -->
        <g
          class="interactive-control small-btn"
          :class="{ selected: selectedControl === 'menu', active: isHardwareActive('menu') }"
          @click="handleControlClick('menu')"
          @mouseenter="handleControlMouseEnter('menu', 505, 230)"
          @mouseleave="handleControlMouseLeave"
        >
          <circle cx="505" cy="230" r="13" class="control-cap circular-cap" />
          <polygon points="502,224 510,230 502,236" fill="#94a3b8" />
        </g>

        <!-- ---------------------------------------------------------------- -->
        <!-- Analog Thumbsticks (Left Stick / L3 & Right Stick / R3) -->
        <!-- ---------------------------------------------------------------- -->
        <!-- Left Stick -->
        <g
          class="interactive-control thumbstick-group"
          :class="{ selected: selectedControl === 'left_stick' || selectedControl === 'l3', active: isHardwareActive('left_stick') || isHardwareActive('l3') }"
          @click="handleControlClick(selectedControl === 'l3' ? 'left_stick' : 'left_stick')"
          @mouseenter="handleControlMouseEnter('left_stick', 360, 375)"
          @mouseleave="handleControlMouseLeave"
        >
          <!-- Stick Well -->
          <circle cx="360" cy="375" r="48" class="stick-well" />

          <!-- Dynamic tilted stick cap -->
          <g :transform="`translate(${leftStickOffset.x}, ${leftStickOffset.y})`">
            <circle cx="360" cy="375" r="38" class="stick-cap" />
            <circle cx="360" cy="375" r="28" class="stick-ridge" />
            <circle cx="360" cy="375" r="14" class="stick-center-well" />
            <text x="360" y="379" text-anchor="middle" class="stick-label">L3</text>
          </g>
        </g>

        <!-- Right Stick -->
        <g
          class="interactive-control thumbstick-group"
          :class="{ selected: selectedControl === 'right_stick' || selectedControl === 'r3', active: isHardwareActive('right_stick') || isHardwareActive('r3') }"
          @click="handleControlClick(selectedControl === 'r3' ? 'right_stick' : 'right_stick')"
          @mouseenter="handleControlMouseEnter('right_stick', 540, 375)"
          @mouseleave="handleControlMouseLeave"
        >
          <!-- Stick Well -->
          <circle cx="540" cy="375" r="48" class="stick-well" />

          <!-- Dynamic tilted stick cap -->
          <g :transform="`translate(${rightStickOffset.x}, ${rightStickOffset.y})`">
            <circle cx="540" cy="375" r="38" class="stick-cap" />
            <circle cx="540" cy="375" r="28" class="stick-ridge" />
            <circle cx="540" cy="375" r="14" class="stick-center-well" />
            <text x="540" y="379" text-anchor="middle" class="stick-label">R3</text>
          </g>
        </g>

        <!-- ---------------------------------------------------------------- -->
        <!-- Live Keycap Badges (Floating Callouts) -->
        <!-- ---------------------------------------------------------------- -->
        <g class="keycap-badges">
          <!-- A Badge -->
          <g v-if="getBadgeLabel('a')" transform="translate(630, 332)">
            <rect x="-24" y="-9" width="48" height="18" rx="6" class="badge-pill" />
            <text x="0" y="3.5" text-anchor="middle" class="badge-text">{{ getBadgeLabel('a') }}</text>
          </g>

          <!-- B Badge -->
          <g v-if="getBadgeLabel('b')" transform="translate(702, 260)">
            <rect x="-24" y="-9" width="48" height="18" rx="6" class="badge-pill" />
            <text x="0" y="3.5" text-anchor="middle" class="badge-text">{{ getBadgeLabel('b') }}</text>
          </g>

          <!-- X Badge -->
          <g v-if="getBadgeLabel('x')" transform="translate(558, 260)">
            <rect x="-24" y="-9" width="48" height="18" rx="6" class="badge-pill" />
            <text x="0" y="3.5" text-anchor="middle" class="badge-text">{{ getBadgeLabel('x') }}</text>
          </g>

          <!-- Y Badge -->
          <g v-if="getBadgeLabel('y')" transform="translate(630, 188)">
            <rect x="-24" y="-9" width="48" height="18" rx="6" class="badge-pill" />
            <text x="0" y="3.5" text-anchor="middle" class="badge-text">{{ getBadgeLabel('y') }}</text>
          </g>

          <!-- L1 Badge -->
          <g v-if="getBadgeLabel('l1')" transform="translate(195, 114)">
            <rect x="-28" y="-9" width="56" height="18" rx="6" class="badge-pill" />
            <text x="0" y="3.5" text-anchor="middle" class="badge-text">{{ getBadgeLabel('l1') }}</text>
          </g>

          <!-- R1 Badge -->
          <g v-if="getBadgeLabel('r1')" transform="translate(705, 114)">
            <rect x="-28" y="-9" width="56" height="18" rx="6" class="badge-pill" />
            <text x="0" y="3.5" text-anchor="middle" class="badge-text">{{ getBadgeLabel('r1') }}</text>
          </g>

          <!-- Left Stick Mode Badge -->
          <g v-if="getBadgeLabel('left_stick')" transform="translate(360, 435)">
            <rect x="-30" y="-10" width="60" height="20" rx="7" class="badge-pill stick-badge-pill" />
            <text x="0" y="4" text-anchor="middle" class="badge-text">{{ getBadgeLabel('left_stick') }}</text>
          </g>

          <!-- Right Stick Mode Badge -->
          <g v-if="getBadgeLabel('right_stick')" transform="translate(540, 435)">
            <rect x="-30" y="-10" width="60" height="20" rx="7" class="badge-pill stick-badge-pill" />
            <text x="0" y="4" text-anchor="middle" class="badge-text">{{ getBadgeLabel('right_stick') }}</text>
          </g>
        </g>
      </g>
    </svg>
  </div>
</template>

<style scoped>
.controller-viewport {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px;
  position: relative;
  z-index: 2;
}

.controller-svg {
  width: 100%;
  max-width: 820px;
  max-height: 520px;
  height: auto;
  filter: drop-shadow(0 20px 40px rgba(0, 0, 0, 0.7));
  user-select: none;
}

/* Shell */
.shell-body {
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.4));
}

.brand-logo {
  font-family: var(--font-sans);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 3px;
  fill: rgba(147, 197, 253, 0.45);
}

.brand-subtext {
  font-family: var(--font-sans);
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 2px;
  fill: rgba(147, 197, 253, 0.3);
}

/* Slot LEDs */
.slot-led {
  fill: #1e293b;
  stroke: rgba(147, 197, 253, 0.2);
  stroke-width: 1;
  transition: all 0.3s ease;
}

.slot-led.active {
  fill: var(--accent-cyan);
  filter: drop-shadow(0 0 6px var(--accent-cyan));
}

/* Controls */
.interactive-control {
  cursor: pointer;
  transition: transform 0.18s cubic-bezier(0.16, 1, 0.3, 1);
}

.interactive-control:hover .control-cap {
  stroke: var(--accent-cyan);
  filter: drop-shadow(0 0 10px rgba(56, 189, 248, 0.6));
}

.interactive-control.selected .control-cap {
  stroke: #ffffff;
  stroke-width: 2.5;
  filter: drop-shadow(0 0 14px var(--accent-cyan)) drop-shadow(0 0 4px #ffffff);
}

.interactive-control.active .control-cap {
  fill: #38bdf8 !important;
  stroke: #ffffff !important;
  filter: drop-shadow(0 0 18px rgba(56, 189, 248, 0.9));
}

.control-cap {
  fill: #161e2e;
  stroke: rgba(147, 197, 253, 0.25);
  stroke-width: 1.5;
  transition: all 0.2s ease;
}

.trigger-cap, .bumper-cap {
  fill: #151c2b;
}

.cap-label {
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 700;
  fill: #94a3b8;
  pointer-events: none;
}

/* D-Pad */
.dpad-backplate {
  fill: #0c1220;
  stroke: rgba(147, 197, 253, 0.15);
  stroke-width: 1.5;
}

.dpad-cap {
  fill: #182236;
}

.dpad-arrow {
  fill: #94a3b8;
  pointer-events: none;
}

/* ABXY */
.abxy-letter {
  font-family: var(--font-sans);
  font-size: 14px;
  font-weight: 800;
  fill: #f8fafc;
  pointer-events: none;
}

.btn-y { border-color: #facc15; }
.btn-x { border-color: #38bdf8; }
.btn-b { border-color: #f43f5e; }
.btn-a { border-color: #34d399; }

/* Center Buttons */
.home-ring {
  transition: all 0.25s ease;
}

.home-btn:hover .home-ring {
  stroke: #ffffff;
  filter: drop-shadow(0 0 6px var(--accent-cyan));
}

/* Sticks */
.stick-well {
  fill: #090e18;
  stroke: rgba(147, 197, 253, 0.18);
  stroke-width: 2;
}

.stick-cap {
  fill: #1a2233;
  stroke: rgba(147, 197, 253, 0.3);
  stroke-width: 1.5;
}

.stick-ridge {
  fill: none;
  stroke: rgba(147, 197, 253, 0.2);
  stroke-width: 1.5;
  stroke-dasharray: 4 2;
}

.stick-center-well {
  fill: #0f1624;
}

.stick-label {
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 700;
  fill: #64748b;
  pointer-events: none;
}

/* Badges */
.badge-pill {
  fill: rgba(15, 23, 42, 0.85);
  stroke: rgba(56, 189, 248, 0.45);
  stroke-width: 1;
  filter: drop-shadow(0 2px 5px rgba(0, 0, 0, 0.5));
}

.stick-badge-pill {
  stroke: rgba(192, 132, 252, 0.5);
}

.badge-text {
  font-family: var(--font-mono);
  font-size: 8.5px;
  font-weight: 600;
  fill: #e2e8f0;
  pointer-events: none;
}
</style>
