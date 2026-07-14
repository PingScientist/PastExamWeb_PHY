<template>
  <section class="user-duration-card" aria-labelledby="user-duration-title">
    <div class="user-duration-heading">
      <div>
        <h3 id="user-duration-title">在線時長統計</h3>
        <p>{{ description }}</p>
      </div>
      <div class="user-duration-switch" role="group" aria-label="切換在線時長統計模式">
        <button
          type="button"
          :class="{ 'is-active': mode === 'hourly' }"
          :aria-pressed="mode === 'hourly'"
          @click="setMode('hourly')"
        >
          當日在線時長紀錄
        </button>
        <button
          type="button"
          :class="{ 'is-active': mode === 'daily' }"
          :aria-pressed="mode === 'daily'"
          @click="setMode('daily')"
        >
          每日在線時長紀錄
        </button>
      </div>
    </div>

    <div class="user-duration-controls">
      <Select
        v-if="mode === 'hourly'"
        v-model="selectedDate"
        :options="recentDateOptions"
        optionLabel="label"
        optionValue="value"
        aria-label="選擇最近七日日期"
        class="user-duration-date-select"
        @change="loadDuration"
      />
      <div v-else class="user-duration-range" role="group" aria-label="每日在線時長範圍">
        <button
          v-for="option in DAILY_OPTIONS"
          :key="option"
          type="button"
          :class="{ 'is-active': days === option }"
          :aria-pressed="days === option"
          @click="setDays(option)"
        >
          {{ option }} 日
        </button>
      </div>
      <span class="user-duration-timezone">統計時區：UTC</span>
    </div>

    <div v-if="loading" class="user-duration-state" role="status">
      <ProgressSpinner strokeWidth="4" />
      <span>載入在線時長紀錄…</span>
    </div>
    <Message v-else-if="error" severity="error" :closable="false">
      <div class="user-duration-error">
        <span>{{ error }}</span>
        <Button label="重新載入" icon="pi pi-refresh" size="small" outlined @click="loadDuration" />
      </div>
    </Message>
    <div v-else-if="!durationData?.history_started_at" class="user-duration-state" role="status">
      在線歷史資料自功能啟用後開始累積，目前尚無紀錄。
    </div>
    <div v-else-if="!hasAvailableHistory" class="user-duration-state" role="status">
      此日期範圍尚無在線時長紀錄。
    </div>
    <div v-else class="user-duration-chart" role="img" :aria-label="chartAriaLabel">
      <div class="user-duration-chart__y-axis" aria-hidden="true">
        <span v-for="tick in chartData.yTicks" :key="`duration-y-${tick}`">
          {{ formatAxisTick(tick) }}
        </span>
      </div>
      <div class="user-duration-chart__plot">
        <div class="user-duration-chart__grid" aria-hidden="true">
          <span
            v-for="tick in chartData.yTicks"
            :key="`duration-grid-${tick}`"
            :style="{ bottom: `${(tick / chartData.yMax) * 100}%` }"
          ></span>
        </div>
        <div
          class="user-duration-chart__bars"
          :style="{ '--duration-chart-columns': chartData.buckets.length }"
        >
          <div
            v-for="bucket in chartData.buckets"
            :key="bucket.start"
            class="user-duration-chart__item"
            tabindex="0"
            :aria-label="`${bucket.fullLabel}，在線時長 ${formatDuration(bucket.duration_seconds)}`"
          >
            <span
              class="user-duration-chart__bar"
              :class="{ 'has-value': bucket.duration_seconds > 0 }"
              :style="{ height: `${(bucket.duration_seconds / chartData.yMax) * 100}%` }"
            ></span>
            <span class="user-duration-chart__tooltip" role="tooltip">
              <strong>{{ bucket.fullLabel }}</strong>
              <span>在線時長：{{ formatDuration(bucket.duration_seconds) }}</span>
            </span>
          </div>
        </div>
        <div
          class="user-duration-chart__x-axis"
          :style="{ '--duration-chart-columns': chartData.buckets.length }"
          aria-hidden="true"
        >
          <span v-for="bucket in chartData.buckets" :key="`duration-label-${bucket.start}`">
            {{ bucket.showLabel ? bucket.label : '' }}
          </span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { getUserOnlineDuration } from '../api'

