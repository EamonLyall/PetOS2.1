// ============================================================
// 侧边导航配置（前端 UI 结构，不属于业务数据）。
//
// 为什么放在前端：
//   - 导航项与前端路由 name 强绑定，属于“界面骨架”，不是数据库业务数据；
//   - 早期版本完全依赖后端 /api/nav，一旦后端未启动或该接口异常，
//     侧边栏会变成空壳（用户看到的“左侧菜单消失”），属于脆弱设计；
//   - 现在以前端配置为唯一基线，后端 /api/nav 正常返回时可覆盖，
//     保证任何情况下侧边栏都能正常渲染。
//
// 字段说明：
//   key  —— 与 router/index.js 中的路由 name 严格一致
//   name —— 侧边栏展示文案
//   icon —— IconSymbols.vue 中的图标标识（AppIcon name）
// ============================================================

export const NAV_ITEMS = [
  { key: 'home', name: '总览首页', icon: 'home' },
  { key: 'pet', name: '我的宠物', icon: 'pet' },
  { key: 'chat', name: '互动陪伴', icon: 'chat' },
  { key: 'device', name: '设备控制', icon: 'device' },
  { key: 'memory', name: '成长记忆', icon: 'memory' },
  { key: 'plugin', name: '插件中心', icon: 'plugin' },
  { key: 'settings', name: '系统设置', icon: 'settings' }
]

// 侧边栏底部“当前设备”卡片在无数据时的兜底展示
export const FALLBACK_DEVICE = {
  id: '',
  name: '未连接设备',
  petKey: '',
  place: '-',
  online: false,
  signal: 0,
  battery: 0,
  wifi: '-',
  fw: '-',
  last: ''
}
