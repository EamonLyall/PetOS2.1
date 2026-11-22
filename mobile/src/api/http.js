// ============================================================
// 前端 HTTP 请求封装（axios）。
//
// 设计说明：
//   - baseURL 取环境变量 VITE_API_BASE（开发环境为 /api），经 Vite 代理转发到后端 8080；
//   - 后端统一响应壳为 { code, message, data }，这里在响应拦截器里统一解包：
//     code === 0 直接返回 data；否则抛出带 message 的错误，由调用方 Toast 提示；
//   - 不在这里写任何本地兜底数据，接口失败就如实报错，保证页面数据全部来自后端数据库。
// ============================================================

import axios from 'axios'

// 后端接口前缀（.env.development 中 VITE_API_BASE=/api）
const baseURL = import.meta.env.VITE_API_BASE || '/api'

const http = axios.create({
  baseURL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' }
})

// 响应拦截器：统一解包后端响应壳
http.interceptors.response.use(
  (response) => {
    const body = response.data
    // 后端正常返回 { code, message, data }
    if (body && typeof body === 'object' && 'code' in body) {
      if (body.code === 0) return body.data
      const err = new Error(body.message || '请求失败')
      err.code = body.code
      throw err
    }
    // 其它情况（如静态文件）原样返回
    return body
  },
  (error) => {
    // 网络错误 / 超时 / 5xx 统一转成 Error，便于上层捕获
    const message =
      error.response?.data?.message ||
      error.message ||
      '网络异常，请确认后端服务已启动'
    throw new Error(message)
  }
)

export default http
