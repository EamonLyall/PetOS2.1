# PetOS 硬件 / 后端对接指南（ESP32 · MQTT · 摄像头 · 大模型）

本文档说明前端如何与后端、硬件、大模型对接。**REST 接口已对接 FastAPI 后端**；浏览器端 MQTT、真实摄像头流为预留层，按本文补齐即可。

---

## 一、总体架构

```
┌──────────┐  MQTT/TCP   ┌──────────┐  REST/WS   ┌──────────┐
│  ESP32   │ ─────────▶ │ Broker   │ ◀────────▶ │  后端    │
│ (ESP32/  │  上报遥测  │ EMQX/    │            │ (Node/  │
│  CAM)    │ ◀───────── │ Mosquitto│  转发/鉴权 │  Java…) │
└──────────┘  下行指令  └──────────┘            └────┬─────┘
                                                    │ 代理大模型
                                             ┌──────▼──────┐
                                             │ 大模型服务   │
                                             │ DeepSeek/通义│
                                             └─────────────┘
        ▲
        │ WebSocket(wss) / HTTP
┌───────┴────────┐
│ 前端 (本工程)   │  axios 连后端 REST；MQTT/摄像头流为预留，后续接入
└────────────────┘
```

职责划分：
- **ESP32**：采集传感器（心率/活跃度/电量/信号）、执行下发的控制指令（音量/屏幕/云台/喂食）、推送摄像头画面；
- **Broker**：消息总线，解耦设备与后端；
- **后端**：鉴权、设备绑定、大模型密钥保管、报文持久化、转发遥测；
- **前端**：展示与交互，不保存任何设备密钥与大模型密钥。

---

## 二、MQTT 对接

### 2.1 连接配置

> 现状：浏览器端 MQTT 尚未接入，下行指令当前由后端 MQTT 预留层处理；前端 `src/services/` 留作后续封装位置。地址与账号来自 `.env`：

```
VITE_MQTT_URL=ws://192.168.x.x:8083/mqtt   # 局域网开发
# 生产：VITE_MQTT_URL=wss://your-broker.example.com/mqtt
```

- 浏览器只能走 **WebSocket**（`ws://` / `wss://`），不能用 TCP 1883；
- EMQX 默认 WebSocket 端口 `8083`，路径 `/mqtt`；Mosquitto 需开启 `websockets` 监听；
- 前端 `clientId` 自动生成 `petos-web-xxxxxxxx`，断线 4 秒自动重连；
- 未配置 `VITE_MQTT_URL` 时进入演示模式，不连接 Broker，页面可独立运行。

### 2.2 主题规划（约定）

设备 ID 规则：`d-nuomi`、`d-tuanzi`…，与后端数据库 `companion_device.id` 一致。

| 方向 | 主题 | QoS | 用途 | 报文示例 |
| --- | --- | --- | --- | --- |
| 上行 设备→云 | `petos/{deviceId}/telemetry` | 1 | 周期遥测：电量/信号/心率/活跃度/在线时长 | 见 2.3 |
| 上行 设备→云 | `petos/{deviceId}/status` | 1 | 上线/离线状态 | `{"online":true,"ts":1732070000}` |
| 上行 设备→云 | `petos/{deviceId}/camera/motion` | 0 | 移动侦测事件 | `{"detected":true,"confidence":0.82,"ts":1732070000}` |
| 上行 设备→云 | `petos/{deviceId}/voice/up` | 1 | 设备端语音识别文本（ASR 结果） | `{"text":"我想出去玩","ts":1732070000}` |
| 下行 云→设备 | `petos/{deviceId}/control/volume` | 1 | 音量 0–100 | `{"volume":70}` |
| 下行 云→设备 | `petos/{deviceId}/control/tts` | 1 | 语音回复开关 | `{"on":true}` |
| 下行 云→设备 | `petos/{deviceId}/control/screen` | 1 | 表情屏开关/表情 | `{"on":true,"expression":"开心"}` |
| 下行 云→设备 | `petos/{deviceId}/control/servo` | 1 | 云台舵机/自动追踪 | `{"tracking":true,"pan":0,"tilt":0}` |
| 下行 云→设备 | `petos/{deviceId}/control/music` | 1 | 音乐播放/暂停/曲目 | `{"playing":false,"track":"午后猫咪轻音乐"}` |
| 下行 云→设备 | `petos/{deviceId}/control/feed` | 1 | 智能喂食 | `{"portion":20}` |
| 下行 云→设备 | `petos/{deviceId}/voice/down` | 1 | 下发 TTS 播报文本 | `{"text":"主人你回来啦～"}` |
| 广播 | `petos/+/status` | 0 | 前端订阅全部设备在线状态 | 同 status |

### 2.3 遥测报文（telemetry）建议字段

```json
{
  "deviceId": "d-nuomi",
  "battery": 78,
  "signal": 92,
  "heartRate": 132,
  "active": 92,
  "onlineMinutes": 46,
  "mood": "愉悦",
  "ts": 1732070000
}
```

后续前端直连 MQTT 时的接入示例（预留，当前未启用）：

```js
import { mqttService, topics } from '@/services/mqtt'

// 连接后订阅当前设备遥测
mqttService.subscribe(topics.telemetry(device.activeDeviceId), (data) => {
  // 把 data.battery / data.signal / data.active 写入 store，视图自动刷新
})

// 下发音量（对应前端音量滑块）
mqttService.publishControl(device.activeDeviceId, 'volume', { volume: comp.voice.volume })
```

### 2.4 ESP32 固件要点（Arduino / ESP-IDF）

