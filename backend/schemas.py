from pydantic import BaseModel, Field
from typing import Optional, List, Union, Any
from datetime import datetime
from decimal import Decimal

# 基础响应模型
class BaseResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[Union[dict, list, Any]] = None

# 用户相关模型
class UserRegister(BaseModel):
    device_id: str = Field(..., min_length=1, max_length=64)
    device_name: Optional[str] = Field(None, max_length=100, description="设备名称（手机型号等）")
    nickname: Optional[str] = Field(None, max_length=50)

class UserLogin(BaseModel):
    device_id: str = Field(..., min_length=1, max_length=64)

class UserInfo(BaseModel):
    id: int
    device_id: str
    device_name: Optional[str]
    username: Optional[str]
    nickname: Optional[str]
    avatar: Optional[str]
    coins: Decimal
    total_coins: Decimal
    level: int
    experience: int
    game_count: int
    best_score: int
    last_login_time: Optional[datetime]
    register_time: datetime
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    nickname: Optional[str] = Field(None, max_length=50)
    avatar: Optional[str] = Field(None, max_length=255)

# 广告相关模型
class AdConfigCreate(BaseModel):
    name: str = Field(..., max_length=100)
    ad_type: str = Field(default="video", pattern="^(video|webpage)$")
    video_url: Optional[str] = Field(None, max_length=500)
    webpage_url: Optional[str] = Field(None, max_length=500) 
    image_url: Optional[str] = Field(None, max_length=500)
    duration: int = Field(..., gt=0)
    reward_coins: Decimal = Field(default=0, ge=0)
    daily_limit: int = Field(default=10, ge=1)
    min_watch_duration: int = Field(default=15, ge=1)
    weight: int = Field(default=1, ge=1)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class AdConfigUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    ad_type: Optional[str] = Field(None, pattern="^(video|webpage)$")
    video_url: Optional[str] = Field(None, max_length=500)
    webpage_url: Optional[str] = Field(None, max_length=500)
    image_url: Optional[str] = Field(None, max_length=500)
    duration: Optional[int] = Field(None, gt=0)
    reward_coins: Optional[Decimal] = Field(None, ge=0)
    daily_limit: Optional[int] = Field(None, ge=1)
    min_watch_duration: Optional[int] = Field(None, ge=1)
    weight: Optional[int] = Field(None, ge=1)
    status: Optional[str] = Field(None, pattern="^(ACTIVE|INACTIVE)$")
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class AdConfigInfo(BaseModel):
    id: int
    name: str
    ad_type: str
    video_url: Optional[str] = None
    webpage_url: Optional[str] = None
    image_url: Optional[str] = None
    duration: int
    reward_coins: Decimal
    daily_limit: int
    min_watch_duration: int
    weight: int
    status: int
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    created_time: datetime
    updated_time: datetime
    
    class Config:
        from_attributes = True

class AdWatchRequest(BaseModel):
    ad_id: str  # Android客户端发送字符串类型的ID
    watch_duration: int = Field(..., ge=1)
    is_completed: bool = Field(default=True)  # 是否完整观看
    skip_time: Optional[int] = Field(default=0)  # 跳过时间
    device_info: Optional[str] = None
    user_id: Optional[str] = None  # Android客户端会发送这个字段
    timestamp: Optional[int] = None  # 时间戳

class AdWatchRecord(BaseModel):
    id: int
    user_id: int
    ad_id: int
    watch_duration: int
    reward_coins: Decimal
    is_completed: int
    watch_time: datetime
    
    class Config:
        from_attributes = True

# 游戏相关模型
class GameResultSubmit(BaseModel):
    score: int = Field(..., ge=0)
    duration: int = Field(..., ge=1)
    needles_inserted: int = Field(default=0, ge=0)

class GameRecord(BaseModel):
    id: int
    user_id: int
    score: int
    duration: int
    needles_inserted: int
    reward_coins: Decimal
    play_time: datetime
    
    class Config:
        from_attributes = True

