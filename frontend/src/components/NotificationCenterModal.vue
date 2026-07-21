<template>
  <div>
    <Dialog
      :visible="visible"
      @update:visible="$emit('update:visible', $event)"
      modal
      :style="{ width: 'min(820px, calc(100vw - 2rem))', maxWidth: '100%' }"
      :draggable="false"
      :blockScroll="true"
      class="notification-center-dialog"
      :pt="{ root: { 'aria-label': '公告與通知', 'aria-labelledby': null } }"
    >
      <template #header>
        <div class="notification-dialog-header">
          <i class="pi pi-bell text-2xl" />
          <span class="notification-dialog-header__title">公告與通知</span>
          <Badge v-if="counts.total" :value="counts.total" severity="danger" />
        </div>
      </template>

      <div v-if="loading" class="flex justify-content-center py-5">
        <ProgressSpinner style="width: 40px; height: 40px" strokeWidth="4" />
      </div>
      <Tabs v-else v-model:value="activeTab" class="notification-center-tabs">
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
            <DataTable
              v-else
              :value="announcements"
              :rows="ANNOUNCEMENT_PAGE_SIZE"
              :first="announcementFirst"
              paginator
              class="notification-table notification-desktop-announcements"
              @page="announcementFirst = $event.first"
            >
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
            <div v-if="announcements.length" class="notification-mobile-announcements">
              <div class="notification-card-list">
                <article
                  v-for="item in visibleMobileAnnouncements"
                  :key="item.id"
                  class="announcement-card"
                  :class="{ 'announcement-card--unread': !item.is_read }"
                >
                  <div class="announcement-card__title-row">
                    <span v-if="!item.is_read" class="unread-dot" aria-label="未讀" />
                    <strong>{{ item.title }}</strong>
                  </div>
                  <div class="announcement-card__tags">
                    <Tag :severity="severity(item.severity)">{{
                      severityLabel(item.severity)
                    }}</Tag>
                    <Tag :severity="item.is_read ? 'secondary' : 'info'">{{
                      item.is_read ? '已讀' : '未讀'
                    }}</Tag>
                  </div>
                  <div class="announcement-card__footer">
                    <small class="text-500">最近更新：{{ formatDate(item.updated_at) }}</small>
                    <Button
                      label="檢視"
                      size="small"
                      outlined
                      class="notification-view-button"
                      @click="openAnnouncement(item)"
                    />
                  </div>
                </article>
              </div>
              <Paginator
                v-if="announcements.length > ANNOUNCEMENT_PAGE_SIZE"
                :first="announcementFirst"
                :rows="ANNOUNCEMENT_PAGE_SIZE"
                :totalRecords="announcements.length"
                :pageLinkSize="1"
                template="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink"
                class="notification-mobile-paginator"
                @page="announcementFirst = $event.first"
              />
            </div>
          </TabPanel>

          <TabPanel value="personal">
            <div class="personal-toolbar">
              <span class="text-sm text-500">{{ counts.personal_notifications }} 則未讀</span>
              <Button
                label="全部標記為已讀"
                icon="pi pi-check-circle"
                size="small"
                outlined
                class="personal-mark-all-button"
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
                <i :class="notificationIcon(item.notification_type)" aria-hidden="true" />
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
  'open-personal-source',
])
const activeTab = ref('announcements')
const detailVisible = ref(false)
const selectedItem = ref(null)
const selectedType = ref('announcement')
const ANNOUNCEMENT_PAGE_SIZE = 5
const announcementFirst = ref(0)
const renderedBody = computed(() => renderMarkdown(selectedItem.value?.body || ''))
const visibleMobileAnnouncements = computed(() =>
  props.announcements.slice(
    announcementFirst.value,
    announcementFirst.value + ANNOUNCEMENT_PAGE_SIZE
  )
)
const severity = (value) => (value === 'danger' ? 'danger' : 'info')
const severityLabel = (value) => (value === 'danger' ? '重要' : '一般')

