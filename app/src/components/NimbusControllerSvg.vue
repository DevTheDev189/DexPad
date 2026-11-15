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

const isControlHighlighted = (id: ControllerControlId): boolean => {
  return props.selectedControl === id || props.hoveredControl === id || isHardwareActive(id);
};

// Clean human-friendly badge label
const getBadgeLabel = (id: ControllerControlId): string => {
  if (id === 'left_stick') {
    return props.profile.sticks.left.mode === 'digital_keys' ? 'WASD' : (props.profile.sticks.left.mode === 'mouse' ? 'Mouse' : 'Off');
  }
  if (id === 'right_stick') {
    return props.profile.sticks.right.mode === 'mouse' ? 'Mouse' : (props.profile.sticks.right.mode === 'digital_keys' ? 'Keys' : 'Off');
  }
  const btn = props.profile.buttons[id];
  if (!btn || btn.type === 'none') return '';
  if (btn.type === 'key') {
    const c = btn.code || '';
    if (c === 'KEY_SPACE') return 'Space';
    if (c === 'KEY_RETURN') return 'Enter';
    if (c === 'KEY_ESC') return 'Esc';
    if (c === 'KEY_TAB') return 'Tab';
    if (c === 'KEY_LEFT_SHIFT' || c === 'KEY_RIGHT_SHIFT') return 'Shift';
    if (c === 'KEY_LEFT_CTRL' || c === 'KEY_RIGHT_CTRL') return 'Ctrl';
    if (c === 'KEY_LEFT_ALT' || c === 'KEY_RIGHT_ALT') return 'Opt';
    if (c === 'KEY_LEFT_GUI' || c === 'KEY_RIGHT_GUI') return 'Cmd';
    if (c.startsWith('KEY_')) return c.replace('KEY_', '');
    return c.toUpperCase();
  }
  if (btn.type === 'mouse_button') {
    if (btn.code === 'MOUSE_LEFT') return 'Left Click';
    if (btn.code === 'MOUSE_RIGHT') return 'Right Click';
    if (btn.code === 'MOUSE_MIDDLE') return 'Mid Click';
    return 'Mouse';
  }
  if (btn.type === 'mouse_scroll') {
    return (btn.delta && btn.delta > 0) ? 'Scroll Up' : 'Scroll Down';
  }
  return '';
};

const handleControlClick = (id: ControllerControlId) => {
  emit('select', id);
};

const handleControlMouseEnter = (id: ControllerControlId, x: number, y: number) => {
  emit('hover', id, { x, y });
};

const handleControlMouseLeave = () => {
  emit('hover', null);
};

// Dynamic stick tilt offsets from telemetry
const leftStickOffset = computed(() => {
  if (!props.telemetry) return { x: 0, y: 0 };
  return {
    x: Math.max(-16, Math.min(16, (props.telemetry.lx / 512) * 14)),
    y: Math.max(-16, Math.min(16, (props.telemetry.ly / 512) * 14)),
  };
});

const rightStickOffset = computed(() => {
  if (!props.telemetry) return { x: 0, y: 0 };
  return {
    x: Math.max(-16, Math.min(16, (props.telemetry.rx / 512) * 14)),
    y: Math.max(-16, Math.min(16, (props.telemetry.ry / 512) * 14)),
  };
});
</script>

