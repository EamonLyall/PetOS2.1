<template>
  <div class="view is-active" data-view="设备控制">
    <div class="page-head">
      <span class="page-head__ico"><AppIcon name="device" /></span>
      <div>
        <h1>设备控制</h1>
        <p>摄像头、麦克风与各类配件，一手掌握</p>
      </div>
    </div>

    <div class="dev-manager">
      <!-- 设备管理 -->
      <article class="card">
        <div class="card__hd">
          <span class="card__badge card__badge--mint"><AppIcon name="link" /></span>
          <h2 class="card__title">设备管理</h2>
          <div class="card__aside">
            <button class="link" type="button" @click="openDrawer">
              <AppIcon name="plus" />管理设备
            </button>
          </div>
        </div>

        <div style="margin-top:14px">
          <div class="dev-current">
            <span class="dev-current__ico"><AppIcon name="paw" /></span>
            <div class="dev-current__main">
              <div class="dev-current__name">{{ store.activeDevice.name }}</div>
              <div class="dev-current__sub">
                <i class="dot" :class="store.connected ? 'dot--on' : 'dot--off'"></i>
                <template v-if="store.connected">
                  {{ store.activePet.name }} · {{ store.activeDevice.place }}
                  · 信号 {{ store.activeDevice.signal }}%
                </template>
                <template v-else>未连接</template>
              </div>
            </div>
            <button class="btn-ghost" type="button" @click="openDrawer">
              <AppIcon name="chevR" />切换
            </button>
          </div>
        </div>

        <ul class="kv-list">
          <li class="kv">
            <span class="kv__ico"><AppIcon name="wifi" /></span>
            <div class="kv__body">
              <span class="kv__label">Wi-Fi 网络</span>
              <span class="kv__value">{{ store.activeDevice.wifi }}</span>
            </div>
            <span class="kv__tail">{{ store.network.wifiQuality }}</span>
          </li>
          <li class="kv">
            <span class="kv__ico kv__ico--violet"><AppIcon name="bolt" /></span>
            <div class="kv__body">
              <span class="kv__label">固件版本</span>
              <span class="kv__value">{{ store.activeDevice.fw }}</span>
            </div>
            <span class="kv__tail">{{ store.network.firmwareLatest ? '已是最新' : '有新版本' }}</span>
          </li>
        </ul>
      </article>

      <!-- 摄像头实时预览 -->
      <article class="card card--control">
        <div class="card__hd">
          <span class="card__badge"><AppIcon name="camera" /></span>
          <h2 class="card__title">摄像头 · 实时预览</h2>
          <div class="card__aside">
            <span class="chip" style="height:22px;font-size:12px;background:rgba(255,255,255,.12);color:#d7e6ff;border-color:rgba(255,255,255,.16)">✦ 亮点功能</span>
          </div>
        </div>

        <div class="cam-showcase">
          <div class="cam-preview">
            <img :src="store.IMG.cat" alt="摄像头预览" />
            <span class="cam-preview__live"><i class="dot"></i>LIVE</span>
            <span class="cam-preview__scan"></span>
            <span class="cam-preview__cap">
              {{ store.activeDevice.place }} · {{ store.camera.resolution }} · {{ store.camera.fps }}fps
            </span>
          </div>
          <div class="cam-showcase__info">
            <span class="cam-showcase__ico"><AppIcon name="camera" /></span>
            <div>
              <div class="cam-showcase__title">智能摄像头</div>
              <div class="cam-showcase__meta">
                <i class="dot dot--on"></i>已连接 · 画面正常
              </div>
            </div>
          </div>
        </div>

        <button class="btn-primary" type="button" style="margin-top:12px" @click="store.ui.cam = true">
          <AppIcon name="play" />查看实时画面
        </button>
      </article>
    </div>

    <div class="info-grid info-grid--2">
      <!-- 语音与音量 -->
      <article class="card">
        <div class="card__hd">
          <span class="card__badge card__badge--amber"><AppIcon name="volume" /></span>
          <h2 class="card__title">语音与音量</h2>
        </div>
        <ul class="kv-list">
          <li class="kv">
            <span class="kv__ico"><AppIcon name="mic" /></span>
            <div class="kv__body">
              <span class="kv__label">麦克风</span>
              <span class="kv__value">
                {{ store.deviceOpts.mic ? '开启' : '已关闭' }}
                · 灵敏度 {{ store.deviceOpts.micSensitivity }}%
              </span>
            </div>
            <AppSwitch
              :model-value="store.deviceOpts.mic"
              label="麦克风"
              @update:model-value="store.toggleOption('device', 'mic')"
            />
          </li>
          <li class="kv">
            <span class="kv__ico kv__ico--amber"><AppIcon name="volume" /></span>
            <div class="kv__body">
              <span class="kv__label">扬声器音量</span>
              <span class="range" style="max-width:220px;margin-top:6px">
                <input
                  type="range"
                  min="0"
                  max="100"
                  :value="store.voice.volume"
                  aria-label="设备音量"
                  :style="{ '--vol': store.voice.volume + '%' }"
                  @input="onVolInput"
                  @change="onVolChange"
                />
                <b class="dev-vol-val">{{ store.voice.volume }}%</b>
              </span>
            </div>
          </li>
          <li class="kv">
            <span class="kv__ico kv__ico--violet"><AppIcon name="speaker" /></span>
            <div class="kv__body">
              <span class="kv__label">语音回复</span>
              <span class="kv__value">TTS 自然音色</span>
            </div>
            <button
              class="switch"
              :class="{ 'is-on': store.voice.tts }"
              type="button"
              aria-label="切换语音回复"
              :aria-pressed="store.voice.tts"
              @click.stop="store.toggleTts"
            ></button>
          </li>
        </ul>
      </article>

      <!-- 屏幕与云台 -->
      <article class="card">
        <div class="card__hd">
          <span class="card__badge card__badge--violet"><AppIcon name="screen" /></span>
          <h2 class="card__title">屏幕与云台</h2>
        </div>
        <ul class="kv-list">
          <li class="kv">
            <span class="kv__ico kv__ico--violet"><AppIcon name="screen" /></span>
            <div class="kv__body">
              <span class="kv__label">表情屏</span>
              <span class="kv__value">
                {{ store.screen.on
                  ? '在线 · 显示「' + store.screen.expression + '」'
                  : '已关闭' }}
              </span>
            </div>
            <button
              class="switch"
              :class="{ 'is-on': store.screen.on }"
              type="button"
              aria-label="切换表情屏"
              :aria-pressed="store.screen.on"
              @click.stop="store.toggleScreen"
            ></button>
          </li>
          <li class="kv">
            <span class="kv__ico"><AppIcon name="servo" /></span>
            <div class="kv__body">
              <span class="kv__label">云台舵机</span>
              <span class="kv__value">{{ store.deviceOpts.gimbal ? '自动追踪开启' : '自动追踪关闭' }}</span>
            </div>
            <AppSwitch
              :model-value="store.deviceOpts.gimbal"
              label="云台舵机"
              @update:model-value="store.toggleOption('device', 'gimbal')"
            />
          </li>
          <li class="kv">
            <span class="kv__ico kv__ico--amber"><AppIcon name="bolt" /></span>
            <div class="kv__body">
              <span class="kv__label">移动侦测</span>
              <span class="kv__value">灵敏度 · {{ store.deviceOpts.motionSensitivity }}</span>
            </div>
            <AppSwitch
              :model-value="store.deviceOpts.motion"
              label="移动侦测"
              @update:model-value="store.toggleOption('device', 'motion')"
            />
          </li>
        </ul>
      </article>
    </div>
  </div>
</template>

<script setup>
import { useCompanionStore } from '@/stores/companion'
import AppIcon from '@/components/AppIcon.vue'
import AppSwitch from '@/components/AppSwitch.vue'

const store = useCompanionStore()

function openDrawer() {
  store.ui.drawer = true
  store.ui.notif = false
}

function onVolInput(e) {
  store.setVolume(parseInt(e.target.value, 10))
}

function onVolChange(e) {
  store.commitVolume()
  store.pushToast('音量已调节至 ' + e.target.value + '%')
}
</script>
