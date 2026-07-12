<template>
  <span
    v-if="validLevel"
    class="contributor-level"
    :class="[`contributor-level--${size}`, `contributor-level--tier-${colorTier}`]"
    :aria-label="accessibleLabel"
    :title="title || undefined"
  >
    <span class="contributor-level__badge">
      <span class="contributor-level__ornament" aria-hidden="true">{{ emblemMark }}</span>
      <span class="contributor-level__label">Lv. {{ validLevel }}</span>
    </span>
    <span v-if="showTitle && title" class="contributor-level__title">{{ title }}</span>
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  level: {
    type: [Number, String],
    default: null,
  },
  title: {
    type: String,
    default: '',
  },
  size: {
    type: String,
    default: 'regular',
    validator: (value) => ['compact', 'regular'].includes(value),
  },
  showTitle: {
    type: Boolean,
    default: false,
  },
})

const validLevel = computed(() => {
  const level = Number(props.level)
  return Number.isInteger(level) && level > 0 ? level : null
})

const colorTier = computed(() => Math.min(validLevel.value || 1, 10))
const emblemMark = computed(() => {
  if (colorTier.value >= 10) return '✦'
  if (colorTier.value >= 7) return '★'
  if (colorTier.value >= 4) return '◆'
  return '•'
})
const accessibleLabel = computed(() =>
  props.title
    ? `投稿者等級 Lv. ${validLevel.value} ${props.title}`
    : `投稿者等級 Lv. ${validLevel.value}`
)
</script>

<style scoped>
.contributor-level {
  --level-badge-bg: #8f4f32;
  --level-badge-fg: #ffffff;
  --level-badge-border: #5e2f1d;
  --level-badge-accent: #f3c6a8;

  display: inline-flex;
  min-width: 0;
  align-items: center;
  gap: 0.45rem;
  vertical-align: middle;
}

.contributor-level__badge {
  position: relative;
  display: inline-flex;
  flex: 0 0 auto;
  align-items: center;
  justify-content: center;
  gap: 0.22rem;
  min-width: 4.15rem;
  padding: 0.28rem 0.65rem;
  border: 0;
  clip-path: polygon(10% 0, 90% 0, 100% 50%, 90% 100%, 10% 100%, 0 50%);
  background: var(--level-badge-bg);
  box-shadow:
    inset 0 0 0 1px var(--level-badge-border),
    inset 0 2px 0 color-mix(in srgb, var(--level-badge-accent) 45%, transparent),
    0 2px 4px color-mix(in srgb, var(--level-badge-border) 52%, transparent);
  color: var(--level-badge-fg);
  font-size: 0.78rem;
  font-weight: 800;
  line-height: 1.1;
  white-space: nowrap;
}

.contributor-level__badge::after {
  position: absolute;
  inset: 3px;
  border: 1px solid color-mix(in srgb, var(--level-badge-accent) 62%, transparent);
  clip-path: inherit;
  content: '';
  pointer-events: none;
}

.contributor-level__ornament {
  color: var(--level-badge-accent);
  font-size: 0.62em;
  line-height: 1;
}

.contributor-level__label {
  position: relative;
  z-index: 1;
  white-space: nowrap;
}

.contributor-level__title {
  padding: 0.16rem 0.48rem 0.16rem 0.42rem;
  border-left: 2px solid var(--level-badge-bg);
  background: color-mix(in srgb, var(--level-badge-bg) 12%, var(--bg-secondary));
  clip-path: polygon(0 0, calc(100% - 0.35rem) 0, 100% 50%, calc(100% - 0.35rem) 100%, 0 100%);
  min-width: 0;
  color: var(--text-color);
  font-size: 1rem;
  font-weight: 700;
  overflow-wrap: anywhere;
}

.contributor-level--compact {
  gap: 0.3rem;
}

.contributor-level--compact .contributor-level__badge {
  min-width: 3.5rem;
  padding: 0.18rem 0.5rem;
  font-size: 0.68rem;
  line-height: 1rem;
}

.contributor-level--compact .contributor-level__title {
  padding-block: 0.08rem;
  font-size: 0.72rem;
}

.contributor-level--tier-2 {
  --level-badge-bg: #64748b;
  --level-badge-border: #475569;
  --level-badge-accent: #e2e8f0;
}

.contributor-level--tier-3 {
  --level-badge-bg: #3f6f8f;
  --level-badge-border: #2d526b;
  --level-badge-accent: #d5eefc;
}

.contributor-level--tier-4 {
  --level-badge-bg: #0f766e;
  --level-badge-border: #064e49;
  --level-badge-accent: #99f6e4;
}

.contributor-level--tier-5 {
  --level-badge-bg: #946200;
  --level-badge-border: #704900;
  --level-badge-accent: #fde68a;
}

.contributor-level--tier-6 {
  --level-badge-bg: #2f855a;
  --level-badge-border: #226342;
  --level-badge-accent: #bbf7d0;
}

.contributor-level--tier-7 {
  --level-badge-bg: #1d4ed8;
  --level-badge-border: #1e3a8a;
  --level-badge-accent: #bfdbfe;
}

.contributor-level--tier-8 {
  --level-badge-bg: #4338ca;
  --level-badge-border: #312e81;
  --level-badge-accent: #c7d2fe;
}

.contributor-level--tier-9 {
  --level-badge-bg: #6d28d9;
  --level-badge-border: #4c1d95;
  --level-badge-accent: #e9d5ff;
}

.contributor-level--tier-10 {
  --level-badge-bg: #9a6700;
  --level-badge-border: #5f3d00;
  --level-badge-accent: #fff4b8;
}
</style>
