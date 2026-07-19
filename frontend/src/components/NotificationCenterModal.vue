<template>
  <div>
    <Dialog
      :visible="visible"
      @update:visible="$emit('update:visible', $event)"
      modal
      :style="{ width: '820px', maxWidth: '95vw' }"
      :draggable="false"
      :blockScroll="true"
      :pt="{ root: { 'aria-label': '公告與通知', 'aria-labelledby': null } }"
    >
      <template #header>
        <div class="flex align-items-center gap-2">
          <i class="pi pi-bell text-2xl" />
          <span class="text-xl font-semibold">公告與通知</span>
          <Badge v-if="counts.total" :value="counts.total" severity="danger" />
        </div>
      </template>

      <div v-if="loading" class="flex justify-content-center py-5">
        <ProgressSpinner style="width: 40px; height: 40px" strokeWidth="4" />
      </div>
      <Tabs v-else v-model:value="activeTab">
        <TabList>
          <Tab value="announcements"><i class="pi pi-megaphone mr-2" />公告</Tab>
          <Tab value="personal">
            <i class="pi pi-bell mr-2" />個人通知
            <Badge
              v-if="counts.personal_notifications"
              :value="counts.personal_notifications"
              severity="danger"
              class="ml-2"
            />
          </Tab>
        </TabList>
        <TabPanels>
          <TabPanel value="announcements">
            <div v-if="announcements.length === 0" class="notification-empty">
              <i class="pi pi-megaphone text-4xl" /><span>目前沒有公告</span>
            </div>
            <DataTable v-else :value="announcements" :rows="5" paginator class="notification-table">
              <Column field="title" header="標題">
                <template #body="{ data }">
                  <div class="flex align-items-center gap-2 min-w-0">
                    <span v-if="!data.is_read" class="unread-dot" aria-label="未讀" />
                    <span class="font-medium text-overflow-ellipsis overflow-hidden">{{
                      data.title
                    }}</span>
                  </div>
                </template>
              </Column>
              <Column header="重要程度" style="width: 7rem">
                <template #body="{ data }"
                  ><Tag :severity="severity(data.severity)">{{
                    severityLabel(data.severity)
                  }}</Tag></template
                >
              </Column>
              <Column header="狀態" style="width: 5rem">
                <template #body="{ data }"
                  ><Tag :severity="data.is_read ? 'secondary' : 'info'">{{
                    data.is_read ? '已讀' : '未讀'
                  }}</Tag></template
                >
              </Column>
              <Column header="最近更新" style="width: 9rem">
                <template #body="{ data }"
                  ><small class="text-500">{{ formatDate(data.updated_at) }}</small></template
                >
              </Column>
              <Column header="操作" style="width: 5rem">
                <template #body="{ data }"
                  ><Button
                    label="檢視"
                    size="small"
                    outlined
                    class="notification-view-button"
                    @click="openAnnouncement(data)"
                /></template>
              </Column>
            </DataTable>
          </TabPanel>

          <TabPanel value="personal">
            <div class="flex justify-content-between align-items-center gap-2 mb-3">
              <span class="text-sm text-500">{{ counts.personal_notifications }} 則未讀</span>
              <Button
                label="全部標記為已讀"
                icon="pi pi-check-circle"
                size="small"
                outlined
                :disabled="!counts.personal_notifications"
                @click="$emit('mark-all-personal-read')"
              />
            </div>
            <div v-if="personalNotifications.length === 0" class="notification-empty">
              <i class="pi pi-bell text-4xl" /><span>目前沒有個人通知</span>
            </div>
            <div v-else class="personal-list">
              <article
                v-for="item in personalNotifications"
                :key="item.id"
                class="personal-item"
                :class="{ 'personal-item--unread': !item.read_at }"
              >
                <i class="pi pi-reply personal-item__icon" aria-hidden="true" />
                <div class="personal-item__body">
                  <div class="flex align-items-center gap-2">
                    <span v-if="!item.read_at" class="unread-dot" aria-label="未讀" />
                    <strong>{{ item.title }}</strong>
                  </div>
                  <p>{{ item.message }}</p>
                  <small class="text-500">{{ formatTimestamp(item.created_at) }}</small>
                  <small v-if="!item.source_available" class="text-500 block mt-1"
                    >來源已不存在</small
                  >
                </div>
                <Button
                  label="檢視"
                  size="small"
                  outlined
                  class="notification-view-button"
                  @click="openPersonal(item)"
                />
              </article>
            </div>
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Dialog>

    <Dialog
      :visible="detailVisible"
      @update:visible="detailVisible = $event"
      modal
      :style="{ width: '520px', maxWidth: '90vw' }"
      :draggable="false"
      :header="selectedType === 'announcement' ? '公告內容' : '個人通知'"
    >
      <div v-if="selectedItem" class="notification-detail">
        <h3>{{ selectedItem.title }}</h3>
        <small class="text-500">{{
          formatTimestamp(selectedItem.updated_at || selectedItem.created_at)
        }}</small>
        <div
          v-if="selectedType === 'announcement'"
          class="markdown-content"
          v-html="renderedBody"
        />
        <p v-else>{{ selectedItem.message }}</p>
        <small v-if="selectedType === 'personal' && !selectedItem.source_available" class="text-500"
          >來源已不存在，無法開啟原留言。</small
        >
      </div>
    </Dialog>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { renderMarkdown } from '@/utils/markdown'

