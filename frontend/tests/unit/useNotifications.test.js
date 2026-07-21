import { beforeEach, describe, expect, it, vi } from 'vitest'

const summary = {
  announcements: [{ id: 1, title: '公告' }],
  personal_notifications: [{ id: 2, title: '回覆' }],
  counts: { announcements: 1, personal_notifications: 1, total: 2 },
}
const center = { ...summary }
const service = vi.hoisted(() => ({
  getUnreadSummary: vi.fn(),
  getCenter: vi.fn(),
  getCounts: vi.fn(),
  markAnnouncementRead: vi.fn(),
  markPersonalRead: vi.fn(),
  markAllPersonalRead: vi.fn(),
  markAllRead: vi.fn(),
  deletePersonal: vi.fn(),
  deleteAllPersonal: vi.fn(),
}))
vi.mock('@/api', () => ({ notificationService: service }))
vi.mock('@/utils/http', () => ({ isUnauthorizedError: () => false }))

describe('useNotifications', () => {
  beforeEach(() => {
    vi.resetModules()
    sessionStorage.clear()
    Object.values(service).forEach((mock) => mock.mockReset())
    service.getUnreadSummary.mockResolvedValue({ data: structuredClone(summary) })
    service.getCenter.mockResolvedValue({ data: structuredClone(center) })
    service.getCounts.mockResolvedValue({ data: structuredClone(summary.counts) })
    service.markAnnouncementRead.mockResolvedValue({})
    service.markPersonalRead.mockResolvedValue({})
    service.markAllPersonalRead.mockResolvedValue({})
    service.markAllRead.mockResolvedValue({})
    service.deletePersonal.mockResolvedValue({ data: { success: true } })
    service.deleteAllPersonal.mockResolvedValue({ data: { deleted_count: 1 } })
  })

  it('removes one notification and refreshes shared unread state after success', async () => {
    const { useNotifications } = await import('@/utils/useNotifications.js')
    const store = useNotifications()
    await store.openCenter()
    service.getCenter.mockResolvedValueOnce({
      data: {
        announcements: summary.announcements,
        personal_notifications: [],
        counts: { announcements: 1, personal_notifications: 0, total: 1 },
      },
    })
    service.getUnreadSummary.mockResolvedValueOnce({
      data: {
        announcements: summary.announcements,
        personal_notifications: [],
        counts: { announcements: 1, personal_notifications: 0, total: 1 },
      },
    })

    await store.deletePersonalNotification(2)

    expect(service.deletePersonal).toHaveBeenCalledWith(2)
    expect(store.state.personalNotifications).toEqual([])
    expect(store.state.unreadSummary.personal_notifications).toEqual([])
    expect(store.state.counts).toEqual({ announcements: 1, personal_notifications: 0, total: 1 })
  })

  it('keeps data on delete failure and clears all personal notification state after bulk success', async () => {
    const { useNotifications } = await import('@/utils/useNotifications.js')
    const store = useNotifications()
    await store.openCenter()
    service.deletePersonal.mockRejectedValueOnce(new Error('delete failed'))
    await expect(store.deletePersonalNotification(2)).rejects.toThrow('delete failed')
    expect(store.state.personalNotifications).toHaveLength(1)

    await store.deleteAllPersonalNotifications()
    expect(service.deleteAllPersonal).toHaveBeenCalledOnce()
    expect(store.state.personalNotifications).toEqual([])
    expect(store.state.unreadSummary.personal_notifications).toEqual([])
    expect(store.state.counts).toEqual({ announcements: 1, personal_notifications: 0, total: 1 })
  })

  it('checks unread content once per login session', async () => {
    const { useNotifications } = await import('@/utils/useNotifications.js')
    const store = useNotifications()
    await store.initNotifications()
    expect(store.state.modalVisible).toBe(true)
    expect(store.unreadTotal.value).toBe(2)
    await store.initNotifications()
    expect(service.getUnreadSummary).toHaveBeenCalledTimes(1)
  })

  it('does not reopen the login summary after a module remount in the same session', async () => {
    sessionStorage.setItem('notification-login-checked', '1')
    const { useNotifications } = await import('@/utils/useNotifications.js')
    const store = useNotifications()
    await store.initNotifications()
    expect(store.state.modalVisible).toBe(false)
    expect(store.state.counts.total).toBe(2)
  })

  it('loads the separated center and updates read state through the API', async () => {
    const { useNotifications } = await import('@/utils/useNotifications.js')
    const store = useNotifications()
    await store.openCenter()
    expect(store.state.announcements).toHaveLength(1)
    expect(store.state.personalNotifications).toHaveLength(1)
    await store.markAnnouncementRead(1)
    await store.markPersonalRead(2)
    await store.markAllPersonalRead()
    await store.markAllRead()
    expect(service.markAnnouncementRead).toHaveBeenCalledWith(1)
    expect(service.markPersonalRead).toHaveBeenCalledWith(2)
    expect(service.markAllPersonalRead).toHaveBeenCalledOnce()
    expect(service.markAllRead).toHaveBeenCalledOnce()
  })
})
