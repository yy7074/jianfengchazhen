"""
优化的IP拦截中间件 - 减少日志、使用Redis缓存
"""
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from services.ip_service_optimized import IPServiceOptimized
from database import get_db
import logging
import time

logger = logging.getLogger(__name__)


class OptimizedIPBlockMiddleware(BaseHTTPMiddleware):
    """优化的IP黑名单拦截中间件"""

    # 白名单路径（不检查IP）
    WHITELIST_PATHS = ["/health", "/docs", "/openapi.json", "/redoc"]

    # 记录已拦截IP的本地缓存（避免重复记录日志）
    _blocked_cache = {}  # {ip: last_log_time}
    _cache_ttl = 60  # 60秒内不重复记录同一IP的拦截日志

    def __init__(self, app, **options):
        super().__init__(app)
        self.silent_mode = options.get('silent_mode', True)  # 静默模式，不记录日志

    async def dispatch(self, request: Request, call_next):
        # 白名单路径直接放行
        path = request.url.path
        if any(path.startswith(p) for p in self.WHITELIST_PATHS):
            return await call_next(request)

        # 管理后台路径放行
        if path.startswith("/vfjsadrhbadmin"):
            return await call_next(request)

        # 获取客户端IP
        client_ip = self._get_client_ip(request)

        if client_ip:
            # 使用优化的快速检查（纯Redis）
            if IPServiceOptimized.is_ip_blocked_fast(client_ip):
                # 静默拦截（减少日志记录）
                should_log = self._should_log_blocked_ip(client_ip)

                if should_log:
                    logger.warning(f"🚫 已拦截被封禁的IP: {client_ip} ({path})")

                # 直接返回403，不记录详细日志
                return JSONResponse(
                    status_code=403,
                    content={
                        "code": 403,
                        "message": "Access denied",
                        "data": None
                    }
                )

        return await call_next(request)

    def _get_client_ip(self, request: Request) -> str:
        """获取客户端真实IP"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "unknown"

    def _should_log_blocked_ip(self, ip: str) -> bool:
        """判断是否应该记录拦截日志（避免重复记录）"""
        now = time.time()
        last_log_time = self._blocked_cache.get(ip, 0)

        # 如果距离上次记录超过TTL，则记录
        if now - last_log_time > self._cache_ttl:
            self._blocked_cache[ip] = now
            # 清理过期缓存
            self._cleanup_cache(now)
            return True

        return False

    def _cleanup_cache(self, now: float):
        """清理过期的缓存"""
        if len(self._blocked_cache) > 1000:  # 缓存过大时清理
            self._blocked_cache = {
                ip: t for ip, t in self._blocked_cache.items()
                if now - t < self._cache_ttl * 2
            }
