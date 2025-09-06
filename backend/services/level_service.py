from sqlalchemy.orm import Session
from sqlalchemy import func
from models import UserLevelConfig, User
from schemas import UserLevelConfigCreate, UserLevelConfigUpdate
from typing import List, Optional
from decimal import Decimal

class LevelService:
    
    @staticmethod
    def init_default_levels(db: Session):
        """初始化默认等级配置"""
        # 检查是否已有等级配置
        existing_levels = db.query(UserLevelConfig).count()
        if existing_levels > 0:
            return
        
        # 默认等级配置
        default_levels = [
            {
                "level": 1,
                "level_name": "新手",
                "ad_coin_multiplier": Decimal("1.00"),
                "game_coin_multiplier": Decimal("1.00"),
                "min_experience": 0,
                "max_experience": 999,
                "description": "初始等级，正常金币奖励",
                "is_active": 1
            },
            {
                "level": 2,
                "level_name": "青铜",
                "ad_coin_multiplier": Decimal("1.20"),
                "game_coin_multiplier": Decimal("1.10"),
                "min_experience": 1000,
                "max_experience": 2999,
                "description": "广告金币+20%，游戏金币+10%",
                "is_active": 1
            },
            {
                "level": 3,
                "level_name": "白银",
                "ad_coin_multiplier": Decimal("1.50"),
                "game_coin_multiplier": Decimal("1.20"),
                "min_experience": 3000,
                "max_experience": 5999,
                "description": "广告金币+50%，游戏金币+20%",
                "is_active": 1
            },
            {
                "level": 4,
                "level_name": "黄金",
                "ad_coin_multiplier": Decimal("1.80"),
                "game_coin_multiplier": Decimal("1.30"),
                "min_experience": 6000,
                "max_experience": 9999,
                "description": "广告金币+80%，游戏金币+30%",
                "is_active": 1
            },
            {
                "level": 5,
                "level_name": "铂金",
                "ad_coin_multiplier": Decimal("2.00"),
                "game_coin_multiplier": Decimal("1.50"),
                "min_experience": 10000,
                "max_experience": 19999,
                "description": "广告金币+100%，游戏金币+50%",
                "is_active": 1
            },
            {
                "level": 6,
                "level_name": "钻石",
                "ad_coin_multiplier": Decimal("2.50"),
                "game_coin_multiplier": Decimal("1.80"),
                "min_experience": 20000,
                "max_experience": 39999,
                "description": "广告金币+150%，游戏金币+80%",
                "is_active": 1
            },
            {
                "level": 7,
                "level_name": "大师",
                "ad_coin_multiplier": Decimal("3.00"),
                "game_coin_multiplier": Decimal("2.00"),
                "min_experience": 40000,
                "max_experience": None,
                "description": "广告金币+200%，游戏金币+100%",
                "is_active": 1
            }
        ]
        
        for level_data in default_levels:
            level_config = UserLevelConfig(**level_data)
            db.add(level_config)
        
        db.commit()
        print("✅ 默认用户等级配置初始化完成")
    
    @staticmethod
    def get_user_level_config(db: Session, user_level: int) -> Optional[UserLevelConfig]:
        """根据用户等级获取等级配置"""
        return db.query(UserLevelConfig).filter(
            UserLevelConfig.level == user_level,
            UserLevelConfig.is_active == 1
        ).first()
    
    @staticmethod
    def get_user_level_by_experience(db: Session, experience: int) -> Optional[UserLevelConfig]:
        """根据经验值获取用户等级配置"""
        return db.query(UserLevelConfig).filter(
            UserLevelConfig.min_experience <= experience,
            (UserLevelConfig.max_experience >= experience) | (UserLevelConfig.max_experience.is_(None)),
            UserLevelConfig.is_active == 1
        ).order_by(UserLevelConfig.level.desc()).first()
    
    @staticmethod
    def calculate_ad_coins(db: Session, user_level: int, base_coins: float) -> float:
        """根据用户等级计算广告金币奖励"""
        level_config = LevelService.get_user_level_config(db, user_level)
        if level_config:
            multiplier = float(level_config.ad_coin_multiplier)
            return round(base_coins * multiplier, 2)
        return base_coins
    
    @staticmethod
    def calculate_game_coins(db: Session, user_level: int, base_coins: float) -> float:
        """根据用户等级计算游戏金币奖励"""
        level_config = LevelService.get_user_level_config(db, user_level)
        if level_config:
            multiplier = float(level_config.game_coin_multiplier)
            return round(base_coins * multiplier, 2)
        return base_coins
    
    @staticmethod
    def update_user_level(db: Session, user_id: int) -> bool:
        """根据经验值更新用户等级"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        # 根据经验值获取应该的等级
        level_config = LevelService.get_user_level_by_experience(db, user.experience)
        if level_config and level_config.level != user.level:
            old_level = user.level
            user.level = level_config.level
            db.commit()
            print(f"用户 {user_id} 等级从 {old_level} 升级到 {user.level}")
            return True
        
        return False
    
    # 管理员功能
    @staticmethod
    def get_all_level_configs(db: Session) -> List[UserLevelConfig]:
        """获取所有等级配置"""
        return db.query(UserLevelConfig).order_by(UserLevelConfig.level).all()
    
    @staticmethod
    def create_level_config(db: Session, level_data: UserLevelConfigCreate) -> UserLevelConfig:
        """创建等级配置"""
        level_config = UserLevelConfig(**level_data.dict())
        db.add(level_config)
        db.commit()
        db.refresh(level_config)
        return level_config
    
    @staticmethod
    def update_level_config(db: Session, level_id: int, level_data: UserLevelConfigUpdate) -> Optional[UserLevelConfig]:
        """更新等级配置"""
        level_config = db.query(UserLevelConfig).filter(UserLevelConfig.id == level_id).first()
        if not level_config:
            return None
        
        for field, value in level_data.dict(exclude_unset=True).items():
            setattr(level_config, field, value)
        
        db.commit()
        db.refresh(level_config)
        return level_config
    
    @staticmethod
    def delete_level_config(db: Session, level_id: int) -> bool:
        """删除等级配置"""
        level_config = db.query(UserLevelConfig).filter(UserLevelConfig.id == level_id).first()
        if not level_config:
            return False
        
        db.delete(level_config)
        db.commit()
        return True
    
    @staticmethod
    def get_level_stats(db: Session) -> dict:
        """获取等级统计信息"""
        # 统计各等级用户数量
        level_stats = db.query(
            User.level.label('level'),
            func.count(User.id).label('user_count')
        ).group_by(User.level).all()
        
        stats = {}
        for stat in level_stats:
            stats[stat.level] = stat.user_count
        
        return {
            "level_distribution": stats,
            "total_levels": db.query(UserLevelConfig).filter(UserLevelConfig.is_active == 1).count(),
            "total_users": db.query(User).count()
        }
