-- ============================================================
-- PetOS 人形监控系统 MySQL 导入脚本（建库 + 建表 + 演示数据）
-- 用法：
--   方式1（命令行）：mysql -u root -p < petos_monitor_mysql.sql
--   方式2（客户端）：Navicat / DBeaver 打开本文件全选执行
-- 导入后把 application.yml 数据源切换为 MySQL（文件内已有注释模板）
-- ============================================================

-- 1. 创建数据库（不存在才创建），指定 utf8mb4 字符集支持中文
CREATE DATABASE IF NOT EXISTS petos_monitor
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_general_ci;

USE petos_monitor;

-- 2. 设备表（先删后建，方便重复导入）
DROP TABLE IF EXISTS device;
CREATE TABLE device (
    id              BIGINT       NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    device_name     VARCHAR(100) DEFAULT NULL COMMENT '设备名称',
    device_type     VARCHAR(30)  DEFAULT NULL COMMENT '设备类型：ESP32_S3/ORANGE_PI',
    sn              VARCHAR(60)  DEFAULT NULL COMMENT '设备序列号',
    online          BIT(1)       DEFAULT NULL COMMENT '在线状态',
    last_heartbeat  DATETIME     DEFAULT NULL COMMENT '最近心跳时间',
    location        VARCHAR(100) DEFAULT NULL COMMENT '安装位置',
    create_time     DATETIME     DEFAULT NULL COMMENT '创建时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_sn (sn)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备表';

-- 3. 传感器数据表
DROP TABLE IF EXISTS sensor_data;
CREATE TABLE sensor_data (
    id              BIGINT       NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    device_sn       VARCHAR(60)  DEFAULT NULL COMMENT '设备SN',
    temperature     DECIMAL(10,2) DEFAULT NULL COMMENT '温度',
    humidity        DECIMAL(10,2) DEFAULT NULL COMMENT '湿度',
    pir_triggered   BIT(1)       DEFAULT NULL COMMENT 'PIR是否检测到人',
    door_closed     BIT(1)       DEFAULT NULL COMMENT '门是否关闭',
    report_time     DATETIME     DEFAULT NULL COMMENT '上报时间',
    PRIMARY KEY (id),
    KEY idx_device_sn (device_sn)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='传感器数据表';

-- 4. 告警抓拍记录表
DROP TABLE IF EXISTS alarm_record;
CREATE TABLE alarm_record (
    id              BIGINT       NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    device_sn       VARCHAR(60)  DEFAULT NULL COMMENT 'ESP32设备SN',
    camera_sn       VARCHAR(60)  DEFAULT NULL COMMENT '香橙派摄像头SN',
    alarm_type      VARCHAR(30)  DEFAULT NULL COMMENT '告警类型',
    confidence      DECIMAL(5,2) DEFAULT NULL COMMENT '识别置信度',
    image_path      VARCHAR(500) DEFAULT NULL COMMENT '图片存储路径',
    image_url       VARCHAR(500) DEFAULT NULL COMMENT '图片访问URL',
    handled         BIT(1)       DEFAULT NULL COMMENT '是否已处理',
    description     VARCHAR(255) DEFAULT NULL COMMENT '告警描述',
    alarm_time      DATETIME     DEFAULT NULL COMMENT '告警时间',
    create_time     DATETIME     DEFAULT NULL COMMENT '入库时间',
    PRIMARY KEY (id),
    KEY idx_device_sn (device_sn)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='告警抓拍记录表';

-- ============================================================
-- 5. 演示数据
-- b'1' 表示布尔真，b'0' 表示布尔假；NOW() 取当前时间
-- ============================================================
INSERT INTO device (device_name, device_type, sn, online, last_heartbeat, location, create_time)
VALUES ('客厅 ESP32-S3', 'ESP32_S3', 'esp32-s3-001', b'1', NOW(), '客厅', NOW());
INSERT INTO device (device_name, device_type, sn, online, last_heartbeat, location, create_time)
VALUES ('门口香橙派摄像头', 'ORANGE_PI', 'orangepi-cam-001', b'1', NOW(), '门口', NOW());

INSERT INTO sensor_data (device_sn, temperature, humidity, pir_triggered, door_closed, report_time) VALUES
('esp32-s3-001', 23.2, 62.0, b'0', b'1', DATE_SUB(NOW(), INTERVAL 10 HOUR)),
('esp32-s3-001', 23.8, 61.0, b'0', b'1', DATE_SUB(NOW(), INTERVAL 9 HOUR)),
('esp32-s3-001', 24.5, 59.0, b'0', b'1', DATE_SUB(NOW(), INTERVAL 8 HOUR)),
('esp32-s3-001', 25.0, 58.0, b'1', b'1', DATE_SUB(NOW(), INTERVAL 7 HOUR)),
('esp32-s3-001', 25.6, 56.0, b'0', b'1', DATE_SUB(NOW(), INTERVAL 6 HOUR)),
('esp32-s3-001', 26.1, 55.0, b'0', b'1', DATE_SUB(NOW(), INTERVAL 5 HOUR)),
('esp32-s3-001', 26.8, 53.0, b'1', b'0', DATE_SUB(NOW(), INTERVAL 4 HOUR)),
('esp32-s3-001', 27.0, 52.0, b'0', b'1', DATE_SUB(NOW(), INTERVAL 3 HOUR)),
('esp32-s3-001', 26.4, 54.0, b'0', b'1', DATE_SUB(NOW(), INTERVAL 2 HOUR)),
('esp32-s3-001', 25.9, 55.5, b'0', b'1', DATE_SUB(NOW(), INTERVAL 1 HOUR)),
('esp32-s3-001', 25.5, 56.0, b'0', b'1', NOW());

INSERT INTO alarm_record (device_sn, camera_sn, alarm_type, confidence, image_path, image_url,
                          handled, description, alarm_time, create_time) VALUES
('esp32-s3-001', 'orangepi-cam-001', 'PERSON_DETECT', 0.93, './upload-images/sample_1.jpg',
 '/images/sample_1.jpg', b'0', '检测到人体，已自动抓拍并联动声光报警',
 DATE_SUB(NOW(), INTERVAL 8 HOUR), DATE_SUB(NOW(), INTERVAL 8 HOUR)),
('esp32-s3-001', 'orangepi-cam-001', 'PERSON_DETECT', 0.85, './upload-images/sample_2.jpg',
 '/images/sample_2.jpg', b'1', '检测到人体，夜视模式抓拍',
 DATE_SUB(NOW(), INTERVAL 6 HOUR), DATE_SUB(NOW(), INTERVAL 6 HOUR)),
('esp32-s3-001', 'orangepi-cam-001', 'PERSON_DETECT', 0.91, './upload-images/sample_3.jpg',
 '/images/sample_3.jpg', b'1', '检测到人体，已自动抓拍并联动云台跟踪',
 DATE_SUB(NOW(), INTERVAL 4 HOUR), DATE_SUB(NOW(), INTERVAL 4 HOUR)),
('esp32-s3-001', 'orangepi-cam-001', 'PERSON_DETECT', 0.96, './upload-images/sample_1.jpg',
 '/images/sample_1.jpg', b'0', '检测到人体，高置信度告警',
 DATE_SUB(NOW(), INTERVAL 2 HOUR), DATE_SUB(NOW(), INTERVAL 2 HOUR)),
('esp32-s3-001', 'orangepi-cam-001', 'PERSON_DETECT', 0.89, './upload-images/sample_2.jpg',
 '/images/sample_2.jpg', b'0', '检测到人体，夜视模式抓拍', NOW(), NOW());
