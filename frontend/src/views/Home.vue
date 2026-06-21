<template>
  <main class="physics-home" :class="{ 'physics-home-dark': isDarkTheme }">
    <div class="physics-board" aria-hidden="true">
      <div class="building-accent">
        <span class="roof"></span>
        <span class="column column-one"></span>
        <span class="column column-two"></span>
        <span class="column column-three"></span>
        <span class="walkway"></span>
        <span class="vine vine-left"></span>
        <span class="vine vine-top"></span>
        <span class="vine vine-right"></span>
      </div>

      <div class="equation-card tensor-card">
        <span>R<sub>μν</sub> − 1/2 Rg<sub>μν</sub> = 8πGT<sub>μν</sub></span>
      </div>
      <div class="equation-card fourier-card">
        <span>F(ω) = ∫ f(t)e<sup>−iωt</sup> dt</span>
      </div>
      <div class="equation-card schrodinger-card">
        <span>iℏ ∂ψ/∂t = Ĥψ</span>
      </div>

      <svg class="feynman-diagram" viewBox="0 0 320 170">
        <path class="fermion" d="M22 28 L136 82 L22 142" />
        <path class="fermion" d="M298 28 L184 82 L298 142" />
        <path
          class="photon"
          d="M136 82 C146 58 164 58 174 82 C184 106 202 106 212 82"
        />
        <circle class="vertex" cx="136" cy="82" r="5" />
        <circle class="vertex" cx="212" cy="82" r="5" />
      </svg>

      <div class="orbit-hint orbit-a"></div>
      <div class="orbit-hint orbit-b"></div>
    </div>

    <section class="hero-shell">
      <div class="hero-copy">
        <p class="eyebrow">PHY Past Exam Archive</p>
        <h1>物理系考古題系統</h1>
        <p class="subtitle">
          整理課程、考題、解答與討論，把期中期末前最需要的資料集中在一個安靜好找的地方。
        </p>
        <div class="hero-actions">
          <Button
            icon="pi pi-sign-in"
            label="登入開始使用"
            size="large"
            @click="openLogin"
          />
          <Button
            icon="pi pi-search"
            label="查看資料庫狀態"
            size="large"
            severity="secondary"
            outlined
            @click="scrollToStats"
          />
        </div>
      </div>
    </section>

    <section ref="statsSection" class="dashboard-strip">
      <article
        v-for="(stat, index) in statistics"
        :key="stat.key"
        class="stat-card"
        :class="{ 'animate-fade-in': statsLoaded }"
        :style="{ animationDelay: `${index * 0.08}s` }"
      >
        <div class="stat-icon">
          <i :class="stat.icon"></i>
        </div>
        <div>
          <p>{{ stat.label }}</p>
          <strong>{{ animatedValues[stat.key] }}</strong>
        </div>
      </article>
    </section>
  </main>
</template>

<script setup>
defineOptions({
  name: 'HomeView',
})

import { ref, onMounted, computed } from 'vue'
import { useTheme } from '../utils/useTheme'
import { statisticsService } from '../api'

const { isDarkTheme } = useTheme()
const statsSection = ref(null)

const statisticsData = ref({
  totalUsers: 0,
  totalDownloads: 0,
  onlineUsers: 0,
  totalArchives: 0,
  totalCourses: 0,
  activeToday: 0,
})

const animatedValues = ref({
  totalUsers: 0,
  totalDownloads: 0,
  onlineUsers: 0,
  totalArchives: 0,
  totalCourses: 0,
  activeToday: 0,
})

const statsLoaded = ref(false)

const statistics = computed(() => [
  {
    key: 'totalArchives',
    label: '考古題',
    icon: 'pi pi-file-pdf',
  },
  {
    key: 'totalCourses',
    label: '課程',
    icon: 'pi pi-book',
  },
  {
    key: 'totalDownloads',
    label: '下載',
    icon: 'pi pi-download',
  },
  {
    key: 'totalUsers',
    label: '使用者',
    icon: 'pi pi-users',
  },
  {
    key: 'activeToday',
    label: '今日活躍',
    icon: 'pi pi-chart-line',
  },
  {
    key: 'onlineUsers',
    label: '在線',
    icon: 'pi pi-circle-fill',
  },
])

onMounted(async () => {
  await fetchStatistics()
})

function openLogin() {
  window.__pastexam?.openLoginModal?.()
}

function scrollToStats() {
  statsSection.value?.scrollIntoView({ behavior: 'smooth', block: 'center' })
}

