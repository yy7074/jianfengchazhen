from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

# 基础响应模型
class BaseResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[dict] = None

# 用户相关模型
class UserRegister(BaseModel):
    device_id: str = Field(..., min_length=1, max_length=64)
    nickname: Optional[str] = Field(None, max_length=50)

class UserLogin(BaseModel):
    device_id: str = Field(..., min_length=1, max_length=64)

class UserInfo(BaseModel):
    id: int
    device_id: str
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
    video_url: str = Field(..., max_length=500)
    duration: int = Field(..., gt=0)
    reward_coins: Decimal = Field(default=0, ge=0)
    daily_limit: int = Field(default=10, ge=1)
    min_watch_duration: int = Field(default=15, ge=1)
    weight: int = Field(default=1, ge=1)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class AdConfigUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    video_url: Optional[str] = Field(None, max_length=500)
    duration: Optional[int] = Field(None, gt=0)
    reward_coins: Optional[Decimal] = Field(None, ge=0)
    daily_limit: Optional[int] = Field(None, ge=1)
    min_watch_duration: Optional[int] = Field(None, ge=1)
    weight: Optional[int] = Field(None, ge=1)
    status: Optional[int] = Field(None, ge=0, le=1)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class AdConfigInfo(BaseModel):
    id: int
    name: str
    video_url: str
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
    ad_id: int
    watch_duration: int = Field(..., ge=1)
    device_info: Optional[str] = None

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