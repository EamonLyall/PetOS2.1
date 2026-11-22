<template>
  <div class="view is-active" data-view="守护预警">
    <div class="page-head">
      <span class="page-head__ico"><AppIcon name="health" /></span>
      <div>
        <h1>守护预警</h1>
        <p>及时发现情绪风险，让关心不缺席</p>
      </div>
      <button class="btn-ghost alert-refresh" type="button" :disabled="refreshing" @click="loadAlerts(true)">
        <AppIcon name="refresh" />{{ refreshing ? '刷新中' : '刷新' }}
      </button>
    </div>

    <div class="alert-disclaimer">
      <AppIcon name="info" />
      <span>预警仅为风险提示，不是医学诊断。若有即时人身危险，请立即联系当地急救/警方（120/110）。</span>
    </div>

    <section class="alert-summary" aria-label="预警统计">
      <article class="alert-stat">
        <span class="alert-stat__ico alert-stat__ico--amber"><AppIcon name="bell" /></span>
        <div><b>{{ store.pendingAlertCount }}</b><span>待家长确认</span></div>
      </article>
      <article class="alert-stat">
        <span class="alert-stat__ico alert-stat__ico--red"><AppIcon name="health" /></span>
        <div><b>{{ criticalCount }}</b><span>未处理紧急预警</span></div>
      </article>
      <article class="alert-stat">
        <span class="alert-stat__ico alert-stat__ico--mint"><AppIcon name="check" /></span>
        <div><b>{{ resolvedCount }}</b><span>已完成处理</span></div>
      </article>
    </section>

    <div class="alert-toolbar">
      <h2>预警记录</h2>
      <div class="seg" role="tablist" aria-label="按状态筛选">
        <button
          v-for="option in filters"
          :key="option.key"
          type="button"
          :class="{ 'is-active': filter === option.key }"
          @click="filter = option.key"
        >{{ option.label }}</button>
      </div>
    </div>

    <section v-if="filteredAlerts.length" class="alert-list" aria-live="polite">
      <article
        v-for="alert in filteredAlerts"
        :key="alert.id"
        class="alert-card"
        :class="[`alert-card--${alert.level}`, { 'alert-card--resolved': alert.status === 'resolved' }]"
      >
        <div class="alert-card__hd">
          <span class="alert-card__ico"><AppIcon :name="alert.level === 'critical' ? 'health' : 'heart'" /></span>
          <div class="alert-card__heading">
            <div>
              <span class="alert-card__level">{{ alert.level === 'critical' ? '紧急预警' : '持续关注' }}</span>
              <span class="alert-card__category">{{ categoryText(alert.category) }}</span>
            </div>
            <h3>{{ alert.summary }}</h3>
          </div>
          <span class="alert-card__status" :class="'is-' + alert.status">{{ statusText(alert.status) }}</span>
        </div>

        <div v-if="alert.evidence.length" class="alert-evidence">
          <b>相关表达</b>
          <ul><li v-for="(text, index) in alert.evidence" :key="index">“{{ text }}”</li></ul>
        </div>
        <p class="alert-guidance"><b>建议：</b>{{ alert.guidance }}</p>
        <div class="alert-card__meta">
          <span><AppIcon name="clock" />{{ formatTime(alert.createdAt) }}</span>
          <span><AppIcon name="device" />{{ deviceName(alert.deviceId) }}</span>
          <span>编号 #{{ alert.id }}</span>
        </div>

        <div v-if="alert.status === 'resolved'" class="alert-result">
          <AppIcon name="check" />
          <div>
            <b>已于 {{ formatTime(alert.handledAt) }} 完成处理</b>
            <p>{{ alert.handleNote || '家长已确认并完成跟进。' }}</p>
          </div>
        </div>
        <template v-else>
          <label class="alert-note">
            <span>处理记录（可选）</span>
            <textarea
              v-model="notes[alert.id]"
              rows="2"
              maxlength="500"
              placeholder="例如：已与孩子沟通，预约学校心理老师继续跟进…"
            ></textarea>
          </label>
          <div class="alert-actions">
            <button
              v-if="alert.status === 'pending'"
              class="btn-ghost"
              type="button"
              :disabled="actingId === alert.id"
              @click="act(alert, 'acknowledged')"
            ><AppIcon name="check" />我已知晓</button>
            <button
              class="btn-primary"
              type="button"
              :disabled="actingId === alert.id"
              @click="act(alert, 'resolved')"
            ><AppIcon name="check" />{{ actingId === alert.id ? '正在保存' : '完成处理' }}</button>
          </div>
        </template>
      </article>
    </section>

    <section v-else class="alert-empty">
      <span><AppIcon :name="filter === 'all' ? 'health' : 'search'" /></span>
      <h2>{{ filter === 'all' ? '暂时没有守护预警' : '该状态下暂无记录' }}</h2>
      <p>{{ filter === 'all' ? '小宠会先陪伴和复评，持续未缓解或出现高危表达时才提醒家长。' : '可以切换其他状态查看。' }}</p>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useCompanionStore } from '@/stores/companion'
import AppIcon from '@/components/AppIcon.vue'

const store = useCompanionStore()
const filter = ref('all')
const filters = [
  { key: 'all', label: '全部' },
  { key: 'pending', label: '待确认' },
  { key: 'acknowledged', label: '跟进中' },
  { key: 'resolved', label: '已处理' }
]
const notes = ref({})
const actingId = ref(null)
const refreshing = ref(false)
let timer = null

const filteredAlerts = computed(() => filter.value === 'all'
  ? store.alerts
  : store.alerts.filter(a => a.status === filter.value))
const criticalCount = computed(() => store.alerts.filter(a => a.level === 'critical' && a.status !== 'resolved').length)
const resolvedCount = computed(() => store.alerts.filter(a => a.status === 'resolved').length)

function statusText(status) {
  return { pending: '待确认', acknowledged: '跟进中', resolved: '已处理' }[status] || status
}
function categoryText(category) {
  return { low_mood: '情绪低落', self_harm: '自伤风险', harm_others: '伤人风险' }[category] || '情绪风险'
}
function formatTime(value) {
  return value ? value.replace('T', ' ').slice(5, 16) : '-'
}
function deviceName(id) {
  return store.devices.find(d => d.id === id)?.name || '桌宠设备'
}
async function loadAlerts(showError = false) {
  if (refreshing.value) return
  refreshing.value = true
  try {
    await store.refreshAlerts()
  } catch (err) {
    if (showError) store.pushToast('预警刷新失败：' + err.message)
  } finally {
    refreshing.value = false
  }
}
async function act(alert, status) {
  actingId.value = alert.id
  await store.updateAlertStatus(alert.id, status, notes.value[alert.id] || '')
  actingId.value = null
}

onMounted(() => {
  loadAlerts(true)
  timer = window.setInterval(() => loadAlerts(false), 15000)
})
onUnmounted(() => window.clearInterval(timer))
</script>
