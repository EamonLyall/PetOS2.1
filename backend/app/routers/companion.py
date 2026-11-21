# ============================================================
# 陪伴域路由：对照前端 Vue 工程（设备 / 宠物 / 聊天 / 插件 / 记忆 / 设置 / 天气）。
#
# 接口统一挂在 /api 前缀下，返回统一响应壳 {code, message, data}。
# 字段名与前端 store、模板读取的字段严格对齐（camelCase），例如 petKey、activeDeviceId。
# ============================================================

from datetime import datetime

from fastapi import APIRouter, Body, Query

from ..database import get_db, get_setting, set_setting
from ..common.response import ok, BusinessError
from ..services import llm
from ..services.mqtt import get_mqtt_service
from .. import seed

router = APIRouter(prefix="/api", tags=["陪伴域"])


# ------------------------------------------------------------
# 行数据 -> 前端字典的转换工具
# ------------------------------------------------------------
def _device_dict(row) -> dict:
    """设备行 -> 前端设备对象（字段与 seed.js 的 devices 一致）。"""
    return {
        "id": row["id"],
        "name": row["name"],
        "petKey": row["pet_key"],
        "place": row["place"],
        "online": bool(row["online"]),
        "signal": row["signal"],
        "battery": row["battery"],
        "fw": row["fw"],
        "wifi": row["wifi"],
        "last": row["last"],
    }


def _nearby_dict(row) -> dict:
    """附近设备行 -> 前端附近设备对象（字段与 seed.js 的 nearby 一致）。"""
    return {
        "id": row["id"],
        "name": row["name"],
        "petKey": row["pet_key"],
        "place": row["place"],
        "signal": row["signal"],
    }


def _pet_dict(row) -> dict:
    """宠物档案行 -> 前端宠物对象（含健康档案扩展字段）。"""
    return {
        "petKey": row["pet_key"],
        "name": row["name"],
        "emoji": row["emoji"],
        "breed": row["breed"],
        "age": row["age"],
        "weight": row["weight"],
        "level": row["level"],
        "growth": row["growth"],
        "mood": row["mood"],
        "active": row["active"],
        "interact": row["interact"],
        "days": row["days"],
        "desc": row["desc"],
        # 健康档案扩展（“我的宠物”页右侧卡片使用）
        "heartRate": row["heart_rate"],
        "activeMinutes": row["active_minutes"],
        "sleepHours": row["sleep_hours"],
        "lastCheckup": row["last_checkup"],
        "moments": row["moments"],
        "songs": row["songs"],
        "games": row["games"],
        # 状态卡片扩展字段（数据库列 -> 前端 camelCase）
        "energy": row["energy"],
        "moodTag": row["mood_tag"],
        "healthStatus": row["health_status"],
    }


def _fill_placeholders(text: str, pet: dict | None) -> str:
    """把时间线/里程碑文案里的 {level} {growth} {name} {breed} {days} 占位符替换成真实值。"""
    if not text or pet is None:
        return text or ""
    replacements = {
        "{level}": str(pet.get("level", "")),
        "{growth}": str(pet.get("growth", "")),
        "{name}": pet.get("name", ""),
        "{breed}": pet.get("breed", ""),
        "{days}": str(pet.get("days", "")),
    }
    for key, value in replacements.items():
        text = text.replace(key, value)
    return text


def _get_pet_or_404(conn, pet_key: str) -> dict:
    """按 pet_key 查宠物档案，不存在则抛业务异常。"""
    row = conn.execute("SELECT * FROM pet WHERE pet_key = ?", (pet_key,)).fetchone()
    if row is None:
        raise BusinessError(f"宠物档案不存在：{pet_key}")
    return _pet_dict(row)


# ------------------------------------------------------------
# 设置分组：所有分组统一从 app_setting 表读取，避免接口各处重复拼装
# ------------------------------------------------------------
SETTING_GROUPS = ("voice", "screen", "music", "network", "device", "notify", "profile", "camera")


def _settings_dict(conn) -> dict:
    """读取完整设置：连接状态 + 8 个结构化分组。"""
    data = {
        "connected": get_setting(conn, "connected", True),
        "activeDeviceId": get_setting(conn, "active_device_id", None),
    }
    for group in SETTING_GROUPS:
        data[group] = get_setting(conn, group, {})
    return data


