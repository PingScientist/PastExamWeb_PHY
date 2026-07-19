import { computed, reactive } from 'vue'
import { notificationService } from '../api'
import { isUnauthorizedError } from './http'
import { STORAGE_KEYS, getSessionItem, removeSessionItem, setSessionItem } from './storage'

const emptyCounts = () => ({ announcements: 0, personal_notifications: 0, total: 0 })

const state = reactive({
  announcements: [],
  personalNotifications: [],
  counts: emptyCounts(),
  unreadSummary: { announcements: [], personal_notifications: [], counts: emptyCounts() },
  modalVisible: false,
  centerVisible: false,
  initialized: false,
  loadingSummary: false,
  loadingCenter: false,
})

const errors = reactive({ summary: null, center: null })
const unreadTotal = computed(() => Number(state.counts.total || 0))

function updateCounts(counts) {
  state.counts = { ...emptyCounts(), ...(counts || {}) }
}

async function initNotifications() {
  if (state.initialized || state.loadingSummary) return
  state.loadingSummary = true
  errors.summary = null
  try {
    const { data } = await notificationService.getUnreadSummary({ limit: 10 })
    state.unreadSummary = data
    updateCounts(data?.counts)
    const alreadyChecked = getSessionItem(STORAGE_KEYS.session.NOTIFICATION_LOGIN_CHECKED)
    if (!alreadyChecked) {
      setSessionItem(STORAGE_KEYS.session.NOTIFICATION_LOGIN_CHECKED, '1')
      state.modalVisible = unreadTotal.value > 0
    }
    state.initialized = true
  } catch (error) {
    errors.summary = error
    if (!isUnauthorizedError(error)) console.error('Failed to load unread notifications:', error)
  } finally {
    state.loadingSummary = false
  }
}

async function refreshCenter() {
  if (state.loadingCenter) return
  state.loadingCenter = true
  errors.center = null
  try {
    const { data } = await notificationService.getCenter({ personal_limit: 50 })
    state.announcements = data?.announcements || []
    state.personalNotifications = data?.personal_notifications || []
    updateCounts(data?.counts)
  } catch (error) {
    errors.center = error
    if (!isUnauthorizedError(error)) console.error('Failed to load notification center:', error)
  } finally {
    state.loadingCenter = false
  }
}

async function refreshSummary() {
  const { data } = await notificationService.getUnreadSummary({ limit: 10 })
  state.unreadSummary = data
  updateCounts(data?.counts)
}

async function refreshCounts() {
  const { data } = await notificationService.getCounts()
  updateCounts(data)
}

async function markAnnouncementRead(id) {
  await notificationService.markAnnouncementRead(id)
  await Promise.all([refreshCenter(), refreshSummary()])
}

async function markPersonalRead(id) {
  await notificationService.markPersonalRead(id)
  await Promise.all([refreshCenter(), refreshSummary()])
}

async function markAllPersonalRead() {
  await notificationService.markAllPersonalRead()
  await Promise.all([refreshCenter(), refreshSummary()])
}

async function markAllRead() {
  await notificationService.markAllRead()
  await Promise.all([refreshCenter(), refreshSummary()])
  state.modalVisible = false
}

async function openCenter() {
  state.modalVisible = false
  await refreshCenter()
  if (!errors.center) state.centerVisible = true
}

function resetForLogout() {
  Object.assign(state, {
    announcements: [],
    personalNotifications: [],
    counts: emptyCounts(),
    unreadSummary: { announcements: [], personal_notifications: [], counts: emptyCounts() },
    modalVisible: false,
    centerVisible: false,
    initialized: false,
  })
  removeSessionItem(STORAGE_KEYS.session.NOTIFICATION_LOGIN_CHECKED)
}

function beginLoginSession() {
  removeSessionItem(STORAGE_KEYS.session.NOTIFICATION_LOGIN_CHECKED)
  state.initialized = false
}

export function useNotifications() {
  return {
    state,
    errors,
    unreadTotal,
    initNotifications,
    refreshCenter,
    refreshSummary,
    refreshCounts,
    markAnnouncementRead,
    markPersonalRead,
    markAllPersonalRead,
    markAllRead,
    openCenter,
    resetForLogout,
    beginLoginSession,
  }
}
