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
                      <Tag severity="secondary" :class="getCategoryBadgeClass(data)">
                        {{ data.label || data.name }}
                      </Tag>
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
                      <Tag severity="secondary" :class="getCategoryBadgeClass(category)">
                        {{ category.label || category.name }}
                      </Tag>
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
                    <Tag severity="secondary" :class="['text-sm', getCategoryBadgeClass(data.category)]">
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
                    <Tag severity="secondary" :class="['course-card-category', getCategoryBadgeClass(course.category)]">
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
                <Column field="is_online" header="上線狀態" sortable style="width: 16%">
                  <template #body="{ data }">
                    <span class="user-online-badge" :class="getOnlineStatusDotClass(data)">
                      <i class="pi pi-circle-fill"></i>
                      <span>{{ getOnlineStatusLabel(data) }}</span>
                    </span>
                  </template>
                </Column>
                <Column header="操作" style="width: 24%">
                  <template #body="{ data }">
                    <div class="admin-card-actions user-management-actions">
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
                      icon="pi pi-key"
                      severity="info"
                      size="small"
                      @click="openResetPasswordDialog(data)"
                      label="重設密碼"
                      aria-label="重設使用者密碼"
                      :title="data.is_local ? '重設密碼' : NON_LOCAL_PASSWORD_RESET_HINT"
                      :disabled="!data.is_local"
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
                    <span class="user-online-badge" :class="getOnlineStatusDotClass(user)">
                      <i class="pi pi-circle-fill"></i>
                      <span>{{ getOnlineStatusLabel(user) }}</span>
                    </span>
                  </section>
                  <section class="admin-card-actions admin-mobile-card-actions user-management-actions">
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
                      icon="pi pi-key"
                      severity="info"
                      size="small"
                      @click="openResetPasswordDialog(user)"
                      label="重設密碼"
                      aria-label="重設使用者密碼"
                      :title="user.is_local ? '重設密碼' : NON_LOCAL_PASSWORD_RESET_HINT"
                      :disabled="!user.is_local"
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
                        <i class="review-sort-icon" :class="getReviewSortHeaderIcon('new', 'subject')" aria-hidden="true"></i>
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
                        <i class="review-sort-icon" :class="getReviewSortHeaderIcon('new', 'kind')" aria-hidden="true"></i>
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
                        <i class="review-sort-icon" :class="getReviewSortHeaderIcon('new', 'name')" aria-hidden="true"></i>
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
                        <i class="review-sort-icon" :class="getReviewSortHeaderIcon('new', 'professor')" aria-hidden="true"></i>
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
                        <i class="review-sort-icon" :class="getReviewSortHeaderIcon('new', 'academic_year')" aria-hidden="true"></i>
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
                        <i class="review-sort-icon" :class="getReviewSortHeaderIcon('new', 'submitted_at')" aria-hidden="true"></i>
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
                        <i class="review-sort-icon" :class="getReviewSortHeaderIcon('new', 'status')" aria-hidden="true"></i>
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
                      <div class="review-row-action-area">
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
                        </div>
                        <div
                          v-if="getReviewTrashNote(data)"
                          :class="['review-card-action-note', getReviewTrashNoteClass(data)]"
                          :title="getReviewTrashNote(data, true)"
                        >
                          <i :class="getReviewTrashNoteIcon(data)" aria-hidden="true"></i>
                          <span class="review-card-action-note__text">{{ getReviewTrashNote(data) }}</span>
                        </div>
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
                        <i class="review-sort-icon" :class="getReviewSortHeaderIcon('existing', 'subject')" aria-hidden="true"></i>
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
                        <i class="review-sort-icon" :class="getReviewSortHeaderIcon('existing', 'name')" aria-hidden="true"></i>
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
                        <i class="review-sort-icon" :class="getReviewSortHeaderIcon('existing', 'professor')" aria-hidden="true"></i>
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
                        <i class="review-sort-icon" :class="getReviewSortHeaderIcon('existing', 'academic_year')" aria-hidden="true"></i>
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
                        <i class="review-sort-icon" :class="getReviewSortHeaderIcon('existing', 'submitted_at')" aria-hidden="true"></i>
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
                        <i class="review-sort-icon" :class="getReviewSortHeaderIcon('existing', 'status')" aria-hidden="true"></i>
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
                      <div class="review-row-action-area">
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
                        </div>
                        <div
                          v-if="getReviewTrashNote(data)"
                          :class="['review-card-action-note', getReviewTrashNoteClass(data)]"
                          :title="getReviewTrashNote(data, true)"
                        >
                          <i :class="getReviewTrashNoteIcon(data)" aria-hidden="true"></i>
                          <span class="review-card-action-note__text">{{ getReviewTrashNote(data) }}</span>
                        </div>
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
                :rowClass="getTrashRowClass"
              >
                <Column field="deleted_at">
                  <template #header>
                    <button type="button" class="review-sort-header" @click="toggleTrashSort('deleted_at')">
                      刪除時間
                      <i class="review-sort-icon" :class="getTrashSortHeaderIcon('deleted_at')" aria-hidden="true"></i>
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
                      <i class="review-sort-icon" :class="getTrashSortHeaderIcon('type')" aria-hidden="true"></i>
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
                      <i class="review-sort-icon" :class="getTrashSortHeaderIcon('name')" aria-hidden="true"></i>
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
                      <i class="review-sort-icon" :class="getTrashSortHeaderIcon('status')" aria-hidden="true"></i>
                    </button>
                  </template>
                  <template #body="{ data }">
                    <Tag
                      :class="['review-status-chip', getSubmissionStatusClass(data.status)]"
                      :severity="getTrashStatusSeverity(data.status)"
                    >
                      {{ getTrashStatusLabel(data.status) }}
                    </Tag>
                  </template>
                </Column>
                <Column field="deleted_by_name">
                  <template #header>
                    <button type="button" class="review-sort-header" @click="toggleTrashSort('deleted_by')">
                      刪除者
                      <i class="review-sort-icon" :class="getTrashSortHeaderIcon('deleted_by')" aria-hidden="true"></i>
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
                        :class="['trash-dependency-chip', getTrashDependencyChipClass(dependency)]"
                      >
                        {{ dependency.label }}
                      </Tag>
                      <span v-if="!getTrashDependencies(data).length" class="trash-dependency-chip trash-dependency-chip--clear">無阻擋</span>
                    </div>
                  </template>
                </Column>
                <Column header="操作">
                  <template #body="{ data }">
                    <div class="admin-card-actions">
                      <Button
                        v-if="canRestoreTrashItem(data)"
                        icon="pi pi-undo"
                        label="還原"
                        size="small"
                        severity="success"
                        outlined
                        @click="confirmRestoreTrashItem(data)"
                      />
                      <Button
                        v-if="canPermanentDeleteTrashItem(data)"
                        icon="pi pi-trash"
                        label="永久刪除"
                        size="small"
                        severity="danger"
                        text
                        @click="confirmPermanentDeleteTrashItem(data)"
                      />
                      <span
                        v-if="!canRestoreTrashItem(data) && !canPermanentDeleteTrashItem(data)"
                        class="text-xs text-500"
                      >
                        目前無可用操作
                      </span>
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
          <div class="flex flex-column gap-2">
            <label>分類標籤顏色</label>
            <div class="category-color-options" role="radiogroup" aria-label="分類標籤顏色">
              <button
                v-for="option in categoryBadgeColorOptions"
                :key="option.value"
                type="button"
                class="category-color-option"
                :class="[
                  getCategoryBadgeClass({ badge_color: option.value }),
                  { 'is-selected': categoryForm.badge_color === option.value },
                ]"
                role="radio"
                :aria-checked="categoryForm.badge_color === option.value"
                @click="categoryForm.badge_color = option.value"
              >
                {{ option.label }}
              </button>
            </div>
            <div class="category-badge-preview">
              <span>預覽</span>
              <Tag severity="secondary" :class="getCategoryBadgeClass(categoryForm)">
                {{ categoryForm.label || categoryForm.name || '分類標籤' }}
              </Tag>
            </div>
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
          <div class="comparison-basis mb-2">
            {{ getComparisonBasisText(selectedArchiveRequest) }}
          </div>
          <div v-if="comparisonLoading" class="text-sm text-500">載入中...</div>
          <div v-else-if="comparisonArchives.length === 0" class="text-sm text-500">
            沒有找到同課程、同教師、同學期、同考試名稱的其他投稿。
          </div>
          <DataTable
            v-else
            :value="comparisonArchives"
            tableStyle="min-width: 36rem"
            responsiveLayout="stack"
            breakpoint="768px"
          >
            <Column header="投稿編號">
              <template #body="{ data }">{{ formatComparisonSubmissionId(data) }}</template>
            </Column>
            <Column field="has_answers" header="解答">
              <template #body="{ data }">{{ data.has_answers ? '有' : '無' }}</template>
            </Column>
            <Column header="狀態">
              <template #body="{ data }">
                <Tag
                  :class="['review-status-chip', getSubmissionStatusClass(data.status)]"
                  :severity="getSubmissionSeverity(data.status)"
                >
                  {{ getSubmissionLabel(data.status) }}
                </Tag>
              </template>
            </Column>
            <Column header="投稿帳號">
              <template #body="{ data }">{{ getRequesterDisplay(data) }}</template>
            </Column>
            <Column header="操作" style="width: 14rem">
              <template #body="{ data }">
                <div class="comparison-row-actions">
                  <Button
                    label="並排預覽"
                    icon="pi pi-columns"
                    size="small"
                    outlined
                    :loading="comparePreviewLoading && comparePreviewArchive?.id === data.id"
                    @click="openComparePreview(data)"
                  />
                  <Button
                    v-if="canTakedownComparisonItem(data)"
                    label="下架"
                    icon="pi pi-eye-slash"
                    size="small"
                    severity="secondary"
                    outlined
                    @click="confirmTakedownComparisonItem(data)"
                  />
                </div>
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
        :visible="showResetPasswordDialog"
        @update:visible="showResetPasswordDialog = $event"
        @hide="closeResetPasswordDialog"
        :modal="true"
        :draggable="false"
        :closeOnEscape="false"
        header="重設密碼"
        :style="{ width: '460px', maxWidth: '92vw' }"
        :autoFocus="false"
      >
        <div class="flex flex-column gap-3">
          <div class="flex flex-column gap-1">
            <label class="font-semibold">使用者</label>
            <div class="text-sm">
              {{ getResetPasswordTargetLabel(resetPasswordUser) }}
              <span v-if="resetPasswordUser?.email" class="text-500">（{{ resetPasswordUser.email }}）</span>
            </div>
          </div>

          <div class="flex flex-column gap-2">
            <label>新密碼</label>
            <Password
              v-model="resetPasswordForm.newPassword"
              placeholder="輸入新密碼"
              class="w-full"
              inputClass="w-full"
              :class="{ 'p-invalid': resetPasswordFormErrors.newPassword }"
              toggleMask
              :feedback="false"
              :maxlength="128"
            />
            <small v-if="resetPasswordFormErrors.newPassword" class="p-error">
              {{ resetPasswordFormErrors.newPassword }}
            </small>
          </div>

          <div class="flex flex-column gap-2">
            <label>確認新密碼</label>
            <Password
              v-model="resetPasswordForm.confirmPassword"
              placeholder="再次輸入新密碼"
              class="w-full"
              inputClass="w-full"
              :class="{ 'p-invalid': resetPasswordFormErrors.confirmPassword }"
              toggleMask
              :feedback="false"
              :maxlength="128"
            />
            <small v-if="resetPasswordFormErrors.confirmPassword" class="p-error">
              {{ resetPasswordFormErrors.confirmPassword }}
            </small>
          </div>
        </div>

        <div class="flex pt-6 justify-end gap-2.5">
          <Button label="取消" icon="pi pi-times" severity="secondary" @click="closeResetPasswordDialog" />
          <Button
            label="確認重設"
            icon="pi pi-key"
            severity="success"
            @click="resetPassword"
            :loading="resetPasswordLoading"
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
        :style="{ width: '44rem', maxWidth: '92vw' }"
      >
        <div class="trash-dependency-help">
          <p class="trash-dependency-help-intro">
            這一欄會告訴你：能不能還原、能不能永久刪除，以及哪些資料會一起處理。
          </p>

          <section class="trash-dependency-help-section">
            <h4 class="trash-dependency-help-title">快速判斷</h4>
            <div class="trash-dependency-help-label-grid">
              <article class="trash-dependency-help-label-card">
                <span class="trash-dependency-help-chip trash-dependency-chip--restore-blocked">阻擋還原</span>
                <p>現在不能還原。通常要先復原父層，或必要關聯已不存在。</p>
              </article>
              <article class="trash-dependency-help-label-card">
                <span class="trash-dependency-help-chip trash-dependency-chip--delete-blocked">阻擋永久刪除</span>
                <p>現在不能永久刪除。通常仍有啟用中的資料依附。</p>
              </article>
              <article class="trash-dependency-help-label-card">
                <span class="trash-dependency-help-chip trash-dependency-chip--cascade">一併永久刪除</span>
                <p>刪除此項時，列出的資料會一起永久刪除。</p>
              </article>
              <article class="trash-dependency-help-label-card">
                <span class="trash-dependency-help-chip trash-dependency-chip--relation">關聯</span>
                <p>只是提醒資料有關，通常不會直接阻擋。</p>
              </article>
              <article class="trash-dependency-help-label-card">
                <span class="trash-dependency-help-chip trash-dependency-chip--clear">無阻擋</span>
                <p>目前沒有影響還原或永久刪除的限制。</p>
              </article>
            </div>
          </section>

          <section class="trash-dependency-help-section">
            <h4 class="trash-dependency-help-title">按鈕規則</h4>
            <div class="trash-dependency-help-rule-list">
              <p><span aria-hidden="true">-</span> 有「阻擋還原」 → 不顯示還原。</p>
              <p><span aria-hidden="true">-</span> 有「阻擋永久刪除」 → 不顯示永久刪除。</p>
              <p><span aria-hidden="true">-</span> 只有「一併永久刪除」或「關聯」 → 按鈕不會自動隱藏。</p>
            </div>
          </section>

          <section class="trash-dependency-help-section">
            <h4 class="trash-dependency-help-title">縮排怎麼看</h4>
            <div class="trash-dependency-help-rule-list">
              <p><span aria-hidden="true">-</span> 只有「已在垃圾桶」的項目會出現在縮排中。</p>
              <p><span aria-hidden="true">-</span> 只是暫時下架的投稿，仍留在審核中心，不會出現在垃圾桶縮排。</p>
            </div>
            <p class="trash-dependency-help-note">縮排只代表目前垃圾桶中的父子關係，不代表所有歷史關聯都會出現。</p>
          </section>

          <section class="trash-dependency-help-section">
            <h4 class="trash-dependency-help-title">兩種常見流程</h4>
            <div class="trash-dependency-help-flow-grid">
              <article class="trash-dependency-help-flow-card">
                <h5>先刪投稿，再刪課程 / 分類</h5>
                <div class="trash-dependency-help-flow" aria-label="課程分類 到 課程 到 考古題投稿 到 考古題">
                  <span>課程分類</span>
                  <i aria-hidden="true">→</i>
                  <span>課程</span>
                  <i aria-hidden="true">→</i>
                  <span>考古題投稿</span>
                  <i aria-hidden="true">→</i>
                  <span>考古題</span>
                </div>
                <p>投稿已從審核中心按「刪除」，所以投稿本身也是垃圾桶項目。關聯考古題會列在投稿底下。</p>
              </article>
              <article class="trash-dependency-help-flow-card">
                <h5>直接刪課程 / 分類</h5>
                <div class="trash-dependency-help-flow" aria-label="課程分類 到 課程 到 考古題">
                  <span>課程分類</span>
                  <i aria-hidden="true">→</i>
                  <span>課程</span>
                  <i aria-hidden="true">→</i>
                  <span>考古題</span>
                </div>
                <p>投稿只是因原課程刪除而暫時下架，仍留在審核中心，所以不會出現在垃圾桶縮排。</p>
                <div class="trash-dependency-help-note">
                  <p>若之後永久刪除此課程，底下考古題會一併永久刪除。</p>
                  <p>相關投稿會進入垃圾桶並標示無法復原。</p>
                  <p>因父層課程與考古題已不存在，投稿會以獨立項目顯示。</p>
                </div>
              </article>
            </div>
          </section>

          <section class="trash-dependency-help-section">
            <h4 class="trash-dependency-help-title">考古題與投稿</h4>
            <div class="trash-dependency-help-rule-list">
              <p><span aria-hidden="true">-</span> 刪除投稿：投稿進垃圾桶，關聯考古題也會被帶入。</p>
              <p><span aria-hidden="true">-</span> 刪除考古題：考古題進垃圾桶，相關投稿通常只會暫時下架。</p>
              <p><span aria-hidden="true">-</span> 考古題顯示在投稿底下時，通常要先還原投稿。</p>
            </div>
          </section>

          <section class="trash-dependency-help-section">
            <h4 class="trash-dependency-help-title">課程、分類與留言</h4>
            <div class="trash-dependency-help-rule-list">
              <p><span aria-hidden="true">-</span> 刪除課程：課程與下轄考古題會進垃圾桶，相關投稿會暫時下架。</p>
              <p><span aria-hidden="true">-</span> 復原課程：只復原因課程刪除而進垃圾桶的考古題；因刪投稿而進垃圾桶的考古題仍需還原投稿。</p>
              <p><span aria-hidden="true">-</span> 復原分類：只復原分類本身，不會自動復原課程。</p>
              <p><span aria-hidden="true">-</span> 留言：不再阻擋考古題永久刪除，會隨考古題一併永久刪除。</p>
            </div>
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
  resetUserPassword,
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
  badge_color: 'slate',
})
const categoryFormErrors = ref({})
const DEFAULT_CATEGORY_BADGE_COLOR = 'slate'
const categoryBadgeColorOptions = [
  { label: '深藍', value: 'navy' },
  { label: '青綠', value: 'teal' },
  { label: '森綠', value: 'forest' },
  { label: '琥珀', value: 'amber' },
  { label: '酒紅', value: 'burgundy' },
  { label: '紫色', value: 'violet' },
  { label: '灰色', value: 'slate' },
  { label: '靛藍', value: 'indigo' },
]
const categoryBadgeColorValues = new Set(categoryBadgeColorOptions.map((option) => option.value))
const legacyCategoryBadgeColorMap = {
  blue: 'navy',
  green: 'forest',
  purple: 'violet',
  rose: 'burgundy',
  gray: 'slate',
}
const users = ref([])
const usersLoading = ref(false)
const userSearchQuery = ref('')
const filterUserType = ref(null)

