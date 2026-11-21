// ============================================================
// 后端接口清单：与后端 FastAPI 路由一一对应。
// 所有函数返回后端响应壳解包后的 data 部分（见 http.js 拦截器）。
// 路径前缀 /api 由 http.js 的 baseURL 统一处理，这里只写相对路径。
// ============================================================

import http from './http'

// ---------- 全局快照 ----------

// 一次性拉取设备 / 宠物 / 天气 / 图表 / 聊天 / 打卡 / 插件 / 记忆等全部数据
export function fetchState() {
  return http.get('/state')
}

// 侧边导航配置
export function fetchNav() {
  return http.get('/nav')
}

// ---------- 设备 ----------

// 已绑定设备列表
export function fetchDevices() {
  return http.get('/devices')
}

// 附近可配对设备
export function fetchNearbyDevices() {
  return http.get('/devices/nearby')
}

// 连接 / 配对设备
export function connectDevice(deviceId) {
  return http.post(`/devices/${deviceId}/connect`)
}

// 断开设备连接
export function disconnectDevice(deviceId) {
  return http.post(`/devices/${deviceId}/disconnect`)
}

// 重新扫描附近设备
export function scanDevices() {
  return http.post('/devices/scan')
}

// ---------- 宠物 / 记忆 ----------

// 宠物档案
export function fetchPetProfile(petKey) {
  return http.get(`/pets/${petKey}/profile`)
}

// 陪伴趋势（week / month / quarter）
export function fetchPetStats(petKey, range) {
  return http.get(`/pets/${petKey}/stats`, { params: { range } })
}

// 快速互动：action 取值 pet / voice / game / music
// 后端会自增今日互动次数并返回最新宠物档案，保证前端展示与数据库一致
export function sendInteraction(petKey, action) {
  return http.post(`/pets/${petKey}/interact`, { action })
}

// ---------- 通知中心 ----------

// 通知列表（含未读数）
export function fetchNotifications() {
  return http.get('/notifications')
}

// 全部标记为已读
export function markNotificationsRead() {
  return http.put('/notifications/read')
}

// ---------- 聊天 ----------

// 历史聊天记录
export function fetchChatMessages() {
  return http.get('/chat/messages')
}

// 发送消息并获取小宠回复；入参 { text, deviceId, messages }
export function sendChatMessage(payload) {
  return http.post('/chat', payload)
}

// ---------- 插件 ----------

// 插件清单
export function fetchPlugins() {
  return http.get('/plugins')
}

// 切换插件启用状态
export function togglePlugin(pluginId) {
  return http.put(`/plugins/${pluginId}/toggle`)
}

// ---------- 打卡 ----------

// 小确幸清单
export function fetchBless() {
  return http.get('/bless')
}

// 切换打卡完成状态
export function toggleBless(itemId) {
  return http.put(`/bless/${itemId}/toggle`)
}

// ---------- 设置 ----------

// 读取全局设置（语音 / 表情屏 / 音乐 / 连接状态）
export function fetchSettings() {
  return http.get('/settings')
}

// 局部更新设置；payload 形如 { voice: { volume: 70 }, screen: { on: true } }
export function updateSettings(payload) {
  return http.put('/settings', payload)
}
