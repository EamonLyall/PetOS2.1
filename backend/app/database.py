# ============================================================
# 数据库模块：负责 SQLite 连接、建表与首次启动种子初始化。
#
# 设计说明：
#   - 默认使用 Python 自带 sqlite3，免安装数据库，路演换电脑直接跑；
#   - 表结构与 sql/petos_companion_mysql.sql 中的 MySQL 版本保持一致，
#     将来切换 MySQL 时表名/字段名无需改动；
#   - 种子数据只在“对应表为空”时写入，重复启动不会重复插入；
#   - 结构化设置（voice/screen/music）以 JSON 字符串存在 app_setting 表。
# ============================================================

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager

from . import seed
from .config import get_settings, BASE_DIR

# 读取全局配置
_settings = get_settings()

# SQLite 数据库文件路径（从 DATABASE_URL=sqlite:///./petos.db 中解析文件名）
if _settings.database_url.startswith("sqlite:///"):
    _db_path = _settings.database_url.replace("sqlite:///", "", 1)
    DB_PATH = Path(_db_path)
    if not DB_PATH.is_absolute():
        DB_PATH = BASE_DIR / DB_PATH
else:
    # 预留 MySQL 分支：当前版本未实现驱动切换，默认回退到 SQLite 文件
    DB_PATH = BASE_DIR / "petos.db"


