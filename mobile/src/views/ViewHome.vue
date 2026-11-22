<template>
  <div class="view is-active" data-view="总览首页">
    <section class="home-top" aria-label="一级信息">
      <HeroBanner />
      <PetInfoCard />
    </section>

    <!-- 离线提示条：仅在未连接时显示 -->
    <div v-if="!store.connected" class="offline-banner">
      <AppIcon name="info" />
      <span>当前未连接设备，宠物数据为上次同步。连接设备后可查看实时状态。</span>
      <button class="btn-soft" type="button" @click="store.ui.drawer = true">
        <AppIcon name="device" />选择设备
      </button>
    </div>

    <section aria-label="二级信息">
      <HomeAiHub />
    </section>

    <section aria-label="三级信息">
      <HomeCameraDock />
    </section>
  </div>
</template>

<script setup>
import { useCompanionStore } from '@/stores/companion'
import AppIcon from '@/components/AppIcon.vue'
import HeroBanner from '@/components/HeroBanner.vue'
import PetInfoCard from '@/components/PetInfoCard.vue'
import HomeAiHub from '@/components/HomeAiHub.vue'
import HomeCameraDock from '@/components/HomeCameraDock.vue'

const store = useCompanionStore()
</script>
