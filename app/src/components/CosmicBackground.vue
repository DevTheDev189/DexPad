<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  spotlight?: { x: number; y: number; active: boolean; color?: string } | null;
}>();

// Deterministic starfield with varied depths and colors
const starsLayer1 = Array.from({ length: 65 }, (_, i) => ({
  id: `s1-${i}`,
  top: `${((i * 17) % 96) + 2}%`,
  left: `${((i * 29) % 96) + 2}%`,
  size: (i % 5 === 0) ? '3.5px' : (i % 2 === 0 ? '2px' : '1px'),
  color: (i % 3 === 0) ? '#38bdf8' : (i % 4 === 0 ? '#c084fc' : '#ffffff'),
  duration: `${2.8 + (i % 5) * 1.2}s`,
  delay: `${(i % 7) * 0.6}s`,
  opacity: 0.35 + (i % 6) * 0.12,
}));

const starsLayer2 = Array.from({ length: 45 }, (_, i) => ({
  id: `s2-${i}`,
  top: `${((i * 23) % 94) + 3}%`,
  left: `${((i * 37) % 96) + 2}%`,
  size: (i % 4 === 0) ? '4px' : '2px',
  color: (i % 2 === 0) ? '#93c5fd' : '#e0e7ff',
  duration: `${4 + (i % 4) * 1.5}s`,
  delay: `${(i % 5) * 0.8}s`,
  opacity: 0.45 + (i % 4) * 0.15,
}));

// Floating cosmic dust specks
const cosmicDust = Array.from({ length: 24 }, (_, i) => ({
  id: `dust-${i}`,
  top: `${((i * 31) % 92) + 4}%`,
  left: `${((i * 41) % 94) + 3}%`,
  size: `${12 + (i % 5) * 8}px`,
  duration: `${18 + (i % 4) * 6}s`,
  delay: `${(i % 6) * -3}s`,
}));

const spotlightStyle = computed(() => {
  if (!props.spotlight || !props.spotlight.active) {
    return {
      transform: 'translate3d(45vw, 48vh, 0) translate(-50%, -50%)',
      opacity: 0.45,
      background: 'radial-gradient(circle, rgba(56, 189, 248, 0.4) 0%, rgba(99, 102, 241, 0.28) 40%, rgba(139, 92, 246, 0.12) 70%, transparent 100%)',
    };
  }

  const { x, y, color } = props.spotlight;
  let bgGradient = 'radial-gradient(circle, rgba(56, 189, 248, 0.65) 0%, rgba(99, 102, 241, 0.45) 45%, rgba(139, 92, 246, 0.2) 75%, transparent 100%)';
  if (color === 'violet') {
    bgGradient = 'radial-gradient(circle, rgba(192, 132, 252, 0.7) 0%, rgba(139, 92, 246, 0.5) 48%, rgba(59, 130, 246, 0.18) 78%, transparent 100%)';
  } else if (color === 'cyan') {
    bgGradient = 'radial-gradient(circle, rgba(56, 189, 248, 0.8) 0%, rgba(59, 130, 246, 0.45) 48%, rgba(99, 102, 241, 0.2) 78%, transparent 100%)';
  }

  return {
    transform: `translate3d(${x}px, ${y}px, 0) translate(-50%, -50%)`,
    opacity: 0.9,
    background: bgGradient,
  };
});
</script>