# 金币相关模型
class CoinTransaction(BaseModel):
    id: int
    user_id: int
    type: str
    amount: Decimal
    balance_after: Decimal
    description: Optional[str]
    created_time: datetime
    
    class Config:
        from_attributes = True

class WithdrawRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)
    alipay_account: str = Field(..., min_length=1, max_length=100)
    real_name: str = Field(..., min_length=1, max_length=50)

class WithdrawInfo(BaseModel):
    id: int
    user_id: int
    amount: Decimal
    coins_used: Decimal
    alipay_account: str
    real_name: str
    status: str
    admin_note: Optional[str]
    request_time: datetime
    process_time: Optional[datetime]
    
    class Config:
        from_attributes = True

# 系统配置模型
class SystemConfigUpdate(BaseModel):
    config_key: str
    config_value: str
    description: Optional[str] = None

class SystemConfigInfo(BaseModel):
    id: int
    config_key: str
    config_value: str
    description: Optional[str]
    updated_time: datetime
    
    class Config:
        from_attributes = True

# 排行榜模型
class LeaderboardEntry(BaseModel):
    rank: int
    user_id: int
    nickname: Optional[str]
    score: int
    play_time: datetime

# 统计数据模型
class UserStats(BaseModel):
    total_users: int
    active_users_today: int
    total_games: int
    total_ads_watched: int
    total_coins_distributed: Decimal

class AdminStats(BaseModel):
    user_stats: UserStats
    pending_withdraws: int
    total_withdraw_amount: Decimal
    active_ads: int

# 管理员相关模型
class AdminLogin(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=6)

class AdminInfo(BaseModel):
    id: int
    username: str
    email: Optional[str]
    role: str
    last_login_time: Optional[datetime]
    created_time: datetime
    status: int
    
    class Config:
        from_attributes = True

class AdminCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=6)
    email: Optional[str] = Field(None, max_length=100)
    role: str = Field(default="admin")

# 分页模型
class PageParams(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)

class PageResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    size: int
    pages: int

# 用户等级配置相关模型
class UserLevelConfigCreate(BaseModel):
    level: int = Field(..., ge=1, le=100, description="用户等级")
    level_name: str = Field(..., max_length=50, description="等级名称")
    ad_coin_multiplier: Decimal = Field(default=1.00, ge=0.1, le=10.0, description="广告金币倍数")
    game_coin_multiplier: Decimal = Field(default=1.00, ge=0.1, le=10.0, description="游戏金币倍数")
    min_experience: int = Field(default=0, ge=0, description="该等级所需最小经验值")
    max_experience: Optional[int] = Field(None, ge=0, description="该等级最大经验值")
    description: Optional[str] = Field(None, description="等级描述")
    is_active: int = Field(default=1, description="是否启用")

class UserLevelConfigUpdate(BaseModel):
    level_name: Optional[str] = Field(None, max_length=50, description="等级名称")
    ad_coin_multiplier: Optional[Decimal] = Field(None, ge=0.1, le=10.0, description="广告金币倍数")
    game_coin_multiplier: Optional[Decimal] = Field(None, ge=0.1, le=10.0, description="游戏金币倍数")
    min_experience: Optional[int] = Field(None, ge=0, description="该等级所需最小经验值")
    max_experience: Optional[int] = Field(None, ge=0, description="该等级最大经验值")
    description: Optional[str] = Field(None, description="等级描述")
    is_active: Optional[int] = Field(None, description="是否启用")

class UserLevelConfigInfo(BaseModel):
    id: int
    level: int
    level_name: str
    ad_coin_multiplier: Decimal
    game_coin_multiplier: Decimal
    min_experience: int
    max_experience: Optional[int]
    description: Optional[str]
    is_active: int
    created_time: datetime
    updated_time: datetime
    
    class Config:
        from_attributes = True 