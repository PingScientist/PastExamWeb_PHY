import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import NotificationModal from '@/components/NotificationModal.vue'

const summary = {
  announcements: [
    { id: 1, title: '系統維護', body: '維護通知', updated_at: '2026-01-01T00:00:00Z' },
  ],
  personal_notifications: [
    { id: 2, title: '有人回覆', message: '回覆內容', created_at: '2026-01-02T00:00:00Z' },
  ],
  counts: { total: 2 },
}
const slotStub = { template: '<div><slot /><slot name="footer" /></div>' }

describe('NotificationModal', () => {
  it('renders separated unread summaries and clear actions', async () => {
    const wrapper = mount(NotificationModal, {
      props: { visible: true, summary },
      global: {
        stubs: {
          Dialog: slotStub,
          Button: {
            template: '<button @click="$emit(\'click\')"><slot />{{ $attrs.label }}</button>',
          },
          Badge: true,
        },
      },
    })
    expect(wrapper.text()).toContain('公告')
    expect(wrapper.text()).toContain('個人通知')
    expect(wrapper.text()).toContain('系統維護')
    expect(wrapper.text()).toContain('有人回覆')
    expect(wrapper.text()).toContain('2026/01/01 08:00')
    expect(wrapper.text()).toContain('2026/01/02 08:00')
    expect(wrapper.text()).not.toMatch(/上午|下午|凌晨|晚上|AM|PM|剛剛|分鐘前/)
    await wrapper.findAll('button')[0].trigger('click')
    expect(wrapper.emitted('view-announcement')[0]).toEqual([1])
  })
})
