package com.petos.monitor;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * 整个后端工程的“启动入口”。
 * 答辩讲解：运行这个 main 方法，就会启动内嵌 Tomcat、自动连数据库、自动连 MQTT，整个后端就跑起来了。
 *
 * @SpringBootApplication：是一个组合注解，等于同时开启了“自动配置 + 组件扫描 + 配置类”。
 *   它会自动扫描本类所在包（com.petos.monitor）下面的所有 controller、service、component 并交给 Spring 管理。
 * @EnableScheduling：开启“定时任务”功能，我们用它每隔一段时间检查设备心跳、判断在线/离线。
 */
@SpringBootApplication
@EnableScheduling
public class PetosMonitorApplication {

    /**
     * main 方法：Java 程序的固定入口，程序从这里开始执行。
     *
     * @param args 启动时可以传入的命令行参数，本项目没用到，照写即可
     */
    public static void main(String[] args) {
        // SpringApplication.run 负责真正启动 SpringBoot：初始化容器、建表、连 MQTT、启动 Tomcat
        SpringApplication.run(PetosMonitorApplication.class, args);
        // 控制台打印一行中文提示，方便确认启动成功
        System.out.println("====== PetOS 人形监控后端启动成功，接口地址 http://localhost:8080 ======");
    }
}
