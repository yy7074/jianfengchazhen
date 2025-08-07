from sqlalchemy.orm import Session
from models import SystemConfig
from schemas import SystemConfigUpdate
from typing import Optional, Dict, List

class ConfigService:
    
    @staticmethod
    def get_config(db: Session, key: str, default_value: str = None) -> str:
        """获取配置值"""
        config = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
        if config:
            return config.config_value
        return default_value
    
    @staticmethod
    def set_config(db: Session, key: str, value: str, description: str = None) -> SystemConfig:
        """设置配置值"""
        config = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
        
        if config:
            # 更新现有配置
            config.config_value = value
            if description:
                config.description = description
        else:
            # 创建新配置
            config = SystemConfig(
                config_key=key,
                config_value=value,
                description=description
            )
            db.add(config)
        
        db.commit()
        db.refresh(config)
        return config
    
    @staticmethod
    def get_all_configs(db: Session) -> List[SystemConfig]:
        """获取所有配置"""
        return db.query(SystemConfig).all()
    
    @staticmethod
    def get_configs_dict(db: Session) -> Dict[str, str]:
        """获取所有配置的字典形式"""
        configs = db.query(SystemConfig).all()
        return {config.config_key: config.config_value for config in configs}
    
    @staticmethod
    def update_multiple_configs(db: Session, config_updates: List[SystemConfigUpdate]) -> bool:
        """批量更新配置"""
        try:
            for update in config_updates:
                ConfigService.set_config(
                    db, 
                    update.config_key, 
                    update.config_value, 
                    update.description
                )
            return True
        except Exception:
            db.rollback()
            return False
    
    @staticmethod
    def delete_config(db: Session, key: str) -> bool:
        """删除配置"""
        config = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
        if config:
            db.delete(config)
            db.commit()
            return True
        return False
    
    @staticmethod
    def init_default_configs(db: Session):
        """初始化默认配置"""
        default_configs = [
            ("coin_to_rmb_rate", "1000", "金币兑换人民币比例（多少金币=1元）"),
            ("min_withdraw_amount", "10", "最小提现金额（元）"),
            ("max_withdraw_amount", "500", "最大提现金额（元）"),
            ("daily_ad_limit", "20", "每日广告观看上限"),
            ("game_reward_coins", "5", "完成一局游戏奖励金币"),
            ("register_reward_coins", "100", "注册奖励金币"),
            ("level_up_reward_coins", "50", "升级奖励金币"),
            ("max_daily_game_rewards", "10", "每日最大游戏奖励次数")
        ]
        
        for key, value, description in default_configs:
            existing = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
            if not existing:
                config = SystemConfig(
                    config_key=key,
                    config_value=value,
                    description=description
                )
                db.add(config)
        
        db.commit()
    
    # 常用配置的便捷方法
    @staticmethod
    def get_coin_to_rmb_rate(db: Session) -> float:
        """获取金币兑换人民币比例"""
        return float(ConfigService.get_config(db, "coin_to_rmb_rate", "1000"))
    
    @staticmethod
    def get_min_withdraw_amount(db: Session) -> float:
        """获取最小提现金额"""
        return float(ConfigService.get_config(db, "min_withdraw_amount", "10"))
    
    @staticmethod
    def get_max_withdraw_amount(db: Session) -> float:
        """获取最大提现金额"""
        return float(ConfigService.get_config(db, "max_withdraw_amount", "500"))
    
    @staticmethod
    def get_daily_ad_limit(db: Session) -> int:
        """获取每日广告观看上限"""
        return int(ConfigService.get_config(db, "daily_ad_limit", "20"))
    
    @staticmethod
    def get_game_reward_coins(db: Session) -> float:
        """获取游戏奖励金币"""
        return float(ConfigService.get_config(db, "game_reward_coins", "5"))
    
    @staticmethod
    def get_register_reward_coins(db: Session) -> float:
        """获取注册奖励金币"""
        return float(ConfigService.get_config(db, "register_reward_coins", "100")) 