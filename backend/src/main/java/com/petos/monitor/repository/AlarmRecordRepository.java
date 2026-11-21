package com.petos.monitor.repository;

import com.petos.monitor.entity.AlarmRecord;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * 告警抓拍记录持久层接口。
 * 负责告警记录的保存与历史查询。
 */
@Repository
public interface AlarmRecordRepository extends JpaRepository<AlarmRecord, Long> {

    /**
     * 查询全部告警记录，按告警时间倒序（最新告警排最前）
     */
    List<AlarmRecord> findAllByOrderByAlarmTimeDesc();

    /**
     * 只查最近 10 条告警，首页/仪表盘用
     */
    List<AlarmRecord> findTop10ByOrderByAlarmTimeDesc();

    /**
     * 查询某台设备的告警记录，按时间倒序，支持按设备筛选
     */
    List<AlarmRecord> findByDeviceSnOrderByAlarmTimeDesc(String deviceSn);
}
