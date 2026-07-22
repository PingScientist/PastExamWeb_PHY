import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import ReportManagementPanel from '@/components/admin/ReportManagementPanel.vue'
import reportManagementSource from '@/components/admin/ReportManagementPanel.vue?raw'

const mocks = vi.hoisted(() => ({
  listSystem: vi.fn(),
  listComments: vi.fn(),
  getComment: vi.fn(),
  reviewComment: vi.fn(),
  deleteSystem: vi.fn(),
  deleteComment: vi.fn(),
  toast: vi.fn(),
  push: vi.fn(),
}))

vi.mock('@/api', () => ({
  reportService: {
    listSystemIssues: mocks.listSystem,
    listCommentReports: mocks.listComments,
    getCommentReport: mocks.getComment,
    reviewCommentReport: mocks.reviewComment,
    deleteSystemIssue: mocks.deleteSystem,
    deleteCommentReport: mocks.deleteComment,
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
    mocks.deleteSystem.mockResolvedValue({ data: { success: true } })
    mocks.deleteComment.mockResolvedValue({ data: { success: true } })
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
    expect(wrapper.find('.report-management__header').exists()).toBe(false)
    expect(wrapper.text()).not.toContain('檢視系統問題摘要並審核留言回報')
    const systemHeaders = wrapper
      .find('.report-management__system-table')
      .findAll('.column-header')
      .map((header) => header.text())
    expect(systemHeaders).toEqual(['回報', '標題與內容', '類型', 'GitHub Issue', '狀態', '操作'])
    expect(systemHeaders).not.toContain('回報時間')
    expect(systemHeaders).not.toContain('回報者')
    const commentHeaders = wrapper
      .find('.report-management__comment-table')
      .findAll('.column-header')
      .map((header) => header.text())
    expect(commentHeaders).toEqual([
      '回報',
      '原因與留言摘要',
      '留言者',
      '課程／考古題',
      '狀態',
      '審核',
      '操作',
    ])
    for (const removedHeader of ['回報時間', '回報者', '留言作者', '審核人', '審核時間']) {
      expect(commentHeaders).not.toContain(removedHeader)
    }
    expect(wrapper.text()).not.toContain('回報編號')
    expect(wrapper.vm.activeTab).toBeUndefined()
    expect(wrapper.vm.archiveListState).toMatchObject({ first: 0, total: 0, loading: false })
    expect(wrapper.vm.formatDateTime('2026-07-20T13:37:00Z', true)).toMatch(/\d{2}:\d{2}/)
    expect(wrapper.vm.formatDateTime('2026-07-20T13:37:00Z', true)).not.toMatch(/上午|下午/)
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

  it('uses compact columns and independently clamps each summary body to three lines', () => {
    const unwantedPdfText = ['本輪不要處理', '行動版 PDF 預覽'].join('')

    expect(reportManagementSource).toContain('system-report-summary__title')
    expect(reportManagementSource).toMatch(
      /\.system-report-summary__title\s*\{[\s\S]*?white-space:\s*nowrap;/
    )
    expect(reportManagementSource).toMatch(
      /\.system-report-summary__body\s*\{[\s\S]*?white-space:\s*normal;[\s\S]*?-webkit-line-clamp:\s*3;/
    )
    expect(reportManagementSource).toMatch(
      /\.comment-report-content__summary\s*\{[\s\S]*?white-space:\s*normal;[\s\S]*?-webkit-line-clamp:\s*3;/
    )
    expect(reportManagementSource).toContain('width: clamp(15rem, 22vw, 21.25rem)')
    expect(reportManagementSource).toContain('header="原因與留言摘要"')
    expect(reportManagementSource).toContain('headerClass="report-user-column"')
    expect(reportManagementSource).toContain('headerClass="report-person-time-column"')
    expect(reportManagementSource).toContain('headerClass="report-review-column"')
    expect(reportManagementSource).toContain('headerClass="report-actions-column"')
    expect(reportManagementSource).toMatch(
      /report-person-time__name[\s\S]*?reporter_name[\s\S]*?report-person-time__time[\s\S]*?created_at/
    )
    expect(reportManagementSource).toContain("data.reviewer_name || '尚未審核'")
    expect(reportManagementSource).toContain(
      '<span v-else class="report-person-time__time">—</span>'
    )
    expect(reportManagementSource).not.toContain(unwantedPdfText)
  })

  it('keeps pagination and server sorting independent for each report list', async () => {
    const wrapper = mountPanel()
    await flushPromises()
    mocks.listSystem.mockClear()
    mocks.listComments.mockClear()

    await wrapper.vm.onSystemPage({ first: 10, rows: 10 })
    await wrapper.vm.onSystemSort({ sortField: 'created_at', sortOrder: 1 })
    await wrapper.vm.onCommentSort({ sortField: 'reviewed_at', sortOrder: -1 })

    expect(mocks.listSystem).toHaveBeenLastCalledWith(
      expect.objectContaining({ offset: 0, limit: 10, sort_by: 'created_at', sort_order: 'asc' })
    )
    expect(mocks.listComments).toHaveBeenLastCalledWith(
      expect.objectContaining({ offset: 0, sort_by: 'reviewed_at', sort_order: 'desc' })
    )
    expect(wrapper.vm.systemPage.first).toBe(0)
    expect(wrapper.vm.commentPage.first).toBe(0)
  })

  it('moves each report type to trash once and clamps an emptied last page', async () => {
    const wrapper = mountPanel()
    await flushPromises()
    wrapper.vm.systemIssues = [{ id: 11, title: 'System' }]
    wrapper.vm.systemTotal = 11
    wrapper.vm.systemPage = { ...wrapper.vm.systemPage, first: 10, rows: 10 }
    wrapper.vm.commentReports = [{ id: 22, reason: 'misinformation' }]
    wrapper.vm.commentTotal = 11
    wrapper.vm.commentPage = { ...wrapper.vm.commentPage, first: 10, rows: 10 }

    wrapper.vm.confirmDeleteSystemIssue({ id: 11, title: 'System' })
    wrapper.vm.confirmDeleteSystemIssue({ id: 11, title: 'System' })
    wrapper.vm.confirmDeleteCommentReport({ id: 22, reason: 'misinformation' })
    wrapper.vm.confirmDeleteCommentReport({ id: 22, reason: 'misinformation' })
    await flushPromises()

    expect(mocks.deleteSystem).toHaveBeenCalledTimes(1)
    expect(mocks.deleteSystem).toHaveBeenCalledWith(11)
    expect(mocks.deleteComment).toHaveBeenCalledTimes(1)
    expect(mocks.deleteComment).toHaveBeenCalledWith(22)
    expect(wrapper.vm.systemPage.first).toBe(0)
    expect(wrapper.vm.commentPage.first).toBe(0)
    expect(mocks.toast).toHaveBeenCalledWith(
      expect.objectContaining({ summary: '回報已移至垃圾桶' })
    )
    expect(reportManagementSource).toContain('aria-label="刪除系統問題回報"')
    expect(reportManagementSource).toContain('aria-label="刪除留言回報"')
    expect(reportManagementSource).toContain(
      '回報會移至垃圾桶，可由管理員在垃圾桶中還原或永久刪除。'
    )
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
