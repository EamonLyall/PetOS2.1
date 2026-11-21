package com.petos.monitor.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.petos.monitor.exception.BusinessException;
import com.petos.monitor.mqtt.MqttClientManager;
import com.petos.monitor.mqtt.MqttTopicConstants;
import org.springframework.stereotype.Service;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * 指令控制业务服务。
 * 前端手动控制（云台、补光灯、蜂鸣器）先到这里，本服务把指令拼成 JSON，
 * 再通过 MQTT 发布给对应 ESP32-S3。
 */
@Service
public class CommandService {

    // 用来把 Map 转成 JSON 字符串
    private final ObjectMapper objectMapper;
    // MQTT 发布器
    private final MqttClientManager mqttClientManager;

    public CommandService(ObjectMapper objectMapper, MqttClientManager mqttClientManager) {
        this.objectMapper = objectMapper;
        this.mqttClientManager = mqttClientManager;
    }

    /**
     * 通用下发方法：所有具体指令最终都走这里
     *
     * @param sn      目标 ESP32 的 SN
     * @param command 指令名称（LIGHT / BUZZER / GIMBAL）
     * @param params  指令参数（开关状态或角度）
     */
    public void sendCommand(String sn, String command, Map<String, Object> params) {
        // 用 LinkedHashMap 保证字段顺序固定，方便答辩时展示报文
        Map<String, Object> payloadMap = new LinkedHashMap<>();
        payloadMap.put("sn", sn);
        payloadMap.put("command", command);
        payloadMap.put("params", params);
        String json;
        try {
            json = objectMapper.writeValueAsString(payloadMap);
        } catch (JsonProcessingException e) {
            throw new BusinessException("指令 JSON 组装失败：" + e.getMessage());
        }
        // 发布到该设备的控制主题
        mqttClientManager.publish(MqttTopicConstants.esp32ControlTopic(sn), json);
    }

    /**
     * 控制补光灯开关
     *
     * @param sn 设备 SN
     * @param on true 开灯，false 关灯
     */
    public void controlLight(String sn, boolean on) {
        Map<String, Object> params = new LinkedHashMap<>();
        params.put("on", on);
        sendCommand(sn, "LIGHT", params);
    }

    /**
     * 控制蜂鸣器开关（测试蜂鸣器用）
     */
    public void controlBuzzer(String sn, boolean on) {
        Map<String, Object> params = new LinkedHashMap<>();
        params.put("on", on);
        sendCommand(sn, "BUZZER", params);
    }

    /**
     * 控制云台舵机转动
     *
     * @param sn  设备 SN
     * @param pan 水平角度（0~180）
     * @param tilt 垂直角度（0~180）
     */
    public void controlGimbal(String sn, Integer pan, Integer tilt) {
        if (pan == null || tilt == null) {
            throw new BusinessException("云台角度不能为空");
        }
        Map<String, Object> params = new LinkedHashMap<>();
        params.put("pan", pan);
        params.put("tilt", tilt);
        sendCommand(sn, "GIMBAL", params);
    }
}
