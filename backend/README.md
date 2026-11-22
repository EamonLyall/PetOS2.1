# PetOS AI Companion 后端（FastAPI + SQLite）

对照 `frontend/` Vue3 工程实现的一体化后端：**宠物陪伴域**（设备 / 宠物档案 / 聊天 / 插件 / 成长记忆 / 设置 / 天气）+ **硬件监控域**（ESP32 传感器 / 香橙派告警抓拍 / 下行指令 / 大屏统计）。

- 前端通过 `src/api/`（axios 封装）调用本后端接口，Pinia store 启动时拉取 `/api/state` 全量快照，交互写回对应接口；后端字段与前端 store、模板读取的字段严格对齐；
- 默认使用 Python 自带 **SQLite** 内嵌库，免安装数据库，首次启动自动建表并灌入演示数据；
- **MQTT、大模型、摄像头**等外部对接项在配置中留空，后端自动进入演示兜底模式，不影响本地联调；接入真实服务时只需改 `.env`。

> 后端入口为 `app/main.py`，运行依赖见 `requirements.txt`。

---

## 一、技术栈

| 选型 | 版本/说明 | 理由 |
| --- | --- | --- |
| FastAPI | 0.165 | 现代异步 Web 框架，自带 Swagger 接口文档，类型校验直观，竞赛二次上手快 |
| Uvicorn | 0.54 | ASGI 服务器，把 FastAPI 跑在 8080 端口 |
| SQLite | Python 自带 `sqlite3` | 免安装、单文件、换电脑即跑；表结构与 MySQL 脚本一致，可平滑切换 |
| python-multipart | 0.0.34 | 解析告警抓拍图片的 `multipart/form-data` 上传 |
| paho-mqtt | 预留（默认不装） | 接入真实 EMQX 时再安装，未安装不影响启动 |

---

## 二、环境要求

- Python **3.10+**（本机已验证 3.13）；
- 端口 **8080** 未被占用（与前端 `vite.config.js` 中 `/api`、`/images` 代理目标一致）；
- 可选：EMQX Broker、大模型 API Key、ESP32/香橙派硬件——不配置也能完整演示。

检查 Python：

```powershell
python --version
```

---

## 三、快速启动

在 `backend/` 目录下执行：

```powershell
cd backend

# 1. 安装依赖（首次）
python -m pip install -r requirements.txt

# 2. 启动后端
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

启动成功后：

- 接口文档（Swagger UI）：<http://localhost:8080/docs>
- 健康检查：<http://localhost:8080/api/health>
- 抓拍图片访问：`http://localhost:8080/images/xxx.jpg`

### 联调自检

后端启动后，在 `backend/` 目录运行自检脚本，逐个校验接口返回结构与种子数据：

```powershell
python scripts/verify_api.py
```

全部通过时输出 `结果：全部通过 ✅`。

### 启动前端

在 `frontend/` 目录下另开一个终端执行：

```powershell
cd frontend
npm install      # 首次
npm run dev
```

前端地址：<http://localhost:5173>，Vite 已把 `/api`、`/images` 代理到 `127.0.0.1:8080`。

---

## 四、目录结构

```
backend/
├─ app/                          # FastAPI 应用源码
│  ├─ main.py                    # 应用入口：lifespan、请求日志、CORS、静态目录、路由注册
│  ├─ config.py                  # .env / 环境变量读取，全局配置单例
│  ├─ database.py                # SQLite 连接、建表 DDL、种子初始化、轻量迁移、设置读写
│  ├─ seed.py                    # 业务数据唯一来源（设备/宠物/通知/设置等）
│  ├─ common/
│  │  └─ response.py             # 统一响应壳 {code, message, data} + 全局/校验异常
│  ├─ services/
│  │  ├─ llm.py                  # 大模型代理（OpenAI 兼容；未配置走兜底话术）
│  │  └─ mqtt.py                 # MQTT 预留客户端（未配置则空操作 + 日志）
│  └─ routers/
│     ├─ companion.py            # 陪伴域：设备/宠物/聊天/互动/插件/记忆/设置/通知
│     └─ monitor.py              # 监控域：传感器/告警/指令/大屏统计
├─ scripts/
│  ├─ verify_api.py              # 接口联调自检脚本
│  └─ db_tool.py                 # 数据库导出 / 导入 / 重置 / 统计
├─ docs/                         # API.md / DATABASE.md / INTEGRATION.md
├─ .env.example                  # 环境变量模板
├─ .env                          # 本地实际配置（外部服务留空，演示兜底）
├─ requirements.txt              # Python 依赖清单
└─ README.md                     # 本文件
```

---

## 五、环境变量（`.env`）

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `APP_PORT` | `8080` | 后端 HTTP 端口，须与前端代理一致 |
| `CORS_ORIGINS` | `http://localhost:5173,...` | 允许跨域的前端来源，逗号分隔 |
| `DATABASE_URL` | `sqlite:///./petos.db` | 数据库连接；MySQL 连接串预留 |
| `MQTT_HOST` | （空） | MQTT Broker 地址；留空不连接，指令仅打印日志 |
| `MQTT_PORT` | `1883` | Broker TCP 端口 |
| `MQTT_USERNAME` / `MQTT_PASSWORD` | （空） | Broker 账号密码，匿名可留空 |
| `LLM_BASE_URL` | （空） | 大模型 OpenAI 兼容地址；留空走兜底话术 |
| `LLM_API_KEY` | （空） | 大模型密钥，**只放后端**，不下发前端 |
| `LLM_MODEL` | `petos-assistant` | 模型标识 |
| `UPLOAD_DIR` | `./upload-images` | 抓拍图片保存目录 |

---

## 六、接口总览

统一响应壳：