const userSortMeta = ref([
  { field: 'is_admin', order: -1 },
  { field: 'name', order: 1 },
])
const USER_PASSWORD_MIN_LENGTH = 8
const NON_LOCAL_PASSWORD_RESET_HINT = '此帳號不是本地帳號，無法由系統重設密碼。'

const getResetPasswordTargetLabel = (user) => {
  return user?.name || user?.email || '該使用者'
}

const getOnlineStatusLabel = (user) => {
  if (user?.online_status_label) {
    return user.online_status_label
  }

  if (user?.is_online === true) {
    return '在線'
  }

  if (!user || !user.last_login_at) {
    return '從未登入'
  }

  return '離線'
}

const getOnlineStatusDotClass = (user) => {
  return user?.is_online ? 'user-online-dot--online' : 'user-online-dot--offline'
}

const showUserDialog = ref(false)
const editingUser = ref(null)
const userSaveLoading = ref(false)

const showResetPasswordDialog = ref(false)
const resetPasswordUser = ref(null)
const resetPasswordLoading = ref(false)
const resetPasswordForm = ref({
  newPassword: "",
  confirmPassword: "",
})
const resetPasswordFormErrors = ref({})


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
const showTrashRelationHierarchy = ref(true)
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
const getReviewSortDirectionIcon = (direction) => (direction === 'asc' ? 'pi pi-sort-amount-up-alt' : 'pi pi-sort-amount-down')
const getReviewSortNeutralIcon = () => 'pi pi-sort-alt'
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
      return
    }
    showTrashRelationHierarchy.value = true
    trashSortState.value = { key: null, direction: 'asc' }
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

