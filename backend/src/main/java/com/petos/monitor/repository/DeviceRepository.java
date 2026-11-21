package com.petos.monitor.repository;

import com.petos.monitor.entity.Device;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * 设备持久层接口。
 * 继承 JpaRepository 后，免费获得 save、findById、findAll、deleteById 等常用方法，不用自己写 SQL。
 * 泛型含义：<Device, Long> 表示操作的实体是 Device，它的主键类型是 Long。
 */
@Repository
public interface DeviceRepository extends JpaRepository<Device, Long> {

    /**
     * 根据设备 SN 查设备，可能查不到，所以用 Optional 包装（避免空指针）
     * Spring Data JPA 会根据方法名自动拼出 SQL：where sn = ?
     */
    Optional<Device> findBySn(String sn);

    /**
     * 判断某个 SN 是否已存在，注册/上报时用来防止重复
     */
    boolean existsBySn(String sn);

    /**
     * 按设备类型查询（比如只查所有 ESP32，或只查所有香橙派）
     */
    List<Device> findByDeviceType(String deviceType);

    /**
     * 按在线状态查询，统计在线/离线设备数量时用
     */
    List<Device> findByOnline(Boolean online);
}
