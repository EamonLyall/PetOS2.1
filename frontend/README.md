# PetOS · AI Companion 前端（Vue3 工程版）

> 由单文件原型 `../petos-companion.html` 重构而来，技术栈 **Vue 3 + Vite 5 + Pinia + Vue Router 4**。
> 业务数据已通过 `src/api/` 接入 FastAPI 后端（数据库）；**MQTT 通信、真实摄像头、浏览器端大模型** 仍为预留层。
> 原型的 7 个页面、16 项能力、视觉样式与交互全部保留，未删减业务功能。

---

## 一、技术选型说明（为什么用这套）

| 选型 | 版本 | 理由 |
| --- | --- | --- |
| Vue 3 | ^3.5 | 目前国内生态最流行、文档最多、兼容性最好；`<script setup>` 写法直观，竞赛二次上手快 |
| Vite 5 | ^5.4 | 构建快、配置简单，Node 18/20/22 均可运行，产物可直接静态部署 |
| Pinia | ^2.2 | Vue 官方推荐状态管理，替代原型里手写的 `state + subscribe/emit` |
| Vue Router 4 | ^4.4 | 7 个页面路由切换；hash 模式便于双击静态页 / 比赛现场部署 |
| Axios | ^1.7 | 统一封装后端 REST 请求，拦截器统一鉴权与错误处理 |
| MQTT.js | ^5.10 | 浏览器端连 MQTT Broker，与 ESP32 经消息总线通信 |

> 兼容性：面向 Chrome / Edge / Firefox 最新版；样式沿用原型设计令牌与响应式断点（1400 / 1180 / 960 / 760 / 560px）。

---

## 二、环境要求

- **Node.js ≥ 18**（推荐 20 或 22，本机已验证 v22.23.2）
- **npm ≥ 9**
- 一个 MQTT Broker（可选，演示模式可跳过）：本地可用 EMQX / Mosquitto；开发期浏览器连接用 `ws://`，生产用 `wss://`
- 后端服务（必需）：FastAPI 提供设备/宠物/聊天/插件/记忆等 REST 接口并落库；前端经 Vite 代理 `/api` 访问，后端未启动时页面数据为空并提示加载失败

检查环境：

```powershell
node -v
npm -v
```

---

## 三、快速启动

在 `frontend` 目录下执行：

```powershell
# 1. 安装依赖（首次）
npm install

# 2. 本地开发（默认 http://localhost:5173 ，host:true 允许手机/局域网访问）
npm run dev

# 3. 打包生产产物（输出到 dist/）
npm run build

# 4. 本地预览打包产物
npm run preview
```

> 首次 `npm install` 若网速慢，可切换淘宝镜像：
> `npm config set registry https://registry.npmmirror.com`

启动后浏览器打开终端提示的地址即可。页面默认进入「总览首页」，左侧导航可切换 7 个页面。

---

## 四、目录结构

```
frontend/
├── index.html                  # 入口 HTML（挂载 #app）
├── vite.config.js              # Vite 配置：@ 别名、/api 与 /cam 代理
├── .env.development            # 开发环境变量（后端/MQTT/大模型/摄像头地址）
├── .env.production             # 生产环境变量
├── .env.example                # 环境变量模板，复制后填写
├── package.json
└── src/
    ├── main.js                 # 应用入口：挂载 Pinia / Router / 全局样式
    ├── App.vue                 # 全局骨架：侧栏 + 顶栏 + 路由出口 + 抽屉/弹窗/Toast
    ├── styles/                 # 从原型迁移的全局样式
    │   ├── tokens.css          #   设计令牌（色彩/圆角/阴影/间距/动效）
    │   ├── base.css            #   基础重置 + 通用元件（卡片/按钮/开关/滑块/数据行）
    │   └── components.css       #   骨架/首页/子页面/弹层/动效/响应式
    ├── icons/
    │   └── symbols.js          # 全部 SVG 图标符号数据（原型 sprite 迁移）
    ├── router/
    │   └── index.js            # 7 条路由（hash 模式，懒加载）
    ├── config/
    │   └── nav.js              # 侧边导航基线配置 + 无设备兜底（后端异常也能显示菜单）
    ├── api/                     # 后端 REST 对接层（axios 封装 + 接口清单）
    │   ├── http.js              #   axios 实例、统一响应壳解包与错误处理
    │   └── index.js             #   设备/宠物/聊天/互动/插件/打卡/设置/通知接口函数
    ├── stores/                  # Pinia 状态层（唯一数据源）
    │   └── companion.js         #   启动拉取 /api/state 快照；所有交互写回后端
    ├── services/                # 外部服务封装层（预留，当前为空）
    │                            #   后续可放浏览器端 MQTT、摄像头流封装
    ├── components/              # 通用与布局组件
    │   ├── AppIcon.vue          #   图标组件
    │   ├── IconSymbols.vue      #   全局 SVG 雪碧图（只渲染一次）
    │   ├── AppSidebar.vue       #   左侧导航 + 底部设备卡
    │   ├── AppTopbar.vue        #   搜索/时钟/设备胶囊/通知/用户
    │   ├── AppSwitch.vue        #   开关组件（受控/非受控两种模式）
    │   ├── DeviceDrawer.vue     #   设备中心抽屉（连接/断开/配对/重扫）
    │   ├── CameraModal.vue      #   摄像头弹窗（静音/截图/录制）
    │   ├── Toasts.vue           #   轻提示队列
    │   ├── HeroBanner.vue       #   首页问候 + 语音唤醒入口
    │   ├── PetInfoCard.vue      #   宠物档案卡
    │   ├── HomeAiHub.vue        #   AI 能力聚合（4 快捷 + 9 项展开面板）
    │   └── HomeCameraDock.vue   #   首页摄像头预览条
    └── views/                  # 7 个业务页面
        ├── ViewHome.vue
        ├── ViewPet.vue
        ├── ViewChat.vue
        ├── ViewDevice.vue
        ├── ViewMemory.vue
        ├── ViewPlugin.vue
        └── ViewSettings.vue
```

