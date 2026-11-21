# ============================================================
# 硬件监控域路由（遗留链路保留）：ESP32-S3 传感器、香橙派告警抓拍、
# 下行指令、大屏统计。字段命名与旧 SpringBoot 实体的 JSON 输出保持一致
# （camelCase，如 deviceSn / pirTriggered），保证旧前端/硬件脚本无需改动。
#
# 说明：陪伴域设备占用了 /api/devices，因此监控域设备列表挂在 /api/monitor/devices；
#       传感器 / 告警 / 指令 / 仪表盘沿用旧路径 /api/sensors、/api/alarms、
#       /api/commands、/api/dashboard，避免与陪伴域冲突。
# ============================================================

import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Body, File, Form, UploadFile

from ..database import get_db
from ..config import get_settings
from ..common.response import ok, BusinessError
from ..services.mqtt import get_mqtt_service

router = APIRouter(tags=["监控域"])

# 允许上传的图片后缀
ALLOWED_IMAGE_SUFFIX = {".jpg", ".jpeg", ".png"}


# ------------------------------------------------------------
# 行数据转换
# ------------------------------------------------------------
def _monitor_device_dict(row) -> dict:
    return {
        "id": row["id"],
        "deviceName": row["device_name"],
        "deviceType": row["device_type"],
        "sn": row["sn"],
        "online": bool(row["online"]),
        "lastHeartbeat": row["last_heartbeat"],
        "location": row["location"],
        "createTime": row["create_time"],
    }


def _sensor_dict(row) -> dict:
    return {
        "id": row["id"],
        "deviceSn": row["device_sn"],
        "temperature": row["temperature"],
        "humidity": row["humidity"],
        "pirTriggered": bool(row["pir_triggered"]),
        "doorClosed": bool(row["door_closed"]),
        "reportTime": row["report_time"],
    }


def _alarm_dict(row) -> dict:
    return {
        "id": row["id"],
        "deviceSn": row["device_sn"],
        "cameraSn": row["camera_sn"],
        "alarmType": row["alarm_type"],
        "confidence": row["confidence"],
        "imagePath": row["image_path"],
        "imageUrl": row["image_url"],
        "handled": bool(row["handled"]),
        "description": row["description"],
        "alarmTime": row["alarm_time"],
        "createTime": row["create_time"],
    }


# ============================================================
# 1. 监控设备
# ============================================================
@router.get("/api/monitor/devices", summary="监控设备列表")
def list_monitor_devices():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM monitor_device ORDER BY id")
        return ok([_monitor_device_dict(r) for r in rows])


@router.get("/api/monitor/devices/type/{device_type}", summary="按类型查监控设备")
def list_monitor_devices_by_type(device_type: str):
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM monitor_device WHERE device_type = ? ORDER BY id",
                            (device_type,))
        return ok([_monitor_device_dict(r) for r in rows])


@router.get("/api/monitor/devices/{sn}", summary="按 SN 查监控设备")
def get_monitor_device(sn: str):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM monitor_device WHERE sn = ?", (sn,)).fetchone()
        if row is None:
            raise BusinessError(f"设备不存在，sn={sn}")
        return ok(_monitor_device_dict(row))


# ============================================================
# 2. 传感器数据
# ============================================================
@router.get("/api/sensors/{sn}/recent", summary="最近 20 条传感器数据")
def recent_sensors(sn: str):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM sensor_data WHERE device_sn = ? ORDER BY report_time DESC, id DESC LIMIT 20",
            (sn,),
        )
        # 图表按时间正序展示，这里反转回来
        return ok([_sensor_dict(r) for r in reversed(list(rows))])


@router.get("/api/sensors/{sn}", summary="全部传感器历史数据")
def all_sensors(sn: str):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM sensor_data WHERE device_sn = ? ORDER BY report_time ASC, id ASC",
            (sn,),
        )
        return ok([_sensor_dict(r) for r in rows])


# ============================================================
# 3. 告警抓拍记录
# ============================================================
@router.get("/api/alarms", summary="全部告警记录（时间倒序）")
def list_alarms():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM alarm_record ORDER BY alarm_time DESC, id DESC")
        return ok([_alarm_dict(r) for r in rows])


@router.get("/api/alarms/recent", summary="最近 10 条告警")
def recent_alarms():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM alarm_record ORDER BY alarm_time DESC, id DESC LIMIT 10")
        return ok([_alarm_dict(r) for r in rows])


@router.get("/api/alarms/device/{sn}", summary="按设备查告警")
def alarms_by_device(sn: str):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM alarm_record WHERE device_sn = ? ORDER BY alarm_time DESC, id DESC",
            (sn,),
        )
        return ok([_alarm_dict(r) for r in rows])


