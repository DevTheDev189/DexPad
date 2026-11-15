<script setup lang="ts">
defineProps<{
  name:
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
    | 'image'
    | 'x'
    | 'chevron-down'
    | 'chevron-right'
    | 'radio'
    | 'link'
    | 'unlink'
    | 'chip'
    | 'sliders';
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
    <template v-else-if="name === 'sparkles'">
      <path d="M12 3l1.912 5.813a2 2 0 0 0 1.275 1.275L21 12l-5.813 1.912a2 2 0 0 0-1.275 1.275L12 21l-1.912-5.813a2 2 0 0 0-1.275-1.275L3 12l5.813-1.912a2 2 0 0 0 1.275-1.275L12 3z" />
    </template>

    <!-- Image -->
    <template v-else-if="name === 'image'">
      <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
      <circle cx="8.5" cy="8.5" r="1.5" />
      <polyline points="21 15 16 10 5 21" />
    </template>

    <!-- X -->
    <template v-else-if="name === 'x'">
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
  </svg>
</template>

<style scoped>
.cosmic-icon {
  display: inline-block;
  vertical-align: middle;
  flex-shrink: 0;
}
</style>
