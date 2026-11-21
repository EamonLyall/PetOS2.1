package com.petos.monitor.service;

import com.petos.monitor.entity.Device;
import com.petos.monitor.repository.DeviceRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * 设备业务服务：负责设备查询、心跳更新、在线/离线判断。
 * Controller 不直接操作 Repository，而是通过本服务，业务逻辑集中在这里。
 */
@Service
public class DeviceService {

    private static final Logger log = LoggerFactory.getLogger(DeviceService.class);

    // 设备持久层
    private final DeviceRepository deviceRepository;

    // 心跳超时秒数：超过这么久没收到心跳就判定离线，来自 yml 配置
    @Value("${app.heartbeat.timeout-seconds}")
    private Long heartbeatTimeoutSeconds;

    // 构造注入
    public DeviceService(DeviceRepository deviceRepository) {
        this.deviceRepository = deviceRepository;
    }

    /**
     * 查询所有设备
     */
    public List<Device> listAll() {
        return deviceRepository.findAll();
    }

    /**
     * 按设备类型查询
     *
     * @param deviceType ESP32_S3 或 ORANGE_PI
     */
    public List<Device> listByType(String deviceType) {
        return deviceRepository.findByDeviceType(deviceType);
    }

    /**
     * 根据 SN 查设备
     */
    public Optional<Device> getBySn(String sn) {
        return deviceRepository.findBySn(sn);
    }

    /**
     * 收到设备心跳时调用：刷新最近心跳时间并标记在线
     *
     * @param sn 上报心跳的设备 SN
     */
    public void receiveHeartbeat(String sn) {
        Optional<Device> deviceOptional = deviceRepository.findBySn(sn);
        if (deviceOptional.isEmpty()) {
            // 设备没在库里（多半是 SN 写错），只记录日志，不自动创建脏数据
            log.warn("【心跳】收到未知设备 SN={} 的心跳，已忽略，请检查设备 SN 配置", sn);
            return;
        }
        Device device = deviceOptional.get();
        device.setLastHeartbeat(LocalDateTime.now());
        device.setOnline(true);
        deviceRepository.save(device);
    }

    /**
     * 定时任务：每 15 秒扫描一次，把超时没心跳的设备标记为离线
     */
    @Scheduled(fixedDelay = 15000)
    public void checkOffline() {
        // 离线判定的时间界限：早于这个时间还没心跳，就算掉线
        LocalDateTime deadline = LocalDateTime.now().minusSeconds(heartbeatTimeoutSeconds);
        // 只检查当前认为在线的设备即可
        List<Device> onlineDevices = deviceRepository.findByOnline(true);
        for (Device device : onlineDevices) {
            // 从没上报过心跳，或最近心跳早于界限，都判定离线
            if (device.getLastHeartbeat() == null || device.getLastHeartbeat().isBefore(deadline)) {
                device.setOnline(false);
                deviceRepository.save(device);
                log.info("【心跳】设备 {} 超过 {} 秒无心跳，判定离线",
                        device.getSn(), heartbeatTimeoutSeconds);
            }
        }
    }
}
