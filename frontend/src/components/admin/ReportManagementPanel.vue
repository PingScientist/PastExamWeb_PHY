<template>
  <section class="report-management" aria-label="回報管理">
    <section class="report-section" aria-labelledby="system-report-heading">
      <div class="report-section__header">
        <div>
          <h4 id="system-report-heading">系統問題回報</h4>
          <p>檢視使用者提交的系統問題摘要與 GitHub Issue 連結狀態。</p>
        </div>
        <div class="report-section__actions">
          <Button
            as="a"
            href="https://github.com/PingScientist/PastExamWeb_PHY/issues"
            target="_blank"
            rel="noopener noreferrer"
            label="前往專案 Issues"
            icon="pi pi-github"
            outlined
            size="small"
          />
          <Button
            icon="pi pi-refresh"
            label="重新整理"
            outlined
            :loading="loading"
            @click="refreshAll"
          />
        </div>
      </div>
      <div class="report-management__filters">
        <InputText
          v-model="systemFilters.search"
          placeholder="搜尋標題、回報者或內容摘要"
          @keyup.enter="applySystemFilters"
        />
        <Select
          v-model="systemFilters.type"
          :options="systemTypeOptions"
          optionLabel="label"
          optionValue="value"
          placeholder="全部類型"
          showClear
          @change="applySystemFilters"
        />
        <Select
          v-model="systemFilters.status"
          :options="systemStatusOptions"
          optionLabel="label"
          optionValue="value"
          placeholder="全部狀態"
          showClear
          @change="applySystemFilters"
        />
        <Button label="搜尋" icon="pi pi-search" outlined @click="applySystemFilters" />
      </div>
      <Message v-if="systemError" severity="error" :closable="false">{{ systemError }}</Message>
      <DataTable
        v-else
        :value="systemIssues"
        :loading="loadingSystem"
        lazy
        paginator
        :first="systemPage.first"
        :rows="systemPage.rows"
        :totalRecords="systemTotal"
        :rowsPerPageOptions="PAGE_SIZE_OPTIONS"
        paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink RowsPerPageDropdown CurrentPageReport"
        currentPageReportTemplate="第 {currentPage} / {totalPages} 頁，共 {totalRecords} 筆"
        :sortField="systemPage.sortField"
        :sortOrder="systemPage.sortOrder"
        responsiveLayout="stack"
        breakpoint="1023px"
        class="report-management__table report-management__system-table admin-data-table"
        tableStyle="table-layout: fixed; min-width: 60rem"
        @page="onSystemPage"
        @sort="onSystemSort"
      >
        <template #empty>目前沒有系統問題回報</template>
        <Column
          field="created_at"
          sortField="created_at"
          header="回報"
          sortable
          headerClass="report-person-time-column"
          bodyClass="report-person-time-column"
          style="width: 10rem; min-width: 10rem"
          ><template #body="{ data }"
            ><div class="report-person-time">
              <span class="report-person-time__name" :title="data.reporter_name">
                {{ data.reporter_name }}
              </span>
              <time class="report-person-time__time" :datetime="data.created_at">
                {{ formatDateTime(data.created_at, true) }}
              </time>
            </div>
          </template>
        </Column>
        <Column
          field="title"
          sortField="title"
          header="標題與內容"
          sortable
          headerClass="system-report-column"
          bodyClass="system-report-column"
          style="width: clamp(15rem, 22vw, 21.25rem)"
          ><template #body="{ data }"
            ><div class="system-report-summary">
              <strong class="system-report-summary__title" :title="data.title || '未命名回報'">
                {{ data.title || '未命名回報' }}
              </strong>
              <span class="system-report-summary__body">{{ data.description || '—' }}</span>
            </div></template
          ></Column
        >
        <Column
          field="report_type"
          sortField="report_type"
          header="類型"
          sortable
          style="width: 8rem"
          ><template #body="{ data }"><Tag :value="issueTypeLabel(data.report_type)" /></template
        ></Column>
        <Column header="GitHub Issue" style="width: 9rem"
          ><template #body="{ data }">{{
            data.github_issue_number ? `#${data.github_issue_number}` : '尚未連結'
          }}</template></Column
        >
        <Column field="status" sortField="status" header="狀態" sortable style="width: 8rem"
          ><template #body><Tag severity="secondary" value="本地摘要" /></template
        ></Column>
        <Column header="操作" style="width: 10rem"
          ><template #body="{ data }"
            ><Button
              as="a"
              :href="safeGithubIssueUrl(data) || undefined"
              target="_blank"
              rel="noopener noreferrer"
              label="前往 GitHub"
              icon="pi pi-external-link"
              size="small"
              outlined
              :disabled="!safeGithubIssueUrl(data)" /></template
        ></Column>
      </DataTable>
    </section>

    <section class="report-section" aria-labelledby="comment-report-heading">
      <div class="report-section__header">
        <div>
          <h4 id="comment-report-heading">留言回報</h4>
          <p>依狀態、原因與內容搜尋留言回報，並開啟詳情完成審核。</p>
        </div>
      </div>
      <div class="report-management__filters">
        <InputText
          v-model="commentFilters.search"
          placeholder="搜尋留言、課程或使用者"
          @keyup.enter="applyCommentFilters"
        />
        <Select
          v-model="commentFilters.status"
          :options="statusOptions"
          optionLabel="label"
          optionValue="value"
          placeholder="全部狀態"
          showClear
          @change="applyCommentFilters"
        />
        <Select
          v-model="commentFilters.reason"
          :options="reasonOptions"
          optionLabel="label"
          optionValue="value"
          placeholder="全部原因"
          showClear
          @change="applyCommentFilters"
        />
        <Button label="搜尋" icon="pi pi-search" outlined @click="applyCommentFilters" />
      </div>
      <Message v-if="commentError" severity="error" :closable="false">{{ commentError }}</Message>
      <DataTable
        v-else
        :value="commentReports"
        :loading="loadingComments"
        lazy
        paginator
        :first="commentPage.first"
        :rows="commentPage.rows"
        :totalRecords="commentTotal"
        :rowsPerPageOptions="PAGE_SIZE_OPTIONS"
        paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink RowsPerPageDropdown CurrentPageReport"
        currentPageReportTemplate="第 {currentPage} / {totalPages} 頁，共 {totalRecords} 筆"
        :sortField="commentPage.sortField"
        :sortOrder="commentPage.sortOrder"
        responsiveLayout="stack"
        breakpoint="1199px"
        class="report-management__table report-management__comment-table admin-data-table"
        tableStyle="table-layout: fixed; min-width: 75rem"
        @page="onCommentPage"
        @sort="onCommentSort"
      >
        <template #empty>目前沒有符合條件的留言回報</template>
        <Column
          field="created_at"
          sortField="created_at"
          header="回報"
          sortable
          headerClass="report-person-time-column"
          bodyClass="report-person-time-column"
          style="width: 9.5rem; min-width: 9.5rem"
          ><template #body="{ data }"
            ><div class="report-person-time">
              <span class="report-person-time__name" :title="data.reporter_name">
                {{ data.reporter_name }}
              </span>
              <time class="report-person-time__time" :datetime="data.created_at">
                {{ formatDateTime(data.created_at, true) }}
              </time>
            </div>
          </template>
        </Column>
        <Column
          field="reason"
          sortField="reason"
          header="原因與留言摘要"
          sortable
          headerClass="comment-report-content-column"
          bodyClass="comment-report-content-column"
          style="width: clamp(16rem, 24vw, 20rem)"
          ><template #body="{ data }"
            ><div class="comment-report-content" :title="data.comment_content_snapshot">
              <strong class="comment-report-content__reason" :title="reasonLabel(data.reason)">
                {{ reasonLabel(data.reason) }}
              </strong>
              <span class="comment-report-content__summary">{{
                data.comment_content_snapshot || '—'
              }}</span>
            </div>
          </template>
        </Column>
        <Column
          field="comment_author_name"
          sortField="comment_author"
          header="留言者"
          sortable
          headerClass="report-user-column"
          bodyClass="report-user-column"
          style="width: 7rem; min-width: 7rem"
          ><template #body="{ data }"
            ><span class="report-user-cell__text" :title="data.comment_author_name">{{
              data.comment_author_name
            }}</span></template
          ></Column
        >
        <Column sortField="course_archive" header="課程／考古題" sortable style="width: 11rem"
          ><template #body="{ data }"
            ><div class="report-management__summary">
              <span>{{ data.course_name }}</span
              ><small>{{ data.archive_name }}</small>
            </div></template
          ></Column
        >
        <Column field="status" sortField="status" header="狀態" sortable style="width: 8rem"
          ><template #body="{ data }"
            ><Tag :severity="statusSeverity(data.status)" :value="statusLabel(data.status)"
          /></template>
        </Column>
        <Column
          field="reviewed_at"
          sortField="reviewed_at"
          header="審核"
          sortable
          headerClass="report-review-column"
          bodyClass="report-review-column"
          style="width: 10rem; min-width: 10rem"
          ><template #body="{ data }"
            ><div class="report-person-time">
              <span
                class="report-person-time__name"
                :class="{ 'report-person-time__name--empty': !data.reviewer_name }"
                :title="data.reviewer_name || '尚未審核'"
              >
                {{ data.reviewer_name || '尚未審核' }}
              </span>
              <time
                v-if="data.reviewed_at"
                class="report-person-time__time"
                :datetime="data.reviewed_at"
              >
                {{ formatDateTime(data.reviewed_at, true) }}
              </time>
              <span v-else class="report-person-time__time">—</span>
            </div>
          </template>
        </Column>
        <Column
          header="操作"
          headerClass="report-actions-column"
          bodyClass="report-actions-column"
          style="width: 9.5rem; min-width: 9.5rem"
          ><template #body="{ data }"
            ><Button
              label="檢視／審核"
              icon="pi pi-search"
              size="small"
              outlined
              @click="openCommentReport(data.id)" /></template
        ></Column>
      </DataTable>
    </section>

    <section
      class="report-section"
      aria-labelledby="archive-report-heading"
      :aria-busy="archiveListState.loading"
    >
      <div class="report-section__header">
        <div>
          <h4 id="archive-report-heading">考古題回報</h4>
          <p>此區段預留未來的考古題回報列表與獨立查詢狀態。</p>
        </div>
      </div>
      <div class="report-management__empty">
        <i class="pi pi-file-pdf" aria-hidden="true" /><strong>考古題回報功能尚未開放</strong
        ><span>目前沒有資料表、分頁或送出流程。</span>
      </div>
    </section>

    <Dialog
      v-model:visible="reviewVisible"
      modal
      header="留言回報審核"
      :style="{ width: '720px', maxWidth: '94vw' }"
      :draggable="false"
    >
      <div v-if="selectedReport" class="report-review">
        <div class="report-review__title">
          <div>
            <strong>留言回報</strong>
            <small>{{ formatDateTime(selectedReport.created_at) }}</small>
          </div>
          <Tag
            :severity="statusSeverity(selectedReport.status)"
            :value="statusLabel(selectedReport.status)"
          />
        </div>
        <dl class="report-review__meta">
          <div>
            <dt>回報者</dt>
            <dd>{{ selectedReport.reporter_name }}</dd>
          </div>
          <div>
            <dt>留言作者</dt>
            <dd>{{ selectedReport.comment_author_name }}</dd>
          </div>
          <div>
            <dt>回報原因</dt>
            <dd>{{ reasonLabel(selectedReport.reason) }}</dd>
          </div>
          <div>
            <dt>建立時間</dt>
            <dd>{{ formatDateTime(selectedReport.created_at) }}</dd>
          </div>
          <div>
            <dt>所屬考古題</dt>
            <dd>{{ selectedReport.course_name }} · {{ selectedReport.archive_name }}</dd>
          </div>
          <div>
            <dt>Thread</dt>
            <dd>{{ selectedReport.thread_id || '—' }}</dd>
          </div>
        </dl>
        <section class="report-review__quote">
          <strong>留言內容快照</strong>
          <p>{{ selectedReport.comment_content_snapshot }}</p>
          <small>{{ formatDateTime(selectedReport.comment_created_at_snapshot) }}</small>
        </section>
        <Message v-if="!selectedReport.source_exists" severity="warn" :closable="false">
          來源留言已不存在；仍可根據快照完成審核。
        </Message>
        <p v-if="selectedReport.custom_message">
          <strong>回報者補充：</strong>{{ selectedReport.custom_message }}
        </p>
        <div class="report-review__field">
          <label for="report-review-status">審核結果</label>
          <Select
            inputId="report-review-status"
            v-model="reviewForm.status"
            :options="reviewStatusOptions"
            optionLabel="label"
            optionValue="value"
            :disabled="isFinal(selectedReport.status)"
          />
        </div>
        <div class="report-review__field">
          <label for="report-admin-response">給回報者的答覆</label>
          <Textarea
            id="report-admin-response"
            v-model="reviewForm.admin_response"
            rows="4"
            maxlength="1000"
            :disabled="isFinal(selectedReport.status)"
          />
          <small>{{ reviewForm.admin_response.length }}/1000</small>
        </div>
        <label v-if="reviewForm.status === 'upheld'" class="report-review__delete-option">
          <Checkbox
            v-model="reviewForm.delete_comment"
            binary
            :disabled="!selectedReport.source_exists"
          />
          同時刪除來源留言（使用既有留言刪除政策）
        </label>
        <div class="report-review__actions">
          <Button
            label="前往來源"
            icon="pi pi-external-link"
            severity="secondary"
            text
            :disabled="!selectedReport.source_exists"
            @click="openReportSource"
          />
          <span class="report-review__spacer" />
          <Button label="關閉" severity="secondary" outlined @click="reviewVisible = false" />
          <Button
            label="儲存審核"
            icon="pi pi-check"
            :loading="reviewSaving"
            :disabled="isFinal(selectedReport.status) || !canSaveReview"
            @click="confirmSaveReview"
          />
        </div>
      </div>
    </Dialog>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import { useRouter } from 'vue-router'
