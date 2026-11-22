# ============================================================
# 种子数据模块：后端首次启动（数据库为空）时写入 SQLite，
# 作为系统初始业务数据，之后所有读写都以数据库为准。
#
# 注意：这里的字段名同时也是接口返回给前端的 JSON 字段名，
#       与前端 store / 模板里读取的字段严格对齐（如 petKey、growth 等）。
# ============================================================

# ---------- 1. 已绑定设备 ----------
# is_nearby=0 表示已配对入库；附近未配对设备见 NEARBY_DEVICES
DEVICES = [
    {
        "id": "d-nuomi", "name": "PetOS 小橘", "pet_key": "nuomi", "place": "客厅",
        "online": True, "signal": 92, "battery": 78, "fw": "v2.4.1",
        "wifi": "PetOS-Home", "last": "刚刚还在陪你", "is_nearby": 0, "sort": 1,
    },
    {
        "id": "d-tuanzi", "name": "PetOS 团子", "pet_key": "tuanzi", "place": "卧室",
        "online": True, "signal": 76, "battery": 54, "fw": "v2.3.8",
        "wifi": "PetOS-Home", "last": "3 分钟前互动", "is_nearby": 0, "sort": 2,
    },
    {
        "id": "d-mochi", "name": "PetOS 麻薯", "pet_key": "mochi", "place": "书房",
        "online": False, "signal": 0, "battery": 12, "fw": "v2.2.1",
        "wifi": "—", "last": "2 天前离线", "is_nearby": 0, "sort": 3,
    },
]

# ---------- 2. 附近可配对设备 ----------
NEARBY_DEVICES = [
    {"id": "d-xiaobai", "name": "PetOS 小白", "pet_key": "xiaobai", "place": "阳台",
     "signal": 88, "is_nearby": 1, "sort": 1},
    {"id": "d-huajuan", "name": "PetOS 花卷", "pet_key": "huajuan", "place": "餐厅",
     "signal": 64, "is_nearby": 1, "sort": 2},
]

# ---------- 3. 宠物档案 ----------
# 后四个字段（heart_rate 等）来自“我的宠物”页面健康档案的演示值，一并落库。
PETS = [
    {
        "pet_key": "nuomi", "name": "糯米", "emoji": "🐱", "breed": "橘猫",
        "age": "1 岁 2 个月", "weight": "4.2 kg", "level": 3, "growth": 68,
        "mood": "愉悦", "active": 92, "interact": 12, "days": 128,
        "desc": "一只喜欢晒太阳的小猫",
        "heart_rate": 132, "active_minutes": 46, "sleep_hours": 11.5,
        "last_checkup": "2026-11-02", "moments": 46, "songs": 56, "games": 24,
        # 状态卡片扩展字段（全部入库，前端不再写死）
        "energy": 78, "mood_tag": "平静", "health_status": "良好",
    },
    {
        "pet_key": "tuanzi", "name": "团子", "emoji": "🐰", "breed": "布偶猫",
        "age": "8 个月", "weight": "3.6 kg", "level": 2, "growth": 41,
        "mood": "安静", "active": 76, "interact": 8, "days": 63,
        "desc": "一只爱睡觉的软乎乎小猫",
        "heart_rate": 128, "active_minutes": 32, "sleep_hours": 12.0,
        "last_checkup": "2026-10-28", "moments": 21, "songs": 18, "games": 9,
        "energy": 72, "mood_tag": "慵懒", "health_status": "良好",
    },
    {
        "pet_key": "mochi", "name": "麻薯", "emoji": "🐻", "breed": "英短",
        "age": "2 岁 1 个月", "weight": "5.1 kg", "level": 4, "growth": 85,
        "mood": "慵懒", "active": 61, "interact": 21, "days": 210,
        "desc": "一只慢吞吞的胖乎乎小猫",
        "heart_rate": 125, "active_minutes": 28, "sleep_hours": 11.0,
        "last_checkup": "2026-10-15", "moments": 88, "songs": 40, "games": 17,
        "energy": 55, "mood_tag": "困倦", "health_status": "偏胖",
    },
    {
        "pet_key": "xiaobai", "name": "小白", "emoji": "🐶", "breed": "柯基",
        "age": "1 岁", "weight": "6.0 kg", "level": 1, "growth": 22,
        "mood": "兴奋", "active": 95, "interact": 3, "days": 12,
        "desc": "刚来到家的新伙伴",
        "heart_rate": 140, "active_minutes": 55, "sleep_hours": 10.0,
        "last_checkup": "2026-11-18", "moments": 3, "songs": 2, "games": 1,
        "energy": 88, "mood_tag": "活跃", "health_status": "良好",
    },
    {
        "pet_key": "huajuan", "name": "花卷", "emoji": "🐹", "breed": "仓鼠",
        "age": "4 个月", "weight": "0.1 kg", "level": 1, "growth": 15,
        "mood": "活泼", "active": 88, "interact": 2, "days": 7,
        "desc": "一团小小的毛球",
        "heart_rate": 150, "active_minutes": 20, "sleep_hours": 13.0,
        "last_checkup": "2026-11-19", "moments": 2, "songs": 0, "games": 0,
        "energy": 64, "mood_tag": "好奇", "health_status": "良好",
    },
]

