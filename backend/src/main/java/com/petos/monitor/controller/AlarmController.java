package com.petos.monitor.controller;

import com.petos.monitor.entity.AlarmRecord;
import com.petos.monitor.service.AlarmService;
import com.petos.monitor.util.Result;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.math.BigDecimal;
import java.util.List;

/**
 * 告警抓拍接口。
 * 基础地址：/api/alarms
 * 包含历史查询、图片上传、标记已处理。
 */
@RestController
@RequestMapping("/api/alarms")
public class AlarmController {

    private final AlarmService alarmService;

    public AlarmController(AlarmService alarmService) {
        this.alarmService = alarmService;
    }

    /**
     * 查询全部告警（按时间倒序）
     * 请求方式：GET
     * 请求地址：/api/alarms
     */
    @GetMapping
    public Result<List<AlarmRecord>> list() {
        return Result.success(alarmService.listAll());
    }

    /**
     * 查询最近 10 条告警（首页用）
     * 请求方式：GET
     * 请求地址：/api/alarms/recent
     */
    @GetMapping("/recent")
    public Result<List<AlarmRecord>> recent() {
        return Result.success(alarmService.listRecent());
    }

    /**
     * 查询某设备的告警
     * 请求方式：GET
     * 请求地址：/api/alarms/device/{sn}
     */
    @GetMapping("/device/{sn}")
    public Result<List<AlarmRecord>> byDevice(@PathVariable String sn) {
        return Result.success(alarmService.listByDevice(sn));
    }

    /**
     * 上传抓拍图片并生成告警记录（香橙派调用）
     * 请求方式：POST
     * 请求地址：/api/alarms/upload
     * 提交方式：multipart/form-data
     * 入参字段：
     *   file       图片文件，只允许 jpg/png（必填）
     *   deviceSn   触发告警的 ESP32 SN（必填）
     *   cameraSn   香橙派摄像头 SN（必填）
     *   confidence YOLO 置信度，0~1（可选）
     * 返回示例：
     * { "code":0, "message":"成功",
     *   "data":{ "id":1, "deviceSn":"esp32-s3-001", "cameraSn":"orangepi-cam-001",
     *            "alarmType":"PERSON_DETECT", "imageUrl":"/images/alarm_xxx.jpg",
     *            "handled":false } }
     */
    @PostMapping("/upload")
    public Result<AlarmRecord> upload(@RequestParam("file") MultipartFile file,
                                      @RequestParam("deviceSn") String deviceSn,
                                      @RequestParam("cameraSn") String cameraSn,
                                      @RequestParam(value = "confidence", required = false)
                                      BigDecimal confidence) {
        return Result.success(alarmService.saveCapture(file, deviceSn, cameraSn, confidence));
    }

    /**
     * 把某条告警标记为已处理
     * 请求方式：PUT
     * 请求地址：/api/alarms/{id}/handle
     */
    @PutMapping("/{id}/handle")
    public Result<AlarmRecord> handle(@PathVariable Long id) {
        return Result.success(alarmService.markHandled(id));
    }
}
