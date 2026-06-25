<template>
  <div class="h-full px-2 md:px-4 admin-container">
    <div class="card h-full flex flex-col">
      <Tabs :value="currentTab" class="flex-1" @update:value="handleTabChange">
        <TabList>
          <Tab value="0">課程管理</Tab>
          <Tab value="1">使用者管理</Tab>
          <Tab value="2">公告管理</Tab>
          <Tab value="3">審核中心</Tab>
        </TabList>
        <TabPanels>
          <TabPanel value="0">
            <div class="p-2 md:p-4">
              <section class="admin-section mb-5">
                <div class="flex flex-column md:flex-row justify-content-between align-items-start md:align-items-center gap-3 mb-3">
                  <div>
                    <h3 class="m-0">課程分類</h3>
                    <p class="m-0 text-sm text-500">管理左側分類順序、分類名稱與科目標籤</p>
                  </div>
                  <Button
                    label="新增分類"
                    icon="pi pi-plus"
                    severity="success"
                    outlined
                    @click="openCreateCategoryDialog"
                  />
                </div>
                <DataTable :value="courseCategories" tableStyle="min-width: 44rem">
                  <Column header="順序" style="width: 12rem">
                    <template #body="{ data }">
                      <div class="flex align-items-center gap-2">
                        <span class="text-sm text-500 w-2rem">{{ getCategoryPosition(data) + 1 }}</span>
                        <Button
                          icon="pi pi-arrow-up"
                          severity="secondary"
                          text
                          rounded
                          size="small"
                          :disabled="!canMoveCategory(data, -1) || categoryOrderLoading"
                          @click="moveCategory(data, -1)"
                        />
                        <Button
                          icon="pi pi-arrow-down"
                          severity="secondary"
                          text
                          rounded
                          size="small"
                          :disabled="!canMoveCategory(data, 1) || categoryOrderLoading"
                          @click="moveCategory(data, 1)"
                        />
                      </div>
                    </template>
                  </Column>
                  <Column field="name" header="分類名稱" />
                  <Column field="label" header="科目標籤">
                    <template #body="{ data }">
                      <Tag severity="secondary">{{ data.label || data.name }}</Tag>
                    </template>
                  </Column>
                  <Column field="key" header="Key" />
                  <Column field="is_active" header="狀態" style="width: 8rem">
                    <template #body="{ data }">
                      <Tag :severity="data.is_active ? 'success' : 'secondary'">
                        {{ data.is_active ? '啟用中' : '已停用' }}
                      </Tag>
                    </template>
                  </Column>
                  <Column header="操作" style="width: 20rem">
                    <template #body="{ data }">
                      <div class="flex gap-2 flex-wrap">
                        <Button icon="pi pi-pencil" label="編輯" size="small" outlined @click="openEditCategoryDialog(data)" />
                        <Button
                          :icon="data.is_active ? 'pi pi-eye-slash' : 'pi pi-check'"
                          :label="data.is_active ? '停用' : '啟用'"
                          size="small"
                          :severity="data.is_active ? 'warn' : 'success'"
                          outlined
                          @click="confirmToggleCategory(data)"
                        />
                        <Button
                          icon="pi pi-trash"
                          label="刪除"
                          size="small"
                          severity="danger"
                          outlined
                          @click="confirmDeleteCategory(data)"
                        />
                      </div>
                    </template>
                  </Column>
                </DataTable>
              </section>

              <div
                class="flex flex-column md:flex-row justify-content-between align-items-start md:align-items-center mb-4 gap-3"
              >
                <div class="flex flex-column md:flex-row gap-3 w-full md:w-auto">
                  <div class="relative w-full md:w-auto">
                    <i class="pi pi-search search-icon"></i>
                    <InputText v-model="searchQuery" placeholder="搜尋課程" class="w-full pl-6" />
                  </div>
                  <Select
                    v-model="filterCategory"
                    :options="categoryOptions"
                    optionLabel="name"
                    optionValue="value"
                    placeholder="篩選分類"
                    showClear
                    class="w-full md:w-14rem"
                  />
                </div>
                <Button
                  label="新增課程"
                  icon="pi pi-plus"
                  severity="success"
                  @click="openCreateDialog"
                  class="w-full md:w-auto"
                />
              </div>

              <ProgressSpinner
                v-if="coursesLoading"
                class="w-full flex justify-content-center mt-4"
                strokeWidth="4"
              />
              <DataTable
                v-else
                :value="filteredCourses"
                paginator
                :rows="10"
                :rowsPerPageOptions="[5, 10, 15, 25, 50]"
                tableStyle="min-width: 50rem"
                scrollable
                scrollHeight="65vh"
              >
                <Column header="順序" style="width: 18%">
                  <template #body="{ data }">
                    <div class="flex align-items-center gap-2">
                      <span class="text-sm text-500 w-2rem">
                        {{ getCoursePosition(data) + 1 }}
                      </span>
                      <Button
                        icon="pi pi-arrow-up"
                        severity="secondary"
                        text
                        rounded
                        size="small"
                        aria-label="上移"
                        :disabled="!canMoveCourse(data, -1) || courseOrderLoading"
                        @click="moveCourse(data, -1)"
                      />
                      <Button
                        icon="pi pi-arrow-down"
                        severity="secondary"
                        text
                        rounded
                        size="small"
                        aria-label="下移"
                        :disabled="!canMoveCourse(data, 1) || courseOrderLoading"
                        @click="moveCourse(data, 1)"
                      />
                    </div>
                  </template>
                </Column>
                <Column field="name" header="課程名稱" style="width: 32%"></Column>
                <Column field="category" header="分類" style="width: 22%">
                  <template #body="{ data }">
                    <Tag :severity="getCategorySeverity(data.category)" class="text-sm">
                      {{ getCategoryName(data.category) }}
                    </Tag>
                  </template>
                </Column>
                <Column header="操作" style="width: 18%">
                  <template #body="{ data }">
                    <div class="flex gap-2">
                      <Button
                        icon="pi pi-pencil"
                        severity="warning"
                        size="small"
                        @click="openEditDialog(data)"
                        label="編輯"
                      />
                      <Button
                        icon="pi pi-trash"
                        severity="danger"
                        size="small"
                        @click="confirmDeleteCourse(data)"
                        label="刪除"
                      />
                    </div>
                  </template>
                </Column>
              </DataTable>
            </div>
          </TabPanel>

          <TabPanel value="1">
            <div class="p-2 md:p-4">
              <div
                class="flex flex-column md:flex-row justify-content-between align-items-start md:align-items-center mb-4 gap-3"
              >
                <div class="flex flex-column md:flex-row gap-3 w-full md:w-auto">
                  <div class="relative w-full md:w-auto">
                    <i class="pi pi-search search-icon"></i>
                    <InputText
                      v-model="userSearchQuery"
                      placeholder="搜尋使用者"
                      class="w-full pl-6"
                    />
                  </div>
                  <Select
                    v-model="filterUserType"
                    :options="userTypeFilterOptions"
                    optionLabel="name"
                    optionValue="value"
                    placeholder="篩選類型"
                    showClear
                    class="w-full md:w-14rem"
                  />
                </div>
                <Button
                  label="新增使用者"
                  icon="pi pi-plus"
                  severity="success"
                  @click="openCreateUserDialog"
                  class="w-full md:w-auto"
                />
              </div>

              <ProgressSpinner
                v-if="usersLoading"
                class="w-full flex justify-content-center mt-4"
                strokeWidth="4"
              />
              <DataTable
                v-else
                :value="filteredUsers"
                paginator
                :rows="10"
                :rowsPerPageOptions="[5, 10, 15, 25, 50]"
                tableStyle="min-width: 50rem"
                scrollable
                scrollHeight="65vh"
                :multiSortMeta="userSortMeta"
                sortMode="multiple"
                removableSort
              >
                <Column field="name" header="使用者名稱" sortable style="width: 15%"></Column>
                <Column field="email" header="電子郵件" sortable style="width: 20%"></Column>
                <Column field="is_admin" header="管理員權限" sortable style="width: 15%">
                  <template #body="{ data }">
                    <Tag :severity="data.is_admin ? 'success' : 'secondary'" class="text-sm">
                      {{ data.is_admin ? '是' : '否' }}
                    </Tag>
                  </template>
                </Column>
                <Column field="is_local" header="帳號類型" sortable style="width: 15%">
                  <template #body="{ data }">
                    <Tag :severity="data.is_local ? 'info' : 'warning'" class="text-sm">
                      {{ data.is_local ? '本地帳號' : '外部帳號' }}
                    </Tag>
                  </template>
                </Column>
                <Column field="last_login" header="最近登入" sortable style="width: 15%">
                  <template #body="{ data }">
                    <span v-if="data.last_login" class="text-sm">
                      {{ formatDateTime(data.last_login) }}
                    </span>
                    <span v-else class="text-sm text-500"> 從未登入 </span>
                  </template>
                </Column>
                <Column header="操作" style="width: 20%">
                  <template #body="{ data }">
                    <div class="flex gap-2">
                      <Button
                        icon="pi pi-pencil"
                        severity="warning"
                        size="small"
                        @click="openEditUserDialog(data)"
                        label="編輯"
                      />
                      <Button
                        icon="pi pi-trash"
                        severity="danger"
                        size="small"
                        @click="confirmDeleteUser(data)"
                        label="刪除"
                        :disabled="data.id === currentUserId"
                      />
                    </div>
                  </template>
                </Column>
              </DataTable>
            </div>
          </TabPanel>

          <TabPanel value="2">
            <div class="p-2 md:p-4">
              <div
                class="flex flex-column md:flex-row justify-content-between align-items-start md:align-items-center mb-4 gap-3"
              >
                <div class="flex flex-column md:flex-row gap-3 w-full md:w-auto">
                  <div class="relative w-full md:w-auto">
                    <i class="pi pi-search search-icon"></i>
                    <InputText
                      v-model="notificationSearchQuery"
                      placeholder="搜尋公告"
                      class="w-full pl-6"
                    />
                  </div>
                  <Select
                    v-model="notificationSeverityFilter"
                    :options="notificationSeverityFilterOptions"
                    optionLabel="label"
                    optionValue="value"
                    placeholder="篩選重要程度"
                    showClear
                    class="w-full md:w-14rem"
                  />
                </div>
                <Button
                  label="新增公告"
                  icon="pi pi-plus"
                  severity="success"
                  @click="openNotificationCreateDialog"
                  class="w-full md:w-auto"
                />
              </div>

              <ProgressSpinner
                v-if="notificationsLoading"
                class="w-full flex justify-content-center mt-4"
                strokeWidth="4"
              />
              <DataTable
                v-else
                :value="filteredNotifications"
                paginator
                :rows="10"
                :rowsPerPageOptions="[5, 10, 15, 25, 50]"
                tableStyle="min-width: 50rem"
                scrollable
                scrollHeight="65vh"
                sortMode="multiple"
                :multiSortMeta="notificationSortMeta"
                removableSort
              >
                <Column field="title" header="標題" sortable style="width: 26%"></Column>
                <Column field="severity" header="重要程度" sortable style="width: 12%">
                  <template #body="{ data }">
                    <Tag :severity="getNotificationSeverity(data.severity)">
                      {{ getNotificationSeverityLabel(data.severity) }}
                    </Tag>
                  </template>
                </Column>
                <Column
                  field="is_active"
                  sortField="is_active"
                  header="啟用中"
                  sortable
                  style="width: 12%"
                >
                  <template #body="{ data }">
                    <Tag :severity="data.is_active ? 'success' : 'secondary'">
                      {{ data.is_active ? '啟用中' : '已停用' }}
                    </Tag>
                  </template>
                </Column>
                <Column header="生效中" sortField="effectiveOrder" sortable style="width: 12%">
                  <template #body="{ data }">
                    <Tag :severity="isNotificationEffective(data) ? 'success' : 'secondary'">
                      {{ isNotificationEffective(data) ? '生效中' : '未生效' }}
                    </Tag>
                  </template>
                </Column>
                <Column
                  field="updated_at"
                  sortField="updated_at"
                  header="最近更新"
                  sortable
                  style="width: 18%"
                >
                  <template #body="{ data }">
                    <span class="text-sm text-700">
                      {{ formatNotificationDate(data.updated_at || data.created_at) }}
                    </span>
                  </template>
                </Column>
                <Column header="操作" style="width: 20%">
                  <template #body="{ data }">
                    <div class="flex gap-2">
                      <Button
                        icon="pi pi-pencil"
                        severity="warning"
                        size="small"
                        @click="openNotificationEditDialog(data)"
                        label="編輯"
                      />
                      <Button
                        icon="pi pi-trash"
                        severity="danger"
                        size="small"
                        @click="confirmDeleteNotification(data)"
                        label="刪除"
                      />
                    </div>
                  </template>
                </Column>
              </DataTable>
            </div>
          </TabPanel>

          <TabPanel value="3">
            <div class="p-2 md:p-4 review-center">
              <div class="review-section">
                <div class="review-section-header">
                  <h3>新課程 / 新分類考古申請</h3>
                  <Button icon="pi pi-refresh" label="重新整理" size="small" outlined @click="loadReviewItems" />
                </div>
                <DataTable :value="newCourseArchiveRequests" :loading="reviewLoading" tableStyle="min-width: 60rem">
                  <Column field="subject" header="課程" />
                  <Column header="投稿類型">
                    <template #body="{ data }">
                      <Tag :severity="getArchiveSubmissionKindSeverity(data)">
                        {{ getArchiveSubmissionKind(data) }}
                      </Tag>
                    </template>
                  </Column>
                  <Column field="name" header="考試名稱" />
                  <Column field="professor" header="授課教師" />
                  <Column field="academic_year" header="學期">
                    <template #body="{ data }">{{ formatAcademicTerm(data.academic_year) }}</template>
                  </Column>
                  <Column field="status" header="狀態">
                    <template #body="{ data }">
                      <Tag :severity="getSubmissionSeverity(data.status)">
                        {{ getSubmissionLabel(data.status) }}
                      </Tag>
                    </template>
                  </Column>
                  <Column header="操作">
                    <template #body="{ data }">
	                      <div class="flex gap-2">
	                        <Button
	                          label="查看/編輯"
	                          icon="pi pi-search"
	                          size="small"
	                          severity="secondary"
	                          outlined
	                          @click="openArchiveRequestDialog(data)"
	                        />
	                        <Button
	                          label="通過"
                          icon="pi pi-check"
                          size="small"
                          severity="success"
                          @click="reviewArchiveSubmission(data.id, 'approve')"
                        />
                        <Button
                          label="退回"
                          icon="pi pi-times"
                          size="small"
                          severity="danger"
                          outlined
                          @click="reviewArchiveSubmission(data.id, 'reject')"
                        />
                        <Button
                          label="刪除"
                          icon="pi pi-trash"
                          size="small"
                          severity="danger"
                          text
                          @click="confirmDeleteArchiveSubmission(data)"
                        />
                      </div>
                    </template>
                  </Column>
                </DataTable>
              </div>

              <div class="review-section mt-5">
                <div class="review-section-header">
                  <h3>既有課程考古申請</h3>
                </div>
                <DataTable :value="existingCourseArchiveRequests" :loading="reviewLoading" tableStyle="min-width: 60rem">
                  <Column field="subject" header="課程" />
                  <Column field="name" header="考試名稱" />
                  <Column field="professor" header="授課教師" />
                  <Column field="academic_year" header="學期">
                    <template #body="{ data }">{{ formatAcademicTerm(data.academic_year) }}</template>
                  </Column>
                  <Column field="status" header="狀態">
                    <template #body="{ data }">
                      <Tag :severity="getSubmissionSeverity(data.status)">
                        {{ getSubmissionLabel(data.status) }}
                      </Tag>
                    </template>
                  </Column>
                  <Column header="操作">
                    <template #body="{ data }">
                      <div class="flex gap-2">
                        <Button
                          label="查看/編輯"
                          icon="pi pi-search"
                          size="small"
                          severity="secondary"
                          outlined
                          @click="openArchiveRequestDialog(data)"
                        />
                        <Button
                          label="通過"
                          icon="pi pi-check"
                          size="small"
                          severity="success"
                          @click="reviewArchiveSubmission(data.id, 'approve')"
                        />
                        <Button
                          label="退回"
                          icon="pi pi-times"
                          size="small"
                          severity="danger"
                          outlined
                          @click="reviewArchiveSubmission(data.id, 'reject')"
                        />
                        <Button
                          label="刪除"
                          icon="pi pi-trash"
                          size="small"
                          severity="danger"
                          text
                          @click="confirmDeleteArchiveSubmission(data)"
                        />
                      </div>
                    </template>
                  </Column>
                </DataTable>
              </div>
            </div>
          </TabPanel>
        </TabPanels>
      </Tabs>

      <Dialog
        :visible="showCourseDialog"
        @update:visible="showCourseDialog = $event"
        :modal="true"
        :draggable="false"
        :closeOnEscape="false"
        :header="editingCourse ? '編輯課程' : '新增課程'"
        :style="{ width: '450px', maxWidth: '90vw' }"
        :autoFocus="false"
      >
        <div class="flex flex-column gap-4">
          <div class="flex flex-column gap-2">
            <label>課程名稱</label>
            <InputText
              v-model="courseForm.name"
              placeholder="輸入課程名稱"
              class="w-full"
              :class="{ 'p-invalid': courseFormErrors.name }"
            />
            <small v-if="courseFormErrors.name" class="p-error">
              {{ courseFormErrors.name }}
            </small>
          </div>

          <div class="flex flex-column gap-2">
            <label>分類</label>
            <Select
              v-model="courseForm.category"
              :options="categoryOptions"
              optionLabel="name"
              optionValue="value"
              placeholder="選擇分類"
              class="w-full"
              :class="{ 'p-invalid': courseFormErrors.category }"
            />
            <small v-if="courseFormErrors.category" class="p-error">
              {{ courseFormErrors.category }}
            </small>
          </div>
        </div>

        <div class="flex pt-6 justify-end gap-2.5">
          <Button label="取消" icon="pi pi-times" severity="secondary" @click="closeCourseDialog" />
          <Button
            :label="editingCourse ? '更新' : '新增'"
            :icon="editingCourse ? 'pi pi-check' : 'pi pi-plus'"
            severity="success"
            @click="saveCourse"
            :loading="saveLoading"
          />
        </div>
      </Dialog>

      <Dialog
        :visible="showCategoryDialog"
        @update:visible="showCategoryDialog = $event"
        :modal="true"
        :draggable="false"
        :header="editingCategory ? '編輯課程分類' : '新增課程分類'"
        :style="{ width: '480px', maxWidth: '92vw' }"
        :autoFocus="false"
      >
        <div class="flex flex-column gap-4">
          <div class="flex flex-column gap-2">
            <label>分類 Key</label>
            <InputText
              v-model="categoryForm.key"
              placeholder="例如 advanced-physics"
              class="w-full"
              :class="{ 'p-invalid': categoryFormErrors.key }"
            />
            <small v-if="categoryFormErrors.key" class="p-error">{{ categoryFormErrors.key }}</small>
          </div>
          <div class="flex flex-column gap-2">
            <label>顯示名稱</label>
            <InputText
              v-model="categoryForm.name"
              placeholder="例如 進階物理"
              class="w-full"
              :class="{ 'p-invalid': categoryFormErrors.name }"
            />
            <small v-if="categoryFormErrors.name" class="p-error">{{ categoryFormErrors.name }}</small>
          </div>
          <div class="flex flex-column gap-2">
            <label>科目旁小標籤</label>
            <InputText v-model="categoryForm.label" placeholder="例如 進階" class="w-full" />
          </div>
          <div class="flex flex-column gap-2">
            <label>PrimeIcons class</label>
            <InputText v-model="categoryForm.icon" placeholder="pi pi-fw pi-book" class="w-full" />
          </div>
        </div>

        <div class="flex pt-6 justify-end gap-2.5">
          <Button label="取消" icon="pi pi-times" severity="secondary" @click="closeCategoryDialog" />
          <Button
            :label="editingCategory ? '更新' : '新增'"
            :icon="editingCategory ? 'pi pi-check' : 'pi pi-plus'"
            severity="success"
            :loading="categorySaveLoading"
            @click="saveCategory"
          />
        </div>
      </Dialog>

      <Dialog
        v-model:visible="showArchiveRequestDialog"
        header="考古題投稿詳情"
        modal
        :draggable="false"
        :style="{ width: '760px', maxWidth: '96vw' }"
      >
        <div class="request-summary mb-4">
          <Tag :severity="getArchiveSubmissionKindSeverity(selectedArchiveRequest)">
            {{ getArchiveSubmissionKind(selectedArchiveRequest) }}
          </Tag>
          <span v-if="selectedArchiveRequest?.requested_course_name">
            這筆投稿通過後會建立或使用新課程「{{ selectedArchiveRequest.requested_course_name }}」。
          </span>
          <span v-else>這筆投稿會掛到既有課程。</span>
        </div>
        <div class="grid">
          <template v-if="archiveRequestEditForm.requested_category_key">
            <div class="col-12 md:col-6 flex flex-column gap-2">
              <label>申請分類 Key</label>
              <InputText v-model="archiveRequestEditForm.requested_category_key" :disabled="!canEditSelectedArchiveRequest" />
            </div>
            <div class="col-12 md:col-6 flex flex-column gap-2">
              <label>申請分類名稱</label>
              <InputText v-model="archiveRequestEditForm.requested_category_name" :disabled="!canEditSelectedArchiveRequest" />
            </div>
            <div class="col-12 md:col-6 flex flex-column gap-2">
              <label>科目旁小標籤</label>
              <InputText v-model="archiveRequestEditForm.requested_category_label" :disabled="!canEditSelectedArchiveRequest" />
            </div>
          </template>
          <div v-if="archiveRequestEditForm.requested_course_name" class="col-12 md:col-6 flex flex-column gap-2">
            <label>申請課程名稱</label>
            <InputText v-model="archiveRequestEditForm.requested_course_name" :disabled="!canEditSelectedArchiveRequest" />
          </div>
          <div class="col-12 md:col-6 flex flex-column gap-2">
            <label>課程</label>
            <InputText v-model="archiveRequestEditForm.subject" :disabled="!canEditSelectedArchiveRequest" />
          </div>
          <div v-if="archiveRequestEditForm.requested_category_key" class="col-12 md:col-6 flex flex-column gap-2">
            <label>分類 Key</label>
            <InputText v-model="archiveRequestEditForm.category" :disabled="!canEditSelectedArchiveRequest" />
          </div>
          <div v-else class="col-12 md:col-6 flex flex-column gap-2">
            <label>分類</label>
            <Select
              v-model="archiveRequestEditForm.category"
              :options="categoryOptions"
              optionLabel="name"
              optionValue="value"
              :disabled="!canEditSelectedArchiveRequest"
            />
          </div>
          <div class="col-12 md:col-6 flex flex-column gap-2">
            <label>考試名稱</label>
            <InputText v-model="archiveRequestEditForm.name" :disabled="!canEditSelectedArchiveRequest" />
          </div>
          <div class="col-12 md:col-6 flex flex-column gap-2">
            <label>授課教師</label>
            <InputText v-model="archiveRequestEditForm.professor" :disabled="!canEditSelectedArchiveRequest" />
          </div>
          <div class="col-12 md:col-6 flex flex-column gap-2">
            <label>學期代碼</label>
            <InputNumber v-model="archiveRequestEditForm.academic_year" :disabled="!canEditSelectedArchiveRequest" :useGrouping="false" />
          </div>
          <div class="col-12 md:col-6 flex flex-column gap-2">
            <label>考試類型</label>
            <Select
              v-model="archiveRequestEditForm.archive_type"
              :options="archiveTypeOptions"
              optionLabel="name"
              optionValue="value"
              :disabled="!canEditSelectedArchiveRequest"
            />
          </div>
          <div class="col-12 flex align-items-center gap-2">
            <Checkbox v-model="archiveRequestEditForm.has_answers" :binary="true" :disabled="!canEditSelectedArchiveRequest" />
            <label>附解答</label>
          </div>
        </div>

        <div class="mt-4">
          <h4 class="mb-2">同課程同考試比對</h4>
          <div v-if="comparisonLoading" class="text-sm text-500">載入中...</div>
          <div v-else-if="comparisonArchives.length === 0" class="text-sm text-500">
            沒有找到相同課程、學期與類型的既有考古題。
          </div>
          <DataTable v-else :value="comparisonArchives" tableStyle="min-width: 36rem">
            <Column field="name" header="考試名稱" />
            <Column field="professor" header="授課教師" />
            <Column field="academic_year" header="學期">
              <template #body="{ data }">{{ formatAcademicTerm(data.academic_year) }}</template>
            </Column>
            <Column field="has_answers" header="解答">
              <template #body="{ data }">{{ data.has_answers ? '有' : '無' }}</template>
            </Column>
            <Column header="操作" style="width: 10rem">
              <template #body="{ data }">
                <Button
                  label="並排預覽"
                  icon="pi pi-columns"
                  size="small"
                  outlined
                  :loading="comparePreviewLoading && comparePreviewArchive?.id === data.id"
                  @click="openComparePreview(data)"
                />
              </template>
            </Column>
          </DataTable>
        </div>

        <div class="mt-4 review-history">
          <h4 class="mb-2">此帳號投稿紀錄</h4>
          <div class="review-requester mb-2">
            <span class="text-sm text-500">投稿帳號</span>
            <strong>{{ getRequesterDisplay(selectedArchiveRequest) }}</strong>
          </div>
          <div v-if="getRequesterHistory(selectedArchiveRequest?.requester_id).length === 0" class="text-sm text-500">
            尚無其他投稿紀錄
          </div>
          <div
            v-for="item in getRequesterHistory(selectedArchiveRequest?.requester_id)"
            :key="`${item.kind}-${item.id}`"
            class="review-history-row"
          >
            <span class="review-history-title">
              {{ item.title }}
              <small>投稿：{{ item.requester }}</small>
            </span>
            <Tag :severity="getSubmissionSeverity(item.status)">{{ getSubmissionLabel(item.status) }}</Tag>
          </div>
        </div>

        <div class="flex justify-end gap-2 mt-4">
          <Button label="關閉" severity="secondary" outlined @click="showArchiveRequestDialog = false" />
          <Button
            label="預覽 PDF"
            icon="pi pi-eye"
            severity="secondary"
            outlined
            :loading="archiveRequestPreviewLoading"
            @click="previewArchiveRequestFile"
          />
          <Button
            label="儲存修改"
            icon="pi pi-save"
            :disabled="!canEditSelectedArchiveRequest"
            :loading="reviewEditLoading"
            @click="saveArchiveRequestEdit"
          />
          <Button
            label="通過"
            icon="pi pi-check"
            severity="success"
            :disabled="!canEditSelectedArchiveRequest"
            @click="reviewArchiveSubmission(selectedArchiveRequest.id, 'approve')"
          />
          <Button
            label="退回"
            icon="pi pi-times"
            severity="danger"
            outlined
            :disabled="!canEditSelectedArchiveRequest"
            @click="reviewArchiveSubmission(selectedArchiveRequest.id, 'reject')"
          />
          <Button
            label="刪除"
            icon="pi pi-trash"
            severity="danger"
            text
            :disabled="!selectedArchiveRequest"
            @click="confirmDeleteArchiveSubmission(selectedArchiveRequest)"
          />
        </div>
      </Dialog>

      <PdfPreviewModal
        :visible="showArchiveRequestPreview"
        @update:visible="showArchiveRequestPreview = $event"
        :previewUrl="archiveRequestPreviewUrl"
        :title="selectedArchiveRequest?.name || ''"
        :academicYear="formatAcademicTerm(selectedArchiveRequest?.academic_year)"
        :archiveType="selectedArchiveRequest?.archive_type || ''"
        :courseName="selectedArchiveRequest?.subject || ''"
        :professorName="selectedArchiveRequest?.professor || ''"
        :loading="archiveRequestPreviewLoading"
        :error="archiveRequestPreviewError"
        :showDownload="false"
        :showDiscussion="false"
        @hide="closeArchiveRequestPreview"
        @error="handleArchiveRequestPreviewError"
      />

      <Dialog
        v-model:visible="showComparePreview"
        modal
        maximizable
        :draggable="false"
        :style="{ width: 'min(1500px, 96vw)', height: 'min(92vh, 92dvh)' }"
        :contentStyle="{ height: '100%', display: 'flex', flexDirection: 'column' }"
        header="申請考卷與既有考卷比對"
        @hide="closeComparePreview"
      >
        <div v-if="comparePreviewError" class="compare-preview-error">
          <i class="pi pi-exclamation-circle"></i>
          無法載入比對 PDF，請稍後再試。
        </div>
        <div v-else class="compare-preview-grid">
          <section class="compare-preview-pane">
            <header>
              <span>申請考卷</span>
              <strong>{{ selectedArchiveRequest?.name }}</strong>
            </header>
            <iframe
              v-if="compareRequestPreviewUrl"
              :src="compareRequestPreviewUrl"
              title="申請考卷 PDF 預覽"
            ></iframe>
            <ProgressSpinner v-else strokeWidth="4" />
          </section>
          <section class="compare-preview-pane">
            <header>
              <span>既有考卷</span>
              <strong>{{ comparePreviewArchive?.name }}</strong>
            </header>
            <iframe
              v-if="compareArchivePreviewUrl"
              :src="compareArchivePreviewUrl"
              title="既有考卷 PDF 預覽"
            ></iframe>
            <ProgressSpinner v-else strokeWidth="4" />
          </section>
        </div>
      </Dialog>

      <Dialog
        :visible="showUserDialog"
        @update:visible="showUserDialog = $event"
        :modal="true"
        :draggable="false"
        :closeOnEscape="false"
        :header="editingUser ? '編輯使用者' : '新增使用者'"
        :style="{ width: '450px', maxWidth: '90vw' }"
        :autoFocus="false"
      >
        <div class="flex flex-column gap-4">
          <div class="flex flex-column gap-2">
            <label>使用者名稱</label>
            <InputText
              v-model="userForm.name"
              placeholder="輸入使用者名稱"
              class="w-full"
              :class="{ 'p-invalid': userFormErrors.name }"
            />
            <small v-if="userFormErrors.name" class="p-error">
              {{ userFormErrors.name }}
            </small>
          </div>

          <div class="flex flex-column gap-2">
            <label>電子郵件</label>
            <InputText
              v-model="userForm.email"
              placeholder="輸入電子郵件"
              class="w-full"
              :class="{ 'p-invalid': userFormErrors.email }"
            />
            <small v-if="userFormErrors.email" class="p-error">
              {{ userFormErrors.email }}
            </small>
          </div>

          <div v-if="!editingUser" class="flex flex-column gap-2">
            <label>密碼</label>
            <Password
              v-model="userForm.password"
              placeholder="輸入密碼"
              class="w-full"
              inputClass="w-full"
              :class="{ 'p-invalid': userFormErrors.password }"
              toggleMask
              :feedback="false"
            />
            <small v-if="userFormErrors.password" class="p-error">
              {{ userFormErrors.password }}
            </small>
          </div>

          <div class="flex align-items-center gap-2">
            <Checkbox v-model="userForm.is_admin" :binary="true" />
            <label>管理員權限</label>
          </div>
        </div>

        <div class="flex pt-6 justify-end gap-2.5">
          <Button label="取消" icon="pi pi-times" severity="secondary" @click="closeUserDialog" />
          <Button
            :label="editingUser ? '更新' : '新增'"
            :icon="editingUser ? 'pi pi-check' : 'pi pi-plus'"
            severity="success"
            @click="saveUser"
            :loading="userSaveLoading"
          />
        </div>
      </Dialog>

      <Dialog
        :visible="showNotificationDialog"
        @update:visible="showNotificationDialog = $event"
        :modal="true"
        :draggable="false"
        :closeOnEscape="false"
        :header="editingNotification ? '編輯公告' : '新增公告'"
        :style="{ width: '540px', maxWidth: '92vw' }"
        :autoFocus="false"
      >
        <div class="flex flex-column gap-4">
          <div class="flex flex-column gap-2">
            <label>標題</label>
            <InputText
              v-model="notificationForm.title"
              placeholder="輸入公告標題"
              class="w-full"
              :class="{ 'p-invalid': notificationFormErrors.title }"
            />
            <small v-if="notificationFormErrors.title" class="p-error">
              {{ notificationFormErrors.title }}
            </small>
          </div>

          <div class="flex flex-column md:flex-row gap-3">
            <div class="flex-1 flex flex-column gap-2">
              <label>重要程度</label>
              <Select
                v-model="notificationForm.severity"
                :options="notificationSeverityOptions"
                optionLabel="label"
                optionValue="value"
                placeholder="選擇重要程度"
                class="w-full"
              />
            </div>
            <div class="flex align-items-center gap-2 mt-3 md:mt-5">
              <ToggleSwitch v-model="notificationForm.is_active" />
              <label class="m-0 font-medium">啟用公告</label>
            </div>
          </div>

          <div class="flex flex-column gap-2">
            <label>內容</label>
            <Textarea
              v-model="notificationForm.body"
              rows="6"
              autoResize
              class="w-full"
              placeholder="輸入公告內容"
              :class="{ 'p-invalid': notificationFormErrors.body }"
            />
            <small v-if="notificationFormErrors.body" class="p-error">
              {{ notificationFormErrors.body }}
            </small>
          </div>

          <div class="flex flex-column gap-3">
            <div class="flex flex-column gap-2">
              <label>生效時間 (選填)</label>
              <DatePicker
                v-model="notificationForm.starts_at"
                showTime
                hourFormat="24"
                :showIcon="true"
                placeholder="選擇生效時間"
                class="w-full"
              />
            </div>
            <div class="flex flex-column gap-2">
              <label>結束時間 (選填)</label>
              <DatePicker
                v-model="notificationForm.ends_at"
                showTime
                hourFormat="24"
                :showIcon="true"
                placeholder="選擇結束時間"
                class="w-full"
                :class="{ 'p-invalid': notificationFormErrors.ends_at }"
              />
              <small v-if="notificationFormErrors.ends_at" class="p-error">
                {{ notificationFormErrors.ends_at }}
              </small>
            </div>
          </div>
        </div>

        <div class="flex pt-6 justify-end gap-2.5">
          <Button
            label="取消"
            icon="pi pi-times"
            severity="secondary"
            @click="closeNotificationDialog"
          />
          <Button
            :label="editingNotification ? '更新' : '新增'"
            :icon="editingNotification ? 'pi pi-check' : 'pi pi-plus'"
            severity="success"
            @click="saveNotification"
            :loading="notificationSaveLoading"
          />
        </div>
      </Dialog>
    </div>
  </div>
