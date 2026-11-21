-- ============================================================
-- PetOS 一体化后端 MySQL 导入脚本（建库 + 建表 + 演示种子数据）
-- 适用：陪伴域（设备/宠物/聊天/插件/记忆/设置）+ 监控域（传感器/告警/设备）
--
-- 用法：
--   方式1（命令行）：mysql -u root -p < petos_companion_mysql.sql
--   方式2（客户端）：Navicat / DBeaver 打开本文件全选执行
-- 说明：默认后端使用 SQLite（免安装，首次启动自动建表灌数据）；
--       本脚本仅在切换 MySQL 时使用，表名/字段名与 SQLite 版本完全一致。
-- ============================================================

-- 1. 创建数据库（不存在才创建），utf8mb4 支持中文与 emoji
CREATE DATABASE IF NOT EXISTS petos_companion
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_general_ci;

USE petos_companion;

-- ============================================================
-- 2. 陪伴域表
-- ============================================================

-- 2.1 设备表（is_nearby=0 已绑定，=1 附近未配对）
DROP TABLE IF EXISTS companion_device;
CREATE TABLE companion_device (
    id        VARCHAR(40)  PRIMARY KEY COMMENT '设备编号（d-nuomi）',
    name      VARCHAR(100) NOT NULL COMMENT '设备名称',
    pet_key   VARCHAR(40)  DEFAULT NULL COMMENT '关联宠物档案 key',
    place     VARCHAR(100) DEFAULT NULL COMMENT '摆放位置',
    online    TINYINT(1)   DEFAULT 0 COMMENT '在线状态 1/0',
    signal    INT          DEFAULT 0 COMMENT '信号强度 0-100',
    battery   INT          DEFAULT 0 COMMENT '电量 0-100',
    fw        VARCHAR(30)  DEFAULT NULL COMMENT '固件版本',
    wifi      VARCHAR(100) DEFAULT NULL COMMENT '所连 Wi-Fi',
    last      VARCHAR(100) DEFAULT NULL COMMENT '最近互动描述',
    is_nearby TINYINT(1)   DEFAULT 0 COMMENT '1=附近未配对 0=已绑定',
    sort      INT          DEFAULT 0 COMMENT '排序号'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='陪伴设备表';

-- 2.2 宠物档案表
DROP TABLE IF EXISTS pet;
CREATE TABLE pet (
    pet_key        VARCHAR(40) PRIMARY KEY COMMENT '档案 key（nuomi…）',
    name           VARCHAR(40) NOT NULL COMMENT '宠物名',
    emoji          VARCHAR(20) DEFAULT NULL COMMENT '表情图标',
    breed          VARCHAR(40) DEFAULT NULL COMMENT '品种',
    age            VARCHAR(40) DEFAULT NULL COMMENT '年龄（展示文本）',
    weight         VARCHAR(40) DEFAULT NULL COMMENT '体重（展示文本）',
    level          INT         DEFAULT 1 COMMENT '等级',
    growth         INT         DEFAULT 0 COMMENT '成长值 0-100',
    mood           VARCHAR(20) DEFAULT NULL COMMENT '情绪状态',
    active         INT         DEFAULT 0 COMMENT '活跃度 0-100',
    interact       INT         DEFAULT 0 COMMENT '今日互动次数',
    days           INT         DEFAULT 0 COMMENT '陪伴天数',
    `desc`         VARCHAR(255) DEFAULT NULL COMMENT '一句话描述',
    heart_rate     INT         DEFAULT 0 COMMENT '心率（次/分）',
    active_minutes INT         DEFAULT 0 COMMENT '今日活动分钟数',
    sleep_hours    DECIMAL(4,1) DEFAULT 0 COMMENT '睡眠时长（小时）',
    last_checkup   VARCHAR(20) DEFAULT NULL COMMENT '最近体检日期',
    moments        INT         DEFAULT 0 COMMENT '精彩瞬间数',
    songs          INT         DEFAULT 0 COMMENT '听过的歌数',
    games          INT         DEFAULT 0 COMMENT '游戏局数',
    energy         INT         DEFAULT 0 COMMENT '能量值 0-100',
    mood_tag       VARCHAR(20) DEFAULT NULL COMMENT '情绪标签',
    health_status  VARCHAR(20) DEFAULT NULL COMMENT '健康状态'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='宠物档案表';

-- 2.3 天气表（单行，id 固定 1）
DROP TABLE IF EXISTS weather;
CREATE TABLE weather (
    id    INT PRIMARY KEY,
    text  VARCHAR(20) COMMENT '天气描述',
    temp  INT         COMMENT '温度（摄氏度）',
    wind  VARCHAR(20) COMMENT '风力描述'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='天气表';

-- 2.4 陪伴趋势图表
DROP TABLE IF EXISTS chart_stat;
CREATE TABLE chart_stat (
    id        BIGINT AUTO_INCREMENT PRIMARY KEY,
    range_key VARCHAR(10) NOT NULL COMMENT 'week/month/quarter',
    label     VARCHAR(20) COMMENT 'X 轴标签',
    interact  INT         COMMENT '互动次数',
    online    INT         COMMENT '在线时长指数',
    sort      INT DEFAULT 0,
    KEY idx_range (range_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='陪伴趋势统计表';

-- 2.5 聊天记录表
DROP TABLE IF EXISTS chat_message;
CREATE TABLE chat_message (
    id         BIGINT AUTO_INCREMENT PRIMARY KEY,
    who        VARCHAR(10) NOT NULL COMMENT 'me=主人 pet=小宠',
    text       TEXT        NOT NULL COMMENT '消息文本',
    device_id  VARCHAR(40) COMMENT '关联设备',
    created_at VARCHAR(30) COMMENT '发送时间',
    sort       INT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='聊天记录表';

-- 2.6 今日小确幸打卡表
DROP TABLE IF EXISTS bless_item;
CREATE TABLE bless_item (
    id    BIGINT AUTO_INCREMENT PRIMARY KEY,
    text  VARCHAR(255) NOT NULL COMMENT '打卡事项',
    done  TINYINT(1) DEFAULT 0 COMMENT '是否完成 1/0',
    sort  INT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='小确幸打卡表';

-- 2.7 插件表
DROP TABLE IF EXISTS plugin;
CREATE TABLE plugin (
    id      BIGINT AUTO_INCREMENT PRIMARY KEY,
    name    VARCHAR(60) NOT NULL COMMENT '插件名',
    icon    VARCHAR(30) COMMENT '图标标识',
    color   VARCHAR(20) COMMENT '颜色修饰类',
    `desc`  VARCHAR(255) COMMENT '插件描述',
    enabled TINYINT(1) DEFAULT 0 COMMENT '是否启用 1/0',
    sort    INT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='插件表';

-- 2.8 全局键值设置表（结构化值以 JSON 存储）
DROP TABLE IF EXISTS app_setting;
CREATE TABLE app_setting (
    `key`   VARCHAR(40) PRIMARY KEY COMMENT '设置项 key',
    value   TEXT COMMENT 'JSON 序列化后的值'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='全局设置表';

-- 2.9 成长时间线表
DROP TABLE IF EXISTS memory_timeline;
CREATE TABLE memory_timeline (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    pet_key     VARCHAR(40) COMMENT '所属宠物',
    event_date  VARCHAR(20) COMMENT '事件日期',
    title       VARCHAR(100) COMMENT '标题（可含占位符）',
    description VARCHAR(255) COMMENT '描述（可含占位符）',
    sort        INT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='成长时间线表';

-- 2.10 里程碑统计表
DROP TABLE IF EXISTS memory_milestone;
CREATE TABLE memory_milestone (
    id      BIGINT AUTO_INCREMENT PRIMARY KEY,
    pet_key VARCHAR(40) COMMENT '所属宠物',
    label   VARCHAR(40) COMMENT '指标名',
    value   VARCHAR(40) COMMENT '指标值（可含占位符）',
    tail    VARCHAR(20) COMMENT '右侧状态文案',
    sort    INT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='里程碑统计表';

-- 2.11 照片墙表
DROP TABLE IF EXISTS gallery_item;
CREATE TABLE gallery_item (
    id         BIGINT AUTO_INCREMENT PRIMARY KEY,
    pet_key    VARCHAR(40) COMMENT '所属宠物',
    image_key  VARCHAR(20) COMMENT '前端本地图片标识 cat/kitten',
    image_url  VARCHAR(255) COMMENT '后端图片地址（预留）',
    caption    VARCHAR(60) COMMENT '图片说明',
    sort       INT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='照片墙表';

-- 2.12 通知中心表（顶栏通知气泡，已读状态落库）
DROP TABLE IF EXISTS notification;
CREATE TABLE notification (
    id       BIGINT AUTO_INCREMENT PRIMARY KEY,
    icon     VARCHAR(30) COMMENT '图标标识 heart/sensor/camera',
    tone     VARCHAR(20) COMMENT '颜色修饰 空/mint/amber',
    text     VARCHAR(255) NOT NULL COMMENT '通知正文',
    time_ago VARCHAR(30) COMMENT '相对时间文案',
    `read`   TINYINT(1) DEFAULT 0 COMMENT '是否已读 1/0',
    sort     INT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='通知中心表';

-- ============================================================
-- 3. 监控域表（遗留硬件链路）
-- ============================================================

DROP TABLE IF EXISTS monitor_device;
CREATE TABLE monitor_device (
    id             BIGINT AUTO_INCREMENT PRIMARY KEY,
    device_name    VARCHAR(100) COMMENT '设备名称',
    device_type    VARCHAR(30)  COMMENT 'ESP32_S3 / ORANGE_PI',
    sn             VARCHAR(60)  UNIQUE COMMENT '设备序列号',
    online         TINYINT(1)  DEFAULT 0,
    last_heartbeat VARCHAR(30),
    location       VARCHAR(100),
    create_time    VARCHAR(30)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='监控设备表';

DROP TABLE IF EXISTS sensor_data;
CREATE TABLE sensor_data (
    id            BIGINT AUTO_INCREMENT PRIMARY KEY,
    device_sn     VARCHAR(60),
    temperature   DECIMAL(10,2),
    humidity      DECIMAL(10,2),
    pir_triggered TINYINT(1) DEFAULT 0,
    door_closed   TINYINT(1) DEFAULT 0,
    report_time   VARCHAR(30),
    KEY idx_sn (device_sn)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='传感器数据表';

DROP TABLE IF EXISTS alarm_record;
CREATE TABLE alarm_record (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    device_sn   VARCHAR(60),
    camera_sn   VARCHAR(60),
    alarm_type  VARCHAR(30),
    confidence  DECIMAL(5,2),
    image_path  VARCHAR(500),
    image_url   VARCHAR(500),
    handled     TINYINT(1) DEFAULT 0,
    description VARCHAR(255),
    alarm_time  VARCHAR(30),
    create_time VARCHAR(30),
    KEY idx_sn (device_sn)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='告警抓拍记录表';

-- ============================================================
-- 4. 演示种子数据（与后端 app/seed.py 保持一致）
-- ============================================================

-- 4.1 陪伴设备（含附近设备）
INSERT INTO companion_device (id, name, pet_key, place, online, signal, battery, fw, wifi, `last`, is_nearby, sort) VALUES
('d-nuomi',  'PetOS 小橘', 'nuomi',  '客厅', 1, 92, 78, 'v2.4.1', 'PetOS-Home', '刚刚还在陪你',   0, 1),
('d-tuanzi', 'PetOS 团子', 'tuanzi', '卧室', 1, 76, 54, 'v2.3.8', 'PetOS-Home', '3 分钟前互动',  0, 2),
('d-mochi',  'PetOS 麻薯', 'mochi',  '书房', 0,  0, 12, 'v2.2.1', '—',          '2 天前离线',    0, 3),
('d-xiaobai','PetOS 小白', 'xiaobai','阳台', 1, 88,  0, '',       '',           '',              1, 1),
('d-huajuan','PetOS 花卷', 'huajuan','餐厅', 1, 64,  0, '',       '',           '',              1, 2);

-- 4.2 宠物档案
INSERT INTO pet (pet_key, name, emoji, breed, age, weight, level, growth, mood, active, interact, days, `desc`,
                 heart_rate, active_minutes, sleep_hours, last_checkup, moments, songs, games,
                 energy, mood_tag, health_status) VALUES
('nuomi',  '糯米', '🐱', '橘猫',   '1 岁 2 个月', '4.2 kg', 3, 68, '愉悦', 92, 12, 128, '一只喜欢晒太阳的小猫',     132, 46, 11.5, '2026-11-02', 46, 56, 24, 78, '平静', '良好'),
('tuanzi', '团子', '🐰', '布偶猫', '8 个月',      '3.6 kg', 2, 41, '安静', 76,  8,  63, '一只爱睡觉的软乎乎小猫',   128, 32, 12.0, '2026-10-28', 21, 18,  9, 72, '慵懒', '良好'),
('mochi',  '麻薯', '🐻', '英短',   '2 岁 1 个月', '5.1 kg', 4, 85, '慵懒', 61, 21, 210, '一只慢吞吞的胖乎乎小猫',   125, 28, 11.0, '2026-10-15', 88, 40, 17, 55, '困倦', '偏胖'),
('xiaobai','小白', '🐶', '柯基',   '1 岁',        '6.0 kg', 1, 22, '兴奋', 95,  3,  12, '刚来到家的新伙伴',         140, 55, 10.0, '2026-11-18',  3,  2,  1, 88, '活跃', '良好'),
('huajuan','花卷', '🐹', '仓鼠',   '4 个月',      '0.1 kg', 1, 15, '活泼', 88,  2,   7, '一团小小的毛球',           150, 20, 13.0, '2026-11-19',  2,  0,  0, 64, '好奇', '良好');

-- 4.3 天气
INSERT INTO weather (id, text, temp, wind) VALUES (1, '晴', 26, '微风');

-- 4.4 趋势图
INSERT INTO chart_stat (range_key, label, interact, online, sort) VALUES
('week',    '周一', 58, 52, 1), ('week',    '周二', 62, 48, 2), ('week',    '周三', 74, 56, 3),
('week',    '周四', 64, 60, 4), ('week',    '周五', 70, 58, 5), ('week',    '周六', 75, 62, 6),
('week',    '周日', 86, 66, 7),
('month',   '第1周', 61, 55, 1), ('month',  '第2周', 68, 58, 2), ('month',  '第3周', 66, 60, 3),
('month',   '第4周', 74, 63, 4), ('month',  '第5周', 82, 70, 5),
('quarter', '8月',   64, 58, 1), ('quarter', '9月',   73, 65, 2), ('quarter', '10月',  81, 70, 3);

-- 4.5 聊天初始记录
INSERT INTO chat_message (who, text, device_id, created_at, sort) VALUES
('pet', '主人你回来啦～今天想和我玩什么呀？😺', 'd-nuomi', NOW(), 1),
('me',  '今天天气怎么样？',                     'd-nuomi', NOW(), 2),
('pet', '今天是晴天，26°C，微风～很适合带我去晒太阳哦 ☀️', 'd-nuomi', NOW(), 3);

-- 4.6 小确幸打卡
INSERT INTO bless_item (text, done, sort) VALUES
('和小猫玩一会小游戏', 1, 1),
('给小猫摸头',         0, 2),
('一起看窗外的云',     0, 3);

-- 4.7 插件
INSERT INTO plugin (name, icon, color, `desc`, enabled, sort) VALUES
('天气助手',   'weather', '',       '语音查询天气，出门前提醒你带伞。',             1, 1),
('音乐电台',   'music',   '--pink', '海量曲库与白噪音，陪它安静入眠。',             1, 2),
('睡前故事',   'memory',  '--violet','温柔的晚安故事，哄你和小猫一起入睡。',        1, 3),
('摄像头监控', 'camera',  '--mint', '✦ 亮点功能，1080P 实时画面与移动侦测。',      1, 4),
('健康提醒',   'health',  '--amber','喂食、驱虫与体检提醒，一个都不落下。',        0, 5),
('智能喂食',   'bolt',    '',       '定时定量投喂，记录每一餐的进食情况。',        0, 6),
('宠物翻译官', 'chat',    '--violet','试试听懂它的呼噜声与喵喵叫是什么意思。',      0, 7),
('打卡日历',   'clock',   '--mint', '记录陪伴的每一天，集齐专属纪念徽章。',        0, 8);

-- 4.8 全局设置（value 为 JSON）
INSERT INTO app_setting (`key`, value) VALUES
('connected',        'true'),
('active_device_id', '"d-nuomi"'),
('voice',            '{"wakeWord": "小宠小宠", "listening": false, "tts": true, "volume": 70}'),
('screen',           '{"on": true, "expression": "开心"}'),
('music',            '{"playing": false, "track": "午后猫咪轻音乐"}'),
('network',          '{"bluetooth": true, "wifiQuality": "信号良好", "firmwareLatest": true}'),
('device',           '{"mic": true, "micSensitivity": 80, "gimbal": true, "motion": true, "motionSensitivity": "中"}'),
('notify',           '{"message": true, "motion": true, "cloudSync": true}'),
('profile',          '{"language": "简体中文", "account": "主人", "appVersion": "2.4.1"}'),
('camera',           '{"resolution": "1080P", "fps": 24, "nightVision": true, "motionDetect": true, "twoWayAudio": true, "streamUrl": ""}');

-- 4.9 时间线
INSERT INTO memory_timeline (pet_key, event_date, title, description, sort) VALUES
(NULL, '2026-11-19', '升级 LV.{level} 🎉',   '陪伴值突破 {growth}，解锁了新的互动姿势「肚皮蹭蹭」。', 1),
(NULL, '2026-11-02', '第 100 天纪念',        '我们一起度过了第 100 天，拍了好多照片～',             2),
(NULL, '2026-09-18', '第一次学会击掌',        '{name}终于愿意抬起小爪子和我击掌啦！',                3),
(NULL, '2026-07-14', '来到这个家',            '那一天，一只小小的{breed}走进了我们的生活。',         4);

-- 4.10 里程碑
INSERT INTO memory_milestone (pet_key, label, value, tail, sort) VALUES
(NULL, '累计互动',     '328 次',  '进行中', 1),
(NULL, '一起听过的歌', '56 首',   '进行中', 2),
(NULL, '趣味游戏',     '24 局',   '进行中', 3),
(NULL, '开心时刻',     '{days} 天','达成',   4);

-- 4.11 照片墙
INSERT INTO gallery_item (pet_key, image_key, image_url, caption, sort) VALUES
(NULL, 'cat',    '', '午后的阳光', 1),
(NULL, 'kitten', '', '睡得正香',   2),
(NULL, 'cat',    '', '窗边发呆',   3),
(NULL, 'kitten', '', '打个小盹',   4);

-- 4.11.1 通知中心
INSERT INTO notification (icon, tone, text, time_ago, `read`, sort) VALUES
('heart',  '',      '糯米已经等你 2 小时啦，快回家陪陪它吧～', '2 分钟前', 0, 1),
('sensor', 'mint',  '智能项圈固件已更新至 v2.4.1',            '1 小时前', 0, 2),
('camera', 'amber', '门口摄像头检测到移动，已自动抓拍',        '3 小时前', 1, 3);

-- 4.12 监控设备 / 传感器 / 告警
INSERT INTO monitor_device (device_name, device_type, sn, online, last_heartbeat, location, create_time) VALUES
('客厅 ESP32-S3',   'ESP32_S3',  'esp32-s3-001',   1, NOW(), '客厅', '客厅'),
('门口香橙派摄像头','ORANGE_PI', 'orangepi-cam-001',1, NOW(), '门口', '门口');

INSERT INTO sensor_data (device_sn, temperature, humidity, pir_triggered, door_closed, report_time) VALUES
('esp32-s3-001', 23.2, 62.0, 0, 1, '2026-11-20 08:00:00'),
('esp32-s3-001', 23.8, 61.0, 0, 1, '2026-11-20 09:00:00'),
('esp32-s3-001', 24.5, 59.0, 0, 1, '2026-11-20 10:00:00'),
('esp32-s3-001', 25.0, 58.0, 1, 1, '2026-11-20 11:00:00'),
('esp32-s3-001', 25.6, 56.0, 0, 1, '2026-11-20 12:00:00'),
('esp32-s3-001', 26.1, 55.0, 0, 1, '2026-11-20 13:00:00'),
('esp32-s3-001', 26.8, 53.0, 1, 0, '2026-11-20 14:00:00'),
('esp32-s3-001', 27.0, 52.0, 0, 1, '2026-11-20 15:00:00'),
('esp32-s3-001', 26.4, 54.0, 0, 1, '2026-11-20 16:00:00'),
('esp32-s3-001', 25.9, 55.5, 0, 1, '2026-11-20 17:00:00'),
('esp32-s3-001', 25.5, 56.0, 0, 1, '2026-11-20 18:00:00');

INSERT INTO alarm_record (device_sn, camera_sn, alarm_type, confidence, image_path, image_url, handled, description, alarm_time, create_time) VALUES
('esp32-s3-001', 'orangepi-cam-001', 'PERSON_DETECT', 0.93, './upload-images/sample_1.jpg', '/images/sample_1.jpg', 0, '检测到人体，已自动抓拍并联动声光报警', '2026-11-20 08:50:00', '2026-11-20 08:50:00'),
('esp32-s3-001', 'orangepi-cam-001', 'PERSON_DETECT', 0.85, './upload-images/sample_2.jpg', '/images/sample_2.jpg', 1, '检测到人体，夜视模式抓拍',             '2026-11-20 10:20:00', '2026-11-20 10:20:00'),
('esp32-s3-001', 'orangepi-cam-001', 'PERSON_DETECT', 0.91, './upload-images/sample_3.jpg', '/images/sample_3.jpg', 1, '检测到人体，已自动抓拍并联动云台跟踪', '2026-11-20 13:15:00', '2026-11-20 13:15:00'),
('esp32-s3-001', 'orangepi-cam-001', 'PERSON_DETECT', 0.96, './upload-images/sample_1.jpg', '/images/sample_1.jpg', 0, '检测到人体，高置信度告警',             '2026-11-20 16:40:00', '2026-11-20 16:40:00'),
('esp32-s3-001', 'orangepi-cam-001', 'PERSON_DETECT', 0.89, './upload-images/sample_2.jpg', '/images/sample_2.jpg', 0, '检测到人体，夜视模式抓拍',             '2026-11-20 18:10:00', '2026-11-20 18:10:00');
