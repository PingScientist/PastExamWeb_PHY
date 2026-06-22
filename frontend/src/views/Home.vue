<template>
  <main class="physics-home" :class="{ 'physics-home-dark': isDarkTheme }">
    <div class="physics-board" aria-hidden="true">
      <svg class="spacetime-mesh" viewBox="0 0 1200 760" preserveAspectRatio="none">
        <defs>
          <radialGradient id="gravity-well" cx="70%" cy="44%" r="42%">
            <stop offset="0%" stop-color="#aed1b8" stop-opacity="0.35" />
            <stop offset="45%" stop-color="#588770" stop-opacity="0.12" />
            <stop offset="100%" stop-color="#588770" stop-opacity="0" />
          </radialGradient>
        </defs>
        <rect width="1200" height="760" fill="url(#gravity-well)" />
        <g class="mesh-lines">
          <path d="M30 70 C260 115 470 140 650 110 C850 76 1015 70 1170 116" />
          <path d="M10 160 C260 215 488 228 680 192 C864 158 1010 164 1190 230" />
          <path d="M0 255 C260 315 510 322 710 272 C882 230 1026 254 1200 335" />
          <path d="M0 360 C270 410 540 416 740 346 C910 288 1042 346 1200 442" />
          <path d="M0 470 C260 510 540 520 735 448 C910 388 1060 468 1200 560" />
          <path d="M20 590 C278 610 548 622 720 560 C900 496 1060 585 1180 690" />
          <path d="M120 0 C170 180 190 330 160 500 C140 610 160 700 210 760" />
          <path d="M275 0 C320 178 334 330 300 490 C274 612 302 702 365 760" />
          <path d="M440 0 C482 180 492 328 452 482 C420 608 468 702 535 760" />
          <path d="M615 0 C648 184 650 332 604 478 C564 606 618 700 695 760" />
          <path d="M790 0 C812 185 800 330 748 475 C702 606 766 702 860 760" />
          <path d="M960 0 C962 186 930 330 872 482 C824 608 900 704 1030 760" />
        </g>
        <g class="geodesics">
          <path d="M220 680 C390 498 526 408 704 392 C872 376 1010 270 1130 78" />
          <path d="M445 52 C584 202 642 332 622 456 C604 576 668 670 806 730" />
        </g>
        <circle class="mass-core" cx="760" cy="380" r="92" />
      </svg>

      <div class="formula-cloud">
        <div
          v-for="(formula, index) in formulaCards"
          :key="formula.name"
          class="theory-card"
          :class="`formula-${index + 1}`"
        >
          <span class="formula-expression">{{ formula.expression }}</span>
        </div>
      </div>
    </div>

    <section class="hero-shell">
      <div class="hero-copy">
        <p class="eyebrow">PHY Past Exam Archive</p>
        <div class="hero-title-lockup">
          <h1>清大物理考古系統</h1>
          <p class="title-roman">Physics &amp; Archaeology System</p>
          <p class="title-campus"><span></span>NTHU<span></span></p>
        </div>
        <p class="subtitle">書卷沒有，考古這有。</p>
        <div class="hero-actions">
          <Button icon="pi pi-sign-in" label="登入開始使用" size="large" @click="openLogin" />
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