import { reportService } from '@/api'
import { getCurrentUser } from '@/utils/auth'

const confirm = useConfirm()
const toast = useToast()
const router = useRouter()
const PAGE_SIZE_OPTIONS = [10, 20, 50]
const loadingSystem = ref(false)
const loadingComments = ref(false)
const systemIssues = ref([])
const systemTotal = ref(0)
const systemError = ref('')
const commentReports = ref([])
const commentTotal = ref(0)
const commentError = ref('')
const reviewVisible = ref(false)
const reviewSaving = ref(false)
const selectedReport = ref(null)
const systemFilters = ref({ search: '', type: null, status: null })
const commentFilters = ref({ search: '', status: null, reason: null })
const systemPage = ref({ first: 0, rows: 10, sortField: 'created_at', sortOrder: -1 })
const commentPage = ref({ first: 0, rows: 10, sortField: 'created_at', sortOrder: -1 })
const archiveListState = ref({
  first: 0,
  rows: 10,
  total: 0,
  sortField: 'created_at',
  sortOrder: -1,
  search: '',
  filter: null,
  loading: false,
  error: '',
})
const reviewForm = ref({ status: 'in_review', admin_response: '', delete_comment: false })
const loading = computed(() => loadingSystem.value || loadingComments.value)

const reasonOptions = [
  { label: '垃圾訊息或重複洗版', value: 'spam_or_duplicate' },
  { label: '攻擊、騷擾或不友善內容', value: 'harassment_or_hostility' },
  { label: '不當或違法內容', value: 'inappropriate_or_illegal' },
  { label: '洩漏個人資料或隱私', value: 'privacy_violation' },
  { label: '錯誤或誤導資訊', value: 'misinformation' },
  { label: '其他', value: 'other' },
]
const systemTypeOptions = [
  { label: '程式錯誤', value: 'bug' },
  { label: '功能建議', value: 'enhancement' },
  { label: '效能問題', value: 'performance' },
  { label: 'UI/UX', value: 'ui-ux' },
  { label: '其他', value: 'question' },
]
const systemStatusOptions = [{ label: '本地摘要', value: 'local_only' }]
const statusOptions = [
  { label: '待處理', value: 'pending' },
  { label: '審核中', value: 'in_review' },
  { label: '回報成立／已處理', value: 'upheld' },
  { label: '回報不成立', value: 'dismissed' },
]
const reviewStatusOptions = statusOptions.filter((item) => item.value !== 'pending')
const canSaveReview = computed(() => {
  if (!reviewForm.value.status) return false
  if (['upheld', 'dismissed'].includes(reviewForm.value.status)) {
    return Boolean(reviewForm.value.admin_response.trim())
  }
  return true
})

