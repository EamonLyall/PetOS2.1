package com.petos.monitor.controller;

import com.petos.monitor.entity.SensorData;
import com.petos.monitor.service.SensorDataService;
import com.petos.monitor.util.Result;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * 传感器数据接口。
 * 基础地址：/api/sensors
 * 前端用这些数据画温湿度曲线、展示 PIR 和门磁状态。
 */
@RestController
@RequestMapping("/api/sensors")
public class SensorDataController {

    private final SensorDataService sensorDataService;

    public SensorDataController(SensorDataService sensorDataService) {
        this.sensorDataService = sensorDataService;
    }

    /**
     * 查询某设备最近 20 条传感器数据（图表用）
     * 请求方式：GET
     * 请求地址：/api/sensors/{sn}/recent
     * 入参：路径 sn 为设备序列号
     * 返回示例：
     * { "code":0, "message":"成功",
     *   "data":[ { "id":1, "deviceSn":"esp32-s3-001", "temperature":26.5,
     *              "humidity":55.0, "pirTriggered":true, "doorClosed":true } ] }
     */
    @GetMapping("/{sn}/recent")
    public Result<List<SensorData>> recent(@PathVariable String sn) {
        return Result.success(sensorDataService.listRecent(sn));
    }

    /**
     * 查询某设备全部历史传感器数据
     * 请求方式：GET
     * 请求地址：/api/sensors/{sn}
     */
    @GetMapping("/{sn}")
    public Result<List<SensorData>> all(@PathVariable String sn) {
        return Result.success(sensorDataService.listAll(sn));
    }
}