const formulaCards = [
  {
    name: 'Euler-Lagrange',
    expression: 'd/dt(∂L/∂q̇ᵢ) − ∂L/∂qᵢ = 0',
  },
  {
    name: 'Hamilton',
    expression: 'q̇ᵢ = ∂H/∂pᵢ,  ṗᵢ = −∂H/∂qᵢ',
  },
  {
    name: 'Hamilton-Jacobi',
    expression: 'H(q, ∂S/∂q, t) + ∂S/∂t = 0',
  },
  {
    name: 'Noether',
    expression: 'δS = 0 ⇒ ∂μjμ = 0',
  },
  {
    name: 'Virial',
    expression: '2⟨T⟩ = ⟨r · ∇V⟩',
  },
  {
    name: 'Maxwell',
    expression: '∂μFμν = μ₀Jν,  ∂[αFβγ] = 0',
  },
  {
    name: 'Lorentz Force',
    expression: 'dpμ/dτ = qFμνuν',
  },
  {
    name: 'Lienard-Wiechert',
    expression: 'φ = 1/4πϵ₀ [q/(R − R · β)]ret',
  },
  {
    name: 'Poynting',
    expression: '∂u/∂t + ∇ · S = −J · E',
  },
  {
    name: 'Jefimenko',
    expression: 'E(r,t) = ∫[ρ/R² + ρ̇/cR − J̇/c²R] d³r′',
  },
  {
    name: 'TDSE',
    expression: 'iℏ∂t|ψ⟩ = Ĥ|ψ⟩',
  },
  {
    name: 'TISE',
    expression: 'Ĥψn = Enψn',
  },
  {
    name: 'Heisenberg',
    expression: 'dA/dt = (i/ℏ)[H,A] + ∂A/∂t',
  },
  {
    name: 'Ehrenfest',
    expression: 'd⟨p⟩/dt = −⟨∇V⟩',
  },
  {
    name: 'Lippmann-Schwinger',
    expression: '|ψ±⟩ = |φ⟩ + G₀±V|ψ±⟩',
  },
  {
    name: 'Boltzmann',
    expression: '∂tf + v · ∇f + F · ∇pf = C[f]',
  },
  {
    name: 'Fokker-Planck',
    expression: '∂tP = −∂i(AiP) + 1/2∂i∂j(BijP)',
  },
  {
    name: 'Langevin',
    expression: 'mẍ + γẋ + ∇V = ξ(t)',
  },
  {
    name: 'Einstein Field',
    expression: 'Gμν + Λgμν = 8πG/c⁴ Tμν',
  },
  {
    name: 'Dirac',
    expression: '(iγμ∂μ − m)ψ = 0',
  },
]

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
  max-width: 42rem;
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
  color: #edf7ed;
  font-size: clamp(3rem, 4.2vw, 4.7rem);
  font-weight: 780;
  line-height: 1.04;
  letter-spacing: 0.08em;
  text-shadow: 0 1.2rem 3rem rgba(0, 0, 0, 0.22);
}

.hero-title-lockup {
  display: inline-grid;
  gap: 0.62rem;
}

.title-roman {
  margin: 0;
  color: rgba(202, 179, 111, 0.94);
  font-size: clamp(0.88rem, 1.25vw, 1.08rem);
  font-weight: 760;
  letter-spacing: 0.34em;
  line-height: 1.1;
  text-transform: uppercase;
}

.title-campus {
  display: grid;
  grid-template-columns: minmax(2.5rem, 1fr) auto minmax(2.5rem, 1fr);
  align-items: center;
  gap: 1rem;
  width: min(100%, 38rem);
  margin: 0;
  color: rgba(202, 179, 111, 0.98);
  font-size: clamp(0.9rem, 1.1vw, 1.05rem);
  font-weight: 760;
  letter-spacing: 0.5em;
  text-indent: 0.5em;
}

.title-campus span {
  display: block;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(202, 179, 111, 0.8));
}

.title-campus span:last-child {
  background: linear-gradient(90deg, rgba(202, 179, 111, 0.8), transparent);
}

.subtitle {
  max-width: 36rem;
  margin: 1.2rem 0 0;
  color: rgba(222, 232, 224, 0.78);
  font-size: clamp(0.98rem, 1.15vw, 1.08rem);
  line-height: 1.78;
}

.hero-actions :deep(.p-button.p-button-secondary.p-button-outlined) {
  color: rgba(232, 240, 226, 0.86);
  border-color: rgba(214, 230, 223, 0.62);
  background: rgba(10, 20, 18, 0.18);
}

.hero-actions :deep(.p-button.p-button-secondary.p-button-outlined:hover) {
  color: #f5fbf6;
  border-color: rgba(238, 246, 239, 0.82);
  background: rgba(214, 230, 223, 0.1);
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
    radial-gradient(circle at 68% 46%, rgba(140, 180, 147, 0.18), transparent 20rem),
    radial-gradient(circle at 24% 20%, rgba(72, 123, 103, 0.1), transparent 20rem),
    linear-gradient(135deg, rgba(12, 28, 25, 0.98), rgba(13, 20, 21, 0.98));
  pointer-events: none;
  z-index: 0;
}

.physics-board::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 70% 44%, rgba(218, 230, 205, 0.08), transparent 8rem),
    linear-gradient(115deg, transparent 0 42%, rgba(225, 236, 221, 0.028) 44%, transparent 48%),
    linear-gradient(
      90deg,
      rgba(8, 18, 16, 0.1),
      rgba(8, 18, 16, 0.58) 26%,
      rgba(8, 18, 16, 0.12) 62%,
      rgba(8, 18, 16, 0.02)
    );
  pointer-events: none;
  z-index: 3;
  animation: fieldGlow 10s ease-in-out infinite alternate;
}

