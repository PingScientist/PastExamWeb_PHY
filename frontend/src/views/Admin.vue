<template>
  <div class="h-full px-2 md:px-4 admin-container">
    <div class="card h-full flex flex-col">
      <Tabs :value="currentTab" class="flex-1" @update:value="handleTabChange">
        <TabList>
          <Tab value="3">審核中心</Tab>
          <Tab value="0">課程管理</Tab>
          <Tab value="2">公告管理</Tab>
          <Tab value="1">使用者管理</Tab>
          <Tab value="4">垃圾桶</Tab>
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
                <DataTable
                  :value="courseCategories"
                  class="admin-data-table admin-desktop-data-table category-management-table"
                  tableStyle="min-width: 44rem"
                  responsiveLayout="stack"
                  breakpoint="768px"
                >
                  <Column header="順序" style="width: 12rem">
                    <template #body="{ data }">
                      <div class="mobile-card-order flex align-items-center gap-2">
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
                <Column field="name" header="分類名稱">
                  <template #body="{ data }">
                    <span class="category-name-desktop">{{ data.name }}</span>
                    <span class="category-name-mobile">
                      <span class="category-mobile-header">
                        <span class="category-mobile-title">{{ data.name }}</span>
                        <span class="category-key-mobile">
                          <span class="mobile-field-label">系統識別碼</span>
                          <span class="mobile-field-value">{{ data.key }}</span>
                        </span>
                      </span>
                    </span>
                  </template>
                </Column>
                  <Column field="label" header="科目標籤">
                    <template #body="{ data }">
                      <Tag severity="secondary">{{ data.label || data.name }}</Tag>
                    </template>
                  </Column>
                  <Column field="key" header="Key">
                    <template #body="{ data }">
                      <span class="category-key-desktop">{{ data.key }}</span>
                    </template>
                  </Column>
                  <Column field="is_active" header="狀態" style="width: 8rem">
                    <template #body="{ data }">
                      <Tag :severity="data.is_active ? 'success' : 'secondary'">
                        {{ data.is_active ? '啟用中' : '已停用' }}
                      </Tag>
                    </template>
                  </Column>
                  <Column header="操作" style="width: 20rem">
                    <template #body="{ data }">
                      <div class="admin-card-actions">
                        <Button icon="pi pi-pencil" label="編輯" aria-label="編輯分類" title="編輯分類" size="small" outlined @click="openEditCategoryDialog(data)" />
                        <Button
                          :icon="data.is_active ? 'pi pi-eye-slash' : 'pi pi-check'"
                          :label="data.is_active ? '停用' : '啟用'"
                          :aria-label="data.is_active ? '停用分類' : '啟用分類'"
                          :title="data.is_active ? '停用分類' : '啟用分類'"
                          size="small"
                          :severity="data.is_active ? 'warn' : 'success'"
                          outlined
                          @click="confirmToggleCategory(data)"
                        />
                        <Button
                          icon="pi pi-trash"
                          label="刪除"
                          aria-label="刪除分類"
                          title="刪除分類"
                          size="small"
                          severity="danger"
                          outlined
                          @click="confirmDeleteCategory(data)"
                        />
                      </div>
                    </template>
                  </Column>
                </DataTable>
                <div class="admin-mobile-list admin-mobile-list--categories">
                  <article
                    v-for="category in courseCategories"
                    :key="category.id"
                    class="admin-mobile-card admin-category-card"
                  >
                    <section class="category-card-topline">
                      <span class="category-card-order">{{ getCategoryPosition(category) + 1 }}</span>
                      <Button
                        icon="pi pi-arrow-up"
                        severity="secondary"
                        text
                        rounded
                        size="small"
                        aria-label="上移"
                        title="上移"
                        :disabled="!canMoveCategory(category, -1) || categoryOrderLoading"
                        @click="moveCategory(category, -1)"
                      />
                      <Button
                        icon="pi pi-arrow-down"
                        severity="secondary"
                        text
                        rounded
                        size="small"
                        aria-label="下移"
                        title="下移"
                        :disabled="!canMoveCategory(category, 1) || categoryOrderLoading"
                        @click="moveCategory(category, 1)"
                      />
                    </section>
                    <section class="category-card-main">
                      <strong class="category-card-title">{{ category.name }}</strong>
                      <span class="category-card-key">
                        <span class="category-card-key-label">系統識別碼</span>
                        <span class="category-card-key-value">{{ category.key }}</span>
                      </span>
                    </section>
                    <section class="category-card-meta">
                      <Tag severity="secondary">{{ category.label || category.name }}</Tag>
                      <Tag :severity="category.is_active ? 'success' : 'secondary'">
                        {{ category.is_active ? '啟用中' : '已停用' }}
                      </Tag>
                    </section>
                    <section class="admin-card-actions admin-mobile-card-actions category-card-actions">
                      <Button
                        icon="pi pi-pencil"
                        label="編輯"
                        aria-label="編輯分類"
                        title="編輯分類"
                        size="small"
                        outlined
                        @click="openEditCategoryDialog(category)"
                      />
                      <Button
                        :icon="category.is_active ? 'pi pi-eye-slash' : 'pi pi-check'"
                        :label="category.is_active ? '停用' : '啟用'"
                        :aria-label="category.is_active ? '停用分類' : '啟用分類'"
                        :title="category.is_active ? '停用分類' : '啟用分類'"
                        size="small"
                        :severity="category.is_active ? 'warn' : 'success'"
                        outlined
                        @click="confirmToggleCategory(category)"
                      />
                      <Button
                        icon="pi pi-trash"
                        label="刪除"
                        aria-label="刪除分類"
                        title="刪除分類"
                        size="small"
                        severity="danger"
                        outlined
                        @click="confirmDeleteCategory(category)"
                      />
                    </section>
                  </article>
                </div>
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
                class="admin-data-table admin-desktop-data-table course-management-table"
                paginator
                :rows="10"
                :rowsPerPageOptions="[5, 10, 15, 25, 50]"
                tableStyle="min-width: 50rem"
                scrollable
                scrollHeight="65vh"
                responsiveLayout="stack"
                breakpoint="768px"
              >
                <Column header="順序" style="width: 18%">
                  <template #body="{ data }">
                    <div class="mobile-card-order flex align-items-center gap-2">
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
                <Column field="name" header="課程名稱" style="width: 32%">
                  <template #body="{ data }">
                    <span class="mobile-primary-text">{{ data.name }}</span>
                  </template>
                </Column>
                <Column field="category" header="分類" style="width: 22%">
                  <template #body="{ data }">
                    <Tag :severity="getCategorySeverity(data.category)" class="text-sm">
                      {{ getCategoryName(data.category) }}
                    </Tag>
                  </template>
                </Column>
                <Column header="操作" style="width: 18%">
                  <template #body="{ data }">
                    <div class="admin-card-actions">
                      <Button
                        icon="pi pi-pencil"
                        severity="warning"
                        size="small"
                        @click="openEditDialog(data)"
                        label="編輯"
                        aria-label="編輯課程"
                        title="編輯課程"
                      />
                      <Button
                        icon="pi pi-trash"
                        severity="danger"
                        size="small"
                        @click="confirmDeleteCourse(data)"
                        label="刪除"
                        aria-label="刪除課程"
                        title="刪除課程"
                      />
                    </div>
                  </template>
                </Column>
              </DataTable>
              <div v-if="!coursesLoading" class="admin-mobile-list admin-mobile-list--courses">
                <article v-for="course in filteredCourses" :key="course.id" class="admin-mobile-card admin-course-card">
                  <section class="course-card-topline">
                    <span class="course-card-order">{{ getCoursePosition(course) + 1 }}</span>
                    <Button
                      icon="pi pi-arrow-up"
                      severity="secondary"
                      text
                      rounded
                      size="small"
                      aria-label="上移"
                      title="上移"
                      :disabled="!canMoveCourse(course, -1) || courseOrderLoading"
                      @click="moveCourse(course, -1)"
                    />
                    <Button
                      icon="pi pi-arrow-down"
                      severity="secondary"
                      text
                      rounded
                      size="small"
                      aria-label="下移"
                      title="下移"
                      :disabled="!canMoveCourse(course, 1) || courseOrderLoading"
                      @click="moveCourse(course, 1)"
                    />
                    <Tag :severity="getCategorySeverity(course.category)" class="course-card-category">
                      {{ getCategoryName(course.category) }}
                    </Tag>
                  </section>
                  <section class="course-card-primary">
                    <strong class="course-card-title">{{ course.name }}</strong>
                  </section>
                  <section class="admin-card-actions admin-mobile-card-actions course-card-actions">
                    <Button
                      icon="pi pi-pencil"
                      severity="warning"
                      size="small"
                      @click="openEditDialog(course)"
                      label="編輯"
                      aria-label="編輯課程"
                      title="編輯課程"
                    />
                    <Button
                      icon="pi pi-trash"
                      severity="danger"
                      size="small"
                      @click="confirmDeleteCourse(course)"
                      label="刪除"
                      aria-label="刪除課程"
                      title="刪除課程"
                    />
                  </section>
                </article>
              </div>
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
                class="admin-data-table admin-desktop-data-table user-management-table"
                paginator
                :rows="10"
                :rowsPerPageOptions="[5, 10, 15, 25, 50]"
                tableStyle="min-width: 50rem"
                scrollable
                scrollHeight="65vh"
                responsiveLayout="stack"
                breakpoint="768px"
                :multiSortMeta="userSortMeta"
                sortMode="multiple"
                removableSort
              >
                <Column header="使用者名稱" sortable style="width: 15%">
                  <template #body="{ data }">
                    <span class="mobile-primary-text admin-desktop-cell">{{ data.name }}</span>
                    <div class="admin-mobile-card admin-user-mobile-card">
                      <div class="admin-card-primary">
                        <strong class="admin-card-title">{{ data.name }}</strong>
                        <span class="admin-card-email">{{ data.email }}</span>
                      </div>
                      <div class="admin-card-meta">
                        <Tag :severity="data.is_admin ? 'success' : 'secondary'" class="text-sm">
                          {{ data.is_admin ? '是' : '否' }}
                        </Tag>
                        <Tag :severity="data.is_local ? 'info' : 'warning'" class="text-sm">
                          {{ data.is_local ? '本地帳號' : '外部帳號' }}
                        </Tag>
                        <span class="admin-card-meta-text">
                          {{ data.last_login ? formatDateTime(data.last_login) : '從未登入' }}
                        </span>
                      </div>
                    </div>
                  </template>
                </Column>
                <Column header="電子郵件" sortable style="width: 20%">
                  <template #body="{ data }">
                    <span class="mobile-long-text admin-desktop-cell">{{ data.email }}</span>
                  </template>
                </Column>
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
                    <div class="admin-card-actions">
                      <Button
                        icon="pi pi-pencil"
                        severity="warning"
                        size="small"
                        @click="openEditUserDialog(data)"
                        label="編輯"
                        aria-label="編輯使用者"
                        title="編輯使用者"
                      />
                      <Button
                        icon="pi pi-trash"
                        severity="danger"
                        size="small"
                        @click="confirmDeleteUser(data)"
                        label="刪除"
                        aria-label="刪除使用者"
                        title="刪除使用者"
                        :disabled="data.id === currentUserId"
                      />
                    </div>
                  </template>
                </Column>
              </DataTable>
              <div v-if="!usersLoading" class="admin-mobile-list admin-mobile-list--users">
                <article v-for="user in filteredUsers" :key="user.id" class="admin-mobile-card admin-user-card">
                  <section class="admin-card-primary">
                    <strong class="admin-card-title">{{ user.name }}</strong>
                    <span class="admin-card-email">{{ user.email }}</span>
                  </section>
                  <section class="admin-card-meta">
                    <Tag :severity="user.is_admin ? 'success' : 'secondary'" class="text-sm">
                      {{ user.is_admin ? '是' : '否' }}
                    </Tag>
                    <Tag :severity="user.is_local ? 'info' : 'warning'" class="text-sm">
                      {{ user.is_local ? '本地帳號' : '外部帳號' }}
                    </Tag>
                    <span class="admin-card-meta-text">
                      {{ user.last_login ? formatDateTime(user.last_login) : '從未登入' }}
                    </span>
                  </section>
                  <section class="admin-card-actions admin-mobile-card-actions">
                    <Button
                      icon="pi pi-pencil"
                      severity="warning"
                      size="small"
                      @click="openEditUserDialog(user)"
                      label="編輯"
                      aria-label="編輯使用者"
                      title="編輯使用者"
                    />
                    <Button
                      icon="pi pi-trash"
                      severity="danger"
                      size="small"
                      @click="confirmDeleteUser(user)"
                      label="刪除"
                      aria-label="刪除使用者"
                      title="刪除使用者"
                      :disabled="user.id === currentUserId"
                    />
                  </section>
                </article>
              </div>
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
                class="admin-data-table admin-desktop-data-table notification-management-table"
                paginator
                :rows="10"
                :rowsPerPageOptions="[5, 10, 15, 25, 50]"
                tableStyle="min-width: 50rem"
                scrollable
                scrollHeight="65vh"
                responsiveLayout="stack"
                breakpoint="768px"
                sortMode="multiple"
                :multiSortMeta="notificationSortMeta"
                removableSort
              >
                <Column field="title" header="標題" sortable style="width: 26%">
                  <template #body="{ data }">
                    <span class="mobile-primary-text admin-desktop-cell">{{ data.title }}</span>
                    <div class="admin-mobile-card admin-announcement-mobile-card">
                      <div class="admin-card-primary">
                        <strong class="admin-card-title">{{ data.title }}</strong>
                      </div>
                      <div class="admin-card-meta">
                        <Tag :severity="getNotificationSeverity(data.severity)">
                          {{ getNotificationSeverityLabel(data.severity) }}
                        </Tag>
                        <Tag :severity="data.is_active ? 'success' : 'secondary'">
                          {{ data.is_active ? '啟用中' : '已停用' }}
                        </Tag>
                        <Tag :severity="isNotificationEffective(data) ? 'success' : 'secondary'">
                          {{ isNotificationEffective(data) ? '生效中' : '未生效' }}
                        </Tag>
                        <span class="admin-card-meta-text">
                          {{ formatNotificationDate(data.updated_at || data.created_at) }}
                        </span>
                      </div>
                    </div>
                  </template>
                </Column>
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
                    <div class="admin-card-actions">
                      <Button
                        icon="pi pi-pencil"
                        severity="warning"
                        size="small"
                        @click="openNotificationEditDialog(data)"
                        label="編輯"
                        aria-label="編輯公告"
                        title="編輯公告"
                      />
                      <Button
                        icon="pi pi-trash"
                        severity="danger"
                        size="small"
                        @click="confirmDeleteNotification(data)"
                        label="刪除"
                        aria-label="刪除公告"
                        title="刪除公告"
                      />
                    </div>
                  </template>
                </Column>
              </DataTable>
              <div v-if="!notificationsLoading" class="admin-mobile-list admin-mobile-list--notifications">
                <article
                  v-for="notification in filteredNotifications"
                  :key="notification.id"
                  class="admin-mobile-card admin-announcement-card"
                >
                  <section class="admin-card-primary">
                    <strong class="admin-card-title">{{ notification.title }}</strong>
                  </section>
                  <section class="admin-card-meta">
                    <Tag :severity="getNotificationSeverity(notification.severity)">
                      {{ getNotificationSeverityLabel(notification.severity) }}
                    </Tag>
                    <Tag :severity="notification.is_active ? 'success' : 'secondary'">
                      {{ notification.is_active ? '啟用中' : '已停用' }}
                    </Tag>
                    <Tag :severity="isNotificationEffective(notification) ? 'success' : 'secondary'">
                      {{ isNotificationEffective(notification) ? '生效中' : '未生效' }}
                    </Tag>
                    <span class="admin-card-meta-text">
                      {{ formatNotificationDate(notification.updated_at || notification.created_at) }}
                    </span>
                  </section>
                  <section class="admin-card-actions admin-mobile-card-actions">
                    <Button
                      icon="pi pi-pencil"
                      severity="warning"
                      size="small"
                      @click="openNotificationEditDialog(notification)"
                      label="編輯"
                      aria-label="編輯公告"
                      title="編輯公告"
                    />
                    <Button
                      icon="pi pi-trash"
                      severity="danger"
                      size="small"
                      @click="confirmDeleteNotification(notification)"
                      label="刪除"
                      aria-label="刪除公告"
                      title="刪除公告"
                    />
                  </section>
                </article>
              </div>
            </div>
          </TabPanel>

          <TabPanel value="3">
            <div class="p-2 md:p-4 review-center">
              <div v-if="reviewLoadError" class="review-load-error">
                {{ reviewLoadError }}
              </div>
              <div class="review-search-toolbar">
                <div class="relative w-full md:w-24rem">
                  <i class="pi pi-search search-icon"></i>
                  <InputText
                    v-model="reviewSearchQuery"
                    placeholder="搜尋投稿編號、標題、課程、投稿者…"
                    class="w-full pl-6"
                  />
                </div>
              </div>
              <div class="review-section">
                <div class="review-section-header">
                  <h3>新課程 / 新分類考古申請</h3>
                  <Button icon="pi pi-refresh" label="重新整理" size="small" outlined @click="loadReviewItems" />
                </div>
                <DataTable
                  :value="newCourseArchiveRequests"
                  :loading="reviewLoading"
                  class="admin-data-table review-request-table review-request-table--new"
                  tableStyle="min-width: 60rem"
                  responsiveLayout="stack"
                  breakpoint="768px"
                >
                  <template #empty>
                    <div class="review-empty-state">沒有符合搜尋條件的投稿。</div>
                  </template>
                  <Column field="subject">
                    <template #header>
                      <button type="button" class="review-sort-header" @click="toggleReviewSort('new', 'subject')">
                        課程
                        <i :class="getReviewSortHeaderIcon('new', 'subject')" aria-hidden="true"></i>
                      </button>
                    </template>
                    <template #body="{ data }">
                      <span class="mobile-primary-text review-card-title review-course-cell">
                        <span>{{ data.subject }}</span>
                        <Tag v-if="data.is_admin_upload" class="review-admin-upload-chip" severity="info">
                          管理員投稿
                        </Tag>
                      </span>
                    </template>
                  </Column>
                  <Column>
                    <template #header>
                      <button type="button" class="review-sort-header" @click="toggleReviewSort('new', 'kind')">
                        投稿類型
                        <i :class="getReviewSortHeaderIcon('new', 'kind')" aria-hidden="true"></i>
                      </button>
                    </template>
                    <template #body="{ data }">
                      <Tag class="review-card-chip" :severity="getArchiveSubmissionKindSeverity(data)">
                        {{ getArchiveSubmissionKind(data) }}
                      </Tag>
                    </template>
                  </Column>
                  <Column field="name">
                    <template #header>
                      <button type="button" class="review-sort-header" @click="toggleReviewSort('new', 'name')">
                        考試名稱
                        <i :class="getReviewSortHeaderIcon('new', 'name')" aria-hidden="true"></i>
                      </button>
                    </template>
                    <template #body="{ data }">
                      <span class="mobile-metadata-text review-card-meta-text">{{ data.name }}</span>
                      <small class="text-xs text-500">投稿編號：{{ formatSubmissionLabel(data) }}</small>
                    </template>
                  </Column>
                  <Column field="professor">
                    <template #header>
                      <button type="button" class="review-sort-header" @click="toggleReviewSort('new', 'professor')">
                        授課教師
                        <i :class="getReviewSortHeaderIcon('new', 'professor')" aria-hidden="true"></i>
                      </button>
                    </template>
                    <template #body="{ data }">
                      <span class="mobile-metadata-text review-card-meta-text">{{ data.professor }}</span>
                    </template>
                  </Column>
                  <Column field="academic_year">
                    <template #header>
                      <button type="button" class="review-sort-header" @click="toggleReviewSort('new', 'academic_year')">
                        學期
                        <i :class="getReviewSortHeaderIcon('new', 'academic_year')" aria-hidden="true"></i>
                      </button>
                    </template>
                    <template #body="{ data }">
                      <span class="review-card-meta-text">{{ formatAcademicTerm(data.academic_year) }}</span>
                    </template>
                  </Column>
                  <Column>
                    <template #header>
                      <button type="button" class="review-sort-header" @click="toggleReviewSort('new', 'submitted_at')">
                        申請時間
                        <i :class="getReviewSortHeaderIcon('new', 'submitted_at')" aria-hidden="true"></i>
                      </button>
                    </template>
                    <template #body="{ data }">
                      <span class="review-card-meta-text">{{ formatReviewSubmissionTime(data) }}</span>
                    </template>
                  </Column>
                  <Column field="status">
                    <template #header>
                      <button type="button" class="review-sort-header" @click="toggleReviewSort('new', 'status')">
                        狀態
                        <i :class="getReviewSortHeaderIcon('new', 'status')" aria-hidden="true"></i>
                      </button>
                    </template>
                    <template #body="{ data }">
                      <Tag
                        :class="['review-card-chip', 'review-status-chip', getSubmissionStatusClass(data.status)]"
                        :severity="getSubmissionSeverity(data.status)"
                      >
                        {{ getSubmissionLabel(data.status) }}
                      </Tag>
                    </template>
                  </Column>
                  <Column header="操作">
                    <template #body="{ data }">
                      <div class="admin-card-actions review-card-actions">
                        <Button
                          label="查看/編輯"
                          icon="pi pi-search"
                          aria-label="查看/編輯"
                          title="查看/編輯"
                          size="small"
                          severity="secondary"
                          outlined
                          @click="openArchiveRequestDialog(data)"
                        />
                        <Button
                          v-for="action in getReviewRowActions(data)"
                          :key="action.key"
                          :label="action.label"
                          :icon="action.icon"
                          :aria-label="action.label"
                          :title="action.label"
                          size="small"
                          :severity="action.severity"
                          :outlined="action.outlined"
                          :text="action.text"
                          @click="runReviewRowAction(data, action.key)"
                        />
                        <small v-if="getReviewTrashNote(data)" class="review-card-action-note">
                          {{ getReviewTrashNote(data) }}
                        </small>
                      </div>
                    </template>
                  </Column>
                </DataTable>
              </div>

              <div class="review-section mt-5">
                <div class="review-section-header">
                  <h3>既有課程考古申請</h3>
                </div>
                <DataTable
                  :value="existingCourseArchiveRequests"
                  :loading="reviewLoading"
                  class="admin-data-table review-request-table"
                  tableStyle="min-width: 60rem"
                  responsiveLayout="stack"
                  breakpoint="768px"
                >
                  <template #empty>
                    <div class="review-empty-state">沒有符合搜尋條件的投稿。</div>
                  </template>
                  <Column field="subject">
                    <template #header>
                      <button type="button" class="review-sort-header" @click="toggleReviewSort('existing', 'subject')">
                        課程
                        <i :class="getReviewSortHeaderIcon('existing', 'subject')" aria-hidden="true"></i>
                      </button>
                    </template>
                    <template #body="{ data }">
                      <span class="mobile-primary-text review-card-title review-course-cell">
                        <span>{{ data.subject }}</span>
                        <Tag v-if="data.is_admin_upload" class="review-admin-upload-chip" severity="info">
                          管理員投稿
                        </Tag>
                      </span>
                    </template>
                  </Column>
                  <Column field="name">
                    <template #header>
                      <button type="button" class="review-sort-header" @click="toggleReviewSort('existing', 'name')">
                        考試名稱
                        <i :class="getReviewSortHeaderIcon('existing', 'name')" aria-hidden="true"></i>
                      </button>
                    </template>
                    <template #body="{ data }">
                      <span class="mobile-metadata-text review-card-meta-text">{{ data.name }}</span>
                      <small class="text-xs text-500">投稿編號：{{ formatSubmissionLabel(data) }}</small>
                    </template>
                  </Column>
                  <Column field="professor">
                    <template #header>
                      <button type="button" class="review-sort-header" @click="toggleReviewSort('existing', 'professor')">
                        授課教師
                        <i :class="getReviewSortHeaderIcon('existing', 'professor')" aria-hidden="true"></i>
                      </button>
                    </template>
                    <template #body="{ data }">
                      <span class="mobile-metadata-text review-card-meta-text">{{ data.professor }}</span>
                    </template>
                  </Column>
                  <Column field="academic_year">
                    <template #header>
                      <button type="button" class="review-sort-header" @click="toggleReviewSort('existing', 'academic_year')">
                        學期
                        <i :class="getReviewSortHeaderIcon('existing', 'academic_year')" aria-hidden="true"></i>
                      </button>
                    </template>
                    <template #body="{ data }">
                      <span class="review-card-meta-text">{{ formatAcademicTerm(data.academic_year) }}</span>
                    </template>
                  </Column>
                  <Column>
                    <template #header>
                      <button type="button" class="review-sort-header" @click="toggleReviewSort('existing', 'submitted_at')">
                        投稿時間
                        <i :class="getReviewSortHeaderIcon('existing', 'submitted_at')" aria-hidden="true"></i>
                      </button>
                    </template>
                    <template #body="{ data }">
                      <span class="review-card-meta-text">{{ formatReviewSubmissionTime(data) }}</span>
                    </template>
                  </Column>
                  <Column field="status">
                    <template #header>
                      <button type="button" class="review-sort-header" @click="toggleReviewSort('existing', 'status')">
                        狀態
                        <i :class="getReviewSortHeaderIcon('existing', 'status')" aria-hidden="true"></i>
                      </button>
                    </template>
                    <template #body="{ data }">
                      <Tag
                        :class="['review-card-chip', 'review-status-chip', getSubmissionStatusClass(data.status)]"
                        :severity="getSubmissionSeverity(data.status)"
                      >
                        {{ getSubmissionLabel(data.status) }}
                      </Tag>
                    </template>
                  </Column>
                  <Column header="操作">
                    <template #body="{ data }">
                      <div class="admin-card-actions review-card-actions">
                        <Button
                          label="查看/編輯"
                          icon="pi pi-search"
                          aria-label="查看/編輯"
                          title="查看/編輯"
                          size="small"
                          severity="secondary"
                          outlined
                          @click="openArchiveRequestDialog(data)"
                        />
                        <Button
                          v-for="action in getReviewRowActions(data)"
                          :key="action.key"
                          :label="action.label"
                          :icon="action.icon"
                          :aria-label="action.label"
                          :title="action.label"
                          size="small"
                          :severity="action.severity"
                          :outlined="action.outlined"
                          :text="action.text"
                          @click="runReviewRowAction(data, action.key)"
                        />
                        <small v-if="getReviewTrashNote(data)" class="review-card-action-note">
                          {{ getReviewTrashNote(data) }}
                        </small>
                      </div>
                    </template>
                  </Column>
                </DataTable>
              </div>
            </div>
          </TabPanel>

          <TabPanel value="4">
            <div class="p-2 md:p-4 trash-center">
              <div class="flex flex-column md:flex-row justify-content-between align-items-start md:align-items-center gap-3 mb-4">
                <div>
                  <h3 class="m-0">垃圾桶</h3>
                  <p class="m-0 text-sm text-500">還原或永久刪除管理中心已刪除項目</p>
                </div>
                <div class="flex flex-column md:flex-row gap-2 w-full md:w-auto">
                  <Select
                    v-model="trashFilterType"
                    :options="trashFilterOptions"
                    optionLabel="label"
                    optionValue="value"
                    class="w-full md:w-12rem"
                    @change="loadTrashItems"
                  />
                  <Button icon="pi pi-refresh" label="重新整理" outlined @click="loadTrashItems" />
                  <Button
                    icon="pi pi-sitemap"
                    :label="getTrashRelationButtonLabel()"
                    outlined
                    :disabled="!isTrashRelationHierarchyFilterOnly"
                    :severity="isTrashRelationHierarchyEnabled ? 'primary' : 'secondary'"
                    :title="isTrashRelationHierarchyFilterOnly ? '' : '相關性顯示僅適用於「全部」篩選。'"
                    @click="toggleTrashRelationHierarchy"
                  />
                  <Button
                    icon="pi pi-info-circle"
                    label="依賴與阻擋說明"
                    outlined
                    aria-label="依賴與阻擋說明"
                    title="依賴與阻擋說明"
                    @click="showTrashDependencyHelpDialog = true"
                  />
                  <Button
                    icon="pi pi-times-circle"
                    label="清空目前範圍"
                    severity="danger"
                    outlined
                    :disabled="!trashItems.length || trashLoading"
                    @click="confirmBulkDeleteTrash"
                  />
                </div>
              </div>

              <DataTable
                :value="sortedTrashItems"
                :loading="trashLoading"
                class="admin-data-table trash-table"
                tableStyle="min-width: 72rem"
                responsiveLayout="stack"
                breakpoint="768px"
              >
                <Column field="deleted_at">
                  <template #header>
                    <button type="button" class="review-sort-header" @click="toggleTrashSort('deleted_at')">
                      刪除時間
                      <i :class="getTrashSortHeaderIcon('deleted_at')" aria-hidden="true"></i>
                    </button>
                  </template>
                  <template #body="{ data }">
                    <span>{{ formatTrashDeletedAt(data.deleted_at) }}</span>
                  </template>
                </Column>
                <Column field="item_type">
                  <template #header>
                    <button type="button" class="review-sort-header" @click="toggleTrashSort('type')">
                      類型
                      <i :class="getTrashSortHeaderIcon('type')" aria-hidden="true"></i>
                    </button>
                  </template>
                  <template #body="{ data }">
                    <Tag severity="secondary">{{ getTrashTypeLabel(data.item_type) }}</Tag>
                  </template>
                </Column>
                <Column field="display_name">
                  <template #header>
                    <button type="button" class="review-sort-header" @click="toggleTrashSort('name')">
                      名稱
                      <i :class="getTrashSortHeaderIcon('name')" aria-hidden="true"></i>
                    </button>
                  </template>
                  <template #body="{ data }">
                    <span class="trash-name-cell">
                    <strong
                      class="trash-name-title"
                      :style="{ paddingLeft: `${isTrashRelationHierarchyEnabled ? getTrashNameIndent(data) : 0}rem` }"
                    >
                        <span
                          v-if="isTrashRelationHierarchyEnabled && (data?.trash_depth || 0) > 0"
                          class="trash-tree-prefix"
                          aria-hidden="true"
                        >
                          {{ getTrashTreePrefix(data) }}
                        </span>
                        {{ data.display_name }}
                      </strong>
                      <small v-if="getTrashSubmissionLabel(data)">{{ getTrashSubmissionLabel(data) }}</small>
                      <small v-if="getTrashSemesterText(data)">{{ getTrashSemesterText(data) }}</small>
                      <small v-if="getTrashContextLine(data)" class="text-secondary">
                        {{ getTrashContextLine(data) }}
                      </small>
                    </span>
                  </template>
                </Column>
                <Column field="status">
                  <template #header>
                    <button type="button" class="review-sort-header" @click="toggleTrashSort('status')">
                      狀態
                      <i :class="getTrashSortHeaderIcon('status')" aria-hidden="true"></i>
                    </button>
                  </template>
                  <template #body="{ data }">
                    <Tag :severity="getTrashStatusSeverity(data.status)">
                      {{ getTrashStatusLabel(data.status) }}
                    </Tag>
                  </template>
                </Column>
                <Column field="deleted_by_name">
                  <template #header>
                    <button type="button" class="review-sort-header" @click="toggleTrashSort('deleted_by')">
                      刪除者
                      <i :class="getTrashSortHeaderIcon('deleted_by')" aria-hidden="true"></i>
                    </button>
                  </template>
                  <template #body="{ data }">
                    <span>{{ getTrashDeletedByLabel(data) }}</span>
                  </template>
                </Column>
                <Column header="依賴與阻擋">
                  <template #body="{ data }">
                    <div class="trash-dependencies">
                      <Tag
                        v-for="dependency in getTrashDependencies(data)"
                        :key="dependency.key"
                        :severity="getTrashDependencySeverity(dependency)"
                      >
                        {{ dependency.label }}
                      </Tag>
                      <span v-if="!getTrashDependencies(data).length" class="text-sm text-500">無阻擋</span>
                    </div>
                  </template>
                </Column>
                <Column header="操作">
                  <template #body="{ data }">
                    <div class="admin-card-actions">
                      <Button
                        icon="pi pi-undo"
                        label="還原"
                        size="small"
                        severity="success"
                        outlined
                        @click="confirmRestoreTrashItem(data)"
                      />
                      <Button
                        icon="pi pi-trash"
                        label="永久刪除"
                        size="small"
                        severity="danger"
                        text
                        @click="confirmPermanentDeleteTrashItem(data)"
                      />
                    </div>
                  </template>
                </Column>
              </DataTable>
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
          <small class="text-500">{{ formatSubmissionLabel(selectedArchiveRequest) }}</small>
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
          <DataTable
            v-else
            :value="comparisonArchives"
            tableStyle="min-width: 36rem"
            responsiveLayout="stack"
            breakpoint="768px"
          >
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
              <small>投稿編號：{{ formatSubmissionLabel(item) }}</small>
              <small>投稿：{{ item.requester }}</small>
            </span>
            <Tag
              :class="['review-status-chip', getSubmissionStatusClass(item.status)]"
              :severity="getSubmissionSeverity(item.status)"
            >
              {{ getSubmissionLabel(item.status) }}
            </Tag>
          </div>
        </div>

        <div class="flex justify-end gap-2 mt-4 review-dialog-actions">
          <Button
            class="review-close-action"
            label="關閉"
            icon="pi pi-times"
            aria-label="關閉"
            severity="secondary"
            outlined
            @click="showArchiveRequestDialog = false"
          />
          <Button
            label="預覽 PDF"
            icon="pi pi-eye"
            aria-label="預覽 PDF"
            severity="secondary"
            outlined
            :loading="archiveRequestPreviewLoading"
            @click="previewArchiveRequestFile"
          />
          <Button
            label="儲存修改"
            icon="pi pi-save"
            aria-label="儲存修改"
            :disabled="!canEditSelectedArchiveRequest"
            :loading="reviewEditLoading"
            @click="saveArchiveRequestEdit"
          />
          <Button
            v-for="action in getReviewRowActions(selectedArchiveRequest)"
            :key="action.key"
            :label="action.label"
            :icon="action.icon"
            :aria-label="action.label"
            :severity="action.severity"
            :outlined="action.outlined"
            :text="action.text"
            :disabled="!selectedArchiveRequest"
            @click="runReviewRowAction(selectedArchiveRequest, action.key)"
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

      <Dialog
        v-model:visible="showTrashDependencyHelpDialog"
        :modal="true"
        :draggable="false"
        :closeOnEscape="true"
        header="如何閱讀「依賴與阻擋」"
        :style="{ width: '40rem', maxWidth: '92vw' }"
      >
        <div class="trash-dependency-help">
          <p class="trash-dependency-help-intro">
            這一欄位用來快速判斷資料是否可刪除、是否可復原，以及刪除時會不會帶走關聯資料。
          </p>

          <section class="trash-dependency-help-section">
            <h4 class="trash-dependency-help-title">常見標籤</h4>
            <ul class="trash-dependency-help-list">
              <li><strong>無阻擋</strong>：目前沒有會影響永久刪除或復原的啟用中依賴。</li>
              <li><strong>無法永久刪除</strong>：仍有啟用中資料連到此項目，需先處理後再刪除。</li>
              <li><strong>一併永久刪除</strong>：已在垃圾桶中的子項會跟著刪除。</li>
              <li><strong>關聯</strong>：與其他資料有關係，通常不一定阻擋。</li>
            </ul>
          </section>

          <section class="trash-dependency-help-section">
            <h4 class="trash-dependency-help-title">縮排判斷</h4>
            <p class="trash-dependency-help-note">在「全部」篩選中，縮排代表垃圾桶中的父子關係。</p>
            <ul class="trash-dependency-help-list">
              <li>刪除父項時，標示為一併永久刪除的子項也會被一起刪除。</li>
            </ul>
            <p class="trash-dependency-help-rule">課程 → 考古題</p>
            <p class="trash-dependency-help-rule">考古題投稿 → 考古題</p>
            <p class="trash-dependency-help-rule">課程分類 → 課程 → 考古題</p>
          </section>

          <section class="trash-dependency-help-section">
            <h4 class="trash-dependency-help-title">考古題與投稿</h4>
            <ul class="trash-dependency-help-list">
              <li>考古題投稿通過後可能建立正式考古題，兩者會互相關聯。</li>
              <li>刪除投稿：投稿進垃圾桶，關聯考古題會列在投稿底下。</li>
              <li>刪除考古題：考古題進垃圾桶，相關投稿會暫時下架，但不一定進垃圾桶。</li>
              <li>若投稿仍啟用並連到考古題，考古題可能被阻擋永久刪除。</li>
            </ul>
          </section>

          <section class="trash-dependency-help-section">
            <h4 class="trash-dependency-help-title">課程與考古題</h4>
            <ul class="trash-dependency-help-list">
              <li>刪除課程：課程與下屬考古題會進入垃圾桶。</li>
              <li>相關投稿會暫時下架，並提示先復原原課程。</li>
              <li>復原課程時，系統會嘗試還原相關投稿原始狀態。</li>
            </ul>
          </section>

          <section class="trash-dependency-help-section">
            <h4 class="trash-dependency-help-title">留言</h4>
            <ul class="trash-dependency-help-list">
              <li>留言不再阻擋考古題永久刪除。</li>
              <li>考古題永久刪除時，關聯留言會一併永久刪除。</li>
            </ul>
          </section>

          <section class="trash-dependency-help-section trash-dependency-help-note">
            <h4 class="trash-dependency-help-title">操作建議</h4>
            <ul class="trash-dependency-help-list">
              <li>看到「無法永久刪除」：先處理被提示的啟用中資料。</li>
              <li>看到「一併永久刪除」：確認子項目可一起處理。</li>
              <li>看到「無法復原」：先復原父層，或確認關聯資料已處理。</li>
            </ul>
          </section>
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
const reviewLoadError = ref('')
const reviewSearchQuery = ref('')
const archiveRequests = ref([])
const trashLoading = ref(false)
const trashItems = ref([])
const showTrashRelationHierarchy = ref(false)
const TRASH_FILTER_ALL_VALUE = 'all'
const trashFilterType = ref(TRASH_FILTER_ALL_VALUE)
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
const submissionStatusPriority = {
  pending: 1,
  approved: 2,
  rejected: 3,
  takedown: 4,
  deleted: 5,
}
const trashFilterOptions = [
  { label: '全部', value: TRASH_FILTER_ALL_VALUE },
  { label: '考古題', value: 'archive' },
  { label: '考古題投稿', value: 'archive_submission' },
  { label: '課程分類', value: 'course_category' },
  { label: '課程', value: 'course' },
  { label: '公告', value: 'notification' },
  { label: '使用者', value: 'user' },
]
const trashTypeLabels = trashFilterOptions.reduce((acc, option) => {
  if (option.value) acc[option.value] = option.label
  return acc
}, {})
const getTrashTypeLabel = (itemType) => trashTypeLabels[itemType] || itemType || '未知'
const getReviewSortDirectionIcon = (direction) => (direction === 'asc' ? 'pi pi-sort-up' : 'pi pi-sort-down')
const getReviewSortNeutralIcon = () => 'pi pi-sort'
const getTrashDeletedTimestamp = (item) => {
  const time = new Date(item?.deleted_at || 0).getTime()
  return Number.isNaN(time) ? 0 : time
}
const submissionStatusAliases = {
  pending: 'pending',
  approved: 'approved',
  rejected: 'rejected',
  takedown: 'takedown',
  deleted: 'deleted',
  '待審核': 'pending',
  '已通過': 'approved',
  '未通過': 'rejected',
  '已下架': 'takedown',
  '已刪除': 'deleted',
}
const reviewSortState = ref({
  new: { key: 'status', direction: 'asc' },
  existing: { key: 'status', direction: 'asc' },
})
const trashSortState = ref({
  key: null,
  direction: 'asc',
})
const showTrashDependencyHelpDialog = ref(false)
const normalizeSubmissionStatus = (status) => {
  const raw = String(status || '').trim()
  const normalized = raw.toLowerCase()
  return submissionStatusAliases[normalized] || submissionStatusAliases[raw] || normalized
}
const getReviewItemStatus = (item) => {
  if (item?.deletedAt || item?.deleted_at) return 'deleted'
  return normalizeSubmissionStatus(item?.status)
}
const getReviewItemStatusPriority = (item) => {
  return submissionStatusPriority[getReviewItemStatus(item)] || 99
}
const getReviewSubmissionTimeValue = (item) => {
  const value = item?.submittedAt ?? item?.submitted_at ?? item?.createdAt ?? item?.created_at ?? item?.uploadedAt ?? item?.uploaded_at
  if (!value) return null
  if (typeof value === 'object') {
    return value.raw ?? value.value ?? value.date ?? value.display ?? value.label ?? null
  }
  return value
}
const getReviewTimestamp = (item) => {
  const timeValue = getReviewSubmissionTimeValue(item)
  if (!timeValue) return 0
  const time = new Date(timeValue).getTime()
  return Number.isNaN(time) ? 0 : time
}
const formatReviewSubmissionTime = (item) => {
  const value = getReviewSubmissionTimeValue(item)
  if (!value) return '—'
  if (typeof value === 'object') {
    return value.display || value.label || '—'
  }
  return formatRelativeTime(value)
}
const getReviewSortValue = (item, key) => {
  if (key === 'status') return getReviewItemStatusPriority(item)
  if (key === 'submitted_at') return getReviewTimestamp(item)
  if (key === 'academic_year') return Number(item.academic_year) || null
  if (key === 'kind') return getArchiveSubmissionKind(item)
  return String(item?.[key] || '').trim()
}
const isMissingReviewSortValue = (value, key) => {
  return value === null || value === undefined || value === '' || (key === 'status' && value >= 99)
}
const compareReviewSortValues = (a, b, key, direction) => {
  const aValue = getReviewSortValue(a, key)
  const bValue = getReviewSortValue(b, key)
  const aMissing = isMissingReviewSortValue(aValue, key)
  const bMissing = isMissingReviewSortValue(bValue, key)
  if (aMissing && bMissing) return 0
  if (aMissing) return 1
  if (bMissing) return -1
  const directionFactor = direction === 'desc' ? -1 : 1
  if (typeof aValue === 'number' && typeof bValue === 'number') {
    return (aValue - bValue) * directionFactor
  }
  return String(aValue).localeCompare(String(bValue), 'zh-TW') * directionFactor
}
const sortArchiveReviewItems = (items, section) => {
  const { key, direction } = reviewSortState.value[section]
  return [...items].sort((a, b) => {
    const primaryDiff = compareReviewSortValues(a, b, key, direction)
    if (primaryDiff !== 0) return primaryDiff
    const statusDiff = getReviewItemStatusPriority(a) - getReviewItemStatusPriority(b)
    if (statusDiff !== 0) return statusDiff
    return getReviewTimestamp(b) - getReviewTimestamp(a)
  })
}