<template>
  <div class="cosmic-canvas" aria-hidden="true">
    <!-- Deep Spatial Vignette -->
    <div class="space-vignette"></div>

    <!-- Perspective Celestial Horizon Grid -->
    <div class="celestial-grid"></div>

    <!-- Fluid Aurora Nebula Clouds -->
    <div class="nebula-cloud nebula-cyan"></div>
    <div class="nebula-cloud nebula-violet"></div>
    <div class="nebula-cloud nebula-magenta"></div>
    <div class="nebula-cloud nebula-core"></div>

    <!-- Cosmic Dust Layer -->
    <div class="dust-layer">
      <div
        v-for="d in cosmicDust"
        :key="d.id"
        class="dust-particle"
        :style="{
          top: d.top,
          left: d.left,
          width: d.size,
          height: d.size,
          animationDuration: d.duration,
          animationDelay: d.delay,
        }"
      />
    </div>

    <!-- Starfield Layer 1 -->
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
          backgroundColor: s.color,
          animationDuration: s.duration,
          animationDelay: s.delay,
          opacity: s.opacity,
        }"
      />
    </div>

    <!-- Starfield Layer 2 with Cross Glow -->
    <div class="star-layer layer-2">
      <div
        v-for="s in starsLayer2"
        :key="s.id"
        class="star star-radiant"
        :style="{
          top: s.top,
          left: s.left,
          width: s.size,
          height: s.size,
          backgroundColor: s.color,
          animationDuration: s.duration,
          animationDelay: s.delay,
          opacity: s.opacity,
        }"
      />
    </div>

    <!-- Interactive Reactive Spotlight Orb -->
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
  background: 
    radial-gradient(circle at 45% 40%, rgba(15, 23, 42, 0.4) 0%, transparent 60%),
    radial-gradient(circle at 50% 50%, #080d1e 0%, #04060d 60%, #020306 100%);
}

/* Subtle Perspective Grid */
.celestial-grid {
  position: absolute;
  inset: 0;
  background-image: 
    linear-gradient(to right, rgba(147, 197, 253, 0.035) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(147, 197, 253, 0.035) 1px, transparent 1px);
  background-size: 80px 80px;
  mask-image: radial-gradient(circle at 50% 50%, black 20%, transparent 75%);
  -webkit-mask-image: radial-gradient(circle at 50% 50%, black 20%, transparent 75%);
  opacity: 0.65;
}

/* Aurora & Fluid Nebula Clouds */
.nebula-cloud {
  position: absolute;
  border-radius: 50%;
  filter: blur(120px);
  will-change: transform;
  animation: floatNebulaSmooth 26s ease-in-out infinite alternate;
}

.nebula-cyan {
  width: 650px;
  height: 650px;
  top: -120px;
  left: -80px;
  background: radial-gradient(circle, rgba(56, 189, 248, 0.28) 0%, rgba(59, 130, 246, 0.18) 45%, transparent 75%);
}

.nebula-violet {
  width: 720px;
  height: 720px;
  bottom: -160px;
  right: -100px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.3) 0%, rgba(99, 102, 241, 0.18) 50%, transparent 78%);
  animation-duration: 32s;
  animation-delay: -10s;
}

.nebula-magenta {
  width: 540px;
  height: 540px;
  top: 15%;
  right: 15%;
  background: radial-gradient(circle, rgba(192, 132, 252, 0.22) 0%, rgba(139, 92, 246, 0.12) 50%, transparent 80%);
  animation-duration: 28s;
  animation-delay: -16s;
}

.nebula-core {
  width: 580px;
  height: 520px;
  top: 32%;
  left: 28%;
  background: radial-gradient(circle, rgba(56, 189, 248, 0.18) 0%, rgba(99, 102, 241, 0.15) 50%, transparent 80%);
  animation-duration: 24s;
  animation-delay: -8s;
}

/* Cosmic Dust */
.dust-layer {
  position: absolute;
  inset: 0;
}

.dust-particle {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(147, 197, 253, 0.22) 0%, transparent 70%);
  filter: blur(4px);
  animation: floatNebulaSmooth ease-in-out infinite alternate;
}

/* Stars */
.star-layer {
  position: absolute;
  inset: 0;
}

.star {
  position: absolute;
  border-radius: 50%;
  animation: twinkleSlow ease-in-out infinite;
  will-change: opacity, transform;
}

.star-radiant {
  box-shadow: 0 0 8px rgba(255, 255, 255, 0.9), 0 0 16px rgba(56, 189, 248, 0.5);
}

/* Reactive Spotlight */
.spotlight-orb {
  position: absolute;
  top: 0;
  left: 0;
  width: 520px;
  height: 520px;
  border-radius: 50%;
  filter: blur(105px);
  pointer-events: none;
  transition: transform 0.65s cubic-bezier(0.16, 1, 0.3, 1), background 0.75s ease, opacity 0.5s ease;
  will-change: transform, opacity;
  z-index: 1;
}
</style>
