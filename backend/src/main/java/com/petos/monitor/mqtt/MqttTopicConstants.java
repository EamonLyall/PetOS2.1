package com.petos.monitor.mqtt;

/**
 * MQTT 主题常量类。
 * 主题（Topic）就像“频道”，发布者往频道里发，订阅者订阅同一个频道才能收到。
 * 这里把所有主题固定写死，ESP32、香橙派、后端三端严格照用，避免各写各的对不上。
 *
 * 命名规则：monitor / 设备类别 / 设备SN / 消息用途
 * 其中 + 是通配符，表示“这一段任意内容都行”，用来一次订阅某一类所有设备。
 */
public class MqttTopicConstants {

    // ===== 后端需要订阅的通配主题（接收上行消息）=====

    // 所有 ESP32 的传感器数据：monitor/esp32/任意SN/sensor
    public static final String SUB_ESP32_SENSOR = "monitor/esp32/+/sensor";
    // 所有 ESP32 的心跳/在线状态
    public static final String SUB_ESP32_STATUS = "monitor/esp32/+/status";
    // 所有 ESP32 的 PIR 原始告警
    public static final String SUB_ESP32_ALARM = "monitor/esp32/+/alarm";
    // 所有香橙派的 YOLO 识别结果
    public static final String SUB_ORANGEPI_DETECT = "monitor/orangepi/+/detect";

    // 把所有要订阅的主题放进数组，连接成功后统一订阅
    public static final String[] ALL_SUBSCRIBE_TOPICS = {
            SUB_ESP32_SENSOR,
            SUB_ESP32_STATUS,
            SUB_ESP32_ALARM,
            SUB_ORANGEPI_DETECT
    };

    /**
     * 拼接发给某台 ESP32 的控制主题
     *
     * @param sn 目标 ESP32 的序列号
     * @return monitor/esp32/{sn}/control
     */
    public static String esp32ControlTopic(String sn) {
        return "monitor/esp32/" + sn + "/control";
    }

    /**
     * 拼接发给某台香橙派的控制主题
     *
     * @param sn 目标香橙派的序列号
     * @return monitor/orangepi/{sn}/control
     */
    public static String orangePiControlTopic(String sn) {
        return "monitor/orangepi/" + sn + "/control";
    }

    /**
     * 从主题字符串里取出设备 SN（主题第三段，下标从 0 数是第 2 段）
     * 例如 monitor/esp32/esp32-s3-001/sensor → esp32-s3-001
     *
     * @param topic 收到消息的完整主题
     * @return 解析出的设备 SN
     */
    public static String parseSn(String topic) {
        String[] parts = topic.split("/");
        return parts[2];
    }
}
