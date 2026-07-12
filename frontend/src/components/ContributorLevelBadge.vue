<template>
  <span
    v-if="validLevel"
    class="contributor-level"
    :class="[`contributor-level--${size}`, `contributor-level--tier-${colorTier}`]"
    :aria-label="accessibleLabel"
    :title="title || undefined"
  >
    <span class="contributor-level__badge">Lv. {{ validLevel }}</span>
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
const accessibleLabel = computed(() =>
  props.title
    ? `投稿者等級 Lv. ${validLevel.value} ${props.title}`
    : `投稿者等級 Lv. ${validLevel.value}`
)
</script>

<style scoped>
.contributor-level {
  --level-badge-bg: #8b5e3c;
  --level-badge-fg: #ffffff;
  --level-badge-border: #68442b;

  display: inline-flex;
  min-width: 0;
  align-items: center;
  gap: 0.45rem;
  vertical-align: middle;
}

.contributor-level__badge {
  display: inline-flex;
  flex: 0 0 auto;
  align-items: center;
  justify-content: center;
  padding: 0.2rem 0.52rem;
  border: 1px solid var(--level-badge-border);
  border-radius: 999px;
  background: var(--level-badge-bg);
  box-shadow: 0 1px 2px color-mix(in srgb, var(--level-badge-border) 55%, transparent);
  color: var(--level-badge-fg);
  font-size: 0.78rem;
  font-weight: 800;
  line-height: 1.1;
  white-space: nowrap;
}

.contributor-level__title {
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
  padding: 0.12rem 0.4rem;
  font-size: 0.68rem;
  line-height: 1rem;
}

.contributor-level--tier-2 {
  --level-badge-bg: #64748b;
  --level-badge-border: #475569;
}

.contributor-level--tier-3 {
  --level-badge-bg: #3f6f8f;
  --level-badge-border: #2d526b;
}

.contributor-level--tier-4 {
  --level-badge-bg: #0f766e;
  --level-badge-border: #0b5954;
}

.contributor-level--tier-5 {
  --level-badge-bg: #946200;
  --level-badge-border: #704900;
}

.contributor-level--tier-6 {
  --level-badge-bg: #2f855a;
  --level-badge-border: #226342;
}

.contributor-level--tier-7 {
  --level-badge-bg: #047857;
  --level-badge-border: #065f46;
}

.contributor-level--tier-8 {
  --level-badge-bg: #4338ca;
  --level-badge-border: #312e81;
}

.contributor-level--tier-9 {
  --level-badge-bg: #6d28d9;
  --level-badge-border: #4c1d95;
}

.contributor-level--tier-10 {
  --level-badge-bg: #075985;
  --level-badge-border: #0c4a6e;
}
</style>
