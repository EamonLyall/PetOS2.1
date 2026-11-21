<template>
  <aside class="sidebar" :class="{ 'is-open': store.ui.menu }" aria-label="主导航">
    <div class="brand">
      <div class="brand__mark"><AppIcon name="paw" /></div>
      <div>
        <div class="brand__name">PetOS</div>
        <div class="brand__sub">AI Companion</div>
      </div>
    </div>

    <nav class="nav" aria-label="功能菜单">
      <router-link
        v-for="n in store.nav"
        :key="n.key"
        :to="{ name: n.key }"
        class="nav__item"
        :class="{ 'is-active': route.name === n.key }"
        @click="store.ui.menu = false"
      >
        <AppIcon :name="n.icon" />
        <span>{{ n.name }}</span>
      </router-link>
    </nav>

    <div class="side-device" title="管理设备连接" @click="openDrawer">
      <div class="side-device__row">
        <span class="side-device__ico"><AppIcon name="device" /></span>
        <div>
          <div class="side-device__name">{{ store.activeDevice.name }}</div>
          <div class="side-device__state">
            <i class="dot" :class="store.connected ? 'dot--on' : 'dot--off'"></i>
            {{ store.connected ? store.activePet.name + ' · 已连接' : '未连接 · 点击选择' }}
          </div>
        </div>
        <span class="side-device__chev"><AppIcon name="chevR" /></span>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { useCompanionStore } from '@/stores/companion'
import AppIcon from './AppIcon.vue'

const route = useRoute()
const store = useCompanionStore()

function openDrawer() {
  store.ui.drawer = true
  store.ui.menu = false
  store.ui.notif = false
}
</script>