# ------------------------------------------------------------
# 建表语句（SQLite 方言；MySQL 版本见 sql/ 目录下的脚本）
# ------------------------------------------------------------
DDL_STATEMENTS = [
    # 陪伴域：已绑定 / 附近设备（is_nearby 区分）
    """
    CREATE TABLE IF NOT EXISTS companion_device (
        id          TEXT PRIMARY KEY,          -- 设备唯一编号（d-nuomi）
        name        TEXT NOT NULL,             -- 设备名称
        pet_key     TEXT,                      -- 关联宠物档案 key
        place       TEXT,                      -- 摆放位置
        online      INTEGER DEFAULT 0,         -- 在线状态 1/0
        signal      INTEGER DEFAULT 0,         -- 信号强度 0-100
        battery     INTEGER DEFAULT 0,         -- 电量 0-100
        fw          TEXT,                      -- 固件版本
        wifi        TEXT,                      -- 所连 Wi-Fi
        last        TEXT,                      -- 最近互动描述
        is_nearby   INTEGER DEFAULT 0,         -- 1=附近未配对 0=已绑定
        sort        INTEGER DEFAULT 0          -- 排序号
    )
    """,
    # 陪伴域：宠物档案
    """
    CREATE TABLE IF NOT EXISTS pet (
        pet_key        TEXT PRIMARY KEY,      -- 档案 key（nuomi…）
        name           TEXT NOT NULL,         -- 宠物名
        emoji          TEXT,                  -- 表情图标
        breed          TEXT,                  -- 品种
        age            TEXT,                  -- 年龄（展示文本）
        weight         TEXT,                  -- 体重（展示文本）
        level          INTEGER DEFAULT 1,     -- 等级
        growth         INTEGER DEFAULT 0,     -- 成长值 0-100
        mood           TEXT,                  -- 情绪状态
        active         INTEGER DEFAULT 0,     -- 活跃度 0-100
        interact       INTEGER DEFAULT 0,     -- 今日互动次数
        days           INTEGER DEFAULT 0,     -- 陪伴天数
        desc           TEXT,                  -- 一句话描述
        heart_rate     INTEGER DEFAULT 0,     -- 心率（次/分）
        active_minutes INTEGER DEFAULT 0,     -- 今日活动分钟数
        sleep_hours    REAL DEFAULT 0,        -- 睡眠时长（小时）
        last_checkup   TEXT,                  -- 最近体检日期
        moments        INTEGER DEFAULT 0,     -- 精彩瞬间数
        songs          INTEGER DEFAULT 0,     -- 听过的歌数
        games          INTEGER DEFAULT 0,     -- 游戏局数
        energy         INTEGER DEFAULT 0,     -- 能量值 0-100（状态卡片）
        mood_tag       TEXT,                  -- 情绪标签（如 平静 / 活跃）
        health_status  TEXT                   -- 健康状态（如 良好 / 偏胖）
    )
    """,
    # 陪伴域：天气（单行表，id 固定为 1）
    """
    CREATE TABLE IF NOT EXISTS weather (
        id    INTEGER PRIMARY KEY,
        text  TEXT,                            -- 天气描述（晴/阴…）
        temp  INTEGER,                         -- 温度（摄氏度）
        wind  TEXT                             -- 风力描述
    )
    """,
    # 陪伴域：陪伴趋势图（按区间分组，逐点存储）
    """
    CREATE TABLE IF NOT EXISTS chart_stat (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        range_key  TEXT NOT NULL,              -- week / month / quarter
        label      TEXT,                       -- X 轴标签
        interact   INTEGER,                    -- 互动次数
        online     INTEGER,                    -- 在线时长指数
        sort       INTEGER DEFAULT 0
    )
    """,
    # 陪伴域：聊天记录
    """
    CREATE TABLE IF NOT EXISTS chat_message (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        who        TEXT NOT NULL,              -- me=主人 pet=小宠
        text       TEXT NOT NULL,              -- 消息文本
        device_id  TEXT,                       -- 关联设备
        created_at TEXT,                       -- 发送时间（ISO 字符串）
        sort       INTEGER DEFAULT 0
    )
    """,
    # 陪伴域：今日小确幸打卡
    """
    CREATE TABLE IF NOT EXISTS bless_item (
        id    INTEGER PRIMARY KEY AUTOINCREMENT,
        text  TEXT NOT NULL,                   -- 打卡事项
        done  INTEGER DEFAULT 0,               -- 是否完成 1/0
        sort  INTEGER DEFAULT 0
    )
    """,
    # 陪伴域：插件清单
    """
    CREATE TABLE IF NOT EXISTS plugin (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        name       TEXT NOT NULL,              -- 插件名
        icon       TEXT,                       -- 图标标识
        color      TEXT,                       -- 颜色修饰类
        desc       TEXT,                       -- 插件描述
        enabled    INTEGER DEFAULT 0,          -- 是否启用 1/0
        sort       INTEGER DEFAULT 0
    )
    """,
    # 陪伴域：全局键值设置（结构化值以 JSON 存储）
    """
    CREATE TABLE IF NOT EXISTS app_setting (
        key   TEXT PRIMARY KEY,                -- 设置项 key
        value TEXT                             -- JSON 序列化后的值
    )
    """,
    # 陪伴域：成长时间线
    """
    CREATE TABLE IF NOT EXISTS memory_timeline (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        pet_key     TEXT,                      -- 所属宠物（预留多宠物）
        event_date  TEXT,                      -- 事件日期
        title       TEXT,                      -- 标题（可含占位符）
        description TEXT,                      -- 描述（可含占位符）
        sort        INTEGER DEFAULT 0
    )
    """,
    # 陪伴域：里程碑统计
    """
    CREATE TABLE IF NOT EXISTS memory_milestone (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        pet_key  TEXT,                         -- 所属宠物
        label    TEXT,                         -- 指标名
        value    TEXT,                         -- 指标值（可含占位符）
        tail     TEXT,                         -- 右侧状态文案
        sort     INTEGER DEFAULT 0
    )
    """,
    # 陪伴域：照片墙
    """
    CREATE TABLE IF NOT EXISTS gallery_item (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        pet_key    TEXT,                       -- 所属宠物
        image_key  TEXT,                       -- 前端本地图片标识 cat/kitten
        image_url  TEXT,                       -- 后端图片地址（预留）
        caption    TEXT,                       -- 图片说明
        sort       INTEGER DEFAULT 0
    )
    """,
    # 陪伴域：通知中心（顶栏通知气泡，状态落库）
    """
    CREATE TABLE IF NOT EXISTS notification (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        icon     TEXT,                         -- 图标标识（heart/sensor/camera）
        tone     TEXT,                         -- 颜色修饰（空/mint/amber）
        text     TEXT NOT NULL,                -- 通知正文
        time_ago TEXT,                         -- 相对时间文案
        read     INTEGER DEFAULT 0,            -- 是否已读 1/0
        sort     INTEGER DEFAULT 0
    )
    """,
    # 监控域（遗留）：硬件设备
    """
    CREATE TABLE IF NOT EXISTS monitor_device (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        device_name    TEXT,
        device_type    TEXT,                   -- ESP32_S3 / ORANGE_PI
        sn             TEXT UNIQUE,            -- 设备序列号
        online         INTEGER DEFAULT 0,
        last_heartbeat TEXT,
        location       TEXT,
        create_time    TEXT
    )
    """,
    # 监控域（遗留）：传感器历史数据
    """
    CREATE TABLE IF NOT EXISTS sensor_data (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        device_sn     TEXT,
        temperature   REAL,
        humidity      REAL,
        pir_triggered INTEGER DEFAULT 0,
        door_closed   INTEGER DEFAULT 0,
        report_time   TEXT
    )
    """,
    # 监控域（遗留）：告警抓拍记录
    """
    CREATE TABLE IF NOT EXISTS alarm_record (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        device_sn   TEXT,
        camera_sn   TEXT,
        alarm_type  TEXT,
        confidence  REAL,
        image_path  TEXT,
        image_url   TEXT,
        handled     INTEGER DEFAULT 0,
        description TEXT,
        alarm_time  TEXT,
        create_time TEXT
    )
    """,
]


