# ============================================================
# 大模型对话代理服务（预留层）。
#
# 职责：
#   - 前端只调用自己后端的 /api/chat，由后端携带 API Key 请求第三方模型；
#   - 密钥永远不出现在前端代码与浏览器请求中（安全原则）；
#   - 未配置 LLM_BASE_URL / LLM_API_KEY，或模型调用失败时，
#     自动回退到内置兜底话术，保证演示不中断（与前端原有兜底行为一致）。
#
# 对接的模型协议：OpenAI 兼容的 /chat/completions（DeepSeek / 通义 / 豆包 / Kimi 等均可）。
# 当前版本用 Python 标准库 urllib 发 HTTP 请求，不额外引入 httpx/requests 依赖。
# ============================================================

import json
import random
import urllib.request
import urllib.error

from .. import seed
from ..config import get_settings

# 系统提示词：定义“小宠”的人设，可按答辩需要调整
SYSTEM_PROMPT = (
    "你是 PetOS 智能宠物陪伴助手，扮演一只黏人、可爱、会陪主人聊天的小宠物。"
    "回答简短亲切，带少量 emoji，语气活泼，每次回复不超过 50 个字。"
)


def _build_messages(history: list[dict], user_text: str) -> list[dict]:
    """
    把前端传来的聊天记录转换成 OpenAI 兼容的 messages 格式。
    前端记录形如 {who: 'me'|'pet', text: '...'}，这里映射成 user / assistant 角色。
    """
    messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
    for item in history or []:
        role = "user" if item.get("who") == "me" else "assistant"
        content = item.get("text", "")
        if content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_text})
    return messages


def _call_openai_compatible(messages: list[dict]) -> str:
    """
    真实调用大模型（OpenAI 兼容协议）。
    任何网络/解析异常都向上抛出，由上层决定是否回退兜底话术。
    """
    settings = get_settings()
    url = f"{settings.llm_base_url}/chat/completions"
    payload = {
        "model": settings.llm_model,
        "messages": messages,
        "temperature": 0.8,
        "stream": False,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.llm_api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    # 取首条回复的文本内容
    return body["choices"][0]["message"]["content"].strip()


def chat(history: list[dict], user_text: str, device_id: str | None = None) -> str:
    """
    对外主方法：根据上下文生成小宠回复。

    :param history: 最近聊天记录 [{who, text}, ...]
    :param user_text: 本次主人发送的文本
    :param device_id: 当前设备 ID（预留：可按宠物人设区分回复风格）
    :return: 回复文本
    """
    settings = get_settings()

    # 已配置大模型：尝试真实调用；失败则回退兜底
    if settings.llm_enabled:
        try:
            messages = _build_messages(history, user_text)
            return _call_openai_compatible(messages)
        except (urllib.error.URLError, urllib.error.HTTPError, KeyError, TimeoutError, OSError) as exc:
            # 模型服务不可用时不打断演示，记录原因后走兜底
            print(f"[LLM] 大模型调用失败，使用兜底回复：{exc}")

    # 兜底模式：从内置话术里随机挑一条（与前端原 CHAT_REPLIES 一致）
    return random.choice(seed.CHAT_REPLIES)
