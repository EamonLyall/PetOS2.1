-- ============================================================
-- PetOS 陪伴系统 · SQLite 数据快照（由 scripts/db_tool.py 自动导出）
-- 导入方式：python scripts/db_tool.py import --force
-- 说明：包含建表语句与全部业务数据，导入后与导出时状态完全一致。
-- ============================================================

BEGIN TRANSACTION;
CREATE TABLE alarm_record (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        device_sn   TEXT,
        camera_sn   TEXT,
        alarm_type  TEXT,
        confidence  REAL,
        image_path  TEXT,
        image_url   TEXT,
        handled     INTEGER DEFAULT 0,
        description TEXT,
        alarm_time  TEXT,
        create_time TEXT
    );
INSERT INTO "alarm_record" VALUES(1,'esp32-s3-001','orangepi-cam-001','PERSON_DETECT',0.93,'./upload-images/sample_1.jpg','/images/sample_1.jpg',0,'检测到人体，已自动抓拍并联动声光报警','2026-11-20 08:50:00','2026-11-20 08:50:00');
INSERT INTO "alarm_record" VALUES(2,'esp32-s3-001','orangepi-cam-001','PERSON_DETECT',0.85,'./upload-images/sample_2.jpg','/images/sample_2.jpg',1,'检测到人体，夜视模式抓拍','2026-11-20 10:20:00','2026-11-20 10:20:00');
INSERT INTO "alarm_record" VALUES(3,'esp32-s3-001','orangepi-cam-001','PERSON_DETECT',0.91,'./upload-images/sample_3.jpg','/images/sample_3.jpg',1,'检测到人体，已自动抓拍并联动云台跟踪','2026-11-20 13:15:00','2026-11-20 13:15:00');
INSERT INTO "alarm_record" VALUES(4,'esp32-s3-001','orangepi-cam-001','PERSON_DETECT',0.96,'./upload-images/sample_1.jpg','/images/sample_1.jpg',0,'检测到人体，高置信度告警','2026-11-20 16:40:00','2026-11-20 16:40:00');
INSERT INTO "alarm_record" VALUES(5,'esp32-s3-001','orangepi-cam-001','PERSON_DETECT',0.89,'./upload-images/sample_2.jpg','/images/sample_2.jpg',0,'检测到人体，夜视模式抓拍','2026-11-20 18:10:00','2026-11-20 18:10:00');
CREATE TABLE app_setting (
        key   TEXT PRIMARY KEY,                -- 设置项 key
        value TEXT                             -- JSON 序列化后的值
    );
INSERT INTO "app_setting" VALUES('connected','true');
INSERT INTO "app_setting" VALUES('active_device_id','"d-nuomi"');
INSERT INTO "app_setting" VALUES('voice','{"wakeWord": "小宠小宠", "listening": false, "tts": true, "volume": 70}');
INSERT INTO "app_setting" VALUES('screen','{"on": true, "expression": "开心"}');
INSERT INTO "app_setting" VALUES('music','{"playing": false, "track": "午后猫咪轻音乐"}');
INSERT INTO "app_setting" VALUES('network','{"bluetooth": true, "wifiQuality": "信号良好", "firmwareLatest": true}');
INSERT INTO "app_setting" VALUES('device','{"mic": true, "micSensitivity": 80, "gimbal": true, "motion": true, "motionSensitivity": "中"}');
INSERT INTO "app_setting" VALUES('notify','{"message": true, "motion": true, "cloudSync": true}');
INSERT INTO "app_setting" VALUES('profile','{"language": "简体中文", "account": "主人", "appVersion": "2.4.1"}');
INSERT INTO "app_setting" VALUES('camera','{"resolution": "1080P", "fps": 24, "nightVision": true, "motionDetect": true, "twoWayAudio": true, "streamUrl": ""}');
CREATE TABLE bless_item (
        id    INTEGER PRIMARY KEY AUTOINCREMENT,
        text  TEXT NOT NULL,                   -- 打卡事项
        done  INTEGER DEFAULT 0,               -- 是否完成 1/0
        sort  INTEGER DEFAULT 0
    );
