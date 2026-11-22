# PetOS · AI Companion PC 端（Vue3）

PC 端前端工程，技术栈 **Vue 3 + Vite 5 + Pinia + Vue Router 4 + Axios**。
业务数据全部通过 `src/api/` 走后端 REST；移动端 H5 在独立工程 `../mobile`，两者共用同一个 FastAPI 后端与数据库。

---

## 一、快速启动

在 `frontend` 目录下执行：

```powershell
npm install          # 首次
npm run dev          # 默认 http://localhost:5173
npm run build        # 生产构建，输出 dist/
npm run preview      # 预览构建产物
```

前置条件：Node.js ≥ 18、后端已启动在 `127.0.0.1:8080`。Vite 已配置 `/api`、`/images` 代理，无需额外处理跨域。

> 首次安装慢可切换镜像：`npm config set registry https://registry.npmmirror.com`

---

## 二、目录结构

```
frontend/
├── index.html
├── vite.config.js              # @ 别名、端口 5173、/api 与 /images 代理
├── package.json
└── src/
    ├── main.js                 # 挂载 Pinia / Router / 全局样式
    ├── App.vue                 # 侧栏 + 顶栏 + 路由出口 + 抽屉/弹窗/Toast
    ├── styles/companion.css    # 全站设计令牌与组件样式
    ├── router/index.js         # 8 条路由（hash 模式，懒加载）
    ├── config/nav.js           # 导航基线（后端异常时仍可显示菜单）
    ├── api/                    # axios 封装与接口函数
    ├── stores/companion.js     # 唯一数据源，启动拉取 /api/state
    ├── components/             # 布局、图标、抽屉、弹窗等通用组件
    └── views/                  # 8 个业务页面
```

### 页面

| 路由 | 页面 |
| --- | --- |
| `/home` | 总览首页 |
| `/pet` | 我的宠物 |
| `/chat` | 互动陪伴（含情绪风险提示） |
| `/alerts` | 守护预警（家长确认 / 处理） |
| `/device` | 设备控制 |
| `/memory` | 成长记忆 |
| `/plugin` | 插件中心 |
| `/settings` | 系统设置 |

---

## 三、数据与接口

- 统一响应壳：`{ code: 0, message: "成功", data: ... }`，`api/http.js` 自动剥壳；
- 启动时 `bootstrap()` 拉取 `/api/state` 与 `/api/nav`，写入 Pinia；交互动作先调接口再更新本地状态；
- 守护预警：`/api/chat` 返回 `risk` 与 `alert`，`GET /api/alerts` 拉取列表，`PUT /api/alerts/{id}` 提交「已知晓 / 完成处理」；
- 完整接口清单与报文示例见 [`../backend/docs/API.md`](../backend/docs/API.md)。

---

## 四、常见问题

**页面空白 / 接口 500？**
确认后端 `8080` 已启动；端口被占用时以 Vite 终端打印的 `Local:` 地址为准。

**聊天回复是固定话术？**
后端未配置大模型时使用内置兜底话术，在 `backend/.env` 配置模型后自动切换。

**摄像头黑屏？**
未配置 `camera.streamUrl` 或 `VITE_CAM_STREAM_URL` 时显示占位图，属正常。
