<template>
  <section class="cam-dock" aria-label="摄像头实时预览">
    <div class="cam-thumb">
      <img :src="streamSrc" alt="摄像头预览" />
      <span class="cam-thumb__live"><i class="dot"></i>LIVE</span>
      <span class="cam-thumb__scan"></span>
    </div>

    <div class="cam-dock__body">
      <div class="cam-dock__title">智能摄像头 · 实时预览</div>
      <div class="cam-dock__meta">
        <i class="dot" :class="store.connected ? 'dot--on' : 'dot--off'"></i>
        {{ store.connected ? '画面正常' : '设备离线' }}
        · {{ dev.place }} · {{ store.camera.resolution }} · {{ store.camera.fps }}fps
      </div>
      <div class="cam-dock__tags">
        <span class="chip chip--blue">{{ store.camera.resolution }} 高清</span>
        <span v-if="store.camera.nightVision" class="chip chip--mint">红外夜视</span>
        <span v-if="store.camera.motionDetect" class="chip chip--amber">移动侦测</span>
        <span v-if="store.camera.twoWayAudio" class="chip chip--blue">双向语音</span>
      </div>
    </div>

    <button class="btn-soft cam-dock__open" type="button" @click="store.ui.cam = true">
      <AppIcon name="play" />查看实时画面
    </button>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useCompanionStore } from '@/stores/companion'
import AppIcon from './AppIcon.vue'

const store = useCompanionStore()
const dev = computed(() => store.activeDevice)
// 摄像头流地址优先级：数据库设置 camera.streamUrl > 环境变量 > 本地占位画面
const streamSrc = computed(
  () => store.camera.streamUrl || import.meta.env.VITE_CAM_STREAM_URL || store.IMG.cat
)
</script>
