package com.petos.monitor.controller;

import com.petos.monitor.entity.Device;
import com.petos.monitor.exception.BusinessException;
import com.petos.monitor.service.DeviceService;
import com.petos.monitor.util.Result;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * 设备管理接口。
 * 基础地址：/api/devices
 * 只负责“接收请求、返回结果”，具体逻辑交给 DeviceService。
 */
@RestController
@RequestMapping("/api/devices")
public class DeviceController {

    private final DeviceService deviceService;

    // 构造注入设备服务
    public DeviceController(DeviceService deviceService) {
        this.deviceService = deviceService;
    }

    /**
     * 查询全部设备
     * 请求方式：GET
     * 请求地址：/api/devices
     * 入参：无
     * 返回示例：
     * {
     *   "code": 0,
     *   "message": "成功",
     *   "data": [ { "id":1, "deviceName":"客厅ESP32", "deviceType":"ESP32_S3",
     *               "sn":"esp32-s3-001", "online":true, "location":"客厅" } ]
     * }
     */
    @GetMapping
    public Result<List<Device>> list() {
        return Result.success(deviceService.listAll());
    }

    /**
     * 按设备类型查询
     * 请求方式：GET
     * 请求地址：/api/devices/type/{deviceType}
     * 入参示例：路径上 deviceType 填 ESP32_S3 或 ORANGE_PI
     */
    @GetMapping("/type/{deviceType}")
    public Result<List<Device>> listByType(@PathVariable String deviceType) {
        return Result.success(deviceService.listByType(deviceType));
    }

    /**
     * 根据 SN 查询单台设备
     * 请求方式：GET
     * 请求地址：/api/devices/{sn}
     */
    @GetMapping("/{sn}")
    public Result<Device> getBySn(@PathVariable String sn) {
        Device device = deviceService.getBySn(sn)
                .orElseThrow(() -> new BusinessException("设备不存在，sn=" + sn));
        return Result.success(device);
    }
}
