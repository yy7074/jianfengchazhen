"""
增强防护中间件 - 多层严格防护
包括：速率限制、请求间隔检查、自动封禁
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from database import redis_client, get_db
from services.ip_service_optimized import IPServiceOptimized
from datetime import datetime
import time
import logging

logger = logging.getLogger(__name__)


class EnhancedProtectionMiddleware(BaseHTTPMiddleware):
    """增强防护中间件 - 严格模式"""

    # 白名单路径（不检查）
    WHITELIST_PATHS = ["/health", "/docs", "/openapi.json", "/redoc"]

    def __init__(self, app, **options):
        super().__init__(app)

        # 严格速率限制配置
        self.limits = {
            'register': {'requests': 2, 'window': 3600},      # 注册: 1小时2次（极严格）
            'login': {'requests': 5, 'window': 60},           # 登录: 1分钟5次
            'ad_watch': {'requests': 30, 'window': 3600},     # 看广告: 1小时30次
            'ad_random': {'requests': 50, 'window': 3600},    # 获取广告: 1小时50次
            'default': {'requests': 20, 'window': 60}         # 默认: 1分钟20次
        }

        # 请求间隔配置（秒）
        self.min_intervals = {
            'register': 300,      # 注册间隔：5分钟
            'ad_watch': 3,        # 看广告间隔：3秒
            'ad_random': 2,       # 获取广告间隔：2秒
            'default': 1          # 默认间隔：1秒
        }

        # 自动封禁配置
        self.auto_ban = {
            'violation_threshold': 5,      # 违规5次自动封禁
            'violation_window': 600,       # 10分钟内的违规
            'ban_duration': 86400          # 封禁24小时
        }

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # 白名单路径放行
        if any(path.startswith(p) for p in self.WHITELIST_PATHS):
            return await call_next(request)

        # 管理后台放行
        if path.startswith("/vfjsadrhbadmin"):
            return await call_next(request)

        # 获取客户端IP
        client_ip = self._get_client_ip(request)

        # 1. 检查IP黑名单（优先级最高）
        if IPServiceOptimized.is_ip_blocked_fast(client_ip):
            logger.warning(f"🚫 黑名单IP访问: {client_ip} -> {path}")
            return JSONResponse(
                status_code=403,
                content={"code": 403, "message": "Access denied", "data": None}
            )

        # 2. 检查请求间隔（防止高频请求）
        if not self._check_request_interval(client_ip, path):
            self._record_violation(client_ip, "interval")
            return JSONResponse(
                status_code=429,
                content={
                    "code": 429,
                    "message": "请求过快，请放慢速度",
                    "data": {"reason": "请求间隔过短"}
                }
            )

        # 3. 检查速率限制
        if not self._check_rate_limit(client_ip, path):
            self._record_violation(client_ip, "rate_limit")

            # 检查是否需要自动封禁
            if self._should_auto_ban(client_ip):
                self._auto_ban_ip(client_ip, "频繁违规速率限制")
                return JSONResponse(
                    status_code=403,
                    content={
                        "code": 403,
                        "message": "由于频繁违规，您的IP已被封禁24小时",
                        "data": None
                    }
                )

            return JSONResponse(
                status_code=429,
                content={
                    "code": 429,
                    "message": "请求次数超限，请稍后再试",
                    "data": {"reason": "超过速率限制"}
                }
            )

        # 4. 记录请求时间（用于间隔检查）
        self._record_request_time(client_ip, path)

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

    def _get_action_type(self, path: str) -> str:
        """根据路径获取操作类型"""
        if '/register' in path or '/user/register' in path:
            return 'register'
        elif '/login' in path:
            return 'login'
        elif '/ad/watch' in path:
            return 'ad_watch'
        elif '/ad/random' in path or '/ad/' in path:
            return 'ad_random'
        else:
            return 'default'

    def _check_request_interval(self, ip: str, path: str) -> bool:
        """检查请求间隔"""
        try:
            action = self._get_action_type(path)
            min_interval = self.min_intervals.get(action, self.min_intervals['default'])

            redis_key = f"last_request:{ip}:{action}"
            last_time = redis_client.get(redis_key)

            if last_time:
                elapsed = time.time() - float(last_time)
                if elapsed < min_interval:
                    logger.warning(f"⚡ 请求过快: {ip} -> {action} (间隔{elapsed:.1f}秒)")
                    return False

            return True

        except Exception as e:
            logger.error(f"间隔检查失败: {e}")
            return True  # 优雅降级

    def _record_request_time(self, ip: str, path: str):
        """记录请求时间"""
        try:
            action = self._get_action_type(path)
            redis_key = f"last_request:{ip}:{action}"
            redis_client.setex(redis_key, 3600, str(time.time()))
        except Exception:
            pass

    def _check_rate_limit(self, ip: str, path: str) -> bool:
        """检查速率限制"""
        try:
            action = self._get_action_type(path)
            config = self.limits.get(action, self.limits['default'])

            max_requests = config['requests']
            window = config['window']

            redis_key = f"rate_limit:{ip}:{action}"
            current = redis_client.get(redis_key)

            if current is None:
                redis_client.setex(redis_key, window, 1)
                return True
            else:
                current_count = int(current)
                if current_count >= max_requests:
                    logger.warning(f"📊 超速率限制: {ip} -> {action} ({current_count}/{max_requests})")
                    return False
                else:
                    redis_client.incr(redis_key)
                    return True

        except Exception as e:
            logger.error(f"速率检查失败: {e}")
            return True  # 优雅降级

    def _record_violation(self, ip: str, violation_type: str):
        """记录违规行为"""
        try:
            redis_key = f"violations:{ip}"
            violation_data = f"{violation_type}:{int(time.time())}"

            # 添加违规记录
            redis_client.lpush(redis_key, violation_data)
            redis_client.expire(redis_key, self.auto_ban['violation_window'])

            # 限制列表长度
            redis_client.ltrim(redis_key, 0, 99)

        except Exception as e:
            logger.error(f"记录违规失败: {e}")

    def _should_auto_ban(self, ip: str) -> bool:
        """判断是否应该自动封禁"""
        try:
            redis_key = f"violations:{ip}"

            # 获取最近的违规次数
            violations = redis_client.lrange(redis_key, 0, -1)

            if not violations:
                return False

            # 统计时间窗口内的违规
            now = time.time()
            window = self.auto_ban['violation_window']
            recent_violations = 0

            for v in violations:
                if isinstance(v, bytes):
                    v = v.decode()
                parts = v.split(':')
                if len(parts) >= 2:
                    timestamp = int(parts[1])
                    if now - timestamp < window:
                        recent_violations += 1

            # 判断是否达到封禁阈值
            return recent_violations >= self.auto_ban['violation_threshold']

        except Exception as e:
            logger.error(f"检查自动封禁失败: {e}")
            return False

    def _auto_ban_ip(self, ip: str, reason: str):
        """自动封禁IP"""
        try:
            # 添加到Redis黑名单
            IPServiceOptimized.add_ip_to_blacklist_fast(ip)

            # 添加到数据库黑名单
            from models import IPBlacklist
            db = next(get_db())
            try:
                # 检查是否已存在
                existing = db.query(IPBlacklist).filter(
                    IPBlacklist.ip_address == ip
                ).first()

                if not existing:
                    from datetime import timedelta
                    blacklist_entry = IPBlacklist(
                        ip_address=ip,
                        reason=f"自动封禁: {reason}",
                        blocked_time=datetime.now(),
                        expire_time=datetime.now() + timedelta(seconds=self.auto_ban['ban_duration']),
                        is_active=1
                    )
                    db.add(blacklist_entry)
                    db.commit()
                    logger.warning(f"🔒 自动封禁IP: {ip} - {reason}")
                else:
                    # 更新过期时间
                    existing.expire_time = datetime.now() + timedelta(seconds=self.auto_ban['ban_duration'])
                    existing.is_active = 1
                    db.commit()
                    logger.warning(f"🔒 延长封禁IP: {ip} - {reason}")
            finally:
                db.close()

        except Exception as e:
            logger.error(f"自动封禁失败: {e}")
