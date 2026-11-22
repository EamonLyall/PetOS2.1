"""轻量情绪风险识别与守护预警。

这是可解释的关键词规则，不作医学诊断。高危表达立即提醒；持续低落必须
跨越至少一轮小宠回复后仍未缓解才生成预警，避免单次负面情绪造成误报。
"""

import json
from datetime import datetime

SELF_HARM_TERMS = (
    "自杀", "想死", "不想活", "活不下去", "结束生命", "结束自己", "轻生",
    "自残", "割腕", "伤害自己", "杀了自己", "一了百了", "跳下去算了",
)
HARM_OTHERS_TERMS = ("想杀人", "伤害别人", "报复社会", "同归于尽")
LOW_MOOD_TERMS = (
    "难过", "伤心", "沮丧", "失落", "抑郁", "焦虑", "孤独", "没人理解我",
    "没意思", "很空虚", "压力好大", "撑不住", "崩溃了", "想哭", "不开心",
    "很痛苦", "讨厌自己", "我没用", "不被喜欢", "被排挤", "被欺负", "活着好累",
)
RECOVERY_TERMS = (
    "好多了", "没事了", "缓解了", "现在开心了", "不难过了", "想开了",
    "已经好了", "我很好", "很开心", "解决了", "恢复过来了",
)
NEGATED_CRITICAL = ("没有想死", "不是想死", "没想过自杀", "不会自杀", "没有自杀")

EMERGENCY_GUIDANCE = (
    "请立即告诉家长、老师或其他可信任的大人，并远离可能伤害自己或他人的物品。"
    "若正处于危险中，请马上拨打 120/110；也可拨打 12356 心理援助热线（以当地开通情况为准）。"
)


def _contains(text: str, terms: tuple[str, ...]) -> bool:
    normalized = "".join((text or "").lower().split())
    return any(term in normalized for term in terms)


def _base_risk() -> dict:
    return {
        "level": "none", "category": "none", "summary": "",
        "guidance": "", "reply": "", "evidence": [],
    }


def assess_risk(history: list[dict], text: str) -> dict:
    """结合本次消息和数据库中的此前对话评估风险。"""
    risk = _base_risk()
    critical_text = text or ""
    for phrase in NEGATED_CRITICAL:
        critical_text = critical_text.replace(phrase, "")

    if _contains(critical_text, SELF_HARM_TERMS):
        risk.update({
            "level": "critical", "category": "self_harm",
            "summary": "检测到可能的自伤或轻生表达，需要家长立即关注",
            "guidance": EMERGENCY_GUIDANCE,
            "reply": "听到你这样说，我很担心你。请不要独自承受，现在就去找家长、老师或其他可信任的大人陪着你。" + EMERGENCY_GUIDANCE,
            "evidence": [text[:160]],
        })
        return risk

    if _contains(critical_text, HARM_OTHERS_TERMS):
        risk.update({
            "level": "critical", "category": "harm_others",
            "summary": "检测到可能伤害他人的高危表达，需要家长立即关注",
            "guidance": EMERGENCY_GUIDANCE,
            "reply": "我很担心你现在的状态。请先离开可能发生冲突的现场，并马上联系可信任的大人陪着你。" + EMERGENCY_GUIDANCE,
            "evidence": [text[:160]],
        })
        return risk

    if _contains(text, RECOVERY_TERMS) or not _contains(text, LOW_MOOD_TERMS):
        return risk

    # 只检查最近一位用户的上一条表达，且中间必须有一轮小宠回复。
    previous_text = ""
    reply_between = False
    for item in reversed((history or [])[-16:]):
        if item.get("who") == "pet":
            reply_between = True
        elif item.get("who") == "me":
            previous_text = item.get("text", "")
            break

    persistent = bool(
        previous_text and reply_between
        and _contains(previous_text, LOW_MOOD_TERMS)
        and not _contains(previous_text, RECOVERY_TERMS)
    )
    if persistent:
        risk.update({
            "level": "warning", "category": "low_mood",
            "summary": "连续两轮表达情绪低落，陪伴后仍未明显缓解",
            "guidance": "建议家长尽快以平和、不评判的方式主动沟通，了解近期压力与睡眠状况；若持续恶化，请寻求学校心理老师或专业心理服务支持。",
            "reply": "我仍然有些担心你。我们可以继续慢慢聊，也请不要独自扛着，可以告诉家长、老师或其他可信任的大人你现在的感受。你现在最难受的是什么？",
            "evidence": [previous_text[:160], text[:160]],
        })
    else:
        risk.update({
            "level": "watch", "category": "low_mood",
            "summary": "检测到情绪低落信号，先由小宠陪伴观察",
            "reply": "听起来你现在有些难受，我愿意听你说。发生什么事了？不用急着组织语言，我们可以慢慢来。",
            "evidence": [text[:160]],
        })
    return risk


