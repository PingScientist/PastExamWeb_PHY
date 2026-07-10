import { getLocalItem, setLocalItem } from './storage'

export const FONT_SIZE_STORAGE_KEY = 'personal-settings-font-size'

export const FONT_SIZE_BASELINE_SCALE = 0.9
export const FONT_SIZE_MIN = 80
export const FONT_SIZE_MAX = 125
export const FONT_SIZE_STEP = 1
export const FONT_SIZE_DEFAULT = 100

const DISPLAY_PERCENT_PREFIX = 'display-percent:'

const LEGACY_FONT_SIZE_SCALE = {
  small: 0.9,
  default: 1,
  large: 1.1,
  'x-large': 1.2,
}

function normalizeFontSizePercent(value) {
  const numeric = Number(value)
  if (!Number.isFinite(numeric)) {
    return FONT_SIZE_DEFAULT
  }

  const clamped = Math.min(FONT_SIZE_MAX, Math.max(FONT_SIZE_MIN, numeric))
  return Math.round(clamped)
}

function displayPercentFromActualScale(value) {
  const numeric = Number(value)
  if (!Number.isFinite(numeric)) {
    return FONT_SIZE_DEFAULT
  }

  return normalizeFontSizePercent((numeric / FONT_SIZE_BASELINE_SCALE) * 100)
}

export function actualScaleFromDisplayPercent(value) {
  const percent = normalizeFontSizePercent(value)
  return Number((FONT_SIZE_BASELINE_SCALE * (percent / 100)).toFixed(4))
}

function parseStoredFontSizePercent(stored) {
  if (!stored) {
    return FONT_SIZE_DEFAULT
  }

  if (Object.hasOwn(LEGACY_FONT_SIZE_SCALE, stored)) {
    return displayPercentFromActualScale(LEGACY_FONT_SIZE_SCALE[stored])
  }

  if (stored.startsWith(DISPLAY_PERCENT_PREFIX)) {
    return normalizeFontSizePercent(stored.slice(DISPLAY_PERCENT_PREFIX.length))
  }

  const numeric = Number(stored)
  if (!Number.isFinite(numeric)) {
    return FONT_SIZE_DEFAULT
  }

  if (numeric > 2) {
    return normalizeFontSizePercent(numeric)
  }

  return displayPercentFromActualScale(numeric)
}

export function getFontSizePreference() {
  const stored = getLocalItem(FONT_SIZE_STORAGE_KEY)
  return parseStoredFontSizePercent(stored)
}

export function applyFontSizePreference(value = getFontSizePreference()) {
  const percent = normalizeFontSizePercent(value)
  const scale = actualScaleFromDisplayPercent(percent)

  if (typeof document !== 'undefined') {
    document.documentElement.style.setProperty('--app-font-scale', String(scale))
    document.documentElement.dataset.appFontSize = String(scale)
  }

  return percent
}

export function setFontSizePreference(value) {
  const percent = normalizeFontSizePercent(value)
  setLocalItem(FONT_SIZE_STORAGE_KEY, `${DISPLAY_PERCENT_PREFIX}${percent}`)
  applyFontSizePreference(percent)
  return percent
}