INSERT INTO "bless_item" VALUES(1,'和小猫玩一会小游戏',1,1);
INSERT INTO "bless_item" VALUES(2,'给小猫摸头',0,2);
INSERT INTO "bless_item" VALUES(3,'一起看窗外的云',0,3);
CREATE TABLE chart_stat (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        range_key  TEXT NOT NULL,              -- week / month / quarter
        label      TEXT,                       -- X 轴标签
        interact   INTEGER,                    -- 互动次数
        online     INTEGER,                    -- 在线时长指数
        sort       INTEGER DEFAULT 0
    );
INSERT INTO "chart_stat" VALUES(1,'week','周一',58,52,1);
INSERT INTO "chart_stat" VALUES(2,'week','周二',62,48,2);
INSERT INTO "chart_stat" VALUES(3,'week','周三',74,56,3);
INSERT INTO "chart_stat" VALUES(4,'week','周四',64,60,4);
INSERT INTO "chart_stat" VALUES(5,'week','周五',70,58,5);
INSERT INTO "chart_stat" VALUES(6,'week','周六',75,62,6);
INSERT INTO "chart_stat" VALUES(7,'week','周日',86,66,7);
INSERT INTO "chart_stat" VALUES(8,'month','第1周',61,55,1);
INSERT INTO "chart_stat" VALUES(9,'month','第2周',68,58,2);
INSERT INTO "chart_stat" VALUES(10,'month','第3周',66,60,3);
INSERT INTO "chart_stat" VALUES(11,'month','第4周',74,63,4);
INSERT INTO "chart_stat" VALUES(12,'month','第5周',82,70,5);
INSERT INTO "chart_stat" VALUES(13,'quarter','8月',64,58,1);
INSERT INTO "chart_stat" VALUES(14,'quarter','9月',73,65,2);
INSERT INTO "chart_stat" VALUES(15,'quarter','10月',81,70,3);
CREATE TABLE chat_message (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        who        TEXT NOT NULL,              -- me=主人 pet=小宠
        text       TEXT NOT NULL,              -- 消息文本
        device_id  TEXT,                       -- 关联设备
        created_at TEXT,                       -- 发送时间（ISO 字符串）
        sort       INTEGER DEFAULT 0
    );
INSERT INTO "chat_message" VALUES(1,'pet','主人你回来啦～今天想和我玩什么呀？😺',NULL,'2026-11-21T17:40:32',1);
INSERT INTO "chat_message" VALUES(2,'me','今天天气怎么样？',NULL,'2026-11-21T17:40:32',2);
INSERT INTO "chat_message" VALUES(3,'pet','今天是晴天，26°C，微风～很适合带我去晒太阳哦 ☀️',NULL,'2026-11-21T17:40:32',3);
CREATE TABLE companion_device (
        id          TEXT PRIMARY KEY,          -- 设备唯一编号（d-nuomi）
        name        TEXT NOT NULL,             -- 设备名称
        pet_key     TEXT,                      -- 关联宠物档案 key
        place       TEXT,                      -- 摆放位置
        online      INTEGER DEFAULT 0,         -- 在线状态 1/0
        signal      INTEGER DEFAULT 0,         -- 信号强度 0-100
        battery     INTEGER DEFAULT 0,         -- 电量 0-100
        fw          TEXT,                      -- 固件版本
        wifi        TEXT,                      -- 所连 Wi-Fi
        last        TEXT,                      -- 最近互动描述
        is_nearby   INTEGER DEFAULT 0,         -- 1=附近未配对 0=已绑定
        sort        INTEGER DEFAULT 0          -- 排序号
    );
