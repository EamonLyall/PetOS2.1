<template>
  <div class="view mine">
    <!-- 账户卡片 -->
    <section class="mine-hero">
      <img class="mine-hero__avatar" :src="store.IMG.kitten" :alt="store.profile.account + '头像'" />
      <div class="mine-hero__info">
        <h1>{{ store.profile.account }}</h1>
        <p>
          <i class="dot" :class="store.connected ? 'dot--on' : 'dot--off'"></i>
          {{ store.connected ? store.activePet.name + ' · 设备在线' : '设备未连接' }}
        </p>
      </div>
      <button class="mine-hero__edit" type="button" @click="toast('账户信息')">账户</button>
    </section>

    <!-- 守护预警入口 -->
    <router-link v-if="store.openAlertCount" class="mine-alert" :to="{ name: 'alerts' }">
      <span class="mine-alert__ico"><AppIcon name="health" /></span>
      <div class="mine-alert__body">
        <b>{{ store.pendingAlertCount ? store.pendingAlertCount + ' 条守护预警待确认' : store.openAlertCount + ' 条守护预警待跟进' }}</b>
        <span>及时了解孩子的情绪状态</span>
      </div>
      <i class="mine-alert__count">{{ store.openAlertCount }}</i>
      <AppIcon name="chevR" />
    </router-link>

    <!-- 功能入口 -->
    <section class="mine-card">
      <div class="mine-card__hd">功能</div>
      <router-link
        v-for="item in entries"
        :key="item.key"
        class="mine-row"
        :to="{ name: item.key }"
      >
        <span class="mine-row__ico"><AppIcon :name="item.icon" /></span>
        <div class="mine-row__body">
          <div class="mine-row__title">{{ item.name }}</div>
          <div class="mine-row__sub">{{ item.desc }}</div>
        </div>
        <AppIcon name="chevR" />
      </router-link>
    </section>

    <!-- 设备与消息 -->
    <section class="mine-card">
      <div class="mine-card__hd">设备与消息</div>

      <button class="mine-row" type="button" @click="openDrawer">
        <span class="mine-row__ico"><AppIcon name="device" /></span>
        <div class="mine-row__body">
          <div class="mine-row__title">当前设备</div>
          <div class="mine-row__sub">
            {{ store.activeDevice.name }} · {{ store.activeDevice.place || '未连接' }}
          </div>
        </div>
        <span class="mine-row__val">管理</span>
      </button>

      <button class="mine-row" type="button" @click="toast('消息通知')">
        <span class="mine-row__ico"><AppIcon name="bell" /></span>
        <div class="mine-row__body">
          <div class="mine-row__title">消息通知</div>
          <div class="mine-row__sub">陪伴提醒与系统消息</div>
        </div>
        <span class="mine-row__val">{{ store.unreadCount ? store.unreadCount + ' 条未读' : '已读完' }}</span>
      </button>

      <button class="mine-row" type="button" @click="toast('关于 PetOS')">
        <span class="mine-row__ico"><AppIcon name="paw" /></span>
        <div class="mine-row__body">
          <div class="mine-row__title">关于 PetOS</div>
          <div class="mine-row__sub">AI Companion · v{{ store.profile.appVersion }}</div>
        </div>
        <AppIcon name="chevR" />
      </button>
    </section>

    <p class="mine-foot">PetOS · 陪伴每一天</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useCompanionStore } from '@/stores/companion'
import AppIcon from '@/components/AppIcon.vue'

const store = useCompanionStore()

const DESC = {
  pet: '档案、成长值与健康状态',
  device: '摄像头、语音与云台控制',
  memory: '时间线与照片墙',
  plugin: '能力插件与开关',
  settings: '网络、语音与隐私'
}

// 从统一导航里取移动端需要的入口，首页/聊天/预警已在底部导航
const entries = computed(() =>
  store.nav
    .filter(n => ['pet', 'device', 'memory', 'plugin', 'settings'].includes(n.key))
    .map(n => ({ ...n, desc: DESC[n.key] || '查看详情' }))
)

function openDrawer() {
  store.ui.drawer = true
}

function toast(title) {
  store.pushToast(title)
}
</script>
