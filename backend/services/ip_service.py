from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from models import IPBlacklist, IPAccessLog, AdWatchRecord, User
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict


class IPService:
    """IP管理服务"""

    # 异常检测阈值配置
    THRESHOLDS = {
        "max_users_per_ip": 5,           # 单IP最大关联用户数
        "max_requests_per_minute": 60,   # 每分钟最大请求数
        "max_ad_watches_per_hour": 100,  # 每小时最大广告观看数
        "auto_block_duration_hours": 24, # 自动封禁时长（小时）
    }

    @staticmethod
    def is_ip_blocked(db: Session, ip_address: str) -> bool:
        """检查IP是否被封禁"""
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

    @staticmethod
    def get_ip_block_info(db: Session, ip_address: str) -> Optional[Dict]:
        """获取IP封禁信息"""
        now = datetime.now()
        blocked = db.query(IPBlacklist).filter(
            IPBlacklist.ip_address == ip_address,
            IPBlacklist.is_active == 1,
            or_(
                IPBlacklist.expire_time.is_(None),
                IPBlacklist.expire_time > now
            )
        ).first()

        if blocked:
            return {
                "id": blocked.id,
                "ip_address": blocked.ip_address,
                "reason": blocked.reason,
                "block_type": blocked.block_type,
                "blocked_time": blocked.blocked_time.isoformat() if blocked.blocked_time else None,
                "expire_time": blocked.expire_time.isoformat() if blocked.expire_time else None,
            }
        return None

    @staticmethod
    def block_ip(db: Session, ip_address: str, reason: str,
                 block_type: str = "manual", duration_hours: int = None,
                 related_user_ids: List[int] = None) -> Dict:
        """封禁IP"""
        # 检查是否已存在
        existing = db.query(IPBlacklist).filter(
            IPBlacklist.ip_address == ip_address
        ).first()

        expire_time = None
        if duration_hours:
            expire_time = datetime.now() + timedelta(hours=duration_hours)

        user_ids_str = ",".join(map(str, related_user_ids)) if related_user_ids else None

        if existing:
            existing.reason = reason
            existing.block_type = block_type
            existing.is_active = 1
            existing.blocked_time = datetime.now()
            existing.expire_time = expire_time
            if user_ids_str:
                existing.related_user_ids = user_ids_str
            db.commit()
            return {"success": True, "message": "IP封禁已更新", "id": existing.id}
        else:
            new_block = IPBlacklist(
                ip_address=ip_address,
                reason=reason,
                block_type=block_type,
                related_user_ids=user_ids_str,
                blocked_time=datetime.now(),
                expire_time=expire_time
            )
            db.add(new_block)
            db.commit()
            return {"success": True, "message": "IP已封禁", "id": new_block.id}

    @staticmethod
    def unblock_ip(db: Session, ip_address: str) -> Dict:
        """解封IP"""
        blocked = db.query(IPBlacklist).filter(
            IPBlacklist.ip_address == ip_address
        ).first()

        if not blocked:
            return {"success": False, "message": "IP不在黑名单中"}

        blocked.is_active = 0
        blocked.updated_time = datetime.now()
        db.commit()
        return {"success": True, "message": "IP已解封"}

    @staticmethod
    def get_ip_users(db: Session, ip_address: str) -> List[Dict]:
        """获取使用该IP的所有用户"""
        # 从广告观看记录中查找
        user_ids = db.query(AdWatchRecord.user_id).filter(
            AdWatchRecord.ip_address == ip_address
        ).distinct().all()

        user_ids = [uid[0] for uid in user_ids]

        if not user_ids:
            return []

        users = db.query(User).filter(User.id.in_(user_ids)).all()
        return [
            {
                "id": u.id,
                "nickname": u.nickname,
                "device_id": u.device_id,
                "device_name": u.device_name,
                "coins": float(u.coins),
                "register_time": u.register_time.isoformat() if u.register_time else None
            }
            for u in users
        ]

    @staticmethod
    def get_user_ips(db: Session, user_id: int) -> List[Dict]:
        """获取用户使用过的所有IP"""
        today = date.today()

        # 查询用户的IP使用记录
        ip_records = db.query(
            AdWatchRecord.ip_address,
            func.count(AdWatchRecord.id).label('request_count'),
            func.min(AdWatchRecord.watch_time).label('first_seen'),
            func.max(AdWatchRecord.watch_time).label('last_seen')
        ).filter(
            AdWatchRecord.user_id == user_id,
            AdWatchRecord.ip_address.isnot(None)
        ).group_by(AdWatchRecord.ip_address).all()

        result = []
        for record in ip_records:
            ip = record.ip_address
            if not ip:
                continue

            # 检查该IP是否被封禁
            is_blocked = IPService.is_ip_blocked(db, ip)

            # 统计该IP关联的用户数
            user_count = db.query(func.count(func.distinct(AdWatchRecord.user_id))).filter(
                AdWatchRecord.ip_address == ip
            ).scalar() or 0

            # 今日请求数
            today_count = db.query(func.count(AdWatchRecord.id)).filter(
                AdWatchRecord.ip_address == ip,
                func.date(AdWatchRecord.watch_time) == today
            ).scalar() or 0

            result.append({
                "ip_address": ip,
                "request_count": record.request_count,
                "today_count": today_count,
                "user_count": user_count,
                "first_seen": record.first_seen.isoformat() if record.first_seen else None,
                "last_seen": record.last_seen.isoformat() if record.last_seen else None,
                "is_blocked": is_blocked,
                "is_suspicious": user_count > IPService.THRESHOLDS["max_users_per_ip"]
            })

        return sorted(result, key=lambda x: x["last_seen"] or "", reverse=True)

    @staticmethod
    def analyze_ip_anomaly(db: Session, ip_address: str) -> Dict:
        """分析IP异常情况"""
        today = date.today()
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)

        # 1. 关联用户数
        user_count = db.query(func.count(func.distinct(AdWatchRecord.user_id))).filter(
            AdWatchRecord.ip_address == ip_address
        ).scalar() or 0

        # 2. 今日请求总数
        today_requests = db.query(func.count(AdWatchRecord.id)).filter(
            AdWatchRecord.ip_address == ip_address,
            func.date(AdWatchRecord.watch_time) == today
        ).scalar() or 0

        # 3. 最近一小时请求数
        hourly_requests = db.query(func.count(AdWatchRecord.id)).filter(
            AdWatchRecord.ip_address == ip_address,
            AdWatchRecord.watch_time >= one_hour_ago
        ).scalar() or 0

        # 4. 获取关联用户详情
        users = IPService.get_ip_users(db, ip_address)

        # 5. 判断异常类型
        anomalies = []
        risk_level = "normal"

        if user_count > IPService.THRESHOLDS["max_users_per_ip"]:
            anomalies.append(f"同一IP关联{user_count}个用户（阈值: {IPService.THRESHOLDS['max_users_per_ip']}）")
            risk_level = "high"

        if hourly_requests > IPService.THRESHOLDS["max_ad_watches_per_hour"]:
            anomalies.append(f"一小时内{hourly_requests}次广告请求（阈值: {IPService.THRESHOLDS['max_ad_watches_per_hour']}）")
            risk_level = "high"

        if today_requests > 500:
            anomalies.append(f"今日请求{today_requests}次")
            if risk_level == "normal":
                risk_level = "medium"

        return {
            "ip_address": ip_address,
            "user_count": user_count,
            "today_requests": today_requests,
            "hourly_requests": hourly_requests,
            "users": users,
            "anomalies": anomalies,
            "risk_level": risk_level,
            "is_blocked": IPService.is_ip_blocked(db, ip_address)
        }

    @staticmethod
    def get_suspicious_ips(db: Session, limit: int = 50) -> List[Dict]:
        """获取可疑IP列表"""
        today = date.today()

        # 查询今日所有IP的统计
        ip_stats = db.query(
            AdWatchRecord.ip_address,
            func.count(AdWatchRecord.id).label('request_count'),
            func.count(func.distinct(AdWatchRecord.user_id)).label('user_count')
        ).filter(
            AdWatchRecord.ip_address.isnot(None),
            func.date(AdWatchRecord.watch_time) == today
        ).group_by(AdWatchRecord.ip_address).having(
            or_(
                func.count(func.distinct(AdWatchRecord.user_id)) > IPService.THRESHOLDS["max_users_per_ip"],
                func.count(AdWatchRecord.id) > 100
            )
        ).order_by(func.count(func.distinct(AdWatchRecord.user_id)).desc()).limit(limit).all()

        result = []
        for stat in ip_stats:
            is_blocked = IPService.is_ip_blocked(db, stat.ip_address)
            result.append({
                "ip_address": stat.ip_address,
                "request_count": stat.request_count,
                "user_count": stat.user_count,
                "is_blocked": is_blocked,
                "risk_level": "high" if stat.user_count > IPService.THRESHOLDS["max_users_per_ip"] else "medium"
            })

        return result

    @staticmethod
    def get_blacklist(db: Session, page: int = 1, size: int = 20,
                      is_active: int = None) -> Dict:
        """获取IP黑名单列表"""
        query = db.query(IPBlacklist)

        if is_active is not None:
            query = query.filter(IPBlacklist.is_active == is_active)

        total = query.count()
        skip = (page - 1) * size
        items = query.order_by(IPBlacklist.blocked_time.desc()).offset(skip).limit(size).all()

        return {
            "items": [
                {
                    "id": item.id,
                    "ip_address": item.ip_address,
                    "reason": item.reason,
                    "block_type": item.block_type,
                    "related_user_ids": item.related_user_ids,
                    "request_count": item.request_count,
                    "is_active": item.is_active,
                    "blocked_time": item.blocked_time.isoformat() if item.blocked_time else None,
                    "expire_time": item.expire_time.isoformat() if item.expire_time else None
                }
                for item in items
            ],
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }

    @staticmethod
    def auto_detect_and_block(db: Session) -> List[Dict]:
        """自动检测并封禁异常IP"""
        suspicious_ips = IPService.get_suspicious_ips(db, limit=100)
        blocked = []

        for ip_info in suspicious_ips:
            if ip_info["is_blocked"]:
                continue

            if ip_info["user_count"] > IPService.THRESHOLDS["max_users_per_ip"] * 2:
                # 严重异常，自动封禁
                users = IPService.get_ip_users(db, ip_info["ip_address"])
                user_ids = [u["id"] for u in users]

                result = IPService.block_ip(
                    db,
                    ip_info["ip_address"],
                    f"自动封禁: 同一IP关联{ip_info['user_count']}个用户",
                    block_type="auto",
                    duration_hours=IPService.THRESHOLDS["auto_block_duration_hours"],
                    related_user_ids=user_ids
                )

                if result["success"]:
                    blocked.append({
                        "ip_address": ip_info["ip_address"],
                        "user_count": ip_info["user_count"],
                        "reason": "用户数超标"
                    })

        return blocked