<template>
  <div class="controller-viewport">
    <svg
      viewBox="0 0 980 600"
      class="controller-svg"
      xmlns="http://www.w3.org/2000/svg"
    >
      <!-- ================================================================== -->
      <!-- LAYER 1: Liquid Plasma Goo (Glow Underlay) -->
      <!-- ================================================================== -->
      <g class="plasma-layer" filter="url(#nebula-goo)">
        <!-- ABXY Plasma Cluster -->
        <circle v-if="isControlHighlighted('y')" cx="640" cy="225" r="36" fill="url(#plasma-violet)" />
        <circle v-if="isControlHighlighted('x')" cx="595" cy="270" r="36" fill="url(#plasma-violet)" />
        <circle v-if="isControlHighlighted('b')" cx="685" cy="270" r="36" fill="url(#plasma-violet)" />
        <circle v-if="isControlHighlighted('a')" cx="640" cy="315" r="36" fill="url(#plasma-cyan)" />

        <!-- D-Pad Plasma Cluster -->
        <circle v-if="isControlHighlighted('dpad_up')" cx="270" cy="230" r="30" fill="url(#plasma-cyan)" />
        <circle v-if="isControlHighlighted('dpad_down')" cx="270" cy="310" r="30" fill="url(#plasma-cyan)" />
        <circle v-if="isControlHighlighted('dpad_left')" cx="230" cy="270" r="30" fill="url(#plasma-cyan)" />
        <circle v-if="isControlHighlighted('dpad_right')" cx="310" cy="270" r="30" fill="url(#plasma-cyan)" />

        <!-- Sticks Plasma -->
        <circle v-if="isControlHighlighted('left_stick') || isControlHighlighted('l3')" cx="365" cy="390" r="55" fill="url(#plasma-cyan)" />
        <circle v-if="isControlHighlighted('right_stick') || isControlHighlighted('r3')" cx="545" cy="390" r="55" fill="url(#plasma-violet)" />

        <!-- Bumpers & Triggers Plasma -->
        <circle v-if="isControlHighlighted('l1') || isControlHighlighted('l2')" cx="270" cy="115" r="50" fill="url(#plasma-cyan)" />
        <circle v-if="isControlHighlighted('r1') || isControlHighlighted('r2')" cx="640" cy="115" r="50" fill="url(#plasma-cyan)" />
      </g>

      <!-- ================================================================== -->
      <!-- LAYER 2: Frosted Obsidian Glass Controller Body -->
      <!-- ================================================================== -->
      <g class="shell-layer">
        <!-- Deep Ambient Drop Shadow -->
        <path
          d="M 230 75 Q 270 60 310 75 L 340 145 Q 455 155 570 145 L 600 75 Q 640 60 680 75 L 740 160 C 805 250 840 380 800 480 C 775 530 720 535 675 490 L 590 435 Q 455 470 320 435 L 235 490 C 190 535 135 530 110 480 C 70 380 105 250 170 160 Z"
          fill="none"
          stroke="rgba(0, 0, 0, 0.75)"
          stroke-width="24"
          filter="blur(20px)"
          opacity="0.9"
        />

        <!-- Translucent Controller Shell with Specular Bevel -->
        <path
          d="M 230 75 Q 270 60 310 75 L 340 145 Q 455 155 570 145 L 600 75 Q 640 60 680 75 L 740 160 C 805 250 840 380 800 480 C 775 530 720 535 675 490 L 590 435 Q 455 470 320 435 L 235 490 C 190 535 135 530 110 480 C 70 380 105 250 170 160 Z"
          fill="url(#shell-gradient)"
          stroke="url(#shell-stroke)"
          stroke-width="2"
          class="shell-body"
        />

        <!-- Inner Bevel Highlights -->
        <path
          d="M 235 85 Q 270 72 305 85 L 335 150 Q 455 160 575 150 L 605 85 Q 640 72 675 85"
          fill="none"
          stroke="rgba(255, 255, 255, 0.2)"
          stroke-width="1.5"
          stroke-linecap="round"
        />

        <!-- Ergonomic Palm Grip Ridges -->
        <path
          d="M 140 290 C 125 360 135 430 165 470"
          fill="none"
          stroke="rgba(147, 197, 253, 0.14)"
          stroke-width="14"
          stroke-linecap="round"
        />
        <path
          d="M 770 290 C 785 360 775 430 745 470"
          fill="none"
          stroke="rgba(147, 197, 253, 0.14)"
          stroke-width="14"
          stroke-linecap="round"
        />

        <!-- Center Inset Plate -->
        <path
          d="M 370 200 Q 455 190 540 200 L 575 320 Q 455 350 335 320 Z"
          fill="rgba(8, 12, 26, 0.65)"
          stroke="rgba(147, 197, 253, 0.15)"
          stroke-width="1.5"
        />

        <!-- 4 Nimbus Player / Slot LEDs -->
        <g class="slot-leds">
          <circle
            v-for="i in 4"
            :key="i"
            :cx="420 + (i - 1) * 23.3"
            cy="285"
            r="3.5"
            :class="['slot-led', { active: activeSlot === i - 1 }]"
          />
        </g>

        <!-- Brand Typography -->
        <text x="455" y="190" text-anchor="middle" class="brand-logo">STEELSERIES</text>
        <text x="455" y="308" text-anchor="middle" class="brand-subtext">NIMBUS+</text>
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
          @mouseenter="handleControlMouseEnter('l2', 270, 85)"
          @mouseleave="handleControlMouseLeave"
        >
          <rect x="230" y="65" width="80" height="38" rx="8" class="control-cap trigger-cap" />
          <text x="270" y="89" text-anchor="middle" class="cap-label">L2</text>
        </g>

        <g
          class="interactive-control trigger"
          :class="{ selected: selectedControl === 'r2', active: isHardwareActive('r2') }"
          @click="handleControlClick('r2')"
          @mouseenter="handleControlMouseEnter('r2', 640, 85)"
          @mouseleave="handleControlMouseLeave"
        >
          <rect x="600" y="65" width="80" height="38" rx="8" class="control-cap trigger-cap" />
          <text x="640" y="89" text-anchor="middle" class="cap-label">R2</text>
        </g>

        <!-- ---------------------------------------------------------------- -->
        <!-- Bumpers L1 / R1 -->
        <!-- ---------------------------------------------------------------- -->
        <g
          class="interactive-control bumper"
          :class="{ selected: selectedControl === 'l1', active: isHardwareActive('l1') }"
          @click="handleControlClick('l1')"
          @mouseenter="handleControlMouseEnter('l1', 270, 125)"
          @mouseleave="handleControlMouseLeave"
        >
          <rect x="225" y="112" width="90" height="28" rx="10" class="control-cap bumper-cap" />
          <text x="270" y="131" text-anchor="middle" class="cap-label">L1</text>
        </g>

        <g
          class="interactive-control bumper"
          :class="{ selected: selectedControl === 'r1', active: isHardwareActive('r1') }"
          @click="handleControlClick('r1')"
          @mouseenter="handleControlMouseEnter('r1', 640, 125)"
          @mouseleave="handleControlMouseLeave"
        >
          <rect x="595" y="112" width="90" height="28" rx="10" class="control-cap bumper-cap" />
          <text x="640" y="131" text-anchor="middle" class="cap-label">R1</text>
        </g>

        <!-- ---------------------------------------------------------------- -->
        <!-- D-Pad Base & Directional Buttons -->
        <!-- ---------------------------------------------------------------- -->
        <g class="dpad-group">
          <circle cx="270" cy="270" r="54" class="dpad-backplate" />

          <!-- D-Pad Up -->
          <g
            class="interactive-control dpad-arm"
            :class="{ selected: selectedControl === 'dpad_up', active: isHardwareActive('dpad_up') }"
            @click="handleControlClick('dpad_up')"
            @mouseenter="handleControlMouseEnter('dpad_up', 270, 230)"
            @mouseleave="handleControlMouseLeave"
          >
            <path d="M 256 252 L 256 225 Q 270 218 284 225 L 284 252 Z" class="control-cap dpad-cap" />
            <polygon points="270,228 264,238 276,238" class="dpad-arrow" />
          </g>

          <!-- D-Pad Down -->
          <g
            class="interactive-control dpad-arm"
            :class="{ selected: selectedControl === 'dpad_down', active: isHardwareActive('dpad_down') }"
            @click="handleControlClick('dpad_down')"
            @mouseenter="handleControlMouseEnter('dpad_down', 270, 310)"
            @mouseleave="handleControlMouseLeave"
          >
            <path d="M 256 288 L 256 315 Q 270 322 284 315 L 284 288 Z" class="control-cap dpad-cap" />
            <polygon points="270,312 264,302 276,302" class="dpad-arrow" />
          </g>

          <!-- D-Pad Left -->
          <g
            class="interactive-control dpad-arm"
            :class="{ selected: selectedControl === 'dpad_left', active: isHardwareActive('dpad_left') }"
            @click="handleControlClick('dpad_left')"
            @mouseenter="handleControlMouseEnter('dpad_left', 230, 270)"
            @mouseleave="handleControlMouseLeave"
          >
            <path d="M 252 256 L 225 256 Q 218 270 225 284 L 252 284 Z" class="control-cap dpad-cap" />
            <polygon points="228,270 238,264 238,276" class="dpad-arrow" />
          </g>

          <!-- D-Pad Right -->
          <g
            class="interactive-control dpad-arm"
            :class="{ selected: selectedControl === 'dpad_right', active: isHardwareActive('dpad_right') }"
            @click="handleControlClick('dpad_right')"
            @mouseenter="handleControlMouseEnter('dpad_right', 310, 270)"
            @mouseleave="handleControlMouseLeave"
          >
            <path d="M 288 256 L 315 256 Q 322 270 315 284 L 288 284 Z" class="control-cap dpad-cap" />
            <polygon points="312,270 302,264 302,276" class="dpad-arrow" />
          </g>
        </g>

        <!-- ---------------------------------------------------------------- -->
        <!-- ABXY Diamond Buttons -->
        <!-- ---------------------------------------------------------------- -->
        <g class="abxy-group">
          <!-- Button Y (Top) -->
          <g
            class="interactive-control abxy-btn"
            :class="{ selected: selectedControl === 'y', active: isHardwareActive('y') }"
            @click="handleControlClick('y')"
            @mouseenter="handleControlMouseEnter('y', 640, 225)"
            @mouseleave="handleControlMouseLeave"
          >
            <circle cx="640" cy="225" r="21" class="control-cap circular-cap btn-y" />
            <text x="640" y="232" text-anchor="middle" class="abxy-letter">Y</text>
          </g>

          <!-- Button X (Left) -->
          <g
            class="interactive-control abxy-btn"
            :class="{ selected: selectedControl === 'x', active: isHardwareActive('x') }"
            @click="handleControlClick('x')"
            @mouseenter="handleControlMouseEnter('x', 595, 270)"
            @mouseleave="handleControlMouseLeave"
          >
            <circle cx="595" cy="270" r="21" class="control-cap circular-cap btn-x" />
            <text x="595" y="277" text-anchor="middle" class="abxy-letter">X</text>
          </g>

          <!-- Button B (Right) -->
          <g
            class="interactive-control abxy-btn"
            :class="{ selected: selectedControl === 'b', active: isHardwareActive('b') }"
            @click="handleControlClick('b')"
            @mouseenter="handleControlMouseEnter('b', 685, 270)"
            @mouseleave="handleControlMouseLeave"
          >
            <circle cx="685" cy="270" r="21" class="control-cap circular-cap btn-b" />
            <text x="685" y="277" text-anchor="middle" class="abxy-letter">B</text>
          </g>

          <!-- Button A (Bottom) -->
          <g
            class="interactive-control abxy-btn"
            :class="{ selected: selectedControl === 'a', active: isHardwareActive('a') }"
            @click="handleControlClick('a')"
            @mouseenter="handleControlMouseEnter('a', 640, 315)"
            @mouseleave="handleControlMouseLeave"
          >
            <circle cx="640" cy="315" r="21" class="control-cap circular-cap btn-a" />
            <text x="640" y="322" text-anchor="middle" class="abxy-letter">A</text>
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
          @mouseenter="handleControlMouseEnter('options', 400, 240)"
          @mouseleave="handleControlMouseLeave"
        >
          <circle cx="400" cy="240" r="14" class="control-cap circular-cap" />
          <path d="M 395 237 L 405 237 M 395 240 L 405 240 M 395 243 L 405 243" stroke="#cbd5e1" stroke-width="1.5" stroke-linecap="round" />
        </g>

        <!-- Home Button -->
        <g
          class="interactive-control home-btn"
          :class="{ selected: selectedControl === 'home', active: isHardwareActive('home') }"
          @click="handleControlClick('home')"
          @mouseenter="handleControlMouseEnter('home', 455, 230)"
          @mouseleave="handleControlMouseLeave"
        >
          <circle cx="455" cy="230" r="20" class="control-cap circular-cap home-cap" />
          <circle cx="455" cy="230" r="13" fill="none" stroke="var(--accent-cyan)" stroke-width="2.5" class="home-ring" />
          <circle cx="455" cy="230" r="4.5" fill="var(--accent-cyan)" />
        </g>

        <!-- Menu (Forward) -->
        <g
          class="interactive-control small-btn"
          :class="{ selected: selectedControl === 'menu', active: isHardwareActive('menu') }"
          @click="handleControlClick('menu')"
          @mouseenter="handleControlMouseEnter('menu', 510, 240)"
          @mouseleave="handleControlMouseLeave"
        >
          <circle cx="510" cy="240" r="14" class="control-cap circular-cap" />
          <polygon points="507,234 515,240 507,246" fill="#cbd5e1" />
        </g>

        <!-- ---------------------------------------------------------------- -->
        <!-- Analog Thumbsticks (Left Stick / L3 & Right Stick / R3) -->
        <!-- ---------------------------------------------------------------- -->
        <!-- Left Stick -->
        <g
          class="interactive-control thumbstick-group"
          :class="{ selected: selectedControl === 'left_stick' || selectedControl === 'l3', active: isHardwareActive('left_stick') || isHardwareActive('l3') }"
          @click="handleControlClick('left_stick')"
          @mouseenter="handleControlMouseEnter('left_stick', 365, 390)"
          @mouseleave="handleControlMouseLeave"
        >
          <circle cx="365" cy="390" r="50" class="stick-well" />
          <g :transform="`translate(${leftStickOffset.x}, ${leftStickOffset.y})`">
            <circle cx="365" cy="390" r="39" class="stick-cap" />
            <circle cx="365" cy="390" r="29" class="stick-ridge" />
            <circle cx="365" cy="390" r="15" class="stick-center-well" />
            <text x="365" y="394" text-anchor="middle" class="stick-label">L3</text>
          </g>
        </g>

        <!-- Right Stick -->
        <g
          class="interactive-control thumbstick-group"
          :class="{ selected: selectedControl === 'right_stick' || selectedControl === 'r3', active: isHardwareActive('right_stick') || isHardwareActive('r3') }"
          @click="handleControlClick('right_stick')"
          @mouseenter="handleControlMouseEnter('right_stick', 545, 390)"
          @mouseleave="handleControlMouseLeave"
        >
          <circle cx="545" cy="390" r="50" class="stick-well" />
          <g :transform="`translate(${rightStickOffset.x}, ${rightStickOffset.y})`">
            <circle cx="545" cy="390" r="39" class="stick-cap" />
            <circle cx="545" cy="390" r="29" class="stick-ridge" />
            <circle cx="545" cy="390" r="15" class="stick-center-well" />
            <text x="545" y="394" text-anchor="middle" class="stick-label">R3</text>
          </g>
        </g>

        <!-- ================================================================ -->
        <!-- CLEAN FLOATING CALLOUT BADGES (No Collisions!) -->
        <!-- ================================================================ -->
        <g class="callout-badges">
          <!-- Button Y (Top Callout) -->
          <g v-if="getBadgeLabel('y')" class="callout-chip" transform="translate(640, 172)">
            <line x1="0" y1="12" x2="0" y2="30" class="callout-line" />
            <rect x="-34" y="-10" width="68" height="20" rx="6" class="chip-bg" />
            <text x="0" y="4" text-anchor="middle" class="chip-text">{{ getBadgeLabel('y') }}</text>
          </g>

          <!-- Button B (Right Callout) -->
          <g v-if="getBadgeLabel('b')" class="callout-chip" transform="translate(748, 270)">
            <line x1="-32" y1="0" x2="-40" y2="0" class="callout-line" />
            <rect x="-32" y="-10" width="64" height="20" rx="6" class="chip-bg" />
            <text x="0" y="4" text-anchor="middle" class="chip-text">{{ getBadgeLabel('b') }}</text>
          </g>

          <!-- Button A (Bottom Callout) -->
          <g v-if="getBadgeLabel('a')" class="callout-chip" transform="translate(640, 362)">
            <line x1="0" y1="-12" x2="0" y2="-25" class="callout-line" />
            <rect x="-34" y="-10" width="68" height="20" rx="6" class="chip-bg" />
            <text x="0" y="4" text-anchor="middle" class="chip-text">{{ getBadgeLabel('a') }}</text>
          </g>

          <!-- Button X (Left Callout) -->
          <g v-if="getBadgeLabel('x')" class="callout-chip" transform="translate(532, 270)">
            <line x1="32" y1="0" x2="40" y2="0" class="callout-line" />
            <rect x="-32" y="-10" width="64" height="20" rx="6" class="chip-bg" />
            <text x="0" y="4" text-anchor="middle" class="chip-text">{{ getBadgeLabel('x') }}</text>
          </g>

          <!-- Bumpers L1 / R1 Callouts -->
          <g v-if="getBadgeLabel('l1')" class="callout-chip" transform="translate(155, 126)">
            <line x1="34" y1="0" x2="68" y2="0" class="callout-line" />
            <rect x="-34" y="-10" width="68" height="20" rx="6" class="chip-bg" />
            <text x="0" y="4" text-anchor="middle" class="chip-text">{{ getBadgeLabel('l1') }}</text>
          </g>
          <g v-if="getBadgeLabel('r1')" class="callout-chip" transform="translate(755, 126)">
            <line x1="-34" y1="0" x2="-68" y2="0" class="callout-line" />
            <rect x="-34" y="-10" width="68" height="20" rx="6" class="chip-bg" />
            <text x="0" y="4" text-anchor="middle" class="chip-text">{{ getBadgeLabel('r1') }}</text>
          </g>

          <!-- Triggers L2 / R2 Callouts -->
          <g v-if="getBadgeLabel('l2')" class="callout-chip" transform="translate(160, 84)">
            <line x1="34" y1="0" x2="68" y2="0" class="callout-line" />
            <rect x="-34" y="-10" width="68" height="20" rx="6" class="chip-bg" />
            <text x="0" y="4" text-anchor="middle" class="chip-text">{{ getBadgeLabel('l2') }}</text>
          </g>
          <g v-if="getBadgeLabel('r2')" class="callout-chip" transform="translate(750, 84)">
            <line x1="-34" y1="0" x2="-68" y2="0" class="callout-line" />
            <rect x="-34" y="-10" width="68" height="20" rx="6" class="chip-bg" />
            <text x="0" y="4" text-anchor="middle" class="chip-text">{{ getBadgeLabel('r2') }}</text>
          </g>

          <!-- Stick Mode Callouts (Directly below stick assemblies) -->
          <g v-if="getBadgeLabel('left_stick')" class="callout-chip" transform="translate(365, 456)">
            <rect x="-32" y="-10" width="64" height="20" rx="6" class="chip-bg stick-chip" />
            <text x="0" y="4" text-anchor="middle" class="chip-text">{{ getBadgeLabel('left_stick') }}</text>
          </g>
          <g v-if="getBadgeLabel('right_stick')" class="callout-chip" transform="translate(545, 456)">
            <rect x="-32" y="-10" width="64" height="20" rx="6" class="chip-bg stick-chip" />
            <text x="0" y="4" text-anchor="middle" class="chip-text">{{ getBadgeLabel('right_stick') }}</text>
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
  padding: 10px;
  position: relative;
  z-index: 2;
}