@contextmanager
def get_db():
    """
    数据库连接上下文管理器：`with get_db() as conn:` 使用。
    - 自动开启外键约束；
    - 正常结束自动提交，异常回滚；
    - 连接用完自动关闭。
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 行结果可按列名取值（dict 风格）
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _table_count(conn: sqlite3.Connection, table: str) -> int:
    """统计某张表的行数，用于判断是否需要写入种子数据。"""
    row = conn.execute(f"SELECT COUNT(*) AS cnt FROM {table}").fetchone()
    return row["cnt"]


def _seed_companion(conn: sqlite3.Connection) -> None:
    """写入陪伴域种子数据（仅当表为空时）。"""
    if _table_count(conn, "companion_device") == 0:
        for d in seed.DEVICES + seed.NEARBY_DEVICES:
            conn.execute(
                """INSERT INTO companion_device
                   (id, name, pet_key, place, online, signal, battery, fw, wifi, last, is_nearby, sort)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (d["id"], d["name"], d["pet_key"], d["place"], int(d.get("online", False)),
                 d["signal"], d.get("battery", 0), d.get("fw", ""), d.get("wifi", "—"),
                 d.get("last", ""), d["is_nearby"], d["sort"]),
            )

    if _table_count(conn, "pet") == 0:
        for p in seed.PETS:
            conn.execute(
                """INSERT INTO pet
                   (pet_key, name, emoji, breed, age, weight, level, growth, mood, active,
                    interact, days, desc, heart_rate, active_minutes, sleep_hours,
                    last_checkup, moments, songs, games, energy, mood_tag, health_status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (p["pet_key"], p["name"], p["emoji"], p["breed"], p["age"], p["weight"],
                 p["level"], p["growth"], p["mood"], p["active"], p["interact"], p["days"],
                 p["desc"], p["heart_rate"], p["active_minutes"], p["sleep_hours"],
                 p["last_checkup"], p["moments"], p["songs"], p["games"],
                 p.get("energy", 0), p.get("mood_tag", ""), p.get("health_status", "")),
            )

    if _table_count(conn, "weather") == 0:
        conn.execute("INSERT INTO weather (id, text, temp, wind) VALUES (1, ?, ?, ?)",
                     (seed.WEATHER["text"], seed.WEATHER["temp"], seed.WEATHER["wind"]))

    if _table_count(conn, "chart_stat") == 0:
        for range_key, payload in seed.CHART.items():
            labels, interacts, onlines = payload["labels"], payload["interact"], payload["online"]
            for idx, label in enumerate(labels):
                conn.execute(
                    """INSERT INTO chart_stat (range_key, label, interact, online, sort)
                       VALUES (?, ?, ?, ?, ?)""",
                    (range_key, label, interacts[idx], onlines[idx], idx + 1),
                )

    if _table_count(conn, "chat_message") == 0:
        for idx, m in enumerate(seed.CHAT_MESSAGES):
            conn.execute(
                """INSERT INTO chat_message (who, text, device_id, created_at, sort)
                   VALUES (?, ?, ?, ?, ?)""",
                (m["who"], m["text"], None, datetime.now().isoformat(timespec="seconds"), idx + 1),
            )

    if _table_count(conn, "bless_item") == 0:
        for idx, b in enumerate(seed.BLESS_LIST):
            conn.execute(
                "INSERT INTO bless_item (text, done, sort) VALUES (?, ?, ?)",
                (b["text"], int(b["done"]), idx + 1),
            )

    if _table_count(conn, "plugin") == 0:
        for p in seed.PLUGINS:
            conn.execute(
                """INSERT INTO plugin (name, icon, color, desc, enabled, sort)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (p["name"], p["icon"], p["color"], p["desc"], p["enabled"], p["sort"]),
            )

    if _table_count(conn, "app_setting") == 0:
        for key, value in seed.SETTINGS.items():
            conn.execute(
                "INSERT INTO app_setting (key, value) VALUES (?, ?)",
                (key, json.dumps(value, ensure_ascii=False)),
            )

    if _table_count(conn, "memory_timeline") == 0:
        for t in seed.TIMELINE:
            conn.execute(
                """INSERT INTO memory_timeline (pet_key, event_date, title, description, sort)
                   VALUES (?, ?, ?, ?, ?)""",
                (None, t["event_date"], t["title"], t["description"], t["sort"]),
            )

    if _table_count(conn, "memory_milestone") == 0:
        for m in seed.MILESTONES:
            conn.execute(
                """INSERT INTO memory_milestone (pet_key, label, value, tail, sort)
                   VALUES (?, ?, ?, ?, ?)""",
                (None, m["label"], m["value"], m["tail"], m["sort"]),
            )

    if _table_count(conn, "gallery_item") == 0:
        for g in seed.GALLERY:
            conn.execute(
                """INSERT INTO gallery_item (pet_key, image_key, image_url, caption, sort)
                   VALUES (?, ?, ?, ?, ?)""",
                (None, g["image_key"], g["image_url"], g["caption"], g["sort"]),
            )

    if _table_count(conn, "notification") == 0:
        for n in seed.NOTIFICATIONS:
            conn.execute(
                """INSERT INTO notification (icon, tone, text, time_ago, read, sort)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (n["icon"], n["tone"], n["text"], n["time_ago"], int(n["read"]), n["sort"]),
            )


def _seed_monitor(conn: sqlite3.Connection) -> None:
    """写入监控域遗留种子数据（仅当表为空时）。"""
    if _table_count(conn, "monitor_device") == 0:
        now = datetime.now().isoformat(timespec="seconds")
        for d in seed.MONITOR_DEVICES:
            conn.execute(
                """INSERT INTO monitor_device
                   (device_name, device_type, sn, online, last_heartbeat, location, create_time)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (d["device_name"], d["device_type"], d["sn"], int(d["online"]),
                 now, d["location"], now),
            )

    if _table_count(conn, "sensor_data") == 0:
        for sn, temp, hum, pir, door, report_time in seed.MONITOR_SENSORS:
            conn.execute(
                """INSERT INTO sensor_data
                   (device_sn, temperature, humidity, pir_triggered, door_closed, report_time)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (sn, temp, hum, int(pir), int(door), report_time),
            )

    if _table_count(conn, "alarm_record") == 0:
        for sn, cam, alarm_type, conf, path, url, handled, desc, alarm_time in seed.MONITOR_ALARMS:
            conn.execute(
                """INSERT INTO alarm_record
                   (device_sn, camera_sn, alarm_type, confidence, image_path, image_url,
                    handled, description, alarm_time, create_time)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (sn, cam, alarm_type, conf, path, url, int(handled), desc, alarm_time, alarm_time),
            )