const props = defineProps({
  visible: Boolean,
  announcements: { type: Array, default: () => [] },
  personalNotifications: { type: Array, default: () => [] },
  counts: { type: Object, default: () => ({ total: 0, personal_notifications: 0 }) },
  loading: Boolean,
  focusType: { type: String, default: null },
  focusId: { type: Number, default: null },
})
const emit = defineEmits([
  'update:visible',
  'mark-announcement-read',
  'mark-personal-read',
  'mark-all-personal-read',
])
const activeTab = ref('announcements')
const detailVisible = ref(false)
const selectedItem = ref(null)
const selectedType = ref('announcement')
const renderedBody = computed(() => renderMarkdown(selectedItem.value?.body || ''))
const severity = (value) => (value === 'danger' ? 'danger' : 'info')
const severityLabel = (value) => (value === 'danger' ? '重要' : '一般')

function openAnnouncement(item) {
  selectedType.value = 'announcement'
  selectedItem.value = item
  detailVisible.value = true
  if (!item.is_read) emit('mark-announcement-read', item.id)
}
function openPersonal(item) {
  selectedType.value = 'personal'
  selectedItem.value = item
  detailVisible.value = true
  if (!item.read_at) emit('mark-personal-read', item.id)
}
watch(
  () => props.visible,
  (visible) => {
    if (!visible) detailVisible.value = false
  }
)
watch(
  () => [props.visible, props.focusType, props.focusId, props.loading],
  ([visible, type, id, loading]) => {
    if (!visible || !id || loading) return
    const items = type === 'personal' ? props.personalNotifications : props.announcements
    const item = items.find((candidate) => candidate.id === id)
    if (!item) return
    activeTab.value = type === 'personal' ? 'personal' : 'announcements'
    selectedType.value = type
    selectedItem.value = item
    detailVisible.value = true
  }
)
const formatDate = (value) => formatTimestamp(value, false)
function formatTimestamp(value, withTime = true) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString(
    'zh-TW',
    withTime
      ? { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }
      : { year: 'numeric', month: '2-digit', day: '2-digit' }
  )
}
</script>

<style scoped>
.notification-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 3rem 1rem;
  color: var(--text-color-secondary);
}
.notification-table {
  font-size: 0.875rem;
  overflow-x: auto;
}
:deep(.notification-view-button.p-button) {
  min-inline-size: 3.25rem;
  white-space: nowrap;
}
:deep(.notification-table .p-datatable-wrapper) {
  overflow-x: auto;
}
:deep(.notification-table table) {
  min-width: 640px;
}
.unread-dot {
  flex: 0 0 auto;
  width: 0.55rem;
  height: 0.55rem;
  border-radius: 50%;
  background: var(--primary-color);
}
.personal-list {
  display: grid;
  gap: 0.6rem;
  max-height: 55vh;
  overflow-y: auto;
}
.personal-item {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: start;
  gap: 0.75rem;
  padding: 0.8rem;
  border: 1px solid var(--surface-border);
  border-radius: var(--content-border-radius);
}
.personal-item--unread {
  background: var(--highlight-bg);
}
.personal-item__icon {
  color: var(--primary-color);
  margin-top: 0.2rem;
}
.personal-item__body {
  min-width: 0;
}
.personal-item__body p {
  margin: 0.35rem 0;
  overflow-wrap: anywhere;
}
.notification-detail {
  max-height: 60vh;
  overflow-y: auto;
}
.notification-detail h3 {
  margin: 0 0 0.25rem;
}
.markdown-content {
  margin-top: 1rem;
  overflow-wrap: anywhere;
}
@media (max-width: 480px) {
  .personal-item {
    grid-template-columns: auto minmax(0, 1fr);
  }
  .personal-item > .p-button {
    grid-column: 2;
    justify-self: end;
  }
}
</style>
