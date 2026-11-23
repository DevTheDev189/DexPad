<script setup lang="ts">
export type IconName =
  | 'bolt'
  | 'gamepad'
  | 'table'
  | 'layout'
  | 'refresh'
  | 'record'
  | 'search'
  | 'check'
  | 'edit'
  | 'trash'
  | 'plus'
  | 'download'
  | 'upload'
  | 'sparkles'
  | 'sparkle'
  | 'image'
  | 'x'
  | 'close'
  | 'chevron-down'
  | 'chevron-right'
  | 'radio'
  | 'link'
  | 'unlink'
  | 'chip'
  | 'sliders'
  | 'brush'
  | 'sun'
  | 'moon'
  | 'monitor'
  | 'zap'
  | 'diamond'
  | 'star'
  | 'play'
  | 'xbox'
  | 'playstation'
  | 'nintendo'
  | 'gyro'
  | 'touchpad';

defineProps<{
  name: IconName;
  size?: number | string;
}>();
</script>

<template>
  <svg
    :width="size || 16"
    :height="size || 16"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    class="cosmic-icon"
  >
    <!-- Bolt -->
    <path v-if="name === 'bolt'" d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />

    <!-- Gamepad -->
    <template v-else-if="name === 'gamepad'">
      <rect x="2" y="6" width="20" height="12" rx="4" />
      <path d="M6 12h4m-2-2v4m10-2h.01m-3 0h.01" />
    </template>

    <!-- Table -->
    <template v-else-if="name === 'table'">
      <rect x="3" y="3" width="18" height="18" rx="2" />
      <path d="M3 9h18M3 15h18M9 9v12M15 9v12" />
    </template>

    <!-- Layout / Controller View -->
    <template v-else-if="name === 'layout' || name === 'sliders'">
      <path d="M4 21v-7m0-4V3m8 18v-9m0-4V3m8 18v-5m0-4V3M1 14h6m2-6h6m2 8h6" />
    </template>

    <!-- Refresh -->
    <template v-else-if="name === 'refresh'">
      <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2" />
    </template>

    <!-- Record -->
    <circle v-else-if="name === 'record'" cx="12" cy="12" r="6" fill="currentColor" />

    <!-- Search -->
    <template v-else-if="name === 'search'">
      <circle cx="11" cy="11" r="8" />
      <line x1="21" y1="21" x2="16.65" y2="16.65" />
    </template>

    <!-- Check -->
    <polyline v-else-if="name === 'check'" points="20 6 9 17 4 12" />

    <!-- Edit -->
    <template v-else-if="name === 'edit'">
      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
    </template>

    <!-- Trash -->
    <template v-else-if="name === 'trash'">
      <polyline points="3 6 5 6 21 6" />
      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
    </template>

    <!-- Plus -->
    <template v-else-if="name === 'plus'">
      <line x1="12" y1="5" x2="12" y2="19" />
      <line x1="5" y1="12" x2="19" y2="12" />
    </template>

    <!-- Download -->
    <template v-else-if="name === 'download'">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="7 10 12 15 17 10" />
      <line x1="12" y1="15" x2="12" y2="3" />
    </template>

    <!-- Upload -->
    <template v-else-if="name === 'upload'">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="17 8 12 3 7 8" />
      <line x1="12" y1="3" x2="12" y2="15" />
    </template>

    <!-- Sparkles -->
    <template v-else-if="name === 'sparkles' || name === 'sparkle'">
      <path d="M12 3l1.912 5.813a2 2 0 0 0 1.275 1.275L21 12l-5.813 1.912a2 2 0 0 0-1.275 1.275L12 21l-1.912-5.813a2 2 0 0 0-1.275-1.275L3 12l5.813-1.912a2 2 0 0 0 1.275-1.275L12 3z" />
    </template>

    <!-- Image -->
    <template v-else-if="name === 'image'">
      <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
      <circle cx="8.5" cy="8.5" r="1.5" />
      <polyline points="21 15 16 10 5 21" />
    </template>

    <!-- X / Close -->
    <template v-else-if="name === 'x' || name === 'close'">
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </template>

    <!-- Chevron Down -->
    <polyline v-else-if="name === 'chevron-down'" points="6 9 12 15 18 9" />

    <!-- Chevron Right -->
    <polyline v-else-if="name === 'chevron-right'" points="9 18 15 12 9 6" />

    <!-- Radio / Telemetry -->
    <template v-else-if="name === 'radio'">
      <circle cx="12" cy="12" r="2" />
      <path d="M16.24 7.76a6 6 0 0 1 0 8.49m-8.48-.01a6 6 0 0 1 0-8.49m11.31-2.82a10 10 0 0 1 0 14.14m-14.14 0a10 10 0 0 1 0-14.14" />
    </template>

    <!-- Link -->
    <template v-else-if="name === 'link'">
      <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
      <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
    </template>

    <!-- Unlink -->
    <template v-else-if="name === 'unlink'">
      <path d="M18.84 12.25l1.72-1.71a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
      <path d="M5.16 11.75l-1.72 1.71a5 5 0 0 0 7.07 7.07l1.72-1.71" />
      <line x1="2" y1="2" x2="22" y2="22" />
    </template>

    <!-- Chip / Hardware -->
    <template v-else-if="name === 'chip'">
      <rect x="4" y="4" width="16" height="16" rx="2" />
      <rect x="9" y="9" width="6" height="6" />
      <line x1="9" y1="1" x2="9" y2="4" />
      <line x1="15" y1="1" x2="15" y2="4" />
      <line x1="9" y1="20" x2="9" y2="23" />
      <line x1="15" y1="20" x2="15" y2="23" />
      <line x1="20" y1="9" x2="23" y2="9" />
      <line x1="20" y1="14" x2="23" y2="14" />
      <line x1="1" y1="9" x2="4" y2="9" />
      <line x1="1" y1="14" x2="4" y2="14" />
    </template>

    <!-- Brush (Theme & Style) -->
    <template v-else-if="name === 'brush'">
      <path d="M18.375 2.625a3.875 3.875 0 0 1 3 3c0 2.14-1.735 3.875-3.875 3.875H16v2.5a5 5 0 0 1-5 5H9.5a2.5 2.5 0 0 0-2.5 2.5c0 1.38-1.12 2.5-2.5 2.5H4a1 1 0 0 1-1-1v-1a5 5 0 0 1 5-5h2a3 3 0 0 0 3-3V9.5a5 5 0 0 1 5-5h.375z" />
    </template>

    <!-- Sun -->
    <template v-else-if="name === 'sun'">
      <circle cx="12" cy="12" r="5" />
      <line x1="12" y1="1" x2="12" y2="3" />
      <line x1="12" y1="21" x2="12" y2="23" />
      <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
      <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
      <line x1="1" y1="12" x2="3" y2="12" />
      <line x1="21" y1="12" x2="23" y2="12" />
      <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
      <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
    </template>

    <!-- Moon -->
    <path v-else-if="name === 'moon'" d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />

    <!-- Monitor / Display -->
    <template v-else-if="name === 'monitor'">
      <rect x="2" y="3" width="20" height="14" rx="2" ry="2" />
      <line x1="8" y1="21" x2="16" y2="21" />
      <line x1="12" y1="17" x2="12" y2="21" />
    </template>

    <!-- Zap / Wave Energy -->
    <polygon v-else-if="name === 'zap'" points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />

    <!-- Diamond / Abstract Shape -->
    <path v-else-if="name === 'diamond'" d="M6 3h12l4 6-10 12L2 9z" />

    <!-- Star / Cosmic -->
    <polygon v-else-if="name === 'star'" points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />

    <!-- Play / Video Loop -->
    <polygon v-else-if="name === 'play'" points="5 3 19 12 5 21 5 3" />

    <!-- Xbox Logo Glyph -->
    <template v-else-if="name === 'xbox'">
      <circle cx="12" cy="12" r="9.5" stroke="currentColor" stroke-width="1.8" />
      <path d="M6.8 6.5C8.8 8.8 12 13.5 12 13.5s3.2-4.7 5.2-7" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" />
      <path d="M5.2 16.2C7.5 14 12 11 12 11s4.5 3 6.8 5.2" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" />
      <path d="M4 10.5C5.8 12 8 13 8 13" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
      <path d="M20 10.5C18.2 12 16 13 16 13" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
    </template>

    <!-- PlayStation Logo Glyph -->
    <template v-else-if="name === 'playstation'">
      <path d="M8.8 3.5v12.2c1.1.5 2.2.5 2.8.2.7-.4.7-1.2.7-1.2 0-1.3-1-1.7-2.3-1.9l-1.2-.2V7.1c.9.2 1.6.7 1.6 1.4h1.8c0-1.6-1.5-2.5-3.4-2.5-1 0-2 .3-2.7.9V3.5h2.6z" fill="currentColor" stroke="none" />
      <path d="M15.5 13.8c-1.1-.4-2.6-.6-4.2.2l-2 1c-.9.4-1.3 1-1.3 1.5 0 1.1 1.2 1.5 3.1 1.5 2.1 0 4-.6 4.9-1.6.5-.5.7-1.1.7-1.6 0-.4-.4-.7-1.2-1z" fill="currentColor" stroke="none" />
    </template>

    <!-- Nintendo Switch Joy-Con Glyph (Authentic Switch Logo) -->
    <template v-else-if="name === 'nintendo'">
      <!-- Left Joy-Con (Hollow with solid stick) -->
      <path d="M4 5.5A3.5 3.5 0 0 1 7.5 2H10v20H7.5A3.5 3.5 0 0 1 4 18.5v-13z" stroke="currentColor" stroke-width="1.8" fill="none" />
      <circle cx="7" cy="8.5" r="1.5" fill="currentColor" stroke="none" />
      <!-- Right Joy-Con (Filled with hollow stick) -->
      <path d="M14 2h2.5A3.5 3.5 0 0 1 20 5.5v13a3.5 3.5 0 0 1-3.5 3.5H14V2z" fill="currentColor" stroke="currentColor" stroke-width="1.8" />
      <circle cx="17" cy="15.5" r="1.5" fill="var(--bg-card, #030712)" stroke="none" />
    </template>

    <!-- Gyro Aim Glyph (Gimbal / Gyroscopic Crosshair) -->
    <template v-else-if="name === 'gyro'">
      <circle cx="12" cy="12" r="9.5" stroke="currentColor" stroke-width="1.5" stroke-dasharray="3 2" />
      <ellipse cx="12" cy="12" rx="9" ry="3.8" transform="rotate(-30 12 12)" stroke="currentColor" stroke-width="1.6" />
      <circle cx="12" cy="12" r="2.5" fill="currentColor" stroke="none" />
      <line x1="12" y1="2" x2="12" y2="5" stroke="currentColor" stroke-width="2" />
      <line x1="12" y1="19" x2="12" y2="22" stroke="currentColor" stroke-width="2" />
      <line x1="2" y1="12" x2="5" y2="12" stroke="currentColor" stroke-width="2" />
      <line x1="19" y1="12" x2="22" y2="12" stroke="currentColor" stroke-width="2" />
    </template>

    <!-- Touchpad Glyph -->
    <template v-else-if="name === 'touchpad'">
      <rect x="2.5" y="5" width="19" height="14" rx="3.5" stroke="currentColor" stroke-width="1.8" fill="none" />
      <line x1="12" y1="14" x2="12" y2="19" stroke="currentColor" stroke-width="1.8" />
      <line x1="2.5" y1="14" x2="21.5" y2="14" stroke="currentColor" stroke-width="1.5" stroke-dasharray="2 2" />
      <circle cx="12" cy="9.5" r="1.5" fill="currentColor" stroke="none" />
    </template>
  </svg>
</template>

<style scoped>
.cosmic-icon {
  display: inline-block;
  vertical-align: middle;
  flex-shrink: 0;
}
</style>
