package com.petos.monitor.mqtt;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.petos.monitor.service.DeviceService;
import com.petos.monitor.service.SensorDataService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;

/**
 * MQTT 消息业务服务。
 * 作用：收到原始字符串消息后，判断它属于哪一类主题，解析 JSON 字段，
 * 再调用对应的业务服务处理，让“通信”和“业务”分开。
 */
@Service
public class MqttMessageService {

    private static final Logger log = LoggerFactory.getLogger(MqttMessageService.class);

    // JSON 解析器
    private final ObjectMapper objectMapper;
    // 设备服务（心跳/在线状态）
    private final DeviceService deviceService;
    // 传感器服务（存温湿度等）
    private final SensorDataService sensorDataService;

    public MqttMessageService(ObjectMapper objectMapper,
                              DeviceService deviceService,
                              SensorDataService sensorDataService) {
        this.objectMapper = objectMapper;
        this.deviceService = deviceService;
        this.sensorDataService = sensorDataService;
    }

    /**
     * 处理一条收到的 MQTT 消息
     *
     * @param topic   主题
     * @param payload 消息字符串（JSON）
     */
    public void handleMessage(String topic, String payload) {
        // 从主题里解析出设备 SN
        String sn = MqttTopicConstants.parseSn(topic);
        try {
            // 按主题结尾的“用途段”区分消息类型
            if (topic.endsWith("/status")) {
                // 心跳消息：刷新在线状态
                deviceService.receiveHeartbeat(sn);
            } else if (topic.endsWith("/sensor")) {
                // 传感器数据：解析并保存，同时刷新心跳
                handleSensor(sn, payload);
                deviceService.receiveHeartbeat(sn);
            } else if (topic.endsWith("/alarm")) {
                // PIR 原始告警：最小版本只记录日志并刷新心跳，
                // 真正的人体确认和图片由香橙派完成后走 HTTP 上传
                log.info("【业务】收到 ESP32 {} 的 PIR 原始告警，等待香橙派 YOLO 复核", sn);
                deviceService.receiveHeartbeat(sn);
            } else if (topic.endsWith("/detect")) {
                // 香橙派识别结果：刷新摄像头心跳
                log.info("【业务】收到香橙派 {} 的识别结果：{}", sn, payload);
                deviceService.receiveHeartbeat(sn);
            } else {
                log.warn("【业务】收到未识别主题的消息：{}", topic);
            }
        } catch (Exception e) {
            // 单条消息解析失败不影响后续消息，记录日志即可
            log.error("【业务】处理消息失败 主题={} 原因={}", topic, e.getMessage());
        }
    }

    /**
     * 解析并保存传感器数据
     */
    private void handleSensor(String sn, String payload) throws Exception {
        JsonNode node = objectMapper.readTree(payload);

        // 温度：字段存在才读取，否则给 null
        BigDecimal temperature = node.has("temperature")
                ? BigDecimal.valueOf(node.path("temperature").asDouble()) : null;
        // 湿度
        BigDecimal humidity = node.has("humidity")
                ? BigDecimal.valueOf(node.path("humidity").asDouble()) : null;
        // PIR 状态
        Boolean pirTriggered = node.has("pir") ? node.path("pir").asBoolean() : null;
        // 门磁状态
        Boolean doorClosed = node.has("doorClosed") ? node.path("doorClosed").asBoolean() : null;

        sensorDataService.save(sn, temperature, humidity, pirTriggered, doorClosed);
    }
}