def _notification_dict(row) -> dict:
    """通知行 -> 前端通知对象。"""
    return {
        "id": row["id"],
        "icon": row["icon"],
        "tone": row["tone"],
        "text": row["text"],
        "timeAgo": row["time_ago"],
        "read": bool(row["read"]),
    }


def _list_notifications(conn) -> list[dict]:
    """按排序读取全部通知。"""
    rows = conn.execute("SELECT * FROM notification ORDER BY sort, id")
    return [_notification_dict(r) for r in rows]


# ============================================================
# 1. 全量快照（前端一次性拉齐所有演示数据，替代本地 seed.js）
# ============================================================
@router.get("/state", summary="全量状态快照")
def get_state():
    """返回设备、宠物、天气、图表、聊天、打卡、插件、记忆等全部前端所需数据。"""
    with get_db() as conn:
        devices = [_device_dict(r) for r in
                   conn.execute("SELECT * FROM companion_device WHERE is_nearby = 0 ORDER BY sort")]
        nearby = [_nearby_dict(r) for r in
                  conn.execute("SELECT * FROM companion_device WHERE is_nearby = 1 ORDER BY sort")]
        pets = {r["pet_key"]: _pet_dict(r) for r in conn.execute("SELECT * FROM pet")}
        weather_row = conn.execute("SELECT * FROM weather WHERE id = 1").fetchone()
        weather = {"text": weather_row["text"], "temp": weather_row["temp"], "wind": weather_row["wind"]}

        # 趋势图：按区间聚合成 {labels, interact, online}
        charts: dict[str, dict] = {}
        for range_key in ("week", "month", "quarter"):
            rows = conn.execute(
                "SELECT label, interact, online FROM chart_stat WHERE range_key = ? ORDER BY sort",
                (range_key,),
            ).fetchall()
            charts[range_key] = {
                "labels": [r["label"] for r in rows],
                "interact": [r["interact"] for r in rows],
                "online": [r["online"] for r in rows],
            }

        settings = _settings_dict(conn)

        chat_messages = [
            {"who": r["who"], "text": r["text"]}
            for r in conn.execute("SELECT who, text FROM chat_message ORDER BY sort, id")
        ]
        bless_list = [
            {"text": r["text"], "done": bool(r["done"])}
            for r in conn.execute("SELECT text, done FROM bless_item ORDER BY sort")
        ]
        plugins = [_plugin_dict(r) for r in conn.execute("SELECT * FROM plugin ORDER BY sort")]

        # 确定当前活跃宠物：优先按已保存的当前设备，否则取第一台已绑定设备
        active_id = settings.get("activeDeviceId")
        active_pet = None
        if active_id:
            active_dev = conn.execute("SELECT * FROM companion_device WHERE id = ?", (active_id,)).fetchone()
            if active_dev:
                active_pet_row = conn.execute(
                    "SELECT * FROM pet WHERE pet_key = ?", (active_dev["pet_key"],)
                ).fetchone()
                active_pet = _pet_dict(active_pet_row) if active_pet_row else None
        if active_pet is None:
            first_dev = conn.execute(
                "SELECT * FROM companion_device WHERE is_nearby = 0 ORDER BY sort LIMIT 1"
            ).fetchone()
            if first_dev:
                active_pet_row = conn.execute(
                    "SELECT * FROM pet WHERE pet_key = ?", (first_dev["pet_key"],)
                ).fetchone()
                active_pet = _pet_dict(active_pet_row) if active_pet_row else None

        # 时间线 / 里程碑文案里的 {level}{growth}{name}{breed}{days} 按当前宠物替换
        timeline = [
            {
                "date": r["event_date"],
                "title": _fill_placeholders(r["title"], active_pet),
                "desc": _fill_placeholders(r["description"], active_pet),
            }
            for r in conn.execute("SELECT * FROM memory_timeline ORDER BY sort")
        ]
        milestones = [
            {
                "label": r["label"],
                "value": _fill_placeholders(r["value"], active_pet),
                "tail": r["tail"],
            }
            for r in conn.execute("SELECT * FROM memory_milestone ORDER BY sort")
        ]
        gallery = [
            {"imageKey": r["image_key"], "imageUrl": r["image_url"], "caption": r["caption"]}
            for r in conn.execute("SELECT * FROM gallery_item ORDER BY sort")
        ]
        notifications = _list_notifications(conn)

    return ok({
        "devices": devices,
        "nearby": nearby,
        "pets": pets,
        "weather": weather,
        "charts": charts,
        "settings": settings,
        "chatMessages": chat_messages,
        "blessList": bless_list,
        "plugins": plugins,
        "timeline": timeline,
        "milestones": milestones,
        "gallery": gallery,
        "notifications": notifications,
        "unreadCount": sum(1 for n in notifications if not n["read"]),
    })