</template>

<script setup>
defineOptions({
  name: 'AdminView',
})

import { ref, computed, watch, onBeforeUnmount } from 'vue'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import { getCurrentUser } from '../utils/auth'
import { isUnauthorizedError } from '../utils/http'
import { formatRelativeTime } from '../utils/time'
import {
  getCourses,
  createCourse,
  updateCourse,
  reorderCourses,
  deleteCourse,
  getUsers,
  createUser,
  updateUser,
  deleteUser,
  notificationService,
  courseService,
  archiveService,
} from '../api'
import { trackEvent, EVENTS } from '../utils/analytics'
import { STORAGE_KEYS, getLocalItem, setLocalItem } from '../utils/storage'
import PdfPreviewModal from '../components/PdfPreviewModal.vue'

const confirm = useConfirm()
const toast = useToast()

const courses = ref([])
const coursesLoading = ref(false)
const searchQuery = ref('')
const filterCategory = ref(null)
const courseOrderLoading = ref(false)

const showCourseDialog = ref(false)
const editingCourse = ref(null)
const saveLoading = ref(false)
const showCategoryDialog = ref(false)
const editingCategory = ref(null)
const categorySaveLoading = ref(false)
const categoryOrderLoading = ref(false)

const courseForm = ref({
  name: '',
  category: '',
})

