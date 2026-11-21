-- ============================================================
-- 数据库初始化脚本（演示数据）
-- H2 内存库每次启动先由 JPA 建表，再执行本脚本
-- （application.yml 中 defer-datasource-initialization=true 保证顺序）。
-- CURRENT_TIMESTAMP 表示取后端启动的当前时间，让设备一启动就是“在线”状态。
-- ============================================================

-- ---------- 1. 两台设备（ESP32-S3 + 香橙派分开管理）----------
INSERT INTO device (id, device_name, device_type, sn, online, last_heartbeat, location, create_time)
VALUES (1, '客厅 ESP32-S3', 'ESP32_S3', 'esp32-s3-001', TRUE, CURRENT_TIMESTAMP,
        '客厅', TIMESTAMP '2026-11-20 08:00:00');

INSERT INTO device (id, device_name, device_type, sn, online, last_heartbeat, location, create_time)
VALUES (2, '门口香橙派摄像头', 'ORANGE_PI', 'orangepi-cam-001', TRUE, CURRENT_TIMESTAMP,
        '门口', TIMESTAMP '2026-11-20 08:00:00');

-- ---------- 2. 传感器历史数据（用于温湿度折线图，按时间排列）----------
INSERT INTO sensor_data (id, device_sn, temperature, humidity, pir_triggered, door_closed, report_time)
VALUES (1, 'esp32-s3-001', 23.2, 62.0, FALSE, TRUE, TIMESTAMP '2026-11-20 08:00:00');
INSERT INTO sensor_data (id, device_sn, temperature, humidity, pir_triggered, door_closed, report_time)
VALUES (2, 'esp32-s3-001', 23.8, 61.0, FALSE, TRUE, TIMESTAMP '2026-11-20 09:00:00');
INSERT INTO sensor_data (id, device_sn, temperature, humidity, pir_triggered, door_closed, report_time)
VALUES (3, 'esp32-s3-001', 24.5, 59.0, FALSE, TRUE, TIMESTAMP '2026-11-20 10:00:00');
INSERT INTO sensor_data (id, device_sn, temperature, humidity, pir_triggered, door_closed, report_time)
VALUES (4, 'esp32-s3-001', 25.0, 58.0, TRUE, TRUE, TIMESTAMP '2026-11-20 11:00:00');
INSERT INTO sensor_data (id, device_sn, temperature, humidity, pir_triggered, door_closed, report_time)
VALUES (5, 'esp32-s3-001', 25.6, 56.0, FALSE, TRUE, TIMESTAMP '2026-11-20 12:00:00');
INSERT INTO sensor_data (id, device_sn, temperature, humidity, pir_triggered, door_closed, report_time)
VALUES (6, 'esp32-s3-001', 26.1, 55.0, FALSE, TRUE, TIMESTAMP '2026-11-20 13:00:00');
INSERT INTO sensor_data (id, device_sn, temperature, humidity, pir_triggered, door_closed, report_time)
VALUES (7, 'esp32-s3-001', 26.8, 53.0, TRUE, FALSE, TIMESTAMP '2026-11-20 14:00:00');
INSERT INTO sensor_data (id, device_sn, temperature, humidity, pir_triggered, door_closed, report_time)
VALUES (8, 'esp32-s3-001', 27.0, 52.0, FALSE, TRUE, TIMESTAMP '2026-11-20 15:00:00');
INSERT INTO sensor_data (id, device_sn, temperature, humidity, pir_triggered, door_closed, report_time)
VALUES (9, 'esp32-s3-001', 26.4, 54.0, FALSE, TRUE, TIMESTAMP '2026-11-20 16:00:00');
INSERT INTO sensor_data (id, device_sn, temperature, humidity, pir_triggered, door_closed, report_time)
VALUES (10, 'esp32-s3-001', 25.9, 55.5, FALSE, TRUE, TIMESTAMP '2026-11-20 17:00:00');
-- 最新一条用当前时间，保证首页“最新温湿度”有值
INSERT INTO sensor_data (id, device_sn, temperature, humidity, pir_triggered, door_closed, report_time)
VALUES (11, 'esp32-s3-001', 25.5, 56.0, FALSE, TRUE, CURRENT_TIMESTAMP);

-- ---------- 3. 告警抓拍记录（图片指向 upload-images 里真实存在的样图）----------
INSERT INTO alarm_record (id, device_sn, camera_sn, alarm_type, confidence, image_path, image_url,
                          handled, description, alarm_time, create_time)
VALUES (1, 'esp32-s3-001', 'orangepi-cam-001', 'PERSON_DETECT', 0.93,
        './upload-images/sample_1.jpg', '/images/sample_1.jpg', FALSE,
        '检测到人体，已自动抓拍并联动声光报警',
        TIMESTAMP '2026-11-20 08:50:00', TIMESTAMP '2026-11-20 08:50:00');
INSERT INTO alarm_record (id, device_sn, camera_sn, alarm_type, confidence, image_path, image_url,
                          handled, description, alarm_time, create_time)
VALUES (2, 'esp32-s3-001', 'orangepi-cam-001', 'PERSON_DETECT', 0.85,
        './upload-images/sample_2.jpg', '/images/sample_2.jpg', TRUE,
        '检测到人体，夜视模式抓拍',
        TIMESTAMP '2026-11-20 10:20:00', TIMESTAMP '2026-11-20 10:20:00');
INSERT INTO alarm_record (id, device_sn, camera_sn, alarm_type, confidence, image_path, image_url,
                          handled, description, alarm_time, create_time)
VALUES (3, 'esp32-s3-001', 'orangepi-cam-001', 'PERSON_DETECT', 0.91,
        './upload-images/sample_3.jpg', '/images/sample_3.jpg', TRUE,
        '检测到人体，已自动抓拍并联动云台跟踪',
        TIMESTAMP '2026-11-20 13:15:00', TIMESTAMP '2026-11-20 13:15:00');
INSERT INTO alarm_record (id, device_sn, camera_sn, alarm_type, confidence, image_path, image_url,
                          handled, description, alarm_time, create_time)
VALUES (4, 'esp32-s3-001', 'orangepi-cam-001', 'PERSON_DETECT', 0.96,
        './upload-images/sample_1.jpg', '/images/sample_1.jpg', FALSE,
        '检测到人体，高置信度告警',
        TIMESTAMP '2026-11-20 16:40:00', TIMESTAMP '2026-11-20 16:40:00');
-- 最新一条未处理告警，用当前时间
INSERT INTO alarm_record (id, device_sn, camera_sn, alarm_type, confidence, image_path, image_url,
                          handled, description, alarm_time, create_time)
VALUES (5, 'esp32-s3-001', 'orangepi-cam-001', 'PERSON_DETECT', 0.89,
        './upload-images/sample_2.jpg', '/images/sample_2.jpg', FALSE,
        '检测到人体，夜视模式抓拍',
        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
