# ============================================================
# MQTT 通信服务（预留层）。
#
# 职责：
#   - 作为后端与 ESP32 / 香橙派之间的消息总线，下行控制指令（音量/屏幕/云台/喂食）
#     与上行遥测、告警都通过 MQTT 主题收发；
#   - 当前版本默认不连接 Broker（MQTT_HOST 留空），publish 仅打印日志/落库，
#     保证后端在没有 EMQX 的环境下也能正常启动并联调前端；
#   - 接入真实 Broker 时：在 .env 填写 MQTT_HOST 等信息，并 pip 安装 paho-mqtt，
#     本模块会自动启用真实连接（import 做了容错，未安装也不报错）。
#
# 主题规划与前端 docs/integration.md 保持一致：
#   petos/{deviceId}/telemetry | status | camera/motion | voice/up   （上行）
#   petos/{deviceId}/control/volume | tts | screen | servo | music | feed （下行）
# ============================================================

import json
from ..config import get_settings

# 主题常量（三端统一，勿随意改名）
TOPIC_TELEMETRY = "petos/{device_id}/telemetry"
TOPIC_STATUS = "petos/{device_id}/status"
TOPIC_CONTROL = "petos/{device_id}/control/{action}"


class MqttService:
    """MQTT 客户端封装：未启用时所有方法为空操作，启用后委托给 paho-mqtt。"""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._client = None  # paho-mqtt 客户端实例（懒加载）
        self._connect()

    def _connect(self) -> None:
        """根据配置尝试连接 Broker；未配置或缺依赖时保持禁用状态。"""
        if not self.settings.mqtt_enabled:
            print("[MQTT] 未配置 MQTT_HOST，进入演示模式，指令不下发 Broker。")
            return

        try:
            # 延迟导入：未安装 paho-mqtt 时不影响后端启动
            import paho.mqtt.client as mqtt  # type: ignore
        except ImportError:
            print("[MQTT] 未安装 paho-mqtt，跳过真实连接（pip install paho-mqtt 后可用）。")
            return

        client = mqtt.Client(client_id=self.settings.mqtt_client_id)
        if self.settings.mqtt_username:
            client.username_pw_set(self.settings.mqtt_username, self.settings.mqtt_password)
        try:
            client.connect(self.settings.mqtt_host, self.settings.mqtt_port, keepalive=30)
            client.loop_start()
            self._client = client
            print(f"[MQTT] 已连接 Broker {self.settings.mqtt_host}:{self.settings.mqtt_port}")
        except OSError as exc:
            # Broker 暂时连不上不阻断后端启动，后续可扩展定时重连
            print(f"[MQTT] Broker 连接失败，进入离线模式：{exc}")
            self._client = None

    def publish(self, device_id: str, action: str, payload: dict) -> None:
        """
        发布下行控制指令到对应主题（陪伴域 petos/{deviceId}/control/{action}）。

        :param device_id: 设备 ID（如 d-nuomi）
        :param action: 控制动作（volume/tts/screen/servo/music/feed…）
        :param payload: 指令内容字典，会序列化为 JSON
        """
        topic = TOPIC_CONTROL.format(device_id=device_id, action=action)
        self.publish_raw(topic, payload)

    def publish_raw(self, topic: str, payload: dict) -> None:
        """
        按完整主题发布消息（监控域旧主题 monitor/... 使用）。

        :param topic: 完整 MQTT 主题
        :param payload: 指令内容字典，会序列化为 JSON
        """
        message = json.dumps(payload, ensure_ascii=False)

        if self._client is not None:
            self._client.publish(topic, message, qos=1)
            print(f"[MQTT] 已下发 {topic} -> {message}")
        else:
            # 演示模式：只打印，便于答辩时讲解“指令原本会走到哪台设备”
            print(f"[MQTT][演示模式] 应下发 {topic} -> {message}")


# 全局单例
_mqtt_service: MqttService | None = None


def get_mqtt_service() -> MqttService:
    """获取 MQTT 服务单例。"""
    global _mqtt_service
    if _mqtt_service is None:
        _mqtt_service = MqttService()
    return _mqtt_service
