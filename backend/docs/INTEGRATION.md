# 外部服务对接指南（MQTT · 大模型 · 摄像头 · ESP32）

本文说明后端预留的外部服务接入点。当前版本在 **未配置任何外部服务** 的情况下即可完整联调前端；按本文补齐配置后，对应链路自动从“演示兜底”切换为真实通信。

---

## 一、总体架构

```
┌──────────┐  MQTT/TCP   ┌──────────┐  REST/WS   ┌──────────┐
│ ESP32/   │ ─────────▶ │ Broker   │ ◀────────▶ │ FastAPI  │
│ ESP32-CAM│ ◀───────── │ EMQX/    │            │ 后端     │
│ 香橙派   │  下行指令   │ Mosquitto│            └────┬─────┘
└──────────┘             └──────────┘                 │ 代理大模型
                                                ┌──────▼──────┐
                                                │ 大模型服务   │
                                                │ DeepSeek/通义│
        ▲                                        └─────────────┘
        │ HTTP / MQTT
┌───────┴────────┐
│ Vue3 前端      │  axios 连后端；mqtt.js 连 Broker；<img> 拉摄像头流
└────────────────┘
```

职责划分：

- **ESP32**：采集传感器（心率/活跃度/电量/信号）、执行下发指令（音量/屏幕/云台/喂食）、推送摄像头画面；
- **Broker**：消息总线，解耦设备与后端；
- **后端**：鉴权预留、设备绑定、大模型密钥保管、报文持久化、转发遥测；
- **前端**：展示与交互，不保存设备密钥与大模型密钥。

---

## 二、MQTT 对接（预留）

### 2.1 配置

在 `backend/.env` 填写：

```ini
MQTT_HOST=127.0.0.1      # Broker 地址，留空则不连接
MQTT_PORT=1883           # TCP 端口（浏览器 WebSocket 用 8083，那是前端侧）
MQTT_USERNAME=petos
MQTT_PASSWORD=petos123
MQTT_CLIENT_ID=petos-backend-server
```

安装依赖：

```powershell
python -m pip install paho-mqtt
```

未安装 `paho-mqtt` 或未填 `MQTT_HOST` 时，后端启动日志会提示进入演示模式，下行指令只打印日志，不影响接口联调。

### 2.2 主题规划（三端统一）

**陪伴域**（设备 ID 规则 `d-nuomi`，与前端种子一致）：

| 方向 | 主题 | QoS | 用途 |
| --- | --- | --- | --- |
| 上行 设备→云 | `petos/{deviceId}/telemetry` | 1 | 周期遥测：电量/信号/心率/活跃度/在线时长 |
| 上行 设备→云 | `petos/{deviceId}/status` | 1 | 上线/离线状态 |
| 上行 设备→云 | `petos/{deviceId}/camera/motion` | 0 | 移动侦测事件 |
| 上行 设备→云 | `petos/{deviceId}/voice/up` | 1 | 设备端 ASR 识别文本 |
| 下行 云→设备 | `petos/{deviceId}/control/volume` | 1 | 音量 0–100 |
| 下行 云→设备 | `petos/{deviceId}/control/tts` | 1 | 语音回复开关 |
| 下行 云→设备 | `petos/{deviceId}/control/screen` | 1 | 表情屏开关/表情 |
| 下行 云→设备 | `petos/{deviceId}/control/servo` | 1 | 云台舵机/自动追踪 |
| 下行 云→设备 | `petos/{deviceId}/control/music` | 1 | 音乐播放/暂停/曲目 |
| 下行 云→设备 | `petos/{deviceId}/control/device` | 1 | 麦克风/云台/移动侦测等设备开关 |
| 下行 云→设备 | `petos/{deviceId}/control/interact` | 1 | 快速互动动作（抚摸/语音/游戏/音乐） |
| 下行 云→设备 | `petos/{deviceId}/control/feed` | 1 | 智能喂食 |
| 下行 云→设备 | `petos/{deviceId}/voice/down` | 1 | 下发 TTS 播报文本 |