const courseFormErrors = ref({})
const categoryForm = ref({
  key: '',
  name: '',
  label: '',
  icon: 'pi pi-fw pi-book',
})
const categoryFormErrors = ref({})
const users = ref([])
const usersLoading = ref(false)
const userSearchQuery = ref('')
const filterUserType = ref(null)

const userSortMeta = ref([
  { field: 'is_admin', order: -1 },
  { field: 'name', order: 1 },
])

const showUserDialog = ref(false)
const editingUser = ref(null)
const userSaveLoading = ref(false)

const userForm = ref({
  name: '',
  email: '',
  password: '',
  is_admin: false,
})

const userFormErrors = ref({})

const notifications = ref([])
const notificationsLoading = ref(false)
const notificationSearchQuery = ref('')
const notificationSeverityFilter = ref(null)

const notificationSortMeta = ref([
  { field: 'is_active', order: -1 },
  { field: 'effectiveOrder', order: -1 },
  { field: 'updated_at', order: -1 },
])

const notificationSeverityOptions = [
  { label: '一般', value: 'info' },
  { label: '重要', value: 'danger' },
]

const notificationSeverityFilterOptions = notificationSeverityOptions

const showNotificationDialog = ref(false)
const editingNotification = ref(null)
const notificationSaveLoading = ref(false)
const notificationForm = ref({
  title: '',
  body: '',
  severity: 'info',
  is_active: true,
  starts_at: null,
  ends_at: null,
})
const notificationFormErrors = ref({})
const reviewLoading = ref(false)
const archiveRequests = ref([])
const courseCategories = ref([])
const reviewEditLoading = ref(false)
const showArchiveRequestDialog = ref(false)
const selectedArchiveRequest = ref(null)
const comparisonArchives = ref([])
const comparisonLoading = ref(false)
const showArchiveRequestPreview = ref(false)
const archiveRequestPreviewUrl = ref('')
const archiveRequestPreviewLoading = ref(false)
const archiveRequestPreviewError = ref(false)
const showComparePreview = ref(false)
const comparePreviewArchive = ref(null)
const compareRequestPreviewUrl = ref('')
const compareArchivePreviewUrl = ref('')
const comparePreviewLoading = ref(false)
const comparePreviewError = ref(false)
const archiveRequestEditForm = ref({
  subject: '',
  category: '',
  name: '',
  academic_year: null,
  archive_type: '',
  professor: '',
  has_answers: false,
  requested_course_name: '',
  requested_category_key: '',
  requested_category_name: '',
  requested_category_label: '',
  requested_category_icon: '',
})
const archiveTypeOptions = [
  { name: '期中考', value: 'midterm' },
  { name: '期末考', value: 'final' },
  { name: '小考', value: 'quiz' },
  { name: '其他', value: 'other' },
]