# ---------- 4. 天气 ----------
WEATHER = {"text": "晴", "temp": 26, "wind": "微风"}

# ---------- 5. 陪伴趋势图 ----------
# 每条记录：区间(week/month/quarter)、标签、互动次数、在线时长、排序
CHART = {
    "week": {
        "labels": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
        "interact": [58, 62, 74, 64, 70, 75, 86],
        "online": [52, 48, 56, 60, 58, 62, 66],
    },
    "month": {
        "labels": ["第1周", "第2周", "第3周", "第4周", "第5周"],
        "interact": [61, 68, 66, 74, 82],
        "online": [55, 58, 60, 63, 70],
    },
    "quarter": {
        "labels": ["8月", "9月", "10月"],
        "interact": [64, 73, 81],
        "online": [58, 65, 70],
    },
}

# ---------- 6. 聊天初始记录 ----------
CHAT_MESSAGES = [
    {"who": "pet", "text": "主人你回来啦～今天想和我玩什么呀？😺"},
    {"who": "me", "text": "今天天气怎么样？"},
    {"who": "pet", "text": "今天是晴天，26°C，微风～很适合带我去晒太阳哦 ☀️"},
]

# ---------- 7. 今日小确幸 ----------
BLESS_LIST = [
    {"text": "和小猫玩一会小游戏", "done": True},
    {"text": "给小猫摸头", "done": False},
    {"text": "一起看窗外的云", "done": False},
]

# ---------- 8. 插件清单 ----------
# n=名称 i=图标 c=颜色类 d=描述 on=是否启用
PLUGINS = [
    {"name": "天气助手", "icon": "weather", "color": "", "desc": "语音查询天气，出门前提醒你带伞。", "enabled": 1, "sort": 1},
    {"name": "音乐电台", "icon": "music", "color": "--pink", "desc": "海量曲库与白噪音，陪它安静入眠。", "enabled": 1, "sort": 2},
    {"name": "睡前故事", "icon": "memory", "color": "--violet", "desc": "温柔的晚安故事，哄你和小猫一起入睡。", "enabled": 1, "sort": 3},
    {"name": "摄像头监控", "icon": "camera", "color": "--mint", "desc": "✦ 亮点功能，1080P 实时画面与移动侦测。", "enabled": 1, "sort": 4},
    {"name": "健康提醒", "icon": "health", "color": "--amber", "desc": "喂食、驱虫与体检提醒，一个都不落下。", "enabled": 0, "sort": 5},
    {"name": "智能喂食", "icon": "bolt", "color": "", "desc": "定时定量投喂，记录每一餐的进食情况。", "enabled": 0, "sort": 6},
    {"name": "宠物翻译官", "icon": "chat", "color": "--violet", "desc": "试试听懂它的呼噜声与喵喵叫是什么意思。", "enabled": 0, "sort": 7},
    {"name": "打卡日历", "icon": "clock", "color": "--mint", "desc": "记录陪伴的每一天，集齐专属纪念徽章。", "enabled": 0, "sort": 8},
]

