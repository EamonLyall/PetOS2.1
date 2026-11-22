<template>
  <section class="card ai-hub" aria-label="AI 核心能力">
    <div class="card__hd">
      <span class="card__badge card__badge--violet"><AppIcon name="spark" /></span>
      <h2 class="card__title">AI 核心能力</h2>
      <div class="card__aside">
        <span class="chip" style="height:24px;font-size:13px">9 项能力</span>
        <button class="link" type="button" @click="store.ui.aiOpen = !store.ui.aiOpen">
          {{ store.ui.aiOpen ? '收起' : '展开全部' }}
          <AppIcon :name="store.ui.aiOpen ? 'chevD' : 'chevR'" />
        </button>
      </div>
    </div>

    <!-- 快捷入口 -->
    <div class="ai-quick">
      <button
        v-for="q in quick"
        :key="q.n"
        class="ai-qitem"
        :class="q.c"
        type="button"
        @click="handleQuick(q)"
      >
        <AppIcon :name="q.i" />{{ q.n }}
      </button>
    </div>

    <!-- 展开面板：9 项能力 -->
    <div class="ai-panel" :class="{ 'is-open': store.ui.aiOpen }">
      <div class="ai-grid">
        <div
          v-for="r in rows"
          :key="r.key"
          class="ai-row"
          :class="{ 'ai-row--wide': r.wide }"
        >
          <span class="ai-row__ico" :class="r.c"><AppIcon :name="r.i" /></span>
          <div class="ai-row__body">
            <div class="ai-row__name">{{ r.n }}</div>
            <!-- 元信息：时钟行单独渲染动态秒数 -->
            <div v-if="r.key === 'clock'" class="ai-row__meta">
              实时时钟 · <b>{{ hms }}</b>
            </div>
            <div v-else-if="r.meta" class="ai-row__meta">{{ r.meta }}</div>
          </div>

          <!-- 操作区 -->
          <span class="ai-row__action">
            <!-- 音量滑杆 -->
            <span v-if="r.type === 'range'" class="range">
              <input
                type="range"
                min="0"
                max="100"
                :value="store.voice.volume"
                aria-label="音量调节"
                :style="{ '--vol': store.voice.volume + '%' }"
                @input="onVolInput"
                @change="onVolChange"
              />
              <b>{{ store.voice.volume }}%</b>
            </span>

            <!-- 真开关 -->
            <button
              v-else-if="r.type === 'switch'"
              class="sw-btn"
              :class="{ 'is-on': switchOn(r) }"
              type="button"
              :aria-label="r.n + '开关'"
              :aria-pressed="switchOn(r)"
              @click.stop="handleRow(r)"
            ></button>

            <!-- 链接按钮（无操作的时钟行不渲染） -->
            <button
              v-else-if="r.type !== 'none'"
              class="link"
              type="button"
              @click="handleRow(r)"
            >
              {{ r.v }}<AppIcon name="chevR" />
            </button>
          </span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useCompanionStore } from '@/stores/companion'
import { useClock } from '@/composables/useClock'
import AppIcon from './AppIcon.vue'

const router = useRouter()
const store = useCompanionStore()
const { hms } = useClock()

// 快捷入口（颜色类与原型一致）
const quick = [
  { n: '多轮对话', i: 'chat', c: '--violet', act: 'goto', to: 'chat' },
  { n: '屏幕显示', i: 'screen', c: '', act: 'toggle-screen' },
  { n: '语音回复', i: 'speaker', c: '--mint', act: 'toggle-tts' },
  { n: '通用问答', i: 'robot', c: '--pink', act: 'goto', to: 'chat' }
]

// 9 项能力（meta 为静态文本，动态值在需要时通过方法取）
const rows = [
  { key: 'wake', n: '语音唤醒', i: 'mic', c: '--violet', type: 'link', v: '唤醒', act: 'wake', meta: '唤醒词 · ' + store.voice.wakeWord },
  { key: 'gotoChat1', n: '多轮对话', i: 'chat', c: '--violet', type: 'link', v: '聊天', act: 'goto', to: 'chat', meta: '连续交流 · 上下文记忆' },
  { key: 'screen', n: '屏幕显示', i: 'screen', c: '', type: 'switch', act: 'toggle-screen' },
  { key: 'tts', n: '语音回复', i: 'speaker', c: '--mint', type: 'switch', act: 'toggle-tts', meta: 'TTS 自然音色' },
  { key: 'volume', n: '音量调节', i: 'volume', c: '--amber', type: 'range', wide: true },
  { key: 'clock', n: '时间显示', i: 'clock', c: '--violet', type: 'none' },
  { key: 'weather', n: '天气查询', i: 'weather', c: '--amber', type: 'link', v: '查看', act: 'toast' },
  { key: 'music', n: '音乐播放', i: 'music', c: '--pink', type: 'link', v: '播放', act: 'music' },
  { key: 'gotoChat2', n: '通用问答 / 聊天', i: 'robot', c: '--mint', type: 'link', v: '聊天', act: 'goto', to: 'chat', meta: '知识问答 · 随时畅聊' }
]

function switchOn(r) {
  if (r.key === 'screen') return store.screen.on
  if (r.key === 'tts') return store.voice.tts
  return false
}

function handleQuick(q) {
  if (q.act === 'goto') router.push({ name: q.to })
  else if (q.act === 'toggle-screen') store.toggleScreen()
  else if (q.act === 'toggle-tts') store.toggleTts()
}

function handleRow(r) {
  switch (r.act) {
    case 'goto':
      router.push({ name: r.to })
      break
    case 'wake':
      store.toggleWake()
      break
    case 'toggle-screen':
      store.toggleScreen()
      break
    case 'toggle-tts':
      store.toggleTts()
      break
    case 'music':
      store.toggleMusic()
      break
    case 'toast': {
      const w = store.weather
      store.pushToast(
        '今天天气：' + w.text + '，' + w.temp + '°C，' + w.wind +
        '，适合带' + store.activePet.name + '晒太阳 ☀️'
      )
      break
    }
  }
}

function onVolInput(e) {
  const v = parseInt(e.target.value, 10)
  store.setVolume(v)
}

function onVolChange(e) {
  store.commitVolume()
  store.pushToast('音量已调节至 ' + e.target.value + '%')
}
</script>