# ============================================================
# 2. 设备相关
# ============================================================
@router.get("/devices", summary="已绑定设备列表")
def list_devices():
    """返回已配对入库的设备（对应前端 store.devices）。"""
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM companion_device WHERE is_nearby = 0 ORDER BY sort")
        return ok([_device_dict(r) for r in rows])


@router.get("/devices/nearby", summary="附近可配对设备")
def list_nearby():
    """返回附近尚未配对的设备（对应前端 store.nearby）。"""
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM companion_device WHERE is_nearby = 1 ORDER BY sort")
        return ok([_nearby_dict(r) for r in rows])


@router.post("/devices/{device_id}/connect", summary="连接 / 配对设备")
def connect_device(device_id: str):
    """
    连接设备：
    - 已绑定设备：直接切换为当前设备并置为已连接；
    - 附近设备：先配对入库（补默认电量/固件/Wi-Fi），再切换连接。
    """
    with get_db() as conn:
        row = conn.execute("SELECT * FROM companion_device WHERE id = ?", (device_id,)).fetchone()
        if row is None:
            raise BusinessError(f"设备不存在：{device_id}")

        # 附近设备首次配对：从“附近”移入“已绑定”，补默认演示值
        if row["is_nearby"] == 1:
            conn.execute(
                """UPDATE companion_device
                   SET is_nearby = 0, online = 1, battery = 66, fw = 'v2.4.0',
                       wifi = 'PetOS-Home', last = '刚刚配对'
                   WHERE id = ?""",
                (device_id,),
            )
            row = conn.execute("SELECT * FROM companion_device WHERE id = ?", (device_id,)).fetchone()

        # 更新全局连接状态与当前设备
        set_setting(conn, "connected", True)
        set_setting(conn, "active_device_id", device_id)

        pet_row = conn.execute("SELECT * FROM pet WHERE pet_key = ?", (row["pet_key"],)).fetchone()
        pet = _pet_dict(pet_row) if pet_row else None

        # 预留：连接成功后可经 MQTT 订阅该设备遥测主题（当前演示模式仅记录日志）
        get_mqtt_service().publish(device_id, "status", {"online": True})

        return ok({"device": _device_dict(row), "pet": pet})


@router.post("/devices/{device_id}/disconnect", summary="断开设备连接")
def disconnect_device(device_id: str):
    """断开当前连接（设备本身在线标记不变，与前端原型行为一致）。"""
    with get_db() as conn:
        row = conn.execute("SELECT id FROM companion_device WHERE id = ?", (device_id,)).fetchone()
        if row is None:
            raise BusinessError(f"设备不存在：{device_id}")
        set_setting(conn, "connected", False)
        get_mqtt_service().publish(device_id, "status", {"online": False})
        return ok({"activeDeviceId": device_id, "connected": False})


@router.post("/devices/scan", summary="重新扫描附近设备")
def scan_devices():
    """
    触发一次附近设备扫描。
    【预留】真实场景由蓝牙/Wi-Fi 发现或 MQTT 心跳上报补充设备；当前返回库中附近设备。
    """
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM companion_device WHERE is_nearby = 1 ORDER BY sort")
        nearby = [_nearby_dict(r) for r in rows]
    return ok({"nearby": nearby, "count": len(nearby)})


@router.get("/devices/{device_id}/telemetry", summary="设备实时遥测")
def device_telemetry(device_id: str):
    """返回当前设备的电量/信号/心率/活跃度等实时遥测（演示值取自档案库）。"""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM companion_device WHERE id = ?", (device_id,)).fetchone()
        if row is None:
            raise BusinessError(f"设备不存在：{device_id}")
        pet_row = conn.execute("SELECT * FROM pet WHERE pet_key = ?", (row["pet_key"],)).fetchone()
        pet = _pet_dict(pet_row) if pet_row else {}
        return ok({
            "deviceId": device_id,
            "battery": row["battery"],
            "signal": row["signal"],
            "heartRate": pet.get("heartRate", 0),
            "active": pet.get("active", 0),
            "onlineMinutes": pet.get("activeMinutes", 0),
            "mood": pet.get("mood", ""),
            "ts": int(datetime.now().timestamp()),
        })