const currentUserId = computed(() => getCurrentUser()?.id)
const canEditSelectedArchiveRequest = computed(() => Boolean(selectedArchiveRequest.value))
const newCourseArchiveRequests = computed(() =>
  archiveRequests.value.filter((item) => item.requested_course_name || item.requested_category_key)
)
const existingCourseArchiveRequests = computed(() =>
  archiveRequests.value.filter((item) => !item.requested_course_name && !item.requested_category_key)
)

const TAB_STORAGE_KEY = STORAGE_KEYS.local.ADMIN_CURRENT_TAB

const getInitialTab = () => {
  try {
    const savedTab = getLocalItem(TAB_STORAGE_KEY)
    if (savedTab && ['0', '1', '2', '3'].includes(savedTab)) {
      return savedTab
    }
  } catch (e) {
    console.error('Failed to load tab from storage:', e)
  }
  return '0'
}

const currentTab = ref(getInitialTab())

const categoryOptions = computed(() =>
  courseCategories.value.filter((category) => category.is_active).map((category) => ({
    name: category.name,
    value: category.key,
    label: category.label,
  }))
)

const userTypeFilterOptions = [
  { name: '管理員', value: true },
  { name: '一般使用者', value: false },
]

const getCategoryName = (category) => {
  return courseCategories.value.find((item) => item.key === category)?.name || category
}

