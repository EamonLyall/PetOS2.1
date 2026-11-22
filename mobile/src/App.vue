<template>
  <!-- 全局 SVG 图标定义（50 个 symbol，一次性挂载） -->
  <IconSymbols />

  <div class="app">
    <AppMobileNav />
    <div class="main">
      <AppTopbar />
      <main class="content">
        <router-view />
      </main>
    </div>
  </div>

  <!-- 遮罩：设备抽屉 / 通知等浮层打开时显示，点击关闭 -->
  <div
    class="overlay"
    :class="{ 'is-open': store.ui.drawer || store.ui.notif }"
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
import AppMobileNav from '@/components/AppMobileNav.vue'
import AppTopbar from '@/components/AppTopbar.vue'
import DeviceDrawer from '@/components/DeviceDrawer.vue'
import CameraModal from '@/components/CameraModal.vue'
import ToastHost from '@/components/ToastHost.vue'

const store = useCompanionStore()

function onOverlayClick() {
  store.ui.drawer = false
  store.ui.notif = false
}

// ESC 关闭所有浮层
function onKeydown(e) {
  if (e.key === 'Escape') {
    store.ui.cam = false
    store.ui.drawer = false
    store.ui.notif = false
  }
}

// 应用启动：从后端数据库拉取全量快照填充全局状态（替代原本地 mock）
let alertSyncTimer = null
onMounted(() => {
  store.bootstrap()
  // 轻量轮询让 PC / H5 家长端无需手动刷新即可收到新预警角标
  alertSyncTimer = window.setInterval(() => store.refreshAlerts().catch(() => {}), 20000)
  document.addEventListener('keydown', onKeydown)
})
onUnmounted(() => {
  window.clearInterval(alertSyncTimer)
  document.removeEventListener('keydown', onKeydown)
})
</script>