# ---------- 9. 全局界面/设备设置 ----------
# 以 key-value 形式存入 app_setting 表，结构化值用 JSON 序列化。
# 说明：设置页与设备页里的开关、文案状态全部由这里驱动，前端不再写死任何演示值。
SETTINGS = {
    "connected": True,
    "active_device_id": "d-nuomi",
    "voice": {"wakeWord": "小宠小宠", "listening": False, "tts": True, "volume": 70},
    "screen": {"on": True, "expression": "开心"},
    "music": {"playing": False, "track": "午后猫咪轻音乐"},
    # 连接与网络
    "network": {"bluetooth": True, "wifiQuality": "信号良好", "firmwareLatest": True},
    # 设备能力开关（麦克风 / 云台 / 移动侦测）
    "device": {"mic": True, "micSensitivity": 80, "gimbal": True,
               "motion": True, "motionSensitivity": "中"},
    # 通知与隐私
    "notify": {"message": True, "motion": True, "cloudSync": True},
    # 账户与版本信息
    "profile": {"language": "简体中文", "account": "主人", "appVersion": "2.4.1"},
    # 摄像头能力参数（设备页 / 首页预览条读取）
    "camera": {"resolution": "1080P", "fps": 24, "nightVision": True,
               "motionDetect": True, "twoWayAudio": True, "streamUrl": ""},
}

# ---------- 9.1 通知中心（对应顶栏通知气泡）----------
# icon 取值与前端 IconSymbols 一致：heart / sensor / camera / device
NOTIFICATIONS = [
    {"icon": "heart", "tone": "", "text": "糯米已经等你 2 小时啦，快回家陪陪它吧～",
     "time_ago": "2 分钟前", "read": 0, "sort": 1},
    {"icon": "sensor", "tone": "mint", "text": "智能项圈固件已更新至 v2.4.1",
     "time_ago": "1 小时前", "read": 0, "sort": 2},
    {"icon": "camera", "tone": "amber", "text": "门口摄像头检测到移动，已自动抓拍",
     "time_ago": "3 小时前", "read": 1, "sort": 3},
]

# ---------- 9.2 快速互动话术（POST /api/pets/{key}/interact 返回）----------
INTERACT_MESSAGES = {
    "pet": "已开启抚摸互动，小猫正在呼噜呼噜～",
    "voice": "语音对话已就绪，说点什么吧",
    "game": "正在进入趣味游戏：逗猫棒大作战",
    "music": "音乐已开始播放",
}

# ---------- 10. 成长时间线 ----------
# 标题/描述里带 {level} {growth} {name} {breed} 的占位，接口层按当前宠物替换
TIMELINE = [
    {"event_date": "2026-11-19", "title": "升级 LV.{level} 🎉",
     "description": "陪伴值突破 {growth}，解锁了新的互动姿势「肚皮蹭蹭」。", "sort": 1},
    {"event_date": "2026-11-02", "title": "第 100 天纪念",
     "description": "我们一起度过了第 100 天，拍了好多照片～", "sort": 2},
    {"event_date": "2026-09-18", "title": "第一次学会击掌",
     "description": "{name}终于愿意抬起小爪子和我击掌啦！", "sort": 3},
    {"event_date": "2026-07-14", "title": "来到这个家",
     "description": "那一天，一只小小的{breed}走进了我们的生活。", "sort": 4},
]

# ---------- 11. 里程碑统计 ----------
MILESTONES = [
    {"label": "累计互动", "value": "328 次", "tail": "进行中", "sort": 1},
    {"label": "一起听过的歌", "value": "56 首", "tail": "进行中", "sort": 2},
    {"label": "趣味游戏", "value": "24 局", "tail": "进行中", "sort": 3},
    {"label": "开心时刻", "value": "{days} 天", "tail": "达成", "sort": 4},
]

