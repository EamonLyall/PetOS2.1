# PetOS 数据库说明

## 一、总体设计

- **默认数据库**：SQLite 内嵌库，文件位于 `backend/petos.db`，Python 标准库 `sqlite3` 驱动，免安装；
- **建表时机**：后端启动时 `app/database.py::init_db()` 自动建表；表为空时灌入种子数据，重复启动不会重复插入；
- **轻量迁移**：`_run_migrations()` 会为旧库自动补 `pet.energy / mood_tag / health_status` 字段和新增设置分组，不清空已有数据；
- **MySQL 切换**：按下方「六、切换 MySQL」的表结构自行建库后，修改 `.env` 的 `DATABASE_URL` 即可；
- **种子来源**：`app/seed.py` 是业务数据唯一来源；前端已改为从后端数据库读取，不再保留本地 mock。

> 重置演示数据：`python scripts/db_tool.py reset --yes`（或停掉后端删除 `backend/petos.db` 后重启）。

---

## 二、陪伴域表

### 2.1 `companion_device` — 陪伴设备表

对应前端 `SEED.devices` 与 `SEED.nearby`。`is_nearby` 区分已绑定 / 附近未配对。

| 字段 | 类型(SQLite) | 说明 | 前端字段 |
| --- | --- | --- | --- |
| `id` | TEXT PK | 设备编号（`d-nuomi`） | `id` |
| `name` | TEXT | 设备名称 | `name` |
| `pet_key` | TEXT | 关联宠物档案 key | `petKey` |
| `place` | TEXT | 摆放位置 | `place` |
| `online` | INT(0/1) | 在线状态 | `online` |
| `signal` | INT | 信号强度 0-100 | `signal` |
| `battery` | INT | 电量 0-100 | `battery` |
| `fw` | TEXT | 固件版本 | `fw` |
| `wifi` | TEXT | 所连 Wi-Fi | `wifi` |
| `last` | TEXT | 最近互动描述 | `last` |
| `is_nearby` | INT(0/1) | 1=附近未配对，0=已绑定 | — |
| `sort` | INT | 排序号 | — |

种子：3 台已绑定（nuomi/tuanzi/mochi）+ 2 台附近（xiaobai/huajuan）。

### 2.2 `pet` — 宠物档案表

对应前端 `SEED.pets`，健康扩展字段来自“我的宠物”页状态卡片。

| 字段 | 说明 | 前端字段 |
| --- | --- | --- |
| `pet_key` | 档案 key（PK） | `petKey` |
| `name` / `emoji` / `breed` | 名字 / 表情 / 品种 | 同名 |
| `age` / `weight` | 年龄 / 体重（展示文本） | 同名 |
| `level` / `growth` | 等级 / 成长值 0-100 | 同名 |
| `mood` / `active` / `interact` / `days` | 情绪 / 活跃度 / 今日互动 / 陪伴天数 | 同名 |
| `desc` | 一句话描述 | `desc` |
| `heart_rate` | 心率（次/分） | `heartRate` |
| `active_minutes` | 今日活动分钟数 | `activeMinutes` |
| `sleep_hours` | 睡眠时长（小时） | `sleepHours` |
| `last_checkup` | 最近体检日期 | `lastCheckup` |
| `moments` / `songs` / `games` | 瞬间数 / 听歌数 / 游戏局数 | `moments` / `songs` / `games` |
| `energy` | 能量值 0-100 | `energy` |
| `mood_tag` | 情绪标签（平静/活跃…） | `moodTag` |
| `health_status` | 健康状态（良好/偏胖…） | `healthStatus` |

种子：5 只宠物（糯米/团子/麻薯/小白/花卷）。

### 2.3 `weather` — 天气表（单行，id=1）

| 字段 | 说明 | 前端字段 |
| --- | --- | --- |
| `text` | 天气描述 | `text` |
| `temp` | 温度（摄氏度） | `temp` |
| `wind` | 风力描述 | `wind` |