1. **Wi-Fi**：先连路由器，再连 Broker；建议用 PubSubClient（Arduino）或 ESP-MQTT（IDF）；
2. **设备 ID**：烧录时固定 `deviceId`，与后端绑定表一致；
3. **订阅**：启动后订阅 `petos/{deviceId}/control/#`，收到指令解析 JSON 执行：
   - `volume` → 调功放/蜂鸣器音量；
   - `screen` → 驱动 OLED/TFT 显示表情；
   - `servo` → 驱动舵机转 pan/tilt；
   - `feed` → 驱动舵机/步进电机出粮；
   - `voice/down` → 送 TTS 模块播报；
4. **上报**：循环中按间隔（如 5–10 秒）发布 `telemetry`；状态变化时发布 `status`；
5. **断线重连**：`loop()` 里保证 `client.loop()`，掉线后重连并重新订阅；
6. **时间戳**：报文 `ts` 用 NTP 同步后的 Unix 秒，便于后端排序。

> 安全提示：生产环境 Broker 必须开启用户名密码/ACL，设备只能发布/订阅自己 `deviceId` 前缀的主题；不要在前端固件里硬编码 Broker 密码。

---

## 三、摄像头对接

### 3.1 方案 A：ESP32-CAM MJPEG 流（最简单，推荐竞赛演示）

ESP32-CAM 固件开启摄像头服务后，浏览器直接用 `<img>` 拉 MJPEG 流：

```
http://192.168.4.1/stream        # 直连热点
http://192.168.x.x/stream        # 局域网路由器
```

前端配置：在 `.env.development` 设置

```
VITE_CAM_STREAM_URL=/cam/stream
```

并在 `vite.config.js` 的 `/cam` 代理里把 target 指向 ESP32-CAM 地址（已预留），避免浏览器跨域/混合内容拦截。未配置时页面显示本地打包的占位图。

### 3.2 方案 B：后端转发 / WebRTC（低延迟，后续扩展）

- 多路摄像头、鉴权、录像留存建议由后端媒体服务转发；
- 低延迟双向场景可上 WebRTC：前端用 `RTCPeerConnection` 拉流，信令走后端；`services/camera.js` 已留扩展位。

### 3.3 画面功能

- **截图**：`cameraService.captureSnapshot(imgEl)` 把当前帧绘到 canvas 导出 PNG；跨域未代理时会被浏览器拦截，弹窗已有提示；
- **录制**：当前为占位提示；真实录制可用 `MediaRecorder` 采集 canvas/流；
- **移动侦测**：由 ESP32/后端检测后经 `camera/motion` 主题推送，前端弹通知。

---

## 四、大模型 API 对接

### 4.1 安全原则（重要）

**大模型 API Key 只放在后端，前端绝不直连第三方。** 前端只调用自己后端的 `/api/chat`，由后端携带密钥请求模型，避免密钥泄露。

### 4.2 对话流程

1. 用户在「互动陪伴」页输入消息 → store `sendChat(text)`；
2. 前端 `api/index.js` 的 `sendChatMessage({ text, deviceId, messages })` POST 到后端 `/api/chat`（历史上下文一并带上）；
3. 后端把上下文转成 OpenAI 兼容 messages 并携带密钥请求模型，返回 `{ "reply": "..." }`；
4. 前端把回复追加到聊天列表；
5. 兜底在**后端**：未配置模型或调用失败时，后端返回内置兜底话术；前端不保存兜底文案。

### 4.3 可接入模型（后端适配 OpenAI 兼容协议即可）

DeepSeek、通义千问、豆包（火山方舟）、Kimi、OpenAI 等。后端只需把请求/响应格式统一成上面的约定，前端无需改动。

### 4.4 语音链路（扩展）

- **ASR（语音转文字）**：浏览器可用 Web Speech API 录音识别，文本走聊天；或 ESP32 采集后经 `voice/up` 上报；
- **TTS（文字转语音）**：后端/模型返回文本后，经 `voice/down` 主题下发设备播报，或浏览器 `speechSynthesis` 直接朗读。

---

## 五、联调顺序建议

1. **启动后端 + 前端**：`npm run dev` 连 FastAPI（8080），确认 7 个页面数据来自数据库、开关/聊天/图表/抽屉/弹窗正常；
2. **REST 写回**：验证设备配对/断开、聊天、插件开关、打卡、音量/屏幕/音乐设置能落库并刷新；
3. **MQTT 链路**：本地起 Broker，后端订阅遥测，用 MQTTX 模拟 ESP32 发布报文，看数据入库后前端刷新；
4. **ESP32 实机**：烧录固件，上报真实遥测，验证下行指令（音量/屏幕/云台）；
5. **大模型**：在后端 `.env` 配好模型地址与密钥，`/api/chat` 返回模型回复；
6. **摄像头**：配置流地址，验证预览/截图；最后做录制与移动侦测通知。

## 六、联调检查清单

- [ ] `.env` 中后端 / MQTT / 摄像头地址已按实际环境填写并重启服务
- [ ] 前端能连上 Broker，当前设备遥测订阅成功
- [ ] 下行指令（音量/TTS/屏幕/云台）ESP32 能收到并执行
- [ ] 设备上线/离线状态能推送到前端胶囊与抽屉
- [ ] `/api/chat` 返回模型回复，密钥未出现在前端代码/请求中
- [ ] 摄像头流可在 `<img>` 正常显示，截图不跨域报错
- [ ] 断网/Broker 离线时前端进入演示/离线态，不白屏
