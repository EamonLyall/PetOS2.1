<template>
  <nav class="mobile-nav" aria-label="移动端主导航">
    <router-link
      v-for="item in items"
      :key="item.key"
      :to="{ name: item.key }"
      class="mobile-nav__item"
      :class="{ 'is-active': route.name === item.key }"
    >
      <AppIcon :name="item.icon" />
      <span>{{ item.name }}</span>
      <i v-if="item.key === 'alerts' && store.openAlertCount" class="mobile-nav__badge">
        {{ store.openAlertCount > 99 ? '99+' : store.openAlertCount }}
      </i>
    </router-link>
    <router-link
      :to="{ name: 'mine' }"
      class="mobile-nav__item"
      :class="{ 'is-active': route.name === 'mine' }"
    >
      <AppIcon name="user" />
      <span>我的</span>
    </router-link>
  </nav>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { useCompanionStore } from '@/stores/companion'
import AppIcon from './AppIcon.vue'

const route = useRoute()
const store = useCompanionStore()
const items = [
  { key: 'home', name: '首页', icon: 'home' },
  { key: 'chat', name: '聊天', icon: 'chat' },
  { key: 'alerts', name: '预警', icon: 'health' }
]
</script>