function openAnnouncement(item) {
  selectedType.value = 'announcement'
  selectedItem.value = item
  detailVisible.value = true
  if (!item.is_read) emit('mark-announcement-read', item.id)
}
function openPersonal(item) {
  if (!item.read_at) emit('mark-personal-read', item.id)
  if (
    item.source_available &&
    ['archive_discussion_thread', 'archive_submission'].includes(item.source_type)
  ) {
    emit('open-personal-source', item)
    return
  }
  selectedType.value = 'personal'
  selectedItem.value = item
  detailVisible.value = true
}
function notificationIcon(type) {
  const icons = {
    discussion_reply: 'pi pi-reply',
    discussion_like: 'pi pi-heart-fill',
    discussion_pin: 'pi pi-bookmark-fill',
    archive_submission_approved: 'pi pi-check-circle',
    archive_submission_rejected: 'pi pi-undo',
    archive_submission_takedown: 'pi pi-eye-slash',
    comment_report_submitted: 'pi pi-flag',
    comment_report_result: 'pi pi-verified',
  }
  return `${icons[type] || 'pi pi-bell'} personal-item__icon`
}
watch(
  () => props.visible,
  (visible) => {
    if (!visible) detailVisible.value = false
  }
)
watch(
  () => props.announcements.length,
  (length) => {
    const lastPageFirst = Math.max(
      0,
      Math.floor(Math.max(0, length - 1) / ANNOUNCEMENT_PAGE_SIZE) * ANNOUNCEMENT_PAGE_SIZE
    )
    if (announcementFirst.value > lastPageFirst) announcementFirst.value = lastPageFirst
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
.notification-dialog-header {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 0.5rem;
}
.notification-dialog-header__title {
  font-size: 1.25rem;
  font-weight: 600;
  line-height: 1.25;
  white-space: nowrap;
}
.notification-center-tabs {
  container-name: notification-center;
  container-type: inline-size;
  min-width: 0;
}
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
.notification-mobile-announcements {
  display: none;
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
.personal-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
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
@container notification-center (max-width: 640px) {
  .notification-desktop-announcements {
    display: none;
  }
  .notification-mobile-announcements {
    display: block;
  }
  .notification-card-list {
    display: grid;
    gap: 0.55rem;
  }
  .announcement-card {
    display: grid;
    min-width: 0;
    gap: 0.55rem;
    padding: 0.7rem;
    border: 1px solid var(--surface-border);
    border-radius: var(--content-border-radius);
    background: var(--surface-card);
  }
  .announcement-card--unread {
    background: var(--highlight-bg);
  }
  .announcement-card__title-row,
  .announcement-card__tags,
  .announcement-card__footer {
    display: flex;
    min-width: 0;
    align-items: center;
  }
  .announcement-card__title-row {
    gap: 0.45rem;
  }
  .announcement-card__title-row strong {
    min-width: 0;
    overflow-wrap: anywhere;
  }
  .announcement-card__tags {
    flex-wrap: wrap;
    gap: 0.35rem;
  }
  .announcement-card__footer {
    justify-content: space-between;
    gap: 0.55rem;
  }
  .announcement-card__footer small {
    min-width: 0;
    overflow-wrap: anywhere;
  }
  :deep(.p-tablist-tab-list) {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    width: 100%;
  }
  :deep(.p-tablist-prev-button),
  :deep(.p-tablist-next-button) {
    display: none;
  }
  :deep(.p-tab) {
    min-width: 0;
    justify-content: center;
    white-space: nowrap;
  }
  :deep(.p-tabpanels) {
    padding: 0.75rem 0 0;
  }
  :deep(.notification-mobile-paginator.p-paginator) {
    justify-content: center;
    gap: 0.1rem;
    padding: 0.55rem 0 0;
    background: transparent;
  }
  :deep(.notification-mobile-paginator .p-paginator-first),
  :deep(.notification-mobile-paginator .p-paginator-prev),
  :deep(.notification-mobile-paginator .p-paginator-page),
  :deep(.notification-mobile-paginator .p-paginator-next),
  :deep(.notification-mobile-paginator .p-paginator-last) {
    min-width: 2.25rem;
    width: 2.25rem;
    height: 2.25rem;
  }
  .personal-toolbar {
    align-items: flex-start;
    flex-wrap: wrap;
  }
  :deep(.personal-mark-all-button.p-button) {
    margin-left: auto;
    white-space: nowrap;
  }
  .personal-list {
    max-height: none;
    overflow: visible;
  }
  .personal-item {
    grid-template-columns: auto minmax(0, 1fr);
    gap: 0.55rem;
    padding: 0.7rem;
  }
  .personal-item > .p-button {
    grid-column: 2;
    justify-self: end;
  }
  .personal-item__body p {
    display: -webkit-box;
    overflow: hidden;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 3;
  }
}

@media (max-width: 640px) {
  :deep(.notification-center-dialog.p-dialog) {
    width: calc(100vw - 1rem) !important;
    max-width: calc(100vw - 1rem) !important;
    max-height: calc(100dvh - 1rem);
    margin-inline: max(0.5rem, env(safe-area-inset-left));
    overflow: hidden;
  }
  :deep(.notification-center-dialog .p-dialog-header) {
    flex: 0 0 auto;
    padding: 0.85rem max(0.85rem, env(safe-area-inset-right)) 0.75rem
      max(0.85rem, env(safe-area-inset-left));
  }
  :deep(.notification-center-dialog .p-dialog-content) {
    min-height: 0;
    padding: 0 0.75rem max(0.75rem, env(safe-area-inset-bottom));
    overflow-x: hidden;
    overflow-y: auto;
    overscroll-behavior: contain;
  }
  .notification-dialog-header {
    gap: 0.4rem;
  }
  .notification-dialog-header__title {
    font-size: 1.05rem;
  }
}
</style>
