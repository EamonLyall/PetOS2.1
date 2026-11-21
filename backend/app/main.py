# ============================================================
# PetOS 后端主入口（FastAPI）。
#
# 启动方式（backend 目录下）：
#   python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
#
# 启动后：
#   - 接口文档（Swagger）：http://localhost:8080/docs
#   - 健康检查：         http://localhost:8080/api/health
#   - 抓拍图片访问：     http://localhost:8080/images/xxx.jpg
# ============================================================

import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .database import init_db, get_db
from .common.response import register_exception_handlers, ok
from .routers import companion, monitor

# 读取全局配置
settings = get_settings()


# ------------------------------------------------------------
# 应用生命周期：启动时建表 / 灌种子 / 建图片目录，关闭时无需额外清理
# 说明：FastAPI 新版本推荐 lifespan 代替已弃用的 @app.on_event("startup")，
#       行为与原实现完全一致，避免启动时出现 DeprecationWarning。
# ------------------------------------------------------------
@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    print("=" * 60)
    print("PetOS 后端启动成功，接口地址 http://localhost:%d" % settings.app_port)
    print(f"数据库：{settings.database_url}")
    print(f"大模型代理：{'已启用' if settings.llm_enabled else '未配置，使用兜底话术'}")
    print(f"MQTT：{'已启用' if settings.mqtt_enabled else '未配置，演示模式不下发 Broker'}")
    print("=" * 60)
    yield


# 创建 FastAPI 应用实例
app = FastAPI(
    title="PetOS AI Companion 后端",
    description="宠物陪伴前端 + ESP32/香橙派硬件监控的一体化后端（FastAPI + SQLite）",
    version="2.1.0",
    lifespan=lifespan,
)

# ------------------------------------------------------------
# 跨域配置：开发期允许前端 Vite 地址访问；生产可在 .env 收紧 CORS_ORIGINS
# ------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------
# 请求日志中间件：为每个请求生成 X-Request-ID，并打印方法/路径/状态码/耗时。
# 答辩演示时可在后端控制台直接看到前端每次点击触发的接口链路。
# ------------------------------------------------------------
@app.middleware("http")
async def request_logger(request: Request, call_next):
    request_id = uuid.uuid4().hex[:8]
    started = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - started) * 1000
    response.headers["X-Request-ID"] = request_id
    # 静态图片请求量较大且无排查价值，日志里跳过，保持控制台干净
    if not request.url.path.startswith("/images"):
        print(f"[API] {request_id} {request.method} {request.url.path} "
              f"-> {response.status_code} {elapsed_ms:.1f}ms")
    return response


# 注册全局异常处理器（统一返回 {code, message, data} 响应壳）
register_exception_handlers(app)


# 抓拍图片静态目录：前端 <img src="/images/xxx.jpg"> 直接访问
app.mount("/images", StaticFiles(directory=str(settings.upload_dir)), name="images")

# 注册业务路由
app.include_router(companion.router)
app.include_router(monitor.router)


@app.get("/api/health", summary="健康检查")
def health():
    """供前端/部署探针检查后端是否存活，并顺带验证数据库连接可用。"""
    db_ok = True
    try:
        with get_db() as conn:
            conn.execute("SELECT 1").fetchone()
    except Exception:  # 数据库异常时仍返回结构化状态，方便部署探针判断
        db_ok = False
    return ok({
        "status": "up" if db_ok else "degraded",
        "service": "petos-backend",
        "version": "2.1.0",
        "database": "ok" if db_ok else "error",
    })