.controller-svg {
  width: 100%;
  max-width: 860px;
  max-height: 540px;
  height: auto;
  filter: drop-shadow(0 25px 45px rgba(0, 0, 0, 0.75));
  user-select: none;
}

/* Shell */
.shell-body {
  filter: drop-shadow(0 6px 16px rgba(0, 0, 0, 0.5));
}

.brand-logo {
  font-family: var(--font-sans);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 3.5px;
  fill: rgba(255, 255, 255, 0.35);
}

.brand-subtext {
  font-family: var(--font-sans);
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 2px;
  fill: rgba(147, 197, 253, 0.35);
}

/* Slot LEDs */
.slot-led {
  fill: #1e293b;
  stroke: rgba(255, 255, 255, 0.15);
  stroke-width: 1;
  transition: all 0.3s ease;
}

.slot-led.active {
  fill: var(--accent-cyan);
  filter: drop-shadow(0 0 8px var(--accent-cyan));
}

/* Interactive Controls */
.interactive-control {
  cursor: pointer;
  transition: transform 0.18s cubic-bezier(0.16, 1, 0.3, 1);
}

.interactive-control:hover .control-cap {
  stroke: var(--accent-cyan);
  filter: drop-shadow(0 0 12px rgba(56, 189, 248, 0.65));
}