const props = defineProps({
  userId: { type: Number, default: null },
  active: { type: Boolean, default: false },
})

const DAILY_OPTIONS = [7, 30, 90]
const mode = ref('hourly')
const days = ref(7)
const selectedDate = ref(new Date().toISOString().slice(0, 10))
const durationData = ref(null)
const loading = ref(false)
const error = ref('')
let requestController = null

const recentDateOptions = computed(() => {
  const today = new Date()
  return Array.from({ length: 7 }, (_, index) => {
    const date = new Date(Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), today.getUTCDate()))
    date.setUTCDate(date.getUTCDate() - index)
    const value = date.toISOString().slice(0, 10)
    return {
      value,
      label: new Intl.DateTimeFormat('zh-TW', {
        timeZone: 'UTC',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
      }).format(date),
    }
  })
})

const description = computed(() =>
  mode.value === 'hourly'
    ? `顯示 ${recentDateOptions.value.find(({ value }) => value === selectedDate.value)?.label || selectedDate.value} 每小時的在線使用時長。`
    : `顯示最近 ${days.value} 個日曆日的每日在線使用時長。`
)

const formatDuration = (value) => {
  const totalSeconds = Math.max(0, Math.round(Number(value) || 0))
  if (totalSeconds === 0) return '0 秒'
  const hours = Math.floor(totalSeconds / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  const seconds = totalSeconds % 60
  const parts = []
  if (hours) parts.push(`${hours} 小時`)
  if (minutes) parts.push(`${minutes} 分鐘`)
  if (!hours && !minutes && seconds) parts.push(`${seconds} 秒`)
  return parts.join(' ')
}

const formatUtcDate = (value, includeYear = false) =>
  new Intl.DateTimeFormat('zh-TW', {
    timeZone: 'UTC',
    ...(includeYear ? { year: 'numeric' } : {}),
    month: '2-digit',
    day: '2-digit',
  }).format(new Date(value))

const chartData = computed(() => {
  const points = Array.isArray(durationData.value?.points) ? durationData.value.points : []
  const maxDuration = Math.max(0, ...points.map(({ duration_seconds }) => duration_seconds))
  const yMax =
    mode.value === 'hourly'
      ? 3600
      : Math.min(86400, Math.max(3600, Math.ceil(maxDuration / 3600) * 3600))
  const yTicks = Array.from({ length: 5 }, (_, index) => Math.round(yMax * (1 - index / 4)))
  const labelEvery = mode.value === 'hourly' ? 3 : days.value === 7 ? 1 : days.value === 30 ? 5 : 15
  const buckets = points.map((point, index) => {
    const start = new Date(point.start)
    const hour = String(start.getUTCHours()).padStart(2, '0')
    const endHour = String(start.getUTCHours() + 1).padStart(2, '0')
    return {
      ...point,
      label: mode.value === 'hourly' ? `${hour} 時` : formatUtcDate(start),
      fullLabel:
        mode.value === 'hourly'
          ? `${formatUtcDate(start, true)} ${hour}:00–${endHour}:00`
          : formatUtcDate(start, true),
      showLabel: index === 0 || index === points.length - 1 || index % labelEvery === 0,
    }
  })
  return { buckets, yMax, yTicks }
})

const hasAvailableHistory = computed(() => chartData.value.buckets.some(({ has_data }) => has_data))
const chartAriaLabel = computed(() =>
  mode.value === 'hourly'
    ? `${selectedDate.value} 的二十四小時在線時長分布`
    : `最近 ${days.value} 日的每日在線時長分布`
)
const formatAxisTick = (seconds) =>
  mode.value === 'hourly' ? `${Math.round(seconds / 60)} 分` : `${Math.round(seconds / 3600)} 時`

const validateResponse = (data) => {
  const expectedCount = mode.value === 'hourly' ? 24 : days.value
  return (
    data?.user_id === props.userId &&
    data?.mode === mode.value &&
    data?.timezone === 'UTC' &&
    Number.isInteger(data?.online_timeout_seconds) &&
    Array.isArray(data?.points) &&
    data.points.length === expectedCount &&
    data.points.every(
      (point) =>
        point?.start &&
        point?.end &&
        Number.isInteger(point?.duration_seconds) &&
        point.duration_seconds >= 0 &&
        typeof point.has_data === 'boolean'
    )
  )
}

const loadDuration = async () => {
  if (!props.active || !props.userId) return
  requestController?.abort()
  const controller = new AbortController()
  requestController = controller
  loading.value = true
  error.value = ''
  try {
    const { data } = await getUserOnlineDuration(props.userId, {
      mode: mode.value,
      date: selectedDate.value,
      days: days.value,
      signal: controller.signal,
    })
    if (requestController !== controller) return
    if (!validateResponse(data)) throw new TypeError('Invalid user online duration response')
    durationData.value = data
  } catch (requestError) {
    if (requestError?.code === 'ERR_CANCELED' || requestController !== controller) return
    durationData.value = null
    error.value = '在線時長載入失敗，請稍後再試。'
  } finally {
    if (requestController === controller) {
      loading.value = false
      requestController = null
    }
  }
}

const setMode = (value) => {
  if (mode.value === value) return
  mode.value = value
  void loadDuration()
}
const setDays = (value) => {
  if (days.value === value) return
  days.value = value
  void loadDuration()
}

watch(
  () => [props.userId, props.active],
  ([userId, active]) => {
    if (userId && active) void loadDuration()
    if (!active) requestController?.abort()
  },
  { immediate: true }
)

onBeforeUnmount(() => requestController?.abort())
</script>

<style scoped>
.user-duration-card {
  display: grid;
  gap: 0.75rem;
  min-width: 0;
  padding: 0.85rem;
  border: 1px solid var(--border-color);
  border-radius: 9px;
  background: var(--bg-secondary);
  color: var(--text-color);
}

.user-duration-heading,
.user-duration-controls,
.user-duration-switch,
.user-duration-range,
.user-duration-error {
  display: flex;
  align-items: center;
}

.user-duration-heading {
  justify-content: space-between;
  gap: 0.65rem 1rem;
}

.user-duration-heading h3,
.user-duration-heading p {
  margin: 0;
}

.user-duration-heading h3 {
  font-size: var(--app-font-size-base);
}

.user-duration-heading p,
.user-duration-timezone {
  margin-top: 0.15rem;
  color: var(--text-secondary);
  font-size: var(--app-font-size-xs);
  line-height: 1.4;
}

.user-duration-switch,
.user-duration-range {
  flex-wrap: wrap;
  gap: 0.25rem;
  padding: 0.2rem;
  border: 1px solid var(--border-color);
  border-radius: 7px;
  background: var(--bg-primary);
}

.user-duration-switch button,
.user-duration-range button {
  min-height: 2.35rem;
  padding: 0.38rem 0.62rem;
  border: 1px solid transparent;
  border-radius: 5px;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font: inherit;
  font-size: var(--app-font-size-xs);
  font-weight: 700;
}

.user-duration-switch button.is-active,
.user-duration-range button.is-active {
  border-color: color-mix(in srgb, var(--primary-color) 42%, var(--border-color));
  background: color-mix(in srgb, var(--primary-color) 12%, var(--bg-primary));
  color: var(--text-color);
}

.user-duration-switch button:focus-visible,
.user-duration-range button:focus-visible {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}

.user-duration-controls {
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.5rem 0.75rem;
}

.user-duration-date-select {
  width: min(100%, 14rem);
}

.user-duration-state {
  display: flex;
  min-height: 8rem;
  align-items: center;
  justify-content: center;
  gap: 0.65rem;
  padding: 1rem;
  border: 1px dashed var(--border-color);
  border-radius: 7px;
  color: var(--text-secondary);
  font-size: var(--app-font-size-sm);
  text-align: center;
}

.user-duration-state :deep(.p-progressspinner) {
  width: 2rem;
  height: 2rem;
}

.user-duration-error {
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.5rem 1rem;
}

.user-duration-chart {
  display: grid;
  grid-template-columns: 3.5rem minmax(0, 1fr);
  gap: 0.5rem;
  min-width: 0;
  height: clamp(13rem, 34vw, 18rem);
  padding-top: 0.35rem;
  font-size: var(--app-font-size-xs);
}

.user-duration-chart__y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: calc(100% - 2rem);
  color: var(--text-secondary);
  text-align: right;
}