async function fetchStatistics() {
  try {
    const response = await statisticsService.getSystemStatistics()

    if (response.data && response.data.data) {
      statisticsData.value = response.data.data
      animateCounters()
      statsLoaded.value = true
      return
    }

    throw new Error('Invalid API response format')
  } catch (error) {
    console.error('Error fetching statistics:', error)
    animatedValues.value = {
      totalUsers: '--',
      totalDownloads: '--',
      onlineUsers: '--',
      totalArchives: '--',
      totalCourses: '--',
      activeToday: '--',
    }
    statsLoaded.value = true
  }
}

function animateCounters() {
  Object.keys(statisticsData.value).forEach((key) => {
    animatedValues.value[key] = formatNumber(statisticsData.value[key])
  })
}

function formatNumber(num) {
  if (Number.isNaN(num) || num === null || num === undefined) {
    return '--'
  }
  return Number(num).toLocaleString('zh-TW')
}
</script>

<style scoped>
.physics-home {
  position: relative;
  min-height: 100%;
  overflow: hidden auto;
  color: var(--text-primary);
  background:
    radial-gradient(circle at 20% 16%, rgba(82, 128, 86, 0.1), transparent 28rem),
    linear-gradient(135deg, #f6faf5 0%, #eef4ef 58%, #f2f0e7 100%);
}

.physics-home-dark {
  background:
    radial-gradient(circle at 20% 16%, rgba(83, 150, 98, 0.12), transparent 34rem),
    linear-gradient(135deg, #101610 0%, #13201a 58%, #171b15 100%);
}

.hero-shell {
  min-height: calc(100vh - var(--navbar-height));
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  width: min(1180px, calc(100% - 2rem));
  margin: 0 auto;
  padding: clamp(2rem, 7vh, 5rem) 0;
}

.hero-copy {
  position: relative;
  z-index: 1;
  max-width: 54rem;
  padding: clamp(1rem, 2vw, 1.5rem) 0;
}

.eyebrow {
  margin: 0 0 0.95rem;
  color: #8fd8cb;
  font-size: 0.86rem;
  font-weight: 650;
  letter-spacing: 0;
  text-transform: uppercase;
}

.physics-home-dark .eyebrow {
  color: #9be0d4;
}

h1 {
  margin: 0;
  max-width: 54rem;
  font-size: clamp(2.75rem, 3.6vw, 4rem);
  font-weight: 560;
  line-height: 1.13;
  letter-spacing: 0;
}

.subtitle {
  max-width: 36rem;
  margin: 1.2rem 0 0;
  color: var(--text-secondary);
  font-size: clamp(0.98rem, 1.15vw, 1.08rem);
  line-height: 1.78;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 2rem;
}

.physics-board {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: calc(100vh - var(--navbar-height));
  min-height: 42rem;
  overflow: hidden;
  background:
    linear-gradient(rgba(236, 246, 232, 0.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(236, 246, 232, 0.035) 1px, transparent 1px),
    radial-gradient(circle at 23% 26%, rgba(99, 150, 96, 0.1), transparent 18rem),
    linear-gradient(135deg, rgba(16, 38, 30, 0.98), rgba(15, 27, 25, 0.96));
  background-size:
    34px 34px,
    34px 34px,
    auto,
    auto,
    auto;
  pointer-events: none;
  z-index: 0;
}

.physics-board::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    linear-gradient(120deg, transparent 0 42%, rgba(237, 242, 226, 0.035) 45%, transparent 49%),
    radial-gradient(circle at 18% 86%, rgba(92, 139, 83, 0.1), transparent 13rem);
  pointer-events: none;
}

.physics-board::after {
  content: '';
  position: absolute;
  inset: 0;
  background:
    linear-gradient(90deg, rgba(10, 23, 16, 0.2) 0%, rgba(10, 23, 16, 0.62) 24%, rgba(10, 23, 16, 0.2) 58%, rgba(10, 23, 16, 0.04) 100%),
    linear-gradient(0deg, rgba(10, 23, 16, 0.28), transparent 38%);
  pointer-events: none;
}

.building-accent {
  position: absolute;
  right: clamp(3rem, 7vw, 7rem);
  bottom: clamp(7rem, 13vh, 9.5rem);
  width: min(15vw, 12.5rem);
  height: min(12vw, 9.5rem);
  opacity: 0.2;
}

.roof,
.walkway,
.column {
  position: absolute;
  display: block;
  background: rgba(218, 216, 199, 0.36);
  box-shadow: inset 0 -3px 0 rgba(114, 112, 98, 0.16);
}

.roof {
  top: 0;
  left: 4%;
  width: 92%;
  height: 16%;
  border-radius: 0.35rem 0.35rem 0 0;
}

.walkway {
  left: 0;
  bottom: 0;
  width: 100%;
  height: 16%;
}

.column {
  top: 14%;
  width: 12%;
  height: 74%;
}

.column-one {
  left: 12%;
}

.column-two {
  left: 44%;
}

.column-three {
  left: 76%;
}

.vine {
  position: absolute;
  display: block;
  background: linear-gradient(180deg, rgba(99, 151, 74, 0.58), rgba(45, 101, 49, 0.58));
  border-radius: 999px;
  box-shadow: none;
}

.vine-left {
  left: 7%;
  top: 8%;
  width: 7%;
  height: 84%;
}

.vine-top {
  left: 6%;
  top: 2%;
  width: 88%;
  height: 9%;
  background: linear-gradient(90deg, rgba(45, 101, 49, 0.58), rgba(99, 151, 74, 0.58));
}

.vine-right {
  right: 9%;
  top: 10%;
  width: 6%;
  height: 78%;
}

.equation-card {
  position: absolute;
  padding: 0.65rem 0.9rem;
  border: 1px solid rgba(221, 238, 205, 0.11);
  border-radius: 0.35rem;
  color: rgba(231, 239, 224, 0.5);
  background: rgba(4, 16, 15, 0.1);
  box-shadow: none;
  font-family: Georgia, 'Times New Roman', serif;
  font-size: clamp(0.85rem, 1.05vw, 1rem);
  white-space: nowrap;
}

.tensor-card {
  top: 16%;
  right: 21%;
  transform: rotate(-3deg);
}

.fourier-card {
  top: 34%;
  right: 6%;
  transform: rotate(2deg);
}

.schrodinger-card {
  right: 31%;
  bottom: 19%;
  transform: rotate(-2deg);
}

.feynman-diagram {
  position: absolute;
  top: 47%;
  right: 23%;
  width: min(16vw, 13.5rem);
  overflow: visible;
  opacity: 0.48;
}

.fermion,
.photon {
  fill: none;
  stroke: rgba(226, 238, 215, 0.46);
  stroke-width: 3.4;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.photon {
  stroke: rgba(196, 176, 113, 0.62);
  stroke-dasharray: 10 10;
}

.vertex {
  fill: rgba(196, 176, 113, 0.7);
}

.orbit-hint {
  position: absolute;
  border: 1px solid rgba(129, 194, 182, 0.12);
  border-radius: 999px;
}

.orbit-a {
  top: 8%;
  right: -9%;
  width: 30%;
  height: 30%;
  transform: rotate(-18deg);
}

.orbit-b {
  left: 55%;
  top: 28%;
  width: 34%;
  height: 16%;
  transform: rotate(24deg);
}

.dashboard-strip {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 0.75rem;
  width: min(1180px, calc(100% - 2rem));
  margin: -5.5rem auto 2rem;
  position: relative;
  z-index: 2;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  min-height: 5.75rem;
  padding: 1rem;
  border: 1px solid rgba(127, 157, 145, 0.16);
  border-radius: 0.4rem;
  background: rgba(255, 255, 255, 0.66);
  box-shadow: 0 12px 28px rgba(26, 38, 34, 0.05);
  backdrop-filter: blur(14px);
  opacity: 0;
  transform: translateY(12px);
}

.physics-home-dark .stat-card {
  background: rgba(15, 24, 21, 0.74);
  border-color: rgba(125, 174, 164, 0.16);
}

.stat-icon {
  display: grid;
  place-items: center;
  width: 2.25rem;
  aspect-ratio: 1;
  border-radius: 999px;
  color: #0f3734;
  background: #c4eee8;
}

.stat-card p {
  margin: 0 0 0.2rem;
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.stat-card strong {
  font-size: 1.35rem;
}

.animate-fade-in {
  animation: fadeInUp 0.45s ease forwards;
}

@keyframes fadeInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 920px) {
  .hero-shell {
    align-items: flex-start;
    padding-top: clamp(2rem, 7vh, 5rem);
  }

  .physics-board {
    min-height: 44rem;
  }

  .dashboard-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    margin-top: 0;
  }
}

@media (max-width: 560px) {
  .hero-shell {
    width: min(100% - 1rem, 1180px);
  }

  .hero-actions :deep(.p-button) {
    width: 100%;
  }

  .equation-card {
    font-size: 0.9rem;
  }

  .tensor-card {
    left: 7%;
    right: auto;
    top: 48%;
  }

  .fourier-card {
    right: 5%;
    top: 60%;
  }

  .schrodinger-card {
    left: 9%;
    right: auto;
    bottom: 8%;
  }

  .feynman-diagram {
    top: 68%;
    right: 5%;
    width: 42vw;
    opacity: 0.28;
  }

  .building-accent {
    right: 2%;
    bottom: 10%;
    width: 34vw;
    height: 24vw;
    opacity: 0.18;
  }

  .dashboard-strip {
    grid-template-columns: 1fr;
    width: min(100% - 1rem, 1180px);
  }
}
</style>
