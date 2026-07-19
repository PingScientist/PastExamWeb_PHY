import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import ArchiveDiscussionPanel from '@/components/ArchiveDiscussionPanel.vue'

const mocks = vi.hoisted(() => ({
  like: vi.fn(),
  unlike: vi.fn(),
  remove: vi.fn(),
  pin: vi.fn(),
  openSocket: vi.fn(),
  getMe: vi.fn(),
  updateSettings: vi.fn(),
  routerPush: vi.fn(),
  toastAdd: vi.fn(),
}))

vi.mock('@/api', () => ({
  discussionService: {
    likeArchiveMessage: mocks.like,
    unlikeArchiveMessage: mocks.unlike,
    deleteArchiveMessage: mocks.remove,
    pinArchiveMessage: mocks.pin,
    openArchiveDiscussionWebSocket: mocks.openSocket,
  },
  userService: {
    getMe: mocks.getMe,
    updateMyDiscussionSettings: mocks.updateSettings,
  },
}))

vi.mock('@/utils/auth', () => ({
  getCurrentUser: () => ({ id: 7, is_admin: true, name: 'Current User' }),
}))
vi.mock('@/utils/analytics', () => ({
  trackEvent: vi.fn(),
  EVENTS: {
    DISCUSSION_SEND_MESSAGE: 'send',
    DISCUSSION_UPDATE_NICKNAME: 'nickname',
    DISCUSSION_SET_DEFAULT_OPEN: 'default-open',
  },
}))
vi.mock('@/utils/usePreferences', () => ({
  getBooleanPreference: () => true,
  setBooleanPreference: vi.fn(),
}))
vi.mock('@/utils/storage', () => ({
  STORAGE_KEYS: { local: { DISCUSSION_DESKTOP_DEFAULT_OPEN: 'discussion-open' } },
}))
vi.mock('@/utils/submissionLevel', () => ({
  loadContributorLevelSettings: vi.fn(),
}))
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: mocks.routerPush,
    currentRoute: { value: { fullPath: '/archive' } },
  }),
}))

function makeSocket() {
  return {
    readyState: 1,
    send: vi.fn(),
    close: vi.fn(),
    onopen: null,
    onmessage: null,
    onerror: null,
    onclose: null,
  }
}

function mountPanel(socket) {
  mocks.openSocket.mockReturnValue(socket)
  return mount(ArchiveDiscussionPanel, {
    props: { courseId: 1, archiveId: 2 },
    global: {
      provide: {
        toast: { add: mocks.toastAdd },
        confirm: { require: ({ accept }) => accept() },
      },
      stubs: {
        DiscussionMessageCard: { template: '<article />' },
        Button: { template: '<button><slot /></button>' },
        Textarea: { template: '<textarea />' },
        Dialog: { template: '<div><slot /><slot name="footer" /></div>' },
        InputText: { template: '<input />' },
        Checkbox: { template: '<input type="checkbox" />' },
        ProgressSpinner: { template: '<div />' },
      },
    },
  })
}

describe('ArchiveDiscussionPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    globalThis.WebSocket = { OPEN: 1 }
    mocks.getMe.mockResolvedValue({
      data: { name: 'Current User', nickname: 'Current', show_level_title: true },
    })
    mocks.like.mockResolvedValue({ data: { liked: true, like_count: 10 } })
    mocks.unlike.mockResolvedValue({ data: { liked: false, like_count: 9 } })
  })

  it('sorts roots and appends a reply to the existing thread without reloading', async () => {
    const socket = makeSocket()
    const wrapper = mountPanel(socket)
    socket.onopen()
    socket.onmessage({
      data: JSON.stringify({
        type: 'history',
        messages: [
          {
            id: 1,
            user_id: 1,
            user_name: 'Pinned',
            is_pinned: true,
            like_count: 0,
            created_at: '2026-01-01T00:00:00Z',
            replies: [],
          },
          {
            id: 2,
            user_id: 2,
            user_name: 'Popular',
            is_pinned: false,
            like_count: 8,
            created_at: '2026-01-02T00:00:00Z',
            replies: [],
          },
          {
            id: 3,
            user_id: 3,
            user_name: 'Newest',
            is_pinned: false,
            like_count: 0,
            created_at: '2026-01-03T00:00:00Z',
            replies: [],
          },
        ],
      }),
    })
    await flushPromises()

    expect(wrapper.vm.sortedMessages.map((message) => message.id)).toEqual([1, 2, 3])
    wrapper.vm.startReply(wrapper.vm.messages[1])
    wrapper.vm.replyDraft = 'thread reply'
    wrapper.vm.sendReply()
    expect(JSON.parse(socket.send.mock.calls[0][0])).toMatchObject({
      type: 'send',
      content: 'thread reply',
      reply_to_message_id: 2,
    })

    socket.onmessage({
      data: JSON.stringify({
        type: 'message',
        message: {
          id: 20,
          parent_id: 2,
          reply_to_message_id: 2,
          user_id: 7,
          user_name: 'Current',
          content: 'thread reply',
          like_count: 0,
          created_at: '2026-01-04T00:00:00Z',
        },
      }),
    })
    expect(wrapper.vm.messages[1].replies).toHaveLength(1)
    expect(mocks.openSocket).toHaveBeenCalledTimes(1)
  })

  it('rolls back optimistic like state and reports an error when the API fails', async () => {
    const socket = makeSocket()
    const wrapper = mountPanel(socket)
    const message = { id: 5, liked_by_current_user: false, like_count: 4 }
    mocks.like.mockRejectedValueOnce(new Error('network'))

    await wrapper.vm.toggleLike(message)

    expect(message.liked_by_current_user).toBe(false)
    expect(message.like_count).toBe(4)
    expect(mocks.toastAdd).toHaveBeenCalledWith(
      expect.objectContaining({ summary: '愛心更新失敗' })
    )
    expect(wrapper.vm.isLikeLoading(5)).toBe(false)
  })

  it('navigates to the maintainable report route with archive context', () => {
    const wrapper = mountPanel(makeSocket())
    wrapper.vm.openReport({ id: 99 })
    expect(mocks.routerPush).toHaveBeenCalledWith({
      name: 'CommentReport',
      params: { courseId: '1', archiveId: '2', messageId: '99' },
      query: { returnTo: '/archive' },
    })
  })
})