const normalizeReviewSearchText = (value) => String(value ?? '').trim().toLowerCase()

const getReviewSearchHaystack = (item) => {
  const fields = [
    item?.id,
    item?.id ? `#${item.id}` : '',
    item?.name,
    item?.subject,
    item?.course_name,
    item?.course_code,
    item?.category,
    item?.requested_course_name,
    item?.requested_category_key,
    item?.requested_category_name,
    item?.requested_category_label,
    item?.requester_name,
    item?.requester_email,
    item?.professor,
    item?.academic_year,
    formatAcademicTerm(item?.academic_year),
    getSubmissionLabel(item?.status),
    getArchiveSubmissionKind(item),
  ]
  return fields.map(normalizeReviewSearchText).filter(Boolean).join(' ')
}

const filteredArchiveRequests = computed(() => {
  const query = normalizeReviewSearchText(reviewSearchQuery.value)
  if (!query) return archiveRequests.value
  return archiveRequests.value.filter((item) => getReviewSearchHaystack(item).includes(query))
})

const toggleReviewSort = (section, key) => {
  const current = reviewSortState.value[section]
  reviewSortState.value = {
    ...reviewSortState.value,
    [section]: {
      key,
      direction: current.key === key && current.direction === 'asc' ? 'desc' : 'asc',
    },
  }
}
const getReviewSortIndicator = (section, key) => {
  const current = reviewSortState.value[section]
  if (current.key !== key) return ''
  return getReviewSortDirectionIcon(current.direction)
}
const getTrashSortIndicator = (key) => {
  if (trashSortState.value.key !== key) return getReviewSortNeutralIcon()
  return getReviewSortDirectionIcon(trashSortState.value.direction)
}
const getReviewSortHeaderIcon = (section, key) => {
  return getReviewSortIndicator(section, key) || getReviewSortNeutralIcon()
}
const getTrashSortHeaderIcon = (key) => {
  return getTrashSortIndicator(key) || getReviewSortNeutralIcon()
}
const isTrashRelationHierarchyFilterOnly = computed(() => trashFilterType.value === TRASH_FILTER_ALL_VALUE)
const isTrashRelationHierarchyEnabled = computed(() => showTrashRelationHierarchy.value && isTrashRelationHierarchyFilterOnly.value)
const toggleTrashRelationHierarchy = () => {
  if (!isTrashRelationHierarchyFilterOnly.value) {
    showTrashRelationHierarchy.value = false
    return
  }
  showTrashRelationHierarchy.value = !showTrashRelationHierarchy.value
  if (showTrashRelationHierarchy.value) {
    trashSortState.value = { key: null, direction: 'asc' }
  }
}
const getTrashRelationButtonLabel = () => (isTrashRelationHierarchyEnabled.value ? '隱藏相關性' : '相關性顯示')
const newCourseArchiveRequests = computed(() =>
  sortArchiveReviewItems(
    filteredArchiveRequests.value.filter((item) => item.requested_course_name || item.requested_category_key),
    'new'
  )
)
const existingCourseArchiveRequests = computed(() =>
  sortArchiveReviewItems(
    filteredArchiveRequests.value.filter((item) => !item.requested_course_name && !item.requested_category_key),
    'existing'
  )
)
const getFilteredTrashRows = () => {
  const filterType = getValidTrashFilterType(trashFilterType.value)
  const rows = Array.isArray(trashItems.value) ? trashItems.value : []
  if (!filterType) {
    return rows
  }
  return rows.filter((item) => item?.item_type === filterType)
}
const getTrashSortValue = (item, key) => {
  if (key === 'deleted_at') return getTrashDeletedTimestamp(item)
  if (key === 'type') return getTrashTypeLabel(item?.item_type)
  if (key === 'name') return String(item?.display_name || '')
  if (key === 'status') return getTrashStatusLabel(item?.status)
  if (key === 'deleted_by') return item?.deleted_by_name || ''
  if (key === 'dependencies') return (getTrashDependencies(item).map((dependency) => dependency.label).join(' '))
  return String(item?.[key] || '')
}
const isMissingTrashSortValue = (value) => value === null || value === undefined || value === ''
const compareTrashSortValues = (a, b) => {
  const { key, direction } = trashSortState.value
  const directionFactor = direction === 'desc' ? -1 : 1
  const aValue = getTrashSortValue(a, key)
  const bValue = getTrashSortValue(b, key)
  const aMissing = isMissingTrashSortValue(aValue)
  const bMissing = isMissingTrashSortValue(bValue)
  if (aMissing && bMissing) return 0
  if (aMissing) return 1
  if (bMissing) return -1
  if (typeof aValue === 'number' && typeof bValue === 'number') {
    return (aValue - bValue) * directionFactor
  }
  return String(aValue).localeCompare(String(bValue), 'zh-TW') * directionFactor
}
const sortTrashItems = (rows) => {
  const sortKey = trashSortState.value.key
  if (!sortKey) {
    return rows
  }
  return [...rows].sort((a, b) => {
    const primaryDiff = compareTrashSortValues(a, b)
    if (primaryDiff !== 0) return primaryDiff
    return getTrashDeletedTimestamp(b) - getTrashDeletedTimestamp(a)
  })
}
const toggleTrashSort = (key) => {
  if (isTrashRelationHierarchyEnabled.value) {
    showTrashRelationHierarchy.value = false
  }
  const current = trashSortState.value
  if (current.key === key) {
    if (current.direction === 'asc') {
      trashSortState.value = { ...current, direction: 'desc' }
      return
    }
    trashSortState.value = { key: null, direction: 'asc' }
    return
  }
  trashSortState.value = {
    key,
    direction: 'asc',
  }
}
const sortedTrashItems = computed(() => {
  const filteredRows = getFilteredTrashRows()
  const sortKey = trashSortState.value.key
  if (isTrashRelationHierarchyEnabled.value) {
    return buildTrashHierarchy(filteredRows, getValidTrashFilterType(trashFilterType.value))
  }
  if (!sortKey) {
    return filteredRows
  }
  return sortTrashItems(filteredRows)
})