@router.post("/api/alarms/upload", summary="上传抓拍图片并生成告警记录")
async def upload_alarm(
    file: UploadFile = File(...),
    deviceSn: str = Form(...),
    cameraSn: str = Form(...),
    confidence: float | None = Form(None),
):
    """
    香橙派识别到人体后调用：上传抓拍图 -> 保存到 upload-images -> 生成告警记录入库。
    仅允许 jpg/jpeg/png；文件名校验失败直接报错。
    """
    settings = get_settings()
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_IMAGE_SUFFIX:
        raise BusinessError("仅支持 jpg / png 图片上传")

    # 生成不重复的文件名，避免覆盖
    filename = f"alarm_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}{suffix}"
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = settings.upload_dir / filename
    file_path.write_bytes(await file.read())

    image_url = f"/images/{filename}"
    now = datetime.now().isoformat(timespec="seconds")

    with get_db() as conn:
        cur = conn.execute(
            """INSERT INTO alarm_record
               (device_sn, camera_sn, alarm_type, confidence, image_path, image_url,
                handled, description, alarm_time, create_time)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (deviceSn, cameraSn, "PERSON_DETECT", confidence,
             str(file_path), image_url, 0, "检测到人体，已自动抓拍", now, now),
        )
        row = conn.execute("SELECT * FROM alarm_record WHERE id = ?", (cur.lastrowid,)).fetchone()

    return ok(_alarm_dict(row))


@router.put("/api/alarms/{alarm_id}/handle", summary="标记告警已处理")
def handle_alarm(alarm_id: int):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM alarm_record WHERE id = ?", (alarm_id,)).fetchone()
        if row is None:
            raise BusinessError(f"告警记录不存在：{alarm_id}")
        conn.execute("UPDATE alarm_record SET handled = 1 WHERE id = ?", (alarm_id,))
        row = conn.execute("SELECT * FROM alarm_record WHERE id = ?", (alarm_id,)).fetchone()
    return ok(_alarm_dict(row))


# ============================================================
# 4. 下行指令（转发 MQTT 给 ESP32 / 香橙派）
# ============================================================
@router.post("/api/commands/light", summary="控制补光灯")
def command_light(body: dict = Body(...)):
    _require_sn(body)
    on = bool(body.get("on"))
    get_mqtt_service().publish_raw(
        f"monitor/esp32/{body['sn']}/control",
        {"sn": body["sn"], "command": "LIGHT", "params": {"on": on}},
    )
    return ok()


@router.post("/api/commands/buzzer", summary="控制蜂鸣器")
def command_buzzer(body: dict = Body(...)):
    _require_sn(body)
    on = bool(body.get("on"))
    get_mqtt_service().publish_raw(
        f"monitor/esp32/{body['sn']}/control",
        {"sn": body["sn"], "command": "BUZZER", "params": {"on": on}},
    )
    return ok()


@router.post("/api/commands/gimbal", summary="控制云台转动")
def command_gimbal(body: dict = Body(...)):
    _require_sn(body)
    pan = int(body.get("pan", 0))
    tilt = int(body.get("tilt", 0))
    get_mqtt_service().publish_raw(
        f"monitor/esp32/{body['sn']}/control",
        {"sn": body["sn"], "command": "GIMBAL", "params": {"pan": pan, "tilt": tilt}},
    )
    return ok()


def _require_sn(body: dict) -> str:
    """校验请求体里的设备 SN 非空。"""
    sn = body.get("sn")
    if not sn or not str(sn).strip():
        raise BusinessError("设备 sn 不能为空")
    return str(sn).strip()


# ============================================================
# 5. 大屏统计
# ============================================================
@router.get("/api/dashboard/stats", summary="大屏汇总统计")
def dashboard_stats():
    with get_db() as conn:
        device_total = conn.execute("SELECT COUNT(*) AS c FROM monitor_device").fetchone()["c"]
        online_total = conn.execute(
            "SELECT COUNT(*) AS c FROM monitor_device WHERE online = 1").fetchone()["c"]
        esp32_total = conn.execute(
            "SELECT COUNT(*) AS c FROM monitor_device WHERE device_type = 'ESP32_S3'").fetchone()["c"]
        pi_total = conn.execute(
            "SELECT COUNT(*) AS c FROM monitor_device WHERE device_type = 'ORANGE_PI'").fetchone()["c"]
        alarm_total = conn.execute("SELECT COUNT(*) AS c FROM alarm_record").fetchone()["c"]
        unhandled = conn.execute(
            "SELECT COUNT(*) AS c FROM alarm_record WHERE handled = 0").fetchone()["c"]
        latest = conn.execute(
            "SELECT temperature, humidity FROM sensor_data ORDER BY report_time DESC, id DESC LIMIT 1"
        ).fetchone()

    return ok({
        "deviceTotal": device_total,
        "onlineTotal": online_total,
        "offlineTotal": device_total - online_total,
        "esp32Total": esp32_total,
        "orangePiTotal": pi_total,
        "alarmTotal": alarm_total,
        "unhandledAlarmTotal": unhandled,
        "latestTemperature": latest["temperature"] if latest else None,
        "latestHumidity": latest["humidity"] if latest else None,
    })
