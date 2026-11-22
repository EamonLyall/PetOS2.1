# PetOS 后端接口文档（API）

- Base URL：`http://127.0.0.1:8080`（开发期前端经 Vite 代理 `/api` 转发到该地址）
- 接口文档（可在线调试）：`/docs`（Swagger UI）、`/redoc`
- 字符编码：UTF-8；请求体 `Content-Type: application/json`（图片上传除外）

## 统一响应壳

所有接口返回同一结构：

```json
{
  "code": 0,
  "message": "成功",
  "data": { }
}
```

| 字段 | 说明 |
| --- | --- |
| `code` | `0` 成功；`400` 参数校验失败；`500` 业务/系统失败。前端按 `code === 0` 判定成功 |
| `message` | 提示信息，失败时可直接展示给用户 |
| `data` | 业务数据，对象 / 数组 / `null` |

业务异常示例（设备不存在等）：

```json
{ "code": 500, "message": "宠物档案不存在：xxx", "data": null }
```

参数校验失败同样返回统一响应壳（不会出现 FastAPI 默认的 422 结构）：

```json
{ "code": 400, "message": "请求参数校验失败：text: field required", "data": null }
```

> 每个响应都会带 `X-Request-ID` 响应头；后端控制台输出 `[API] {requestId} {method} {path} -> {status} {耗时}ms`，便于答辩时展示请求链路。

---

## 一、陪伴域

### 1.1 GET `/api/state` — 全量状态快照

一次性返回前端首页与各页面所需的全部数据，前端 store 启动时拉取本接口填充状态。

> 说明：本快照中的 `timeline`、`milestones` 文案已按当前活跃宠物（优先 `settings.activeDeviceId` 对应设备的宠物，否则取第一台已绑定设备）替换 `{level} {growth} {name} {breed} {days}` 占位符，前端可直接渲染，无需二次插值。

**响应 `data` 示例（节选）：**

```json
{
  "devices": [
    {
      "id": "d-nuomi", "name": "PetOS 小橘", "petKey": "nuomi", "place": "客厅",
      "online": true, "signal": 92, "battery": 78, "fw": "v2.4.1",
      "wifi": "PetOS-Home", "last": "刚刚还在陪你"
    }
  ],
  "nearby": [
    { "id": "d-xiaobai", "name": "PetOS 小白", "petKey": "xiaobai", "place": "阳台", "signal": 88 }
  ],
  "pets": {
    "nuomi": {
      "petKey": "nuomi", "name": "糯米", "emoji": "🐱", "breed": "橘猫",
      "age": "1 岁 2 个月", "weight": "4.2 kg", "level": 3, "growth": 68,
      "mood": "愉悦", "active": 92, "interact": 12, "days": 128,
      "desc": "一只喜欢晒太阳的小猫",
      "heartRate": 132, "activeMinutes": 46, "sleepHours": 11.5,
      "lastCheckup": "2026-11-02", "moments": 46, "songs": 56, "games": 24,
      "energy": 78, "moodTag": "平静", "healthStatus": "良好"
    }
  },
  "weather": { "text": "晴", "temp": 26, "wind": "微风" },
  "charts": {
    "week":   { "labels": ["周一", "周二"], "interact": [58, 62], "online": [52, 48] },
    "month":  { "labels": ["第1周"], "interact": [61], "online": [55] },
    "quarter":{ "labels": ["8月"],   "interact": [64], "online": [58] }
  },
  "settings": {
    "connected": true,
    "activeDeviceId": "d-nuomi",
    "voice": { "wakeWord": "小宠小宠", "listening": false, "tts": true, "volume": 70 },
    "screen": { "on": true, "expression": "开心" },
    "music": { "playing": false, "track": "午后猫咪轻音乐" },
    "network": { "bluetooth": true, "wifiQuality": "信号良好", "firmwareLatest": true },
    "device": { "mic": true, "micSensitivity": 80, "gimbal": true, "motion": true, "motionSensitivity": "中" },
    "notify": { "message": true, "motion": true, "cloudSync": true },
    "profile": { "language": "简体中文", "account": "主人", "appVersion": "2.4.1" },
    "camera": { "resolution": "1080P", "fps": 24, "nightVision": true, "motionDetect": true, "twoWayAudio": true, "streamUrl": "" }
  },
  "chatMessages": [ { "who": "pet", "text": "主人你回来啦～" } ],
  "blessList": [ { "text": "和小猫玩一会小游戏", "done": true } ],
  "plugins": [ { "id": 1, "name": "天气助手", "icon": "weather", "color": "", "desc": "...", "enabled": true, "n": "天气助手", "i": "weather", "c": "", "d": "...", "on": true } ],
  "timeline":  [ { "date": "2026-11-19", "title": "升级 LV.3 🎉", "desc": "..." } ],
  "milestones":[ { "label": "累计互动", "value": "328 次", "tail": "进行中" } ],
  "gallery":   [ { "imageKey": "cat", "imageUrl": "", "caption": "午后的阳光" } ],
  "notifications": [
    { "id": 1, "icon": "heart", "tone": "", "text": "糯米已经等你 2 小时啦，快回家陪陪它吧～", "timeAgo": "2 分钟前", "read": false }
  ],
  "unreadCount": 2
}
```