watch(
  trashFilterType,
  (nextFilterType) => {
    if (nextFilterType !== TRASH_FILTER_ALL_VALUE) {
      showTrashRelationHierarchy.value = false
    }
  }
)

const getTrashItemKey = (item, fallbackIndex = 0) => {
  const type = item?.item_type || 'unknown'
  if (item?.id === null || item?.id === undefined) {
    return `${type}:tmp:${fallbackIndex}`
  }
  return `${type}:${item.id}`
}

const getTrashParentKey = (item) => {
  if (!item?.parent_type || item?.parent_id === null || item?.parent_id === undefined) return null
  return `${item.parent_type}:${item.parent_id}`
}

const getTrashNameIndent = (item) => Math.max(0, Number(item?.trash_depth || 0)) * 1.65

const getTrashTreePrefix = (item) => {
  const depth = Math.max(0, Number(item?.trash_depth || 0))
  if (!depth) return ''
  return `${'│  '.repeat(Math.max(0, depth - 1))}└─`
}

const getValidTrashFilterType = (value) => {
  const validFilterValues = new Set(trashFilterOptions.map((option) => option.value))
  if (value === TRASH_FILTER_ALL_VALUE) return null
  return validFilterValues.has(value) ? value : null
}

const getTrashFilterApiValue = (value) => getValidTrashFilterType(value)


