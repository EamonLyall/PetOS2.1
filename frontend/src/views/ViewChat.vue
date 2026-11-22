<template>
  <div class="view is-active" data-view="互动陪伴">
    <div class="page-head">
      <span class="page-head__ico"><AppIcon name="chat" /></span>
      <div>
        <h1>互动陪伴</h1>
        <p>陪它聊聊天、玩玩游戏，让每一天都有笑声</p>
      </div>
    </div>

    <div class="info-grid info-grid--2">
      <!-- 陪伴数据统计 + 趋势图 -->
      <article class="card">
        <div class="card__hd">
          <span class="card__badge"><AppIcon name="chart" /></span>
          <h2 class="card__title">陪伴数据统计</h2>
          <div class="card__aside">
            <div class="seg" role="tablist">
              <button
                v-for="opt in segOptions"
                :key="opt.key"
                type="button"
                :class="{ 'is-active': store.ui.range === opt.key }"
                @click="store.ui.range = opt.key"
              >{{ opt.label }}</button>
            </div>
          </div>
        </div>

        <div class="chart">
          <div class="chart__legend">
            <span><i class="legend-dot legend-dot--blue"></i>互动次数</span>
            <span><i class="legend-dot legend-dot--violet"></i>在线时长</span>
          </div>

          <svg viewBox="0 0 640 238" role="img" aria-label="陪伴数据趋势图">
            <defs>
              <linearGradient id="areaBlue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#5b8df6" stop-opacity=".22" />
                <stop offset="100%" stop-color="#5b8df6" stop-opacity="0" />
              </linearGradient>
              <linearGradient id="areaViolet" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#9a8cf5" stop-opacity=".16" />
                <stop offset="100%" stop-color="#9a8cf5" stop-opacity="0" />
              </linearGradient>
              <linearGradient id="strokeBlue" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stop-color="#6ea8ff" />
                <stop offset="100%" stop-color="#3f7cf5" />
              </linearGradient>
              <linearGradient id="strokeViolet" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stop-color="#bcb0ff" />
                <stop offset="100%" stop-color="#8b78f0" />
              </linearGradient>
            </defs>

            <!-- 横向网格线 + 纵轴刻度 -->
            <g>
              <template v-for="g in gridLines" :key="g.v">
                <line class="grid-line" x1="46" x2="630" :y1="g.y" :y2="g.y" />
                <text class="axis-text" x="34" :y="g.y + 3.5" text-anchor="end">{{ g.v }}</text>
              </template>
            </g>

            <!-- X 轴标签 -->
            <g>
              <text
                v-for="(x, i) in xLabels"
                :key="i"
                class="axis-text axis-text--x"
                :x="x.x"
                y="222"
                text-anchor="middle"
              >{{ x.l }}</text>
            </g>

            <!-- 面积 -->
            <path :d="areaI" fill="url(#areaBlue)" />
            <path :d="areaO" fill="url(#areaViolet)" />

            <!-- 折线（带入场描边动画） -->
            <path ref="lineIEl" class="line line--blue" :d="lineI" />
            <path ref="lineOEl" class="line line--violet" :d="lineO" />

            <!-- 数据点 -->
            <g>
              <template v-for="(d, i) in dots" :key="i">
                <circle :cx="d.cx" :cy="d.cy" r="9" fill="transparent">
                  <title>互动 {{ d.v }} 次</title>
                </circle>
                <circle
                  :cx="d.cx" :cy="d.cy" r="3.4"
                  fill="#fff" stroke="#4a80f0" stroke-width="2"
                />
              </template>
            </g>
          </svg>
        </div>
      </article>

      <!-- 快速互动 -->
      <article class="card">
        <div class="card__hd">
          <span class="card__badge card__badge--amber"><AppIcon name="bolt" /></span>
          <h2 class="card__title">快速互动</h2>
        </div>
        <div class="quick-grid">
          <button class="quick" type="button" @click="store.interact('pet')">
            <span class="quick__ico"><AppIcon name="hand" /></span>
            <span>抚摸互动</span>
          </button>
          <button class="quick" type="button" @click="store.interact('voice')">
            <span class="quick__ico quick__ico--mint"><AppIcon name="mic" /></span>
            <span>语音对话</span>
          </button>
          <button class="quick" type="button" @click="store.interact('game')">
            <span class="quick__ico quick__ico--violet"><AppIcon name="game" /></span>
            <span>趣味游戏</span>
          </button>
          <button class="quick" type="button" @click="store.interact('music')">
            <span class="quick__ico quick__ico--amber"><AppIcon name="music" /></span>
            <span>播放音乐</span>
          </button>
        </div>
      </article>
    </div>

    <!-- 聊天 -->
    <section class="grid">
      <article class="card">
        <div class="card__hd">
          <span class="card__badge card__badge--violet"><AppIcon name="robot" /></span>
          <h2 class="card__title">和小宠聊聊天</h2>
          <div class="card__aside">
            <span class="badge-online"><i class="dot dot--on"></i>在线</span>
          </div>
        </div>

        <div
          v-if="store.latestRisk.level === 'warning' || store.latestRisk.level === 'critical'"
          class="chat-risk"
          :class="'chat-risk--' + store.latestRisk.level"
          role="status"
          aria-live="polite"
        >
          <AppIcon name="health" />
          <div>
            <b>{{ store.latestRisk.summary }}</b>
            <p>{{ store.latestRisk.guidance }}</p>
            <router-link :to="{ name: 'alerts' }">查看守护预警</router-link>
          </div>
        </div>

        <div class="chat">
          <div ref="chatBody" class="chat__body">
            <div
              v-for="(m, i) in store.chatMessages"
              :key="i"
              class="chat__msg"
              :class="{ 'chat__msg--me': m.who === 'me' }"
            >
              <span class="chat__ava">
                <AppIcon :name="m.who === 'me' ? 'user' : 'paw'" />
              </span>
              <div class="chat__bubble">{{ m.text }}</div>
            </div>
          </div>

          <div class="chat__foot">
            <input
              v-model="draft"
              type="text"
              placeholder="和小宠说点什么…"
              autocomplete="off"
              aria-label="输入消息"
              @keydown.enter="doSend"
            />
            <button class="chat__send" type="button" @click="doSend">发送</button>
          </div>
        </div>
      </article>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useCompanionStore } from '@/stores/companion'
