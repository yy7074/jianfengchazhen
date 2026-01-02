"""
速率限制中间件 - 防止恶意批量请求
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from database import redis_client
from datetime import datetime, timedelta
import time

class RateLimitMiddleware(BaseHTTPMiddleware):
    """速率限制中间件"""

    def __init__(self, app, **options):
        super().__init__(app)
        # 速率限制配置
        self.limits = options.get('limits', {
            'register': {'requests': 5, 'window': 3600},      # 注册: 1小时5次
            'login': {'requests': 10, 'window': 60},          # 登录: 1分钟10次
            'ad_watch': {'requests': 100, 'window': 3600},    # 观看广告: 1小时100次
            'default': {'requests': 60, 'window': 60}         # 默认: 1分钟60次
        })

    async def dispatch(self, request: Request, call_next):
        # 获取客户端IP
        client_ip = self.get_client_ip(request)

        # 检查速率限制
        if not self.check_rate_limit(request, client_ip):
            raise HTTPException(
                status_code=429,
                detail={
                    "code": 429,
                    "message": "请求过于频繁，请稍后再试",
                    "data": {
                        "ip": client_ip,
                        "retry_after": "60秒"
                    }
                }
            )

        # 继续处理请求
        response = await call_next(request)
        return response

    def get_client_ip(self, request: Request) -> str:
        """获取客户端IP"""
        # 检查X-Forwarded-For头（代理情况）
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        # 检查X-Real-IP头
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # 返回直接连接IP
        return request.client.host if request.client else "unknown"

    def get_limit_config(self, request: Request) -> dict:
        """根据路径获取限制配置"""
        path = request.url.path

        # 注册接口
        if '/register' in path or '/user/register' in path:
            return self.limits['register']

        # 登录接口
        if '/login' in path:
            return self.limits['login']

        # 广告接口
        if '/ad/' in path:
            return self.limits['ad_watch']

        # 默认限制
        return self.limits['default']

    def check_rate_limit(self, request: Request, client_ip: str) -> bool:
        """检查速率限制"""
        try:
            # 获取限制配置
            config = self.get_limit_config(request)
            max_requests = config['requests']
            window = config['window']

            # Redis键
            path_key = request.url.path.replace('/', '_')
            redis_key = f"rate_limit:{client_ip}:{path_key}"

            # 获取当前计数
            current = redis_client.get(redis_key)

            if current is None:
                # 第一次请求，设置计数和过期时间
                redis_client.setex(redis_key, window, 1)
                return True
            else:
                current_count = int(current)

                if current_count >= max_requests:
                    # 超过限制
                    return False
                else:
                    # 增加计数
                    redis_client.incr(redis_key)
                    return True

        except Exception as e:
            # Redis出错时不阻止请求（优雅降级）
            print(f"Rate limit check error: {e}")
            return True

# 创建便捷的限制检查函数
def check_ip_rate_limit(ip: str, action: str, max_requests: int = 60, window: int = 60) -> bool:
    """
    检查IP速率限制

    Args:
        ip: IP地址
        action: 操作类型
        max_requests: 最大请求数
        window: 时间窗口（秒）

    Returns:
        是否允许请求
    """
    try:
        redis_key = f"rate_limit:{ip}:{action}"
        current = redis_client.get(redis_key)

        if current is None:
            redis_client.setex(redis_key, window, 1)
            return True
        else:
            current_count = int(current)
            if current_count >= max_requests:
                return False
            else:
                redis_client.incr(redis_key)
                return True

    except Exception:
        return True  # 优雅降级