const buildTrashHierarchy = (items, filterType) => {
  const normalizedFilterType = getValidTrashFilterType(filterType)
  const rowMap = new Map()
  for (const [index, rawItem] of (Array.isArray(items) ? items : []).entries()) {
    if (!rawItem || typeof rawItem !== 'object' || !rawItem.item_type) continue
    const row = {
      ...rawItem,
      _trashRowIndex: index,
      trash_depth: 0,
    }
    const key = getTrashItemKey(row, index)
    const existing = rowMap.get(key)
    if (!existing) {
      rowMap.set(key, row)
      continue
    }
    const dependencies = [...(existing.dependencies || [])]
    for (const dependency of row.dependencies || []) {
      if (!dependencies.includes(dependency)) dependencies.push(dependency)
    }
    rowMap.set(key, {
      ...existing,
      dependencies,
      deleted_at: getTrashDeletedTimestamp(row) > getTrashDeletedTimestamp(existing) ? row.deleted_at : existing.deleted_at,
      deleted_by_id: getTrashDeletedTimestamp(row) > getTrashDeletedTimestamp(existing) ? row.deleted_by_id : existing.deleted_by_id,
      deleted_by_name: getTrashDeletedTimestamp(row) > getTrashDeletedTimestamp(existing) ? row.deleted_by_name : existing.deleted_by_name,
    })
  }
  const rows = [...rowMap.values()]
    .map((item, index) => ({
      ...item,
      _trashRowIndex: item._trashRowIndex ?? index,
      trash_depth: 0,
    }))
    .sort((a, b) => getTrashDeletedTimestamp(b) - getTrashDeletedTimestamp(a))

  if (normalizedFilterType !== null && normalizedFilterType !== undefined) {
    return rows
      .sort((a, b) => getTrashDeletedTimestamp(b) - getTrashDeletedTimestamp(a))
      .map((item) => ({ ...item, trash_depth: 0 }))
  }

  if (!rows.length) return []

  const itemMap = new Map()
  const childrenMap = new Map()
  const roots = []

  for (const row of rows) {
    const key = getTrashItemKey(row, row._trashRowIndex)
    itemMap.set(key, row)
    childrenMap.set(key, [])
  }
  for (const row of rows) {
    const parentKey = getTrashParentKey(row)
    if (parentKey && itemMap.has(parentKey)) {
      childrenMap.get(parentKey)?.push(row)
    } else {
      roots.push(row)
    }
  }

  for (const children of childrenMap.values()) {
    children.sort((a, b) => getTrashDeletedTimestamp(b) - getTrashDeletedTimestamp(a))
  }
  roots.sort((a, b) => getTrashDeletedTimestamp(b) - getTrashDeletedTimestamp(a))

  const visited = new Set()
  const result = []
  const walk = (node, depth) => {
    const key = getTrashItemKey(node, node._trashRowIndex)
    if (visited.has(key)) return
    visited.add(key)

    result.push({ ...node, trash_depth: depth })
    const children = childrenMap.get(key) || []
    for (const child of children) {
      walk(child, depth + 1)
    }
  }
  for (const root of roots) {
    walk(root, 0)
  }

  if (!result.length && rows.length) {
    return rows.map((item) => ({ ...item, trash_depth: 0 }))
  }

  return result
}

