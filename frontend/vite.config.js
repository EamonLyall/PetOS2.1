import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 5173,
    host: true, // 允许局域网内 ESP32 / 手机访问调试
    // 占位图统一放在仓库根目录 shared/images，需要允许 Vite 读取上级目录
    fs: {
      allow: [fileURLToPath(new URL('..', import.meta.url))]
    },
    proxy: {
      // 后端 REST 接口代理：开发环境把 /api 转发到后端服务，避免跨域
      '/api': {
        target: 'http://127.0.0.1:8080',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/api')
      },
      // 后端本地抓拍图片：/images 转发到后端 8080，前端 <img src="/images/xx.jpg">
      '/images': {
        target: 'http://127.0.0.1:8080',
        changeOrigin: true
      },
      // 摄像头 MJPEG 流代理（香橙派/ESP32-CAM 直出 /stream），需要时打开
      '/cam': {
        target: 'http://192.168.4.1',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/cam/, '')
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    chunkSizeWarningLimit: 900
  }
})
