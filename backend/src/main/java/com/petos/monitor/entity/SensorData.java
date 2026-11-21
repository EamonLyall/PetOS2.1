package com.petos.monitor.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 传感器数据实体类：对应数据库表 sensor_data。
 * ESP32-S3 每次上报温湿度、PIR、门磁状态，就存成一行，前端用它画图表。
 */
@Entity
@Table(name = "sensor_data")
public class SensorData {

    /** 主键 ID，数据库自增 */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * 上报这组数据的设备 SN（外键作用，和 device.sn 对应）
     * 不直接用设备主键，是因为硬件报文里天然带 SN，对接更直接
     */
    @Column(name = "device_sn")
    private String deviceSn;

    /**
     * 温度，单位摄氏度
     * 用 BigDecimal 而不用 double，是为了精确表示小数，避免浮点误差
     */
    @Column(name = "temperature")
    private BigDecimal temperature;

    /**
     * 湿度，单位百分比
     */
    @Column(name = "humidity")
    private BigDecimal humidity;

    /**
     * PIR 人体红外状态：true 表示此刻检测到人，false 表示无人
     */
    @Column(name = "pir_triggered")
    private Boolean pirTriggered;

    /**
     * 门磁状态：true 表示门关闭，false 表示门被打开
     */
    @Column(name = "door_closed")
    private Boolean doorClosed;

    /**
     * 上报时间：设备产生这组数据的时间，前端按时间排序展示
     */
    @Column(name = "report_time")
    private LocalDateTime reportTime;

    // 无参构造：JPA 反射创建对象时需要
    public SensorData() {
    }

    // getter / setter
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getDeviceSn() {
        return deviceSn;
    }

    public void setDeviceSn(String deviceSn) {
        this.deviceSn = deviceSn;
    }

    public BigDecimal getTemperature() {
        return temperature;
    }

    public void setTemperature(BigDecimal temperature) {
        this.temperature = temperature;
    }

    public BigDecimal getHumidity() {
        return humidity;
    }

    public void setHumidity(BigDecimal humidity) {
        this.humidity = humidity;
    }

    public Boolean getPirTriggered() {
        return pirTriggered;
    }

    public void setPirTriggered(Boolean pirTriggered) {
        this.pirTriggered = pirTriggered;
    }

    public Boolean getDoorClosed() {
        return doorClosed;
    }

    public void setDoorClosed(Boolean doorClosed) {
        this.doorClosed = doorClosed;
    }

    public LocalDateTime getReportTime() {
        return reportTime;
    }

    public void setReportTime(LocalDateTime reportTime) {
        this.reportTime = reportTime;
    }
}
