import { createRouter, createWebHashHistory } from 'vue-router'

// 移动端 H5 路由（hash 模式，便于静态部署与手机端演示）
const routes = [
  { path: '/', redirect: '/home' },
  { path: '/home', name: 'home', component: () => import('@/views/ViewHome.vue') },
  { path: '/pet', name: 'pet', component: () => import('@/views/ViewPet.vue') },
  { path: '/chat', name: 'chat', component: () => import('@/views/ViewChat.vue') },
  { path: '/alerts', name: 'alerts', component: () => import('@/views/ViewAlerts.vue') },
  { path: '/mine', name: 'mine', component: () => import('@/views/ViewMine.vue') },
  { path: '/device', name: 'device', component: () => import('@/views/ViewDevice.vue') },
  { path: '/memory', name: 'memory', component: () => import('@/views/ViewMemory.vue') },
  { path: '/plugin', name: 'plugin', component: () => import('@/views/ViewPlugin.vue') },
  { path: '/settings', name: 'settings', component: () => import('@/views/ViewSettings.vue') }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

export default router
