import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import ReportManagementPanel from '@/components/admin/ReportManagementPanel.vue'
import reportManagementSource from '@/components/admin/ReportManagementPanel.vue?raw'

const mocks = vi.hoisted(() => ({
  listSystem: vi.fn(),
  getSystem: vi.fn(),
  updateSystemReadState: vi.fn(),
  listComments: vi.fn(),
  getComment: vi.fn(),
  reviewComment: vi.fn(),
  deleteSystem: vi.fn(),
  deleteComment: vi.fn(),
  confirm: vi.fn((options) => options.accept?.()),
  toast: vi.fn(),
  push: vi.fn(),
}))

vi.mock('@/api', () => ({
  reportService: {
    listSystemIssues: mocks.listSystem,
    getSystemIssue: mocks.getSystem,
    updateSystemIssueReadState: mocks.updateSystemReadState,
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
  useConfirm: () => ({ require: mocks.confirm }),
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
    mocks.getSystem.mockResolvedValue({ data: { id: 1, is_read: false } })
    mocks.updateSystemReadState.mockResolvedValue({ data: { id: 1, is_read: true } })
    mocks.listComments.mockResolvedValue({ data: { items: [], total: 0 } })
    mocks.deleteSystem.mockResolvedValue({ data: { success: true } })
    mocks.deleteComment.mockResolvedValue({ data: { success: true } })
    mocks.confirm.mockImplementation((options) => options.accept?.())
  })

  it('keeps the three report sources separated without per-row GitHub presentation', async () => {
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
    expect(systemHeaders).toEqual(['回報', '標題與內容', '類型', '說明', '狀態', '操作'])
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
    expect(reportManagementSource).not.toContain('header="GitHub Issue"')
    expect(reportManagementSource).not.toContain('label="前往 GitHub"')
    expect(reportManagementSource).toContain('label="前往專案 Issues"')
    expect(reportManagementSource).toContain('rel="noopener noreferrer"')
  })

  it('opens a full local-summary detail without unsafe HTML', async () => {
    const wrapper = mountPanel()
    await flushPromises()
    const report = {
      id: 12,
      reporter_name: '回報者',
      created_at: '2026-07-22T10:00:00Z',
      report_type: 'bug',
      title: '完整標題',
      description: '第一行\n第二行很長的完整內容',
      contact: null,
    }

    mocks.getSystem.mockResolvedValue({ data: report })
    await wrapper.vm.openSystemReport(report)
    await flushPromises()

    expect(wrapper.vm.systemDetailVisible).toBe(true)
    expect(wrapper.vm.selectedSystemReport).toEqual(report)
    expect(wrapper.text()).toContain('完整標題')
    expect(wrapper.text()).toContain('第一行\n第二行很長的完整內容')
    expect(wrapper.text()).toContain('未提供')
    expect(wrapper.text()).toContain('無法確認使用者是否已在 GitHub 正式建立 Issue')
    expect(reportManagementSource).not.toContain('v-html')
    expect(reportManagementSource).toContain('aria-label="檢視系統問題回報"')
    expect(mocks.getSystem).toHaveBeenCalledWith(report.id)
    expect(mocks.updateSystemReadState).not.toHaveBeenCalled()
  })

  it('updates read state only after explicit save and supports marking unread again', async () => {
    const report = {
      id: 42,
      reporter_name: '回報者',
      report_type: 'bug',
      title: '問題',
      description: '內容',
      is_read: false,
      read_at: null,
      read_by_username: null,
    }
    mocks.getSystem.mockResolvedValue({ data: report })
    mocks.updateSystemReadState
      .mockResolvedValueOnce({
        data: {
          ...report,
          is_read: true,
          read_at: '2026-07-22T12:00:00Z',
          read_by_username: '管理員',
        },
      })
      .mockResolvedValueOnce({ data: { ...report, is_read: false } })
    const wrapper = mountPanel()
    await flushPromises()

    await wrapper.vm.openSystemReport(report)
    expect(mocks.updateSystemReadState).not.toHaveBeenCalled()

    wrapper.vm.systemReadForm = true
    await wrapper.vm.saveSystemReadState()
    expect(mocks.updateSystemReadState).toHaveBeenNthCalledWith(1, report.id, true)
    expect(wrapper.vm.selectedSystemReport.is_read).toBe(true)

    wrapper.vm.systemReadForm = false
    await wrapper.vm.saveSystemReadState()
    expect(mocks.updateSystemReadState).toHaveBeenNthCalledWith(2, report.id, false)
    expect(wrapper.vm.selectedSystemReport.is_read).toBe(false)
    expect(mocks.toast).toHaveBeenCalledWith(expect.objectContaining({ summary: '閱讀狀態已更新' }))
  })

  it('keeps the previous read state when saving fails', async () => {
    const report = { id: 52, is_read: false }
    mocks.getSystem.mockResolvedValue({ data: report })
    mocks.updateSystemReadState.mockRejectedValueOnce(new Error('unavailable'))
    const wrapper = mountPanel()
    await flushPromises()
    await wrapper.vm.openSystemReport(report)

    wrapper.vm.systemReadForm = true
    await wrapper.vm.saveSystemReadState()

    expect(wrapper.vm.selectedSystemReport.is_read).toBe(false)
    expect(wrapper.vm.systemReadForm).toBe(false)
    expect(mocks.toast).toHaveBeenCalledWith(expect.objectContaining({ summary: '更新失敗' }))
  })

  it('uses compact columns and independently clamps each summary body to three lines', () => {
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
  })

  it('keeps both report action groups aligned without wrapping button labels', () => {
    expect(reportManagementSource.match(/class="report-row-actions"/g)).toHaveLength(2)
    expect(reportManagementSource).toContain(
      'headerClass="report-actions-column report-actions-column--system"'
    )
    expect(reportManagementSource).toContain('style="width: 12rem; min-width: 12rem"')
    expect(reportManagementSource).toContain('style="width: 17rem; min-width: 17rem"')
    expect(reportManagementSource).toMatch(
      /\.report-row-actions\s*\{[\s\S]*?display:\s*inline-flex;[\s\S]*?align-items:\s*center;[\s\S]*?justify-content:\s*flex-end;[\s\S]*?flex-wrap:\s*nowrap;/
    )
    expect(reportManagementSource).toMatch(
      /\.report-row-actions :deep\(\.p-button\)\s*\{[\s\S]*?white-space:\s*nowrap;/
    )
    expect(reportManagementSource).toContain(
      ':deep(.report-actions-column:not(.report-actions-column--system))'
    )
    expect(reportManagementSource).toMatch(
      /@media \(max-width: 1199px\)[\s\S]*?\.report-row-actions\s*\{\s*justify-content:\s*flex-start;\s*padding-inline-end:\s*0;\s*\}/
    )
  })

  it('keeps pagination and server sorting independent for each report list', async () => {
    const wrapper = mountPanel()
    await flushPromises()
    mocks.listSystem.mockClear()
    mocks.listComments.mockClear()

    await wrapper.vm.onSystemPage({ first: 10, rows: 10 })
    wrapper.vm.systemFilters.readState = 'unread'
    await wrapper.vm.applySystemFilters()
    await wrapper.vm.onSystemSort({ sortField: 'created_at', sortOrder: 1 })
    await wrapper.vm.onCommentSort({ sortField: 'reviewed_at', sortOrder: -1 })

    expect(mocks.listSystem).toHaveBeenLastCalledWith(
      expect.objectContaining({
        offset: 0,
        limit: 10,
        read_state: 'unread',
        sort_by: 'created_at',
        sort_order: 'asc',
      })
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
    mocks.reviewComment.mockResolvedValue({ data: { ...report, status: 'upheld' } })
    const wrapper = mountPanel()
    await flushPromises()

    await wrapper.vm.openCommentReport(8)
    wrapper.vm.reviewForm.status = 'upheld'
    wrapper.vm.reviewForm.admin_response = '   '
    await wrapper.vm.saveReview()

    expect(mocks.reviewComment).toHaveBeenCalledWith(8, {
      status: 'upheld',
      admin_response: null,
      delete_comment: false,
    })
    expect(mocks.toast).toHaveBeenCalledWith(expect.objectContaining({ summary: '審核已更新' }))
    expect(wrapper.vm.statusLabel('pending')).toBe('待審核')
    expect(wrapper.vm.statusLabel('upheld')).toBe('回報成立')
    expect(wrapper.vm.statusLabel('dismissed')).toBe('回報不成立')
    expect(wrapper.vm.statusSeverity('pending')).toBe('warn')
    expect(wrapper.vm.statusSeverity('upheld')).toBe('success')
    expect(wrapper.vm.statusSeverity('dismissed')).toBe('danger')
    expect(reportManagementSource).not.toContain('in_review')
    expect(reportManagementSource).toContain("selectedReport.admin_response || '未提供答覆'")
  })

  it('uses a localized final-review confirmation and sends at most one request', async () => {
    const report = {
      id: 18,
      status: 'pending',
      admin_response: null,
      source_exists: true,
      reporter_name: 'Reporter',
      comment_author_name: 'Author',
      reason: 'misinformation',
      course_name: 'Course',
      archive_name: 'Exam',
      comment_content_snapshot: 'content',
    }
    mocks.getComment.mockResolvedValue({ data: report })
    mocks.reviewComment.mockResolvedValue({ data: { ...report, status: 'upheld' } })
    mocks.confirm.mockImplementation((options) => {
      options.accept?.()
      options.accept?.()
    })
    const wrapper = mountPanel()
    await flushPromises()
    await wrapper.vm.openCommentReport(report.id)
    wrapper.vm.reviewForm.status = 'upheld'

    wrapper.vm.confirmSaveReview()
    await flushPromises()

    expect(mocks.confirm).toHaveBeenCalledWith(
      expect.objectContaining({
        header: '確認送出審核結果',
        message: expect.stringContaining('送出後將通知回報者。'),
        rejectLabel: '取消',
        acceptLabel: '確認送出',
        defaultFocus: 'reject',
      })
    )
    expect(mocks.confirm.mock.calls[0][0].message).toContain(
      '審核結果與管理員答覆送出後將無法修改。'
    )
    expect(mocks.reviewComment).toHaveBeenCalledTimes(1)
  })

  it('cancels without an API call and warns when the source comment will be deleted', async () => {
    const report = {
      id: 28,
      status: 'pending',
      admin_response: null,
      source_exists: true,
      reporter_name: 'Reporter',
      comment_author_name: 'Author',
      reason: 'misinformation',
      course_name: 'Course',
      archive_name: 'Exam',
      comment_content_snapshot: 'content',
    }
    mocks.getComment.mockResolvedValue({ data: report })
    mocks.confirm.mockImplementation(() => {})
    const wrapper = mountPanel()
    await flushPromises()
    await wrapper.vm.openCommentReport(report.id)
    wrapper.vm.reviewForm.status = 'upheld'
    wrapper.vm.reviewForm.delete_comment = true

    wrapper.vm.confirmSaveReview()

    const options = mocks.confirm.mock.calls[0][0]
    expect(options.message).toContain('被回報留言將永久刪除，無法復原，也不會進入垃圾桶。')
    expect(options.acceptClass).toBe('p-button-danger')
    expect(mocks.reviewComment).not.toHaveBeenCalled()
  })

  it('keeps finalized reports read-only in the dialog and API handler', async () => {
    const finalized = {
      id: 38,
      status: 'dismissed',
      admin_response: '審核完成',
      source_exists: true,
    }
    mocks.getComment.mockResolvedValue({ data: finalized })
    const wrapper = mountPanel()
    await flushPromises()
    await wrapper.vm.openCommentReport(finalized.id)

    await wrapper.vm.saveReview()

    expect(mocks.reviewComment).not.toHaveBeenCalled()
    expect(reportManagementSource).toContain('審核結果已送出，無法修改。')
    expect(reportManagementSource).toContain("isFinal(data.status) ? '檢視' : '檢視／審核'")
    expect(reportManagementSource).toContain('v-if="!isFinal(selectedReport.status)"')
  })
})