def alert_dict(row) -> dict:
    return {
        "id": row["id"], "deviceId": row["device_id"], "level": row["level"],
        "category": row["category"], "status": row["status"], "summary": row["summary"],
        "evidence": json.loads(row["evidence"] or "[]"), "guidance": row["guidance"],
        "createdAt": row["created_at"], "updatedAt": row["updated_at"],
        "handledAt": row["handled_at"], "handleNote": row["handle_note"] or "",
    }


def save_alert(conn, device_id: str | None, risk: dict) -> dict | None:
    """新建预警，或更新同一设备的未处理预警，避免重复轰炸。"""
    if risk["level"] not in ("warning", "critical"):
        return None
    now = datetime.now().isoformat(timespec="seconds")
    row = conn.execute(
        """SELECT * FROM emotion_alert
           WHERE COALESCE(device_id, '') = COALESCE(?, '') AND status != 'resolved'
           ORDER BY id DESC LIMIT 1""",
        (device_id,),
    ).fetchone()
    if row:
        keep_critical = row["level"] == "critical" and risk["level"] != "critical"
        level = "critical" if keep_critical else risk["level"]
        summary = row["summary"] if keep_critical else risk["summary"]
        guidance = row["guidance"] if keep_critical else risk["guidance"]
        evidence = row["evidence"] if keep_critical else json.dumps(risk["evidence"], ensure_ascii=False)
        conn.execute(
            """UPDATE emotion_alert SET level = ?, category = ?, summary = ?, evidence = ?,
               guidance = ?, updated_at = ? WHERE id = ?""",
            (level, row["category"] if keep_critical else risk["category"], summary,
             evidence, guidance, now, row["id"]),
        )
        if row["level"] != level:
            conn.execute(
                """INSERT INTO notification (icon, tone, text, time_ago, read, sort)
                   SELECT 'health', 'amber', '守护预警已升级为紧急，请立即查看', '刚刚', 0,
                          COALESCE(MAX(sort), 0) + 1 FROM notification"""
            )
    else:
        conn.execute(
            """INSERT INTO emotion_alert
               (device_id, level, category, status, summary, evidence, guidance, created_at, updated_at)
               VALUES (?, ?, ?, 'pending', ?, ?, ?, ?, ?)""",
            (device_id, risk["level"], risk["category"], risk["summary"],
             json.dumps(risk["evidence"], ensure_ascii=False), risk["guidance"], now, now),
        )
        alert_id = conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
        conn.execute(
            """INSERT INTO notification (icon, tone, text, time_ago, read, sort)
               SELECT 'health', 'amber', ?, '刚刚', 0, COALESCE(MAX(sort), 0) + 1
               FROM notification""",
            ("紧急守护预警，请家长立即查看" if risk["level"] == "critical"
             else "新的情绪守护预警，请家长关注",),
        )
        row = conn.execute("SELECT * FROM emotion_alert WHERE id = ?", (alert_id,)).fetchone()
        return alert_dict(row)
    row = conn.execute("SELECT * FROM emotion_alert WHERE id = ?", (row["id"],)).fetchone()
    return alert_dict(row)
