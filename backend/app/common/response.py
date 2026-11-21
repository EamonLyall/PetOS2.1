# ============================================================
# 统一响应壳：与旧 SpringBoot 后端 Result 类、前端 README 约定保持一致。
# 所有接口返回固定结构：
#   { "code": 0, "message": "成功", "data": ... }
# code=0 表示成功，其它数字表示失败；前端拦截器按 code 判断是否成功。
# ============================================================

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# 成功 / 失败状态码常量
CODE_SUCCESS = 0
CODE_ERROR = 500


def ok(data=None, message: str = "成功") -> dict:
    """组装成功响应（带业务数据）。"""
    return {"code": CODE_SUCCESS, "message": message, "data": data}


def fail(message: str, code: int = CODE_ERROR, data=None) -> dict:
    """组装失败响应。"""
    return {"code": code, "message": message, "data": data}


class BusinessError(Exception):
    """业务异常：接口里主动抛出（如设备不存在、参数缺失），由全局异常处理器统一转成失败壳。"""

    def __init__(self, message: str, code: int = CODE_ERROR):
        self.message = message
        self.code = code
        super().__init__(message)


def register_exception_handlers(app) -> None:
    """在 FastAPI 应用上注册全局异常处理器，保证任何报错都返回统一响应壳。"""

    @app.exception_handler(BusinessError)
    async def _business_error_handler(_: Request, exc: BusinessError) -> JSONResponse:
        return JSONResponse(status_code=200, content=fail(exc.message, exc.code))

    @app.exception_handler(RequestValidationError)
    async def _validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        """参数校验失败也返回统一响应壳，避免前端拦截器拿到非约定结构。"""
        errors = exc.errors() or []
        detail = "；".join(
            f"{'.'.join(str(x) for x in err.get('loc', []) if x != 'body')}: {err.get('msg', '')}"
            for err in errors
        )
        return JSONResponse(
            status_code=200,
            content=fail(f"请求参数校验失败：{detail or '请检查请求体'}", 400),
        )

    @app.exception_handler(Exception)
    async def _unhandled_error_handler(_: Request, exc: Exception) -> JSONResponse:
        # 未预期异常：记录到服务端日志，前端只拿到友好提示，不暴露堆栈
        return JSONResponse(status_code=200, content=fail(f"服务器内部错误：{exc}"))
