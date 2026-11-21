package com.petos.monitor.service;

import com.petos.monitor.entity.SensorData;
import com.petos.monitor.repository.SensorDataRepository;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

/**
 * 传感器数据业务服务：负责把 MQTT 上报的传感器数据存库、给前端提供查询。
 */
@Service
public class SensorDataService {

    private final SensorDataRepository sensorDataRepository;

    // 构造注入
    public SensorDataService(SensorDataRepository sensorDataRepository) {
        this.sensorDataRepository = sensorDataRepository;
    }

    /**
     * 保存一条传感器数据
     *
     * @param deviceSn      设备 SN
     * @param temperature   温度
     * @param humidity      湿度
     * @param pirTriggered  PIR 是否检测到人
     * @param doorClosed    门是否关闭
     */
    public void save(String deviceSn,
                     BigDecimal temperature,
                     BigDecimal humidity,
                     Boolean pirTriggered,
                     Boolean doorClosed) {
        SensorData sensorData = new SensorData();
        sensorData.setDeviceSn(deviceSn);
        sensorData.setTemperature(temperature);
        sensorData.setHumidity(humidity);
        sensorData.setPirTriggered(pirTriggered);
        sensorData.setDoorClosed(doorClosed);
        sensorData.setReportTime(LocalDateTime.now());
        sensorDataRepository.save(sensorData);
    }

    /**
     * 查询某设备最近 20 条数据（前端图表用）
     */
    public List<SensorData> listRecent(String deviceSn) {
        return sensorDataRepository.findTop20ByDeviceSnOrderByReportTimeDesc(deviceSn);
    }

    /**
     * 查询某设备全部历史数据
     */
    public List<SensorData> listAll(String deviceSn) {
        return sensorDataRepository.findByDeviceSnOrderByReportTimeDesc(deviceSn);
    }
}