# ============================================================
# 3. 宠物档案 / 记忆 / 统计
# ============================================================
@router.get("/pets/{pet_key}/profile", summary="宠物档案")
def pet_profile(pet_key: str):
    """返回单个宠物的完整档案（对应“我的宠物”页）。"""
    with get_db() as conn:
        pet = _get_pet_or_404(conn, pet_key)
    return ok(pet)


@router.get("/pets/{pet_key}/timeline", summary="成长时间线")
def pet_timeline(pet_key: str):
    """返回成长时间线，文案占位符按当前宠物替换。"""
    with get_db() as conn:
        pet = _get_pet_or_404(conn, pet_key)
        rows = conn.execute("SELECT * FROM memory_timeline ORDER BY sort").fetchall()
        timeline = [
            {
                "date": r["event_date"],
                "title": _fill_placeholders(r["title"], pet),
                "desc": _fill_placeholders(r["description"], pet),
            }
            for r in rows
        ]
    return ok(timeline)


@router.get("/pets/{pet_key}/milestones", summary="里程碑统计")
def pet_milestones(pet_key: str):
    """返回里程碑指标（累计互动/听歌/游戏/开心时刻）。"""
    with get_db() as conn:
        pet = _get_pet_or_404(conn, pet_key)
        rows = conn.execute("SELECT * FROM memory_milestone ORDER BY sort").fetchall()
        milestones = [
            {"label": r["label"], "value": _fill_placeholders(r["value"], pet), "tail": r["tail"]}
            for r in rows
        ]
    return ok(milestones)


@router.get("/pets/{pet_key}/gallery", summary="照片墙")
def pet_gallery(pet_key: str):
    """返回照片墙列表。"""
    with get_db() as conn:
        _get_pet_or_404(conn, pet_key)  # 校验宠物存在
        rows = conn.execute("SELECT * FROM gallery_item ORDER BY sort")
        gallery = [
            {"imageKey": r["image_key"], "imageUrl": r["image_url"], "caption": r["caption"]}
            for r in rows
        ]
    return ok(gallery)


@router.get("/pets/{pet_key}/stats", summary="陪伴统计趋势")
def pet_stats(pet_key: str, range: str = Query("week", description="week/month/quarter")):
    """返回指定区间的互动次数与在线时长趋势图数据。"""
    if range not in ("week", "month", "quarter"):
        raise BusinessError("range 仅支持 week / month / quarter")
    with get_db() as conn:
        _get_pet_or_404(conn, pet_key)
        rows = conn.execute(
            "SELECT label, interact, online FROM chart_stat WHERE range_key = ? ORDER BY sort",
            (range,),
        ).fetchall()
        return ok({
            "range": range,
            "labels": [r["label"] for r in rows],
            "interact": [r["interact"] for r in rows],
            "online": [r["online"] for r in rows],
        })


@router.post("/pets/{pet_key}/interact", summary="快速互动（写入数据库）")
def pet_interact(pet_key: str, payload: dict = Body(default={})):
    """
    前端“快速互动”按钮调用：互动次数 +1 落库，抚摸/游戏额外增加成长值（上限 100）。
    返回最新宠物档案，前端直接合并，保证界面与数据库严格一致。
    """
    action = (payload.get("action") or "pet").strip()
    if action not in seed.INTERACT_MESSAGES:
        raise BusinessError("action 仅支持 pet / voice / game / music")

    with get_db() as conn:
        _get_pet_or_404(conn, pet_key)

        # 互动次数 +1；抚摸和游戏会带来少量成长值（最多 100）
        conn.execute("UPDATE pet SET interact = interact + 1 WHERE pet_key = ?", (pet_key,))
        if action in ("pet", "game"):
            conn.execute(
                "UPDATE pet SET growth = MIN(100, growth + 1) WHERE pet_key = ?", (pet_key,)
            )
        row = conn.execute("SELECT * FROM pet WHERE pet_key = ?", (pet_key,)).fetchone()
        pet = _pet_dict(row)

        # 找到该宠物对应的设备，预留 MQTT 下行（真实场景可让设备做出动作反馈）
        device = conn.execute(
            "SELECT id FROM companion_device WHERE pet_key = ? ORDER BY sort LIMIT 1", (pet_key,)
        ).fetchone()
        if device:
            get_mqtt_service().publish(device["id"], "interact", {"action": action})

    return ok({"action": action, "pet": pet, "message": seed.INTERACT_MESSAGES[action]})