# ---------- 12. 照片墙 ----------
# image_key 对应前端本地图片资源（cat / kitten）；image_url 预留后端图片地址
GALLERY = [
    {"image_key": "cat", "image_url": "", "caption": "午后的阳光", "sort": 1},
    {"image_key": "kitten", "image_url": "", "caption": "睡得正香", "sort": 2},
    {"image_key": "cat", "image_url": "", "caption": "窗边发呆", "sort": 3},
    {"image_key": "kitten", "image_url": "", "caption": "打个小盹", "sort": 4},
]

# ---------- 13. 聊天兜底话术（大模型未接入时使用） ----------
CHAT_REPLIES = [
    "好呀，我最喜欢陪着主人啦～ 😺",
    "嗯嗯，我记住啦！我们是最要好的朋友～",
    "喵～ 我开心得打滚啦！",
    "要不要一起晒晒太阳？我找到一个超棒的位置 ☀️",
]

# ============================================================================
# 以下为硬件监控域初始数据，对应 /api/sensors、/api/alarms、/api/dashboard，
# 供 ESP32 / 香橙派链路联调使用。
# ============================================================================

MONITOR_DEVICES = [
    {"device_name": "客厅 ESP32-S3", "device_type": "ESP32_S3", "sn": "esp32-s3-001",
     "online": True, "location": "客厅"},
    {"device_name": "门口香橙派摄像头", "device_type": "ORANGE_PI", "sn": "orangepi-cam-001",
     "online": True, "location": "门口"},
]

MONITOR_SENSORS = [
    ("esp32-s3-001", 23.2, 62.0, False, True, "2026-11-20 08:00:00"),
    ("esp32-s3-001", 23.8, 61.0, False, True, "2026-11-20 09:00:00"),
    ("esp32-s3-001", 24.5, 59.0, False, True, "2026-11-20 10:00:00"),
    ("esp32-s3-001", 25.0, 58.0, True, True, "2026-11-20 11:00:00"),
    ("esp32-s3-001", 25.6, 56.0, False, True, "2026-11-20 12:00:00"),
    ("esp32-s3-001", 26.1, 55.0, False, True, "2026-11-20 13:00:00"),
    ("esp32-s3-001", 26.8, 53.0, True, False, "2026-11-20 14:00:00"),
    ("esp32-s3-001", 27.0, 52.0, False, True, "2026-11-20 15:00:00"),
    ("esp32-s3-001", 26.4, 54.0, False, True, "2026-11-20 16:00:00"),
    ("esp32-s3-001", 25.9, 55.5, False, True, "2026-11-20 17:00:00"),
    ("esp32-s3-001", 25.5, 56.0, False, True, "2026-11-20 18:00:00"),
]

MONITOR_ALARMS = [
    ("esp32-s3-001", "orangepi-cam-001", "PERSON_DETECT", 0.93,
     "", "", False,
     "检测到人体，已自动抓拍并联动声光报警", "2026-11-20 08:50:00"),
    ("esp32-s3-001", "orangepi-cam-001", "PERSON_DETECT", 0.85,
     "", "", True,
     "检测到人体，夜视模式抓拍", "2026-11-20 10:20:00"),
    ("esp32-s3-001", "orangepi-cam-001", "PERSON_DETECT", 0.91,
     "", "", True,
     "检测到人体，已自动抓拍并联动云台跟踪", "2026-11-20 13:15:00"),
    ("esp32-s3-001", "orangepi-cam-001", "PERSON_DETECT", 0.96,
     "", "", False,
     "检测到人体，高置信度告警", "2026-11-20 16:40:00"),
    ("esp32-s3-001", "orangepi-cam-001", "PERSON_DETECT", 0.89,
     "", "", False,
     "检测到人体，夜视模式抓拍", "2026-11-20 18:10:00"),
]