**监控域**（遗留硬件链路，SN 规则 `esp32-s3-001` / `orangepi-cam-001`）：

| 方向 | 主题 | 用途 |
| --- | --- | --- |
| 上行 | `monitor/esp32/{sn}/sensor` | 温湿度、PIR、门磁 |
| 上行 | `monitor/esp32/{sn}/status` | 心跳/在线状态 |
| 上行 | `monitor/esp32/{sn}/alarm` | PIR 原始告警 |
| 上行 | `monitor/orangepi/{sn}/detect` | YOLO 识别结果 |
| 下行 | `monitor/esp32/{sn}/control` | 蜂鸣器/补光灯/云台指令 |
| 下行 | `monitor/orangepi/{sn}/control` | 摄像头控制指令 |

### 2.3 遥测报文示例

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

### 2.4 后端下发入口

- 陪伴域：`services/mqtt.py::MqttService.publish(device_id, action, payload)`，主题 `petos/{deviceId}/control/{action}`；
- 监控域：`MqttService.publish_raw(topic, payload)`，用于 `monitor/...` 旧主题；
- 接口层在设备连接、设置更新、指令控制时自动调用对应下发方法。

### 2.5 ESP32 固件要点

1. Wi-Fi 先连路由器，再连 Broker；Arduino 用 PubSubClient，IDF 用 ESP-MQTT；
2. 设备 ID/SN 烧录时固定，与后端绑定表一致；
3. 订阅 `petos/{deviceId}/control/#`（监控域订阅 `monitor/esp32/{sn}/control`），解析 JSON 执行音量/屏幕/舵机/喂食；
4. 每 5–10 秒上报一次 `telemetry`，状态变化时上报 `status`；
5. `loop()` 保证 `client.loop()`，掉线重连并重新订阅；
6. 报文 `ts` 用 NTP 同步后的 Unix 秒。

> 生产安全：Broker 必须开启用户名密码/ACL，设备只能收发自己前缀的主题；固件里不硬编码 Broker 密码。

---

## 三、大模型对话代理（预留）

### 3.1 安全原则

**大模型 API Key 只放在后端，前端绝不直连第三方。** 前端只调用自己后端的 `/api/chat`，由后端携带密钥请求模型。

### 3.2 配置

```ini
LLM_BASE_URL=https://api.deepseek.com/v1   # OpenAI 兼容地址，留空走兜底
LLM_API_KEY=你的密钥                        # 留空走兜底
LLM_MODEL=petos-assistant
```

### 3.3 对话流程

1. 前端在“互动陪伴”页发送消息 → `POST /api/chat`（别名 `/api/llm/chat`）；
2. 后端把最近上下文转成 OpenAI 兼容 messages：

   ```json
   [
     { "role": "system", "content": "你是 PetOS 智能宠物陪伴助手…" },
     { "role": "user", "content": "今天天气怎么样？" },
     { "role": "assistant", "content": "今天是晴天，26°C…" },
     { "role": "user", "content": "推荐个小游戏吧" }
   ]
   ```

3. 后端请求 `{LLM_BASE_URL}/chat/completions`，取 `choices[0].message.content`；
4. 主人消息与模型回复均落库 `chat_message`，返回 `{ "reply": "..." }`；
5. 未配置或调用失败时，自动回退内置兜底话术（与前端原 `CHAT_REPLIES` 一致），演示不中断。

### 3.4 可接入模型

DeepSeek、通义千问、豆包（火山方舟）、Kimi、OpenAI 等，只要兼容 OpenAI `/chat/completions` 协议即可，后端无需改协议层。

### 3.5 语音链路（扩展）

- **ASR**：浏览器 Web Speech API 录音识别后走聊天接口；或 ESP32 采集后经 `voice/up` 上报；
- **TTS**：模型返回文本后经 `voice/down` 下发设备播报，或浏览器 `speechSynthesis` 朗读。