.user-duration-chart__plot {
  position: relative;
  min-width: 0;
  height: 100%;
  border-left: 1px solid var(--border-color);
  border-bottom: 1px solid var(--border-color);
}

.user-duration-chart__grid,
.user-duration-chart__bars {
  position: absolute;
  inset: 0 0 2rem;
}

.user-duration-chart__grid span {
  position: absolute;
  right: 0;
  left: 0;
  border-top: 1px solid color-mix(in srgb, var(--border-color) 70%, transparent);
}

.user-duration-chart__bars,
.user-duration-chart__x-axis {
  display: grid;
  grid-template-columns: repeat(var(--duration-chart-columns), minmax(0, 1fr));
}

.user-duration-chart__bars {
  z-index: 1;
  align-items: end;
  gap: clamp(1px, 0.25vw, 3px);
  padding-inline: 2px;
}

.user-duration-chart__item {
  position: relative;
  display: flex;
  min-width: 0;
  height: 100%;
  align-items: flex-end;
  justify-content: center;
  outline: none;
}

.user-duration-chart__bar {
  display: block;
  width: 100%;
  min-height: 0;
  border-radius: 4px 4px 1px 1px;
}

.user-duration-chart__bar.has-value {
  background: var(--primary-color);
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--primary-color) 60%, transparent);
}

