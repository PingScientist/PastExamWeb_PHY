<template>
  <section class="report-management" aria-label="回報管理">
    <header class="report-management__header">
      <div>
        <h3>回報管理</h3>
        <p>檢視系統問題摘要並審核留言回報</p>
      </div>
      <Button
        icon="pi pi-refresh"
        label="重新整理"
        outlined
        :loading="loading"
        @click="refreshActiveTab"
      />
    </header>

    <Tabs v-model:value="activeTab">
      <TabList>
        <Tab value="system"><i class="pi pi-wrench" aria-hidden="true" />系統問題回報</Tab>
        <Tab value="comments"><i class="pi pi-flag" aria-hidden="true" />留言回報</Tab>
        <Tab value="archives"><i class="pi pi-file-pdf" aria-hidden="true" />考古題回報</Tab>
      </TabList>
      <TabPanels>
        <TabPanel value="system">
          <div class="report-management__actions">
            <span>共 {{ systemTotal }} 筆本地回報摘要</span>
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
          </div>
          <DataTable
            :value="systemIssues"
            :loading="loadingSystem"
            paginator
            :rows="10"
            responsiveLayout="stack"
            breakpoint="900px"
            class="report-management__table"
          >
            <template #empty>目前沒有系統問題回報</template>
            <Column field="created_at" header="回報時間">
              <template #body="{ data }">{{ formatDateTime(data.created_at) }}</template>
            </Column>
            <Column field="reporter_name" header="回報者" />
            <Column field="title" header="標題">
              <template #body="{ data }">
                <div class="report-management__summary">
                  <strong>{{ data.title }}</strong>
                  <span>{{ truncate(data.description, 90) }}</span>
                </div>
              </template>
            </Column>
            <Column field="report_type" header="類型">
              <template #body="{ data }"
                ><Tag :value="issueTypeLabel(data.report_type)"
              /></template>
            </Column>
            <Column header="GitHub Issue">
              <template #body="{ data }">
                {{ data.github_issue_number ? `#${data.github_issue_number}` : '尚未連結' }}
              </template>
            </Column>
            <Column field="status" header="狀態">
              <template #body><Tag severity="secondary" value="本地摘要" /></template>
            </Column>
            <Column header="操作">
              <template #body="{ data }">
                <Button
                  as="a"
                  :href="safeGithubIssueUrl(data) || undefined"
                  target="_blank"
                  rel="noopener noreferrer"
                  label="前往 GitHub"
                  icon="pi pi-external-link"
                  size="small"
                  outlined
                  :disabled="!safeGithubIssueUrl(data)"
                />
              </template>
            </Column>
          </DataTable>
        </TabPanel>

        <TabPanel value="comments">
          <div class="report-management__filters">
            <InputText
              v-model="commentFilters.search"
              placeholder="搜尋編號、留言、課程或使用者"
              @keyup.enter="loadCommentReports"
            />
            <Select
              v-model="commentFilters.status"
              :options="statusOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="全部狀態"
              showClear
              @change="loadCommentReports"
            />
            <Select
              v-model="commentFilters.reason"
              :options="reasonOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="全部原因"
              showClear
              @change="loadCommentReports"
            />
            <Button label="搜尋" icon="pi pi-search" outlined @click="loadCommentReports" />
          </div>
          <DataTable
            :value="commentReports"
            :loading="loadingComments"
            paginator
            :rows="10"
            responsiveLayout="stack"
            breakpoint="1000px"
            class="report-management__table"
          >
            <template #empty>目前沒有符合條件的留言回報</template>
            <Column field="id" header="回報編號">
              <template #body="{ data }">#{{ data.id }}</template>
            </Column>
            <Column field="status" header="狀態">
              <template #body="{ data }">
                <Tag :severity="statusSeverity(data.status)" :value="statusLabel(data.status)" />
              </template>
            </Column>
            <Column field="reason" header="原因">
              <template #body="{ data }">{{ reasonLabel(data.reason) }}</template>
            </Column>
            <Column field="reporter_name" header="回報者" />
            <Column field="comment_author_name" header="留言作者" />
            <Column header="留言摘要">
              <template #body="{ data }">
                <div class="report-management__summary">
                  <span>{{ truncate(data.comment_content_snapshot, 90) }}</span>
                  <small>{{ data.course_name }} · {{ data.archive_name }}</small>
                </div>
              </template>
            </Column>
            <Column field="created_at" header="回報時間">
              <template #body="{ data }">{{ formatDateTime(data.created_at) }}</template>
            </Column>
            <Column header="審核人／時間">
              <template #body="{ data }">
                <div class="report-management__summary">
                  <span>{{ data.reviewer_name || '尚未審核' }}</span>
                  <small>{{ data.reviewed_at ? formatDateTime(data.reviewed_at) : '—' }}</small>
                </div>
              </template>
            </Column>
            <Column header="操作">
              <template #body="{ data }">
                <Button
                  label="檢視／審核"
                  icon="pi pi-search"
                  size="small"
                  outlined
                  @click="openCommentReport(data.id)"
                />
              </template>
            </Column>
          </DataTable>
        </TabPanel>

        <TabPanel value="archives">
          <div class="report-management__empty">
            <i class="pi pi-file-pdf" aria-hidden="true" />
            <strong>考古題回報功能尚未開放</strong>
            <span>此分頁僅預留未來功能位置，目前沒有資料表或送出流程。</span>
          </div>
        </TabPanel>
      </TabPanels>
    </Tabs>

    <Dialog
      v-model:visible="reviewVisible"
      modal
      header="留言回報審核"
      :style="{ width: '720px', maxWidth: '94vw' }"
      :draggable="false"
    >
      <div v-if="selectedReport" class="report-review">
        <div class="report-review__title">
          <strong>回報 #{{ selectedReport.id }}</strong>
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
            <dd>#{{ selectedReport.thread_id || '—' }}</dd>
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
import { computed, onMounted, ref, watch } from 'vue'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import { useRouter } from 'vue-router'
import { reportService } from '@/api'
import { getCurrentUser } from '@/utils/auth'