const getTrashContextLine = (item) => {
  if (!item) return ''
  if (item.item_type === 'archive' && item.course_name) return `課程：${item.course_name}`
  if (item.item_type === 'course' && item.parent_name) return `隸屬分類：${item.parent_name}`
  if (item.item_type === 'archive_submission') {
    if (item.parent_name) return `關聯考古題：${item.parent_name}`
    if (item.course_name) return `課程：${item.course_name}`
  }
  return ''
}

const TAB_STORAGE_KEY = STORAGE_KEYS.local.ADMIN_CURRENT_TAB

const getInitialTab = () => {
  try {
    const savedTab = getLocalItem(TAB_STORAGE_KEY)
    if (savedTab && ['0', '1', '2', '3', '4'].includes(savedTab)) {
      return savedTab
    }
  } catch (e) {
    console.error('Failed to load tab from storage:', e)
  }
  return '0'
}

const currentTab = ref(getInitialTab())

const categoryOptions = computed(() =>
  courseCategories.value
    .filter((category) => !category.deleted_at)
    .map((category) => ({
    name: category.is_active ? category.name : `${category.name}（已停用）`,
    value: category.key,
    label: category.label,
  }))
)
const categoryInfoMap = computed(() =>
  courseCategories.value.reduce((acc, category) => {
    if (!category.deleted_at) {
      acc[category.key] = category
    }
    return acc
  }, {})
)

const userTypeFilterOptions = [
  { name: '管理員', value: true },
  { name: '一般使用者', value: false },
]

const getCategoryName = (category) => {
  return categoryInfoMap.value[category]?.name || category
}

const getCategoryDisplayLabel = (category) => {
  return categoryInfoMap.value[category]?.label || categoryInfoMap.value[category]?.name || ''
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
    takedown: '已下架',
    deleted: '已刪除',
  }
  return labels[normalizeSubmissionStatus(status)] || '未知狀態'
}

const getSubmissionSeverity = (status) => {
  const normalized = normalizeSubmissionStatus(status)
  if (normalized === 'approved') return 'success'
  if (normalized === 'rejected') return 'danger'
  if (normalized === 'deleted') return 'danger'
  if (normalized === 'takedown') return 'secondary'
  return 'warning'
}

const getSubmissionStatusClass = (status) => {
  const normalized = normalizeSubmissionStatus(status)
  if (normalized === 'approved') return 'review-status-approved'
  if (normalized === 'rejected') return 'review-status-rejected'
  if (normalized === 'takedown') return 'review-status-takedown'
  if (normalized === 'deleted') return 'review-status-deleted'
  return 'review-status-pending'
}

const reviewActionDefinitions = {
  approve: { key: 'approve', label: '通過', icon: 'pi pi-check', severity: 'success' },
  reject: { key: 'reject', label: '退回', icon: 'pi pi-ban', severity: 'danger', outlined: true },
  takedown: { key: 'takedown', label: '下架', icon: 'pi pi-eye-slash', severity: 'secondary', outlined: true },
  republish: { key: 'republish', label: '重新上架', icon: 'pi pi-refresh', severity: 'success', outlined: true },
  delete: { key: 'delete', label: '刪除', icon: 'pi pi-trash', severity: 'danger', text: true },
}

const getReviewRowActions = (item) => {
  const status = getReviewItemStatus(item)
  if (status === 'pending') {
    return [reviewActionDefinitions.approve, reviewActionDefinitions.reject, reviewActionDefinitions.delete]
  }
  if (status === 'approved') {
    return [reviewActionDefinitions.takedown, reviewActionDefinitions.reject, reviewActionDefinitions.delete]
  }
  if (status === 'rejected') {
    return [reviewActionDefinitions.approve, reviewActionDefinitions.delete]
  }
  if (status === 'takedown') {
    if (isReviewBlockedByCourseTrash(item)) {
      return []
    }
    return [reviewActionDefinitions.republish, reviewActionDefinitions.delete]
  }
  return []
}

const isCourseTrashLifecycleReason = (reason) => {
  if (!reason) return false
  return reason === 'course_trashed' || reason.startsWith('course_trashed|')
}

const isReviewBlockedByCourseTrash = (item) => {
  return getReviewItemStatus(item) === 'takedown' &&
    (isCourseTrashLifecycleReason(item?.lifecycle_reason) || item?.linked_course_deleted === true)
}

const getReviewTrashNote = (item) => {
  if (getReviewItemStatus(item) !== 'takedown') return ''
  if (item?.lifecycle_reason === 'linked_archive_permanently_deleted') return '無法復原：關聯考古題已永久刪除。'
  if (isCourseTrashLifecycleReason(item?.lifecycle_reason) || item?.linked_course_deleted === true) {
    return window.innerWidth <= 900
      ? '原課程在垃圾桶；請先復原原課程，投稿會回到原本狀態。'
      : '原課程已在垃圾桶，此投稿暫時下架。請先到垃圾桶復原原課程，復原後會回到原本狀態。'
  }
  if (item?.lifecycle_reason === 'archive_trashed' || item?.linked_archive_deleted === true) {
    return '關聯考古題在垃圾桶，請先復原考古題。'
  }
  return ''
}

const runReviewRowAction = (item, action) => {
  if (!item?.id) return
  if (action === 'delete') {
    confirmDeleteArchiveSubmission(item)
    return
  }
  reviewArchiveSubmission(item.id, action)
}

