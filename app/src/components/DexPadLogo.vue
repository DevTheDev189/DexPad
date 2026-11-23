<script setup lang="ts">
withDefaults(
  defineProps<{
    variant?: 'full' | 'icon' | 'stacked' | 'glyph';
    size?: 'sm' | 'md' | 'lg' | number;
  }>(),
  {
    variant: 'full',
    size: 'md',
  }
);
</script>

<template>
  <div
    class="dexpad-logo-root"
    :class="[`variant-${variant}`, typeof size === 'string' ? `size-${size}` : '']"
    :style="typeof size === 'number' ? { height: `${size}px` } : {}"
  >
    <!-- 1. ICON ONLY (Apple/Figma Minimalist Squircle Tile with Intersecting Stroke) -->
    <svg
      v-if="variant === 'icon'"
      viewBox="0 0 100 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      class="logo-svg icon-only"
    >
      <defs>
        <linearGradient id="tech-accent-grad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#38bdf8" />
          <stop offset="100%" stop-color="#0284c7" />
        </linearGradient>

        <linearGradient id="tech-surface-grad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#182235" />
          <stop offset="100%" stop-color="#0b111e" />
        </linearGradient>

        <filter id="layer-depth" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="1.5" stdDeviation="1.8" flood-color="rgba(0, 0, 0, 0.45)" />
        </filter>
      </defs>

      <!-- Apple-style Continuous Squircle Tile -->
      <rect
        x="2"
        y="2"
        width="96"
        height="96"
        rx="24"
        fill="url(#tech-surface-grad)"
        stroke="rgba(255, 255, 255, 0.14)"
        stroke-width="1.5"
      />

      <g>
        <!-- Diagonal Bar 1: Top-Left to Bottom-Right (Cyan Capsule) -->
        <rect
          x="20"
          y="41"
          width="60"
          height="18"
          rx="9"
          transform="rotate(45 50 50)"
          fill="url(#tech-accent-grad)"
        />

        <!-- Diagonal Stroke 2: Top-Right to Bottom-Left (Contoured White Stroke, Shifted Lower, No Black Circle) -->
        <path
          d="M 65,21 C 69.4,25.4 69.4,32.6 65,37 L 57,45 L 45,57 L 37,65 C 32.6,69.4 25.4,69.4 21,65 C 16.6,60.6 16.6,53.4 21,49 L 29,41 Z"
          transform="translate(0, 3)"
          fill="#f8fafc"
          filter="url(#layer-depth)"
        />
      </g>
    </svg>

    <!-- 2. BARE GLYPH (No Tile Container, Just Pure Minimal Vector Mark) -->
    <svg
      v-else-if="variant === 'glyph'"
      viewBox="0 0 80 80"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      class="logo-svg bare-glyph"
    >
      <defs>
        <linearGradient id="glyph-accent" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#38bdf8" />
          <stop offset="100%" stop-color="#0284c7" />
        </linearGradient>
        <filter id="glyph-depth" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="1.2" stdDeviation="1.5" flood-color="rgba(0, 0, 0, 0.4)" />
        </filter>
      </defs>
      <!-- Diagonal 1 -->
      <rect
        x="11"
        y="32"
        width="58"
        height="16"
        rx="8"
        transform="rotate(45 40 40)"
        fill="url(#glyph-accent)"
      />
      <!-- Diagonal Stroke 2 (Scaled & shifted lower) -->
      <g transform="translate(-10, -8)">
        <path
          d="M 65,21 C 69.4,25.4 69.4,32.6 65,37 L 57,45 L 45,57 L 37,65 C 32.6,69.4 25.4,69.4 21,65 C 16.6,60.6 16.6,53.4 21,49 L 29,41 Z"
          transform="translate(0, 3)"
          fill="#f8fafc"
          filter="url(#glyph-depth)"
        />
      </g>
    </svg>

    <!-- 3. STACKED VERTICAL LOCKUP (Tile on Top, Adaptive Text Below) -->
    <svg
      v-else-if="variant === 'stacked'"
      viewBox="0 0 120 136"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      class="logo-svg stacked-lockup"
    >
      <defs>
        <linearGradient id="stk-accent" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#38bdf8" />
          <stop offset="100%" stop-color="#0284c7" />
        </linearGradient>
        <linearGradient id="stk-surf" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#182235" />
          <stop offset="100%" stop-color="#0b111e" />
        </linearGradient>
        <filter id="stk-depth" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="1" stdDeviation="1.2" flood-color="rgba(0, 0, 0, 0.4)" />
        </filter>
      </defs>

      <!-- Center Squircle Tile (Scale to 72x72) -->
      <g transform="translate(24, 8)">
        <rect
          width="72"
          height="72"
          rx="18"
          fill="url(#stk-surf)"
          stroke="rgba(255, 255, 255, 0.12)"
          stroke-width="1.2"
        />
        <rect
          x="15"
          y="30"
          width="42"
          height="12"
          rx="6"
          transform="rotate(45 36 36)"
          fill="url(#stk-accent)"
        />
        <g transform="translate(0, 0) scale(0.72)">
          <path
            d="M 65,21 C 69.4,25.4 69.4,32.6 65,37 L 57,45 L 45,57 L 37,65 C 32.6,69.4 25.4,69.4 21,65 C 16.6,60.6 16.6,53.4 21,49 L 29,41 Z"
            transform="translate(0, 3)"
            fill="#f8fafc"
            filter="url(#stk-depth)"
          />
        </g>
      </g>

      <!-- Adaptive Modern Typography -->
      <g transform="translate(60, 108)" text-anchor="middle">
        <text
          y="0"
          font-family="-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', system-ui, sans-serif"
          font-size="19"
          letter-spacing="-0.03em"
        >
          <tspan font-weight="700" class="dex-text">Dex</tspan><tspan font-weight="400" class="pad-text">Pad</tspan>
        </text>
        <text
          class="logo-subtitle"
          y="15"
          font-family="-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Inter', system-ui, sans-serif"
          font-size="8.5"
          font-weight="500"
          letter-spacing="0.16em"
        >
          CONTROLLER STUDIO
        </text>
      </g>
    </svg>

    <!-- 4. FULL HORIZONTAL LOCKUP (Default: Sleek Minimalist Squircle + Dynamic Contrast Wordmark) -->
    <svg
      v-else
      viewBox="0 0 200 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      class="logo-svg full-lockup"
    >
      <defs>
        <linearGradient id="full-accent" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#38bdf8" />
          <stop offset="100%" stop-color="#0284c7" />
        </linearGradient>
        <linearGradient id="full-surf" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#182235" />
          <stop offset="100%" stop-color="#0b111e" />
        </linearGradient>
        <filter id="full-depth" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="0.8" stdDeviation="1" flood-color="rgba(0, 0, 0, 0.4)" />
        </filter>
      </defs>

      <!-- Left: Apple-style Squircle Tile (38x38) -->
      <g transform="translate(4, 5)">
        <rect
          width="38"
          height="38"
          rx="10"
          fill="url(#full-surf)"
          stroke="rgba(255, 255, 255, 0.12)"
          stroke-width="1"
        />

        <!-- Cyan Capsule -->
        <rect
          x="7.5"
          y="15.5"
          width="23"
          height="7"
          rx="3.5"
          transform="rotate(45 19 19)"
          fill="url(#full-accent)"
        />

        <!-- Contoured White Stroke (Scaled to 38x38) -->
        <g transform="translate(0, 0) scale(0.38)">
          <path
            d="M 65,21 C 69.4,25.4 69.4,32.6 65,37 L 57,45 L 45,57 L 37,65 C 32.6,69.4 25.4,69.4 21,65 C 16.6,60.6 16.6,53.4 21,49 L 29,41 Z"
            transform="translate(0, 3)"
            fill="#f8fafc"
            filter="url(#full-depth)"
          />
        </g>
      </g>

      <!-- Right: Ultra-Clean Typography with Adaptive Contrast -->
      <g transform="translate(54, 27)">
        <text
          font-family="-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', system-ui, sans-serif"
          font-size="20"
          letter-spacing="-0.035em"
        >
          <tspan font-weight="700" class="dex-text">Dex</tspan><tspan font-weight="400" class="pad-text">Pad</tspan>
        </text>

        <!-- Dynamic Subtitle Indicator Tag -->
        <text
          class="logo-subtitle"
          x="1"
          y="11"
          font-family="-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Inter', system-ui, sans-serif"
          font-size="7.5"
          font-weight="600"
          letter-spacing="0.14em"
        >
          CONTROLLER STUDIO
        </text>
      </g>
    </svg>
  </div>
</template>

<style scoped>
.dexpad-logo-root {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  user-select: none;
  flex-shrink: 0;
}

.logo-svg {
  display: block;
  height: 100%;
  width: auto;
}

/* ==========================================================================
   Adaptive Light/Dark Theme Color Inks
   ========================================================================== */

/* Dark Mode (Default) */
.dex-text {
  fill: var(--text-primary, #ffffff);
  transition: fill 0.25s ease;
}

.pad-text {
  fill: var(--accent-sky, #38bdf8);
  transition: fill 0.25s ease;
}

.logo-subtitle {
  fill: var(--text-muted, #94a3b8);
  transition: fill 0.25s ease;
}

/* Light Mode: Switch "Dex" text to Black / Slate for High Readability */
:global(.theme-light) .dex-text {
  fill: #0f172a !important;
}

:global(.theme-light) .pad-text {
  fill: var(--accent-sky, #0284c7) !important;
}

:global(.theme-light) .logo-subtitle {
  fill: #475569 !important;
}

/* Size Presets */
.size-sm {
  height: 24px;
}

.size-md {
  height: 32px;
}

.size-lg {
  height: 44px;
}
</style>
