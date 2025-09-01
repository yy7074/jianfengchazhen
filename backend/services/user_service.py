from sqlalchemy.orm import Session
from sqlalchemy import func
from models import User, CoinTransaction, TransactionType, UserStatus
from schemas import UserRegister, UserUpdate
from typing import Optional
from datetime import datetime
from decimal import Decimal
import hashlib

class UserService:
    
    @staticmethod
    def create_user(db: Session, user_data: UserRegister) -> User:
        """创建新用户"""
        # 检查设备ID是否已存在
        existing_user = db.query(User).filter(User.device_id == user_data.device_id).first()
        if existing_user:
            raise ValueError("设备ID已存在")
        
        # 创建新用户
        user = User(
            device_id=user_data.device_id,
            device_name=user_data.device_name,
            nickname=user_data.nickname or f"用户{user_data.device_id[-6:]}",
            coins=0,
            total_coins=0
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # 发放注册奖励
        UserService.add_register_reward(db, user)
        
        return user
    
    @staticmethod
    def get_user_by_device_id(db: Session, device_id: str) -> Optional[User]:
        """根据设备ID获取用户"""
        return db.query(User).filter(User.device_id == device_id).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id) -> Optional[User]:
        """根据用户ID获取用户"""
        # 尝试将user_id转换为int，如果失败则直接使用字符串
        try:
            user_id_int = int(user_id)
            return db.query(User).filter(User.id == user_id_int).first()
        except (ValueError, TypeError):
            # 如果user_id不是数字，则按字符串处理
            return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """更新用户信息"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        if user_data.nickname:
            user.nickname = user_data.nickname
        if user_data.avatar:
            user.avatar = user_data.avatar
        
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def update_last_login(db: Session, user_id: int):
        """更新最后登录时间"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.last_login_time = datetime.now()
            db.commit()
    
    @staticmethod
    def add_coins(db: Session, user_id: int, amount: float, transaction_type: TransactionType, 
                  description: str = None, related_id: int = None) -> bool:
        """给用户添加金币"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        # 转换为Decimal类型
        amount_decimal = Decimal(str(amount))
        
        # 更新用户金币
        user.coins += amount_decimal
        user.total_coins += amount_decimal
        
        # 记录交易
        transaction = CoinTransaction(
            user_id=user_id,
            type=transaction_type,
            amount=amount_decimal,
            balance_after=user.coins,
            description=description,
            related_id=related_id
        )
        
        db.add(transaction)
        db.commit()
        return True
    
    @staticmethod
    def deduct_coins(db: Session, user_id: int, amount: float, transaction_type: TransactionType,
                     description: str = None, related_id: int = None) -> bool:
        """扣除用户金币"""
        user = db.query(User).filter(User.id == user_id).first()
        amount_decimal = Decimal(str(amount))
        if not user or user.coins < amount_decimal:
            return False
        
        # 更新用户金币
        user.coins -= amount_decimal
        
        # 记录交易
        transaction = CoinTransaction(
            user_id=user_id,
            type=transaction_type,
            amount=-amount_decimal,
            balance_after=user.coins,
            description=description,
            related_id=related_id
        )
        
        db.add(transaction)
        db.commit()
        return True
    
    @staticmethod
    def add_register_reward(db: Session, user: User):
        """发放注册奖励"""
        from services.config_service import ConfigService
        reward_coins = float(ConfigService.get_config(db, "register_reward_coins", "100"))
        
        if reward_coins > 0:
            UserService.add_coins(
                db, user.id, reward_coins, 
                TransactionType.REGISTER_REWARD,
                "注册奖励"
            )
    
    @staticmethod
    def update_game_stats(db: Session, user_id: int, score: int, duration: int, needles: int):
        """更新游戏统计"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.game_count += 1
            if score > user.best_score:
                user.best_score = score
            
            # 增加经验值
            experience_gain = max(1, score // 10)
            user.experience += experience_gain
            
            # 计算等级（每1000经验升一级）
            new_level = user.experience // 1000 + 1
            user.level = new_level
            
            db.commit()
    
    @staticmethod
    def get_user_stats(db: Session, user_id: int) -> dict:
        """获取用户统计信息"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {}
        
        # 获取今日游戏次数
        today = datetime.now().date()
        today_games = db.query(func.count(GameRecord.id)).filter(
            GameRecord.user_id == user_id,
            func.date(GameRecord.play_time) == today
        ).scalar() or 0
        
        # 获取今日广告观看次数
        today_ads = db.query(func.count(AdWatchRecord.id)).filter(
            AdWatchRecord.user_id == user_id,
            func.date(AdWatchRecord.watch_time) == today
        ).scalar() or 0
        
        return {
            "user_info": user,
            "today_games": today_games,
            "today_ads": today_ads,
            "next_level_exp": (user.level * 1000) - user.experience
        } 