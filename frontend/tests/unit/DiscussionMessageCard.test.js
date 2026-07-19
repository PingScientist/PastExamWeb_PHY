import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import DiscussionMessageCard from '@/components/DiscussionMessageCard.vue'

const ButtonStub = {
  inheritAttrs: false,
  props: ['label'],
  emits: ['click'],
  template: '<button v-bind="$attrs" @click="$emit(\'click\')">{{ label }}</button>',
}

describe('DiscussionMessageCard', () => {
  it('keeps time below wrapping author metadata and exposes ordered accessible actions', () => {
    const wrapper = mount(DiscussionMessageCard, {
      props: {
        message: {
          id: 1,
          user_name: '這是一個非常長的留言者名稱',
          author_show_level_title: true,
          author_experience: 54,
          content: '留言內容',
          is_pinned: true,
          liked_by_current_user: true,
          like_count: 1234,
          created_at: '2026-07-20T08:00:00Z',
        },
        canPin: true,
        canDelete: true,
      },
      global: {
        stubs: {
          Button: ButtonStub,
          Tag: { template: '<span><slot /></span>' },
        },
      },
    })

    const authorBlock = wrapper.get('.discussion-card__author-block')
    expect(authorBlock.find('.discussion-card__author-line').exists()).toBe(true)
    expect(authorBlock.find('time.discussion-card__time').exists()).toBe(true)
    expect(wrapper.get('.discussion-card__like-button').text()).toContain('1234')

    const labels = wrapper.findAll('button').map((button) => button.attributes('aria-label'))
    expect(labels).toEqual(['回覆留言', '取消愛心', '取消置頂', '回報留言', '刪除留言'])
  })
})