function ensureAdmin() {
  if (!getCurrentUser()?.is_admin) throw new Error('Admin access required')
}
async function loadSystemIssues() {
  ensureAdmin()
  loadingSystem.value = true
  systemError.value = ''
  try {
    const { data } = await reportService.listSystemIssues({
      search: systemFilters.value.search.trim() || undefined,
      report_type: systemFilters.value.type || undefined,
      status: systemFilters.value.status || undefined,
      sort_by: systemPage.value.sortField,
      sort_order: systemPage.value.sortOrder === 1 ? 'asc' : 'desc',
      limit: systemPage.value.rows,
      offset: systemPage.value.first,
    })
    systemIssues.value = data.items || []
    systemTotal.value = Number(data.total || 0)
  } catch (error) {
    console.error('Load system issue reports error:', error)
    systemError.value = '無法載入系統問題回報，請重新整理後再試。'
    toast.add({
      severity: 'error',
      summary: '載入失敗',
      detail: '無法載入系統問題回報',
      life: 3000,
    })
  } finally {
    loadingSystem.value = false
  }
}
async function loadCommentReports() {
  ensureAdmin()
  loadingComments.value = true
  commentError.value = ''
  try {
    const { data } = await reportService.listCommentReports({
      search: commentFilters.value.search.trim() || undefined,
      status: commentFilters.value.status || undefined,
      reason: commentFilters.value.reason || undefined,
      sort_by: commentPage.value.sortField,
      sort_order: commentPage.value.sortOrder === 1 ? 'asc' : 'desc',
      limit: commentPage.value.rows,
      offset: commentPage.value.first,
    })
    commentReports.value = data.items || []
    commentTotal.value = Number(data.total || 0)
  } catch (error) {
    console.error('Load comment reports error:', error)
    commentError.value = '無法載入留言回報，請重新整理後再試。'
    toast.add({ severity: 'error', summary: '載入失敗', detail: '無法載入留言回報', life: 3000 })
  } finally {
    loadingComments.value = false
  }
}
function applySystemFilters() {
  systemPage.value.first = 0
  return loadSystemIssues()
}
function applyCommentFilters() {
  commentPage.value.first = 0
  return loadCommentReports()
}
function onSystemPage(event) {
  systemPage.value.first = event.first
  systemPage.value.rows = event.rows
  return loadSystemIssues()
}
function onCommentPage(event) {
  commentPage.value.first = event.first
  commentPage.value.rows = event.rows
  return loadCommentReports()
}
function onSystemSort(event) {
  systemPage.value.first = 0
  systemPage.value.sortField = event.sortField || 'created_at'
  systemPage.value.sortOrder = event.sortOrder || -1
  return loadSystemIssues()
}
function onCommentSort(event) {
  commentPage.value.first = 0
  commentPage.value.sortField = event.sortField || 'created_at'
  commentPage.value.sortOrder = event.sortOrder || -1
  return loadCommentReports()
}
function refreshAll() {
  return Promise.allSettled([loadSystemIssues(), loadCommentReports()])
}
async function openCommentReport(id) {
  try {
    const { data } = await reportService.getCommentReport(id)
    selectedReport.value = data
    reviewForm.value = {
      status: data.status === 'pending' ? 'in_review' : data.status,
      admin_response: data.admin_response || '',
      delete_comment: false,
    }
    reviewVisible.value = true
  } catch (error) {
    console.error('Load comment report detail error:', error)
    toast.add({ severity: 'error', summary: '載入失敗', detail: '無法載入回報詳情', life: 3000 })
  }
}
function confirmSaveReview() {
  const finalResult = ['upheld', 'dismissed'].includes(reviewForm.value.status)
  confirm.require({
    header: finalResult ? '確認送出最終審核結果' : '確認更新審核狀態',
    message: reviewForm.value.delete_comment
      ? '此操作會刪除來源留言並送出最終通知，確定繼續？'
      : finalResult
        ? '最終結果送出後不可變更，確定繼續？'
        : '確定將此回報標記為審核中？',
    icon: reviewForm.value.delete_comment ? 'pi pi-exclamation-triangle' : 'pi pi-question-circle',
    accept: saveReview,
  })
}
async function saveReview() {
  if (!selectedReport.value || !canSaveReview.value) return
  reviewSaving.value = true
  try {
    const { data } = await reportService.reviewCommentReport(selectedReport.value.id, {
      status: reviewForm.value.status,
      admin_response: reviewForm.value.admin_response.trim() || null,
      delete_comment: reviewForm.value.delete_comment,
    })
    selectedReport.value = data
    toast.add({
      severity: 'success',
      summary: '審核已更新',
      detail: '留言回報審核狀態已更新',
      life: 3000,
    })
    await loadCommentReports()
  } catch (error) {
    console.error('Review comment report error:', error)
    toast.add({ severity: 'error', summary: '更新失敗', detail: '回報狀態未變更', life: 3000 })
  } finally {
    reviewSaving.value = false
  }
}
function openReportSource() {
  const item = selectedReport.value
  if (!item?.source_exists) return
  reviewVisible.value = false
  router.push({
    path: '/archive',
    query: {
      courseId: item.course_id,
      archiveId: item.archive_id,
      threadId: item.thread_id,
      messageId: item.comment_id,
    },
  })
}
function reasonLabel(value) {
  return reasonOptions.find((item) => item.value === value)?.label || value
}
function statusLabel(value) {
  return statusOptions.find((item) => item.value === value)?.label || value
}
function statusSeverity(value) {
  return (
    { pending: 'warn', in_review: 'info', upheld: 'success', dismissed: 'secondary' }[value] ||
    'secondary'
  )
}
function issueTypeLabel(value) {
  return (
    {
      bug: '程式錯誤',
      enhancement: '功能建議',
      performance: '效能問題',
      'ui-ux': 'UI/UX',
      question: '其他',
    }[value] || value
  )
}
function isFinal(value) {
  return ['upheld', 'dismissed'].includes(value)
}
function safeGithubIssueUrl(item) {
  const url = String(item?.github_issue_url || '')
  const match = url.match(
    /^https:\/\/github\.com\/PingScientist\/PastExamWeb_PHY\/issues\/([1-9][0-9]*)$/
  )
  return match && Number(match[1]) === Number(item.github_issue_number) ? url : null
}
function formatDateTime(value, force24Hour = false) {
  if (!value) return '—'
  const options = {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }
  if (force24Hour) options.hour12 = false
  return new Date(value).toLocaleString('zh-TW', options)
}

