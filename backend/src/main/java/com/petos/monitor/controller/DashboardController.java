package com.petos.monitor.controller;

import com.petos.monitor.service.DashboardService;
import com.petos.monitor.util.Result;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/**
 * 仪表盘统计接口。
 * 基础地址：/api/dashboard
 */
@RestController
@RequestMapping("/api/dashboard")
public class DashboardController {

    private final DashboardService dashboardService;

    public DashboardController(DashboardService dashboardService) {
        this.dashboardService = dashboardService;
    }

    /**
     * 获取大屏汇总统计
     * 请求方式：GET
     * 请求地址：/api/dashboard/stats
     * 入参：无
     * 返回示例：
     * { "code":0, "message":"成功",
     *   "data":{ "deviceTotal":2, "onlineTotal":2, "offlineTotal":0,
     *            "esp32Total":1, "orangePiTotal":1,
     *            "alarmTotal":2, "unhandledAlarmTotal":1,
     *            "latestTemperature":26.00, "latestHumidity":55.00 } }
     */
    @GetMapping("/stats")
    public Result<Map<String, Object>> stats() {
        return Result.success(dashboardService.getStats());
    }
}
