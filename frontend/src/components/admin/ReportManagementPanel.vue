<template>
  <section class="report-management" aria-label="回報管理">
    <section class="report-section" aria-labelledby="system-report-heading">
      <div class="report-section__header">
        <div>
          <h4 id="system-report-heading">系統問題回報</h4>
          <p>檢視使用者提交至本站的系統問題摘要。</p>
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
      <div class="report-management__filters report-management__filters--system">
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
          v-model="systemFilters.readState"
          :options="systemReadStateOptions"
          optionLabel="label"
          optionValue="value"
          aria-label="系統問題回報閱讀狀態"
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
        <Column header="說明" style="width: 8rem"
          ><template #body><Tag severity="secondary" value="本地摘要" /></template
        ></Column>
        <Column header="狀態" style="width: 7rem"
          ><template #body="{ data }"
            ><Tag
              class="system-read-state-tag"
              :severity="data.is_read ? 'secondary' : 'warn'"
              :value="data.is_read ? '已讀' : '未讀'" /></template
        ></Column>
        <Column
          header="操作"
          headerClass="report-actions-column report-actions-column--system"
          bodyClass="report-actions-column report-actions-column--system"
          style="width: 12rem; min-width: 12rem"
          ><template #body="{ data }"
            ><div class="report-row-actions">
              <Button
                label="檢視"
                icon="pi pi-search"
                aria-label="檢視系統問題回報"
                title="檢視系統問題回報"
                size="small"
                outlined
                :loading="loadingSystemDetailId === data.id"
                :disabled="loadingSystemDetailId !== null"
                @click="openSystemReport(data)"
              />
              <Button
                label="刪除"
                icon="pi pi-trash"
                severity="danger"
                aria-label="刪除系統問題回報"
                title="刪除系統問題回報"
                size="small"
                outlined
                :loading="deletingSystemId === data.id"
                :disabled="deletingSystemId !== null"
                @click="confirmDeleteSystemIssue(data)"
              /></div></template
        ></Column>
      </DataTable>

      <Dialog
        v-model:visible="systemDetailVisible"
        modal
        header="系統問題回報詳情"
        :style="{ width: '680px', maxWidth: '94vw' }"
        :contentStyle="{ maxHeight: '70vh', overflowY: 'auto' }"
        :draggable="false"
      >
        <div v-if="selectedSystemReport" class="system-report-detail">
          <dl class="report-review__meta">
            <div>
              <dt>回報者</dt>
              <dd>{{ selectedSystemReport.reporter_name }}</dd>
            </div>
            <div>
              <dt>回報時間</dt>
              <dd>{{ formatDateTime(selectedSystemReport.created_at, true) }}</dd>
            </div>
            <div>
              <dt>問題類型</dt>
              <dd>{{ issueTypeLabel(selectedSystemReport.report_type) }}</dd>
            </div>
            <div>
              <dt>聯絡方式</dt>
              <dd>{{ selectedSystemReport.contact || '未提供' }}</dd>
            </div>
          </dl>
          <section class="system-report-detail__content">
            <strong>問題標題</strong>
            <p>{{ selectedSystemReport.title || '未命名回報' }}</p>
          </section>
          <section class="system-report-detail__content">
            <strong>完整詳細描述</strong>
            <p>{{ selectedSystemReport.description || '—' }}</p>
          </section>
          <section class="system-report-detail__note">
            <Tag severity="secondary" value="本地摘要" />
            <p>此紀錄保存在本站，無法確認使用者是否已在 GitHub 正式建立 Issue。</p>
          </section>
          <section class="system-report-detail__read-state">
            <div class="system-report-detail__read-heading">
              <strong>已讀狀態</strong>
              <Tag
                class="system-read-state-tag"
                :severity="selectedSystemReport.is_read ? 'secondary' : 'warn'"
                :value="selectedSystemReport.is_read ? '已讀' : '未讀'"
              />
            </div>
            <label class="system-report-detail__read-option">
              <Checkbox v-model="systemReadForm" binary :disabled="systemReadSaving" />
              標記為已讀
            </label>
            <small>閱讀狀態由管理員手動維護，開啟此視窗不會自動標記已讀。</small>
            <small v-if="selectedSystemReport.read_at">
              最後標記：{{ selectedSystemReport.read_by_username || '管理員' }}，{{
                formatDateTime(selectedSystemReport.read_at, true)
              }}
            </small>
          </section>
          <div class="report-review__actions">
            <span class="report-review__spacer" />
            <Button
              label="關閉"
              severity="secondary"
              outlined
              @click="systemDetailVisible = false"
            />
            <Button
              label="儲存"
              icon="pi pi-save"
              :loading="systemReadSaving"
              :disabled="systemReadSaving"
              @click="saveSystemReadState"
            />
          </div>
        </div>
      </Dialog>
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
          style="width: 17rem; min-width: 17rem"
          ><template #body="{ data }"
            ><div class="report-row-actions">
              <Button
                :label="isFinal(data.status) ? '檢視' : '檢視／審核'"
                icon="pi pi-search"
                aria-label="檢視或審核留言回報"
                title="檢視或審核留言回報"
                size="small"
                outlined
                @click="openCommentReport(data.id)"
              />
              <Button
                label="刪除"
                icon="pi pi-trash"
                severity="danger"
                aria-label="刪除留言回報"
                title="刪除留言回報"
                size="small"
                outlined
                :loading="deletingCommentId === data.id"
                :disabled="deletingCommentId !== null"
                @click="confirmDeleteCommentReport(data)"
              /></div></template
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
        <p v-if="isFinal(selectedReport.status)" class="report-review__response">
          <strong>管理員答覆：</strong>{{ selectedReport.admin_response || '未提供答覆' }}
        </p>
        <Message v-if="isFinal(selectedReport.status)" severity="info" :closable="false">
          審核結果已送出，無法修改。
        </Message>
        <div v-if="!isFinal(selectedReport.status)" class="report-review__field">
          <label for="report-review-status">審核結果</label>
          <Select
            inputId="report-review-status"
            v-model="reviewForm.status"
            :options="reviewStatusOptions"
            optionLabel="label"
            optionValue="value"
            :disabled="reviewSaving"
          />
        </div>
        <div v-if="!isFinal(selectedReport.status)" class="report-review__field">
          <label for="report-admin-response">給回報者的答覆</label>
          <Textarea
            id="report-admin-response"
            v-model="reviewForm.admin_response"
            rows="4"
            maxlength="1000"
            :disabled="reviewSaving"
          />
          <small>{{ reviewForm.admin_response.length }}/1000</small>
        </div>
        <label
          v-if="!isFinal(selectedReport.status) && reviewForm.status === 'upheld'"
          class="report-review__delete-option"
        >
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
            v-if="!isFinal(selectedReport.status)"
            label="儲存審核"
            icon="pi pi-check"
            :loading="reviewSaving"
            :disabled="!canSaveReview"
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
const systemDetailVisible = ref(false)
const loadingSystemDetailId = ref(null)
const systemReadSaving = ref(false)
const systemReadForm = ref(false)
const reviewSaving = ref(false)
const deletingSystemId = ref(null)
const deletingCommentId = ref(null)
const selectedReport = ref(null)
const selectedSystemReport = ref(null)
const systemFilters = ref({ search: '', type: null, readState: 'all' })
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
const reviewForm = ref({ status: 'pending', admin_response: '', delete_comment: false })
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
const systemReadStateOptions = [
  { label: '全部狀態', value: 'all' },
  { label: '未讀', value: 'unread' },
  { label: '已讀', value: 'read' },
]
const statusOptions = [
  { label: '待審核', value: 'pending' },
  { label: '回報成立', value: 'upheld' },
  { label: '回報不成立', value: 'dismissed' },
]
const reviewStatusOptions = computed(() =>
  isFinal(selectedReport.value?.status)
    ? statusOptions.filter((item) => item.value !== 'pending')
    : statusOptions
)
const canSaveReview = computed(() => {
  if (!['upheld', 'dismissed'].includes(reviewForm.value.status)) return false
  return reviewForm.value.admin_response.length <= 1000
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
      read_state: systemFilters.value.readState,
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
function clampReportPageAfterDelete(page, total) {
  const nextTotal = Math.max(0, total - 1)
  const maxFirst = nextTotal
    ? Math.floor((nextTotal - 1) / Math.max(1, page.rows)) * Math.max(1, page.rows)
    : 0
  page.first = Math.min(page.first, maxFirst)
  return nextTotal
}
function confirmDeleteSystemIssue(item) {
  if (!item?.id || deletingSystemId.value !== null) return
  confirm.require({
    header: '刪除這筆回報？',
    message: '回報會移至垃圾桶，可由管理員在垃圾桶中還原或永久刪除。',
    icon: 'pi pi-exclamation-triangle',
    rejectLabel: '取消',
    acceptLabel: '刪除',
    acceptClass: 'p-button-danger',
    accept: () => deleteSystemIssue(item),
  })
}
async function openSystemReport(item) {
  if (!item?.id || loadingSystemDetailId.value !== null) return
  loadingSystemDetailId.value = item.id
  try {
    const { data } = await reportService.getSystemIssue(item.id)
    selectedSystemReport.value = data
    systemReadForm.value = Boolean(data.is_read)
    systemDetailVisible.value = true
  } catch (error) {
    console.error('Load system issue report detail error:', error)
    toast.add({ severity: 'error', summary: '載入失敗', detail: '無法載入回報詳情', life: 3000 })
  } finally {
    loadingSystemDetailId.value = null
  }
}
async function saveSystemReadState() {
  if (!selectedSystemReport.value?.id || systemReadSaving.value) return
  systemReadSaving.value = true
  try {
    const { data } = await reportService.updateSystemIssueReadState(
      selectedSystemReport.value.id,
      systemReadForm.value
    )
    selectedSystemReport.value = data
    systemReadForm.value = Boolean(data.is_read)
    systemIssues.value = systemIssues.value.map((item) => (item.id === data.id ? data : item))
    toast.add({
      severity: 'success',
      summary: '閱讀狀態已更新',
      detail: data.is_read ? '已標記為已讀' : '已標記為未讀',
      life: 3000,
    })
  } catch (error) {
    console.error('Update system issue report read state error:', error)
    systemReadForm.value = Boolean(selectedSystemReport.value.is_read)
    toast.add({ severity: 'error', summary: '更新失敗', detail: '閱讀狀態未變更', life: 3000 })
  } finally {
    systemReadSaving.value = false
  }
}
async function deleteSystemIssue(item) {
  if (!item?.id || deletingSystemId.value !== null) return
  deletingSystemId.value = item.id
  try {
    await reportService.deleteSystemIssue(item.id)
    systemIssues.value = systemIssues.value.filter((candidate) => candidate.id !== item.id)
    systemTotal.value = clampReportPageAfterDelete(systemPage.value, systemTotal.value)
    toast.add({
      severity: 'success',
      summary: '回報已移至垃圾桶',
      detail: '系統問題回報可在垃圾桶中還原或永久刪除',
      life: 3000,
    })
    await loadSystemIssues()
  } catch (error) {
    console.error('Delete system issue report error:', error)
    toast.add({ severity: 'error', summary: '刪除失敗', detail: '系統問題回報未變更', life: 3000 })
  } finally {
    deletingSystemId.value = null
  }
}
function confirmDeleteCommentReport(item) {
  if (!item?.id || deletingCommentId.value !== null) return
  confirm.require({
    header: '刪除這筆回報？',
    message: '回報會移至垃圾桶，可由管理員在垃圾桶中還原或永久刪除。',
    icon: 'pi pi-exclamation-triangle',
    rejectLabel: '取消',
    acceptLabel: '刪除',
    acceptClass: 'p-button-danger',
    accept: () => deleteCommentReport(item),
  })
}
async function deleteCommentReport(item) {
  if (!item?.id || deletingCommentId.value !== null) return
  deletingCommentId.value = item.id
  try {
    await reportService.deleteCommentReport(item.id)
    commentReports.value = commentReports.value.filter((candidate) => candidate.id !== item.id)
    commentTotal.value = clampReportPageAfterDelete(commentPage.value, commentTotal.value)
    if (selectedReport.value?.id === item.id) reviewVisible.value = false
    toast.add({
      severity: 'success',
      summary: '回報已移至垃圾桶',
      detail: '留言回報可在垃圾桶中還原或永久刪除',
      life: 3000,
    })
    await loadCommentReports()
  } catch (error) {
    console.error('Delete comment report error:', error)
    toast.add({ severity: 'error', summary: '刪除失敗', detail: '留言回報未變更', life: 3000 })
  } finally {
    deletingCommentId.value = null
  }
}
async function openCommentReport(id) {
  try {
    const { data } = await reportService.getCommentReport(id)
    selectedReport.value = data
    reviewForm.value = {
      status: data.status,
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
  if (
    reviewSaving.value ||
    !selectedReport.value ||
    isFinal(selectedReport.value.status) ||
    !canSaveReview.value
  )
    return
  const deletesComment = reviewForm.value.status === 'upheld' && reviewForm.value.delete_comment
  const message = ['送出後將通知回報者。', '審核結果與管理員答覆送出後將無法修改。']
  if (deletesComment) {
    message.push('被回報留言將永久刪除，無法復原，也不會進入垃圾桶。')
  }
  confirm.require({
    header: '確認送出審核結果',
    message: message.join('\n'),
    icon: deletesComment ? 'pi pi-exclamation-triangle' : 'pi pi-question-circle',
    rejectLabel: '取消',
    acceptLabel: '確認送出',
    acceptClass: deletesComment ? 'p-button-danger' : 'p-button-primary',
    defaultFocus: 'reject',
    accept: saveReview,
  })
}
async function saveReview() {
  if (
    reviewSaving.value ||
    !selectedReport.value ||
    isFinal(selectedReport.value.status) ||
    !canSaveReview.value
  )
    return
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
  return { pending: 'warn', upheld: 'success', dismissed: 'danger' }[value] || 'secondary'
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
.report-row-actions {
  display: inline-flex;
  width: 100%;
  align-items: center;
  justify-content: flex-end;
  flex-wrap: nowrap;
  gap: 0.5rem;
  padding-inline-end: 0.35rem;
}
.report-row-actions :deep(.p-button) {
  flex: 0 0 auto;
  white-space: nowrap;
}
.report-management__filters {
  display: grid;
  grid-template-columns: minmax(12rem, 1fr) repeat(2, minmax(10rem, auto)) auto;
  gap: 0.6rem;
  margin-block: 1rem;
}
.report-management__filters--system {
  grid-template-columns: minmax(12rem, 1fr) repeat(2, minmax(10rem, auto)) auto;
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
  width: 17rem;
  min-width: 17rem;
  padding-inline: 0.75rem 1rem;
  vertical-align: middle;
}
:deep(.report-actions-column--system) {
  width: 12rem;
  min-width: 12rem;
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
.system-report-detail {
  display: grid;
  min-width: 0;
  gap: 1rem;
}
.system-report-detail__content,
.system-report-detail__note {
  min-width: 0;
  padding: 0.75rem;
  border-radius: var(--content-border-radius);
  background: var(--surface-50);
}
.system-report-detail__content p,
.system-report-detail__note p {
  margin: 0.45rem 0 0;
  overflow-wrap: anywhere;
  white-space: pre-wrap;
}
.system-report-detail__note {
  border: 1px solid var(--surface-border);
}
.system-report-detail__read-state {
  display: grid;
  gap: 0.65rem;
  padding: 0.75rem;
  border: 1px solid var(--surface-border);
  border-radius: var(--content-border-radius);
}
.system-report-detail__read-heading,
.system-report-detail__read-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.system-report-detail__read-heading {
  justify-content: space-between;
}
.system-report-detail__read-state small {
  color: var(--text-color-secondary);
  overflow-wrap: anywhere;
}
.system-read-state-tag {
  white-space: nowrap;
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
  :deep(.report-actions-column--system) {
    width: 100%;
    min-width: 0;
    max-width: none;
    padding-inline: var(--p-datatable-body-cell-padding, 0.75rem);
  }
}
@media (max-width: 1199px) {
  :deep(.comment-report-content-column),
  :deep(.report-person-time-column),
  :deep(.report-user-column),
  :deep(.report-review-column),
  :deep(.report-actions-column:not(.report-actions-column--system)) {
    width: 100%;
    min-width: 0;
    max-width: none;
    padding-inline: var(--p-datatable-body-cell-padding, 0.75rem);
  }
  .report-row-actions {
    justify-content: flex-start;
    padding-inline-end: 0;
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