const getArchiveSubmissionKind = (item) => {
  if (item?.requested_category_key) return '新分類 + 新課程'
  if (item?.requested_course_name) return '新課程'
  return '考古題投稿'
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
    filtered = filtered.filter((course) => {
      const courseName = (course.name || '').toLowerCase()
      const categoryName = (getCategoryName(course.category) || '').toLowerCase()
      const categoryLabel = getCategoryDisplayLabel(course.category).toLowerCase()
      const categoryKey = (course.category || '').toLowerCase()
      return (
        courseName.includes(query) ||
        categoryName.includes(query) ||
        categoryLabel.includes(query) ||
        categoryKey.includes(query)
      )
    })
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
      courseService.getAllCourses(),
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
  reviewLoadError.value = ''
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
    reviewLoadError.value = '審核資料載入失敗，請稍後再試或查看伺服器日誌。'
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

const loadTrashItems = async () => {
  trashLoading.value = true
  try {
    const rawFilterType = getTrashFilterApiValue(trashFilterType.value)
    const filterType = rawFilterType === null ? null : rawFilterType
    if ((rawFilterType === null && trashFilterType.value !== TRASH_FILTER_ALL_VALUE) || rawFilterType !== null && rawFilterType !== trashFilterType.value) {
      trashFilterType.value = rawFilterType === null ? TRASH_FILTER_ALL_VALUE : rawFilterType
    }
    const { data } = await archiveService.listTrashItems(filterType)
    const items = Array.isArray(data) ? data : Array.isArray(data?.items) ? data.items : []
    trashItems.value = items.filter((item) => item && typeof item === 'object')
  } catch (error) {
    console.error('載入垃圾桶失敗:', error)
    if (isUnauthorizedError(error)) return
    toast.add({
      severity: 'error',
      summary: '錯誤',
      detail: getTrashErrorMessage(error, '垃圾桶載入失敗'),
      life: 3500,
    })
  } finally {
    trashLoading.value = false
  }
}

const formatTrashDeletedAt = (value) => {
  return value ? formatRelativeTime(value) : '—'
}

const getTrashSemesterText = (item) => {
  if (!['archive', 'archive_submission'].includes(item?.item_type)) return ''
  if (!item.academic_term) return '學期：—'
  return `學期：${item.academic_term}`
}

const getTrashStatusLabel = (statusValue) => {
  const normalized = normalizeSubmissionStatus(statusValue || 'deleted')
  const labels = {
    pending: '待審核',
    approved: '已通過',
    rejected: '未通過',
    takedown: '已下架',
    deleted: '已刪除',
  }
  return labels[normalized] || '已刪除'
}

const getTrashStatusSeverity = (statusValue) => {
  const normalized = normalizeSubmissionStatus(statusValue || 'deleted')
  if (normalized === 'approved') return 'success'
  if (normalized === 'pending') return 'warning'
  if (normalized === 'takedown') return 'secondary'
  return 'danger'
}

const getTrashDeletedByLabel = (item) => {
  return item?.deleted_by_name || (item?.deleted_by_id ? `使用者 #${item.deleted_by_id}` : '—')
}

const getTrashDependencies = (item) => {
  const dependencies = Array.isArray(item?.dependencies) ? item.dependencies.filter(Boolean) : []
  return dependencies
    .map((dependency) => formatTrashDependency(dependency, item?.item_type))
    .filter((item) => item?.label)
    .sort((a, b) => {
      if (a.blocking !== b.blocking) {
        return a.blocking ? -1 : 1
      }
      if (a.kindOrder !== b.kindOrder) {
        return a.kindOrder - b.kindOrder
      }
      return a.label.localeCompare(b.label)
    })
}

const getTrashDependencySeverity = (dependency) => {
  return dependency?.severity || 'secondary'
}

const formatSubmissionLabel = (item) => {
  if (!item || item.id === null || item.id === undefined) {
    return '投稿編號：—'
  }
  return `投稿編號：#${item.id}`
}

const getTrashSubmissionLabel = (item) => {
  if (!['archive', 'archive_submission'].includes(item?.item_type)) return ''
  const submissionId = item?.source_submission_id || (item?.item_type === 'archive_submission' ? item?.id : null)
  return submissionId ? `投稿編號：#${submissionId}` : '投稿編號：—'
}

const applyDependencyCount = (label, count) => {
  if (label.includes('{count}')) return label.replace('{count}', count)
  return `${count} 筆${label}`
}

const formatTrashDependency = (dependency, itemType = '') => {
  if (!dependency) return null

  if (typeof dependency === 'object') {
    const count = Number(dependency.count || 0) || 1
    const normalizedKind = String(dependency.kind || '').toLowerCase()
    const typeRaw = String(dependency.type || '').toLowerCase()
    const typeLabel = String(dependency.label || '').trim() || ''

    if (['active', 'blocking', 'blocking_live', 'blockingActive'].includes(normalizedKind)) {
      const label = typeLabel || getFallbackRelationLabel(typeRaw, 'active', itemType)
      return {
        key: `blocking-${typeRaw || 'dependency'}-${count}`,
        label: `阻擋永久刪除：${applyDependencyCount(label, count)}`,
        severity: 'danger',
        blocking: true,
        kindOrder: 0,
      }
    }

    if (['trashed', 'deleted', 'soft_deleted'].includes(normalizedKind)) {
      const label = typeLabel || getFallbackRelationLabel(typeRaw, 'trashed', itemType)
      return {
        key: `trashed-${typeRaw || 'dependency'}-${count}`,
        label: `一併永久刪除：${applyDependencyCount(label, count)}`,
        severity: 'info',
        blocking: false,
        kindOrder: 1,
      }
    }
  }

  const raw = String(dependency || '').trim()
  if (!raw) return null

  if (raw.startsWith('阻擋永久刪除：')) {
    return {
      key: `blocking-${raw}`,
      label: raw,
      severity: 'danger',
      blocking: true,
      kindOrder: 0,
    }
  }

  if (raw.startsWith('一併永久刪除：')) {
    return {
      key: `trashed-${raw}`,
      label: raw,
      severity: 'info',
      blocking: false,
      kindOrder: 1,
    }
  }

  if (
    raw.startsWith('關聯考古題：') ||
    raw.startsWith('關聯投稿：') ||
    raw.startsWith('隨投稿永久刪除：') ||
    raw === '關聯考古題仍啟用中'
  ) {
    return {
      key: `relation-${raw}`,
      label: raw,
      severity: 'secondary',
      blocking: false,
      kindOrder: 2,
    }
  }

  const value = raw.toLowerCase()
  const countMatch = raw.match(/(\d+)/)
  const count = countMatch ? Number(countMatch[1]) : 1

  const isActive = value.includes('active') || value.includes('啟用')
  const isTrashed =
    value.includes('trashed') || value.includes('deleted') || value.includes('已刪除') || value.includes('刪除')
  const isSubmission = value.includes('submission')
  const isCourse = value.includes('course') || value.includes('課程')
  const isArchive = value.includes('archive') || value.includes('考古題')
  const isCategory = value.includes('category') || value.includes('分類')
  const isComment = value.includes('comment') || value.includes('留言')

  const relationLabel = (() => {
    if (isSubmission) {
      return isActive || isTrashed ? '投稿' : '相關投稿'
    }
    if (isCourse) return '課程'
    if (isArchive) return '考古題'
    if (isCategory) return '分類'
    if (isComment) return '留言'
    return '關聯資料'
  })()

  if (value.includes('linked archive')) {
    if (isActive) {
      return {
        key: `relation-${raw}`,
        label: '關聯：此項目仍關聯到考古題（未刪除）',
        severity: 'secondary',
        blocking: false,
        kindOrder: 2,
      }
    }
    if (isTrashed) {
      return {
        key: `relation-${raw}`,
        label: '一併永久刪除：關聯考古題已刪除',
        severity: 'info',
        blocking: false,
        kindOrder: 1,
      }
    }
  }

  if (value.includes('linked archive submissions')) {
    return {
      key: `relation-${raw}`,
      label: `關聯：此項目與考古題的其他投稿有 ${count} 筆關聯（不一定阻擋）`,
      severity: 'secondary',
      blocking: false,
      kindOrder: 2,
    }
  }

  const blockerLabel = (() => {
    if (itemType === 'archive') {
      return isSubmission
        ? `1 筆啟用中投稿引用此考古題`
        : isCourse
          ? `啟用中課程依附此課程`
        : isArchive
            ? `啟用中考古題依附`
            : `啟用中${relationLabel}`
    }
    if (itemType === 'course') {
      return isArchive
        ? `啟用中考古題依附此課程`
        : isSubmission
          ? `啟用中投稿依附此分類`
          : `啟用中${relationLabel}`
    }
    if (itemType === 'course_category') {
      return isCourse
        ? `啟用中課程依附此分類`
        : isSubmission
          ? `啟用中投稿依附此分類`
          : `啟用中${relationLabel}`
    }
    return `啟用中${relationLabel}`
  })()

  const cascadeLabel = (() => {
    if (itemType === 'archive') {
      return isSubmission
        ? `1 筆已刪除投稿連到此考古題`
        : isComment
          ? `考古題留言 ${count} 筆已在垃圾桶`
          : `已刪除${relationLabel}`
    }
    if (itemType === 'course') {
      return isArchive
        ? `${count} 筆已刪除考古題屬於此課程`
        : `已刪除${relationLabel}`
    }
    if (itemType === 'course_category') {
      return isCourse
        ? `${count} 門已刪除課程屬於此分類`
        : `已刪除${relationLabel}`
    }
    return `已刪除${relationLabel} ${count} 筆`
  })()

  if (isActive) {
    return {
      key: `blocking-${raw}`,
      label: `阻擋永久刪除：${blockerLabel.replace('1 筆', `${count} 筆`)}`,
      severity: 'danger',
      blocking: true,
      kindOrder: 0,
    }
  }
  if (isTrashed) {
    return {
      key: `trashed-${raw}`,
      label: `一併永久刪除：${cascadeLabel}`,
      severity: 'info',
      blocking: false,
      kindOrder: 1,
    }
  }

  return {
    key: `relation-${raw}`,
    label: `關聯：${relationLabel}${count ? ` ${count} 筆` : ''}`,
    severity: 'secondary',
    blocking: false,
    kindOrder: 2,
  }
}

const getFallbackRelationLabel = (typeRaw, kind, itemType) => {
  const t = typeRaw.toLowerCase()
  const isSubmission = t.includes('submission') || t.includes('投稿')
  const isCourse = t.includes('course') || t.includes('課程')
  const isArchive = t.includes('archive') || t.includes('考古題')

  if (kind === 'active') {
    if (itemType === 'archive' && isSubmission) return '{count} 筆啟用中投稿仍連到此考古題'
    if (itemType === 'course' && isArchive) return '{count} 筆啟用中考古題仍屬於此課程'
    if (itemType === 'course_category' && isCourse) return '{count} 門啟用中課程仍屬於此分類'
    if (isSubmission) return '{count} 筆啟用中投稿仍關聯此項目'
    if (isCourse) return '{count} 門啟用中課程仍關聯此項目'
    if (isArchive) return '{count} 筆啟用中考古題仍關聯此項目'
    return '{count} 筆啟用中關聯資料仍關聯此項目'
  }

  if (itemType === 'archive' && isSubmission) return '{count} 筆已刪除投稿連到此考古題'
  if (itemType === 'course' && isArchive) return '{count} 筆已刪除考古題屬於此課程'
  if (itemType === 'course_category' && isCourse) return '{count} 門已刪除課程屬於此分類'
  if (isSubmission) return '{count} 筆已刪除投稿關聯此項目'
  if (isCourse) return '{count} 門已刪除課程關聯此項目'
  if (isArchive) return '{count} 筆已刪除考古題關聯此項目'
  return '{count} 筆已刪除關聯資料關聯此項目'
}

const getTrashErrorMessage = (error, fallback = '操作失敗') => {
  const detail = error?.response?.data?.detail
  if (!detail) return fallback
  if (typeof detail === 'string') return detail
  if (detail.message) return detail.message
  if (Array.isArray(detail.blockingDependencies) && detail.blockingDependencies.length) {
    return '仍有依賴資料阻擋此操作'
  }
  return fallback
}

const getTrashBulkResultMessage = (data) => {
  const deletedCount = Number(data?.deleted_count ?? data?.deleted ?? 0)
  const failedCount = Number(data?.failed_count ?? data?.failed ?? 0)
  if (deletedCount > 0 && failedCount > 0) return `已永久刪除 ${deletedCount} 筆，${failedCount} 筆失敗`
  if (deletedCount > 0) return `已永久刪除 ${deletedCount} 筆`
  if (failedCount > 0) return `${failedCount} 筆永久刪除失敗`
  return '沒有可永久刪除的項目'
}

const confirmRestoreTrashItem = (item) => {
  confirm.require({
    message: `確定要還原「${item.display_name}」嗎？`,
    header: '確認還原',
    icon: 'pi pi-undo',
    accept: () => restoreTrashItem(item),
  })
}

const restoreTrashItem = async (item) => {
  try {
    await archiveService.restoreTrashItem(item.item_type, item.id)
    toast.add({ severity: 'success', summary: '已還原', detail: '項目已還原', life: 3000 })
    await loadTrashItems()
  } catch (error) {
    console.error('還原垃圾桶項目失敗:', error)
    if (isUnauthorizedError(error)) return
    toast.add({
      severity: 'error',
      summary: '還原失敗',
      detail: getTrashErrorMessage(error, '項目還原失敗'),
      life: 4000,
    })
  }
}

const confirmPermanentDeleteTrashItem = (item) => {
  confirm.require({
    message: `確定要永久刪除「${item.display_name}」嗎？此動作無法復原。`,
    header: '確認永久刪除',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: () => permanentlyDeleteTrashItem(item),
  })
}

const permanentlyDeleteTrashItem = async (item) => {
  try {
    const { data } = await archiveService.permanentlyDeleteTrashItem(item.item_type, item.id)
    const deletedCount = Number(data?.deleted_count ?? data?.deleted ?? 1)
    toast.add({ severity: 'success', summary: '已永久刪除', detail: `已永久刪除 ${deletedCount} 筆`, life: 3000 })
    await loadTrashItems()
  } catch (error) {
    console.error('永久刪除垃圾桶項目失敗:', error)
    if (isUnauthorizedError(error)) return
    toast.add({
      severity: 'error',
      summary: '永久刪除失敗',
      detail: getTrashErrorMessage(error, '永久刪除失敗'),
      life: 4500,
    })
  }
}

const confirmBulkDeleteTrash = () => {
  const scopeLabel = trashFilterOptions.find((option) => option.value === trashFilterType.value)?.label || '全部'
  confirm.require({
    message: `確定要永久刪除「${scopeLabel}」範圍內的垃圾桶項目嗎？此動作無法復原。`,
    header: '確認清空目前範圍',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: bulkDeleteTrashScope,
  })
}

const bulkDeleteTrashScope = async () => {
  try {
    const scopeType = getTrashFilterApiValue(trashFilterType.value)
    const { data } = await archiveService.permanentlyDeleteTrashScope(scopeType)
    const deletedCount = Number(data?.deleted_count ?? data?.deleted ?? 0)
    const failedCount = Number(data?.failed_count ?? data?.failed ?? 0)
    if (deletedCount > 0) {
      toast.add({
        severity: failedCount ? 'warn' : 'success',
        summary: failedCount ? '部分完成' : '已清空',
        detail: getTrashBulkResultMessage(data),
        life: 4500,
      })
    } else {
      toast.add({
        severity: failedCount ? 'error' : 'info',
        summary: failedCount ? '清空失敗' : '沒有項目',
        detail: getTrashBulkResultMessage(data),
        life: 4500,
      })
    }
    await loadTrashItems()
  } catch (error) {
    console.error('清空垃圾桶範圍失敗:', error)
    if (isUnauthorizedError(error)) return
    toast.add({
      severity: 'error',
      summary: '清空失敗',
      detail: getTrashErrorMessage(error, '清空目前範圍失敗'),
      life: 4500,
    })
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
    } else if (action === 'takedown') {
      await archiveService.takedownSubmission(submissionId)
    } else if (action === 'republish') {
      await archiveService.republishSubmission(submissionId)
    } else {
      await archiveService.rejectSubmission(submissionId)
    }
    const actionMessages = {
      approve: '考古題投稿已通過',
      reject: '考古題投稿已退回',
      takedown: '考古題投稿已下架',
      republish: '考古題投稿已重新上架',
    }
    toast.add({
      severity: 'success',
      summary: '完成',
      detail: actionMessages[action] || '考古題投稿狀態已更新',
      life: 3000,
    })
    await loadReviewItems()
    showArchiveRequestDialog.value = false
  } catch (error) {
    console.error('審核考古題投稿失敗:', error)
    if (isUnauthorizedError(error)) return
    toast.add({ severity: 'error', summary: '錯誤', detail: getTrashErrorMessage(error, '審核考古題投稿失敗'), life: 3000 })
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
    message: `確定要刪除分類「${category.name}」嗎？刪除後將進入垃圾桶。`,
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
    toast.add({ severity: 'success', summary: '成功', detail: '分類已移到垃圾桶', life: 3000 })
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
    return
  }

  if (tab === '4') {
    await loadTrashItems()
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
    4: 'trash',
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
  min-width: 0;
  max-width: 100%;
  overflow-x: hidden;
}

.card {
  background-color: var(--bg-primary);
  min-width: 0;
  max-width: 100%;
}

:deep(.p-tabs) {
  background: var(--p-tabs-tabpanel-background);
  min-width: 0;
  max-width: 100%;
}

:deep(.p-tabpanels),
:deep(.p-tabpanel) {
  min-width: 0;
  max-width: 100%;
  overflow-x: hidden;
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
  max-width: 100%;
  overflow-x: auto;
}

:deep(.p-datatable-table-container) {
  max-width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
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

.review-search-toolbar {
  display: flex;
  justify-content: flex-start;
  margin-bottom: 1rem;
}

.review-empty-state {
  padding: 1rem;
  color: var(--text-secondary);
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

.review-sort-header {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0;
  border: 0;
  background: transparent;
  color: inherit;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}

.review-course-cell {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  flex-wrap: wrap;
}

:deep(.review-admin-upload-chip) {
  background: rgba(59, 130, 246, 0.18);
  color: #93c5fd;
  border-color: rgba(59, 130, 246, 0.4);
}

.review-load-error {
  margin-bottom: 1rem;
  padding: 0.75rem 1rem;
  border: 1px solid rgba(239, 68, 68, 0.38);
  border-radius: 8px;
  background: rgba(239, 68, 68, 0.12);
  color: #fecaca;
}

.trash-name-cell {
  display: inline-flex;
  flex-direction: column;
  gap: 0.2rem;
  min-width: 16rem;
}

.trash-name-title {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  white-space: nowrap;
}

.trash-tree-prefix {
  color: var(--text-secondary);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-weight: 700;
  letter-spacing: 0;
}

.trash-name-cell small {
  color: var(--text-secondary);
  margin-left: 0.15rem;
}

.trash-dependencies {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.trash-dependency-help {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  padding-right: 0.15rem;
}

.trash-dependency-help-intro {
  margin: 0;
  color: var(--text-secondary);
}

.trash-dependency-help-section {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 0.7rem 0.8rem;
  background: color-mix(in srgb, var(--surface-card) 86%, transparent);
}

.trash-dependency-help-title {
  margin: 0 0 0.45rem 0;
  font-size: 0.95rem;
  font-weight: 700;
}

.trash-dependency-help-list {
  margin: 0;
  padding-left: 1.1rem;
  color: var(--text-color);
}

.trash-dependency-help-list li + li {
  margin-top: 0.3rem;
}

.trash-dependency-help-rule,
.trash-dependency-help-note {
  margin: 0.35rem 0 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.trash-dependency-help-note {
  border: 1px dashed color-mix(in srgb, var(--border-color) 60%, transparent);
  padding: 0.45rem 0.55rem;
  border-radius: 6px;
}

:deep(.review-status-chip.review-status-pending) {
  background: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
  border-color: rgba(245, 158, 11, 0.42);
}

:deep(.review-status-chip.review-status-approved) {
  background: rgba(34, 197, 94, 0.18);
  color: #86efac;
  border-color: rgba(34, 197, 94, 0.38);
}

:deep(.review-status-chip.review-status-rejected) {
  background: rgba(239, 68, 68, 0.18);
  color: #fca5a5;
  border-color: rgba(239, 68, 68, 0.38);
}

:deep(.review-status-chip.review-status-takedown) {
  background: rgba(100, 116, 139, 0.22);
  color: #cbd5e1;
  border-color: rgba(100, 116, 139, 0.42);
}

:deep(.review-status-chip.review-status-deleted) {
  background: rgba(127, 29, 29, 0.28);
  color: #fecaca;
  border-color: rgba(127, 29, 29, 0.5);
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

.category-name-mobile,
.category-key-mobile,
.category-key-mobile-inline {
  display: none;
}

.category-name-desktop {
  display: inline;
}

.category-key-desktop {
  display: inline;
}

.mobile-primary-text,
.mobile-long-text,
.mobile-metadata-text {
  display: block;
  min-width: 0;
  max-width: 100%;
}

.admin-mobile-card {
  display: none;
}

.admin-mobile-list {
  display: none;
}

/* Mobile responsive adjustments */
@media (max-width: 768px) {
  .admin-container {
    padding-left: 0.75rem !important;
    padding-right: 0.75rem !important;
    overflow-x: hidden;
  }

  :deep(.p-tablist),
  :deep(.p-tablist-content),
  :deep(.p-tablist-tab-list) {
    overflow-x: auto;
    scrollbar-width: thin;
  }

  :deep(.p-tab) {
    flex: 0 0 auto;
    white-space: nowrap;
  }

  :deep(.p-datatable) {
    font-size: 0.875rem;
    overflow-x: auto;
    border-radius: 8px;
    max-width: 100%;
  }

  :deep(.p-datatable-table-container) {
    overflow-x: visible !important;
    max-height: none !important;
  }

  :deep(.p-datatable-table) {
    display: block;
    min-width: 0 !important;
    width: 100% !important;
  }

  :deep(.p-datatable-thead) {
    display: none;
  }

  :deep(.p-datatable-tbody) {
    display: block;
  }

  :deep(.p-datatable-tbody > tr) {
    display: grid;
    grid-template-columns: minmax(0, 1fr);
    gap: 0.45rem;
    width: 100%;
    margin-bottom: 0.65rem;
    padding: 0.8rem;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    background: color-mix(in srgb, var(--bg-secondary) 86%, transparent);
  }

  :deep(.p-datatable .p-datatable-tbody > tr > td) {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.2rem;
    width: 100%;
    min-width: 0;
    padding: 0 !important;
    border: 0 !important;
    background: transparent !important;
    overflow-wrap: normal;
    word-break: normal;
  }

  :deep(.p-datatable .p-datatable-tbody > tr > td .p-column-title) {
    display: block;
    color: var(--text-secondary);
    font-size: 0.72rem;
    font-weight: 700;
    line-height: 1.3;
  }

  :deep(.p-datatable .p-column-title + *) {
    width: 100%;
  }

  :deep(.p-datatable .p-tag) {
    width: fit-content;
    max-width: 100%;
    white-space: nowrap;
  }

  .mobile-card-order {
    width: auto;
    min-width: 0;
    flex-wrap: nowrap;
  }

  .mobile-card-order .w-2rem {
    width: auto !important;
    min-width: 1.25rem;
    text-align: center;
  }

  :deep(.mobile-card-order .p-button) {
    width: 2rem;
    min-width: 2rem;
    height: 2rem;
    min-height: 2rem;
  }

  :deep(.course-management-table .p-column-title),
  :deep(.category-management-table .p-column-title) {
    display: none !important;
  }

  :deep(.course-management-table .p-datatable-tbody > tr),
  :deep(.category-management-table .p-datatable-tbody > tr) {
    grid-template-columns: minmax(0, 1fr);
    align-items: stretch;
    gap: 0.55rem;
    padding: 0.9rem;
  }

  :deep(.category-management-table .p-datatable-tbody > tr > td:nth-child(1)) {
    align-self: stretch;
  }

  :deep(.category-management-table .p-datatable-tbody > tr > td:nth-child(2)) {
    align-self: stretch;
  }

  :deep(.category-management-table .p-datatable-tbody > tr > td:nth-child(3)) {
    align-self: stretch;
  }

  :deep(.category-management-table .p-datatable-tbody > tr > td:nth-child(4)) {
    display: none;
  }

  :deep(.category-management-table .p-datatable-tbody > tr > td:nth-child(5)) {
    align-self: stretch;
  }

  :deep(.category-management-table .p-datatable-tbody > tr > td:nth-child(6)) {
    align-self: stretch;
  }

  :deep(.course-management-table .p-datatable-tbody > tr > td),
  :deep(.category-management-table .p-datatable-tbody > tr > td) {
    grid-area: auto;
    align-self: stretch;
  }

  .category-name-desktop,
  .category-key-desktop {
    display: none;
  }

  .category-name-mobile {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
    align-items: flex-start;
    width: 100%;
    min-width: 0;
  }

  .category-mobile-header {
    display: grid;
    grid-template-columns: minmax(0, 1fr);
    align-items: start;
    gap: 0.45rem;
    width: 100%;
  }

  .category-mobile-title {
    min-width: 0;
    color: var(--text-primary);
    font-size: 1rem;
    font-weight: 700;
    line-height: 1.35;
    word-break: normal;
    overflow-wrap: break-word;
  }

  .category-key-mobile {
    display: inline-flex;
    flex-direction: column;
    gap: 0.15rem;
    align-items: flex-start;
    max-width: 100%;
    padding: 0.35rem 0.55rem;
    border: 1px solid var(--border-color);
    border-radius: 0.55rem;
    background: color-mix(in srgb, var(--panel-bg) 88%, var(--primary-color) 12%);
  }

  .mobile-field-label {
    display: block;
    color: var(--accent-gold);
    font-size: 0.68rem;
    font-weight: 700;
    line-height: 1.25;
    letter-spacing: 0.04em;
    white-space: nowrap;
  }

  .mobile-field-value {
    display: block;
    color: var(--text-primary);
    font-size: 0.95rem;
    line-height: 1.35;
    overflow-wrap: anywhere;
  }

  .mobile-primary-text,
  .mobile-long-text,
  .mobile-metadata-text {
    min-width: 0;
    max-width: 100%;
    width: 100%;
    word-break: normal;
  }

  .mobile-primary-text {
    font-weight: 700;
    font-size: 1rem;
    line-height: 1.35;
    color: var(--text-primary);
    word-break: normal;
    overflow-wrap: break-word;
  }

  .mobile-long-text {
    overflow-wrap: anywhere;
    word-break: break-word;
  }

  .mobile-metadata-text {
    color: var(--text-secondary);
    font-size: 0.85rem;
    line-height: 1.35;
  }

  :deep(.admin-desktop-data-table.user-management-table),
  :deep(.admin-desktop-data-table.course-management-table),
  :deep(.admin-desktop-data-table.category-management-table),
  :deep(.admin-desktop-data-table.notification-management-table) {
    display: none;
  }

  .admin-mobile-list {
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
    width: 100%;
    min-width: 0;
  }

  .admin-mobile-list .admin-mobile-card {
    display: flex;
    flex-direction: column;
    width: 100%;
    max-width: 100%;
    min-width: 0;
    gap: 0.85rem;
    box-sizing: border-box;
    padding: 1rem;
    border: 1px solid color-mix(in srgb, var(--primary-color) 38%, var(--border-color));
    border-radius: 8px;
    background: color-mix(in srgb, var(--bg-secondary) 86%, transparent);
  }

  .admin-mobile-list .admin-card-primary {
    display: block;
    width: 100%;
    max-width: 100%;
    min-width: 0;
  }

  .admin-mobile-list .admin-card-title {
    display: block;
    width: 100%;
    max-width: 100%;
    min-width: 0;
    color: var(--text-primary);
    font-size: 1rem;
    font-weight: 800;
    line-height: 1.35;
    word-break: normal;
    overflow-wrap: break-word;
  }

  .admin-mobile-list .admin-card-email {
    display: block;
    width: 100%;
    max-width: 100%;
    min-width: 0;
    margin-top: 0.25rem;
    color: var(--text-primary);
    font-size: 0.95rem;
    line-height: 1.4;
    word-break: normal;
    overflow-wrap: anywhere;
  }

  .admin-mobile-list .admin-card-meta {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.45rem;
    width: 100%;
    min-width: 0;
  }

  .admin-mobile-list .admin-card-meta-text {
    color: var(--text-primary);
    font-size: 0.9rem;
    line-height: 1.3;
    white-space: nowrap;
  }

  :deep(.admin-mobile-list .p-tag) {
    white-space: nowrap;
  }

  .admin-mobile-list--categories .admin-category-card {
    gap: 0.7rem;
  }

  .category-card-topline {
    display: flex;
    align-items: center;
    gap: 0.45rem;
    width: 100%;
    min-width: 0;
  }

  .category-card-order {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 1.85rem;
    height: 1.85rem;
    border-radius: 999px;
    background: color-mix(in srgb, var(--primary-color) 18%, transparent);
    color: var(--text-primary);
    font-size: 0.85rem;
    font-weight: 800;
    line-height: 1;
  }

  :deep(.category-card-topline .p-button) {
    width: 2rem;
    min-width: 2rem;
    height: 2rem;
    min-height: 2rem;
    padding-inline: 0;
    justify-content: center;
  }

  :deep(.category-card-topline .pi) {
    margin: 0;
    line-height: 1;
  }

  .category-card-main {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 0.75rem;
    width: 100%;
    min-width: 0;
  }

  .category-card-title {
    display: block;
    min-width: 0;
    color: var(--text-primary);
    font-size: 1.05rem;
    font-weight: 800;
    line-height: 1.35;
    word-break: normal;
    overflow-wrap: break-word;
  }

  .category-card-key {
    display: inline-flex;
    flex: 0 1 auto;
    flex-direction: column;
    gap: 0.1rem;
    align-items: flex-start;
    max-width: 48%;
    padding: 0.32rem 0.5rem;
    border: 1px solid var(--border-color);
    border-radius: 0.55rem;
    background: color-mix(in srgb, var(--panel-bg) 88%, var(--primary-color) 12%);
  }

  .category-card-key-label {
    color: var(--accent-gold);
    font-size: 0.68rem;
    font-weight: 800;
    line-height: 1.2;
    white-space: nowrap;
  }

  .category-card-key-value {
    max-width: 100%;
    color: var(--text-primary);
    font-size: 0.82rem;
    line-height: 1.25;
    overflow-wrap: anywhere;
  }

  .category-card-meta {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.45rem;
    width: 100%;
    min-width: 0;
  }

  .admin-mobile-list.admin-mobile-list--categories .admin-mobile-card-actions.category-card-actions {
    display: grid;
    grid-template-columns: repeat(3, minmax(44px, 1fr));
    gap: 0.5rem;
    width: 100%;
    align-items: center;
  }

  :deep(.admin-mobile-list--categories .admin-mobile-card-actions .p-button-label) {
    display: none;
  }

  :deep(.admin-mobile-list--categories .admin-mobile-card-actions .pi) {
    margin: 0;
    line-height: 1;
  }

  :deep(.admin-mobile-list--categories .admin-mobile-card-actions .p-button) {
    width: 100%;
    min-width: 44px;
    min-height: 44px;
    justify-content: center;
  }

  .admin-mobile-list--courses .admin-course-card {
    gap: 0.7rem;
  }

  .course-card-topline {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.45rem;
    width: 100%;
    min-width: 0;
  }

  .course-card-order {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 1.85rem;
    height: 1.85rem;
    border-radius: 999px;
    background: color-mix(in srgb, var(--primary-color) 18%, transparent);
    color: var(--text-primary);
    font-size: 0.85rem;
    font-weight: 800;
    line-height: 1;
  }

  :deep(.course-card-topline .p-button) {
    width: 2rem;
    min-width: 2rem;
    height: 2rem;
    min-height: 2rem;
    padding-inline: 0;
    justify-content: center;
  }

  :deep(.course-card-topline .pi) {
    margin: 0;
    line-height: 1;
  }

  :deep(.course-card-category) {
    width: fit-content;
    max-width: 100%;
    white-space: nowrap;
  }

  .course-card-primary {
    display: block;
    width: 100%;
    min-width: 0;
  }

  .course-card-title {
    display: block;
    width: 100%;
    max-width: 100%;
    min-width: 0;
    color: var(--text-primary);
    font-size: 1.05rem;
    font-weight: 800;
    line-height: 1.35;
    word-break: normal;
    overflow-wrap: break-word;
  }

  .admin-mobile-list .admin-mobile-card-actions {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    width: 100%;
    gap: 0.5rem;
  }

  :deep(.admin-mobile-list--courses .admin-mobile-card-actions .p-button-label) {
    display: none;
  }

  :deep(.admin-mobile-list--courses .admin-mobile-card-actions .pi) {
    margin: 0;
    line-height: 1;
  }

  :deep(.admin-mobile-list .admin-mobile-card-actions .p-button) {
    width: 100%;
    min-width: 0;
    min-height: 2.65rem;
    justify-content: center;
  }

  :deep(.user-management-table .p-column-title),
  :deep(.notification-management-table .p-column-title) {
    display: none !important;
  }

  :deep(.user-management-table .p-datatable-tbody > tr),
  :deep(.notification-management-table .p-datatable-tbody > tr) {
    display: flex;
    flex-direction: column;
    grid-template-columns: minmax(0, 1fr);
    gap: 0.7rem;
    padding: 1rem;
  }

  :deep(.user-management-table .p-datatable-tbody > tr > td:nth-child(1)),
  :deep(.notification-management-table .p-datatable-tbody > tr > td:nth-child(1)) {
    display: block;
    width: 100%;
    max-width: 100%;
    min-width: 0;
  }

  :deep(.user-management-table .p-datatable-tbody > tr > td:nth-child(2)),
  :deep(.user-management-table .p-datatable-tbody > tr > td:nth-child(3)),
  :deep(.user-management-table .p-datatable-tbody > tr > td:nth-child(4)),
  :deep(.user-management-table .p-datatable-tbody > tr > td:nth-child(5)),
  :deep(.notification-management-table .p-datatable-tbody > tr > td:nth-child(2)),
  :deep(.notification-management-table .p-datatable-tbody > tr > td:nth-child(3)),
  :deep(.notification-management-table .p-datatable-tbody > tr > td:nth-child(4)),
  :deep(.notification-management-table .p-datatable-tbody > tr > td:nth-child(5)) {
    display: none;
  }

  :deep(.user-management-table .p-datatable-tbody > tr > td:last-child),
  :deep(.notification-management-table .p-datatable-tbody > tr > td:last-child) {
    display: block;
    width: 100%;
    max-width: 100%;
    min-width: 0;
  }

  :deep(.user-management-table .admin-desktop-cell),
  :deep(.notification-management-table .admin-desktop-cell) {
    display: none;
  }

  .admin-mobile-card {
    display: flex;
    flex-direction: column;
    width: 100%;
    max-width: 100%;
    min-width: 0;
    gap: 0.75rem;
    box-sizing: border-box;
  }

  :deep(.user-management-table .admin-mobile-card),
  :deep(.notification-management-table .admin-mobile-card) {
    display: flex;
    width: 100%;
    max-width: 100%;
    min-width: 0;
  }

  .admin-card-primary {
    display: block;
    width: 100%;
    max-width: 100%;
    min-width: 0;
  }

  .admin-card-title {
    display: block;
    width: 100%;
    max-width: 100%;
    min-width: 0;
    color: var(--text-primary);
    font-size: 1rem;
    font-weight: 800;
    line-height: 1.35;
    word-break: normal;
    overflow-wrap: break-word;
  }

  .admin-card-email {
    display: block;
    width: 100%;
    max-width: 100%;
    min-width: 0;
    margin-top: 0.25rem;
    color: var(--text-primary);
    font-size: 0.95rem;
    line-height: 1.4;
    word-break: normal;
    overflow-wrap: anywhere;
  }

  .admin-card-meta {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.45rem;
    width: 100%;
    min-width: 0;
  }

  .admin-card-meta-text {
    color: var(--text-primary);
    font-size: 0.9rem;
    line-height: 1.3;
    white-space: nowrap;
  }

  :deep(.user-management-table .admin-card-actions),
  :deep(.notification-management-table .admin-card-actions) {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    width: 100%;
    gap: 0.5rem;
  }

  :deep(.user-management-table .admin-card-actions .p-button),
  :deep(.notification-management-table .admin-card-actions .p-button) {
    width: 100%;
    min-width: 0;
    min-height: 2.6rem;
  }

  .admin-card-actions {
    width: 100%;
    min-width: 0;
    display: flex;
    flex-wrap: wrap;
    gap: 0.45rem;
    align-items: stretch;
  }

  :deep(.admin-card-actions .p-button) {
    width: auto;
    min-width: 7rem;
    min-height: 2.35rem;
    justify-content: center;
  }

  :deep(.course-management-table .admin-card-actions),
  :deep(.category-management-table .admin-card-actions) {
    width: 100%;
    flex-direction: row;
    flex-wrap: wrap;
    gap: 0.35rem;
  }

  :deep(.course-management-table .admin-card-actions .p-button),
  :deep(.category-management-table .admin-card-actions .p-button) {
    min-width: 2.45rem;
    width: 2.45rem;
    height: 2.45rem;
    padding-inline: 0;
  }

  :deep(.course-management-table .admin-card-actions .p-button-label),
  :deep(.category-management-table .admin-card-actions .p-button-label) {
    display: none;
  }

  :deep(.course-management-table .admin-card-actions .pi),
  :deep(.category-management-table .admin-card-actions .pi) {
    margin: 0;
    line-height: 1;
  }

  :deep(.p-datatable .p-button) {
    min-height: 2.25rem;
    white-space: nowrap;
  }

  :deep(.p-datatable .p-button.p-button-icon-only) {
    width: 2.5rem;
    min-width: 2.5rem;
    flex-basis: 2.5rem;
    padding-inline: 0;
    justify-content: center;
  }


  :deep(.p-datatable-tbody > tr:last-child) {
    margin-bottom: 0;
  }

  :deep(.review-request-table .p-datatable-tbody > tr) {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.55rem 0.75rem;
    padding: 0.9rem;
    align-items: center;
  }

  :deep(.review-request-table .p-datatable-tbody > tr > td) {
    width: 100%;
    min-width: 0;
    align-self: stretch;
  }

  :deep(.review-request-table .p-datatable-tbody > tr > td:first-child),
  :deep(.review-request-table .p-datatable-tbody > tr > td:last-child) {
    grid-column: 1 / -1;
  }

  :deep(.review-request-table .p-column-title) {
    display: none !important;
  }

  :deep(.review-card-title) {
    display: block;
    width: 100%;
    max-width: 100%;
    min-width: 0;
    color: var(--text-primary);
    font-size: 1rem;
    font-weight: 800;
    line-height: 1.35;
    word-break: normal;
    overflow-wrap: break-word;
  }

  :deep(.review-card-meta-text) {
    display: inline-flex;
    width: fit-content;
    max-width: 100%;
    color: var(--text-primary);
    font-size: 0.9rem;
    line-height: 1.35;
    white-space: nowrap;
  }

  :deep(.review-request-table .p-tag),
  :deep(.review-card-chip) {
    width: fit-content;
    max-width: 100%;
    white-space: nowrap;
  }

  :deep(.review-request-table--new .p-datatable-tbody > tr > td:nth-child(1)) {
    order: 1;
    grid-column: 1 / -1;
  }

  :deep(.review-request-table--new .p-datatable-tbody > tr > td:nth-child(3)) {
    order: 2;
    grid-column: 1;
  }

  :deep(.review-request-table--new .p-datatable-tbody > tr > td:nth-child(4)) {
    order: 3;
    grid-column: 2;
  }

  :deep(.review-request-table--new .p-datatable-tbody > tr > td:nth-child(5)) {
    order: 4;
    grid-column: 1;
  }

  :deep(.review-request-table--new .p-datatable-tbody > tr > td:nth-child(2)) {
    order: 5;
    grid-column: 1;
  }

  :deep(.review-request-table--new .p-datatable-tbody > tr > td:nth-child(6)) {
    order: 6;
    grid-column: 2;
  }

  :deep(.review-request-table--new .p-datatable-tbody > tr > td:nth-child(7)) {
    order: 7;
    grid-column: 1 / -1;
  }

  :deep(.review-card-actions) {
    display: grid;
    grid-template-columns: repeat(4, minmax(2.5rem, 1fr));
    width: 100%;
    gap: 0.45rem;
  }

  :deep(.review-card-action-note) {
    grid-column: 1 / -1;
    color: var(--text-color-secondary);
    font-size: 0.75rem;
    line-height: 1.25;
    margin-top: 0.2rem;
  }

  :deep(.review-card-actions .p-button) {
    width: 100%;
    min-width: 0;
    min-height: 2.5rem;
    padding-inline: 0.4rem;
    justify-content: center;
  }

  :deep(.review-card-actions .p-button-label) {
    display: none;
  }

  :deep(.review-card-actions .pi) {
    margin: 0;
    line-height: 1;
  }

  :deep(.p-paginator) {
    font-size: 0.875rem;
    justify-content: flex-start;
    overflow-x: auto;
    padding: 0.5rem 0;
    max-width: 100%;
  }

  .compare-preview-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  :deep(.admin-card-actions .p-button) {
    min-width: 2.6rem;
    width: 2.6rem;
    padding-inline: 0.4rem;
    justify-content: center;
  }

  :deep(.admin-card-actions .p-button .p-button-label) {
    display: none;
  }

  :deep(.admin-card-actions .p-button .pi) {
    margin: 0;
    line-height: 1;
  }

}

@media (max-width: 600px) {
  :deep(.admin-card-actions .p-button) {
    min-width: 2.65rem;
    width: 2.65rem;
    min-height: 2.65rem;
    padding-inline: 0.45rem;
    justify-content: center;
  }

  :deep(.admin-card-actions .p-button .p-button-label) {
    display: none;
  }

  :deep(.admin-card-actions .p-button .pi) {
    margin: 0;
    line-height: 1;
  }

  :deep(.user-management-table .admin-card-actions),
  :deep(.notification-management-table .admin-card-actions) {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    width: 100%;
    gap: 0.5rem;
  }

  :deep(.user-management-table .admin-card-actions .p-button),
  :deep(.notification-management-table .admin-card-actions .p-button) {
    width: 100%;
    min-width: 0;
    min-height: 2.65rem;
  }

  :deep(.admin-mobile-list .admin-mobile-card-actions .p-button) {
    width: 100%;
    min-width: 0;
    min-height: 2.65rem;
  }
}

@media (max-width: 768px) {
  .review-dialog-actions {
    display: grid !important;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.5rem;
    justify-content: stretch;
  }

  :deep(.review-dialog-actions .p-button) {
    width: 100%;
    min-width: 0;
    min-height: 2.75rem;
    padding-inline: 0.45rem;
    justify-content: center;
  }

  :deep(.review-dialog-actions .p-button-label) {
    display: none;
  }

  :deep(.review-dialog-actions .pi) {
    margin: 0;
    line-height: 1;
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

  :deep(.p-datatable .admin-card-actions),
  :deep(.p-datatable .review-card-actions) {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  :deep(.review-card-action-note) {
    width: 100%;
    color: var(--text-color-secondary);
    font-size: 0.75rem;
    line-height: 1.25;
    margin-top: 0.2rem;
  }

  /* Ensure buttons don't wrap on desktop */
  :deep(.p-datatable .flex.gap-2) {
    flex-wrap: nowrap;
    gap: 0.5rem;
  }
}
</style>
