import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import NotificationCenterModal from '@/components/NotificationCenterModal.vue'

const slotStub = { template: '<div><slot /><slot name="header" /></div>' }
const tabsStub = { template: '<div><slot /></div>' }
const announcements = [
  {
    id: 1,
    title: '公告一',
    body: '內容',
    severity: 'info',
    is_read: false,
    updated_at: '2026-01-01T00:00:00Z',
  },
]
const personal = [
  {
    id: 2,
    title: '回覆通知',
    message: '內容',
    read_at: null,
    source_available: true,
    created_at: '2026-01-02T00:00:00Z',
  },
]

describe('NotificationCenterModal', () => {
  it('separates announcements and personal notifications and marks detail read', async () => {
    const wrapper = mount(NotificationCenterModal, {
      props: {
        visible: true,
        announcements,
        personalNotifications: personal,
        counts: { total: 2, personal_notifications: 1 },
      },
      global: {
        stubs: {
          Dialog: slotStub,
          Tabs: tabsStub,
          TabList: tabsStub,
          Tab: tabsStub,
          TabPanels: tabsStub,
          TabPanel: tabsStub,
          DataTable: tabsStub,
          Column: true,
          Button: true,
          Tag: true,
          Badge: true,
        },
      },
    })
    expect(wrapper.text()).toContain('公告與通知')
    expect(wrapper.text()).toContain('公告')
    expect(wrapper.text()).toContain('個人通知')
    wrapper.vm.openAnnouncement(announcements[0])
    expect(wrapper.emitted('mark-announcement-read')).toEqual([[1]])
    wrapper.vm.openPersonal(personal[0])
    expect(wrapper.emitted('mark-personal-read')).toEqual([[2]])
  })
})