const getTrashRowClass = (item) => {
  if (!isTrashRelationHierarchyEnabled.value) return ''
  const groupIndex = item?.trash_relation_group_index
  const groupSize = Number(item?.trash_relation_group_size || 0)
  if (groupIndex === null || groupIndex === undefined || groupSize <= 1) return ''
  const bandClass = Number(groupIndex) % 2 === 0
    ? 'trash-row--relation-group-even'
    : 'trash-row--relation-group-odd'
  return `trash-row--relation-group ${bandClass}`
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
      trash_relation_group_index: null,
      trash_relation_group_size: 1,
    }))
    .sort((a, b) => getTrashDeletedTimestamp(b) - getTrashDeletedTimestamp(a))

  if (normalizedFilterType !== null && normalizedFilterType !== undefined) {
    return rows
      .sort((a, b) => getTrashDeletedTimestamp(b) - getTrashDeletedTimestamp(a))
      .map((item) => ({
        ...item,
        trash_depth: 0,
        trash_relation_group_index: null,
        trash_relation_group_size: 1,
      }))
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

  const countSubtree = (node, seen = new Set()) => {
    const key = getTrashItemKey(node, node._trashRowIndex)
    if (seen.has(key)) return 0
    seen.add(key)
    const children = childrenMap.get(key) || []
    return 1 + children.reduce((total, child) => total + countSubtree(child, seen), 0)
  }

  const walk = (node, depth, relationGroupIndex = null, relationGroupSize = 1) => {
    const key = getTrashItemKey(node, node._trashRowIndex)
    if (visited.has(key)) return
    visited.add(key)

    result.push({
      ...node,
      trash_depth: depth,
      trash_relation_group_index: relationGroupIndex,
      trash_relation_group_size: relationGroupSize,
    })
    const children = childrenMap.get(key) || []
    for (const child of children) {
      walk(child, depth + 1, relationGroupIndex, relationGroupSize)
    }
  }
  let nextRelationGroupIndex = 0
  for (const root of roots) {
    const relationGroupSize = countSubtree(root)
    const relationGroupIndex = relationGroupSize > 1 ? nextRelationGroupIndex++ : null
    walk(root, 0, relationGroupIndex, relationGroupSize)
  }

  if (!result.length && rows.length) {
    return rows.map((item) => ({
      ...item,
      trash_depth: 0,
      trash_relation_group_index: null,
      trash_relation_group_size: 1,
    }))
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

const normalizeCategoryBadgeColor = (color) => {
  const value = (color || DEFAULT_CATEGORY_BADGE_COLOR).toString().trim().toLowerCase()
  const mappedValue = legacyCategoryBadgeColorMap[value] || value
  return categoryBadgeColorValues.has(mappedValue) ? mappedValue : DEFAULT_CATEGORY_BADGE_COLOR
}

const getCategoryBadgeColor = (category) => {
  if (typeof category === 'string') {
    return normalizeCategoryBadgeColor(categoryInfoMap.value[category]?.badge_color)
  }
  return normalizeCategoryBadgeColor(category?.badge_color)
}

const getCategoryBadgeClass = (category) => {
  return `category-badge category-badge--${getCategoryBadgeColor(category)}`
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

const getReviewTrashNote = (item, fullText = false) => {
  const status = getReviewItemStatus(item)
  if (!['takedown', 'deleted'].includes(status)) return ''
  if (item?.lifecycle_reason === 'linked_archive_permanently_deleted') return '無法復原：關聯考古題已永久刪除。'
  if (isCourseTrashLifecycleReason(item?.lifecycle_reason) || item?.linked_course_deleted === true) {
    if (status === 'deleted') {
      const shortText = '原課程在垃圾桶，請至垃圾桶處理。'
      const fullTextMessage =
        '此投稿已刪除；其原課程仍在垃圾桶，請到垃圾桶查看關聯項目。'
      return fullText ? fullTextMessage : shortText
    }
    const shortText = '原課程在垃圾桶，復原後會回到原狀。'
    const fullTextMessage =
      '原課程已在垃圾桶，此投稿暫時下架。請先到垃圾桶復原原課程，復原後會回到原本狀態。'
    return fullText ? fullTextMessage : shortText
  }
  if (item?.lifecycle_reason === 'archive_trashed' || item?.linked_archive_deleted === true) {
    return '關聯考古題在垃圾桶，請先復原考古題。'
  }
  return ''
}

const isReviewTrashWarningNote = (item) => {
  const note = getReviewTrashNote(item)
  return note.includes('無法復原') || note.includes('永久刪除')
}

const getReviewTrashNoteClass = (item) => {
  return isReviewTrashWarningNote(item)
    ? 'review-card-action-note--warning'
    : 'review-card-action-note--info'
}

const getReviewTrashNoteIcon = (item) => {
  return isReviewTrashWarningNote(item) ? 'pi pi-exclamation-circle' : 'pi pi-info-circle'
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
    const isDefaultFilter = filterType === null
    showTrashRelationHierarchy.value = isDefaultFilter
    if (isDefaultFilter) {
      trashSortState.value = { key: null, direction: 'asc' }
    }
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
    .filter((dependency) => String(dependency?.label || '').trim())
    .sort((a, b) => {
      if (a.restoreBlocking !== b.restoreBlocking) {
        return a.restoreBlocking ? -1 : 1
      }
      if (a.deleteBlocking !== b.deleteBlocking) {
        return a.deleteBlocking ? -1 : 1
      }
      if (a.kindOrder !== b.kindOrder) {
        return a.kindOrder - b.kindOrder
      }
      return a.label.localeCompare(b.label)
    })
}

const canRestoreTrashItem = (item) => {
  if (item?.canRestore === false) return false
  if (item?.canRestore === true) return true
  return !getTrashDependencyHasRestoreBlocker(item)
}

const canPermanentDeleteTrashItem = (item) => {
  if (item?.canPermanentDelete === false) return false
  if (item?.canPermanentDelete === true) return true
  return !getTrashDependencyHasPermanentDeleteBlocker(item)
}

const getTrashDependencyHasRestoreBlocker = (item) => {
  return getTrashDependencies(item).some((dependency) =>
    String(dependency?.label || '').startsWith('阻擋還原：'),
  )
}

const getTrashDependencyHasPermanentDeleteBlocker = (item) => {
  return getTrashDependencies(item).some((dependency) =>
    String(dependency?.label || '').startsWith('阻擋永久刪除：'),
  )
}

const getTrashDependencySeverity = (dependency) => {
  return dependency?.severity || 'secondary'
}

const getTrashDependencyChipClass = (dependency) => {
  const label = String(dependency?.label || '')
  if (dependency?.restoreBlocking || label.startsWith('阻擋還原：')) return 'trash-dependency-chip--restore-blocked'
  if (dependency?.deleteBlocking || label.startsWith('阻擋永久刪除：')) return 'trash-dependency-chip--delete-blocked'
  if (label.startsWith('一併永久刪除：')) return 'trash-dependency-chip--cascade'
  if (label === '無阻擋') return 'trash-dependency-chip--clear'
  return 'trash-dependency-chip--relation'
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
        deleteBlocking: true,
        restoreBlocking: false,
        kindOrder: 1,
      }
    }

    if (['trashed', 'deleted', 'soft_deleted'].includes(normalizedKind)) {
      const label = typeLabel || getFallbackRelationLabel(typeRaw, 'trashed', itemType)
      return {
        key: `trashed-${typeRaw || 'dependency'}-${count}`,
        label: `一併永久刪除：${applyDependencyCount(label, count)}`,
        severity: 'info',
        blocking: false,
        restoreBlocking: false,
        deleteBlocking: false,
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
      restoreBlocking: false,
      deleteBlocking: true,
      kindOrder: 1,
    }
  }

  if (raw.startsWith('阻擋還原：')) {
    return {
      key: `restore-blocking-${raw}`,
      label: raw,
      severity: 'warning',
      blocking: true,
      restoreBlocking: true,
      deleteBlocking: false,
      kindOrder: 0,
    }
  }

  if (raw.startsWith('無法復原：')) {
    return {
      key: `restore-blocking-${raw}`,
      label: `阻擋還原：${raw.replace('無法復原：', '')}`,
      severity: 'warning',
      blocking: true,
      restoreBlocking: true,
      deleteBlocking: false,
      kindOrder: 0,
    }
  }

  if (raw.startsWith('一併永久刪除：')) {
    return {
      key: `trashed-${raw}`,
      label: raw,
      severity: 'info',
      blocking: false,
      restoreBlocking: false,
      deleteBlocking: false,
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
      restoreBlocking: false,
      deleteBlocking: false,
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
        restoreBlocking: false,
        deleteBlocking: false,
        kindOrder: 2,
      }
    }
    if (isTrashed) {
      return {
        key: `relation-${raw}`,
        label: '一併永久刪除：關聯考古題已刪除',
        severity: 'info',
        blocking: false,
        restoreBlocking: false,
        deleteBlocking: false,
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
      restoreBlocking: false,
      deleteBlocking: false,
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
      restoreBlocking: false,
      deleteBlocking: true,
      kindOrder: 1,
    }
  }

  if (isTrashed) {
    return {
      key: `trashed-${raw}`,
      label: `一併永久刪除：${cascadeLabel}`,
      severity: 'info',
      blocking: false,
      restoreBlocking: false,
      deleteBlocking: false,
      kindOrder: 1,
    }
  }

  return {
    key: `relation-${raw}`,
    label: `關聯：${relationLabel}${count ? ` ${count} 筆` : ''}`,
    severity: 'secondary',
    blocking: false,
    restoreBlocking: false,
    deleteBlocking: false,
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
    const { data } = await archiveService.restoreTrashItem(item.item_type, item.id)
    toast.add({
      severity: 'success',
      summary: '已還原',
      detail: data?.message || '項目已還原',
      life: 3500,
    })
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

const openComparePreview = async (comparison) => {
  if (!selectedArchiveRequest.value?.id || !comparison?.id) return
  comparePreviewArchive.value = comparison
  comparePreviewLoading.value = true
  comparePreviewError.value = false
  revokeComparePreviewUrls()
  showComparePreview.value = true

  try {
    const [requestResponse, comparisonResponse] = await Promise.all([
      archiveService.getSubmissionPreviewFile(selectedArchiveRequest.value.id),
      archiveService.getSubmissionPreviewFile(comparison.id),
    ])
    compareRequestPreviewUrl.value = URL.createObjectURL(
      new Blob([requestResponse.data], { type: 'application/pdf' })
    )
    compareArchivePreviewUrl.value = URL.createObjectURL(
      new Blob([comparisonResponse.data], { type: 'application/pdf' })
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
  if (!request?.id) return

  comparisonLoading.value = true
  try {
    const { data } = await archiveService.listSubmissionComparisons(request.id)
    comparisonArchives.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('載入比對資料失敗:', error)
    if (isUnauthorizedError(error)) return
    toast.add({ severity: 'error', summary: '錯誤', detail: '比對資料載入失敗', life: 3000 })
  } finally {
    comparisonLoading.value = false
  }
}

const getComparisonBasisText = (item) => {
  const course = item?.requested_course_name || item?.subject || '—'
  const exam = item?.name || '—'
  const professor = item?.professor || '—'
  const semester = formatAcademicTerm(item?.academic_year) || '—'
  return `比對基準：課程 ${course}｜考試 ${exam}｜教師 ${professor}｜學期 ${semester}`
}

const formatComparisonSubmissionId = (item) => {
  return item?.id ? `#${item.id}` : '—'
}

const canTakedownComparisonItem = (item) => {
  return item?.can_takedown === true && ['pending', 'approved'].includes(normalizeSubmissionStatus(item?.status))
}

const confirmTakedownComparisonItem = (item) => {
  if (!canTakedownComparisonItem(item) || !item?.id) return
  confirm.require({
    message: '確定要下架這筆比對項目嗎？',
    header: '確認下架',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: '下架',
    rejectLabel: '取消',
    accept: () => takedownComparisonItem(item),
  })
}

const takedownComparisonItem = async (item) => {
  if (!item?.id) return
  try {
    await archiveService.takedownSubmission(item.id)
    toast.add({ severity: 'success', summary: '完成', detail: '已下架', life: 3000 })
    await loadReviewItems()
    await loadArchiveComparison(selectedArchiveRequest.value)
  } catch (error) {
    console.error('下架比對項目失敗:', error)
    if (isUnauthorizedError(error)) return
    toast.add({ severity: 'error', summary: '錯誤', detail: getTrashErrorMessage(error, '下架比對項目失敗'), life: 3000 })
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
    badge_color: DEFAULT_CATEGORY_BADGE_COLOR,
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
    badge_color: getCategoryBadgeColor(category),
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
    badge_color: DEFAULT_CATEGORY_BADGE_COLOR,
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
      badge_color: getCategoryBadgeColor(categoryForm.value),
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


const closeResetPasswordDialog = () => {
  showResetPasswordDialog.value = false
  resetPasswordUser.value = null
  resetPasswordForm.value = {
    newPassword: '',
    confirmPassword: '',
  }
  resetPasswordFormErrors.value = {}
  resetPasswordLoading.value = false
}

const openResetPasswordDialog = (user) => {
  if (!user?.is_local) return

  resetPasswordUser.value = user
  resetPasswordForm.value = {
    newPassword: '',
    confirmPassword: '',
  }
  resetPasswordFormErrors.value = {}
  showResetPasswordDialog.value = true
}

const validateResetPasswordForm = () => {
  const errors = {}
  const newPassword = (resetPasswordForm.value.newPassword || '').trim()
  const confirmPassword = (resetPasswordForm.value.confirmPassword || '').trim()

  if (!newPassword) {
    errors.newPassword = '新密碼是必填欄位'
  } else if (newPassword.length < USER_PASSWORD_MIN_LENGTH) {
    errors.newPassword = `新密碼至少 ${USER_PASSWORD_MIN_LENGTH} 字`
  }

  if (!confirmPassword) {
    errors.confirmPassword = '請再次輸入新密碼'
  } else if (confirmPassword !== newPassword) {
    errors.confirmPassword = '兩次輸入的密碼不一致'
  }

  resetPasswordFormErrors.value = errors
  return Object.keys(errors).length === 0
}

const resetPassword = async () => {
  if (!validateResetPasswordForm()) return
  if (!resetPasswordUser.value?.is_local || !resetPasswordUser.value?.id) return

  resetPasswordLoading.value = true
  try {
    const payload = {
      new_password: (resetPasswordForm.value.newPassword || '').trim(),
    }

    await resetUserPassword(resetPasswordUser.value.id, payload)

    toast.add({
      severity: 'success',
      summary: '成功',
      detail: `使用者 ${getResetPasswordTargetLabel(resetPasswordUser.value)} 的密碼已更新。`,
      life: 3000,
    })

    closeResetPasswordDialog()
    await loadUsers()
  } catch (error) {
    console.error('重設密碼失敗:', error)
    if (isUnauthorizedError(error)) {
      return
    }
    toast.add({
      severity: 'error',
      summary: '錯誤',
      detail: `重設密碼失敗：${error?.response?.data?.detail || '請稍後再試'}`,
      life: 3500,
    })
  } finally {
    resetPasswordLoading.value = false
  }
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

.comparison-basis {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.comparison-row-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
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

.review-row-action-area {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  align-items: flex-start;
  min-width: 0;
}

.review-sort-icon {
  font-size: 0.8rem;
  line-height: 1;
  opacity: 0.8;
  color: var(--text-color-secondary);
}

.review-card-action-note {
  display: inline-flex;
  align-items: flex-start;
  gap: 0.35rem;
  margin: 0.15rem 0 0;
  width: 100%;
  max-width: min(18rem, 100%);
  min-width: 0;
  padding: 0.35rem 0.5rem;
  border: 1px solid var(--border-color);
  border-left-width: 3px;
  border-radius: 6px;
  background: color-mix(in srgb, var(--surface-ground) 55%, transparent);
  color: var(--text-color-secondary);
  font-size: 0.76rem;
  line-height: 1.35;
  white-space: normal;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.review-card-action-note .pi {
  flex: 0 0 auto;
  flex-shrink: 0;
  margin-top: 0.08rem;
  font-size: 0.78rem;
}

.review-card-action-note span {
  min-width: 0;
  white-space: normal;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.review-card-action-note__text {
  min-width: 0;
  white-space: normal;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.review-card-action-note--info {
  border-color: #8aa1b8;
  border-left-color: #3d647e;
  background: #eef3f6;
  color: #344b5d;
}

.review-card-action-note--warning {
  border-color: #c99a61;
  border-left-color: #9a5f23;
  background: #f6eee3;
  color: #694018;
}

:global(.dark) .review-card-action-note--info,
:global(.dark) :deep(.review-card-action-note--info) {
  border-color: rgba(138, 161, 184, 0.44);
  border-left-color: rgba(126, 169, 196, 0.72);
  background: rgba(61, 100, 126, 0.18);
  color: #c7d3dd;
}

:global(.dark) .review-card-action-note--warning,
:global(.dark) :deep(.review-card-action-note--warning) {
  border-color: rgba(201, 154, 97, 0.46);
  border-left-color: rgba(225, 171, 95, 0.76);
  background: rgba(154, 95, 35, 0.18);
  color: #ead4b8;
}

.review-sort-icon.pi-sort-amount-up-alt,
.review-sort-icon.pi-sort-amount-down {
  color: var(--primary-color);
  opacity: 1;
}

.review-course-cell {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  flex-wrap: wrap;
}

.category-color-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(5.5rem, 1fr));
  gap: 0.5rem;
}

.category-color-option {
  border-radius: 999px;
  padding: 0.4rem 0.65rem;
  cursor: pointer;
  transition:
    outline-color 0.15s ease,
    transform 0.15s ease;
}

.category-color-option:hover {
  transform: translateY(-1px);
}

.category-color-option.is-selected {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}

.category-badge-preview {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  color: var(--text-secondary);
  font-size: 0.86rem;
}

.category-color-option.category-badge,
:deep(.category-badge) {
  border: 1px solid transparent;
  font-weight: 700;
  letter-spacing: 0;
  line-height: 1.25;
  max-width: 100%;
  white-space: normal;
}

.category-color-option.category-badge--navy,
:deep(.category-badge--navy) {
  background: #dbe4f0;
  border-color: #475f83;
  color: #1f3a5f;
}

.category-color-option.category-badge--teal,
:deep(.category-badge--teal) {
  background: #d5ebe7;
  border-color: #2f766e;
  color: #175e58;
}

.category-color-option.category-badge--forest,
:deep(.category-badge--forest) {
  background: #dce8d8;
  border-color: #4f7a45;
  color: #315f2a;
}

.category-color-option.category-badge--amber,
:deep(.category-badge--amber) {
  background: #efe2c8;
  border-color: #9a6b24;
  color: #7a4d12;
}

.category-color-option.category-badge--burgundy,
:deep(.category-badge--burgundy) {
  background: #eed8dd;
  border-color: #8f3f50;
  color: #743041;
}

.category-color-option.category-badge--violet,
:deep(.category-badge--violet) {
  background: #e3dcef;
  border-color: #6d5599;
  color: #513f7d;
}

.category-color-option.category-badge--slate,
:deep(.category-badge--slate) {
  background: #dfe4ea;
  border-color: #64748b;
  color: #334155;
}

.category-color-option.category-badge--indigo,
:deep(.category-badge--indigo) {
  background: #dde1f2;
  border-color: #5262a3;
  color: #364381;
}

:global(.dark) .category-color-option.category-badge--navy,
:global(.dark) :deep(.category-badge--navy) {
  background: rgba(71, 95, 131, 0.28);
  border-color: rgba(125, 151, 190, 0.58);
  color: #c7d6ea;
}

:global(.dark) .category-color-option.category-badge--teal,
:global(.dark) :deep(.category-badge--teal) {
  background: rgba(45, 118, 110, 0.26);
  border-color: rgba(89, 170, 160, 0.52);
  color: #b7ded8;
}

:global(.dark) .category-color-option.category-badge--forest,
:global(.dark) :deep(.category-badge--forest) {
  background: rgba(79, 122, 69, 0.28);
  border-color: rgba(128, 174, 116, 0.52);
  color: #c2dfb9;
}

:global(.dark) .category-color-option.category-badge--amber,
:global(.dark) :deep(.category-badge--amber) {
  background: rgba(154, 107, 36, 0.28);
  border-color: rgba(199, 153, 78, 0.56);
  color: #ead2a3;
}

:global(.dark) .category-color-option.category-badge--burgundy,
:global(.dark) :deep(.category-badge--burgundy) {
  background: rgba(143, 63, 80, 0.28);
  border-color: rgba(194, 105, 122, 0.54);
  color: #e5bec8;
}

:global(.dark) .category-color-option.category-badge--violet,
:global(.dark) :deep(.category-badge--violet) {
  background: rgba(109, 85, 153, 0.28);
  border-color: rgba(159, 137, 199, 0.56);
  color: #d9cdef;
}

:global(.dark) .category-color-option.category-badge--slate,
:global(.dark) :deep(.category-badge--slate) {
  background: rgba(100, 116, 139, 0.26);
  border-color: rgba(148, 163, 184, 0.5);
  color: #d1d9e4;
}

:global(.dark) .category-color-option.category-badge--indigo,
:global(.dark) :deep(.category-badge--indigo) {
  background: rgba(82, 98, 163, 0.28);
  border-color: rgba(131, 146, 205, 0.56);
  color: #cfd6f1;
}

:deep(.review-admin-upload-chip) {
  background: #dbeafe;
  color: #1d4ed8;
  border-color: #3b82f6;
  font-weight: 700;
}

:global(.dark) :deep(.review-admin-upload-chip) {
  background: rgba(59, 130, 246, 0.22);
  color: #bfdbfe;
  border-color: rgba(96, 165, 250, 0.56);
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

:deep(.trash-table .p-datatable-tbody > tr.trash-row--relation-group-even) {
  --trash-relation-row-bg: rgba(16, 185, 129, 0.055);
}

:deep(.trash-table .p-datatable-tbody > tr.trash-row--relation-group-odd) {
  --trash-relation-row-bg: rgba(59, 130, 246, 0.045);
}

:deep(.trash-table .p-datatable-tbody > tr.trash-row--relation-group) {
  background: var(--trash-relation-row-bg);
}

:deep(.trash-table .p-datatable-tbody > tr.trash-row--relation-group > td) {
  background: var(--trash-relation-row-bg);
}

:deep(.trash-table .p-datatable-tbody > tr.trash-row--relation-group:hover > td) {
  background: color-mix(in srgb, var(--trash-relation-row-bg) 72%, var(--bg-secondary) 28%);
}

.trash-dependency-help {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-height: min(70vh, 44rem);
  overflow-y: auto;
  padding-right: 0.2rem;
  font-size: 0.92rem;
}

.trash-dependency-help-intro {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.55;
}

.trash-dependency-help-section {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 0.75rem 0.85rem;
  background: color-mix(in srgb, var(--surface-card) 90%, transparent);
}

.trash-dependency-help-title {
  margin: 0 0 0.55rem 0;
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-color);
}

.trash-dependency-help-label-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(12rem, 1fr));
  gap: 0.55rem;
}

.trash-dependency-help-label-card,
.trash-dependency-help-flow-card {
  border: 1px solid color-mix(in srgb, var(--border-color) 72%, transparent);
  border-radius: 8px;
  background: color-mix(in srgb, var(--surface-ground) 42%, transparent);
}

.trash-dependency-help-label-card {
  padding: 0.6rem;
}

.trash-dependency-help-label-card p,
.trash-dependency-help-flow-card p,
.trash-dependency-help-rule-list p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.trash-dependency-help-label-card p {
  margin-top: 0.4rem;
  font-size: 0.86rem;
}

.trash-dependency-chip,
.trash-dependency-help-chip,
:deep(.trash-dependency-chip) {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  max-width: 100%;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  padding: 0.15rem 0.5rem;
  font-size: 0.78rem;
  font-weight: 700;
  line-height: 1.35;
  overflow-wrap: anywhere;
}

.trash-dependency-chip--restore-blocked,
:deep(.trash-dependency-chip--restore-blocked) {
  background: #fef3c7;
  border-color: #f59e0b;
  color: #92400e;
}

.trash-dependency-chip--delete-blocked,
:deep(.trash-dependency-chip--delete-blocked) {
  background: #fee2e2;
  border-color: #ef4444;
  color: #991b1b;
}

.trash-dependency-chip--cascade,
:deep(.trash-dependency-chip--cascade) {
  background: #dbeafe;
  border-color: #3b82f6;
  color: #1d4ed8;
}

.trash-dependency-chip--relation,
:deep(.trash-dependency-chip--relation) {
  background: #e2e8f0;
  border-color: #64748b;
  color: #334155;
}

.trash-dependency-chip--clear,
:deep(.trash-dependency-chip--clear) {
  background: #dcfce7;
  border-color: #22c55e;
  color: #166534;
}

:global(.dark) .trash-dependency-chip--restore-blocked,
:global(.dark) :deep(.trash-dependency-chip--restore-blocked) {
  background: rgba(245, 158, 11, 0.22);
  border-color: rgba(251, 191, 36, 0.55);
  color: #fcd34d;
}

:global(.dark) .trash-dependency-chip--delete-blocked,
:global(.dark) :deep(.trash-dependency-chip--delete-blocked) {
  background: rgba(239, 68, 68, 0.2);
  border-color: rgba(248, 113, 113, 0.54);
  color: #fca5a5;
}

:global(.dark) .trash-dependency-chip--cascade,
:global(.dark) :deep(.trash-dependency-chip--cascade) {
  background: rgba(59, 130, 246, 0.2);
  border-color: rgba(96, 165, 250, 0.54);
  color: #bfdbfe;
}

:global(.dark) .trash-dependency-chip--relation,
:global(.dark) :deep(.trash-dependency-chip--relation) {
  background: rgba(100, 116, 139, 0.24);
  border-color: rgba(148, 163, 184, 0.5);
  color: #cbd5e1;
}

:global(.dark) .trash-dependency-chip--clear,
:global(.dark) :deep(.trash-dependency-chip--clear) {
  background: rgba(34, 197, 94, 0.2);
  border-color: rgba(74, 222, 128, 0.52);
  color: #86efac;
}

.trash-dependency-help-rule-list {
  display: grid;
  gap: 0.35rem;
}

.trash-dependency-help-rule-list p {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 0.45rem;
  overflow-wrap: anywhere;
}

.trash-dependency-help-rule-list span {
  color: var(--primary-color);
  font-weight: 700;
}

.trash-dependency-help-flow-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(15rem, 1fr));
  gap: 0.65rem;
}

.trash-dependency-help-flow-card {
  padding: 0.7rem;
}

.trash-dependency-help-flow-card h5 {
  margin: 0 0 0.5rem;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-color);
}

.trash-dependency-help-flow-card p {
  margin-top: 0.55rem;
  font-size: 0.86rem;
}

.trash-dependency-help-flow {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.28rem;
  border: 1px dashed color-mix(in srgb, var(--border-color) 72%, transparent);
  border-radius: 8px;
  padding: 0.45rem;
  background: color-mix(in srgb, var(--surface-card) 72%, transparent);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}

.trash-dependency-help-flow span {
  border: 1px solid color-mix(in srgb, var(--border-color) 72%, transparent);
  border-radius: 999px;
  padding: 0.12rem 0.4rem;
  color: var(--text-color);
  font-size: 0.78rem;
  line-height: 1.45;
  background: color-mix(in srgb, var(--surface-ground) 55%, transparent);
}

.trash-dependency-help-flow i {
  color: var(--text-secondary);
  font-style: normal;
  font-size: 0.82rem;
}

.trash-dependency-help-note {
  margin: 0.5rem 0 0;
  border: 1px dashed color-mix(in srgb, var(--border-color) 60%, transparent);
  padding: 0.45rem 0.55rem;
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: 0.86rem;
  line-height: 1.5;
  overflow-wrap: anywhere;
}

.trash-dependency-help-note p {
  margin: 0;
}

.trash-dependency-help-note p + p {
  margin-top: 0.25rem;
}

@media (max-width: 640px) {
  .trash-dependency-help {
    max-height: 72vh;
  }

  .trash-dependency-help-section {
    padding: 0.7rem;
  }

  .trash-dependency-help-label-grid,
  .trash-dependency-help-flow-grid {
    grid-template-columns: 1fr;
  }
}

:deep(.review-status-chip.review-status-pending) {
  background: #fef3c7;
  color: #92400e;
  border-color: #f59e0b;
  font-weight: 700;
}

:deep(.review-status-chip.review-status-approved) {
  background: #dcfce7;
  color: #166534;
  border-color: #22c55e;
  font-weight: 700;
}

:deep(.review-status-chip.review-status-rejected) {
  background: #fee2e2;
  color: #991b1b;
  border-color: #ef4444;
  font-weight: 700;
}

:deep(.review-status-chip.review-status-takedown) {
  background: #e2e8f0;
  color: #334155;
  border-color: #64748b;
  font-weight: 700;
}

:deep(.review-status-chip.review-status-deleted) {
  background: #ffe4e6;
  color: #9f1239;
  border-color: #f43f5e;
  font-weight: 700;
}

:global(.dark) :deep(.review-status-chip.review-status-pending) {
  background: rgba(245, 158, 11, 0.22);
  color: #fcd34d;
  border-color: rgba(251, 191, 36, 0.55);
}

:global(.dark) :deep(.review-status-chip.review-status-approved) {
  background: rgba(34, 197, 94, 0.2);
  color: #86efac;
  border-color: rgba(74, 222, 128, 0.52);
}

:global(.dark) :deep(.review-status-chip.review-status-rejected) {
  background: rgba(239, 68, 68, 0.2);
  color: #fca5a5;
  border-color: rgba(248, 113, 113, 0.54);
}

:global(.dark) :deep(.review-status-chip.review-status-takedown) {
  background: rgba(100, 116, 139, 0.24);
  color: #cbd5e1;
  border-color: rgba(148, 163, 184, 0.5);
}

:global(.dark) :deep(.review-status-chip.review-status-deleted) {
  background: rgba(244, 63, 94, 0.2);
  color: #fda4af;
  border-color: rgba(251, 113, 133, 0.54);
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

.user-online-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  color: var(--text-color);
  font-size: 0.85rem;
  line-height: 1.35;
  white-space: nowrap;
}

.user-online-badge .pi {
  font-size: 0.58rem;
  line-height: 1;
}

.user-online-dot--online {
  color: #16a34a;
}

  .user-online-dot--offline {
    color: var(--text-secondary);
  }

  :deep(.user-management-table .user-management-actions) {
    display: flex !important;
    flex-direction: row !important;
    align-items: center;
    justify-content: flex-start;
    gap: 0.5rem;
    flex-wrap: wrap;
    width: 100%;
    min-width: 0;
  }

  :deep(.user-management-table .user-management-actions .p-button),
  :deep(.user-management-table .user-management-actions button) {
    flex: 0 0 auto;
    width: auto;
    min-width: auto;
  }

:global(.dark) .user-online-dot--online {
  color: #22c55e;
}
:global(.dark) .user-online-dot--offline {
  color: var(--text-secondary);
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

  :deep(.notification-management-table .admin-card-actions) {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    width: 100%;
    gap: 0.5rem;
  }

  :deep(.user-management-table .admin-card-actions) {
    display: flex;
    flex-wrap: wrap;
    width: 100%;
    gap: 0.5rem;
    align-items: center;
  }

  :deep(.notification-management-table .admin-card-actions .p-button) {
    width: 100%;
    min-width: 0;
    min-height: 2.6rem;
  }

  :deep(.user-management-table .admin-card-actions .p-button) {
    width: auto;
    min-width: 7rem;
    min-height: 2.35rem;
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
    max-width: 100%;
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

  :deep(.notification-management-table .admin-card-actions) {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    width: 100%;
    gap: 0.5rem;
  }

  :deep(.user-management-table .admin-card-actions) {
    display: flex;
    flex-wrap: wrap;
    width: 100%;
    gap: 0.5rem;
    align-items: center;
  }

  :deep(.notification-management-table .admin-card-actions .p-button) {
    width: 100%;
    min-width: 0;
    min-height: 2.65rem;
  }

  :deep(.user-management-table .admin-card-actions .p-button) {
    width: auto;
    min-width: 7rem;
    min-height: 2.35rem;
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
  max-width: min(18rem, 100%);
}

  :deep(.review-card-action-note),
  :deep(.review-card-action-note .review-card-action-note__text) {
    white-space: normal;
  }

  /* Ensure buttons don't wrap on desktop */
  :deep(.p-datatable .flex.gap-2) {
    flex-wrap: nowrap;
    gap: 0.5rem;
  }
}
</style>