.user-duration-chart__tooltip {
  position: absolute;
  z-index: 4;
  bottom: calc(100% + 0.35rem);
  left: 50%;
  display: none;
  width: max-content;
  max-width: min(20rem, calc(100vw - 3rem));
  padding: 0.4rem 0.55rem;
  border: 1px solid var(--border-color);
  border-radius: 5px;
  background: var(--bg-primary);
  color: var(--text-color);
  font-size: var(--app-font-size-xs);
  line-height: 1.4;
  overflow-wrap: anywhere;
  transform: translateX(-50%);
}

.user-duration-chart__tooltip strong,
.user-duration-chart__tooltip span {
  display: block;
}

.user-duration-chart__item:hover,
.user-duration-chart__item:focus-visible {
  z-index: 3;
}

.user-duration-chart__item:hover .user-duration-chart__tooltip,
.user-duration-chart__item:focus-visible .user-duration-chart__tooltip {
  display: block;
}

.user-duration-chart__item:first-child .user-duration-chart__tooltip {
  left: 0;
  transform: none;
}

.user-duration-chart__item:last-child .user-duration-chart__tooltip {
  right: 0;
  left: auto;
  transform: none;
}

.user-duration-chart__item:focus-visible {
  box-shadow: inset 0 0 0 2px var(--primary-color);
}

.user-duration-chart__x-axis {
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  height: 1.9rem;
  align-items: start;
  gap: 1px;
  padding-top: 0.35rem;
  color: var(--text-secondary);
  text-align: center;
}

.user-duration-chart__x-axis span {
  min-width: 0;
  font-size: var(--app-font-size-xs);
  line-height: 1.1;
  white-space: nowrap;
}

.user-duration-chart__x-axis span:first-child {
  text-align: left;
}

.user-duration-chart__x-axis span:last-child {
  text-align: right;
}

@media (max-width: 640px) {
  .user-duration-heading {
    align-items: stretch;
    flex-direction: column;
  }

  .user-duration-switch {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .user-duration-chart {
    grid-template-columns: 2.75rem minmax(0, 1fr);
    height: 14rem;
  }
}
</style>
