import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import CommentReport from '@/views/CommentReport.vue'

const mocks = vi.hoisted(() => ({
  list: vi.fn(),
  push: vi.fn(),
  back: vi.fn(),
}))

vi.mock('@/api', () => ({
  discussionService: { listArchiveMessages: mocks.list },
}))
vi.mock('vue-router', () => ({
  useRoute: () => ({
    params: { courseId: '10', archiveId: '20', messageId: '31' },
    query: { returnTo: '/archive' },
  }),
  useRouter: () => ({ push: mocks.push, back: mocks.back }),
}))

describe('CommentReport', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mocks.list.mockResolvedValue({
      data: [
        {
          id: 30,
          user_name: 'Root',
          content: 'Root content',
          created_at: '2026-07-20T00:00:00Z',
          replies: [
            {
              id: 31,
              user_name: 'Reply author',
              content: 'Reply content',
              created_at: '2026-07-20T01:00:00Z',
            },
          ],
        },
      ],
    })
  })

  it('loads a reply summary and returns to the originating route', async () => {
    const wrapper = mount(CommentReport, {
      global: {
        stubs: {
          Button: { template: '<button @click="$emit(\'click\')"><slot /></button>' },
          Card: { template: '<section><slot name="title" /><slot name="content" /></section>' },
          Message: { template: '<div><slot /></div>' },
          ProgressSpinner: { template: '<div />' },
        },
      },
    })
    await flushPromises()

    expect(wrapper.text()).toContain('回報功能尚在建置中')
    expect(wrapper.text()).toContain('Reply author')
    expect(wrapper.text()).toContain('Reply content')
    wrapper.vm.goBack()
    expect(mocks.push).toHaveBeenCalledWith('/archive')
  })
})
