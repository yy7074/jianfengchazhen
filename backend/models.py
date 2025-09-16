from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, Text, Enum, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class UserStatus(enum.Enum):
    ACTIVE = 1
    DISABLED = 0

class AdStatus(enum.Enum):
    ACTIVE = 1
    DISABLED = 0

class TransactionType(enum.Enum):
    AD_REWARD = "ad_reward"
    GAME_REWARD = "game_reward"
    WITHDRAW = "withdraw"
    REGISTER_REWARD = "register_reward"
    ADMIN_ADJUST = "admin_adjust"

class WithdrawStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"

class AdminRole(enum.Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    OPERATOR = "operator"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(64), unique=True, nullable=False, comment="设备唯一标识")
    device_name = Column(String(100), comment="设备名称（手机型号等）")
    username = Column(String(50), unique=True, comment="用户名（可选）")
    nickname = Column(String(50), comment="昵称")
    avatar = Column(String(255), comment="头像URL")
    coins = Column(DECIMAL(10, 2), default=0, comment="金币余额")
    total_coins = Column(DECIMAL(10, 2), default=0, comment="历史总金币")
    level = Column(Integer, default=1, comment="用户等级")
    experience = Column(Integer, default=0, comment="用户经验值")
    game_count = Column(Integer, default=0, comment="游戏次数")
    best_score = Column(Integer, default=0, comment="最高分")
    last_login_time = Column(DateTime, comment="最后登录时间")
    register_time = Column(DateTime, default=func.now())
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, comment="状态")
    
    # 关系
    ad_watch_records = relationship("AdWatchRecord", back_populates="user")
    coin_transactions = relationship("CoinTransaction", back_populates="user")
    withdraw_requests = relationship("WithdrawRequest", back_populates="user")
    game_records = relationship("GameRecord", back_populates="user")

class AdConfig(Base):
    __tablename__ = "ad_configs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="广告名称")
    ad_type = Column(String(20), default="video", comment="广告类型：video=视频广告, webpage=网页广告")
    video_url = Column(String(1000), comment="视频文件URL（视频广告用）")
    webpage_url = Column(String(500), comment="网页跳转URL（网页广告用）")
    image_url = Column(String(500), comment="广告图片URL")
    duration = Column(Integer, nullable=False, comment="展示时长（秒）")
    reward_coins = Column(DECIMAL(8, 2), default=0, comment="观看奖励金币")
    daily_limit = Column(Integer, default=10, comment="每日观看限制")
    min_watch_duration = Column(Integer, default=15, comment="最少观看时长（秒）")
    weight = Column(Integer, default=1, comment="权重（用于随机选择）")
    status = Column(Enum(AdStatus), default=AdStatus.ACTIVE, comment="状态")
    start_time = Column(DateTime, comment="开始时间")
    end_time = Column(DateTime, comment="结束时间")
    created_time = Column(DateTime, default=func.now())
    updated_time = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 关系
    watch_records = relationship("AdWatchRecord", back_populates="ad")

class AdWatchRecord(Base):
    __tablename__ = "ad_watch_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ad_id = Column(Integer, ForeignKey("ad_configs.id"), nullable=False)
    watch_duration = Column(Integer, nullable=False, comment="实际观看时长（秒）")
    reward_coins = Column(DECIMAL(8, 2), default=0, comment="获得金币")
    is_completed = Column(Integer, default=0, comment="是否完整观看")
    ip_address = Column(String(45), comment="IP地址")
    device_info = Column(Text, comment="设备信息")
    watch_time = Column(DateTime, default=func.now())
    
    # 关系
    user = relationship("User", back_populates="ad_watch_records")
    ad = relationship("AdConfig", back_populates="watch_records")
    
    # 索引
    __table_args__ = (
        Index('idx_user_date', 'user_id', func.date('watch_time')),
        Index('idx_ad_date', 'ad_id', func.date('watch_time')),
    )

class SystemConfig(Base):
    __tablename__ = "system_configs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    config_key = Column(String(50), unique=True, nullable=False)
    config_value = Column(Text, nullable=False)
    description = Column(String(200), comment="配置描述")
    updated_time = Column(DateTime, default=func.now(), onupdate=func.now())

class CoinTransaction(Base):
    __tablename__ = "coin_transactions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False, comment="金币数量（正数为收入，负数为支出）")
    balance_after = Column(DECIMAL(10, 2), nullable=False, comment="操作后余额")
    description = Column(String(200), comment="描述")
    related_id = Column(Integer, comment="关联ID（如广告ID、游戏记录ID等）")
    created_time = Column(DateTime, default=func.now())
    
    # 关系
    user = relationship("User", back_populates="coin_transactions")
    
    # 索引
    __table_args__ = (
        Index('idx_user_time', 'user_id', 'created_time'),
    )

class WithdrawRequest(Base):
    __tablename__ = "withdraw_requests"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(DECIMAL(8, 2), nullable=False, comment="提现金额（人民币）")
    coins_used = Column(DECIMAL(10, 2), nullable=False, comment="消耗金币数量")
    alipay_account = Column(String(100), comment="支付宝账号")
    real_name = Column(String(50), comment="真实姓名")
    status = Column(Enum(WithdrawStatus), default=WithdrawStatus.PENDING)
    admin_note = Column(Text, comment="管理员备注")
    request_time = Column(DateTime, default=func.now())
    process_time = Column(DateTime, comment="处理时间")
    
    # 关系
    user = relationship("User", back_populates="withdraw_requests")
    
    # 索引
    __table_args__ = (
        Index('idx_user_status', 'user_id', 'status'),
    )

class GameRecord(Base):
    __tablename__ = "game_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    score = Column(Integer, nullable=False, comment="游戏得分")
    duration = Column(Integer, nullable=False, comment="游戏时长（秒）")
    needles_inserted = Column(Integer, default=0, comment="成功插入针数")
    reward_coins = Column(DECIMAL(8, 2), default=0, comment="奖励金币")
    play_time = Column(DateTime, default=func.now())
    
    # 关系
    user = relationship("User", back_populates="game_records")
    
    # 索引
    __table_args__ = (
        Index('idx_user_score', 'user_id', 'score'),
        Index('idx_score_time', 'score', 'play_time'),
    )

class UserLevelConfig(Base):
    __tablename__ = "user_level_configs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(Integer, unique=True, nullable=False, comment="用户等级")
    level_name = Column(String(50), nullable=False, comment="等级名称")
    ad_coin_multiplier = Column(DECIMAL(3, 2), default=1.00, comment="广告金币倍数")
    game_coin_multiplier = Column(DECIMAL(3, 2), default=1.00, comment="游戏金币倍数")
    min_experience = Column(Integer, default=0, comment="该等级所需最小经验值")
    max_experience = Column(Integer, comment="该等级最大经验值（null表示无上限）")
    description = Column(Text, comment="等级描述")
    is_active = Column(Integer, default=1, comment="是否启用：1启用，0禁用")
    created_time = Column(DateTime, default=func.now())
    updated_time = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 索引
    __table_args__ = (
        Index('idx_level', 'level'),
        Index('idx_experience_range', 'min_experience', 'max_experience'),
    )

class Admin(Base):
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), comment="邮箱")
    role = Column(Enum(AdminRole), default=AdminRole.ADMIN)
    last_login_time = Column(DateTime)
    created_time = Column(DateTime, default=func.now())
    status = Column(Integer, default=1, comment="状态：1正常，0禁用") 