# ============================================================
# 4. 天气
# ============================================================
@router.get("/weather", summary="当前天气")
def get_weather():
    """返回首页/天气助手使用的天气信息。"""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM weather WHERE id = 1").fetchone()
        return ok({"text": row["text"], "temp": row["temp"], "wind": row["wind"]})


# ============================================================
# 5. 全局设置（语音 / 表情屏 / 音乐 / 连接状态）
# ============================================================
@router.get("/settings", summary="获取全局设置")
def get_settings_api():
    """返回连接状态与全部结构化设置分组（语音/屏幕/音乐/网络/设备/通知/账户/摄像头）。"""
    with get_db() as conn:
        data = _settings_dict(conn)
    return ok(data)


@router.put("/settings", summary="更新全局设置")
def update_settings(payload: dict = Body(...)):
    """
    局部更新设置，支持字段：connected / activeDeviceId 以及
    voice / screen / music / network / device / notify / profile / camera。
    结构化对象采用浅合并：只覆盖传入的子字段，未传字段保持数据库原值。
    """
    with get_db() as conn:
        if "connected" in payload:
            set_setting(conn, "connected", bool(payload["connected"]))
        if "activeDeviceId" in payload:
            set_setting(conn, "active_device_id", payload["activeDeviceId"])

        # 结构化分组统一浅合并（原先只支持 voice/screen/music，现扩展为全部设置分组）
        for key in SETTING_GROUPS:
            if key in payload and isinstance(payload[key], dict):
                current = get_setting(conn, key, {})
                current.update(payload[key])
                set_setting(conn, key, current)

        # 语音/屏幕/音乐/设备开关变化时，预留 MQTT 下行指令（演示模式仅打印日志）
        mqtt = get_mqtt_service()
        active_id = get_setting(conn, "active_device_id", None)
        if active_id:
            if "voice" in payload and "volume" in payload["voice"]:
                mqtt.publish(active_id, "volume", {"volume": payload["voice"]["volume"]})
            if "voice" in payload and "tts" in payload["voice"]:
                mqtt.publish(active_id, "tts", {"on": payload["voice"]["tts"]})
            if "screen" in payload:
                mqtt.publish(active_id, "screen", payload["screen"])
            if "music" in payload:
                mqtt.publish(active_id, "music", payload["music"])
            if "device" in payload:
                mqtt.publish(active_id, "device", payload["device"])

        data = _settings_dict(conn)
    return ok(data)


# ============================================================
# 6. 聊天
# ============================================================
@router.get("/chat/messages", summary="历史聊天记录")
def list_messages():
    """返回当前全部聊天记录（对应前端 store.chatMessages）。"""
    with get_db() as conn:
        rows = conn.execute("SELECT who, text FROM chat_message ORDER BY sort, id")
        return ok([{"who": r["who"], "text": r["text"]} for r in rows])


@router.post("/chat", summary="发送消息并获取小宠回复")
@router.post("/llm/chat", summary="大模型对话代理别名（兼容前端 VITE_LLM_BASE_URL=/api/llm）")
def chat(payload: dict = Body(...)):
    """
    对话代理：保存主人消息 -> 调用大模型（未配置则兜底）-> 保存回复 -> 返回。
    入参 JSON：{ "text": "你好", "deviceId": "d-nuomi", "messages": [...] }
    """
    text = (payload.get("text") or "").strip()
    if not text:
        raise BusinessError("消息内容不能为空")
    device_id = payload.get("deviceId")
    history = payload.get("messages") or []

    with get_db() as conn:
        # 若前端未带历史，取库中记录作为上下文
        if not history:
            history = [
                {"who": r["who"], "text": r["text"]}
                for r in conn.execute("SELECT who, text FROM chat_message ORDER BY sort, id")
            ]

        # 落库主人消息
        max_sort = conn.execute("SELECT COALESCE(MAX(sort), 0) AS m FROM chat_message").fetchone()["m"]
        conn.execute(
            "INSERT INTO chat_message (who, text, device_id, created_at, sort) VALUES (?, ?, ?, ?, ?)",
            ("me", text, device_id, datetime.now().isoformat(timespec="seconds"), max_sort + 1),
        )

        # 调用大模型/兜底生成回复
        reply = llm.chat(history, text, device_id)

        # 落库小宠回复
        conn.execute(
            "INSERT INTO chat_message (who, text, device_id, created_at, sort) VALUES (?, ?, ?, ?, ?)",
            ("pet", reply, device_id, datetime.now().isoformat(timespec="seconds"), max_sort + 2),
        )

    return ok({"reply": reply})


