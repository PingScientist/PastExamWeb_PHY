<template>
  <div id="app" class="flex flex-column">
    <Toast position="bottom-right" />
    <ConfirmDialog />
    <Navbar class="navbar px-1" @toggle-sidebar="toggleSidebar" />
    <div class="content-container">
      <div v-if="hasAppRenderError" class="app-render-error">
        <div class="app-render-error__box">
          <h3>頁面暫時無法顯示</h3>
          <p>{{ appRenderErrorMessage || '應用程式發生未預期錯誤，請嘗試重新整理。' }}</p>
          <button type="button" class="app-render-error__action" @click="reloadApp">
            重新整理
          </button>
        </div>
      </div>
      <router-view v-else />
    </div>
  </div>
</template>

<script>
import Navbar from './components/Navbar.vue'
import { provide, ref, watch, onErrorCaptured } from 'vue'
import { useRoute } from 'vue-router'
import Toast from 'primevue/toast'
import ConfirmDialog from 'primevue/confirmdialog'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { setGlobalToast } from './utils/toast'
import { applyFontSizePreference } from './utils/fontSizePreference'

export default {
  components: {
    Navbar,
    Toast,
    ConfirmDialog,
  },
  setup() {
    const sidebarVisible = ref(true)
    const toast = useToast()
    const confirm = useConfirm()
    const route = useRoute()
    const hasAppRenderError = ref(false)
    const appRenderErrorMessage = ref('')

    setGlobalToast(toast)
    applyFontSizePreference()

    provide('sidebarVisible', sidebarVisible)
    provide('toast', toast)
    provide('confirm', confirm)

    const toggleSidebar = () => {
      sidebarVisible.value = !sidebarVisible.value
    }

    const reloadApp = () => {
      hasAppRenderError.value = false
      appRenderErrorMessage.value = ''
      window.location.reload()
    }

    onErrorCaptured((error) => {
      console.error('Vue runtime error:', error)
      hasAppRenderError.value = true
      appRenderErrorMessage.value = error?.message || '未定義錯誤'
      return false
    })

    watch(
      () => route.fullPath,
      () => {
        hasAppRenderError.value = false
        appRenderErrorMessage.value = ''
      }
    )

    return {
      toggleSidebar,
      hasAppRenderError,
      appRenderErrorMessage,
      reloadApp,
    }
  },
}
</script>

<style>
:root {
  --navbar-height: 60px;
}

html,
body,
#app {
  height: 100%;
  margin: 0;
  padding: 0;
  max-width: 100%;
  min-width: 0;
  overflow-x: hidden;
}

*,
*::before,
*::after {
  box-sizing: border-box;
}

#app {
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 0;
}

.app-render-error {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.app-render-error__box {
  max-width: 32rem;
  width: 100%;
  background: var(--p-card-background, var(--bg-primary));
  border: 1px solid var(--surface-border, #d9d9d9);
  padding: 1.5rem;
  border-radius: 0.75rem;
  text-align: center;
}

.app-render-error__box h3 {
  margin-top: 0;
}

.app-render-error__action {
  border: 1px solid var(--surface-border, #d9d9d9);
  background: var(--surface-card, #ffffff);
  color: inherit;
  border-radius: 0.5rem;
  padding: 0.5rem 1rem;
}

.navbar {
  height: var(--navbar-height);
  z-index: 100;
}

.content-container {
  height: calc(100vh - var(--navbar-height));
  overflow-y: auto;
  overflow-x: hidden;
  min-width: 0;
  max-width: 100%;
}

@supports (height: 100svh) {
  .content-container {
    height: calc(100svh - var(--navbar-height));
  }
}
</style>