### 1.2 GET `/api/devices` — 已绑定设备列表

返回 `data`：设备对象数组（字段同 1.1 的 `devices`）。

### 1.3 GET `/api/devices/nearby` — 附近可配对设备

返回 `data`：附近设备对象数组（字段同 1.1 的 `nearby`）。

### 1.4 POST `/api/devices/{id}/connect` — 连接 / 配对设备

- 已绑定设备：切换为当前设备并置为已连接；
- 附近设备：先配对入库（补默认电量 66、固件 `v2.4.0`、Wi-Fi `PetOS-Home`），再连接。

**响应 `data`：**

```json
{ "device": { "id": "d-nuomi", "petKey": "nuomi", "...": "..." }, "pet": { "petKey": "nuomi", "name": "糯米" } }
```

### 1.5 POST `/api/devices/{id}/disconnect` — 断开连接

**响应 `data`：** `{ "activeDeviceId": "d-nuomi", "connected": false }`

### 1.6 POST `/api/devices/scan` — 重新扫描附近设备

**响应 `data`：** `{ "nearby": [ ... ], "count": 2 }`

> 预留：真实场景由蓝牙/Wi-Fi 发现或 MQTT 心跳上报补充设备；当前返回库中附近设备。

### 1.7 GET `/api/devices/{id}/telemetry` — 实时遥测

**响应 `data`：**

```json
{
  "deviceId": "d-nuomi", "battery": 78, "signal": 92,
  "heartRate": 132, "active": 92, "onlineMinutes": 46,
  "mood": "愉悦", "ts": 1732070000
}
```

### 1.8 GET `/api/pets/{petKey}/profile` — 宠物档案

`petKey` 示例：`nuomi` / `tuanzi` / `mochi` / `xiaobai` / `huajuan`。
返回 `data`：单个宠物对象（字段同 1.1 的 `pets[petKey]`）。

### 1.9 GET `/api/pets/{petKey}/timeline` — 成长时间线

文案中的 `{level} {growth} {name} {breed}` 占位符已按当前宠物替换。

**响应 `data`：**

```json
[
  { "date": "2026-11-19", "title": "升级 LV.3 🎉", "desc": "陪伴值突破 68，解锁了新的互动姿势「肚皮蹭蹭」。" }
]
```

### 1.10 GET `/api/pets/{petKey}/milestones` — 里程碑统计

**响应 `data`：**

```json
[
  { "label": "累计互动", "value": "328 次", "tail": "进行中" },
  { "label": "开心时刻", "value": "128 天", "tail": "达成" }
]
```

### 1.11 GET `/api/pets/{petKey}/gallery` — 照片墙

**响应 `data`：** `[ { "imageKey": "cat", "imageUrl": "", "caption": "午后的阳光" } ]`

### 1.12 GET `/api/pets/{petKey}/stats?range=week` — 陪伴趋势

| 参数 | 取值 | 说明 |
| --- | --- | --- |
| `range` | `week` / `month` / `quarter` | 趋势区间，默认 `week` |

**响应 `data`：**

```json
{
  "range": "week",
  "labels": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
  "interact": [58, 62, 74, 64, 70, 75, 86],
  "online": [52, 48, 56, 60, 58, 62, 66]
}
```

