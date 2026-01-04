from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from models import AdConfig, AdWatchRecord, User, AdStatus, TransactionType
from schemas import AdConfigCreate, AdConfigUpdate, AdWatchRequest
from services.user_service import UserService
from services.config_service import ConfigService
from typing import List, Optional
from datetime import datetime, date
import random
import json

class AdService:

    # Redis缓存TTL配置（秒）
    CACHE_TTL = {
        "active_ads": 300,  # 活跃广告列表缓存5分钟
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
    def _clear_ads_cache():
        """清除广告相关缓存"""
        redis = AdService._get_redis()
        if redis:
            try:
                redis.delete("active_ads")
            except Exception:
                pass

    @staticmethod
    def _get_active_ads_cached(db: Session) -> List[AdConfig]:
        """获取活跃广告列表（带缓存）"""
        redis = AdService._get_redis()
        cache_key = "active_ads"

        # 尝试从Redis获取缓存
        if redis:
            try:
                cached = redis.get(cache_key)
                if cached:
                    # 从缓存反序列化广告ID列表
                    ad_ids = json.loads(cached)
                    if ad_ids:
                        # 根据ID查询广告对象
                        ads = db.query(AdConfig).filter(AdConfig.id.in_(ad_ids)).all()
                        # 按原始顺序排序
                        ads_dict = {ad.id: ad for ad in ads}
                        return [ads_dict[aid] for aid in ad_ids if aid in ads_dict]
            except Exception:
                pass

        # 缓存未命中，查询数据库
        now = datetime.now()
        available_ads = db.query(AdConfig).filter(
            AdConfig.status == AdStatus.ACTIVE,
            or_(AdConfig.start_time.is_(None), AdConfig.start_time <= now),
            or_(AdConfig.end_time.is_(None), AdConfig.end_time >= now)
        ).all()

        # 写入Redis缓存（只缓存ID列表，减少内存占用）
        if redis and available_ads:
            try:
                ad_ids = [ad.id for ad in available_ads]
                redis.setex(
                    cache_key,
                    AdService.CACHE_TTL["active_ads"],
                    json.dumps(ad_ids)
                )
            except Exception:
                pass

        return available_ads
    
    @staticmethod
    def get_random_ad(db: Session, user_id) -> Optional[AdConfig]:
        """获取随机广告（考虑权重和用户今日观看限制）"""
        # 获取今日观看记录
        today = date.today()
        today_watches = db.query(AdWatchRecord).filter(
            AdWatchRecord.user_id == user_id,
            func.date(AdWatchRecord.watch_time) == today
        ).all()

        # 获取系统每日广告总限制（使用缓存）
        daily_limit = int(ConfigService.get_config(db, "daily_ad_limit", "20"))
        if len(today_watches) >= daily_limit:
            return None

        # 统计每个广告今日观看次数
        ad_watch_count = {}
        for watch in today_watches:
            ad_watch_count[watch.ad_id] = ad_watch_count.get(watch.ad_id, 0) + 1

        # 获取当前有效的广告（使用缓存）
        available_ads = AdService._get_active_ads_cached(db)

        # 过滤掉已达到每日限制的广告
        eligible_ads = []
        for ad in available_ads:
            watched_today = ad_watch_count.get(ad.id, 0)
            if watched_today < ad.daily_limit:
                eligible_ads.append(ad)

        if not eligible_ads:
            return None

        # 根据权重随机选择
        weights = [ad.weight for ad in eligible_ads]
        return random.choices(eligible_ads, weights=weights, k=1)[0]
    
    @staticmethod
    def watch_ad(db: Session, user_id, watch_request: AdWatchRequest, ip_address: str = None) -> dict:
        """处理广告观看"""
        # 获取广告配置 - 将字符串ID转换为整数
        try:
            ad_id = int(watch_request.ad_id)
        except ValueError:
            return {"success": False, "message": "无效的广告ID格式"}
            
        ad = db.query(AdConfig).filter(AdConfig.id == ad_id).first()
        if not ad or ad.status != AdStatus.ACTIVE:
            return {"success": False, "message": "广告不存在或已下线"}
        
        # 获取最小观看时长（根据广告类型）
        if ad.ad_type == "video":
            min_duration = ConfigService.get_video_ad_min_duration(db)
        else:  # webpage
            min_duration = ConfigService.get_webpage_ad_min_duration(db)
        
        # 检查观看时长是否达标（只依赖服务端验证的观看时长，不信任客户端的is_completed标志）
        is_completed = watch_request.watch_duration >= min_duration
        
        # 计算奖励金币（使用配置的动态奖励范围）
        if is_completed:
            # 如果广告本身设置了奖励金币，优先使用广告设置
            if ad.reward_coins > 0:
                base_reward_coins = float(ad.reward_coins)
            else:
                # 使用系统配置的奖励范围随机生成
                min_coins, max_coins = ConfigService.get_ad_reward_coins_range(db)
                base_reward_coins = random.uniform(min_coins, max_coins)
                base_reward_coins = round(base_reward_coins, 2)
            
            # 根据用户等级计算最终奖励
            from services.level_service import LevelService
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                reward_coins = LevelService.calculate_ad_coins(db, user.level, base_reward_coins)
            else:
                reward_coins = base_reward_coins
        else:
            reward_coins = 0
        
        # 检查今日观看限制
        today = date.today()
        today_count = db.query(func.count(AdWatchRecord.id)).filter(
            AdWatchRecord.user_id == user_id,
            AdWatchRecord.ad_id == ad_id,
            func.date(AdWatchRecord.watch_time) == today
        ).scalar()
        
        if today_count >= ad.daily_limit:
            return {"success": False, "message": "今日该广告观看次数已达上限"}
        
        # 检查系统每日总限制
        daily_limit = int(ConfigService.get_config(db, "daily_ad_limit", "20"))
        total_today = db.query(func.count(AdWatchRecord.id)).filter(
            AdWatchRecord.user_id == user_id,
            func.date(AdWatchRecord.watch_time) == today
        ).scalar()
        
        if total_today >= daily_limit:
            return {"success": False, "message": "今日广告观看次数已达上限"}
        
        # 记录观看记录
        watch_record = AdWatchRecord(
            user_id=user_id,
            ad_id=ad_id,
            watch_duration=watch_request.watch_duration,
            reward_coins=reward_coins,
            is_completed=1 if is_completed else 0,
            ip_address=ip_address,
            device_info=watch_request.device_info
        )
        
        db.add(watch_record)
        db.commit()
        db.refresh(watch_record)
        
        # 发放奖励金币
        if reward_coins > 0:
            UserService.add_coins(
                db, user_id, float(reward_coins),
                TransactionType.AD_REWARD,
                f"观看广告奖励: {ad.name}",
                watch_record.id
            )
        
        return {
            "success": True,
            "message": "广告观看完成",
            "reward_coins": reward_coins,
            "is_completed": is_completed
        }
    
    @staticmethod
    def get_user_ad_stats(db: Session, user_id) -> dict:
        """获取用户广告观看统计"""
        today = date.today()
        
        # 今日观看次数
        today_count = db.query(func.count(AdWatchRecord.id)).filter(
            AdWatchRecord.user_id == user_id,
            func.date(AdWatchRecord.watch_time) == today
        ).scalar() or 0
        
        # 今日获得金币
        today_coins = db.query(func.sum(AdWatchRecord.reward_coins)).filter(
            AdWatchRecord.user_id == user_id,
            func.date(AdWatchRecord.watch_time) == today
        ).scalar() or 0
        
        # 总观看次数
        total_count = db.query(func.count(AdWatchRecord.id)).filter(
            AdWatchRecord.user_id == user_id
        ).scalar() or 0
        
        # 总获得金币
        total_coins = db.query(func.sum(AdWatchRecord.reward_coins)).filter(
            AdWatchRecord.user_id == user_id
        ).scalar() or 0
        
        # 每日限制
        daily_limit = int(ConfigService.get_config(db, "daily_ad_limit", "20"))
        
        return {
            "today_count": today_count,
            "today_coins": float(today_coins),
            "total_count": total_count,
            "total_coins": float(total_coins),
            "daily_limit": daily_limit,
            "remaining_today": max(0, daily_limit - today_count)
        }
    
    # 管理员功能
    @staticmethod
    def create_ad_config(db: Session, ad_data: AdConfigCreate) -> AdConfig:
        """创建广告配置"""
        ad = AdConfig(**ad_data.dict())
        db.add(ad)
        db.commit()
        db.refresh(ad)
        # 清除广告缓存
        AdService._clear_ads_cache()
        return ad
    
    @staticmethod
    def update_ad_config(db: Session, ad_id: int, ad_data: AdConfigUpdate) -> Optional[AdConfig]:
        """更新广告配置"""
        ad = db.query(AdConfig).filter(AdConfig.id == ad_id).first()
        if not ad:
            return None

        # 更新字段，特殊处理status字段
        for field, value in ad_data.dict(exclude_unset=True).items():
            if field == 'status':
                # 将前端的字符串状态转换为数据库枚举值
                if value == 'ACTIVE' or value == 1:
                    setattr(ad, field, AdStatus.ACTIVE)  # 设置枚举值
                elif value == 'INACTIVE' or value == 0:
                    setattr(ad, field, AdStatus.DISABLED)  # 设置枚举值
                elif isinstance(value, AdStatus):
                    setattr(ad, field, value)  # 已经是枚举类型
                # 如果是其他值就忽略
            else:
                setattr(ad, field, value)

        db.commit()
        db.refresh(ad)
        # 清除广告缓存
        AdService._clear_ads_cache()
        return ad
    
    @staticmethod
    def delete_ad_config(db: Session, ad_id: int) -> bool:
        """删除广告配置"""
        from models import AdWatchRecord

        ad = db.query(AdConfig).filter(AdConfig.id == ad_id).first()
        if not ad:
            return False

        # 检查是否有相关的观看记录
        watch_records_count = db.query(AdWatchRecord).filter(AdWatchRecord.ad_id == ad_id).count()

        if watch_records_count > 0:
            # 如果有观看记录，先删除相关记录
            db.query(AdWatchRecord).filter(AdWatchRecord.ad_id == ad_id).delete()

        # 删除广告配置
        db.delete(ad)
        db.commit()
        # 清除广告缓存
        AdService._clear_ads_cache()
        return True
    
    @staticmethod
    def get_ad_config(db: Session, ad_id: int) -> Optional[AdConfig]:
        """获取广告配置"""
        return db.query(AdConfig).filter(AdConfig.id == ad_id).first()
    
    @staticmethod
    def get_all_ad_configs(db: Session, skip: int = 0, limit: int = 100) -> List[AdConfig]:
        """获取所有广告配置"""
        return db.query(AdConfig).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_ad_stats(db: Session, ad_id: int = None) -> dict:
        """获取广告统计数据"""
        today = date.today()
        
        if ad_id:
            # 单个广告统计
            query = db.query(AdWatchRecord).filter(AdWatchRecord.ad_id == ad_id)
            
            today_views = query.filter(func.date(AdWatchRecord.watch_time) == today).count()
            total_views = query.count()
            today_coins = query.filter(func.date(AdWatchRecord.watch_time) == today).with_entities(
                func.sum(AdWatchRecord.reward_coins)).scalar() or 0
            total_coins = query.with_entities(func.sum(AdWatchRecord.reward_coins)).scalar() or 0
            
            return {
                "ad_id": ad_id,
                "today_views": today_views,
                "total_views": total_views,
                "today_coins": float(today_coins),
                "total_coins": float(total_coins)
            }
        else:
            # 全部广告统计
            today_views = db.query(func.count(AdWatchRecord.id)).filter(
                func.date(AdWatchRecord.watch_time) == today).scalar() or 0
            total_views = db.query(func.count(AdWatchRecord.id)).scalar() or 0
            today_coins = db.query(func.sum(AdWatchRecord.reward_coins)).filter(
                func.date(AdWatchRecord.watch_time) == today).scalar() or 0
            total_coins = db.query(func.sum(AdWatchRecord.reward_coins)).scalar() or 0
            
            return {
                "today_views": today_views,
                "total_views": total_views,
                "today_coins": float(today_coins),
                "total_coins": float(total_coins)
            }
    
    @staticmethod
    def init_default_ads(db: Session):
        """初始化默认广告配置"""
        # 检查是否已有广告配置
        existing_ads = db.query(AdConfig).count()
        if existing_ads > 0:
            return
        
        # 示例广告视频配置（使用公开的测试视频）
        # 获取系统配置的默认奖励金币
        default_reward = ConfigService.get_ad_reward_coins_default(db)
        min_coins, max_coins = ConfigService.get_ad_reward_coins_range(db)
        
        default_ads = [
            {
                "name": "游戏推广广告",
                "ad_type": "video",
                "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
                "duration": 30,
                "reward_coins": 36,  # 30-40双数
                "daily_limit": 5,
                "min_watch_duration": ConfigService.get_video_ad_min_duration(db),
                "weight": 3,
                "status": AdStatus.ACTIVE
            },
            {
                "name": "应用下载广告",
                "ad_type": "video",
                "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
                "duration": 25,
                "reward_coins": 40,  # 30-40双数
                "daily_limit": 3,
                "min_watch_duration": ConfigService.get_video_ad_min_duration(db),
                "weight": 2,
                "status": AdStatus.ACTIVE
            },
            {
                "name": "品牌推广广告",
                "ad_type": "video",
                "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
                "duration": 15,
                "reward_coins": 32,  # 30-40双数
                "daily_limit": 10,
                "min_watch_duration": 10,
                "weight": 5,
                "status": AdStatus.ACTIVE
            },
            {
                "name": "购物广告",
                "ad_type": "video",
                "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
                "duration": 20,
                "reward_coins": 38,  # 30-40双数
                "daily_limit": 4,
                "min_watch_duration": 15,
                "weight": 3,
                "status": AdStatus.ACTIVE
            }
        ]
        
        for ad_data in default_ads:
            ad = AdConfig(**ad_data)
            db.add(ad)
        
        db.commit()
        print("✅ 默认广告配置初始化完成") 