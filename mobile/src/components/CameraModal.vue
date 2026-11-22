<template>
  <div
    class="modal"
    :class="{ 'is-open': store.ui.cam }"
    role="dialog"
    aria-modal="true"
    :aria-hidden="!store.ui.cam"
    @click.self="store.ui.cam = false"
  >
    <div class="modal__panel">
      <div class="modal__hd">
        <span class="card__badge card__badge--mint"><AppIcon name="camera" /></span>
        <h3>智能摄像头 · 实时画面</h3>
        <span class="badge-online" :class="{ 'is-off': !store.connected }">
          <i class="dot" :class="store.connected ? 'dot--on' : 'dot--off'"></i>
          {{ store.connected ? '已连接' : '离线' }}
        </span>
        <button class="modal__close" type="button" aria-label="关闭" @click="store.ui.cam = false">
          <AppIcon name="close" />
        </button>
      </div>

      <div class="modal__body">
        <div class="live">
          <img :src="streamSrc" alt="摄像头实时画面" />
          <span class="live__tag"><i class="dot"></i>LIVE</span>
          <span class="live__scan"></span>
          <span class="live__meta">
            <i class="dot dot--on"></i>
            {{ store.activeDevice.place }} · {{ store.camera.resolution }} · {{ store.camera.fps }}fps
          </span>
        </div>

        <div class="ctrl-row">
          <button type="button" @click="store.pushToast('麦克风已静音')">
            <AppIcon name="mute" />静音
          </button>
          <button type="button" @click="store.pushToast('已保存当前画面截图')">
            <AppIcon name="shot" />截图
          </button>
          <button type="button" @click="store.pushToast('开始录制 10 秒短视频')">
            <AppIcon name="record" />录制
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useCompanionStore } from '@/stores/companion'
import AppIcon from './AppIcon.vue'

const store = useCompanionStore()

// 摄像头流地址优先级：数据库设置 camera.streamUrl > 环境变量 > 本地占位画面
const streamSrc = computed(
  () => store.camera.streamUrl || import.meta.env.VITE_CAM_STREAM_URL || store.IMG.cat
)
</script>
