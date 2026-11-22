<template>
  <section class="hero" aria-label="今日问候">
    <img class="hero__cat" :src="store.IMG.cat" alt="正在晒太阳的小猫" />

    <div class="hero__text">
      <span class="hero__eyebrow"><AppIcon name="spark" />{{ dateStr }}</span>
      <h1 class="hero__greet">
        <span>{{ greet }}</span>
        <span class="wave" aria-hidden="true">👋</span>
      </h1>
      <p class="hero__sub">今天也要和{{ pet.name }}一起度过哦～</p>
      <div class="hero__meta">
        <span class="chip chip--mint"><AppIcon name="smile" />{{ pet.mood }}</span>
        <span class="chip chip--amber">
          <AppIcon name="bolt" />活跃度 <b>{{ pet.active }}%</b>
        </span>
        <span class="chip chip--blue">
          <AppIcon name="chat" />今日互动 <b>{{ pet.interact }} 次</b>
        </span>
      </div>
    </div>

    <div class="hero__aside">
      <button
        class="voice-orb"
        :class="{ 'is-listening': store.voice.listening }"
        type="button"
        aria-label="语音唤醒"
        :aria-pressed="store.voice.listening"
        @click="store.toggleWake"
      >
        <span class="voice-orb__ring"></span>
        <span class="voice-orb__core"><AppIcon name="mic" /></span>
      </button>
      <div class="voice-copy">
        <div class="voice-copy__title">
          {{ store.voice.listening ? '我在听，请说话…' : '语音唤醒' }}
        </div>
        <div class="voice-copy__sub">唤醒词 · {{ store.voice.wakeWord }}</div>
      </div>
      <div v-if="store.voice.listening" class="voice-wave" aria-hidden="true">
        <i></i><i></i><i></i><i></i><i></i>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useCompanionStore } from '@/stores/companion'
import AppIcon from './AppIcon.vue'

const WEEK = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

const store = useCompanionStore()
const pet = computed(() => store.activePet)

const now = new Date()
const h = now.getHours()
const greet = computed(() => {
  if (h < 5) return '夜深了，主人！'
  if (h < 11) return '早上好，主人！'
  if (h < 13) return '中午好，主人！'
  if (h < 18) return '下午好，主人！'
  return '晚上好，主人！'
})

const dateStr = computed(
  () => (now.getMonth() + 1) + '月' + now.getDate() + '日 · ' + WEEK[now.getDay()]
)
</script>