### 1.12.1 POST `/api/pets/{petKey}/interact` — 快速互动（写库）

前端聊天页“抚摸互动 / 语音对话 / 趣味游戏 / 播放音乐”调用。

**请求体：**

```json
{ "action": "pet" }
```

| `action` | 说明 |
| --- | --- |
| `pet` | 抚摸互动：互动次数 +1，成长值 +1（上限 100） |
| `voice` | 语音对话：互动次数 +1 |
| `game` | 趣味游戏：互动次数 +1，成长值 +1（上限 100） |
| `music` | 播放音乐：互动次数 +1 |

**响应 `data`：**

```json
{
  "action": "pet",
  "pet": { "petKey": "nuomi", "interact": 13, "growth": 69, "energy": 78, "...": "..." },
  "message": "已开启抚摸互动，小猫正在呼噜呼噜～"
}
```

> 非法 `action` 返回 `code=500`；互动同时会向对应设备预留 MQTT `control/interact` 下行。

### 1.13 GET `/api/weather` — 当前天气

**响应 `data`：** `{ "text": "晴", "temp": 26, "wind": "微风" }`

### 1.14 GET `/api/settings` — 获取全局设置

**响应 `data`：** 同 1.1 的 `settings`。

### 1.15 PUT `/api/settings` — 更新全局设置

局部更新，支持字段：`connected`、`activeDeviceId`、`voice`、`screen`、`music`、
`network`、`device`、`notify`、`profile`、`camera`；
所有结构化对象均浅合并，只覆盖传入的子字段。

**请求体示例：**

```json
{
  "voice": { "volume": 80, "tts": false },
  "screen": { "expression": "撒娇" },
  "network": { "bluetooth": false },
  "device": { "mic": false },
  "notify": { "cloudSync": false }
}
```

**响应 `data`：** 更新后的完整 `settings`（同 1.1）。

> `voice` 音量/TTS、`screen`、`music`、`device` 变化时会预留 MQTT 下行；未配置 Broker 时仅打印 `[MQTT][演示模式]` 日志。

### 1.16 GET `/api/chat/messages` — 历史聊天记录

**响应 `data`：** `[ { "who": "me", "text": "..." }, { "who": "pet", "text": "..." } ]`

### 1.17 POST `/api/chat` — 发送消息并获取回复

别名：`POST /api/llm/chat`（兼容前端 `VITE_LLM_BASE_URL=/api/llm`）。

**请求体：**

```json
{ "text": "推荐个小游戏吧", "deviceId": "d-nuomi", "messages": [] }
```

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `text` | 是 | 主人发送的文本，空串报错 |
| `deviceId` | 否 | 当前设备 ID，预留按宠物人设区分回复 |
| `messages` | 否 | 历史记录；不传则取库中记录作为上下文 |

**响应 `data`：** `{ "reply": "好呀，我最喜欢陪着主人啦～ 😺" }`

> 未配置大模型时，回复来自内置兜底话术；配置 `LLM_BASE_URL` / `LLM_API_KEY` 后走 OpenAI 兼容接口。

### 1.18 GET `/api/plugins` — 插件清单

**响应 `data`：** 插件对象数组，同时含规范字段与原型短字段：

```json
{
  "id": 1, "name": "天气助手", "icon": "weather", "color": "",
  "desc": "语音查询天气，出门前提醒你带伞。", "enabled": true,
  "n": "天气助手", "i": "weather", "c": "", "d": "语音查询天气，出门前提醒你带伞。", "on": true
}
```

### 1.19 PUT `/api/plugins/{id}/toggle` — 切换插件启用状态

**响应 `data`：** 切换后的完整插件对象。

### 1.20 GET `/api/bless` — 小确幸打卡清单

**响应 `data`：** `[ { "id": 1, "text": "和小猫玩一会小游戏", "done": true } ]`

### 1.21 PUT `/api/bless/{id}/toggle` — 切换打卡完成状态

**响应 `data`：** `{ "id": 2, "text": "给小猫摸头", "done": true }`

### 1.22 GET `/api/nav` — 侧边导航配置

**响应 `data`：** `[ { "key": "home", "name": "总览首页", "icon": "home" }, ... ]`

> 前端 `src/config/nav.js` 已内置同一份基线配置，本接口返回时覆盖；即使本接口异常，侧边栏也不会消失。