# ============================================================
# 7. 插件中心
# ============================================================
def _plugin_dict(row) -> dict:
    """插件行 -> 前端插件对象；同时保留规范字段与前端原型短字段（n/i/c/d/on）。"""
    return {
        "id": row["id"],
        "name": row["name"],
        "icon": row["icon"],
        "color": row["color"],
        "desc": row["desc"],
        "enabled": bool(row["enabled"]),
        # 原型短字段别名，方便未改造的前端模板直接渲染
        "n": row["name"],
        "i": row["icon"],
        "c": row["color"],
        "d": row["desc"],
        "on": bool(row["enabled"]),
    }


@router.get("/plugins", summary="插件清单")
def list_plugins():
    """返回全部插件（含启用状态），对应“插件中心”页。"""
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM plugin ORDER BY sort")
        return ok([_plugin_dict(r) for r in rows])


@router.put("/plugins/{plugin_id}/toggle", summary="切换插件启用状态")
def toggle_plugin(plugin_id: int):
    """翻转指定插件的启用/禁用状态。"""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM plugin WHERE id = ?", (plugin_id,)).fetchone()
        if row is None:
            raise BusinessError(f"插件不存在：{plugin_id}")
        new_enabled = 0 if row["enabled"] else 1
        conn.execute("UPDATE plugin SET enabled = ? WHERE id = ?", (new_enabled, plugin_id))
        row = conn.execute("SELECT * FROM plugin WHERE id = ?", (plugin_id,)).fetchone()
    return ok(_plugin_dict(row))


# ============================================================
# 8. 今日小确幸打卡
# ============================================================
@router.get("/bless", summary="小确幸打卡清单")
def list_bless():
    """返回今日小确幸事项及完成状态。"""
    with get_db() as conn:
        rows = conn.execute("SELECT id, text, done FROM bless_item ORDER BY sort")
        return ok([{"id": r["id"], "text": r["text"], "done": bool(r["done"])} for r in rows])


@router.put("/bless/{item_id}/toggle", summary="切换打卡完成状态")
def toggle_bless(item_id: int):
    """翻转指定打卡事项的完成状态。"""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM bless_item WHERE id = ?", (item_id,)).fetchone()
        if row is None:
            raise BusinessError(f"打卡事项不存在：{item_id}")
        new_done = 0 if row["done"] else 1
        conn.execute("UPDATE bless_item SET done = ? WHERE id = ?", (new_done, item_id))
        row = conn.execute("SELECT id, text, done FROM bless_item WHERE id = ?", (item_id,)).fetchone()
    return ok({"id": row["id"], "text": row["text"], "done": bool(row["done"])})


# ============================================================
# 9. 通知中心（顶栏通知气泡，已读状态落库）
# ============================================================
@router.get("/notifications", summary="通知列表")
def list_notifications():
    """返回全部通知与未读数，顶栏通知气泡直接渲染该数据。"""
    with get_db() as conn:
        notifications = _list_notifications(conn)
    return ok({
        "notifications": notifications,
        "unreadCount": sum(1 for n in notifications if not n["read"]),
    })


@router.put("/notifications/read", summary="全部标记为已读")
def read_all_notifications():
    """把全部通知标记为已读，并返回最新列表。"""
    with get_db() as conn:
        conn.execute("UPDATE notification SET read = 1")
        notifications = _list_notifications(conn)
    return ok({"notifications": notifications, "unreadCount": 0})


# ============================================================
# 10. 导航配置（静态，供侧边栏渲染；前端已内置同源配置作为兜底）
# ============================================================
@router.get("/nav", summary="侧边导航配置")
def list_nav():
    """返回侧边导航项（key 与路由 name 对应）。"""
    return ok([
        {"key": "home", "name": "总览首页", "icon": "home"},
        {"key": "pet", "name": "我的宠物", "icon": "pet"},
        {"key": "chat", "name": "互动陪伴", "icon": "chat"},
        {"key": "device", "name": "设备控制", "icon": "device"},
        {"key": "memory", "name": "成长记忆", "icon": "memory"},
        {"key": "plugin", "name": "插件中心", "icon": "plugin"},
        {"key": "settings", "name": "系统设置", "icon": "settings"},
    ])