def init_db() -> None:
    """启动时调用：建表 + 写入种子数据。"""
    # 确保数据库文件所在目录存在
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_db() as conn:
        for ddl in DDL_STATEMENTS:
            conn.execute(ddl)
        _seed_companion(conn)
        _seed_monitor(conn)
        _run_migrations(conn)


# ------------------------------------------------------------
# 轻量迁移：兼容旧版数据库文件（不删数据，只补字段 / 补设置项）
# ------------------------------------------------------------
def _table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    """读取某张表当前已存在的字段名集合。"""
    return {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}


def _run_migrations(conn: sqlite3.Connection) -> None:
    """
    为老版本 petos.db 补齐新增字段与设置项：
    - pet.energy / mood_tag / health_status：状态卡片所需，缺失时 ALTER 并回填种子值；
    - network / device / notify / profile / camera：设置页与设备页所需分组。
    该函数可重复执行，不会覆盖已有数据。
    """
    pet_columns = _table_columns(conn, "pet")
    added_pet_columns = []
    for column, ddl in (
        ("energy", "INTEGER DEFAULT 0"),
        ("mood_tag", "TEXT"),
        ("health_status", "TEXT"),
    ):
        if column not in pet_columns:
            conn.execute(f"ALTER TABLE pet ADD COLUMN {column} {ddl}")
            added_pet_columns.append(column)

    # 仅当本次确实新增了字段时才回填，避免覆盖用户后续修改的数据
    if added_pet_columns:
        for p in seed.PETS:
            conn.execute(
                "UPDATE pet SET energy = ?, mood_tag = ?, health_status = ? WHERE pet_key = ?",
                (p.get("energy", 0), p.get("mood_tag", ""), p.get("health_status", ""), p["pet_key"]),
            )

    # 补齐新增的设置分组（老库只有 voice / screen / music）
    for key in ("network", "device", "notify", "profile", "camera"):
        if get_setting(conn, key, None) is None:
            set_setting(conn, key, seed.SETTINGS[key])


# ------------------------------------------------------------
# 设置项读写小工具（app_setting 表，JSON 值）
# ------------------------------------------------------------
def get_setting(conn: sqlite3.Connection, key: str, default=None):
    """读取一个设置项，不存在时返回 default。"""
    row = conn.execute("SELECT value FROM app_setting WHERE key = ?", (key,)).fetchone()
    if row is None:
        return default
    return json.loads(row["value"])


def set_setting(conn: sqlite3.Connection, key: str, value) -> None:
    """写入/更新一个设置项（存在则覆盖）。"""
    conn.execute(
        """INSERT INTO app_setting (key, value) VALUES (?, ?)
           ON CONFLICT(key) DO UPDATE SET value = excluded.value""",
        (key, json.dumps(value, ensure_ascii=False)),
    )
