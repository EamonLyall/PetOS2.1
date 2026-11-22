import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// 全局样式：沿用 PC 端设计令牌与组件样式，再叠加移动端专属布局
import './styles/companion.css'
import './styles/mobile.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