### 2.4 `chart_stat` — 陪伴趋势统计表

对应前端 `CHART`，按区间逐点存储。

| 字段 | 说明 |
| --- | --- |
| `range_key` | `week` / `month` / `quarter` |
| `label` | X 轴标签 |
| `interact` | 互动次数 |
| `online` | 在线时长指数 |
| `sort` | 点序 |

### 2.5 `chat_message` — 聊天记录表

| 字段 | 说明 |
| --- | --- |
| `who` | `me`=主人，`pet`=小宠 |
| `text` | 消息文本 |
| `device_id` | 关联设备（预留） |
| `created_at` | 发送时间（ISO 字符串） |
| `sort` | 顺序 |

### 2.6 `bless_item` — 今日小确幸打卡表

| 字段 | 说明 |
| --- | --- |
| `text` | 打卡事项 |
| `done` | 是否完成 1/0 |
| `sort` | 顺序 |

### 2.7 `plugin` — 插件表

| 字段 | 说明 | 前端字段 |
| --- | --- | --- |
| `name` | 插件名 | `n` / `name` |
| `icon` | 图标标识 | `i` / `icon` |
| `color` | 颜色修饰类 | `c` / `color` |
| `desc` | 插件描述 | `d` / `desc` |
| `enabled` | 是否启用 1/0 | `on` / `enabled` |
| `sort` | 顺序 | — |

### 2.8 `app_setting` — 全局键值设置表

结构化值以 JSON 字符串存储。

| key | 内容 | 前端对应 |
| --- | --- | --- |
| `connected` | 是否已连接设备 | `store.connected` |
| `active_device_id` | 当前设备 ID | `store.activeDeviceId` |
| `voice` | `{wakeWord, listening, tts, volume}` | `store.voice` |
| `screen` | `{on, expression}` | `store.screen` |
| `music` | `{playing, track}` | `store.music` |
| `network` | `{bluetooth, wifiQuality, firmwareLatest}` | `store.network` |
| `device` | `{mic, micSensitivity, gimbal, motion, motionSensitivity}` | `store.deviceOpts` |
| `notify` | `{message, motion, cloudSync}` | `store.notify` |
| `profile` | `{language, account, appVersion}` | `store.profile` |
| `camera` | `{resolution, fps, nightVision, motionDetect, twoWayAudio, streamUrl}` | `store.camera` |

### 2.9 `memory_timeline` — 成长时间线表

| 字段 | 说明 |
| --- | --- |
| `pet_key` | 所属宠物（预留多宠物，种子为空） |
| `event_date` | 事件日期 |
| `title` / `description` | 标题 / 描述（可含 `{level}` 等占位符，接口层替换） |
| `sort` | 顺序 |

### 2.10 `memory_milestone` — 里程碑统计表

| 字段 | 说明 |
| --- | --- |
| `label` | 指标名 |
| `value` | 指标值（可含 `{days}` 占位符） |
| `tail` | 右侧状态文案 |

### 2.11 `gallery_item` — 照片墙表

| 字段 | 说明 |
| --- | --- |
| `image_key` | 前端本地图片标识 `cat` / `kitten` |
| `image_url` | 后端图片地址（预留，种子为空） |
| `caption` | 图片说明 |

### 2.12 `notification` — 通知中心表

| 字段 | 说明 | 前端字段 |
| --- | --- | --- |
| `icon` | 图标标识（heart/sensor/camera） | `icon` |
| `tone` | 颜色修饰（空/mint/amber） | `tone` |
| `text` | 通知正文 | `text` |
| `time_ago` | 相对时间文案 | `timeAgo` |
| `read` | 是否已读 1/0 | `read` |
| `sort` | 排序号 | — |

种子：3 条通知（2 条未读）。顶栏“全部已读”会更新 `read` 字段并写库。

---

## 三、监控域表（遗留硬件链路）

### 3.1 `monitor_device` — 监控设备表