```json
{ "code": 0, "message": "成功", "data": {} }
```

`code=0` 成功，非 0 失败；`data` 为业务数据。完整字段与示例见 [docs/API.md](./docs/API.md)。

**陪伴域**

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/state` | 全量快照（设备/宠物/天气/图表/聊天/打卡/插件/记忆/设置/通知） |
| GET | `/api/devices` | 已绑定设备列表 |
| GET | `/api/devices/nearby` | 附近可配对设备 |
| POST | `/api/devices/{id}/connect` | 连接 / 配对设备 |
| POST | `/api/devices/{id}/disconnect` | 断开连接 |
| POST | `/api/devices/scan` | 重新扫描附近设备 |
| GET | `/api/devices/{id}/telemetry` | 设备实时遥测 |
| GET | `/api/pets/{petKey}/profile` | 宠物档案 |
| GET | `/api/pets/{petKey}/timeline` | 成长时间线 |
| GET | `/api/pets/{petKey}/milestones` | 里程碑统计 |
| GET | `/api/pets/{petKey}/gallery` | 照片墙 |
| GET | `/api/pets/{petKey}/stats?range=week` | 陪伴趋势（week/month/quarter） |
| POST | `/api/pets/{petKey}/interact` | 快速互动（写库：互动次数/成长值） |
| GET | `/api/weather` | 当前天气 |
| GET | `/api/settings` | 全局设置（语音/屏幕/音乐/网络/设备/通知/账户/摄像头） |
| PUT | `/api/settings` | 更新全局设置（分组浅合并） |
| GET | `/api/chat/messages` | 历史聊天记录 |
| POST | `/api/chat`（别名 `/api/llm/chat`） | 发送消息并获取回复 |
| GET | `/api/plugins` | 插件清单 |
| PUT | `/api/plugins/{id}/toggle` | 切换插件启用状态 |
| GET | `/api/bless` | 小确幸打卡清单 |
| PUT | `/api/bless/{id}/toggle` | 切换打卡完成状态 |
| GET | `/api/nav` | 侧边导航配置 |
| GET | `/api/notifications` | 通知列表与未读数 |
| PUT | `/api/notifications/read` | 全部标记为已读 |

**监控域（遗留硬件链路）**

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/monitor/devices` | 监控设备列表 |
| GET | `/api/monitor/devices/type/{type}` | 按类型查设备 |
| GET | `/api/monitor/devices/{sn}` | 按 SN 查设备 |
| GET | `/api/sensors/{sn}/recent` | 最近 20 条传感器数据 |
| GET | `/api/sensors/{sn}` | 全部传感器历史 |
| GET | `/api/alarms` | 全部告警（倒序） |
| GET | `/api/alarms/recent` | 最近 10 条告警 |
| GET | `/api/alarms/device/{sn}` | 按设备查告警 |
| POST | `/api/alarms/upload` | 上传抓拍图并生成告警 |
| PUT | `/api/alarms/{id}/handle` | 标记告警已处理 |
| POST | `/api/commands/light` | 补光灯开关 |
| POST | `/api/commands/buzzer` | 蜂鸣器开关 |
| POST | `/api/commands/gimbal` | 云台转动 |
| GET | `/api/dashboard/stats` | 大屏汇总统计 |

---

## 七、数据库

- 默认 SQLite 文件：`backend/petos.db`，首次启动自动建表灌数；旧库会自动补齐新增字段，不丢数据。
- 表结构、字段说明、数据来源对照见 [docs/DATABASE.md](./docs/DATABASE.md)。
- 数据库工具（答辩前同步队友数据）：

```powershell
python scripts/db_tool.py export          # 导出 SQL 快照 -> sql/petos_companion_sqlite.sql
python scripts/db_tool.py import --force  # 队友导入快照
python scripts/db_tool.py reset --yes     # 重置为初始种子数据
python scripts/db_tool.py stats           # 查看各表行数
```

- 切换 MySQL：按 `docs/DATABASE.md` 的表结构建库后，修改 `.env` 的 `DATABASE_URL`。

---

## 八、外部服务预留

| 服务 | 当前状态 | 接入方式 |
| --- | --- | --- |
| MQTT Broker | 未连接（演示模式） | `.env` 填 `MQTT_HOST`，`pip install paho-mqtt`，见 [docs/INTEGRATION.md](./docs/INTEGRATION.md) |
| 大模型 | 兜底话术 | `.env` 填 `LLM_BASE_URL` / `LLM_API_KEY`，OpenAI 兼容协议 |
| 摄像头流 | 占位图 | 数据库 `camera.streamUrl` 或前端 `VITE_CAM_STREAM_URL` 指向 ESP32-CAM，经 Vite `/cam` 代理 |

---

## 九、常见问题

| 现象 | 排查 |
| --- | --- |
| 后端起不来 / 8080 占用 | 确认端口未被占用；`python -m uvicorn app.main:app` 看报错 |
| 前端拿不到数据 | 确认后端 8080 已启动；浏览器 Network 看 `/api` 请求状态码；Vite 代理目标是否为 127.0.0.1:8080 |
| 中文回复是兜底话术 | `LLM_BASE_URL` / `LLM_API_KEY` 未配置，属正常兜底；接入模型后自动切换 |
| 指令下发无反应 | `MQTT_HOST` 未配置，演示模式只打印日志；接 Broker 后才会真实下发 |
| 图片不显示 | 确认 `upload-images` 目录存在，访问 `/images/文件名` 直链验证 |
| 想重置演示数据 | `python scripts/db_tool.py reset --yes`；或停掉后端删除 `backend/petos.db` 后重启 |
| 队友数据不一致 | 你执行 `python scripts/db_tool.py export`，队友执行 `python scripts/db_tool.py import --force` |
