import { reactive } from 'vue'
import { api } from '../api/services/client'

// Safe fallback only. A successful API load replaces these runtime values.
export const DEFAULT_SUBMISSION_LEVELS = [
  { level: 1, name: '新手投稿者', minExp: 0 },
  { level: 2, name: '初階整理者', minExp: 2 },
  { level: 3, name: '穩定投稿者', minExp: 5 },
  { level: 4, name: '認真貢獻者', minExp: 9 },
  { level: 5, name: '經典整理師', minExp: 14 },
  { level: 6, name: '題庫建設者', minExp: 20 },
  { level: 7, name: '資源探索者', minExp: 27 },
  { level: 8, name: '校園收藏家', minExp: 35 },
  { level: 9, name: '傳奇貢獻者', minExp: 44 },
  { level: 10, name: '題庫宗師', minExp: 54 },
]

export const SUBMISSION_LEVELS = reactive(DEFAULT_SUBMISSION_LEVELS.map((level) => ({ ...level })))

export const CONTRIBUTOR_LEVEL_PALETTE = [
  { bg: '#7a513a', fg: '#ffffff', border: '#493023', accent: '#ddb99f' },
  { bg: '#66747b', fg: '#ffffff', border: '#3d474c', accent: '#d8e0e3' },
  { bg: '#285c68', fg: '#ffffff', border: '#173a42', accent: '#b8dce2' },
  { bg: '#23745d', fg: '#ffffff', border: '#12493a', accent: '#afe0cf' },
  { bg: '#304f68', fg: '#ffffff', border: '#1a3040', accent: '#bfd2df' },
  { bg: '#1d6c70', fg: '#ffffff', border: '#104447', accent: '#ace0df' },
  { bg: '#365f8a', fg: '#ffffff', border: '#203a55', accent: '#c3d5e8' },
  { bg: '#f1eee5', fg: '#263238', border: '#77756f', accent: '#ffffff' },
  { bg: '#252a2d', fg: '#ffffff', border: '#b9c2c7', accent: '#e3e8ea' },
  { bg: '#806322', fg: '#ffffff', border: '#493711', accent: '#f6e2a1' },
]

let settingsLoaded = false
let settingsRequest = null

function normalizeSettings(settings) {
  if (!Array.isArray(settings) || settings.length !== 10) {
    throw new Error('投稿等級設定必須正好包含 10 個等級')
  }

  const names = new Set()
  let previousMinExp = null
  return settings.map((item, index) => {
    const level = item?.level
    const name = typeof item?.name === 'string' ? item.name.trim() : ''
    const minExp = item?.minExp ?? item?.min_exp
    if (!Number.isInteger(level) || level !== index + 1) {
      throw new Error('投稿等級必須依序為 Lv.1 至 Lv.10')
    }
    if (!name || name.length > 30 || !/[^\s\p{Cf}]/u.test(name)) {
      throw new Error(`Lv.${level} 名稱不可為空白，且不得超過 30 個字元`)
    }
    if (names.has(name)) throw new Error('投稿等級名稱不可重複')
    if (!Number.isInteger(minExp) || minExp < 0) {
      throw new Error(`Lv.${level} 累積 EXP 必須是非負整數`)
    }
    if (level === 1 && minExp !== 0) throw new Error('Lv.1 累積 EXP 必須為 0')
    if (previousMinExp !== null && minExp <= previousMinExp) {
      throw new Error('Lv.2 至 Lv.10 累積 EXP 門檻必須嚴格遞增')
    }
    names.add(name)
    previousMinExp = minExp
    return { level, name, minExp }
  })
}

function replaceRuntimeSettings(settings) {
  const normalized = normalizeSettings(settings)
  SUBMISSION_LEVELS.splice(0, SUBMISSION_LEVELS.length, ...normalized)
  return getContributorLevelSettingsSnapshot()
}

export function validateContributorLevelSettings(settings) {
  return normalizeSettings(settings)
}

export function getContributorLevelSettingsSnapshot() {
  return SUBMISSION_LEVELS.map((level) => ({ ...level }))
}

export async function loadContributorLevelSettings({ force = false } = {}) {
  if (settingsLoaded && !force) return getContributorLevelSettingsSnapshot()
  if (settingsRequest) return settingsRequest

  settingsRequest = api
    .get('/settings/contributor-levels')
    .then(({ data }) => {
      const settings = replaceRuntimeSettings(data)
      settingsLoaded = true
      return settings
    })
    .catch(() => {
      settingsLoaded = true
      return getContributorLevelSettingsSnapshot()
    })
    .finally(() => {
      settingsRequest = null
    })
  return settingsRequest
}

export async function saveContributorLevelSettings(settings) {
  const normalized = normalizeSettings(settings)
  const payload = normalized.map(({ level, name, minExp }) => ({
    level,
    name,
    min_exp: minExp,
  }))
  const { data } = await api.put('/settings/contributor-levels', payload)
  settingsLoaded = true
  return replaceRuntimeSettings(data)
}

export function getContributorLevelPalette(level) {
  const index = Math.min(Math.max(Number(level) || 1, 1), CONTRIBUTOR_LEVEL_PALETTE.length) - 1
  return CONTRIBUTOR_LEVEL_PALETTE[index]
}

export function resolveSubmissionLevel(experience) {
  const currentExp = Math.max(0, Number(experience) || 0)
  const currentLevel = SUBMISSION_LEVELS.reduce(
    (matchedLevel, level) => (currentExp >= level.minExp ? level : matchedLevel),
    SUBMISSION_LEVELS[0]
  )
  const nextLevel = SUBMISSION_LEVELS[currentLevel.level]
  if (!nextLevel) {
    return {
      ...currentLevel,
      currentExp,
      isMaxLevel: true,
      progressInLevel: 1,
      progressRange: 1,
      progressPercent: 100,
      expToNextLevel: 0,
    }
  }
  const progressRange = nextLevel.minExp - currentLevel.minExp
  const progressInLevel = Math.max(0, currentExp - currentLevel.minExp)
  return {
    ...currentLevel,
    currentExp,
    isMaxLevel: false,
    progressInLevel,
    progressRange,
    progressPercent: Math.min(100, (progressInLevel / progressRange) * 100),
    expToNextLevel: Math.max(0, nextLevel.minExp - currentExp),
  }
}

export function formatSubmissionLevelTitle(experience) {
  const level = resolveSubmissionLevel(experience)
  return `Lv.${level.level} ${level.name}`
}
