package com.petos.monitor.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.PrePersist;
import jakarta.persistence.Table;

import java.time.LocalDateTime;

/**
 * 设备实体类：对应数据库里的一张设备表（device）。
 * 一台 ESP32-S3 或一台香橙派摄像头，在表里各占一行。
 *
 * @Entity 告诉 JPA：这是一个需要映射到数据库表的实体
 * @Table 指定这张表的名字叫 device
 */
@Entity
@Table(name = "device")
public class Device {

    /**
     * 主键 ID：每条设备记录的唯一编号
     * @Id 表示这是主键
     * @GeneratedValue 让数据库自动生成自增 ID，不用我们手动赋值
     */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * 设备名称：给人看的名字，比如“客厅 ESP32-S3”
     */
    @Column(name = "device_name")
    private String deviceName;

    /**
     * 设备类型：区分两类硬件
     * 固定取值：ESP32_S3（单片机）、ORANGE_PI（香橙派摄像头）
     */
    @Column(name = "device_type")
    private String deviceType;

    /**
     * 设备序列号 SN：硬件的唯一标识，ESP32 烧录时固定，告警和图片都靠它关联设备
     * unique = true 表示这一列不允许重复
     */
    @Column(name = "sn", unique = true)
    private String sn;

    /**
     * 在线状态：true 在线，false 离线，由心跳定时任务更新
     */
    @Column(name = "online")
    private Boolean online;

    /**
     * 最近一次心跳时间：用来判断设备是否掉线
     */
    @Column(name = "last_heartbeat")
    private LocalDateTime lastHeartbeat;

    /**
     * 安装位置：比如“客厅”“门口”，方便前端展示
     */
    @Column(name = "location")
    private String location;

    /**
     * 记录创建时间：这台设备第一次入库的时间
     */
    @Column(name = "create_time")
    private LocalDateTime createTime;

    /**
     * @PrePersist：在这条数据第一次被“插入”数据库之前自动执行
     * 作用：自动补上创建时间，不用每个 service 手动 set
     */
    @PrePersist
    public void prePersist() {
        if (this.createTime == null) {
            this.createTime = LocalDateTime.now();
        }
    }

    // 下面是所有字段的 getter / setter，手写出来方便零基础对照理解
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getDeviceName() {
        return deviceName;
    }

    public void setDeviceName(String deviceName) {
        this.deviceName = deviceName;
    }

    public String getDeviceType() {
        return deviceType;
    }

    public void setDeviceType(String deviceType) {
        this.deviceType = deviceType;
    }

    public String getSn() {
        return sn;
    }

    public void setSn(String sn) {
        this.sn = sn;
    }

    public Boolean getOnline() {
        return online;
    }

    public void setOnline(Boolean online) {
        this.online = online;
    }

    public LocalDateTime getLastHeartbeat() {
        return lastHeartbeat;
    }

    public void setLastHeartbeat(LocalDateTime lastHeartbeat) {
        this.lastHeartbeat = lastHeartbeat;
    }

    public String getLocation() {
        return location;
    }

    public void setLocation(String location) {
        this.location = location;
    }

    public LocalDateTime getCreateTime() {
        return createTime;
    }

    public void setCreateTime(LocalDateTime createTime) {
        this.createTime = createTime;
    }
}
