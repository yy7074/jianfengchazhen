"""
IP服务优化版本 - 使用Redis Set存储黑名单，避免数据库查询
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from models import IPBlacklist, IPAccessLog, AdWatchRecord, User
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Set
import json
import logging

logger = logging.getLogger(__name__)


class IPServiceOptimized:
    """IP管理服务 - 优化版"""

    # Redis键名
    REDIS_KEYS = {
        "blocked_ips_set": "ip_blacklist:blocked_set",  # 被封禁IP的集合
        "blocked_ips_sync": "ip_blacklist:last_sync",   # 最后同步时间
    }

    # 缓存TTL配置
    CACHE_TTL = {
        "ip_blocked": 300,      # IP封禁状态缓存5分钟
        "sync_interval": 60,    # 黑名单同步间隔60秒
    }

    @staticmethod
    def _get_redis():
        """获取Redis客户端"""
        try:
            from database import redis_client
            return redis_client
        except Exception:
            return None

    @staticmethod
    def sync_blocked_ips_to_redis(db: Session) -> int:
        """
        从数据库同步被封禁IP到Redis Set
        返回：同步的IP数量
        """
        redis = IPServiceOptimized._get_redis()
        if not redis:
            return 0

        try:
            # 查询所有活跃的封禁IP
            now = datetime.now()
            blocked_ips = db.query(IPBlacklist.ip_address).filter(
                IPBlacklist.is_active == 1,
                or_(
                    IPBlacklist.expire_time.is_(None),
                    IPBlacklist.expire_time > now
                )
            ).all()

            # 提取IP地址列表
            ip_list = [ip[0] for ip in blocked_ips]

            # 清空旧的集合
            redis.delete(IPServiceOptimized.REDIS_KEYS["blocked_ips_set"])

            # 批量添加到Redis Set
            if ip_list:
                redis.sadd(IPServiceOptimized.REDIS_KEYS["blocked_ips_set"], *ip_list)

            # 记录最后同步时间
            redis.set(
                IPServiceOptimized.REDIS_KEYS["blocked_ips_sync"],
                datetime.now().isoformat()
            )

            logger.info(f"✅ 同步{len(ip_list)}个封禁IP到Redis")
            return len(ip_list)

        except Exception as e:
            logger.error(f"❌ 同步封禁IP到Redis失败: {e}")
            return 0

    @staticmethod
    def is_ip_blocked_fast(ip_address: str, db: Session = None) -> bool:
        """
        快速检查IP是否被封禁（纯Redis，不查数据库）
        如果Redis不可用，降级到数据库查询
        """
        redis = IPServiceOptimized._get_redis()

        # 如果Redis可用，直接查Redis Set
        if redis:
            try:
                # 检查是否需要同步（每60秒同步一次）
                last_sync = redis.get(IPServiceOptimized.REDIS_KEYS["blocked_ips_sync"])
                if not last_sync or (
                    datetime.now() - datetime.fromisoformat(last_sync.decode() if isinstance(last_sync, bytes) else last_sync)
                ).total_seconds() > IPServiceOptimized.CACHE_TTL["sync_interval"]:
                    # 需要同步，但不在这里执行（避免阻塞）
                    # 可以用后台任务或启动时同步
                    pass

                # 检查IP是否在黑名单集合中
                is_blocked = redis.sismember(
                    IPServiceOptimized.REDIS_KEYS["blocked_ips_set"],
                    ip_address
                )
                return bool(is_blocked)

            except Exception as e:
                logger.warning(f"Redis检查IP失败，降级到数据库: {e}")

        # Redis不可用或失败，降级到数据库查询
        if db:
            now = datetime.now()
            blocked = db.query(IPBlacklist).filter(
                IPBlacklist.ip_address == ip_address,
                IPBlacklist.is_active == 1,
                or_(
                    IPBlacklist.expire_time.is_(None),
                    IPBlacklist.expire_time > now
                )
            ).first()
            return blocked is not None

        return False

    @staticmethod
    def add_ip_to_blacklist_fast(ip_address: str):
        """快速添加IP到Redis黑名单（不查数据库）"""
        redis = IPServiceOptimized._get_redis()
        if redis:
            try:
                redis.sadd(
                    IPServiceOptimized.REDIS_KEYS["blocked_ips_set"],
                    ip_address
                )
                logger.info(f"✅ 添加{ip_address}到Redis黑名单")
            except Exception as e:
                logger.error(f"❌ 添加IP到Redis黑名单失败: {e}")

    @staticmethod
    def remove_ip_from_blacklist_fast(ip_address: str):
        """快速从Redis黑名单移除IP"""
        redis = IPServiceOptimized._get_redis()
        if redis:
            try:
                redis.srem(
                    IPServiceOptimized.REDIS_KEYS["blocked_ips_set"],
                    ip_address
                )
                logger.info(f"✅ 从Redis黑名单移除{ip_address}")
            except Exception as e:
                logger.error(f"❌ 从Redis黑名单移除IP失败: {e}")

    @staticmethod
    def get_blocked_ips_count() -> int:
        """获取当前封禁IP数量"""
        redis = IPServiceOptimized._get_redis()
        if redis:
            try:
                return redis.scard(IPServiceOptimized.REDIS_KEYS["blocked_ips_set"])
            except Exception:
                pass
        return 0
