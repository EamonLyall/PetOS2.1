package com.petos.monitor.service;

import com.petos.monitor.entity.AlarmRecord;
import com.petos.monitor.entity.Device;
import com.petos.monitor.entity.SensorData;
import com.petos.monitor.repository.AlarmRecordRepository;
import com.petos.monitor.repository.DeviceRepository;
import com.petos.monitor.repository.SensorDataRepository;
import org.springframework.stereotype.Service;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * 仪表盘统计业务服务。
 * 作用：给监控大屏一次性汇总“设备数量、在线情况、告警数量、最新温湿度”等关键指标，
 * 前端不用发很多个请求，拿一个接口就能渲染顶部统计卡片。
 */
@Service
public class DashboardService {

    // 设备、告警、传感器三个持久层
    private final DeviceRepository deviceRepository;
    private final AlarmRecordRepository alarmRecordRepository;
    private final SensorDataRepository sensorDataRepository;

    // 构造注入
    public DashboardService(DeviceRepository deviceRepository,
                            AlarmRecordRepository alarmRecordRepository,
                            SensorDataRepository sensorDataRepository) {
        this.deviceRepository = deviceRepository;
        this.alarmRecordRepository = alarmRecordRepository;
        this.sensorDataRepository = sensorDataRepository;
    }

    /**
     * 汇总大屏统计数据
     *
     * @return 字段名见名知意的统计 Map
     */
    public Map<String, Object> getStats() {
        // 用 LinkedHashMap 保证字段顺序，方便调试和讲解
        Map<String, Object> stats = new LinkedHashMap<>();

        // 1. 统计设备相关指标
        List<Device> devices = deviceRepository.findAll();
        int onlineCount = 0;          // 在线设备数
        int offlineCount = 0;         // 离线设备数
        int esp32Count = 0;           // ESP32 数量
        int orangePiCount = 0;        // 香橙派数量
        for (Device device : devices) {
            // 按在线状态计数
            if (Boolean.TRUE.equals(device.getOnline())) {
                onlineCount++;
            } else {
                offlineCount++;
            }
            // 按设备类型计数
            if ("ESP32_S3".equals(device.getDeviceType())) {
                esp32Count++;
            } else if ("ORANGE_PI".equals(device.getDeviceType())) {
                orangePiCount++;
            }
        }
        stats.put("deviceTotal", devices.size());
        stats.put("onlineTotal", onlineCount);
        stats.put("offlineTotal", offlineCount);
        stats.put("esp32Total", esp32Count);
        stats.put("orangePiTotal", orangePiCount);

        // 2. 统计告警相关指标
        List<AlarmRecord> alarms = alarmRecordRepository.findAll();
        int unhandledCount = 0; // 未处理告警数
        for (AlarmRecord alarm : alarms) {
            if (!Boolean.TRUE.equals(alarm.getHandled())) {
                unhandledCount++;
            }
        }
        stats.put("alarmTotal", alarms.size());
        stats.put("unhandledAlarmTotal", unhandledCount);

        // 3. 取 ESP32 最新一条传感器数据，展示最新温湿度
        List<SensorData> latestList =
                sensorDataRepository.findTop20ByDeviceSnOrderByReportTimeDesc("esp32-s3-001");
        if (!latestList.isEmpty()) {
            SensorData latest = latestList.get(0); // 列表按时间倒序，第一条就是最新
            stats.put("latestTemperature", latest.getTemperature());
            stats.put("latestHumidity", latest.getHumidity());
            stats.put("latestPirTriggered", latest.getPirTriggered());
            stats.put("latestDoorClosed", latest.getDoorClosed());
        }
        return stats;
    }
}
