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
        Column: { props: ['header'], template: '<div class="column-header">{{ header }}</div>' },
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
    expect(mocks.listComments).toHaveBeenCalled()
    expect(wrapper.findAll('.report-section')).toHaveLength(3)
    expect(wrapper.text()).not.toContain('回報編號')
    expect(wrapper.vm.activeTab).toBeUndefined()
    expect(wrapper.vm.archiveListState).toMatchObject({ first: 0, total: 0, loading: false })
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

  it('keeps pagination and server sorting independent for each report list', async () => {
    const wrapper = mountPanel()
    await flushPromises()
    mocks.listSystem.mockClear()
    mocks.listComments.mockClear()

    await wrapper.vm.onSystemPage({ first: 10, rows: 10 })
    await wrapper.vm.onCommentSort({ sortField: 'reason', sortOrder: 1 })

    expect(mocks.listSystem).toHaveBeenLastCalledWith(
      expect.objectContaining({ offset: 10, limit: 10, sort_by: 'created_at' })
    )
    expect(mocks.listComments).toHaveBeenLastCalledWith(
      expect.objectContaining({ offset: 0, sort_by: 'reason', sort_order: 'asc' })
    )
    expect(wrapper.vm.systemPage.first).toBe(10)
    expect(wrapper.vm.commentPage.first).toBe(0)
  })

  it('keeps the available section usable when another report request fails', async () => {
    mocks.listSystem.mockRejectedValueOnce(new Error('system unavailable'))
    mocks.listComments.mockResolvedValueOnce({ data: { items: [{ id: 9 }], total: 1 } })

    const wrapper = mountPanel()
    await flushPromises()

    expect(wrapper.vm.systemError).toContain('無法載入系統問題回報')
    expect(wrapper.vm.commentError).toBe('')
    expect(wrapper.vm.commentReports).toEqual([{ id: 9 }])
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