const getCategorySeverity = (category) => {
  const severityMap = {
    fundamental: 'info',
    required: 'success',
    experience: 'warning',
    optional: 'danger',
    graduate: 'contrast',
    'math-department': 'secondary',
    freshman: 'info',
    sophomore: 'success',
    junior: 'warning',
    senior: 'danger',
    interdisciplinary: 'secondary',
  }
  return severityMap[category] || 'secondary'
}

const categoryOrder = computed(() =>
  courseCategories.value.reduce((acc, category, index) => {
    acc[category.key] = index
    return acc
  }, {})
)

const sortCourses = (courseList) => {
  return [...courseList].sort((a, b) => {
    const categoryDiff = (categoryOrder.value[a.category] ?? 999) - (categoryOrder.value[b.category] ?? 999)
    if (categoryDiff !== 0) return categoryDiff
    const orderDiff = (a.order_index ?? 0) - (b.order_index ?? 0)
    if (orderDiff !== 0) return orderDiff
    return (a.id ?? 0) - (b.id ?? 0)
  })
}

const getNotificationSeverity = (severity) => {
  const map = {
    info: 'info',
    success: 'success',
    warning: 'warning',
    danger: 'danger',
  }
  return map[severity] || 'secondary'
}

const getNotificationSeverityLabel = (severity) => {
  const map = {
    info: '一般',
    success: '成功',
    warning: '提醒',
    danger: '重要',
  }
  return map[severity] || '未知'
}

const isNotificationEffective = (notification) => {
  if (!notification || !notification.is_active) {
    return false
  }

  const now = new Date()

  if (notification.starts_at) {
    const startsAt = new Date(notification.starts_at)
    if (!Number.isNaN(startsAt.getTime()) && startsAt > now) {
      return false
    }
  }

  if (notification.ends_at) {
    const endsAt = new Date(notification.ends_at)
    if (!Number.isNaN(endsAt.getTime()) && endsAt < now) {
      return false
    }
  }

  return true
}

const formatNotificationDate = (value) => {
  return formatRelativeTime(value)
}

const getSubmissionLabel = (status) => {
  const labels = {
    pending: '待審核',
    approved: '已通過',
    rejected: '未通過',
    PENDING: '待審核',
    APPROVED: '已通過',
    REJECTED: '未通過',
  }
  return labels[status] || status
}

const getSubmissionSeverity = (status) => {
  const normalized = String(status || '').toLowerCase()
  if (normalized === 'approved') return 'success'
  if (normalized === 'rejected') return 'danger'
  return 'warning'
}

const getArchiveSubmissionKind = (item) => {
  if (item?.requested_category_key) return '新分類 + 新課程'
  if (item?.requested_course_name) return '新課程'
  return '既有課程'
}

const getArchiveSubmissionKindSeverity = (item) => {
  if (item?.requested_category_key) return 'warning'
  if (item?.requested_course_name) return 'info'
  return 'secondary'
}

const formatAcademicTerm = (value) => {
  const numericValue = Number(value)
  if (!numericValue) return ''
  if (numericValue >= 1000 && numericValue < 2000) {
    const year = Math.floor(numericValue / 10)
    const semester = numericValue % 10
    return `${year}${semester === 1 ? '上' : '下'}學期`
  }
  return `${numericValue} 年`
}

const resetNotificationForm = () => {
  notificationForm.value = {
    title: '',
    body: '',
    severity: 'info',
    is_active: true,
    starts_at: null,
    ends_at: null,
  }
  notificationFormErrors.value = {}
  editingNotification.value = null
}

const toDate = (value) => {
  if (!value) return null
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? null : date
}

const filteredCourses = computed(() => {
  let filtered = sortCourses(courses.value)

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter((course) => course.name.toLowerCase().includes(query))
  }

  if (filterCategory.value) {
    filtered = filtered.filter((course) => course.category === filterCategory.value)
  }

  return filtered
})

const getCategoryCourses = (category) => {
  return sortCourses(courses.value.filter((course) => course.category === category))
}

const getCoursePosition = (course) => {
  return getCategoryCourses(course.category).findIndex((item) => item.id === course.id)
}

const canMoveCourse = (course, direction) => {
  const position = getCoursePosition(course)
  if (position < 0) return false
  const categoryCourses = getCategoryCourses(course.category)
  const nextPosition = position + direction
  return nextPosition >= 0 && nextPosition < categoryCourses.length
}

const getCategoryPosition = (category) => {
  return courseCategories.value.findIndex((item) => item.id === category.id)
}

const canMoveCategory = (category, direction) => {
  const position = getCategoryPosition(category)
  const nextPosition = position + direction
  return position >= 0 && nextPosition >= 0 && nextPosition < courseCategories.value.length
}

const moveCategory = async (category, direction) => {
  if (!canMoveCategory(category, direction)) return

  const currentIndex = getCategoryPosition(category)
  const nextIndex = currentIndex + direction
  const reordered = [...courseCategories.value]
  const [movedCategory] = reordered.splice(currentIndex, 1)
  reordered.splice(nextIndex, 0, movedCategory)

  categoryOrderLoading.value = true
  try {
    await courseService.reorderCategories(reordered.map((item) => item.id))
    courseCategories.value = reordered.map((item, index) => ({ ...item, order_index: index }))
    await loadCourses()
  } catch (error) {
    console.error('更新分類順序失敗:', error)
    if (isUnauthorizedError(error)) return
    toast.add({ severity: 'error', summary: '錯誤', detail: '分類順序更新失敗', life: 3000 })
  } finally {
    categoryOrderLoading.value = false
  }
}

const moveCourse = async (course, direction) => {
  if (!canMoveCourse(course, direction)) return

  const categoryCourses = getCategoryCourses(course.category)
  const currentIndex = categoryCourses.findIndex((item) => item.id === course.id)
  const nextIndex = currentIndex + direction
  const reordered = [...categoryCourses]
  const [movedCourse] = reordered.splice(currentIndex, 1)
  reordered.splice(nextIndex, 0, movedCourse)

  courseOrderLoading.value = true
  try {
    await reorderCourses(
      course.category,
      reordered.map((item) => item.id)
    )
    trackEvent(EVENTS.UPDATE_COURSE, {
      action: 'reorder',
      courseName: course.name,
      category: course.category,
    })
    await loadCourses()
  } catch (error) {
    console.error('更新課程順序失敗:', error)
    if (isUnauthorizedError(error)) {
      return
    }
    toast.add({
      severity: 'error',
      summary: '錯誤',
      detail: '課程順序更新失敗',
      life: 3000,
    })
  } finally {
    courseOrderLoading.value = false
  }
}

const filteredUsers = computed(() => {
  let filtered = users.value

  if (userSearchQuery.value) {
    const query = userSearchQuery.value.toLowerCase()
    filtered = filtered.filter(
      (user) => user.name.toLowerCase().includes(query) || user.email.toLowerCase().includes(query)
    )
  }

  if (filterUserType.value !== null) {
    filtered = filtered.filter((user) => user.is_admin === filterUserType.value)
  }

  return filtered
})

const filteredNotifications = computed(() => {
  let filtered = notifications.value

  if (notificationSearchQuery.value) {
    const query = notificationSearchQuery.value.toLowerCase()
    filtered = filtered.filter(
      (notification) =>
        notification.title.toLowerCase().includes(query) ||
        notification.body.toLowerCase().includes(query)
    )
  }

  if (notificationSeverityFilter.value) {
    filtered = filtered.filter(
      (notification) => notification.severity === notificationSeverityFilter.value
    )
  }

  return filtered.map((notification) => {
    const effectiveOrder = isNotificationEffective(notification) ? 1 : 0
    return {
      ...notification,
      effectiveOrder,
    }
  })
})

const loadCategories = async () => {
  try {
    const response = await courseService.listAdminCategories()
    courseCategories.value = Array.isArray(response.data) ? response.data : []
  } catch (error) {
    console.error('載入課程分類失敗:', error)
    if (isUnauthorizedError(error)) return
    toast.add({
      severity: 'error',
      summary: '錯誤',
      detail: '載入課程分類失敗',
      life: 3000,
    })
  }
}

const loadCourses = async () => {
  coursesLoading.value = true
  try {
    const [categoryResponse, courseResponse] = await Promise.all([
      courseService.listAdminCategories(),
      getCourses(),
    ])
    courseCategories.value = Array.isArray(categoryResponse.data) ? categoryResponse.data : []
    const response = courseResponse
    courses.value = response.data
  } catch (error) {
    console.error('載入課程失敗:', error)
    if (isUnauthorizedError(error)) {
      return
    }
    toast.add({
      severity: 'error',
      summary: '錯誤',
      detail: '載入課程失敗',
      life: 3000,
    })
  } finally {
    coursesLoading.value = false
  }
}

const loadUsers = async () => {
  usersLoading.value = true
  try {
    const response = await getUsers()
    users.value = response.data
  } catch (error) {
    console.error('載入使用者失敗:', error)
    if (isUnauthorizedError(error)) {
      return
    }
    toast.add({
      severity: 'error',
      summary: '錯誤',
      detail: '載入使用者失敗',
      life: 3000,
    })
  } finally {
    usersLoading.value = false
  }
}

const loadNotifications = async () => {
  notificationsLoading.value = true
  try {
    const { data } = await notificationService.getAllAdmin()
    notifications.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('載入公告失敗:', error)
    if (isUnauthorizedError(error)) {
      return
    }
    toast.add({
      severity: 'error',
      summary: '錯誤',
      detail: '載入公告失敗',
      life: 3000,
    })
  } finally {
    notificationsLoading.value = false
  }
}

