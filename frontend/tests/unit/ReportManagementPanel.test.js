import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import ReportManagementPanel from '@/components/admin/ReportManagementPanel.vue'

const mocks = vi.hoisted(() => ({
  listSystem: vi.fn(),
  listComments: vi.fn(),
  getComment: vi.fn(),
  reviewComment: vi.fn(),
  toast: vi.fn(),
  push: vi.fn(),
}))

vi.mock('@/api', () => ({
  reportService: {
    listSystemIssues: mocks.listSystem,
    listCommentReports: mocks.listComments,
    getCommentReport: mocks.getComment,
    reviewCommentReport: mocks.reviewComment,
  },
}))
vi.mock('@/utils/auth', () => ({ getCurrentUser: () => ({ id: 1, is_admin: true }) }))
vi.mock('primevue/usetoast', () => ({ useToast: () => ({ add: mocks.toast }) }))
vi.mock('primevue/useconfirm', () => ({
  useConfirm: () => ({ require: ({ accept }) => accept() }),
}))
vi.mock('vue-router', () => ({ useRouter: () => ({ push: mocks.push }) }))

const slotStub = { template: '<div><slot /></div>' }

function mountPanel() {
  return mount(ReportManagementPanel, {
    global: {
      stubs: {
        Tabs: slotStub,
        TabList: slotStub,
        Tab: slotStub,
        TabPanels: slotStub,
        TabPanel: slotStub,
        DataTable: slotStub,
        Column: true,
        Dialog: slotStub,
        Button: true,
        InputText: true,
        Select: true,
        Tag: true,
        Message: slotStub,
        Textarea: true,
        Checkbox: true,
      },
    },
  })
}

describe('ReportManagementPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mocks.listSystem.mockResolvedValue({ data: { items: [], total: 0 } })
    mocks.listComments.mockResolvedValue({ data: { items: [], total: 0 } })
  })

  it('keeps the three report sources separated and rejects untrusted GitHub links', async () => {
    const wrapper = mountPanel()
    await flushPromises()

    expect(wrapper.text()).toContain('系統問題回報')
    expect(wrapper.text()).toContain('留言回報')
    expect(wrapper.text()).toContain('考古題回報功能尚未開放')
    expect(mocks.listSystem).toHaveBeenCalled()
    expect(
      wrapper.vm.safeGithubIssueUrl({
        github_issue_number: 12,
        github_issue_url: 'https://evil.example/issues/12',
      })
    ).toBeNull()
    expect(
      wrapper.vm.safeGithubIssueUrl({
        github_issue_number: 12,
        github_issue_url: 'https://github.com/PingScientist/PastExamWeb_PHY/issues/12',
      })
    ).toBe('https://github.com/PingScientist/PastExamWeb_PHY/issues/12')
  })

  it('loads and saves a comment review through the admin API', async () => {
    const report = {
      id: 8,
      status: 'pending',
      admin_response: null,
      source_exists: true,
      reporter_name: 'Reporter',
      comment_author_name: 'Author',
      reason: 'misinformation',
      course_name: 'Course',
      archive_name: 'Exam',
      comment_content_snapshot: 'content',
      thread_id: 3,
    }
    mocks.getComment.mockResolvedValue({ data: report })
    mocks.reviewComment.mockResolvedValue({ data: { ...report, status: 'in_review' } })
    const wrapper = mountPanel()
    await flushPromises()

    await wrapper.vm.openCommentReport(8)
    wrapper.vm.reviewForm.admin_response = '正在確認'
    await wrapper.vm.saveReview()

    expect(mocks.reviewComment).toHaveBeenCalledWith(8, {
      status: 'in_review',
      admin_response: '正在確認',
      delete_comment: false,
    })
    expect(mocks.toast).toHaveBeenCalledWith(expect.objectContaining({ summary: '審核已更新' }))
  })
})