INSERT INTO "companion_device" VALUES('d-nuomi','PetOS 小橘','nuomi','客厅',1,92,78,'v2.4.1','PetOS-Home','刚刚还在陪你',0,1);
INSERT INTO "companion_device" VALUES('d-tuanzi','PetOS 团子','tuanzi','卧室',1,76,54,'v2.3.8','PetOS-Home','3 分钟前互动',0,2);
INSERT INTO "companion_device" VALUES('d-mochi','PetOS 麻薯','mochi','书房',0,0,12,'v2.2.1','—','2 天前离线',0,3);
INSERT INTO "companion_device" VALUES('d-xiaobai','PetOS 小白','xiaobai','阳台',1,88,66,'v2.4.0','PetOS-Home','刚刚配对',1,1);
INSERT INTO "companion_device" VALUES('d-huajuan','PetOS 花卷','huajuan','餐厅',0,64,0,'','—','',1,2);
CREATE TABLE gallery_item (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        pet_key    TEXT,                       -- 所属宠物
        image_key  TEXT,                       -- 前端本地图片标识 cat/kitten
        image_url  TEXT,                       -- 后端图片地址（预留）
        caption    TEXT,                       -- 图片说明
        sort       INTEGER DEFAULT 0
    );
INSERT INTO "gallery_item" VALUES(1,NULL,'cat','','午后的阳光',1);
INSERT INTO "gallery_item" VALUES(2,NULL,'kitten','','睡得正香',2);
INSERT INTO "gallery_item" VALUES(3,NULL,'cat','','窗边发呆',3);
INSERT INTO "gallery_item" VALUES(4,NULL,'kitten','','打个小盹',4);
CREATE TABLE memory_milestone (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        pet_key  TEXT,                         -- 所属宠物
        label    TEXT,                         -- 指标名
        value    TEXT,                         -- 指标值（可含占位符）
        tail     TEXT,                         -- 右侧状态文案
        sort     INTEGER DEFAULT 0
    );
INSERT INTO "memory_milestone" VALUES(1,NULL,'累计互动','328 次','进行中',1);
INSERT INTO "memory_milestone" VALUES(2,NULL,'一起听过的歌','56 首','进行中',2);
INSERT INTO "memory_milestone" VALUES(3,NULL,'趣味游戏','24 局','进行中',3);
INSERT INTO "memory_milestone" VALUES(4,NULL,'开心时刻','{days} 天','达成',4);
CREATE TABLE memory_timeline (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        pet_key     TEXT,                      -- 所属宠物（预留多宠物）
        event_date  TEXT,                      -- 事件日期
        title       TEXT,                      -- 标题（可含占位符）
        description TEXT,                      -- 描述（可含占位符）
        sort        INTEGER DEFAULT 0
    );
INSERT INTO "memory_timeline" VALUES(1,NULL,'2026-11-19','升级 LV.{level} 🎉','陪伴值突破 {growth}，解锁了新的互动姿势「肚皮蹭蹭」。',1);
INSERT INTO "memory_timeline" VALUES(2,NULL,'2026-11-02','第 100 天纪念','我们一起度过了第 100 天，拍了好多照片～',2);
INSERT INTO "memory_timeline" VALUES(3,NULL,'2026-09-18','第一次学会击掌','{name}终于愿意抬起小爪子和我击掌啦！',3);
INSERT INTO "memory_timeline" VALUES(4,NULL,'2026-07-14','来到这个家','那一天，一只小小的{breed}走进了我们的生活。',4);
CREATE TABLE monitor_device (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        device_name    TEXT,
        device_type    TEXT,                   -- ESP32_S3 / ORANGE_PI
        sn             TEXT UNIQUE,            -- 设备序列号
        online         INTEGER DEFAULT 0,
        last_heartbeat TEXT,
        location       TEXT,
        create_time    TEXT
    );
INSERT INTO "monitor_device" VALUES(1,'客厅 ESP32-S3','ESP32_S3','esp32-s3-001',1,'2026-11-21T17:40:32','客厅','2026-11-21T17:40:32');
INSERT INTO "monitor_device" VALUES(2,'门口香橙派摄像头','ORANGE_PI','orangepi-cam-001',1,'2026-11-21T17:40:32','门口','2026-11-21T17:40:32');
CREATE TABLE notification (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        icon     TEXT,                         -- 图标标识（heart/sensor/camera）
        tone     TEXT,                         -- 颜色修饰（空/mint/amber）
        text     TEXT NOT NULL,                -- 通知正文
        time_ago TEXT,                         -- 相对时间文案
        read     INTEGER DEFAULT 0,            -- 是否已读 1/0
        sort     INTEGER DEFAULT 0
    );
