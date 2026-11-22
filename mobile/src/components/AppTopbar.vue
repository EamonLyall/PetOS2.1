<template>
  <header class="topbar">
    <router-link class="mobile-brand" :to="{ name: 'home' }" aria-label="PetOS 首页">
      <span class="mobile-brand__mark"><AppIcon name="paw" /></span>
      <b>PetOS</b>
    </router-link>

    <label class="search" for="searchInput">
      <AppIcon name="search" />
      <input
        id="searchInput"
        ref="searchInput"
        v-model="keyword"
        type="text"
        placeholder="搜索功能或指令…"
        autocomplete="off"
        @keydown.enter="doSearch"
      />
      <kbd class="search__kbd">Ctrl + K</kbd>
    </label>

    <div class="topbar__right">
      <span class="pill pill--clock" aria-label="当前时间">
        <AppIcon name="clock" /><b>{{ hm }}</b>
      </span>

      <span
        class="pill pill--device"
        :class="{ 'is-off': !store.connected }"
        title="设备中心"
        @click="openDrawer"
      >
        <i class="dot" :class="store.connected ? 'dot--on' : 'dot--off'"></i>
        <template v-if="store.connected">
          <b>{{ store.activePet.name }}</b> · 已连接
        </template>
        <template v-else>未连接 · 选择设备</template>
      </span>

      <div style="position:relative">
        <button
          class="icon-btn"
          type="button"
          aria-label="通知"
          :aria-expanded="store.ui.notif"
          aria-controls="notifPop"
          @click.stop="toggleNotif"
        >
          <AppIcon name="bell" />
          <i v-if="store.unreadCount > 0" class="icon-btn__badge"></i>
        </button>

        <div
          id="notifPop"
          class="popover"
          :class="{ 'is-open': store.ui.notif }"
          role="dialog"
          aria-label="通知中心"
          @click.stop
        >
          <div class="popover__hd">
            <b>通知</b><span @click="readAll">全部已读</span>
          </div>
          <!-- 通知内容来自数据库 notification 表（后端 /api/state 快照） -->
          <div v-for="n in store.notifications" :key="n.id" class="notif">
            <div class="notif__ico" :class="n.tone ? 'notif__ico--' + n.tone : ''">
              <AppIcon :name="n.icon" />
            </div>
            <div class="notif__body">
              <b>{{ n.text }}</b>
              <span>{{ n.timeAgo }}</span>
            </div>
          </div>
          <div v-if="!store.notifications.length" class="notif">
            <div class="notif__ico"><AppIcon name="info" /></div>
            <div class="notif__body"><b>暂时没有新通知</b><span>—</span></div>
          </div>
        </div>
      </div>

      <button class="topbar-user" type="button" @click="store.pushToast('账号中心为原型占位页')">
        <img class="avatar" :src="store.IMG.kitten" :alt="store.profile.account + '头像'" @error="onAvatarError" />
        <span>{{ store.profile.account }}</span>
        <AppIcon name="chevD" />
      </button>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useCompanionStore } from '@/stores/companion'
import { useClock } from '@/composables/useClock'
import AppIcon from './AppIcon.vue'

const store = useCompanionStore()
const { hm } = useClock()

const keyword = ref('')
const searchInput = ref(null)

function openDrawer() {
  store.ui.drawer = true
  store.ui.notif = false
}

function toggleNotif() {
  store.ui.notif = !store.ui.notif
}

function readAll() {
  // 全部已读写入数据库，成功后由 store 刷新通知列表
  store.markAllRead()
  store.ui.notif = false
}

function doSearch() {
  const q = keyword.value.trim()
  if (!q) return
  store.pushToast('正在搜索：「' + q + '」')
  keyword.value = ''
}

function onAvatarError(e) {
  e.target.style.opacity = 0
}

// 全局快捷键：Ctrl/Cmd + K 聚焦搜索框
function onKeydown(e) {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
    e.preventDefault()
    if (searchInput.value) {
      searchInput.value.focus()
      searchInput.value.select()
    }
  }
}

// 点击通知气泡以外的区域时关闭通知
function onDocClick() {
  if (store.ui.notif) store.ui.notif = false
}

onMounted(() => {
  document.addEventListener('keydown', onKeydown)
  document.addEventListener('click', onDocClick)
})
onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown)
  document.removeEventListener('click', onDocClick)
})
</script>
