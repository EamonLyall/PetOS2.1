<template>
  <article class="pet-card" aria-label="宠物档案">
    <div class="pet-card__top">
      <img class="pet-avatar" :src="store.IMG.kitten" :alt="pet.name + '头像'" />
      <div style="min-width:0">
        <div class="pet-name">
          {{ pet.name }} <span class="lv">LV.{{ pet.level }}</span>
        </div>
        <p class="pet-desc">{{ pet.desc }}</p>
        <div class="pet-online" :class="{ 'is-off': !store.connected }">
          <i class="dot" :class="store.connected ? 'dot--on' : 'dot--off'"></i>
          {{ store.connected
            ? dev.name + ' · ' + dev.place
            : '设备离线 · 数据为上次同步' }}
        </div>
      </div>
      <button
        class="icon-btn"
        type="button"
        aria-label="查看宠物详情"
        style="margin-left:auto;width:30px;height:30px"
        @click="router.push({ name: 'pet' })"
      >
        <AppIcon name="chevR" />
      </button>
    </div>

    <div class="pet-card__growth">
      <div class="growth-row">
        <span>成长值</span>
        <b>{{ pet.growth }} <em>/ 100</em></b>
      </div>
      <div
        class="bar"
        role="progressbar"
        :aria-valuenow="pet.growth"
        aria-valuemin="0"
        aria-valuemax="100"
      >
        <i :style="{ width: pet.growth + '%' }"></i>
      </div>
      <div class="pet-hint">
        <AppIcon name="check" />
        距离 LV.{{ pet.level + 1 }} 还需 {{ 100 - pet.growth }} 点陪伴值
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCompanionStore } from '@/stores/companion'
import AppIcon from './AppIcon.vue'

const router = useRouter()
const store = useCompanionStore()
const pet = computed(() => store.activePet)
const dev = computed(() => store.activeDevice)
</script>
