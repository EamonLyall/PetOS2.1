package com.petos.monitor.controller;

import com.petos.monitor.exception.BusinessException;
import com.petos.monitor.service.CommandService;
import com.petos.monitor.util.Result;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/**
 * 指令控制接口。
 * 基础地址：/api/commands
 * 前端手动操作云台、补光灯、蜂鸣器，都通过这里下发，后端再转 MQTT 给 ESP32。
 */
@RestController
@RequestMapping("/api/commands")
public class CommandController {

    private final CommandService commandService;

    public CommandController(CommandService commandService) {
        this.commandService = commandService;
    }

    /**
     * 控制补光灯
     * 请求方式：POST
     * 请求地址：/api/commands/light
     * 入参 JSON：{ "sn":"esp32-s3-001", "on":true }
     * 返回示例：{ "code":0, "message":"成功", "data":null }
     */
    @PostMapping("/light")
    public Result<Void> light(@RequestBody Map<String, Object> body) {
        String sn = getSn(body);
        boolean on = getBoolean(body, "on");
        commandService.controlLight(sn, on);
        return Result.success();
    }

    /**
     * 控制蜂鸣器
     * 请求方式：POST
     * 请求地址：/api/commands/buzzer
     * 入参 JSON：{ "sn":"esp32-s3-001", "on":true }
     */
    @PostMapping("/buzzer")
    public Result<Void> buzzer(@RequestBody Map<String, Object> body) {
        String sn = getSn(body);
        boolean on = getBoolean(body, "on");
        commandService.controlBuzzer(sn, on);
        return Result.success();
    }

    /**
     * 控制云台转动
     * 请求方式：POST
     * 请求地址：/api/commands/gimbal
     * 入参 JSON：{ "sn":"esp32-s3-001", "pan":90, "tilt":45 }
     */
    @PostMapping("/gimbal")
    public Result<Void> gimbal(@RequestBody Map<String, Object> body) {
        String sn = getSn(body);
        // 角度在 JSON 里是数字，统一转成 Integer
        Integer pan = Integer.valueOf(String.valueOf(body.get("pan")));
        Integer tilt = Integer.valueOf(String.valueOf(body.get("tilt")));
        commandService.controlGimbal(sn, pan, tilt);
        return Result.success();
    }

    /**
     * 从请求体里取 SN 并做非空校验，三个接口复用
     */
    private String getSn(Map<String, Object> body) {
        Object sn = body.get("sn");
        if (sn == null || String.valueOf(sn).isBlank()) {
            throw new BusinessException("设备 sn 不能为空");
        }
        return String.valueOf(sn);
    }

    /**
     * 从请求体里取布尔值，兼容 true/false 两种写法
     */
    private boolean getBoolean(Map<String, Object> body, String key) {
        Object value = body.get(key);
        if (value == null) {
            throw new BusinessException(key + " 不能为空");
        }
        return Boolean.parseBoolean(String.valueOf(value));
    }
}