const confirm = useConfirm()
const toast = useToast()
const router = useRouter()
const activeTab = ref('system')
const loadingSystem = ref(false)
const loadingComments = ref(false)
const systemIssues = ref([])
const systemTotal = ref(0)
const commentReports = ref([])
const reviewVisible = ref(false)
const reviewSaving = ref(false)
const selectedReport = ref(null)
const commentFilters = ref({ search: '', status: null, reason: null })
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
  try {
    const { data } = await reportService.listSystemIssues({ limit: 100 })
    systemIssues.value = data.items || []
    systemTotal.value = Number(data.total || 0)
  } catch (error) {
    console.error('Load system issue reports error:', error)
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
  try {
    const { data } = await reportService.listCommentReports({
      search: commentFilters.value.search.trim() || undefined,
      status: commentFilters.value.status || undefined,
      reason: commentFilters.value.reason || undefined,
      limit: 100,
    })
    commentReports.value = data.items || []
  } catch (error) {
    console.error('Load comment reports error:', error)
    toast.add({ severity: 'error', summary: '載入失敗', detail: '無法載入留言回報', life: 3000 })
  } finally {
    loadingComments.value = false
  }
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
      detail: `回報 #${data.id} 已更新`,
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
function refreshActiveTab() {
  return activeTab.value === 'comments' ? loadCommentReports() : loadSystemIssues()
}
function truncate(value, max) {
  const text = String(value || '')
  return text.length > max ? `${text.slice(0, max)}…` : text
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
function formatDateTime(value) {
  if (!value) return '—'
  return new Date(value).toLocaleString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

watch(activeTab, (value) => {
  if (value === 'comments' && !commentReports.value.length) void loadCommentReports()
  if (value === 'system' && !systemIssues.value.length) void loadSystemIssues()
})
onMounted(loadSystemIssues)
</script>

<style scoped>
.report-management {
  min-width: 0;
}
.report-management__header,
.report-management__actions,
.report-review__actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}
.report-management__header h3 {
  margin: 0;
}
.report-management__header p {
  margin: 0.25rem 0 0;
  color: var(--text-color-secondary);
}
.report-management__filters {
  display: grid;
  grid-template-columns: minmax(12rem, 1fr) repeat(2, minmax(10rem, auto)) auto;
  gap: 0.6rem;
  margin-bottom: 1rem;
}
.report-management__table {
  margin-top: 1rem;
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
:deep(.p-tablist-tab-list) {
  flex-wrap: wrap;
}
:deep(.p-tab) {
  gap: 0.4rem;
}
@media (max-width: 760px) {
  .report-management__header {
    align-items: flex-start;
    flex-direction: column;
  }
  .report-management__filters {
    grid-template-columns: minmax(0, 1fr);
  }
  .report-review__meta {
    grid-template-columns: minmax(0, 1fr);
  }
  .report-review__actions {
    flex-wrap: wrap;
  }
}
</style>