.physics-board::after {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(
      circle at 68% 46%,
      transparent 0 13rem,
      rgba(7, 16, 14, 0.1) 18rem,
      transparent 31rem
    ),
    linear-gradient(0deg, rgba(8, 18, 16, 0.32), transparent 40%);
  pointer-events: none;
  z-index: 4;
  animation: gravityVignette 12s ease-in-out infinite alternate;
}

.formula-cloud::before {
  content: '';
  position: absolute;
  top: -18%;
  left: -24%;
  width: 46%;
  height: 145%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(172, 219, 205, 0.085),
    rgba(202, 179, 111, 0.095),
    transparent
  );
  filter: blur(16px);
  transform: skewX(-16deg);
  animation: spectralSweep 5.2s linear infinite;
}

.spacetime-mesh {
  position: absolute;
  inset: -4% -3% -2% -2%;
  width: 100%;
  height: 100%;
  opacity: 0.68;
  z-index: 1;
  transform-origin: 68% 46%;
  animation: spacetimeDrift 6.8s ease-in-out infinite alternate;
}

.mesh-lines path {
  fill: none;
  stroke: rgba(198, 223, 205, 0.23);
  stroke-width: 1.35;
  vector-effect: non-scaling-stroke;
  animation: meshBreathing 5.5s ease-in-out infinite alternate;
}

.geodesics path {
  fill: none;
  stroke: rgba(202, 179, 111, 0.58);
  stroke-width: 2.8;
  stroke-linecap: round;
  stroke-dasharray: 22 18;
  vector-effect: non-scaling-stroke;
  animation: geodesicFlow 3.8s linear infinite;
}

.mass-core {
  fill: rgba(232, 238, 218, 0.09);
  stroke: rgba(221, 237, 210, 0.18);
  stroke-width: 1.2;
  vector-effect: non-scaling-stroke;
  transform-origin: 760px 380px;
  animation: massPulse 3.2s ease-in-out infinite;
}

.formula-cloud {
  position: absolute;
  inset: 0;
  z-index: 2;
  animation: formulaFieldDrift 6.6s ease-in-out infinite alternate;
}

.theory-card {
  position: absolute;
  display: block;
  max-width: min(24rem, 28vw);
  color: rgba(232, 240, 226, 0.25);
  font-family: Georgia, 'Times New Roman', serif;
  transform: rotate(var(--tilt, 0deg));
  white-space: nowrap;
  animation: var(--formula-motion, formulaOrbitA) var(--float-duration, 8s) ease-in-out infinite;
  animation-delay: var(--float-delay, 0s);
}

.formula-expression {
  font-size: clamp(0.9rem, 1.05vw, 1.15rem);
  line-height: 1.2;
  text-shadow: 0 0 1rem rgba(168, 204, 181, 0.1);
}

.formula-1 {
  top: 12%;
  left: 52%;
  --tilt: -3deg;
  --float-delay: -1s;
  --float-duration: 7.5s;
  --formula-motion: formulaOrbitA;
}

.formula-2 {
  top: 22%;
  left: 64%;
  --tilt: 2deg;
  --float-delay: -7s;
  --float-duration: 8.6s;
  --formula-motion: formulaOrbitB;
}

.formula-3 {
  top: 34%;
  left: 55%;
  --tilt: -1deg;
  --float-delay: -4s;
  --float-duration: 9.2s;
  --formula-motion: formulaOrbitC;
}

.formula-4 {
  top: 9%;
  right: 5%;
  --tilt: 3deg;
  --float-delay: -10s;
  --float-duration: 7.8s;
  --formula-motion: formulaOrbitB;
}

.formula-5 {
  bottom: 20%;
  right: 13%;
  --tilt: -2deg;
  --float-delay: -13s;
  --float-duration: 8.2s;
  --formula-motion: formulaOrbitA;
}

.formula-6 {
  top: 46%;
  right: 6%;
  --tilt: 2deg;
  --float-delay: -5s;
  --float-duration: 9.8s;
  --formula-motion: formulaOrbitC;
}

.formula-7 {
  top: 19%;
  left: 6%;
  --tilt: -2deg;
  --float-delay: -9s;
  --float-duration: 8.4s;
  --formula-motion: formulaOrbitC;
}

.formula-8 {
  bottom: 14%;
  right: 34%;
  --tilt: 3deg;
  --float-delay: -2s;
  --float-duration: 7.4s;
  --formula-motion: formulaOrbitB;
}