const loadReviewItems = async () => {
  reviewLoading.value = true
  try {
    const [categoryResponse, allCoursesResponse, archiveResponse] = await Promise.all([
      courseService.listAdminCategories(),
      getCourses(),
      archiveService.listAdminSubmissions(),
    ])
    courseCategories.value = Array.isArray(categoryResponse.data) ? categoryResponse.data : []
    courses.value = Array.isArray(allCoursesResponse.data) ? allCoursesResponse.data : []
    archiveRequests.value = Array.isArray(archiveResponse.data) ? archiveResponse.data : []
  } catch (error) {
    console.error('載入審核資料失敗:', error)
    if (isUnauthorizedError(error)) {
      return
    }
    toast.add({
      severity: 'error',
      summary: '錯誤',
      detail: '載入審核資料失敗',
      life: 3000,
    })
  } finally {
    reviewLoading.value = false
  }
}

const openArchiveRequestDialog = async (request) => {
  selectedArchiveRequest.value = request
  archiveRequestEditForm.value = {
    subject: request.subject,
    category: request.category,
    name: request.name,
    academic_year: request.academic_year,
    archive_type: request.archive_type,
    professor: request.professor,
    has_answers: Boolean(request.has_answers),
    requested_course_name: request.requested_course_name || '',
    requested_category_key: request.requested_category_key || '',
    requested_category_name: request.requested_category_name || '',
    requested_category_label: request.requested_category_label || '',
    requested_category_icon: request.requested_category_icon || 'pi pi-fw pi-book',
  }
  showArchiveRequestDialog.value = true
  await loadArchiveComparison(request)
}

const saveArchiveRequestEdit = async () => {
  if (!selectedArchiveRequest.value) return
  reviewEditLoading.value = true
  try {
    const { data } = await archiveService.updateSubmission(
      selectedArchiveRequest.value.id,
      archiveRequestEditForm.value
    )
    selectedArchiveRequest.value = data
    toast.add({ severity: 'success', summary: '成功', detail: '考古題投稿已更新', life: 3000 })
    await loadReviewItems()
    await loadArchiveComparison(data)
  } catch (error) {
    console.error('更新考古題投稿失敗:', error)
    if (isUnauthorizedError(error)) return
    toast.add({ severity: 'error', summary: '錯誤', detail: '考古題投稿更新失敗', life: 3000 })
  } finally {
    reviewEditLoading.value = false
  }
}

const previewArchiveRequestFile = async () => {
  if (!selectedArchiveRequest.value?.id) return
  archiveRequestPreviewLoading.value = true
  archiveRequestPreviewError.value = false
  try {
    if (archiveRequestPreviewUrl.value) {
      URL.revokeObjectURL(archiveRequestPreviewUrl.value)
      archiveRequestPreviewUrl.value = ''
    }
    const { data } = await archiveService.getSubmissionPreviewFile(selectedArchiveRequest.value.id)
    archiveRequestPreviewUrl.value = URL.createObjectURL(
      new Blob([data], { type: 'application/pdf' })
    )
    showArchiveRequestPreview.value = true
  } catch (error) {
    console.error('預覽投稿 PDF 失敗:', error)
    archiveRequestPreviewError.value = true
    if (isUnauthorizedError(error)) return
    toast.add({ severity: 'error', summary: '預覽失敗', detail: '無法載入投稿 PDF', life: 3000 })
  } finally {
    archiveRequestPreviewLoading.value = false
  }
}

const closeArchiveRequestPreview = () => {
  showArchiveRequestPreview.value = false
  archiveRequestPreviewError.value = false
  if (archiveRequestPreviewUrl.value) {
    URL.revokeObjectURL(archiveRequestPreviewUrl.value)
    archiveRequestPreviewUrl.value = ''
  }
}

const handleArchiveRequestPreviewError = () => {
  archiveRequestPreviewError.value = true
}

const revokeComparePreviewUrls = () => {
  if (compareRequestPreviewUrl.value) {
    URL.revokeObjectURL(compareRequestPreviewUrl.value)
    compareRequestPreviewUrl.value = ''
  }
  if (compareArchivePreviewUrl.value) {
    URL.revokeObjectURL(compareArchivePreviewUrl.value)
    compareArchivePreviewUrl.value = ''
  }
}

const openComparePreview = async (archive) => {
  if (!selectedArchiveRequest.value?.id || !archive?.id || !archive?.course_id) return
  comparePreviewArchive.value = archive
  comparePreviewLoading.value = true
  comparePreviewError.value = false
  revokeComparePreviewUrls()
  showComparePreview.value = true

  try {
    const [requestResponse, archiveResponse] = await Promise.all([
      archiveService.getSubmissionPreviewFile(selectedArchiveRequest.value.id),
      archiveService.getArchivePreviewFile(archive.course_id, archive.id),
    ])
    compareRequestPreviewUrl.value = URL.createObjectURL(
      new Blob([requestResponse.data], { type: 'application/pdf' })
    )
    compareArchivePreviewUrl.value = URL.createObjectURL(
      new Blob([archiveResponse.data], { type: 'application/pdf' })
    )
  } catch (error) {
    console.error('載入比對 PDF 失敗:', error)
    comparePreviewError.value = true
    if (isUnauthorizedError(error)) return
    toast.add({ severity: 'error', summary: '預覽失敗', detail: '無法載入比對 PDF', life: 3000 })
  } finally {
    comparePreviewLoading.value = false
  }
}

const closeComparePreview = () => {
  showComparePreview.value = false
  comparePreviewArchive.value = null
  comparePreviewError.value = false
  comparePreviewLoading.value = false
  revokeComparePreviewUrls()
}

const loadArchiveComparison = async (request) => {
  comparisonArchives.value = []
  if (!request?.subject || !request?.category) return

  comparisonLoading.value = true
  try {
    const matchingCourse = courses.value.find(
      (course) => course.name === request.subject && course.category === request.category
    )
    if (!matchingCourse) return

    const { data } = await courseService.getCourseArchives(matchingCourse.id)
    comparisonArchives.value = (Array.isArray(data) ? data : [])
      .filter(
        (archive) =>
          Number(archive.academic_year) === Number(request.academic_year) &&
          archive.archive_type === request.archive_type &&
          archive.name === request.name
      )
      .map((archive) => ({
        ...archive,
        course_id: matchingCourse.id,
      }))
  } catch (error) {
    console.error('載入比對資料失敗:', error)
    if (isUnauthorizedError(error)) return
    toast.add({ severity: 'error', summary: '錯誤', detail: '比對資料載入失敗', life: 3000 })
  } finally {
    comparisonLoading.value = false
  }
}

const getRequesterHistory = (requesterId) => {
  if (!requesterId) return []
  const archiveHistory = archiveRequests.value
    .filter((item) => item.requester_id === requesterId)
    .map((item) => ({
      kind: 'archive',
      id: item.id,
      title: `考古題：${item.subject} / ${item.name}`,
      requester: getRequesterDisplay(item),
      status: item.status,
    }))
  return archiveHistory
}

const getRequesterDisplay = (request) => {
  if (!request) return '未知帳號'
  return request.requester_name || request.requester_email || `使用者 #${request.requester_id}`
}

const reviewArchiveSubmission = async (submissionId, action) => {
  try {
    if (action === 'approve') {
      await archiveService.approveSubmission(submissionId)
    } else {
      await archiveService.rejectSubmission(submissionId)
    }
    toast.add({
      severity: 'success',
      summary: '完成',
      detail: action === 'approve' ? '考古題投稿已通過' : '考古題投稿已退回',
      life: 3000,
    })
    await loadReviewItems()
    showArchiveRequestDialog.value = false
  } catch (error) {
    console.error('審核考古題投稿失敗:', error)
    if (isUnauthorizedError(error)) return
    toast.add({ severity: 'error', summary: '錯誤', detail: '審核考古題投稿失敗', life: 3000 })
  }
}

const confirmDeleteArchiveSubmission = (submission) => {
  if (!submission?.id) return
  confirm.require({
    message: `確定要刪除「${submission.subject} / ${submission.name}」這筆投稿紀錄嗎？`,
    header: '確認刪除投稿紀錄',
    icon: 'pi pi-exclamation-triangle',
    accept: () => deleteArchiveSubmissionAction(submission),
  })
}

const deleteArchiveSubmissionAction = async (submission) => {
  try {
    await archiveService.deleteSubmission(submission.id)
    toast.add({
      severity: 'success',
      summary: '已刪除',
      detail: '投稿紀錄已刪除',
      life: 3000,
    })
    if (selectedArchiveRequest.value?.id === submission.id) {
      showArchiveRequestDialog.value = false
      selectedArchiveRequest.value = null
    }
    await loadReviewItems()
  } catch (error) {
    console.error('刪除考古題投稿失敗:', error)
    if (isUnauthorizedError(error)) return
    toast.add({ severity: 'error', summary: '錯誤', detail: '投稿紀錄刪除失敗', life: 3000 })
  }
}

const openCreateDialog = () => {
  courseForm.value = {
    name: '',
    category: '',
  }
  courseFormErrors.value = {}
  editingCourse.value = null
  showCourseDialog.value = true
  trackEvent(EVENTS.CREATE_COURSE, { action: 'open-dialog' })
}

const openEditDialog = (course) => {
  courseForm.value = {
    name: course.name,
    category: course.category,
  }
  courseFormErrors.value = {}
  editingCourse.value = course
  showCourseDialog.value = true
  trackEvent(EVENTS.UPDATE_COURSE, { action: 'open-dialog', courseName: course.name })
}

const closeCourseDialog = () => {
  showCourseDialog.value = false
  courseForm.value = {
    name: '',
    category: '',
  }
  courseFormErrors.value = {}
  editingCourse.value = null
}

const validateCourseForm = () => {
  const errors = {}

  if (!courseForm.value.name.trim()) {
    errors.name = '課程名稱是必填欄位'
  }

  if (!courseForm.value.category) {
    errors.category = '分類是必填欄位'
  }

  courseFormErrors.value = errors
  return Object.keys(errors).length === 0
}