INSERT INTO "notification" VALUES(1,'heart','','糯米已经等你 2 小时啦，快回家陪陪它吧～','2 分钟前',0,1);
INSERT INTO "notification" VALUES(2,'sensor','mint','智能项圈固件已更新至 v2.4.1','1 小时前',0,2);
INSERT INTO "notification" VALUES(3,'camera','amber','门口摄像头检测到移动，已自动抓拍','3 小时前',1,3);
CREATE TABLE pet (
        pet_key        TEXT PRIMARY KEY,      -- 档案 key（nuomi…）
        name           TEXT NOT NULL,         -- 宠物名
        emoji          TEXT,                  -- 表情图标
        breed          TEXT,                  -- 品种
        age            TEXT,                  -- 年龄（展示文本）
        weight         TEXT,                  -- 体重（展示文本）
        level          INTEGER DEFAULT 1,     -- 等级
        growth         INTEGER DEFAULT 0,     -- 成长值 0-100
        mood           TEXT,                  -- 情绪状态
        active         INTEGER DEFAULT 0,     -- 活跃度 0-100
        interact       INTEGER DEFAULT 0,     -- 今日互动次数
        days           INTEGER DEFAULT 0,     -- 陪伴天数
        desc           TEXT,                  -- 一句话描述
        heart_rate     INTEGER DEFAULT 0,     -- 心率（次/分）
        active_minutes INTEGER DEFAULT 0,     -- 今日活动分钟数
        sleep_hours    REAL DEFAULT 0,        -- 睡眠时长（小时）
        last_checkup   TEXT,                  -- 最近体检日期
        moments        INTEGER DEFAULT 0,     -- 精彩瞬间数
        songs          INTEGER DEFAULT 0,     -- 听过的歌数
        games          INTEGER DEFAULT 0,     -- 游戏局数
        energy         INTEGER DEFAULT 0,     -- 能量值 0-100（状态卡片）
        mood_tag       TEXT,                  -- 情绪标签（如 平静 / 活跃）
        health_status  TEXT                   -- 健康状态（如 良好 / 偏胖）
    );
INSERT INTO "pet" VALUES('nuomi','糯米','🐱','橘猫','1 岁 2 个月','4.2 kg',3,68,'愉悦',92,12,128,'一只喜欢晒太阳的小猫',132,46,11.5,'2026-11-02',46,56,24,78,'平静','良好');
INSERT INTO "pet" VALUES('tuanzi','团子','🐰','布偶猫','8 个月','3.6 kg',2,41,'安静',76,8,63,'一只爱睡觉的软乎乎小猫',128,32,12.0,'2026-10-28',21,18,9,72,'慵懒','良好');
INSERT INTO "pet" VALUES('mochi','麻薯','🐻','英短','2 岁 1 个月','5.1 kg',4,85,'慵懒',61,21,210,'一只慢吞吞的胖乎乎小猫',125,28,11.0,'2026-10-15',88,40,17,55,'困倦','偏胖');
INSERT INTO "pet" VALUES('xiaobai','小白','🐶','柯基','1 岁','6.0 kg',1,22,'兴奋',95,3,12,'刚来到家的新伙伴',140,55,10.0,'2026-11-18',3,2,1,88,'活跃','良好');
INSERT INTO "pet" VALUES('huajuan','花卷','🐹','仓鼠','4 个月','0.1 kg',1,15,'活泼',88,2,7,'一团小小的毛球',150,20,13.0,'2026-11-19',2,0,0,64,'好奇','良好');
CREATE TABLE plugin (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        name       TEXT NOT NULL,              -- 插件名
        icon       TEXT,                       -- 图标标识
        color      TEXT,                       -- 颜色修饰类
        desc       TEXT,                       -- 插件描述
        enabled    INTEGER DEFAULT 0,          -- 是否启用 1/0
        sort       INTEGER DEFAULT 0
    );