---

## 五、环境变量说明（`.env.development`）

| 变量 | 作用 | 示例 |
| --- | --- | --- |
| `VITE_API_BASE` | 后端 REST 前缀，开发期由 Vite 代理转发 | `/api` |
| `VITE_MQTT_URL` | MQTT Broker  WebSocket 地址；留空则跳过连接（演示模式，预留） | `ws://127.0.0.1:8083/mqtt` |
| `VITE_MQTT_USERNAME` / `VITE_MQTT_PASSWORD` | Broker 账号密码（匿名可留空，预留） | — |
| `VITE_CAM_STREAM_URL` | 摄像头 MJPEG 流地址；数据库 `camera.streamUrl` 优先，留空用占位图 | `/cam/stream` |

> 当前版本业务数据全部走后端 REST；`VITE_LLM_*` 不再需要，聊天密钥与模型调用统一由后端 `.env` 管理。

修改 `.env` 后需**重启 dev 服务**才生效。

---

## 六、分层与数据流

### 6.1 状态流向

```
ESP32/香橙派 ──MQTT──▶ Broker ──▶ FastAPI 后端 ──REST──▶ 前端 api 层 ──▶ Pinia store ──▶ 组件
        ▲                                                                    │
        └────────────── 下行控制指令（音量/开关/云台/喂食）◀── 后端 MQTT 预留层 ◀──┘
```

- **组件** 只负责渲染与发动作，不直接写请求；
- **store** 是唯一数据源，启动时 `bootstrap()` 用 `Promise.allSettled` 分别拉 `/api/state` 与 `/api/nav`，任一接口失败都不会清空页面；交互动作先调 `api/*` 再更新本地状态；
- **导航** 以 `src/config/nav.js` 为基线，后端 `/api/nav` 正常时覆盖，因此后端未启动时左侧菜单仍可显示；
- **api 层**（`src/api/`）封装 HTTP 接口与响应壳解包；浏览器端 MQTT / 摄像头流等外部服务封装后续放 `services/`。

### 6.2 已落地与预留

| 位置 | 状态 | 说明 |
| --- | --- | --- |
| `api/http.js`、`api/index.js` | 已落地 | axios 实例、统一剥壳；设备/宠物/聊天/互动/插件/打卡/设置/通知接口 |
| `stores/companion.js` | 已落地 | 快照初始化、连接/断开/扫描、聊天、快速互动、插件、打卡、设置、通知已读 |
| `config/nav.js` | 已落地 | 导航基线 + 设备兜底，避免单接口异常导致侧边栏消失 |
| 浏览器端 MQTT | 预留 | 下行指令当前由后端 MQTT 预留层处理，前端未直连 Broker |
| 摄像头流 | 预留 | 数据库 `camera.streamUrl` / `VITE_CAM_STREAM_URL` / 本地占位图三级回退 |
| 大模型 | 后端代理 | 前端只调 `/api/chat`，密钥与模型调用在后端 |

---

## 七、后端 REST 接口约定（已对接）

后端统一响应壳：`{ code: 0, message: "成功", data: ... }`，`code === 0` 为成功。
前端 `api/http.js` 拦截器已自动剥壳，组件/store 拿到的就是 `data`。