import AppIcon from '@/components/AppIcon.vue'

const store = useCompanionStore()
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

const segOptions = [
  { key: 'week', label: '近一周' },
  { key: 'month', label: '近一月' },
  { key: 'quarter', label: '近三月' }
]

// —— 图表几何计算（坐标常量与原型一致）——
const X0 = 46, X1 = 630, Y0 = 16, Y1 = 196
function xAt(i, n) {
  return n === 1 ? (X0 + X1) / 2 : X0 + (X1 - X0) * i / (n - 1)
}
function yAt(v) {
  return Y1 - (Y1 - Y0) * v / 100
}
// 平滑曲线路径（Catmull-Rom 转三次贝塞尔，张力 t=.18）
function smoothPath(pts) {
  if (pts.length < 2) return ''
  let s = 'M ' + pts[0][0].toFixed(1) + ' ' + pts[0][1].toFixed(1)
  for (let i = 0; i < pts.length - 1; i++) {
    const p0 = pts[i - 1] || pts[i], p1 = pts[i], p2 = pts[i + 1], p3 = pts[i + 2] || p2, t = .18
    s += ' C ' +
      (p1[0] + (p2[0] - p0[0]) * t).toFixed(1) + ' ' + (p1[1] + (p2[1] - p0[1]) * t).toFixed(1) + ', ' +
      (p2[0] - (p3[0] - p1[0]) * t).toFixed(1) + ' ' + (p2[1] - (p3[1] - p1[1]) * t).toFixed(1) + ', ' +
      p2[0].toFixed(1) + ' ' + p2[1].toFixed(1)
  }
  return s
}

// 趋势图数据来自后端快照（store.charts），按当前区间取对应一组
const chartData = computed(() => store.charts[store.ui.range] || { labels: [], interact: [], online: [] })
const count = computed(() => chartData.value.labels.length)
const ptsI = computed(() => chartData.value.interact.map((v, i) => [xAt(i, count.value), yAt(v)]))
const ptsO = computed(() => chartData.value.online.map((v, i) => [xAt(i, count.value), yAt(v)]))

const lineI = computed(() => smoothPath(ptsI.value))
const lineO = computed(() => smoothPath(ptsO.value))
const areaI = computed(() => {
  if (ptsI.value.length === 0) return ''
  return lineI.value + ' L ' + ptsI.value[ptsI.value.length - 1][0].toFixed(1) + ' ' + Y1 +
    ' L ' + ptsI.value[0][0].toFixed(1) + ' ' + Y1 + ' Z'
})
const areaO = computed(() => {
  if (ptsO.value.length === 0) return ''
  return lineO.value + ' L ' + ptsO.value[ptsO.value.length - 1][0].toFixed(1) + ' ' + Y1 +
    ' L ' + ptsO.value[0][0].toFixed(1) + ' ' + Y1 + ' Z'
})

const gridLines = computed(() =>
  [100, 75, 50, 25, 0].map(v => ({ v, y: yAt(v) }))
)
const xLabels = computed(() =>
  chartData.value.labels.map((l, i) => ({ l, x: xAt(i, count.value).toFixed(1) }))
)
const dots = computed(() =>
  ptsI.value.map((p, i) => ({
    cx: p[0].toFixed(1), cy: p[1].toFixed(1), v: chartData.value.interact[i]
  }))
)

// 折线入场描边动画
const lineIEl = ref(null)
const lineOEl = ref(null)
function playAnim() {
  if (reduceMotion) return
  nextTick(() => {
    [lineIEl.value, lineOEl.value].forEach(p => {
      if (!p) return
      const len = p.getTotalLength()
      p.style.transition = 'none'
      p.style.strokeDasharray = len
      p.style.strokeDashoffset = len
      requestAnimationFrame(() => {
        p.style.transition = 'stroke-dashoffset .9s cubic-bezier(.4,0,.2,1)'
        p.style.strokeDashoffset = 0
      })
    })
  })
}
onMounted(playAnim)
watch(() => store.ui.range, playAnim)

// —— 聊天 ——
const draft = ref('')
const chatBody = ref(null)
async function doSend() {
  const text = draft.value
  if (!text.trim()) return
  draft.value = ''
  await store.sendChat(text)
}
watch(() => store.chatMessages.length, () => {
  nextTick(() => {
    if (chatBody.value) chatBody.value.scrollTop = chatBody.value.scrollHeight
  })
})
</script>