.interactive-control.selected .control-cap {
  stroke: #ffffff;
  stroke-width: 2.5;
  filter: drop-shadow(0 0 16px var(--accent-cyan)) drop-shadow(0 0 6px #ffffff);
}

.interactive-control.active .control-cap {
  fill: #38bdf8 !important;
  stroke: #ffffff !important;
  filter: drop-shadow(0 0 20px rgba(56, 189, 248, 0.95));
}

.control-cap {
  fill: rgba(18, 26, 46, 0.92);
  stroke: rgba(255, 255, 255, 0.18);
  stroke-width: 1.5;
  transition: all 0.2s ease;
}

.trigger-cap, .bumper-cap {
  fill: rgba(15, 22, 38, 0.95);
}

.cap-label {
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 700;
  fill: var(--text-secondary);
  pointer-events: none;
}

/* D-Pad */
.dpad-backplate {
  fill: rgba(8, 12, 24, 0.9);
  stroke: rgba(255, 255, 255, 0.14);
  stroke-width: 1.5;
}

.dpad-cap {
  fill: rgba(20, 28, 48, 0.95);
}

.dpad-arrow {
  fill: var(--text-secondary);
  pointer-events: none;
}

/* ABXY */
.abxy-letter {
  font-family: var(--font-sans);
  font-size: 14px;
  font-weight: 800;
  fill: #ffffff;
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
  filter: drop-shadow(0 0 8px var(--accent-cyan));
}

/* Sticks */
.stick-well {
  fill: rgba(6, 10, 20, 0.95);
  stroke: rgba(255, 255, 255, 0.16);
  stroke-width: 2;
}

.stick-cap {
  fill: rgba(22, 30, 52, 0.95);
  stroke: rgba(255, 255, 255, 0.22);
  stroke-width: 1.5;
}

.stick-ridge {
  fill: none;
  stroke: rgba(255, 255, 255, 0.16);
  stroke-width: 1.5;
  stroke-dasharray: 4 2;
}

.stick-center-well {
  fill: rgba(10, 16, 30, 0.95);
}

.stick-label {
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 700;
  fill: var(--text-muted);
  pointer-events: none;
}

/* Callout Chips */
.callout-line {
  stroke: rgba(56, 189, 248, 0.4);
  stroke-width: 1;
  stroke-dasharray: 2 2;
}

.chip-bg {
  fill: rgba(12, 18, 36, 0.88);
  stroke: rgba(56, 189, 248, 0.45);
  stroke-width: 1;
  filter: drop-shadow(0 4px 10px rgba(0, 0, 0, 0.5));
}

.stick-chip {
  stroke: rgba(192, 132, 252, 0.5);
}

.chip-text {
  font-family: var(--font-mono);
  font-size: 9.5px;
  font-weight: 700;
  fill: #f8fafc;
  pointer-events: none;
}
</style>