| 方法 | 路径 | 说明 | 前端封装（`api/index.js`） |
| --- | --- | --- | --- |
| GET | `/api/state` | 全量快照（设备/宠物/天气/图表/聊天/打卡/插件/记忆/设置/通知） | `fetchState()` |
| GET | `/api/nav` | 侧边导航（前端已内置基线兜底） | `fetchNav()` |
| GET | `/api/devices` | 已绑定设备列表 | `fetchDevices()` |
| GET | `/api/devices/nearby` | 附近可配对设备 | `fetchNearbyDevices()` |
| POST | `/api/devices/:id/connect` | 连接 / 配对设备 | `connectDevice(id)` |
| POST | `/api/devices/:id/disconnect` | 断开设备 | `disconnectDevice(id)` |
| POST | `/api/devices/scan` | 触发一次扫描 | `scanDevices()` |
| GET | `/api/pets/:petKey/profile` | 宠物档案（含能量/情绪标签/健康状态） | `fetchPetProfile(petKey)` |
| GET | `/api/pets/:petKey/stats?range=week` | 陪伴统计趋势 | `fetchPetStats(petKey, range)` |
| POST | `/api/pets/:petKey/interact` | 快速互动（抚摸/语音/游戏/音乐） | `sendInteraction(petKey, action)` |
| GET | `/api/chat/messages` | 历史聊天记录 | `fetchChatMessages()` |
| POST | `/api/chat` | 对话代理（大模型 / 兜底） | `sendChatMessage(payload)` |
| GET | `/api/plugins` | 插件清单 | `fetchPlugins()` |
| PUT | `/api/plugins/:id/toggle` | 切换插件开关 | `togglePlugin(id)` |
| GET | `/api/bless` | 小确幸清单 | `fetchBless()` |
| PUT | `/api/bless/:id/toggle` | 切换打卡 | `toggleBless(id)` |
| GET/PUT | `/api/settings` | 读取/更新语音·屏幕·音乐·网络·设备·通知·账户·摄像头设置 | `fetchSettings()` / `updateSettings(payload)` |
| GET | `/api/notifications` | 通知列表与未读数 | `fetchNotifications()` |
| PUT | `/api/notifications/read` | 全部标记为已读 | `markNotificationsRead()` |

鉴权：当前版本未做登录鉴权；预留 token 后可在 `http.js` 拦截器统一带 `Authorization: Bearer <token>`。

> 详细的 MQTT 主题表、ESP32 上报/下行报文格式、摄像头与大模型对接步骤，见 **[`docs/integration.md`](./docs/integration.md)**。

---

## 八、页面与原型对照

| 路由 | 页面 | 保留能力 |
| --- | --- | --- |
| `/home` | 总览首页 | 问候、宠物档案、语音唤醒、AI 能力聚合、摄像头预览、离线提示条 |
| `/pet` | 我的宠物 | 档案、成长值、情绪/健康/活跃度、健康档案、今日小确幸打卡 |
| `/chat` | 互动陪伴 | 周/月/季趋势图、抚摸/语音/游戏/音乐、多轮聊天（接大模型） |
| `/device` | 设备控制 | 设备管理、摄像头预览、麦克风/音量/TTS/表情屏/云台/移动侦测 |
| `/memory` | 成长记忆 | 时间线、里程碑统计、照片墙 |
| `/plugin` | 插件中心 | 已启用/可安装分组、8 个插件与开关 |
| `/settings` | 系统设置 | 设备切换、网络、语音、通知隐私、账户关于 |

---

## 九、常见问题

**1. 启动后页面空白 / 控制台报错找不到模块？**
确认在 `frontend/` 目录执行 `npm install` 后再 `npm run dev`；依赖未装全时先删 `node_modules` 重装。

**1.1 左侧导航菜单消失？**
已修复：导航基线在 `src/config/nav.js`，不再依赖 `/api/nav` 成功返回；若仍空白，Ctrl+F5 强制刷新并查看控制台是否有脚本错误。

**1.2 打开 5173 是 500 / 空白？**
5173 可能被其他程序占用，Vite 会自动换端口（5174/5175…）；请以终端打印的 `Local: http://localhost:xxxx/` 为准。

**2. MQTT 连不上？**
- 确认 Broker 已启动、`VITE_MQTT_URL` 端口正确（EMQX WebSocket 默认 8083，路径 `/mqtt`）；
- 浏览器 `ws://` 只能连局域网/本地，`https` 页面下必须用 `wss://`；
- 未配置 URL 时前端进入演示模式，不会阻塞页面，控制台有 `[MQTT] 未配置` 提示。

**3. 摄像头黑屏 / 截图失败？**
- 未配置数据库 `camera.streamUrl` 与 `VITE_CAM_STREAM_URL` 时显示占位图，属正常；
- 真实流跨域时，把地址走 Vite 代理（`/cam`）或后端转发；跨域未代理时截图会被浏览器拦截，弹窗有对应提示。

**4. 聊天回复是兜底话术，没走大模型？**
兜底发生在**后端**：未配置 `LLM_BASE_URL` / `LLM_API_KEY` 或模型调用失败时，后端从内置话术随机回复；在后端 `.env` 配好大模型后，`/api/chat` 即返回模型回复，前端无需改动。

**5. 改了样式不生效？**
全局样式在 `src/styles/`；组件内不要重复定义同名类。设计值统一改 `tokens.css` 变量。

---

## 十、建议的后续路线

1. ~~接后端 REST~~（已完成：`/api/state` 快照 + 各写回接口）；
2. 接 MQTT：ESP32 上报遥测，前端订阅刷新信号/电量/活跃度；
3. 接大模型：在后端 `.env` 配置模型地址与密钥，聊天即走真实模型；
4. 接摄像头：ESP32-CAM 推 MJPEG 流，替换占位图；
5. 扩展：WebRTC 低延迟视频、语音识别（浏览器 Web Speech API）、TTS 播报、固件 OTA。