const saveCourse = async () => {
  if (!validateCourseForm()) return

  saveLoading.value = true
  try {
    if (editingCourse.value) {
      await updateCourse(editingCourse.value.id, courseForm.value)
      trackEvent(EVENTS.UPDATE_COURSE, {
        action: 'submit',
        courseName: courseForm.value.name,
        category: courseForm.value.category,
      })
      toast.add({
        severity: 'success',
        summary: '成功',
        detail: '課程更新成功',
        life: 3000,
      })
    } else {
      await createCourse(courseForm.value)
      trackEvent(EVENTS.CREATE_COURSE, {
        action: 'submit',
        courseName: courseForm.value.name,
        category: courseForm.value.category,
      })
      toast.add({
        severity: 'success',
        summary: '成功',
        detail: '課程新增成功',
        life: 3000,
      })
    }
    closeCourseDialog()
    await loadCourses()
  } catch (error) {
    console.error('儲存課程失敗:', error)
    if (isUnauthorizedError(error)) {
      return
    }
    toast.add({
      severity: 'error',
      summary: '錯誤',
      detail: editingCourse.value ? '課程更新失敗' : '課程新增失敗',
      life: 3000,
    })
  } finally {
    saveLoading.value = false
  }
}

const confirmDeleteCourse = (course) => {
  confirm.require({
    message: `確定要刪除課程「${course.name}」嗎？`,
    header: '刪除確認',
    icon: 'pi pi-exclamation-triangle',
    rejectClass: 'p-button-secondary p-button-outlined',
    acceptClass: 'p-button-danger',
    rejectLabel: '取消',
    acceptLabel: '刪除',
    accept: () => deleteCourseAction(course),
  })
}

const deleteCourseAction = async (course) => {
  try {
    await deleteCourse(course.id)
    trackEvent(EVENTS.DELETE_COURSE, {
      courseName: course.name,
      category: course.category,
    })
    toast.add({
      severity: 'success',
      summary: '成功',
      detail: '課程刪除成功',
      life: 3000,
    })
    await loadCourses()
  } catch (error) {
    console.error('刪除課程失敗:', error)
    if (isUnauthorizedError(error)) {
      return
    }
    toast.add({
      severity: 'error',
      summary: '錯誤',
      detail: '課程刪除失敗',
      life: 3000,
    })
  }
}

const openCreateCategoryDialog = () => {
  categoryForm.value = {
    key: '',
    name: '',
    label: '',
    icon: 'pi pi-fw pi-book',
  }
  categoryFormErrors.value = {}
  editingCategory.value = null
  showCategoryDialog.value = true
}

const openEditCategoryDialog = (category) => {
  categoryForm.value = {
    key: category.key,
    name: category.name,
    label: category.label || '',
    icon: category.icon || 'pi pi-fw pi-book',
  }
  categoryFormErrors.value = {}
  editingCategory.value = category
  showCategoryDialog.value = true
}

const closeCategoryDialog = () => {
  showCategoryDialog.value = false
  editingCategory.value = null
  categoryForm.value = {
    key: '',
    name: '',
    label: '',
    icon: 'pi pi-fw pi-book',
  }
  categoryFormErrors.value = {}
}

const validateCategoryForm = () => {
  const errors = {}
  if (!categoryForm.value.key.trim()) {
    errors.key = '分類 Key 是必填欄位'
  } else if (!/^[a-z0-9-]+$/.test(categoryForm.value.key.trim())) {
    errors.key = '只能使用小寫英文字母、數字與連字號'
  }
  if (!categoryForm.value.name.trim()) {
    errors.name = '顯示名稱是必填欄位'
  }
  categoryFormErrors.value = errors
  return Object.keys(errors).length === 0
}

const saveCategory = async () => {
  if (!validateCategoryForm()) return

  categorySaveLoading.value = true
  try {
    const payload = {
      key: categoryForm.value.key.trim(),
      name: categoryForm.value.name.trim(),
      label: categoryForm.value.label.trim(),
      icon: categoryForm.value.icon.trim() || 'pi pi-fw pi-book',
    }
    if (editingCategory.value) {
      await courseService.updateCategory(editingCategory.value.id, payload)
    } else {
      await courseService.createCategory(payload)
    }
    toast.add({
      severity: 'success',
      summary: '成功',
      detail: editingCategory.value ? '分類更新成功' : '分類新增成功',
      life: 3000,
    })
    closeCategoryDialog()
    await loadCourses()
  } catch (error) {
    console.error('儲存分類失敗:', error)
    if (isUnauthorizedError(error)) return
    toast.add({ severity: 'error', summary: '錯誤', detail: '分類儲存失敗', life: 3000 })
  } finally {
    categorySaveLoading.value = false
  }
}

const confirmToggleCategory = (category) => {
  const nextActive = !category.is_active
  confirm.require({
    message: `確定要${nextActive ? '啟用' : '停用'}分類「${category.name}」嗎？`,
    header: `${nextActive ? '啟用' : '停用'}分類`,
    icon: 'pi pi-exclamation-triangle',
    rejectClass: 'p-button-secondary p-button-outlined',
    acceptClass: nextActive ? 'p-button-success' : 'p-button-warning',
    rejectLabel: '取消',
    acceptLabel: nextActive ? '啟用' : '停用',
    accept: () => toggleCategoryActive(category, nextActive),
  })
}

const toggleCategoryActive = async (category, isActive) => {
  try {
    await courseService.setCategoryActive(category.id, isActive)
    toast.add({
      severity: 'success',
      summary: '成功',
      detail: `分類已${isActive ? '啟用' : '停用'}`,
      life: 3000,
    })
    await loadCourses()
  } catch (error) {
    console.error('更新分類狀態失敗:', error)
    if (isUnauthorizedError(error)) return
    toast.add({
      severity: 'error',
      summary: '錯誤',
      detail: error?.response?.data?.detail || '分類狀態更新失敗',
      life: 3000,
    })
  }
}

const confirmDeleteCategory = (category) => {
  confirm.require({
    message: `確定要永久刪除分類「${category.name}」嗎？只有完全沒有課程或投稿引用的分類才能刪除。`,
    header: '刪除分類',
    icon: 'pi pi-exclamation-triangle',
    rejectClass: 'p-button-secondary p-button-outlined',
    acceptClass: 'p-button-danger',
    rejectLabel: '取消',
    acceptLabel: '刪除',
    accept: () => deleteCategoryAction(category),
  })
}

const deleteCategoryAction = async (category) => {
  try {
    await courseService.deleteCategory(category.id)
    toast.add({ severity: 'success', summary: '成功', detail: '分類已刪除', life: 3000 })
    await loadCourses()
  } catch (error) {
    console.error('刪除分類失敗:', error)
    if (isUnauthorizedError(error)) return
    toast.add({
      severity: 'error',
      summary: '錯誤',
      detail: error?.response?.data?.detail || '分類刪除失敗',
      life: 3000,
    })
  }
}

const openCreateUserDialog = () => {
  userForm.value = {
    name: '',
    email: '',
    password: '',
    is_admin: false,
  }
  userFormErrors.value = {}
  editingUser.value = null
  showUserDialog.value = true
  trackEvent(EVENTS.CREATE_USER, { action: 'open-dialog' })
}

const openEditUserDialog = (user) => {
  userForm.value = {
    name: user.name,
    email: user.email,
    password: '',
    is_admin: user.is_admin,
  }
  userFormErrors.value = {}
  editingUser.value = user
  showUserDialog.value = true
  trackEvent(EVENTS.UPDATE_USER, { action: 'open-dialog', userName: user.name })
}

const closeUserDialog = () => {
  showUserDialog.value = false
  userForm.value = {
    name: '',
    email: '',
    password: '',
    is_admin: false,
  }
  userFormErrors.value = {}
  editingUser.value = null
}

const validateUserForm = () => {
  const errors = {}

  if (!userForm.value.name.trim()) {
    errors.name = '使用者名稱是必填欄位'
  }

  if (!userForm.value.email.trim()) {
    errors.email = '電子郵件是必填欄位'
  } else if (!/\S+@\S+\.\S+/.test(userForm.value.email)) {
    errors.email = '電子郵件格式不正確'
  }

  if (!editingUser.value && !userForm.value.password.trim()) {
    errors.password = '密碼是必填欄位'
  }

  userFormErrors.value = errors
  return Object.keys(errors).length === 0
}

const saveUser = async () => {
  if (!validateUserForm()) return

  userSaveLoading.value = true
  try {
    if (editingUser.value) {
      const updateData = {
        name: userForm.value.name,
        email: userForm.value.email,
        is_admin: userForm.value.is_admin,
      }
      if (userForm.value.password.trim()) {
        updateData.password = userForm.value.password
      }
      await updateUser(editingUser.value.id, updateData)
      trackEvent(EVENTS.UPDATE_USER, {
        action: 'submit',
        userName: userForm.value.name,
        isAdmin: userForm.value.is_admin,
      })
      toast.add({
        severity: 'success',
        summary: '成功',
        detail: '使用者更新成功',
        life: 3000,
      })
    } else {
      await createUser(userForm.value)
      trackEvent(EVENTS.CREATE_USER, {
        action: 'submit',
        userName: userForm.value.name,
        isAdmin: userForm.value.is_admin,
      })
      toast.add({
        severity: 'success',
        summary: '成功',
        detail: '使用者新增成功',
        life: 3000,
      })
    }
    closeUserDialog()
    await loadUsers()
  } catch (error) {
    console.error('儲存使用者失敗:', error)
    if (isUnauthorizedError(error)) {
      return
    }
    toast.add({
      severity: 'error',
      summary: '錯誤',
      detail: editingUser.value ? '使用者更新失敗' : '使用者新增失敗',
      life: 3000,
    })
  } finally {
    userSaveLoading.value = false
  }
}

const confirmDeleteUser = (user) => {
  confirm.require({
    message: `確定要刪除使用者「${user.name}」嗎？`,
    header: '刪除確認',
    icon: 'pi pi-exclamation-triangle',
    rejectClass: 'p-button-secondary p-button-outlined',
    acceptClass: 'p-button-danger',
    rejectLabel: '取消',
    acceptLabel: '刪除',
    accept: () => deleteUserAction(user),
  })
}