onMounted(refreshAll)
</script>

<style scoped>
.report-management {
  min-width: 0;
}
.report-section__header,
.report-review__actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}
.report-section {
  min-width: 0;
  padding-block: 1.25rem;
  border-bottom: 1px solid var(--surface-border);
}
.report-section:first-of-type {
  padding-top: 0;
}
.report-section:last-of-type {
  border-bottom: 0;
}
.report-section__header h4 {
  margin: 0;
  color: var(--text-color);
  font-size: 1.05rem;
}
.report-section__header p {
  margin: 0.25rem 0 0;
  color: var(--text-color-secondary);
}
.report-section__actions {
  display: inline-flex;
  align-items: center;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.report-management__filters {
  display: grid;
  grid-template-columns: minmax(12rem, 1fr) repeat(2, minmax(10rem, auto)) auto;
  gap: 0.6rem;
  margin-block: 1rem;
}
.report-management__table {
  width: 100%;
}
.report-management__summary {
  display: flex;
  min-width: 10rem;
  flex-direction: column;
  gap: 0.2rem;
  overflow-wrap: anywhere;
}
.report-management__summary small,
.report-management__summary span {
  color: var(--text-color-secondary);
}
.system-report-summary {
  display: grid;
  width: 100%;
  min-width: 0;
  max-width: 100%;
  overflow: hidden;
  white-space: normal;
}
:deep(.system-report-column) {
  width: clamp(15rem, 22vw, 21.25rem);
  max-width: 21.25rem;
  overflow: hidden;
  white-space: normal;
}
.system-report-summary__title {
  display: block;
  min-width: 0;
  max-width: 100%;
  overflow: hidden;
  color: var(--text-color);
  font-size: 0.9rem;
  font-weight: 600;
  line-height: 1.4;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.system-report-summary__body {
  display: -webkit-box;
  width: 100%;
  min-width: 0;
  max-width: 100%;
  max-height: calc(1.35em * 3);
  margin-top: 0.2rem;
  overflow: hidden;
  overflow-wrap: anywhere;
  color: var(--text-color-secondary);
  font-size: 0.82rem;
  line-height: 1.35;
  text-overflow: ellipsis;
  white-space: normal;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
}
.comment-report-content {
  display: grid;
  width: 100%;
  min-width: 0;
  max-width: 100%;
  overflow: hidden;
  white-space: normal;
}
.comment-report-content__reason {
  display: block;
  min-width: 0;
  max-width: 100%;
  overflow: hidden;
  color: var(--text-color);
  font-size: 0.88rem;
  font-weight: 600;
  line-height: 1.4;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.comment-report-content__summary {
  display: -webkit-box;
  width: 100%;
  min-width: 0;
  max-width: 100%;
  max-height: calc(1.35em * 3);
  margin-top: 0.2rem;
  overflow: hidden;
  overflow-wrap: anywhere;
  color: var(--text-color-secondary);
  font-size: 0.82rem;
  line-height: 1.35;
  text-overflow: ellipsis;
  white-space: normal;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
}
:deep(.comment-report-content-column) {
  width: clamp(16rem, 24vw, 20rem);
  max-width: 20rem;
  overflow: hidden;
  white-space: normal;
}
:deep(.report-person-time-column) {
  overflow: hidden;
  white-space: normal;
}
:deep(.report-user-column) {
  width: 7rem;
  min-width: 7rem;
  max-width: 7rem;
  overflow: hidden;
}
.report-user-cell__text {
  display: block;
  min-width: 0;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.report-person-time {
  display: grid;
  width: 100%;
  min-width: 0;
  max-width: 100%;
  gap: 0.18rem;
}
.report-person-time__name,
.report-person-time__time {
  display: block;
  min-width: 0;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.report-person-time__name {
  color: var(--text-color);
  line-height: 1.35;
}
.report-person-time__name--empty {
  color: var(--text-color-secondary);
}
.report-person-time__time {
  color: var(--text-color-secondary);
  font-size: 0.78rem;
  line-height: 1.3;
}
:deep(.report-review-column) {
  width: 10rem;
  min-width: 10rem;
  padding-inline-end: 1.25rem;
  overflow: hidden;
  white-space: normal;
}
:deep(.report-actions-column) {
  width: 9.5rem;
  min-width: 9.5rem;
  padding-inline-start: 0.75rem;
}
:deep(.report-actions-column .p-button) {
  white-space: nowrap;
}
.report-management__empty {
  display: flex;
  min-height: 15rem;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 0.65rem;
  color: var(--text-color-secondary);
  text-align: center;
}
.report-management__empty i {
  font-size: 2rem;
}
.report-review {
  display: grid;
  gap: 1rem;
}
.report-review__title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}
.report-review__title > div {
  display: grid;
  gap: 0.2rem;
}
.report-review__title small {
  color: var(--text-color-secondary);
}
.report-review__meta {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.55rem;
  margin: 0;
}
.report-review__meta div {
  min-width: 0;
  padding: 0.5rem;
  border-radius: var(--content-border-radius);
  background: var(--surface-50);
}
.report-review__meta dt {
  color: var(--text-color-secondary);
  font-size: 0.78rem;
}
.report-review__meta dd {
  margin: 0.15rem 0 0;
  overflow-wrap: anywhere;
}
.report-review__quote {
  padding: 0.7rem;
  border-left: 3px solid var(--surface-border);
  background: var(--surface-50);
}
.report-review__quote p {
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}
.report-review__field {
  display: grid;
  gap: 0.35rem;
}
.report-review__delete-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.report-review__spacer {
  flex: 1;
}
@media (max-width: 1023px) {
  .report-section__header {
    align-items: flex-start;
    flex-direction: column;
  }
  .report-management__filters {
    grid-template-columns: minmax(0, 1fr);
  }
  .system-report-summary {
    width: 100%;
  }
  :deep(.system-report-column) {
    width: 100%;
    max-width: none;
  }
}
@media (max-width: 1199px) {
  :deep(.comment-report-content-column),
  :deep(.report-person-time-column),
  :deep(.report-user-column),
  :deep(.report-review-column),
  :deep(.report-actions-column) {
    width: 100%;
    min-width: 0;
    max-width: none;
    padding-inline: var(--p-datatable-body-cell-padding, 0.75rem);
  }
}
@media (max-width: 760px) {
  .report-review__meta {
    grid-template-columns: minmax(0, 1fr);
  }
  .report-review__actions {
    flex-wrap: wrap;
  }
}
</style>