.formula-9 {
  top: 60%;
  left: 57%;
  --tilt: -3deg;
  --float-delay: -12s;
  --float-duration: 9.4s;
  --formula-motion: formulaOrbitA;
}

.formula-10 {
  bottom: 22%;
  right: 4%;
  --tilt: 2deg;
  --float-delay: -6s;
  --float-duration: 8.8s;
  --formula-motion: formulaOrbitC;
}

.formula-11 {
  top: 15%;
  left: 32%;
  --tilt: 1deg;
  --float-delay: -15s;
  --float-duration: 7.9s;
  --formula-motion: formulaOrbitA;
}

.formula-12 {
  bottom: 14%;
  left: 6%;
  --tilt: -2deg;
  --float-delay: -3s;
  --float-duration: 8.5s;
  --formula-motion: formulaOrbitB;
}

.formula-13 {
  top: 30%;
  right: 18%;
  --tilt: -2deg;
  --float-delay: -11s;
  --float-duration: 9s;
  --formula-motion: formulaOrbitC;
}

.formula-14 {
  bottom: 30%;
  left: 44%;
  --tilt: 2deg;
  --float-delay: -8s;
  --float-duration: 7.7s;
  --formula-motion: formulaOrbitB;
}

.formula-15 {
  bottom: 7%;
  left: 43%;
  --tilt: -1deg;
  --float-delay: -14s;
  --float-duration: 8.9s;
  --formula-motion: formulaOrbitA;
}

.formula-16 {
  bottom: 28%;
  left: 10%;
  --tilt: 2deg;
  --float-delay: -4s;
  --float-duration: 9.6s;
  --formula-motion: formulaOrbitC;
}

.formula-17 {
  bottom: 18%;
  left: 23%;
  --tilt: -3deg;
  --float-delay: -16s;
  --float-duration: 7.6s;
  --formula-motion: formulaOrbitB;
}

.formula-18 {
  top: 40%;
  left: 73%;
  --tilt: -1deg;
  --float-delay: -7s;
  --float-duration: 9.1s;
  --formula-motion: formulaOrbitA;
}

.formula-19 {
  top: 7%;
  left: 68%;
  color: rgba(242, 238, 216, 0.34);
  --tilt: -2deg;
  --float-delay: -18s;
  --float-duration: 8s;
  --formula-motion: formulaOrbitC;
}

.formula-20 {
  bottom: 39%;
  right: 31%;
  --tilt: 3deg;
  --float-delay: -5s;
  --float-duration: 8.7s;
  --formula-motion: formulaOrbitA;
}

.dashboard-strip {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.55rem;
  width: min(17.5rem, calc(100% - 2rem));
  margin: 0;
  position: absolute;
  top: clamp(8.5rem, 20vh, 14rem);
  right: max(1rem, calc((100% - 1180px) / 2));
  z-index: 2;
}

.dashboard-strip::before {
  content: 'Archive Metrics';
  color: rgba(202, 179, 111, 0.72);
  font-size: 0.68rem;
  font-weight: 760;
  letter-spacing: 0.26em;
  line-height: 1;
  text-transform: uppercase;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  min-height: 4.4rem;
  padding: 0.78rem 0.9rem;
  border: 1px solid rgba(128, 166, 151, 0.14);
  border-left: 3px solid rgba(202, 179, 111, 0.62);
  border-radius: 0.3rem;
  background:
    linear-gradient(90deg, rgba(202, 179, 111, 0.08), transparent 44%), rgba(7, 18, 17, 0.62);
  box-shadow: none;
  backdrop-filter: blur(16px);
  opacity: 0;
  transform: translateY(12px);
}

.physics-home-dark .stat-card {
  background:
    linear-gradient(90deg, rgba(202, 179, 111, 0.08), transparent 44%), rgba(7, 18, 17, 0.62);
  border-color: rgba(125, 174, 164, 0.16);
  border-left-color: rgba(202, 179, 111, 0.62);
}

.stat-icon {
  display: grid;
  place-items: center;
  width: 2rem;
  aspect-ratio: 1;
  border-radius: 0.25rem;
  color: #c7b06b;
  background: rgba(196, 238, 232, 0.08);
}

.stat-card p {
  margin: 0 0 0.2rem;
  color: rgba(229, 238, 229, 0.74);
  font-size: 0.85rem;
}

