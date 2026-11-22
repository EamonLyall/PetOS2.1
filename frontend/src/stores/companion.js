// ============================================================
// PetOS 宠物陪伴 · 全局状态（Pinia）。
//
// 数据来源：全部来自后端 FastAPI 接口（数据库），不再使用本地 mock 种子。
// 启动时由 App.vue 调用 bootstrap() 一次性拉取 /api/state 快照填充；
// 后续交互动作（连接设备、聊天、插件开关、打卡、设置变更）先调接口，
// 成功后再更新本地响应式状态，保证页面展示与数据库一致。
//
// 说明：store.IMG 仅为前端打包的本地占位图片资源，不属于业务 mock 数据。
// ============================================================

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import catBanner from '../../../shared/images/cat-banner.jpg'
import kittenSquare from '../../../shared/images/kitten-square.jpg'
import { NAV_ITEMS, FALLBACK_DEVICE } from '@/config/nav'
import * as api from '@/api'

// 本地图片资源（打包进前端，用于头像 / 摄像头占位 / 照片墙兜底）
const IMG = { cat: catBanner, kitten: kittenSquare }

// 空数据兜底：接口未返回时保证模板读取不报错
const EMPTY_PET = {
  petKey: '', name: '未命名', emoji: '🐾', breed: '-', age: '-', weight: '-',
  level: 1, growth: 0, mood: '-', active: 0, interact: 0, days: 0, desc: '',
  heartRate: 0, activeMinutes: 0, sleepHours: 0, lastCheckup: '-',
  moments: 0, songs: 0, games: 0,
  // 数据库扩展字段（我的宠物页健康/状态卡片）
  energy: 0, moodTag: '-', healthStatus: '-'
}

// 空设置兜底：后端 settings 未返回对应分组时保证模板读取不报错
const EMPTY_NETWORK = { bluetooth: true, wifiQuality: '-', firmwareLatest: true }
const EMPTY_DEVICE_OPTS = { mic: true, micSensitivity: 0, gimbal: true, motion: true, motionSensitivity: '-' }
const EMPTY_NOTIFY = { message: true, motion: true, cloudSync: true }
const EMPTY_PROFILE = { language: '简体中文', account: '主人', appVersion: '-' }
const EMPTY_CAMERA = { resolution: '-', fps: 0, nightVision: true, motionDetect: true, twoWayAudio: true, streamUrl: '' }

