# -*- coding: utf-8 -*-
# 联调自检脚本：逐个请求后端接口，校验返回壳与关键字段是否与前端 mock 一致。
# 用法：后端启动后，在 backend 目录执行  python scripts/verify_api.py
import json
import urllib.request

BASE = "http://127.0.0.1:8080"


def get(path):
    with urllib.request.urlopen(BASE + path, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def post(path, payload):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def put(path, payload=None):
    data = json.dumps(payload or {}).encode("utf-8") if payload is not None else b"{}"
    req = urllib.request.Request(
        BASE + path, data=data, headers={"Content-Type": "application/json"}, method="PUT"
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


failures = []


def check(name, cond, detail=""):
    print(("PASS" if cond else "FAIL"), name, detail)
    if not cond:
        failures.append(name)


# 1. 健康检查
h = get("/api/health")
check("health 响应壳", h["code"] == 0 and h["data"]["status"] == "up")
check("health 数据库可用", h["data"].get("database") == "ok", str(h["data"].get("database")))

# 1.1 导航配置
nav = get("/api/nav")["data"]
check("导航项=8", len(nav) == 8, str(len(nav)))
check("导航含守护预警页", any(x["key"] == "alerts" for x in nav))
check("导航含设置页", any(x["key"] == "settings" for x in nav))

# 2. 全量快照
s = get("/api/state")["data"]
check("state 设备数=3", len(s["devices"]) == 3, str(len(s["devices"])))
check("state 附近设备数=2", len(s["nearby"]) == 2, str(len(s["nearby"])))
check("state 宠物数=5", len(s["pets"]) == 5, str(len(s["pets"])))
check("state 含天气", s["weather"] == {"text": "晴", "temp": 26, "wind": "微风"})
check("state 图表三区间", set(s["charts"].keys()) == {"week", "month", "quarter"})
check("state 聊天记录=3", len(s["chatMessages"]) == 3)
check("state 打卡=3", len(s["blessList"]) == 3)
check("state 插件=8", len(s["plugins"]) == 8)
check("state 时间线=4", len(s["timeline"]) == 4)
check("state 照片墙=4", len(s["gallery"]) == 4)
check("state 含通知", len(s["notifications"]) >= 1 and "unreadCount" in s)
check("state 含守护预警", isinstance(s.get("alerts"), list) and "openAlertCount" in s)
# 设置分组完整性：设置页与设备页的所有开关都由这些分组驱动
for group in ("voice", "screen", "music", "network", "device", "notify", "profile", "camera"):
    check(f"state 设置分组 {group}", isinstance(s["settings"].get(group), dict))

# 3. 设备列表字段对齐前端
d0 = s["devices"][0]
check("设备字段 petKey", d0["petKey"] == "nuomi")
check("设备字段 signal/battery", d0["signal"] == 92 and d0["battery"] == 78)

# 4. 宠物档案
p = get("/api/pets/nuomi/profile")["data"]
check("宠物档案名", p["name"] == "糯米")
check("宠物成长值", p["growth"] == 68 and p["level"] == 3)
check("宠物健康字段", p["heartRate"] == 132 and p["sleepHours"] == 11.5)

# 5. 趋势统计
st = get("/api/pets/nuomi/stats?range=week")["data"]
check("周趋势标签=7", len(st["labels"]) == 7)
check("周趋势互动首项", st["interact"][0] == 58)
stm = get("/api/pets/nuomi/stats?range=month")["data"]
check("月趋势标签=5", len(stm["labels"]) == 5)

# 6. 时间线占位符替换
tl = get("/api/pets/nuomi/timeline")["data"]
check("时间线首条替换 LV.3", "LV.3" in tl[0]["title"], tl[0]["title"])

# 7. 里程碑
ms = get("/api/pets/nuomi/milestones")["data"]
check("里程碑天数替换", "128 天" in ms[3]["value"], ms[3]["value"])

# 8. 插件开关
pl = get("/api/plugins")["data"]
check("插件初始启用=4", sum(1 for x in pl if x["enabled"]) == 4)
t = put("/api/plugins/5/toggle")["data"]
check("插件5切换为启用", t["enabled"] is True)
put("/api/plugins/5/toggle")  # 还原

# 9. 打卡切换
bl = get("/api/bless")["data"]
check("打卡首项已完成", bl[0]["done"] is True)
tb = put("/api/bless/2/toggle")["data"]
check("打卡第2项切换完成", tb["done"] is True)
put("/api/bless/2/toggle")  # 还原

# 10. 聊天（兜底模式）
c = post("/api/chat", {"text": "你好呀", "deviceId": "d-nuomi"})
check("聊天返回 reply", bool(c["data"]["reply"]), c["data"]["reply"])
msgs = get("/api/chat/messages")["data"]
check("聊天记录新增2条", len(msgs) == 5, str(len(msgs)))

# 11. 连接/断开附近设备
conn = post("/api/devices/d-xiaobai/connect", {})["data"]
check("附近设备配对成功", conn["device"]["petKey"] == "xiaobai" and conn["device"]["online"])
near = get("/api/devices/nearby")["data"]
check("配对后附近剩1台", len(near) == 1, str(len(near)))
disc = post("/api/devices/d-xiaobai/disconnect", {})["data"]
check("断开连接", disc["connected"] is False)
# 还原：把小白移回附近
import os
import sqlite3
from pathlib import Path
db_url = os.environ.get("DATABASE_URL", "sqlite:///./petos.db")
db = Path(db_url.replace("sqlite:///", "", 1)) if db_url.startswith("sqlite:///") else Path("petos.db")
if not db.is_absolute():
    db = Path(__file__).resolve().parent.parent / db
con = sqlite3.connect(db)
con.execute("UPDATE companion_device SET is_nearby = 1 WHERE id = 'd-xiaobai'")
con.execute("UPDATE app_setting SET value = 'true' WHERE key = 'connected'")
con.execute("UPDATE app_setting SET value = '\"d-nuomi\"' WHERE key = 'active_device_id'")
con.commit(); con.close()

# 12. 快速互动：互动次数 +1 落库，并返回最新宠物档案
before = get("/api/pets/nuomi/profile")["data"]
inter = post("/api/pets/nuomi/interact", {"action": "pet"})["data"]
check("互动次数+1", inter["pet"]["interact"] == before["interact"] + 1,
      f'{before["interact"]} -> {inter["pet"]["interact"]}')
check("互动返回话术", bool(inter["message"]), inter["message"])

# 13. 设置分组读写（蓝牙开关，测试后还原）
st1 = put("/api/settings", {"network": {"bluetooth": False}})["data"]
check("设置写入 bluetooth", st1["network"]["bluetooth"] is False)
st2 = put("/api/settings", {"network": {"bluetooth": True}})["data"]
check("设置还原 bluetooth", st2["network"]["bluetooth"] is True)

# 14. 通知中心：列表 + 全部已读
nf = get("/api/notifications")["data"]
check("通知列表非空", len(nf["notifications"]) >= 1)
check("未读数字段", "unreadCount" in nf)
nf2 = put("/api/notifications/read")["data"]
check("全部已读后未读=0", nf2["unreadCount"] == 0)

# 15. 监控域遗留接口
dev = get("/api/monitor/devices")["data"]
check("监控设备=2", len(dev) == 2)
sen = get("/api/sensors/esp32-s3-001/recent")["data"]
check("传感器最近20条内有数据", len(sen) > 0)
alm = get("/api/alarms/recent")["data"]
check("告警最近10条", len(alm) > 0)
dash = get("/api/dashboard/stats")["data"]
check("大屏统计设备总数", dash["deviceTotal"] == 2)

# 清理：删除自检产生的 2 条聊天与互动增量，恢复未读状态，保证可重复执行
con = sqlite3.connect(db)
con.execute("DELETE FROM chat_message WHERE id IN (SELECT id FROM chat_message ORDER BY sort DESC, id DESC LIMIT 2)")
con.execute("UPDATE pet SET interact = ?, growth = ? WHERE pet_key = 'nuomi'",
            (before["interact"], before["growth"]))
con.execute("UPDATE notification SET read = 0 WHERE sort <= 2")
con.commit(); con.close()

print("\n结果：", "全部通过 ✅" if not failures else f"失败 {len(failures)} 项：{failures}")