.stat-card strong {
  color: #f4fbf4;
  font-size: 1.3rem;
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

@keyframes spacetimeDrift {
  from {
    transform: translate3d(-5%, -2.2%, 0) scale(1.03) rotate(-0.9deg);
  }

  to {
    transform: translate3d(5.4%, 2.1%, 0) scale(1.085) rotate(1deg);
  }
}

@keyframes meshBreathing {
  from {
    opacity: 0.66;
  }

  to {
    opacity: 1;
  }
}

@keyframes geodesicFlow {
  from {
    stroke-dashoffset: 0;
  }

  to {
    stroke-dashoffset: -720;
  }
}

@keyframes massPulse {
  0%,
  100% {
    opacity: 0.48;
    transform: scale(0.82);
  }

  50% {
    opacity: 1;
    transform: scale(1.36);
  }
}

@keyframes fieldGlow {
  from {
    opacity: 0.82;
    transform: translate3d(-2%, 0.4%, 0);
  }

  to {
    opacity: 1;
    transform: translate3d(2%, -1.1%, 0);
  }
}

@keyframes gravityVignette {
  from {
    opacity: 0.85;
  }

  to {
    opacity: 1;
  }
}

@keyframes formulaFieldDrift {
  from {
    transform: translate3d(-3.2%, 1.8%, 0);
  }

  to {
    transform: translate3d(3.1%, -1.9%, 0);
  }
}

@keyframes formulaOrbitA {
  0%,
  100% {
    opacity: 0.18;
    transform: rotate(var(--tilt, 0deg)) translate3d(0, 0, 0);
  }

  33% {
    opacity: 0.36;
    transform: rotate(var(--tilt, 0deg)) translate3d(2.4rem, -1.45rem, 0);
  }

  66% {
    opacity: 0.26;
    transform: rotate(var(--tilt, 0deg)) translate3d(-1.7rem, 1.65rem, 0);
  }
}

@keyframes formulaOrbitB {
  0%,
  100% {
    opacity: 0.2;
    transform: rotate(var(--tilt, 0deg)) translate3d(0, 0, 0);
  }

  38% {
    opacity: 0.34;
    transform: rotate(var(--tilt, 0deg)) translate3d(-2.6rem, -1.25rem, 0);
  }

  72% {
    opacity: 0.27;
    transform: rotate(var(--tilt, 0deg)) translate3d(1.9rem, 1.9rem, 0);
  }
}

@keyframes formulaOrbitC {
  0%,
  100% {
    opacity: 0.17;
    transform: rotate(var(--tilt, 0deg)) translate3d(0, 0, 0);
  }

  50% {
    opacity: 0.38;
    transform: rotate(var(--tilt, 0deg)) translate3d(0.9rem, -2.6rem, 0);
  }

  78% {
    opacity: 0.24;
    transform: rotate(var(--tilt, 0deg)) translate3d(-2.2rem, 0.9rem, 0);
  }
}

@keyframes spectralSweep {
  from {
    transform: translateX(-25vw) skewX(-16deg);
  }

  to {
    transform: translateX(150vw) skewX(-16deg);
  }
}

@media (max-width: 1100px) {
  .dashboard-strip {
    position: relative;
    top: auto;
    right: auto;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    width: min(1180px, calc(100% - 2rem));
    margin: -5.5rem auto 2rem;
  }

  .dashboard-strip::before {
    grid-column: 1 / -1;
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

  .theory-card {
    max-width: 42vw;
  }

  .formula-7,
  .formula-10,
  .formula-12,
  .formula-15,
  .formula-17,
  .formula-18 {
    display: none;
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

  .spacetime-mesh {
    inset: 4% -35% 0 -22%;
    width: 150%;
    opacity: 0.52;
  }

  .theory-card {
    display: none;
    max-width: 72vw;
    padding: 0.5rem 0.62rem;
  }

  .formula-expression {
    font-size: 0.82rem;
  }

  .formula-1,
  .formula-6,
  .formula-11,
  .formula-19,
  .formula-20 {
    display: grid;
  }

  .formula-1 {
    top: 54%;
    right: 5%;
    left: auto;
  }

  .formula-6 {
    top: 66%;
    left: 8%;
    right: auto;
  }

  .formula-11 {
    top: 78%;
    left: 14%;
  }

  .formula-19 {
    top: 44%;
    left: 9%;
  }

  .formula-20 {
    bottom: 7%;
    right: 6%;
  }

  .dashboard-strip {
    grid-template-columns: 1fr;
    width: min(100% - 1rem, 1180px);
  }
}
</style>