### 1.23 GET `/api/notifications` — 通知列表

**响应 `data`：**

```json
{
  "notifications": [
    { "id": 1, "icon": "heart", "tone": "", "text": "糯米已经等你 2 小时啦，快回家陪陪它吧～", "timeAgo": "2 分钟前", "read": false }
  ],
  "unreadCount": 2
}
```

### 1.24 PUT `/api/notifications/read` — 全部标记为已读

**响应 `data`：** 最新通知列表，`unreadCount` 为 `0`。

---

## 二、监控域（遗留硬件链路）

### 2.1 GET `/api/monitor/devices` — 监控设备列表

**响应 `data`：**

```json
{
  "id": 1, "deviceName": "客厅 ESP32-S3", "deviceType": "ESP32_S3",
  "sn": "esp32-s3-001", "online": true, "lastHeartbeat": "...",
  "location": "客厅", "createTime": "..."
}
```

### 2.2 GET `/api/monitor/devices/type/{deviceType}`

按类型过滤：`ESP32_S3` / `ORANGE_PI`。

### 2.3 GET `/api/monitor/devices/{sn}`

按 SN 查询单台设备；不存在返回 `code=500`。

### 2.4 GET `/api/sensors/{sn}/recent` — 最近 20 条传感器数据

**响应 `data`：**

```json
{
  "id": 1, "deviceSn": "esp32-s3-001", "temperature": 23.2, "humidity": 62.0,
  "pirTriggered": false, "doorClosed": true, "reportTime": "2026-11-20 08:00:00"
}
```

### 2.5 GET `/api/sensors/{sn}` — 全部传感器历史（时间正序）

### 2.6 GET `/api/alarms` — 全部告警（时间倒序）

### 2.7 GET `/api/alarms/recent` — 最近 10 条告警

### 2.8 GET `/api/alarms/device/{sn}` — 按设备查告警

**告警对象字段：**

```json
{
  "id": 1, "deviceSn": "esp32-s3-001", "cameraSn": "orangepi-cam-001",
  "alarmType": "PERSON_DETECT", "confidence": 0.93,
  "imagePath": "", "imageUrl": "",
  "handled": false, "description": "检测到人体，已自动抓拍并联动声光报警",
  "alarmTime": "2026-11-20 08:50:00", "createTime": "2026-11-20 08:50:00"
}
```

### 2.9 POST `/api/alarms/upload` — 上传抓拍图并生成告警

`multipart/form-data`：

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `file` | 是 | 图片文件，仅允许 jpg/jpeg/png |
| `deviceSn` | 是 | 触发告警的 ESP32 SN |
| `cameraSn` | 是 | 香橙派摄像头 SN |
| `confidence` | 否 | YOLO 置信度 0~1 |

**响应 `data`：** 新生成的告警记录对象。

### 2.10 PUT `/api/alarms/{id}/handle` — 标记告警已处理

### 2.11 POST `/api/commands/light` — 补光灯开关

**请求体：** `{ "sn": "esp32-s3-001", "on": true }`

### 2.12 POST `/api/commands/buzzer` — 蜂鸣器开关

**请求体：** `{ "sn": "esp32-s3-001", "on": true }`

### 2.13 POST `/api/commands/gimbal` — 云台转动

**请求体：** `{ "sn": "esp32-s3-001", "pan": 90, "tilt": 45 }`

> 三条指令经 MQTT 主题 `monitor/esp32/{sn}/control` 下发；未配置 Broker 时仅打印日志。

### 2.14 GET `/api/dashboard/stats` — 大屏汇总统计

**响应 `data`：**

```json
{
  "deviceTotal": 2, "onlineTotal": 2, "offlineTotal": 0,
  "esp32Total": 1, "orangePiTotal": 1,
  "alarmTotal": 5, "unhandledAlarmTotal": 3,
  "latestTemperature": 25.5, "latestHumidity": 56.0
}
```

---

## 三、健康检查

### GET `/api/health`

**响应 `data`：** `{ "status": "up", "service": "petos-backend", "version": "2.1.0", "database": "ok" }`

> `status` 为 `up` 表示服务与数据库都正常；数据库连接失败时返回 `degraded` 且 `database=error`，便于部署探针区分。
