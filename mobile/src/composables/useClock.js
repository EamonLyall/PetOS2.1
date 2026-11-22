import { ref } from 'vue'

// 模块级单例：全局只维护一个定时器，多个组件共享同一份时间
const hm = ref('--:--')      // 顶栏：时:分
const hms = ref('--:--:--')  // AI 能力区：时:分:秒
let started = false

function pad(n) {
  return n < 10 ? '0' + n : '' + n
}

function tick() {
  const d = new Date()
  hm.value = pad(d.getHours()) + ':' + pad(d.getMinutes())
  hms.value = hm.value + ':' + pad(d.getSeconds())
}

export function useClock() {
  if (!started) {
    started = true
    tick()
    setInterval(tick, 1000)
  }
  return { hm, hms }
}
