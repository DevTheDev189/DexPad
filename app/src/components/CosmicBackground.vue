<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  spotlight?: { x: number; y: number; active: boolean; color?: string } | null;
}>();

// Generate deterministic starfield items
const starsLayer1 = Array.from({ length: 45 }, (_, i) => ({
  id: `s1-${i}`,
  top: `${((i * 19) % 97) + 1.5}%`,
  left: `${((i * 23) % 96) + 2}%`,
  size: (i % 3 === 0) ? '3px' : '1.5px',
  duration: `${3 + (i % 4) * 1.5}s`,
  delay: `${(i % 5) * 0.7}s`,
  opacity: 0.3 + (i % 5) * 0.15,
}));

const starsLayer2 = Array.from({ length: 35 }, (_, i) => ({
  id: `s2-${i}`,
  top: `${((i * 31) % 95) + 2.5}%`,
  left: `${((i * 17) % 98) + 1}%`,
  size: (i % 4 === 0) ? '3.5px' : '2px',
  duration: `${4 + (i % 3) * 2}s`,
  delay: `${(i % 4) * 0.9}s`,
  opacity: 0.4 + (i % 4) * 0.15,
}));

const spotlightStyle = computed(() => {
  if (!props.spotlight || !props.spotlight.active) {
    return {
      transform: 'translate3d(50vw, 50vh, 0) translate(-50%, -50%)',
      opacity: 0.45,
      background: 'radial-gradient(circle, rgba(59, 130, 246, 0.45) 0%, rgba(99, 102, 241, 0.3) 45%, rgba(139, 92, 246, 0.15) 75%, transparent 100%)',
    };
  }

  const { x, y, color } = props.spotlight;
  let bgGradient = 'radial-gradient(circle, rgba(56, 189, 248, 0.6) 0%, rgba(99, 102, 241, 0.4) 45%, rgba(139, 92, 246, 0.2) 75%, transparent 100%)';
  if (color === 'violet') {
    bgGradient = 'radial-gradient(circle, rgba(192, 132, 252, 0.65) 0%, rgba(139, 92, 246, 0.45) 50%, rgba(59, 130, 246, 0.15) 80%, transparent 100%)';
  } else if (color === 'cyan') {
    bgGradient = 'radial-gradient(circle, rgba(56, 189, 248, 0.75) 0%, rgba(59, 130, 246, 0.4) 50%, rgba(99, 102, 241, 0.2) 80%, transparent 100%)';
  }

  return {
    transform: `translate3d(${x}px, ${y}px, 0) translate(-50%, -50%)`,
    opacity: 0.85,
    background: bgGradient,
  };
});
</script>

<template>
  <div class="cosmic-canvas" aria-hidden="true">
    <!-- Deep Space Background Gradients -->
    <div class="space-vignette"></div>

    <!-- Static Nebula Clouds -->
    <div class="nebula-cloud nebula-top-left"></div>
    <div class="nebula-cloud nebula-bottom-right"></div>
    <div class="nebula-cloud nebula-center"></div>

    <!-- Starfield Layers -->
    <div class="star-layer layer-1">
      <div
        v-for="s in starsLayer1"
        :key="s.id"
        class="star"
        :style="{
          top: s.top,
          left: s.left,
          width: s.size,
          height: s.size,
          animationDuration: s.duration,
          animationDelay: s.delay,
          opacity: s.opacity,
        }"
      />
    </div>

    <div class="star-layer layer-2">
      <div
        v-for="s in starsLayer2"
        :key="s.id"
        class="star star-cross"
        :style="{
          top: s.top,
          left: s.left,
          width: s.size,
          height: s.size,
          animationDuration: s.duration,
          animationDelay: s.delay,
          opacity: s.opacity,
        }"
      />
    </div>

    <!-- Dynamic Reactive Spotlight Orb -->
    <div class="spotlight-orb" :style="spotlightStyle"></div>
  </div>
</template>

<style scoped>
.cosmic-canvas {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  z-index: 0;
  background-color: var(--bg-void);
}

.space-vignette {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 50% 45%, #0d1224 0%, #060914 55%, #030408 100%);
}

.nebula-cloud {
  position: absolute;
  border-radius: 50%;
  filter: blur(110px);
  opacity: 0.38;
  animation: floatNebula 24s ease-in-out infinite alternate;
  will-change: transform;
}

.nebula-top-left {
  width: 580px;
  height: 580px;
  top: -120px;
  left: -100px;
  background: radial-gradient(circle, #1e1b4b 0%, #0f172a 60%, transparent 80%);
}

.nebula-bottom-right {
  width: 640px;
  height: 640px;
  bottom: -150px;
  right: -100px;
  background: radial-gradient(circle, #2e1065 0%, #1e1b4b 50%, transparent 80%);
  animation-duration: 30s;
  animation-delay: -8s;
}

.nebula-center {
  width: 520px;
  height: 440px;
  top: 35%;
  left: 30%;
  background: radial-gradient(circle, rgba(56, 189, 248, 0.12) 0%, rgba(99, 102, 241, 0.15) 50%, transparent 80%);
  animation-duration: 26s;
  animation-delay: -14s;
}

/* Stars */
.star-layer {
  position: absolute;
  inset: 0;
}

.star {
  position: absolute;
  background-color: #ffffff;
  border-radius: 50%;
  box-shadow: 0 0 6px rgba(255, 255, 255, 0.8), 0 0 12px rgba(56, 189, 248, 0.4);
  animation: twinkle ease-in-out infinite;
  will-change: opacity, transform;
}

.star-cross {
  box-shadow: 0 0 8px rgba(192, 132, 252, 0.9), 0 0 16px rgba(139, 92, 246, 0.5);
}

/* Dynamic Reactive Spotlight */
.spotlight-orb {
  position: absolute;
  top: 0;
  left: 0;
  width: 500px;
  height: 500px;
  border-radius: 50%;
  filter: blur(95px);
  pointer-events: none;
  transition: transform 0.65s cubic-bezier(0.16, 1, 0.3, 1), background 0.75s ease, opacity 0.5s ease;
  will-change: transform, opacity;
  z-index: 1;
}
</style>
