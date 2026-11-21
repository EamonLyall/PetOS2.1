# ============================================================
# 配置模块：负责读取 .env 文件与系统环境变量，集中暴露给全后端使用。
# 设计说明：
#   - 不引入 python-dotenv 依赖，这里手写一个极简 .env 解析器，保证零额外安装；
#   - 系统环境变量优先级高于 .env 文件（方便部署时用容器环境变量覆盖）；
#   - 外部服务（MQTT / 大模型）地址与密钥留空时，后端进入演示兜底模式，
#     不会因为连不上外部服务而启动失败。
# ============================================================

import os
from pathlib import Path

# 后端工程根目录（app/config.py 向上两级即为 backend/）
BASE_DIR = Path(__file__).resolve().parent.parent


def _load_env_file() -> None:
    """读取后端根目录下的 .env 文件，把键值对注入 os.environ（已存在的系统变量不覆盖）。"""
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        # 跳过空行与注释行
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        # 系统环境变量优先：只有当前不存在时才写入
        if key and key not in os.environ:
            os.environ[key] = value


# 模块导入时立即加载 .env
_load_env_file()


def _get_bool(name: str, default: bool = False) -> bool:
    """把环境变量解析成布尔值（支持 true/1/yes/on）。"""
    return os.environ.get(name, "").lower() in ("1", "true", "yes", "on")


class Settings:
    """全局配置对象：在 main.py 启动时实例化一次，各处通过 get_settings() 取用。"""

    def __init__(self) -> None:
        # ---------- 服务基础 ----------
        self.app_port: int = int(os.environ.get("APP_PORT", "8080"))
        # 跨域来源：逗号分隔的字符串拆成列表
        self.cors_origins: list[str] = [
            origin.strip()
            for origin in os.environ.get(
                "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
            ).split(",")
            if origin.strip()
        ]

        # ---------- 数据库 ----------
        # 默认 sqlite:///./petos.db；MySQL 连接串预留，当前版本先以 SQLite 落地
        self.database_url: str = os.environ.get("DATABASE_URL", "sqlite:///./petos.db")

        # ---------- MQTT（预留，可留空） ----------
        self.mqtt_host: str = os.environ.get("MQTT_HOST", "").strip()
        self.mqtt_port: int = int(os.environ.get("MQTT_PORT", "1883"))
        self.mqtt_username: str = os.environ.get("MQTT_USERNAME", "").strip()
        self.mqtt_password: str = os.environ.get("MQTT_PASSWORD", "").strip()
        self.mqtt_client_id: str = os.environ.get("MQTT_CLIENT_ID", "petos-backend-server")

        # ---------- 大模型（预留，可留空） ----------
        self.llm_base_url: str = os.environ.get("LLM_BASE_URL", "").strip().rstrip("/")
        self.llm_api_key: str = os.environ.get("LLM_API_KEY", "").strip()
        self.llm_model: str = os.environ.get("LLM_MODEL", "petos-assistant")

        # ---------- 文件存储 ----------
        self.upload_dir: Path = BASE_DIR / os.environ.get("UPLOAD_DIR", "./upload-images")

    @property
    def mqtt_enabled(self) -> bool:
        """是否启用 MQTT：配置了 Broker 地址才算启用。"""
        return bool(self.mqtt_host)

    @property
    def llm_enabled(self) -> bool:
        """是否启用真实大模型：同时配置了地址和密钥才算启用。"""
        return bool(self.llm_base_url and self.llm_api_key)


# 全局单例配置
_settings: Settings | None = None


def get_settings() -> Settings:
    """获取全局配置单例（懒加载，便于测试时替换）。"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