| 字段 | 说明 |
| --- | --- |
| `device_name` / `device_type` | 名称 / 类型（`ESP32_S3`、`ORANGE_PI`） |
| `sn` | 设备序列号（唯一） |
| `online` | 在线状态 |
| `last_heartbeat` | 最近心跳时间 |
| `location` / `create_time` | 位置 / 入库时间 |

### 3.2 `sensor_data` — 传感器数据表

| 字段 | 说明 |
| --- | --- |
| `device_sn` | 设备 SN |
| `temperature` / `humidity` | 温度 / 湿度 |
| `pir_triggered` | PIR 是否检测到人 |
| `door_closed` | 门是否关闭 |
| `report_time` | 上报时间 |

### 3.3 `alarm_record` — 告警抓拍记录表

| 字段 | 说明 |
| --- | --- |
| `device_sn` / `camera_sn` | ESP32 SN / 香橙派摄像头 SN |
| `alarm_type` | 告警类型（`PERSON_DETECT`） |
| `confidence` | YOLO 置信度 0~1 |
| `image_path` / `image_url` | 服务器路径 / 访问 URL |
| `handled` | 是否已处理 |
| `description` / `alarm_time` / `create_time` | 描述 / 告警时间 / 入库时间 |

---

## 四、数据来源对照（前端页面 ← 数据库表）

| 前端位置 | 后端表 / 种子 |
| --- | --- |
| `store.devices` | `companion_device`（`is_nearby=0`） |
| `store.nearby` | `companion_device`（`is_nearby=1`） |
| `store.pets` | `pet`（含 energy / mood_tag / health_status） |
| `store.weather` | `weather` |
| `store.charts` | `chart_stat` |
| `store.chatMessages` 初始 3 条 | `chat_message` |
| `store.blessList` | `bless_item` |
| `store.plugins` 8 个插件 | `plugin` |
| `store.voice / screen / music` | `app_setting` |
| `store.network / deviceOpts / notify / profile / camera` | `app_setting` 新增分组 |
| `store.notifications` | `notification` |
| `store.timeline` 4 条 | `memory_timeline` |
| `store.milestones` 4 项 | `memory_milestone` |
| `store.gallery` 4 张 | `gallery_item` |
| 旧监控大屏数据 | `monitor_device` / `sensor_data` / `alarm_record` |

> 前端唯一的静态数据是 `src/config/nav.js` 的导航骨架和本地图片资源；所有业务数据均来自以上数据表。

---

## 五、数据库快照与队友共享

项目提供 `backend/scripts/db_tool.py`，用于把当前 SQLite 数据导出成 SQL 快照，队友导入后得到完全一致的数据。

```powershell
# 在 backend 目录下执行
python scripts/db_tool.py export              # 导出 -> backend/sql/petos_companion_sqlite.sql
python scripts/db_tool.py import --force      # 导入（覆盖本地 petos.db）
python scripts/db_tool.py reset --yes         # 重置为初始种子数据
python scripts/db_tool.py stats               # 查看各表行数
```

- 导出内容包含建表语句与全部业务数据（设备/宠物/聊天/插件/设置/通知/监控）；
- 快照文件建议随代码提交，答辩前统一执行一次 `export`，队友 `import` 即可；
- 导入后会再执行一次 `init_db()`，兼容旧快照缺字段的情况。

---

## 六、切换 MySQL

1. 按第 2～4 节的表结构在 MySQL 中建库建表；
2. 修改 `backend/.env`：

   ```ini
   DATABASE_URL=mysql+pymysql://root:你的密码@127.0.0.1:3306/petos_companion?charset=utf8mb4
   ```

3. 安装驱动（预留）：`python -m pip install PyMySQL`。

> 当前 FastAPI 版本的数据访问层基于 SQLite 标准库；切换 MySQL 时，`app/database.py` 的连接构造部分需按所用驱动补充实现，表结构与 SQL 脚本无需改动。
