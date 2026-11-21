package com.petos.monitor.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.PrePersist;
import jakarta.persistence.Table;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 告警抓拍记录实体类：对应数据库表 alarm_record。
 * 香橙派 YOLO 确认是人体并上传图片后，后端生成一条这样的记录。
 */
@Entity
@Table(name = "alarm_record")
public class AlarmRecord {

    /** 主键 ID，数据库自增 */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * 触发告警的 ESP32-S3 设备 SN
     * 告警和图片都关联设备 SN，方便按设备筛选、定位是哪台设备报的警
     */
    @Column(name = "device_sn")
    private String deviceSn;

    /**
     * 负责拍照识别的香橙派摄像头 SN
     */
    @Column(name = "camera_sn")
    private String cameraSn;

    /**
     * 告警类型：固定写 PERSON_DETECT（检测到人体），后续可扩展烟雾、门磁等类型
     */
    @Column(name = "alarm_type")
    private String alarmType;

    /**
     * YOLO 识别置信度：0~1 的小数，越接近 1 表示越确定是人，答辩时可展示模型可信度
     */
    @Column(name = "confidence")
    private BigDecimal confidence;

    /**
     * 图片在服务器上的存储路径（相对路径），用于内部定位文件
     */
    @Column(name = "image_path", length = 500)
    private String imagePath;

    /**
     * 图片访问 URL：前端 img 标签直接用这个地址显示图片
     */
    @Column(name = "image_url", length = 500)
    private String imageUrl;

    /**
     * 是否已处理：false 未处理，true 已处理，前端可做“确认告警”功能
     */
    @Column(name = "handled")
    private Boolean handled;

    /**
     * 告警描述文字：给前端展示的一句话说明
     */
    @Column(name = "description")
    private String description;

    /**
     * 告警发生时间：设备实际触发的时间
     */
    @Column(name = "alarm_time")
    private LocalDateTime alarmTime;

    /**
     * 记录入库时间：后端收到并保存的时间
     */
    @Column(name = "create_time")
    private LocalDateTime createTime;

    /**
     * 插入数据库前自动补齐：创建时间、默认未处理状态
     */
    @PrePersist
    public void prePersist() {
        if (this.createTime == null) {
            this.createTime = LocalDateTime.now();
        }
        if (this.handled == null) {
            this.handled = false;
        }
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

    public String getCameraSn() {
        return cameraSn;
    }

    public void setCameraSn(String cameraSn) {
        this.cameraSn = cameraSn;
    }

    public String getAlarmType() {
        return alarmType;
    }

    public void setAlarmType(String alarmType) {
        this.alarmType = alarmType;
    }

    public BigDecimal getConfidence() {
        return confidence;
    }

    public void setConfidence(BigDecimal confidence) {
        this.confidence = confidence;
    }

    public String getImagePath() {
        return imagePath;
    }

    public void setImagePath(String imagePath) {
        this.imagePath = imagePath;
    }

    public String getImageUrl() {
        return imageUrl;
    }

    public void setImageUrl(String imageUrl) {
        this.imageUrl = imageUrl;
    }

    public Boolean getHandled() {
        return handled;
    }

    public void setHandled(Boolean handled) {
        this.handled = handled;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public LocalDateTime getAlarmTime() {
        return alarmTime;
    }

    public void setAlarmTime(LocalDateTime alarmTime) {
        this.alarmTime = alarmTime;
    }

    public LocalDateTime getCreateTime() {
        return createTime;
    }

    public void setCreateTime(LocalDateTime createTime) {
        this.createTime = createTime;
    }
}
