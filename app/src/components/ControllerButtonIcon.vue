<script setup lang="ts">
import { computed } from 'vue';
import type { ControllerControlId } from '../types/keymap';
import type { PlatformLegendMode } from '../types/controllers';

const props = withDefaults(
  defineProps<{
    controlId: ControllerControlId | 'dpad';
    platformMode?: PlatformLegendMode;
    size?: number | string;
  }>(),
  {
    platformMode: 'playstation',
    size: 20,
  }
);

const isXbox = computed(() => props.platformMode === 'xbox');
const isNintendo = computed(() => props.platformMode === 'nintendo');

// Normalized control ID
const id = computed(() => props.controlId);
</script>

<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    class="controller-button-icon"
  >
    <!-- ========================================================================
         FACE BUTTON: A / CROSS
         ======================================================================== -->
    <template v-if="id === 'a'">
      <circle cx="12" cy="12" r="10" class="btn-base-circle" />
      <!-- Xbox: Green A -->
      <template v-if="isXbox">
        <text x="12" y="16.2" text-anchor="middle" font-size="12" font-weight="900" fill="#22c55e" font-family="var(--font-sans, sans-serif)">A</text>
      </template>
      <!-- Nintendo: Red/Bright A -->
      <template v-else-if="isNintendo">
        <text x="12" y="16.2" text-anchor="middle" font-size="12" font-weight="900" fill="#ef4444" font-family="var(--font-sans, sans-serif)">A</text>
      </template>
      <!-- PlayStation: Blue Cross (✕) - Bold High Contrast -->
      <template v-else>
        <line x1="7" y1="7" x2="17" y2="17" stroke="#38bdf8" stroke-width="3" stroke-linecap="round" />
        <line x1="17" y1="7" x2="7" y2="17" stroke="#38bdf8" stroke-width="3" stroke-linecap="round" />
      </template>
    </template>

    <!-- ========================================================================
         FACE BUTTON: B / CIRCLE
         ======================================================================== -->
    <template v-else-if="id === 'b'">
      <circle cx="12" cy="12" r="10" class="btn-base-circle" />
      <!-- Xbox: Red B -->
      <template v-if="isXbox">
        <text x="12" y="16.2" text-anchor="middle" font-size="12" font-weight="900" fill="#ef4444" font-family="var(--font-sans, sans-serif)">B</text>
      </template>
      <!-- Nintendo: Crisp White B -->
      <template v-else-if="isNintendo">
        <text x="12" y="16.2" text-anchor="middle" font-size="12" font-weight="900" fill="#f8fafc" font-family="var(--font-sans, sans-serif)">B</text>
      </template>
      <!-- PlayStation: Red Circle (○) - Bold High Contrast -->
      <template v-else>
        <circle cx="12" cy="12" r="5.5" stroke="#ef4444" stroke-width="3" fill="none" />
      </template>
    </template>

    <!-- ========================================================================
         FACE BUTTON: X / SQUARE
         ======================================================================== -->
    <template v-else-if="id === 'x'">
      <circle cx="12" cy="12" r="10" class="btn-base-circle" />
      <!-- Xbox: Blue X -->
      <template v-if="isXbox">
        <text x="12" y="16.2" text-anchor="middle" font-size="12" font-weight="900" fill="#3b82f6" font-family="var(--font-sans, sans-serif)">X</text>
      </template>
      <!-- Nintendo: Crisp White X -->
      <template v-else-if="isNintendo">
        <text x="12" y="16.2" text-anchor="middle" font-size="12" font-weight="900" fill="#f8fafc" font-family="var(--font-sans, sans-serif)">X</text>
      </template>
      <!-- PlayStation: Pink Square (□) - Bold High Contrast -->
      <template v-else>
        <rect x="7.2" y="7.2" width="9.6" height="9.6" stroke="#ec4899" stroke-width="3" rx="1.5" fill="none" />
      </template>
    </template>

    <!-- ========================================================================
         FACE BUTTON: Y / TRIANGLE
         ======================================================================== -->
    <template v-else-if="id === 'y'">
      <circle cx="12" cy="12" r="10" class="btn-base-circle" />
      <!-- Xbox: Yellow Y -->
      <template v-if="isXbox">
        <text x="12" y="16.2" text-anchor="middle" font-size="12" font-weight="900" fill="#eab308" font-family="var(--font-sans, sans-serif)">Y</text>
      </template>
      <!-- Nintendo: Crisp White Y -->
      <template v-else-if="isNintendo">
        <text x="12" y="16.2" text-anchor="middle" font-size="12" font-weight="900" fill="#f8fafc" font-family="var(--font-sans, sans-serif)">Y</text>
      </template>
      <!-- PlayStation: Green Triangle (△) - Bold High Contrast -->
      <template v-else>
        <polygon points="12,5.5 17.8,16.5 6.2,16.5" stroke="#10b981" stroke-width="3" stroke-linejoin="round" fill="none" />
      </template>
    </template>

    <!-- ========================================================================
         LEFT TRIGGER (L2 / LT / ZL) - Curved Pull Trigger Silhouette
         ======================================================================== -->
    <template v-else-if="id === 'l2'">
      <path
        d="M17 3H9C6 3 4.5 4.8 4.5 7.5v4c0 3.8 2.2 7 5 9l1.8 1.2c.4.3 1.2.3 1.7 0l2-1.3c1.5-1 2-2.5 2-4.4V5c0-1.2-.8-2-2-2z"
        class="trigger-shape"
      />
      <!-- Trigger Pull Notch -->
      <path d="M7 8h4M7 11h4" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" opacity="0.6" />
      <text x="12.5" y="17" text-anchor="middle" font-size="7.5" font-weight="800" fill="currentColor" opacity="0.9">
        {{ isXbox ? 'LT' : isNintendo ? 'ZL' : 'L2' }}
      </text>
    </template>

    <!-- ========================================================================
         RIGHT TRIGGER (R2 / RT / ZR) - Mirrored Curved Pull Trigger Silhouette
         ======================================================================== -->
    <template v-else-if="id === 'r2'">
      <path
        d="M7 3h8c3 0 4.5 4.8 4.5 7.5v4c0 3.8-2.2 7-5 9l-1.8 1.2c-.4.3-1.2.3-1.7 0l-2-1.3c-1.5-1-2-2.5-2-4.4V5c0-1.2.8-2 2-2z"
        class="trigger-shape"
      />
      <path d="M13 8h4M13 11h4" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" opacity="0.6" />
      <text x="11.5" y="17" text-anchor="middle" font-size="7.5" font-weight="800" fill="currentColor" opacity="0.9">
        {{ isXbox ? 'RT' : isNintendo ? 'ZR' : 'R2' }}
      </text>
    </template>

    <!-- ========================================================================
         LEFT SHOULDER BUMPER (L1 / LB / L)
         ======================================================================== -->
    <template v-else-if="id === 'l1' || id === 'l4'">
      <path
        d="M3 14.5C3 9 7 5.5 13 5.5h8v8c0 2.2-1.5 3.5-3.5 3.5H6c-2 0-3-1.2-3-2.5z"
        class="bumper-shape"
      />
      <text x="12" y="14" text-anchor="middle" font-size="8" font-weight="800" fill="currentColor">
        {{ isXbox ? (id === 'l4' ? 'L4' : 'LB') : isNintendo ? (id === 'l4' ? 'L4' : 'L') : (id === 'l4' ? 'L4' : 'L1') }}
      </text>
    </template>

    <!-- ========================================================================
         RIGHT SHOULDER BUMPER (R1 / RB / R)
         ======================================================================== -->
    <template v-else-if="id === 'r1' || id === 'r4'">
      <path
        d="M21 14.5C21 9 17 5.5 11 5.5H3v8c0 2.2 1.5 3.5 3.5 3.5h11c2 0 3-1.2 3-2.5z"
        class="bumper-shape"
      />
      <text x="12" y="14" text-anchor="middle" font-size="8" font-weight="800" fill="currentColor">
        {{ isXbox ? (id === 'r4' ? 'R4' : 'RB') : isNintendo ? (id === 'r4' ? 'R4' : 'R') : (id === 'r4' ? 'R4' : 'R1') }}
      </text>
    </template>

    <!-- ========================================================================
         LEFT ANALOG THUMBSTICK (Left Stick)
         ======================================================================== -->
    <template v-else-if="id === 'left_stick'">
      <circle cx="12" cy="12" r="10" class="stick-base-ring" />
      <circle cx="12" cy="12" r="6.5" class="stick-center-well" />
      <circle cx="12" cy="12" r="3" fill="var(--accent-custom)" opacity="0.8" />
      <!-- Left orientation hint -->
      <path d="M6 12h2" stroke="var(--accent-custom)" stroke-width="1.8" stroke-linecap="round" />
    </template>

    <!-- ========================================================================
         RIGHT ANALOG THUMBSTICK (Right Stick)
         ======================================================================== -->
    <template v-else-if="id === 'right_stick'">
      <circle cx="12" cy="12" r="10" class="stick-base-ring" />
      <circle cx="12" cy="12" r="6.5" class="stick-center-well" />
      <circle cx="12" cy="12" r="3" fill="var(--accent-custom)" opacity="0.8" />
      <!-- Right orientation hint -->
      <path d="M16 12h2" stroke="var(--accent-custom)" stroke-width="1.8" stroke-linecap="round" />
    </template>

    <!-- ========================================================================
         THUMBSTICK CLICKS (L3 / R3)
         ======================================================================== -->
    <template v-else-if="id === 'l3' || id === 'r3'">
      <circle cx="12" cy="12" r="9.5" class="stick-base-ring" />
      <circle cx="12" cy="12" r="5.5" class="stick-center-well" />
      <path d="M12 6.5v6.5m-2.5-2.5l2.5 2.5 2.5-2.5" stroke="var(--accent-custom)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
      <text x="12" y="19.5" text-anchor="middle" font-size="6.5" font-weight="800" fill="currentColor">
        {{ id === 'l3' ? (isXbox ? 'LS' : 'L3') : (isXbox ? 'RS' : 'R3') }}
      </text>
    </template>

    <!-- ========================================================================
         UNIFIED D-PAD (4-Way Directional Cross)
         ======================================================================== -->
    <template v-else-if="id === 'dpad'">
      <path
        d="M9 2.5h6v5h5v6h-5v5H9v-5H4v-6h5v-5z"
        class="dpad-cross-shape"
      />
      <circle cx="12" cy="12" r="1.8" fill="currentColor" opacity="0.4" />
      <!-- Small directional ticks -->
      <path d="M12 4.5l-1.5 2h3zM12 19.5l-1.5-2h3zM4.5 12l2-1.5v3zM19.5 12l-2-1.5v3z" fill="currentColor" opacity="0.6" />
    </template>

    <!-- ========================================================================
         DISCRETE D-PAD DIRECTIONS (Up, Down, Left, Right)
         ======================================================================== -->
    <template v-else-if="id === 'dpad_up'">
      <path d="M9 2.5h6v5h5v6h-5v5H9v-5H4v-6h5v-5z" class="dpad-cross-shape" />
      <polygon points="12,3.5 14.5,7 9.5,7" fill="var(--accent-custom)" />
    </template>

    <template v-else-if="id === 'dpad_down'">
      <path d="M9 2.5h6v5h5v6h-5v5H9v-5H4v-6h5v-5z" class="dpad-cross-shape" />
      <polygon points="12,20.5 14.5,17 9.5,17" fill="var(--accent-custom)" />
    </template>

    <template v-else-if="id === 'dpad_left'">
      <path d="M9 2.5h6v5h5v6h-5v5H9v-5H4v-6h5v-5z" class="dpad-cross-shape" />
      <polygon points="3.5,12 7,9.5 7,14.5" fill="var(--accent-custom)" />
    </template>

    <template v-else-if="id === 'dpad_right'">
      <path d="M9 2.5h6v5h5v6h-5v5H9v-5H4v-6h5v-5z" class="dpad-cross-shape" />
      <polygon points="20.5,12 17,9.5 17,14.5" fill="var(--accent-custom)" />
    </template>

    <!-- ========================================================================
         SYSTEM: MENU / OPTIONS / PLUS
         ======================================================================== -->
    <template v-else-if="id === 'menu'">
      <circle cx="12" cy="12" r="9.5" class="btn-base-circle" />
      <!-- Nintendo: Plus (+) -->
      <template v-if="isNintendo">
        <path d="M12 7v10M7 12h10" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" />
      </template>
      <!-- Xbox / PlayStation: 3 Stacked Horizontal Lines (Menu / Options) -->
      <template v-else>
        <line x1="7" y1="8" x2="17" y2="8" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
        <line x1="7" y1="12" x2="17" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
        <line x1="7" y1="16" x2="17" y2="16" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
      </template>
    </template>

    <!-- ========================================================================
         SYSTEM: OPTIONS / VIEW / MINUS / SHARE
         ======================================================================== -->
    <template v-else-if="id === 'options'">
      <circle cx="12" cy="12" r="9.5" class="btn-base-circle" />
      <!-- Nintendo: Minus (−) -->
      <template v-if="isNintendo">
        <line x1="7" y1="12" x2="17" y2="12" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" />
      </template>
      <!-- Xbox: View (2 overlapping squares) -->
      <template v-else-if="isXbox">
        <rect x="6.5" y="9.5" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="1.6" fill="none" />
        <rect x="10.5" y="6.5" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="1.6" fill="none" />
      </template>
      <!-- PlayStation: Share / Create (3 radiating lines) -->
      <template v-else>
        <line x1="7" y1="15" x2="10.5" y2="9" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
        <line x1="12" y1="16" x2="12" y2="7.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
        <line x1="17" y1="15" x2="13.5" y2="9" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
      </template>
    </template>

    <!-- ========================================================================
         SYSTEM: HOME / GUIDE
         ======================================================================== -->
    <template v-else-if="id === 'home'">
      <!-- Nintendo: House (⌂) -->
      <template v-if="isNintendo">
        <circle cx="12" cy="12" r="10" class="btn-base-circle" />
        <path d="M6 12l6-5 6 5v5a1 1 0 0 1-1 1h-3v-4h-4v4H7a1 1 0 0 1-1-1v-5z" fill="currentColor" stroke="none" />
      </template>
      <!-- Xbox: Sphere with iconic X -->
      <template v-else-if="isXbox">
        <circle cx="12" cy="12" r="9.5" stroke="currentColor" stroke-width="1.8" class="btn-base-circle" />
        <path d="M7.2 7C9 9 12 13 12 13s3-4 4.8-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
        <path d="M5.8 15.5C8 13.5 12 11 12 11s4 2.5 6.2 4.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
      </template>
      <!-- PlayStation: PS glyph -->
      <template v-else>
        <circle cx="12" cy="12" r="10" class="btn-base-circle" />
        <path d="M9 5v9.5c.8.4 1.7.4 2.2.2.6-.3.6-.9.6-.9 0-1-.8-1.3-1.8-1.5l-.9-.1V7.8c.7.2 1.2.5 1.2 1.1h1.4c0-1.2-1.2-1.9-2.6-1.9-.8 0-1.5.2-2.1.7V5H9z" fill="currentColor" stroke="none" />
        <path d="M14.5 13c-.8-.3-2-.5-3.2.1l-1.5.8c-.7.3-1 .8-1 1.2 0 .8.9 1.1 2.4 1.1 1.6 0 3.1-.5 3.8-1.2.4-.4.5-.8.5-1.2 0-.3-.3-.5-.9-.8z" fill="currentColor" stroke="none" />
      </template>
    </template>

    <!-- ========================================================================
         TOUCHPAD (PlayStation DualSense Touchpad)
         ======================================================================== -->
    <template v-else-if="id === 'touchpad'">
      <rect x="3.5" y="6.5" width="17" height="11" rx="2.5" class="btn-base-circle" />
      <line x1="8.5" y1="12" x2="15.5" y2="12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" opacity="0.6" />
    </template>

    <!-- ========================================================================
         FALLBACK / GENERIC
         ======================================================================== -->
    <template v-else>
      <circle cx="12" cy="12" r="9.5" class="btn-base-circle" />
      <circle cx="12" cy="12" r="3" fill="currentColor" opacity="0.6" />
    </template>
  </svg>
</template>

<style scoped>
.controller-button-icon {
  display: inline-block;
  vertical-align: middle;
  flex-shrink: 0;
}

.btn-base-circle {
  fill: #000000;
  stroke: rgba(255, 255, 255, 0.40);
  stroke-width: 1.5;
}

.trigger-shape {
  fill: #000000;
  stroke: rgba(255, 255, 255, 0.40);
  stroke-width: 1.6;
  stroke-linejoin: round;
}

.bumper-shape {
  fill: #000000;
  stroke: rgba(255, 255, 255, 0.40);
  stroke-width: 1.6;
  stroke-linejoin: round;
}

.stick-base-ring {
  fill: #000000;
  stroke: rgba(255, 255, 255, 0.40);
  stroke-width: 1.6;
}

.stick-center-well {
  fill: none;
  stroke: rgba(255, 255, 255, 0.25);
  stroke-width: 1.2;
}

.dpad-cross-shape {
  fill: #000000;
  stroke: rgba(255, 255, 255, 0.40);
  stroke-width: 1.5;
  stroke-linejoin: round;
}
</style>
