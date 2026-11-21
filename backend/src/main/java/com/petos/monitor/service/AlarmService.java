package com.petos.monitor.service;

import com.petos.monitor.entity.AlarmRecord;
import com.petos.monitor.exception.BusinessException;
import com.petos.monitor.repository.AlarmRecordRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Locale;

/**
 * 告警抓拍业务服务：接收香橙派上传的图片、校验、存到本地、生成告警记录。
 */
@Service
public class AlarmService {

    private static final Logger log = LoggerFactory.getLogger(AlarmService.class);

    private final AlarmRecordRepository alarmRecordRepository;

    // 图片保存目录
    @Value("${app.upload.path}")
    private String uploadPath;

    // 图片网址前缀
    @Value("${app.upload.url-prefix}")
    private String urlPrefix;

    public AlarmService(AlarmRecordRepository alarmRecordRepository) {
        this.alarmRecordRepository = alarmRecordRepository;
    }

    /**
     * 保存抓拍图片并生成告警记录
     *
     * @param file       前端/香橙派上传的图片文件
     * @param deviceSn   触发告警的 ESP32 SN
     * @param cameraSn   拍照的香橙派 SN
     * @param confidence YOLO 置信度（可为空）
     * @return 保存后的告警记录（含可访问的图片 URL）
     */
    public AlarmRecord saveCapture(MultipartFile file,
                                   String deviceSn,
                                   String cameraSn,
                                   BigDecimal confidence) {
        // 1. 基础非空校验
        if (file == null || file.isEmpty()) {
            throw new BusinessException("图片文件不能为空");
        }

        // 2. 取原始文件名并转小写，用于判断扩展名
        String originalFilename = file.getOriginalFilename();
        if (originalFilename == null) {
            throw new BusinessException("文件名不合法");
        }
        String lowerName = originalFilename.toLowerCase(Locale.ROOT);
        // 只允许 jpg、jpeg、png 三种后缀
        if (!lowerName.endsWith(".jpg") && !lowerName.endsWith(".jpeg")
                && !lowerName.endsWith(".png")) {
            throw new BusinessException("只允许上传 jpg/png 格式的图片");
        }

        // 3. 确定保存目录，不存在就创建
        File directory = new File(uploadPath);
        if (!directory.exists() && !directory.mkdirs()) {
            throw new BusinessException("创建图片存储目录失败：" + directory.getAbsolutePath());
        }

        // 4. 生成一个不会重复的新文件名：时间戳 + 随机数 + 原扩展名
        String suffix = lowerName.endsWith(".png") ? ".png" : ".jpg";
        String timePart = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMddHHmmss"));
        String newFileName = "alarm_" + timePart + "_" + (int) (Math.random() * 10000) + suffix;

        // 5. 把文件写到磁盘
        File targetFile = new File(directory, newFileName);
        try {
            file.transferTo(targetFile);
        } catch (IOException e) {
            log.error("图片保存失败", e);
            throw new BusinessException("图片保存失败：" + e.getMessage());
        }

        // 6. 组装告警记录
        AlarmRecord record = new AlarmRecord();
        record.setDeviceSn(deviceSn);
        record.setCameraSn(cameraSn);
        record.setAlarmType("PERSON_DETECT");
        record.setConfidence(confidence);
        record.setImagePath(new File(uploadPath, newFileName).getPath());
        // 图片 URL 用相对路径，前端通过 8080 端口 + 前缀访问
        record.setImageUrl(urlPrefix + "/" + newFileName);
        record.setAlarmTime(LocalDateTime.now());
        record.setDescription("检测到人体，已自动抓拍并联动声光报警");
        record.setHandled(false);

        return alarmRecordRepository.save(record);
    }

    /**
     * 查询全部告警，按时间倒序
     */
    public List<AlarmRecord> listAll() {
        return alarmRecordRepository.findAllByOrderByAlarmTimeDesc();
    }

    /**
     * 查询最近 10 条告警
     */
    public List<AlarmRecord> listRecent() {
        return alarmRecordRepository.findTop10ByOrderByAlarmTimeDesc();
    }

    /**
     * 查询某设备的告警
     */
    public List<AlarmRecord> listByDevice(String deviceSn) {
        return alarmRecordRepository.findByDeviceSnOrderByAlarmTimeDesc(deviceSn);
    }

    /**
     * 把某条告警标记为已处理
     */
    public AlarmRecord markHandled(Long id) {
        AlarmRecord record = alarmRecordRepository.findById(id)
                .orElseThrow(() -> new BusinessException("告警记录不存在，id=" + id));
        record.setHandled(true);
        return alarmRecordRepository.save(record);
    }
}