export const useCompanionStore = defineStore('companion', () => {
  // —— 业务数据（初始为空，bootstrap 后由后端填充）——
  const devices = ref([])        // 已绑定设备
  const nearby = ref([])         // 附近未配对设备
  const pets = ref({})           // 宠物档案，按 petKey 索引
  const weather = ref({ text: '-', temp: 0, wind: '-' })
  const charts = ref({})         // 趋势图 { week, month, quarter }
  const plugins = ref([])        // 插件清单
  const timeline = ref([])       // 成长时间线
  const milestones = ref([])     // 里程碑统计
  const gallery = ref([])        // 照片墙
  // 侧边导航：以前端配置为基线，后端 /api/nav 正常返回时再覆盖，
  // 避免后端未启动时左侧菜单整体消失（历史 bug）
  const nav = ref([...NAV_ITEMS])

  // —— 连接与当前设备 ——
  const connected = ref(false)
  const activeDeviceId = ref(null)

  // —— 语音 / 表情屏 / 音乐 ——
  const voice = ref({ wakeWord: '小宠小宠', listening: false, tts: true, volume: 70 })
  const screen = ref({ on: true, expression: '开心' })
  const music = ref({ playing: false, track: '午后猫咪轻音乐' })

  // —— 数据库设置分组（全部来自 app_setting 表，前端不再写死）——
  const network = ref({ ...EMPTY_NETWORK })      // 蓝牙 / Wi-Fi 质量 / 固件状态
  const deviceOpts = ref({ ...EMPTY_DEVICE_OPTS }) // 麦克风 / 云台 / 移动侦测
  const notify = ref({ ...EMPTY_NOTIFY })        // 消息 / 移动侦测 / 云同步
  const profile = ref({ ...EMPTY_PROFILE })      // 语言 / 账户 / 版本
  const camera = ref({ ...EMPTY_CAMERA })        // 摄像头分辨率 / 帧率 / 能力

  // —— 通知中心（数据库 notification 表）——
  const notifications = ref([])
  const unreadCount = computed(() => notifications.value.filter(n => !n.read).length)

  // 情绪守护预警与最近一次聊天风险评估（均来自后端）
  const alerts = ref([])
  const latestRisk = ref({ level: 'none', category: 'none', summary: '', guidance: '' })
  const openAlertCount = computed(() => alerts.value.filter(a => a.status !== 'resolved').length)
  const pendingAlertCount = computed(() => alerts.value.filter(a => a.status === 'pending').length)

  // —— 浮层 / 界面状态（纯前端交互态，不走后端）——
  const ui = ref({
    aiOpen: false,
    drawer: false,
    cam: false,
    notif: false,
    menu: false,
    range: 'week'
  })

  // —— 数据加载状态 ——
  const loaded = ref(false)
  const loading = ref(false)

  // —— Toast 轻提示（最多保留 3 条）——
  const toasts = ref([])
  let toastSeq = 0
  function pushToast(msg) {
    const id = ++toastSeq
    toasts.value.push({ id, msg })
    while (toasts.value.length > 3) toasts.value.shift()
    setTimeout(() => {
      toasts.value = toasts.value.filter(t => t.id !== id)
    }, 2400)
  }

  // —— 聊天记录 / 今日小确幸 ——
  const chatMessages = ref([])
  const blessList = ref([])

  // ============================================================
  // 派生：当前设备与对应宠物（带空值兜底，避免加载中模板报错）
  // ============================================================
  const activeDevice = computed(() => {
    return (
      devices.value.find(d => d.id === activeDeviceId.value) ||
      devices.value[0] ||
      { ...FALLBACK_DEVICE }
    )
  })

  const activePet = computed(() => {
    const key = activeDevice.value.petKey
    return (key && pets.value[key]) || EMPTY_PET
  })

  // ============================================================
  // 设置合并：把后端 settings 的各个分组写入本地状态
  // ============================================================
  function applySettings(s) {
    if (!s) return
    connected.value = !!s.connected
    activeDeviceId.value = s.activeDeviceId || activeDeviceId.value
    if (s.voice) voice.value = { ...voice.value, ...s.voice }
    if (s.screen) screen.value = { ...screen.value, ...s.screen }
    if (s.music) music.value = { ...music.value, ...s.music }
    if (s.network) network.value = { ...network.value, ...s.network }
    if (s.device) deviceOpts.value = { ...deviceOpts.value, ...s.device }
    if (s.notify) notify.value = { ...notify.value, ...s.notify }
    if (s.profile) profile.value = { ...profile.value, ...s.profile }
    if (s.camera) camera.value = { ...camera.value, ...s.camera }
  }

  // ============================================================
  // 初始化：从后端拉取全量快照
  // 使用 allSettled 分别处理：任一接口失败都不会让整个页面数据清空
  // ============================================================
  async function bootstrap() {
    if (loading.value) return
    loading.value = true
    try {
      const [stateRes, navRes] = await Promise.allSettled([api.fetchState(), api.fetchNav()])

      if (stateRes.status === 'fulfilled') {
        const state = stateRes.value || {}
        devices.value = state.devices || []
        nearby.value = state.nearby || []
        pets.value = state.pets || {}
        weather.value = state.weather || weather.value
        charts.value = state.charts || {}
        plugins.value = state.plugins || []
        timeline.value = state.timeline || []
        milestones.value = state.milestones || []
        gallery.value = state.gallery || []
        chatMessages.value = state.chatMessages || []
        blessList.value = state.blessList || []
        notifications.value = state.notifications || []
        alerts.value = state.alerts || []
        applySettings(state.settings)
        loaded.value = true
      } else {
        // 后端不可用时明确提示，但保留前端导航与空态兜底，页面不会白屏
        pushToast('数据加载失败：' + (stateRes.reason?.message || '请确认后端服务已启动'))
      }

      // 后端导航接口正常且结构合法时才覆盖前端基线配置
      if (navRes.status === 'fulfilled' && Array.isArray(navRes.value) && navRes.value.length) {
        nav.value = navRes.value
      }
    } finally {
      loading.value = false
    }
  }

  // ============================================================
  // 设置变更：调后端局部更新，成功后合并返回的最新设置
  // ============================================================
  async function persistSettings(partial) {
    const data = await api.updateSettings(partial)
    if (!data) return
    applySettings(data)
  }

  // ============================================================
  // 通用开关：更新数据库设置里的某个布尔项（用于设置页 / 设备页）
  // group 取值：network / device / notify，key 为分组内字段名
  // ============================================================
  async function toggleOption(group, key) {
    const map = { network, device: deviceOpts, notify }
    const target = map[group]
    if (!target) return
    const next = !target.value[key]
    try {
      await persistSettings({ [group]: { [key]: next } })
      pushToast(labelOf(group, key) + (next ? ' · 已开启' : ' · 已关闭'))
    } catch (err) {
      pushToast('设置保存失败：' + err.message)
    }
  }

  // 开关中文名（Toast 文案）
  function labelOf(group, key) {
    const labels = {
      'network.bluetooth': '蓝牙',
      'device.mic': '麦克风',
      'device.gimbal': '云台舵机',
      'device.motion': '移动侦测',
      'notify.message': '消息通知',
      'notify.motion': '移动侦测提醒',
      'notify.cloudSync': '数据云端同步',
      'voice.tts': '语音回复'
    }
    return labels[group + '.' + key] || key
  }

  // ============================================================
  // 设备动作
  // ============================================================

  // 连接 / 配对设备：已绑定直接切换；附近设备先配对入库再连
  async function connectDevice(id) {
    let d = devices.value.find(x => x.id === id)
    const isNew = !d
    try {
      const data = await api.connectDevice(id)
      d = data.device
      // 附近设备配对成功后，从附近列表移入已绑定列表
      if (isNew && d) {
        nearby.value = nearby.value.filter(x => x.id !== id)
        if (!devices.value.find(x => x.id === id)) devices.value.push(d)
      }
      activeDeviceId.value = id
      connected.value = true
      // 后端顺带返回了对应宠物档案，合并进 pets
      if (data.pet) pets.value = { ...pets.value, [data.pet.petKey]: data.pet }
      const petName = data.pet ? data.pet.name : (pets.value[d.petKey]?.name || '')
      pushToast((isNew ? '已配对并连接 ' : '已连接 ') + d.name + ' · 正在同步「' + petName + '」档案')
    } catch (err) {
      pushToast('连接失败：' + err.message)
    }
  }

  // 断开连接（设备本身在线标记不变，与原型行为一致）
  async function disconnect() {
    const id = activeDeviceId.value
    if (!id) return
    try {
      await api.disconnectDevice(id)
      connected.value = false
      pushToast('已断开设备连接，可随时在设备中心重新连接')
    } catch (err) {
      pushToast('断开失败：' + err.message)
    }
  }

  // 重新扫描附近设备
  async function rescan() {
    try {
      const data = await api.scanDevices()
      nearby.value = data.nearby || []
      pushToast('已重新扫描，发现 ' + nearby.value.length + ' 台可用设备')
    } catch (err) {
      pushToast('扫描失败：' + err.message)
    }
  }

  // ============================================================
  // 语音 / 屏幕 / 音乐（持久化到后端设置）
  // ============================================================

  // 语音唤醒：纯前端聆听态，3.2 秒后自动结束
  function toggleWake() {
    voice.value.listening = !voice.value.listening
    if (voice.value.listening) {
      pushToast('已唤醒「' + voice.value.wakeWord + '」，我在听～')
      setTimeout(() => {
        if (voice.value.listening) {
          voice.value.listening = false
          pushToast('收到指令，已为你记录本次互动 🐾')
        }
      }, 3200)
    }
  }

  // 音乐播放 / 暂停
  async function toggleMusic() {
    const playing = !music.value.playing
    try {
      await persistSettings({ music: { playing } })
      pushToast(playing ? '▶ 开始播放「' + music.value.track + '」' : '⏸ 音乐已暂停')
    } catch (err) {
      pushToast('操作失败：' + err.message)
    }
  }

  // 语音回复开关
  async function toggleTts() {
    const tts = !voice.value.tts
    try {
      await persistSettings({ voice: { tts } })
      pushToast('语音回复已' + (tts ? '开启' : '关闭'))
    } catch (err) {
      pushToast('操作失败：' + err.message)
    }
  }

  // 表情屏开关
  async function toggleScreen() {
    const on = !screen.value.on
    try {
      await persistSettings({ screen: { on } })
    } catch (err) {
      pushToast('操作失败：' + err.message)
    }
  }

  // 音量拖动：先更新本地显示，松手时由 commitVolume 提交后端
  function setVolume(v) {
    voice.value.volume = v
  }

  // 松手后把音量提交到后端设置
  async function commitVolume() {
    try {
      await persistSettings({ voice: { volume: voice.value.volume } })
    } catch (err) {
      pushToast('音量保存失败：' + err.message)
    }
  }

  // ============================================================
  // 聊天：发送消息并接收后端（大模型 / 兜底）回复
  // ============================================================
  async function sendChat(text) {
    const content = (text || '').trim()
    if (!content) return
    // 先把主人消息上屏
    chatMessages.value.push({ who: 'me', text: content })
    try {
      const data = await api.sendChatMessage({
        text: content,
        deviceId: activeDeviceId.value,
        messages: chatMessages.value.map(({ who, text: t }) => ({ who, text: t }))
      })
      chatMessages.value.push({ who: 'pet', text: data.reply })
      latestRisk.value = data.risk || latestRisk.value
      if (data.alert) upsertAlert(data.alert)
      if (data.notifications) notifications.value = data.notifications
      if (data.alert) {
        pushToast(data.alert.level === 'critical' ? '已生成紧急守护预警，请家长立即查看' : '已通知家长端持续关注情绪状态')
      }
    } catch (err) {
      pushToast('发送失败：' + err.message)
    }
  }

  // ============================================================
  // 今日小确幸打卡
  // ============================================================
  async function toggleBless(index) {
    const item = blessList.value[index]
    if (!item) return
    try {
      const data = await api.toggleBless(item.id)
      blessList.value[index] = data
      if (data.done) pushToast('又完成一项小确幸 🐾')
    } catch (err) {
      pushToast('打卡失败：' + err.message)
    }
  }

  // ============================================================
  // 快速互动：写入数据库（今日互动次数 +1），并刷新当前宠物档案
  // ============================================================
  const INTERACT_TOAST = {
    pet: '已开启抚摸互动，小猫正在呼噜呼噜～',
    voice: '语音对话已就绪，说点什么吧',
    game: '正在进入趣味游戏：逗猫棒大作战',
    music: '音乐已开始播放'
  }

  async function interact(action) {
    const petKey = activePet.value.petKey
    if (!petKey) {
      pushToast('请先连接设备后再互动')
      return
    }
    try {
      const data = await api.sendInteraction(petKey, action)
      if (data && data.pet) {
        pets.value = { ...pets.value, [data.pet.petKey]: data.pet }
      }
      if (action === 'music') await toggleMusic()
      pushToast(data?.message || INTERACT_TOAST[action] || '互动成功')
    } catch (err) {
      pushToast('互动失败：' + err.message)
    }
  }

  // ============================================================
  // 通知中心：全部已读（写数据库）
  // ============================================================
  async function markAllRead() {
    try {
      const data = await api.markNotificationsRead()
      notifications.value = data.notifications || notifications.value.map(n => ({ ...n, read: true }))
      pushToast('通知已全部标为已读')
    } catch (err) {
      pushToast('操作失败：' + err.message)
    }
  }

  // ============================================================
  // 情绪守护预警：PC / H5 共用后端记录
  // ============================================================
  function upsertAlert(alert) {
    const statusOrder = { pending: 0, acknowledged: 1, resolved: 2 }
    alerts.value = [alert, ...alerts.value.filter(a => a.id !== alert.id)]
      .sort((a, b) => statusOrder[a.status] - statusOrder[b.status] || b.id - a.id)
  }

  async function refreshAlerts() {
    const [alertData, notificationData] = await Promise.all([api.fetchAlerts(), api.fetchNotifications()])
    alerts.value = alertData.alerts || []
    notifications.value = notificationData.notifications || []
  }

  async function updateAlertStatus(id, status, handleNote = '') {
    try {
      const data = await api.updateAlert(id, { status, handleNote })
      upsertAlert(data.alert)
      pushToast(status === 'resolved' ? '预警已标记为处理完成' : '已确认知晓，记得继续跟进')
      return true
    } catch (err) {
      pushToast('预警更新失败：' + err.message)
      return false
    }
  }

  // ============================================================
  // 插件开关
  // ============================================================
  async function togglePlugin(p) {
    try {
      const data = await api.togglePlugin(p.id)
      const idx = plugins.value.findIndex(x => x.id === data.id)
      if (idx >= 0) plugins.value[idx] = data
      pushToast('切换' + data.n + (data.on ? ' · 已开启' : ' · 已关闭'))
    } catch (err) {
      pushToast('插件切换失败：' + err.message)
    }
  }

  return {
    IMG, devices, nearby, pets, weather, charts, plugins, timeline, milestones,
    gallery, nav, connected, activeDeviceId, voice, screen, music, ui,
    network, deviceOpts, notify, profile, camera, notifications, unreadCount,
    alerts, latestRisk, openAlertCount, pendingAlertCount,
    loaded, loading, toasts, chatMessages, blessList,
    activeDevice, activePet,
    bootstrap, pushToast, connectDevice, disconnect, rescan,
    toggleWake, toggleMusic, toggleTts, toggleScreen,
    setVolume, commitVolume, sendChat, toggleBless, togglePlugin, persistSettings,
    toggleOption, interact, markAllRead, refreshAlerts, updateAlertStatus
  }
})
