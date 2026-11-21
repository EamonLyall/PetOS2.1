package com.petos.monitor.repository;

import com.petos.monitor.entity.SensorData;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

/**
 * 传感器数据持久层接口。
 * 负责把 ESP32 上报的温湿度、PIR、门磁数据存库、查询。
 */
@Repository
public interface SensorDataRepository extends JpaRepository<SensorData, Long> {

    /**
     * 查询某台设备的全部传感器数据，按上报时间倒序（最新的在前）
     * 方法名里的 OrderBy...Desc 会被自动翻译成 order by report_time desc
     */
    List<SensorData> findByDeviceSnOrderByReportTimeDesc(String deviceSn);

    /**
     * 只查某台设备最近的 20 条数据，前端图表用，避免一次拉太多
     * Top20 表示只取前 20 条
     */
    List<SensorData> findTop20ByDeviceSnOrderByReportTimeDesc(String deviceSn);

    /**
     * 查询某台设备在一段时间区间内的数据，方便做时间段筛选
     */
    List<SensorData> findByDeviceSnAndReportTimeBetween(String deviceSn,
                                                        LocalDateTime startTime,
                                                        LocalDateTime endTime);
}
