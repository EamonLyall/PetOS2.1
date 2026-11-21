import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// 全局样式：原型完整样式（设计令牌 + 基础重置 + 全部组件样式）
import './styles/companion.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
