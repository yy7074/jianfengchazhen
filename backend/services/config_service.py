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
            ("coin_to_rmb_rate", "33000", "金币兑换人民币比例（多少金币=1元）"),
            ("min_withdraw_amount", "0.5", "最小提现金额（元）"),
            ("max_withdraw_amount", "30", "最大提现金额（元）"),
            ("daily_ad_limit", "20", "每日广告观看上限"),
            ("game_reward_coins", "5", "完成一局游戏奖励金币"),
            ("register_reward_coins", "100", "注册奖励金币"),
            ("level_up_reward_coins", "50", "升级奖励金币"),
            ("max_daily_game_rewards", "10", "每日最大游戏奖励次数"),
            # 广告奖励配置
            ("ad_reward_coins_min", "50", "观看广告最小奖励金币"),
            ("ad_reward_coins_max", "200", "观看广告最大奖励金币"),
            ("ad_reward_coins_default", "100", "观看广告默认奖励金币"),
            ("video_ad_min_duration", "15", "视频广告最小观看时长（秒）"),
            ("webpage_ad_min_duration", "10", "网页广告最小观看时长（秒）"),
            # 兑换比例设置
            ("exchange_rate_enabled", "1", "是否启用动态汇率（1启用，0禁用）"),
            ("exchange_rate_update_interval", "3600", "汇率更新间隔（秒）"),
            ("withdrawal_fee_rate", "0", "提现手续费率（百分比，0表示免费）"),
            ("withdrawal_min_coins", "1000", "提现最小金币数量"),
            ("daily_withdraw_limit", "1", "每日提现次数限制")
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
        return float(ConfigService.get_config(db, "coin_to_rmb_rate", "33000"))
    
    @staticmethod
    def get_min_withdraw_amount(db: Session) -> float:
        """获取最小提现金额"""
        return float(ConfigService.get_config(db, "min_withdraw_amount", "10"))
    
    @staticmethod
    def get_max_withdraw_amount(db: Session) -> float:
        """获取最大提现金额"""
        return float(ConfigService.get_config(db, "max_withdraw_amount", "500"))
    
    @staticmethod
    def get_daily_withdraw_limit(db: Session) -> int:
        """获取每日提现次数限制"""
        return int(ConfigService.get_config(db, "daily_withdraw_limit", "1"))
    
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
    
    # 新增广告奖励相关配置方法
    @staticmethod
    def get_ad_reward_coins_range(db: Session) -> tuple:
        """获取广告奖励金币范围"""
        min_coins = float(ConfigService.get_config(db, "ad_reward_coins_min", "50"))
        max_coins = float(ConfigService.get_config(db, "ad_reward_coins_max", "200"))
        return min_coins, max_coins
    
    @staticmethod
    def get_ad_reward_coins_default(db: Session) -> float:
        """获取默认广告奖励金币"""
        return float(ConfigService.get_config(db, "ad_reward_coins_default", "100"))
    
    @staticmethod
    def get_video_ad_min_duration(db: Session) -> int:
        """获取视频广告最小观看时长"""
        return int(ConfigService.get_config(db, "video_ad_min_duration", "15"))
    
    @staticmethod
    def get_webpage_ad_min_duration(db: Session) -> int:
        """获取网页广告最小观看时长"""
        return int(ConfigService.get_config(db, "webpage_ad_min_duration", "10"))
    
    # 新增兑换比例相关配置方法
    @staticmethod
    def get_withdrawal_fee_rate(db: Session) -> float:
        """获取提现手续费率"""
        return float(ConfigService.get_config(db, "withdrawal_fee_rate", "0"))
    
    @staticmethod
    def get_withdrawal_min_coins(db: Session) -> float:
        """获取提现最小金币数量"""
        return float(ConfigService.get_config(db, "withdrawal_min_coins", "1000"))
    
    @staticmethod
    def is_exchange_rate_enabled(db: Session) -> bool:
        """是否启用动态汇率"""
        return ConfigService.get_config(db, "exchange_rate_enabled", "1") == "1"
    
    @staticmethod
    def get_exchange_rate_update_interval(db: Session) -> int:
        """获取汇率更新间隔"""
        return int(ConfigService.get_config(db, "exchange_rate_update_interval", "3600"))
    
    @staticmethod
    def calculate_rmb_amount(db: Session, coins: float) -> float:
        """根据配置计算金币对应的人民币金额"""
        rate = ConfigService.get_coin_to_rmb_rate(db)
        return round(coins / rate, 2)
    
    @staticmethod
    def calculate_coins_needed(db: Session, rmb_amount: float) -> float:
        """根据配置计算人民币对应需要的金币数量"""
        rate = ConfigService.get_coin_to_rmb_rate(db)
        return round(rmb_amount * rate, 2) 