---

## 四、摄像头对接（预留）

### 4.1 方案 A：ESP32-CAM MJPEG 流（竞赛演示推荐）

固件开启摄像头服务后，浏览器直接用 `<img>` 拉 MJPEG 流：

```
http://192.168.4.1/stream        # 直连热点
http://192.168.x.x/stream        # 局域网路由器
```

前端 `.env.development` 配置：

```
VITE_CAM_STREAM_URL=/cam/stream
```

摄像头流地址优先级：数据库 `app_setting.camera.streamUrl` > `VITE_CAM_STREAM_URL` > 本地占位画面。
`vite.config.js` 的 `/cam` 代理 target 指向 ESP32-CAM 地址，避免跨域/混合内容拦截；未配置时前端显示占位图。

### 4.2 方案 B：后端转发 / WebRTC（后续扩展）

多路摄像头、鉴权、录像留存建议由后端媒体服务转发；低延迟双向场景可上 WebRTC，信令走后端。

### 4.3 画面功能

- **截图**：前端 canvas 导出 PNG；跨域未代理时会被浏览器拦截；
- **录制**：当前占位提示，真实录制可用 `MediaRecorder`；
- **移动侦测**：ESP32/后端检测后经 `camera/motion` 主题推送，前端弹通知；
- **抓拍上传**：香橙派识别到人体后 `POST /api/alarms/upload`（multipart，仅 jpg/png），图片存 `upload-images/`，经 `/images/xxx.jpg` 访问。

---

## 五、联调顺序建议

1. **后端自检**：启动后端，运行 `python scripts/verify_api.py`，确认全部接口通过；
2. **前后端联调**：`npm run dev` 启动前端，store 启动时调用 `/api/state` 拉取设备/宠物/天气/图表/设置/通知等全量数据；确认 7 个页面、开关、聊天、图表、抽屉、弹窗均来自数据库；
3. **写回验证**：设备配对/断开、聊天、快速互动、插件开关、打卡、设置变更、通知已读落库后刷新一致；
4. **数据交付**：`python scripts/db_tool.py export` 生成 SQL 快照，队友 `import --force` 后数据完全一致；
5. **MQTT 链路**：本地起 Broker，用 MQTTX 模拟 ESP32 发布 `telemetry`/`status`，验证后端落库与下行指令；
6. **ESP32 实机**：烧录固件，上报真实遥测，验证音量/屏幕/云台下行；
7. **大模型**：填好 `LLM_BASE_URL` / `LLM_API_KEY`，聊天返回模型回复；
8. **摄像头**：配置数据库 `camera.streamUrl` 或 `VITE_CAM_STREAM_URL`，验证预览/截图；最后做录制与移动侦测通知。

---

## 六、联调检查清单

- [ ] 后端 8080 已启动，`/api/health` 返回 `status: up` 且 `database: ok`
- [ ] `/api/state` 返回的设备/宠物/天气/图表/设置/通知与 `app/seed.py` 一致
- [ ] 7 个侧边导航页均可打开，左侧菜单不依赖 `/api/nav` 也能显示
- [ ] 前端 `/api`、`/images` 代理指向 `127.0.0.1:8080`
- [ ] 设置页开关、通知已读、快速互动刷新后状态保持（已落库）
- [ ] `python scripts/db_tool.py stats` 各表行数正常，`export` 可生成快照
- [ ] （可选）前端能连上 Broker，当前设备遥测订阅成功
- [ ] （可选）下行指令（音量/TTS/屏幕/云台/设备开关/互动）设备能收到并执行
- [ ] （可选）`/api/chat` 返回模型回复，密钥未出现在前端代码/请求中
- [ ] （可选）摄像头流可在 `<img>` 正常显示，截图不跨域报错
- [ ] Broker / 模型离线时后端进入演示兜底模式，不白屏、不报错
