<template>
  <svg class="metaball-defs-svg" aria-hidden="true" focusable="false">
    <defs>
      <!-- Liquid Metaball / Plasma Goo Filter -->
      <filter id="nebula-goo">
        <feGaussianBlur in="SourceGraphic" stdDeviation="10" result="blur" />
        <feColorMatrix
          in="blur"
          mode="matrix"
          values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 22 -9"
          result="goo"
        />
        <feBlend in="SourceGraphic" in2="goo" />
      </filter>

      <!-- Soft Glow Filter -->
      <filter id="plasma-glow" x="-50%" y="-50%" width="200%" height="200%">
        <feGaussianBlur stdDeviation="8" result="blur" />
        <feColorMatrix
          type="matrix"
          values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 2 0"
        />
        <feMerge>
          <feMergeNode in="blur" />
          <feMergeNode in="SourceGraphic" />
        </feMerge>
      </filter>

      <!-- Cosmic Radial Gradients -->
      <radialGradient id="plasma-cyan" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.9" />
        <stop offset="60%" stop-color="#3b82f6" stop-opacity="0.5" />
        <stop offset="100%" stop-color="#6366f1" stop-opacity="0" />
      </radialGradient>

      <radialGradient id="plasma-violet" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="#c084fc" stop-opacity="0.9" />
        <stop offset="60%" stop-color="#8b5cf6" stop-opacity="0.5" />
        <stop offset="100%" stop-color="#3b82f6" stop-opacity="0" />
      </radialGradient>

      <radialGradient id="plasma-active" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="#ffffff" stop-opacity="1" />
        <stop offset="35%" stop-color="#38bdf8" stop-opacity="0.8" />
        <stop offset="70%" stop-color="#8b5cf6" stop-opacity="0.4" />
        <stop offset="100%" stop-color="#6366f1" stop-opacity="0" />
      </radialGradient>

      <!-- Glass Shell Linear Gradients -->
      <linearGradient id="shell-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#1e293b" stop-opacity="0.82" />
        <stop offset="45%" stop-color="#0f172a" stop-opacity="0.88" />
        <stop offset="100%" stop-color="#090d16" stop-opacity="0.95" />
      </linearGradient>

      <linearGradient id="shell-stroke" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#93c5fd" stop-opacity="0.4" />
        <stop offset="50%" stop-color="#38bdf8" stop-opacity="0.15" />
        <stop offset="100%" stop-color="#8b5cf6" stop-opacity="0.3" />
      </linearGradient>

      <linearGradient id="button-cap-grad" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stop-color="#334155" stop-opacity="0.9" />
        <stop offset="100%" stop-color="#1e293b" stop-opacity="0.95" />
      </linearGradient>
    </defs>
  </svg>
</template>

<style scoped>
.metaball-defs-svg {
  position: absolute;
  width: 0;
  height: 0;
  pointer-events: none;
  opacity: 0;
}
</style>

