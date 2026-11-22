<template>
  <!-- 全局 SVG 图标定义（50 个 symbol，一次性挂载） -->
  <IconSymbols />

  <div class="app">
    <AppSidebar />
    <div class="main">
      <AppTopbar />
      <main class="content">
        <router-view />
      </main>
    </div>
  </div>

  <!-- 遮罩：抽屉 / 侧边导航打开时显示，点击关闭 -->
  <div
    class="overlay"
    :class="{ 'is-open': store.ui.drawer || store.ui.menu }"
    @click="onOverlayClick"
  ></div>

  <!-- 浮层 -->
  <DeviceDrawer />
  <CameraModal />
  <ToastHost />
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useCompanionStore } from '@/stores/companion'
import IconSymbols from '@/components/IconSymbols.vue'
import AppSidebar from '@/components/AppSidebar.vue'
import AppTopbar from '@/components/AppTopbar.vue'
import DeviceDrawer from '@/components/DeviceDrawer.vue'
import CameraModal from '@/components/CameraModal.vue'
import ToastHost from '@/components/ToastHost.vue'

const store = useCompanionStore()

function onOverlayClick() {
  store.ui.drawer = false
  store.ui.menu = false
}

// ESC 关闭所有浮层
function onKeydown(e) {
  if (e.key === 'Escape') {
    store.ui.cam = false
    store.ui.drawer = false
    store.ui.notif = false
    store.ui.menu = false
  }
}

// 应用启动：从后端数据库拉取全量快照填充全局状态（替代原本地 mock）
let alertSyncTimer = null
onMounted(() => {
  store.bootstrap()
  // 轻量轮询让家长端无需手动刷新即可收到新预警角标（移动端 H5 工程同样如此）
  alertSyncTimer = window.setInterval(() => store.refreshAlerts().catch(() => {}), 20000)
  document.addEventListener('keydown', onKeydown)
})
onUnmounted(() => {
  window.clearInterval(alertSyncTimer)
  document.removeEventListener('keydown', onKeydown)
})
</script>