INSERT INTO "plugin" VALUES(1,'天气助手','weather','','语音查询天气，出门前提醒你带伞。',1,1);
INSERT INTO "plugin" VALUES(2,'音乐电台','music','--pink','海量曲库与白噪音，陪它安静入眠。',1,2);
INSERT INTO "plugin" VALUES(3,'睡前故事','memory','--violet','温柔的晚安故事，哄你和小猫一起入睡。',1,3);
INSERT INTO "plugin" VALUES(4,'摄像头监控','camera','--mint','✦ 亮点功能，1080P 实时画面与移动侦测。',1,4);
INSERT INTO "plugin" VALUES(5,'健康提醒','health','--amber','喂食、驱虫与体检提醒，一个都不落下。',0,5);
INSERT INTO "plugin" VALUES(6,'智能喂食','bolt','','定时定量投喂，记录每一餐的进食情况。',0,6);
INSERT INTO "plugin" VALUES(7,'宠物翻译官','chat','--violet','试试听懂它的呼噜声与喵喵叫是什么意思。',0,7);
INSERT INTO "plugin" VALUES(8,'打卡日历','clock','--mint','记录陪伴的每一天，集齐专属纪念徽章。',0,8);
CREATE TABLE sensor_data (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        device_sn     TEXT,
        temperature   REAL,
        humidity      REAL,
        pir_triggered INTEGER DEFAULT 0,
        door_closed   INTEGER DEFAULT 0,
        report_time   TEXT
    );
INSERT INTO "sensor_data" VALUES(1,'esp32-s3-001',23.2,62.0,0,1,'2026-11-20 08:00:00');
INSERT INTO "sensor_data" VALUES(2,'esp32-s3-001',23.8,61.0,0,1,'2026-11-20 09:00:00');
INSERT INTO "sensor_data" VALUES(3,'esp32-s3-001',24.5,59.0,0,1,'2026-11-20 10:00:00');
INSERT INTO "sensor_data" VALUES(4,'esp32-s3-001',25.0,58.0,1,1,'2026-11-20 11:00:00');
INSERT INTO "sensor_data" VALUES(5,'esp32-s3-001',25.6,56.0,0,1,'2026-11-20 12:00:00');
INSERT INTO "sensor_data" VALUES(6,'esp32-s3-001',26.1,55.0,0,1,'2026-11-20 13:00:00');
INSERT INTO "sensor_data" VALUES(7,'esp32-s3-001',26.8,53.0,1,0,'2026-11-20 14:00:00');
INSERT INTO "sensor_data" VALUES(8,'esp32-s3-001',27.0,52.0,0,1,'2026-11-20 15:00:00');
INSERT INTO "sensor_data" VALUES(9,'esp32-s3-001',26.4,54.0,0,1,'2026-11-20 16:00:00');
INSERT INTO "sensor_data" VALUES(10,'esp32-s3-001',25.9,55.5,0,1,'2026-11-20 17:00:00');
INSERT INTO "sensor_data" VALUES(11,'esp32-s3-001',25.5,56.0,0,1,'2026-11-20 18:00:00');
CREATE TABLE weather (
        id    INTEGER PRIMARY KEY,
        text  TEXT,                            -- 天气描述（晴/阴…）
        temp  INTEGER,                         -- 温度（摄氏度）
        wind  TEXT                             -- 风力描述
    );
INSERT INTO "weather" VALUES(1,'晴',26,'微风');
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('chart_stat',15);
INSERT INTO "sqlite_sequence" VALUES('chat_message',5);
INSERT INTO "sqlite_sequence" VALUES('bless_item',3);
INSERT INTO "sqlite_sequence" VALUES('plugin',8);
INSERT INTO "sqlite_sequence" VALUES('memory_timeline',4);
INSERT INTO "sqlite_sequence" VALUES('memory_milestone',4);
INSERT INTO "sqlite_sequence" VALUES('gallery_item',4);
INSERT INTO "sqlite_sequence" VALUES('notification',3);
INSERT INTO "sqlite_sequence" VALUES('monitor_device',2);
INSERT INTO "sqlite_sequence" VALUES('sensor_data',11);
INSERT INTO "sqlite_sequence" VALUES('alarm_record',5);
COMMIT;