const deleteUserAction = async (user) => {
  try {
    await deleteUser(user.id)
    trackEvent(EVENTS.DELETE_USER, {
      userName: user.name,
      isAdmin: user.is_admin,
    })
    toast.add({
      severity: 'success',
      summary: '成功',
      detail: '使用者刪除成功',
      life: 3000,
    })
    await loadUsers()
  } catch (error) {
    console.error('刪除使用者失敗:', error)
    if (isUnauthorizedError(error)) {
      return
    }
    toast.add({
      severity: 'error',
      summary: '錯誤',
      detail: '使用者刪除失敗',
      life: 3000,
    })
  }
}

const openNotificationCreateDialog = () => {
  resetNotificationForm()
  showNotificationDialog.value = true
  trackEvent(EVENTS.CREATE_NOTIFICATION, { action: 'open-dialog' })
}

const openNotificationEditDialog = (notification) => {
  notificationForm.value = {
    title: notification.title,
    body: notification.body,
    severity: notification.severity,
    is_active: notification.is_active,
    starts_at: toDate(notification.starts_at),
    ends_at: toDate(notification.ends_at),
  }
  notificationFormErrors.value = {}
  editingNotification.value = notification
  showNotificationDialog.value = true
  trackEvent(EVENTS.UPDATE_NOTIFICATION, {
    action: 'open-dialog',
    notificationId: notification.id,
  })
}

const closeNotificationDialog = () => {
  showNotificationDialog.value = false
  resetNotificationForm()
}

const validateNotificationForm = () => {
  const errors = {}

  if (!notificationForm.value.title.trim()) {
    errors.title = '公告標題是必填欄位'
  }

  if (!notificationForm.value.body.trim()) {
    errors.body = '公告內容是必填欄位'
  }

  if (notificationForm.value.starts_at && notificationForm.value.ends_at) {
    if (notificationForm.value.ends_at.getTime() < notificationForm.value.starts_at.getTime()) {
      errors.ends_at = '結束時間需晚於生效時間'
    }
  }

  notificationFormErrors.value = errors
  return Object.keys(errors).length === 0
}

const saveNotification = async () => {
  if (!validateNotificationForm()) {
    return
  }

  notificationSaveLoading.value = true
  const payload = {
    title: notificationForm.value.title.trim(),
    body: notificationForm.value.body.trim(),
    severity: notificationForm.value.severity,
    is_active: notificationForm.value.is_active,
    starts_at: notificationForm.value.starts_at
      ? notificationForm.value.starts_at.toISOString()
      : null,
    ends_at: notificationForm.value.ends_at ? notificationForm.value.ends_at.toISOString() : null,
  }

  try {
    if (editingNotification.value) {
      await notificationService.update(editingNotification.value.id, payload)
      trackEvent(EVENTS.UPDATE_NOTIFICATION, {
        action: 'submit',
        notificationId: editingNotification.value.id,
      })
      toast.add({
        severity: 'success',
        summary: '成功',
        detail: '公告更新成功',
        life: 3000,
      })
    } else {
      await notificationService.create(payload)
      trackEvent(EVENTS.CREATE_NOTIFICATION, { action: 'submit' })
      toast.add({
        severity: 'success',
        summary: '成功',
        detail: '公告新增成功',
        life: 3000,
      })
    }
    closeNotificationDialog()
    await loadNotifications()
  } catch (error) {
    console.error('儲存公告失敗:', error)
    if (isUnauthorizedError(error)) {
      return
    }
    toast.add({
      severity: 'error',
      summary: '錯誤',
      detail: editingNotification.value ? '公告更新失敗' : '公告新增失敗',
      life: 3000,
    })
  } finally {
    notificationSaveLoading.value = false
  }
}

const confirmDeleteNotification = (notification) => {
  confirm.require({
    message: `確定要刪除公告「${notification.title}」嗎？`,
    header: '刪除確認',
    icon: 'pi pi-exclamation-triangle',
    rejectClass: 'p-button-secondary p-button-outlined',
    acceptClass: 'p-button-danger',
    rejectLabel: '取消',
    acceptLabel: '刪除',
    accept: () => deleteNotificationAction(notification),
  })
}

const deleteNotificationAction = async (notification) => {
  try {
    await notificationService.remove(notification.id)
    trackEvent(EVENTS.DELETE_NOTIFICATION, { notificationId: notification.id })
    toast.add({
      severity: 'success',
      summary: '成功',
      detail: '公告刪除成功',
      life: 3000,
    })
    await loadNotifications()
  } catch (error) {
    console.error('刪除公告失敗:', error)
    if (isUnauthorizedError(error)) {
      return
    }
    toast.add({
      severity: 'error',
      summary: '錯誤',
      detail: '公告刪除失敗',
      life: 3000,
    })
  }
}

const formatDateTime = (dateString) => {
  if (!dateString) return '從未登入'
  return formatRelativeTime(dateString)
}

// Persist the current tab in localStorage
const saveTabToStorage = (tabValue) => {
  try {
    setLocalItem(TAB_STORAGE_KEY, tabValue)
  } catch (e) {
    console.error('Failed to save tab to storage:', e)
  }
}

const loadTabData = async (value) => {
  const tab = String(value)
  await loadCategories()

  if (tab === '0') {
    await loadCourses()
    return
  }

  if (tab === '1') {
    await loadUsers()
    return
  }

  if (tab === '2') {
    await loadNotifications()
    return
  }

  if (tab === '3') {
    await loadReviewItems()
  }
}

const handleTabChange = (value) => {
  const tabValue = String(value)
  currentTab.value = tabValue
  saveTabToStorage(tabValue)

  const tabNames = {
    0: 'courses',
    1: 'users',
    2: 'notifications',
    3: 'reviews',
  }

  trackEvent(EVENTS.SWITCH_TAB, {
    tab: tabNames[tabValue] || tabValue,
  })
}

watch(
  currentTab,
  async (value) => {
    await loadTabData(value)
  },
  { immediate: true }
)

onBeforeUnmount(() => {
  closeArchiveRequestPreview()
  closeComparePreview()
})
</script>

<style scoped>
.admin-container {
  background: var(--p-tabs-tabpanel-background);
}

.card {
  background-color: var(--bg-primary);
}

:deep(.p-tabs) {
  background: var(--p-tabs-tabpanel-background);
}

:deep(.p-tabview-header) {
  background: var(--bg-primary);
}

:deep(.p-tabview-content) {
  background: var(--bg-primary);
  padding: 0;
}

:deep(.p-datatable) {
  background: var(--bg-primary);
}

:deep(.p-datatable-thead > tr > th) {
  background: var(--bg-primary);
  border-color: var(--border-color);
}

:deep(.p-datatable-tbody > tr > td) {
  background: var(--bg-primary);
  border-color: var(--border-color);
}

:deep(.p-dialog) {
  background: var(--bg-primary);
}

:deep(.p-dialog-header) {
  background: var(--bg-primary);
  border-color: var(--border-color);
}

:deep(.p-dialog-content) {
  background: var(--bg-primary);
}

.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  margin-top: -0.5rem;
}

.relative {
  position: relative;
}

.search-container {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.review-history {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 0.875rem;
  background: color-mix(in srgb, var(--bg-secondary) 75%, transparent);
}

.review-history-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.5rem 0;
  border-top: 1px solid var(--border-color);
}

.review-history-row:first-of-type {
  border-top: 0;
}

.review-requester {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.review-history-title {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.review-history-title small {
  color: var(--text-secondary);
}

.compare-preview-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 1rem;
  flex: 1;
  min-height: 0;
}

.compare-preview-pane {
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 0;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
  background: var(--bg-secondary);
}

.compare-preview-pane header {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border-color);
}

.compare-preview-pane header span {
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.compare-preview-pane iframe {
  flex: 1;
  width: 100%;
  min-height: 0;
  border: 0;
  background: #52585b;
}

.compare-preview-error {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  min-height: 20rem;
  color: var(--text-secondary);
}

/* Mobile responsive adjustments */
@media (max-width: 768px) {
  :deep(.p-dialog .p-dialog-content) {
    font-size: 0.875rem;
  }

  :deep(.p-dialog .p-dialog-header) {
    font-size: 1rem;
  }

  :deep(.p-dialog label) {
    font-size: 0.875rem;
  }

  :deep(.p-dialog .p-inputtext) {
    font-size: 0.875rem;
  }

  :deep(.p-dialog .p-button) {
    font-size: 0.875rem;
    padding: 0.5rem 0.75rem;
  }

  :deep(.p-dialog .p-dropdown-label),
  :deep(.p-dialog .p-password-input) {
    font-size: 0.875rem;
  }

  :deep(.p-dialog .p-checkbox-label) {
    font-size: 0.875rem;
  }

  /* Table adjustments for mobile */
  :deep(.p-datatable) {
    font-size: 0.875rem;
    overflow-x: auto;
  }

  :deep(.p-datatable-table) {
    min-width: 600px;
    width: 100%;
  }

  :deep(.p-datatable .p-datatable-thead > tr > th),
  :deep(.p-datatable .p-datatable-tbody > tr > td) {
    white-space: nowrap;
  }

  :deep(.p-datatable .p-button) {
    white-space: nowrap;
  }

  :deep(.p-paginator) {
    font-size: 0.875rem;
  }

  .compare-preview-grid {
    grid-template-columns: 1fr;
  }
}

/* Desktop table overflow handling */
@media (min-width: 769px) {
  :deep(.p-datatable) {
    overflow-x: auto;
  }

  :deep(.p-datatable-table) {
    min-width: 800px;
    width: 100%;
  }

  :deep(.p-datatable .p-datatable-thead > tr > th),
  :deep(.p-datatable .p-datatable-tbody > tr > td) {
    white-space: nowrap;
  }

  :deep(.p-datatable .p-button) {
    white-space: nowrap;
  }

  /* Ensure buttons don't wrap on desktop */
  :deep(.p-datatable .flex.gap-2) {
    flex-wrap: nowrap;
    gap: 0.5rem;
  }
}
</style>
