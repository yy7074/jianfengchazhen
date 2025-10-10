from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_
from database import get_db
from schemas import *
from services.user_service import UserService
from services.ad_service import AdService
from services.config_service import ConfigService
from services.version_service import VersionService
from models import *
from typing import List
import os
from datetime import date, datetime, timedelta

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# 简单的管理员认证（生产环境应使用更安全的方式）
def verify_admin():
    # 这里应该实现真正的管理员认证
    # 暂时返回True，实际项目中需要JWT或Session认证
    return True

# 管理后台首页
@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    """管理后台首页"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    # 获取统计数据
    today = date.today()
    
    # 用户统计
    total_users = db.query(func.count(User.id)).scalar() or 0
    today_users = db.query(func.count(User.id)).filter(
        func.date(User.register_time) == today
    ).scalar() or 0
    active_users = db.query(func.count(User.id)).filter(
        func.date(User.last_login_time) == today
    ).scalar() or 0
    
    # 游戏统计
    total_games = db.query(func.count(GameRecord.id)).scalar() or 0
    today_games = db.query(func.count(GameRecord.id)).filter(
        func.date(GameRecord.play_time) == today
    ).scalar() or 0
    
    # 广告统计
    total_ads_watched = db.query(func.count(AdWatchRecord.id)).scalar() or 0
    today_ads = db.query(func.count(AdWatchRecord.id)).filter(
        func.date(AdWatchRecord.watch_time) == today
    ).scalar() or 0
    
    # 金币统计
    total_coins = db.query(func.sum(CoinTransaction.amount)).filter(
        CoinTransaction.amount > 0
    ).scalar() or 0
    today_coins = db.query(func.sum(CoinTransaction.amount)).filter(
        CoinTransaction.amount > 0,
        func.date(CoinTransaction.created_time) == today
    ).scalar() or 0
    
    # 提现统计
    pending_withdraws = db.query(func.count(WithdrawRequest.id)).filter(
        WithdrawRequest.status == WithdrawStatus.PENDING
    ).scalar() or 0
    
    stats = {
        "users": {"total": total_users, "today": today_users, "active": active_users},
        "games": {"total": total_games, "today": today_games},
        "ads": {"total": total_ads_watched, "today": today_ads},
        "coins": {"total": float(total_coins), "today": float(today_coins)},
        "withdraws": {"pending": pending_withdraws}
    }
    
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "stats": stats
    })

# 提现管理页面
@router.get("/withdraws", response_class=HTMLResponse)
async def withdraw_management_page(request: Request):
    """提现审核管理页面"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    return templates.TemplateResponse("admin/withdraw_management.html", {
        "request": request
    })

# 等级管理页面
@router.get("/levels", response_class=HTMLResponse)
async def level_management_page(request: Request):
    """等级管理页面"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    return templates.TemplateResponse("admin/level_management.html", {
        "request": request
    })

# API接口
@router.get("/api/stats")
async def get_admin_stats(db: Session = Depends(get_db)):
    """获取管理后台统计数据API"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    today = date.today()
    
    # 详细统计数据
    stats = {
        "users": {
            "total": db.query(func.count(User.id)).scalar() or 0,
            "today_new": db.query(func.count(User.id)).filter(
                func.date(User.register_time) == today
            ).scalar() or 0,
            "today_active": db.query(func.count(User.id)).filter(
                func.date(User.last_login_time) == today
            ).scalar() or 0,
            "total_coins": db.query(func.sum(User.coins)).scalar() or 0
        },
        "games": {
            "total": db.query(func.count(GameRecord.id)).scalar() or 0,
            "today": db.query(func.count(GameRecord.id)).filter(
                func.date(GameRecord.play_time) == today
            ).scalar() or 0,
            "avg_score": db.query(func.avg(GameRecord.score)).scalar() or 0,
            "max_score": db.query(func.max(GameRecord.score)).scalar() or 0
        },
        "ads": {
            "total_views": db.query(func.count(AdWatchRecord.id)).scalar() or 0,
            "today_views": db.query(func.count(AdWatchRecord.id)).filter(
                func.date(AdWatchRecord.watch_time) == today
            ).scalar() or 0,
            "total_rewards": db.query(func.sum(AdWatchRecord.reward_coins)).scalar() or 0,
            "active_ads": db.query(func.count(AdConfig.id)).filter(
                AdConfig.status == AdStatus.ACTIVE
            ).scalar() or 0
        },
        "withdraws": {
            "pending": db.query(func.count(WithdrawRequest.id)).filter(
                WithdrawRequest.status == WithdrawStatus.PENDING
            ).scalar() or 0,
            "pending_amount": db.query(func.sum(WithdrawRequest.amount)).filter(
                WithdrawRequest.status == WithdrawStatus.PENDING
            ).scalar() or 0,
            "completed": db.query(func.count(WithdrawRequest.id)).filter(
                WithdrawRequest.status == WithdrawStatus.COMPLETED
            ).scalar() or 0,
            "completed_amount": db.query(func.sum(WithdrawRequest.amount)).filter(
                WithdrawRequest.status == WithdrawStatus.COMPLETED
            ).scalar() or 0
        }
    }
    
    return BaseResponse(message="获取成功", data=stats)

# 用户管理
@router.get("/api/users")
async def get_users_list(
    page: int = 1,
    size: int = 20,
    search: str = None,
    db: Session = Depends(get_db)
):
    """获取用户列表"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    query = db.query(User)
    
    if search:
        query = query.filter(
            or_(
                User.device_id.contains(search),
                User.nickname.contains(search),
                User.username.contains(search)
            )
        )
    
    total = query.count()
    skip = (page - 1) * size
    users = query.order_by(User.register_time.desc()).offset(skip).limit(size).all()
    
    # 手动构建用户数据，避免Pydantic验证问题
    users_data = []
    for user in users:
        user_data = {
            "id": user.id,
            "device_id": user.device_id,
            "device_name": user.device_name,
            "username": user.username,
            "nickname": user.nickname,
            "avatar": user.avatar,
            "coins": float(user.coins or 0),
            "total_coins": float(user.total_coins or 0),
            "level": user.level or 1,
            "experience": user.experience or 0,
            "game_count": user.game_count or 0,
            "best_score": user.best_score or 0,
            "last_login_time": user.last_login_time.isoformat() if user.last_login_time else None,
            "register_time": user.register_time.isoformat() if user.register_time else None
        }
        users_data.append(user_data)
    
    return BaseResponse(
        message="获取成功",
        data={
            "items": users_data,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    )

# 用户等级管理
@router.get("/api/levels")
async def get_level_configs(db: Session = Depends(get_db)):
    """获取所有等级配置"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    from services.level_service import LevelService
    levels = LevelService.get_all_level_configs(db)
    
    levels_data = []
    for level in levels:
        level_data = {
            "id": level.id,
            "level": level.level,
            "level_name": level.level_name,
            "ad_coin_multiplier": float(level.ad_coin_multiplier),
            "game_coin_multiplier": float(level.game_coin_multiplier),
            "min_experience": level.min_experience,
            "max_experience": level.max_experience,
            "description": level.description,
            "is_active": level.is_active,
            "created_time": level.created_time.isoformat() if level.created_time else None,
            "updated_time": level.updated_time.isoformat() if level.updated_time else None
        }
        levels_data.append(level_data)
    
    return BaseResponse(
        message="获取成功",
        data=levels_data
    )

@router.post("/api/levels")
async def create_level_config(level_data: UserLevelConfigCreate, db: Session = Depends(get_db)):
    """创建等级配置"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    from services.level_service import LevelService
    from models import UserLevelConfig
    
    # 检查等级是否已存在
    existing_level = db.query(UserLevelConfig).filter(UserLevelConfig.level == level_data.level).first()
    if existing_level:
        raise HTTPException(status_code=400, detail="该等级已存在")
    
    level_config = LevelService.create_level_config(db, level_data)
    return BaseResponse(
        message="创建成功",
        data={
            "id": level_config.id,
            "level": level_config.level,
            "level_name": level_config.level_name,
            "ad_coin_multiplier": float(level_config.ad_coin_multiplier),
            "game_coin_multiplier": float(level_config.game_coin_multiplier),
            "min_experience": level_config.min_experience,
            "max_experience": level_config.max_experience,
            "description": level_config.description,
            "is_active": level_config.is_active
        }
    )

@router.put("/api/levels/{level_id}")
async def update_level_config(level_id: int, level_data: UserLevelConfigUpdate, db: Session = Depends(get_db)):
    """更新等级配置"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    from services.level_service import LevelService
    level_config = LevelService.update_level_config(db, level_id, level_data)
    if not level_config:
        raise HTTPException(status_code=404, detail="等级配置不存在")
    
    return BaseResponse(
        message="更新成功",
        data={
            "id": level_config.id,
            "level": level_config.level,
            "level_name": level_config.level_name,
            "ad_coin_multiplier": float(level_config.ad_coin_multiplier),
            "game_coin_multiplier": float(level_config.game_coin_multiplier),
            "min_experience": level_config.min_experience,
            "max_experience": level_config.max_experience,
            "description": level_config.description,
            "is_active": level_config.is_active
        }
    )

@router.delete("/api/levels/{level_id}")
async def delete_level_config(level_id: int, db: Session = Depends(get_db)):
    """删除等级配置"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    from services.level_service import LevelService
    success = LevelService.delete_level_config(db, level_id)
    if not success:
        raise HTTPException(status_code=404, detail="等级配置不存在")
    
    return BaseResponse(message="删除成功")

@router.get("/api/level-stats")
async def get_level_stats(db: Session = Depends(get_db)):
    """获取等级统计信息"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    from services.level_service import LevelService
    stats = LevelService.get_level_stats(db)
    
    return BaseResponse(
        message="获取成功",
        data=stats
    )

# 用户编辑
@router.put("/api/users/{user_id}")
async def update_user(
    user_id: int, 
    user_data: dict,
    db: Session = Depends(get_db)
):
    """更新用户信息"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新允许编辑的字段
    if "nickname" in user_data:
        user.nickname = user_data["nickname"]
    if "coins" in user_data:
        user.coins = float(user_data["coins"])
    if "level" in user_data:
        user.level = int(user_data["level"])
    if "experience" in user_data:
        user.experience = int(user_data["experience"])
    
    try:
        db.commit()
        db.refresh(user)
        return BaseResponse(message="用户信息更新成功")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="更新失败")

# 广告管理
@router.get("/api/ads")
async def get_ads_list(db: Session = Depends(get_db)):
    """获取广告列表"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    ads = AdService.get_all_ad_configs(db)
    # 临时简化，避免Pydantic验证问题
    ads_data = []
    for ad in ads:
        # 处理状态值，兼容不同的数据类型
        status_value = ad.status
        if hasattr(status_value, 'value'):  # 如果是枚举
            is_active = status_value.value == 1
        else:  # 如果是字符串
            is_active = str(status_value).upper() == 'ACTIVE'
        
        ad_data = {
            "id": ad.id,
            "name": ad.name,
            "ad_type": ad.ad_type or "video",
            "video_url": ad.video_url,
            "webpage_url": ad.webpage_url,
            "image_url": ad.image_url,
            "duration": ad.duration,
            "reward_coins": float(ad.reward_coins or 0),
            "weight": ad.weight or 1,
            "status": 1 if is_active else 0
        }
        ads_data.append(ad_data)
    
    return BaseResponse(
        message="获取成功",
        data=ads_data
    )

@router.post("/api/ads")
async def create_ad(ad_data: AdConfigCreate, db: Session = Depends(get_db)):
    """创建广告"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    ad = AdService.create_ad_config(db, ad_data)
    return BaseResponse(
        message="创建成功",
        data=AdConfigInfo.from_orm(ad).dict()
    )

@router.put("/api/ads/{ad_id}")
async def update_ad(ad_id: int, ad_data: AdConfigUpdate, db: Session = Depends(get_db)):
    """更新广告"""
    try:
        if not verify_admin():
            raise HTTPException(status_code=401, detail="需要管理员权限")
        
        # 验证广告ID
        if ad_id <= 0:
            raise HTTPException(status_code=400, detail="无效的广告ID")
        
        ad = AdService.update_ad_config(db, ad_id, ad_data)
        if not ad:
            raise HTTPException(status_code=404, detail="广告不存在")
        
        # 处理状态值，兼容不同的数据类型
        status_value = ad.status
        if hasattr(status_value, 'value'):  # 如果是枚举
            is_active = status_value.value == 1
        else:  # 如果是字符串
            is_active = str(status_value).upper() == 'ACTIVE'
        
        # 手动构建响应数据，避免Pydantic序列化问题
        ad_data_dict = {
            "id": ad.id,
            "name": ad.name,
            "ad_type": ad.ad_type,
            "video_url": ad.video_url,
            "webpage_url": ad.webpage_url,
            "image_url": ad.image_url,
            "duration": ad.duration,
            "reward_coins": str(ad.reward_coins),  # 转换为字符串避免Decimal序列化问题
            "daily_limit": ad.daily_limit,
            "min_watch_duration": ad.min_watch_duration,
            "weight": ad.weight,
            "status": 1 if is_active else 0,
            "start_time": ad.start_time.isoformat() if ad.start_time else None,
            "end_time": ad.end_time.isoformat() if ad.end_time else None,
            "created_time": ad.created_time.isoformat() if ad.created_time else None,
            "updated_time": ad.updated_time.isoformat() if ad.updated_time else None
        }
        
        return BaseResponse(
            message="更新成功",
            data=ad_data_dict
        )
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.error(f"更新广告失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")

@router.delete("/api/ads/{ad_id}")
async def delete_ad(ad_id: int, db: Session = Depends(get_db)):
    """删除广告"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    success = AdService.delete_ad_config(db, ad_id)
    if not success:
        raise HTTPException(status_code=404, detail="广告不存在")
    
    return BaseResponse(message="删除成功")

# 文件上传
@router.post("/api/upload/video")
async def upload_video(file: UploadFile = File(...)):
    """上传广告视频"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    # 检查文件类型
    allowed_types = ["video/mp4", "video/avi", "video/mov", "video/wmv"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="不支持的视频格式")
    
    # 检查文件大小（50MB限制）
    max_size = 50 * 1024 * 1024
    if file.size > max_size:
        raise HTTPException(status_code=400, detail="视频文件过大，最大50MB")
    
    # 生成文件名
    import uuid
    file_ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{file_ext}"
    file_path = f"uploads/videos/{filename}"
    
    # 保存文件
    os.makedirs("uploads/videos", exist_ok=True)
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    return BaseResponse(
        message="上传成功",
        data={
            "filename": filename,
            "url": f"/uploads/videos/{filename}",
            "size": file.size
        }
    )

# 用户等级管理
@router.get("/api/levels")
async def get_level_configs(db: Session = Depends(get_db)):
    """获取所有等级配置"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    from services.level_service import LevelService
    levels = LevelService.get_all_level_configs(db)
    
    levels_data = []
    for level in levels:
        level_data = {
            "id": level.id,
            "level": level.level,
            "level_name": level.level_name,
            "ad_coin_multiplier": float(level.ad_coin_multiplier),
            "game_coin_multiplier": float(level.game_coin_multiplier),
            "min_experience": level.min_experience,
            "max_experience": level.max_experience,
            "description": level.description,
            "is_active": level.is_active,
            "created_time": level.created_time.isoformat() if level.created_time else None,
            "updated_time": level.updated_time.isoformat() if level.updated_time else None
        }
        levels_data.append(level_data)
    
    return BaseResponse(
        message="获取成功",
        data=levels_data
    )

@router.post("/api/levels")
async def create_level_config(level_data: UserLevelConfigCreate, db: Session = Depends(get_db)):
    """创建等级配置"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    from services.level_service import LevelService
    from models import UserLevelConfig
    
    # 检查等级是否已存在
    existing_level = db.query(UserLevelConfig).filter(UserLevelConfig.level == level_data.level).first()
    if existing_level:
        raise HTTPException(status_code=400, detail="该等级已存在")
    
    level_config = LevelService.create_level_config(db, level_data)
    return BaseResponse(
        message="创建成功",
        data={
            "id": level_config.id,
            "level": level_config.level,
            "level_name": level_config.level_name,
            "ad_coin_multiplier": float(level_config.ad_coin_multiplier),
            "game_coin_multiplier": float(level_config.game_coin_multiplier),
            "min_experience": level_config.min_experience,
            "max_experience": level_config.max_experience,
            "description": level_config.description,
            "is_active": level_config.is_active
        }
    )

@router.put("/api/levels/{level_id}")
async def update_level_config(level_id: int, level_data: UserLevelConfigUpdate, db: Session = Depends(get_db)):
    """更新等级配置"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    from services.level_service import LevelService
    level_config = LevelService.update_level_config(db, level_id, level_data)
    if not level_config:
        raise HTTPException(status_code=404, detail="等级配置不存在")
    
    return BaseResponse(
        message="更新成功",
        data={
            "id": level_config.id,
            "level": level_config.level,
            "level_name": level_config.level_name,
            "ad_coin_multiplier": float(level_config.ad_coin_multiplier),
            "game_coin_multiplier": float(level_config.game_coin_multiplier),
            "min_experience": level_config.min_experience,
            "max_experience": level_config.max_experience,
            "description": level_config.description,
            "is_active": level_config.is_active
        }
    )

@router.delete("/api/levels/{level_id}")
async def delete_level_config(level_id: int, db: Session = Depends(get_db)):
    """删除等级配置"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    from services.level_service import LevelService
    success = LevelService.delete_level_config(db, level_id)
    if not success:
        raise HTTPException(status_code=404, detail="等级配置不存在")
    
    return BaseResponse(message="删除成功")

@router.get("/api/level-stats")
async def get_level_stats(db: Session = Depends(get_db)):
    """获取等级统计信息"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    from services.level_service import LevelService
    stats = LevelService.get_level_stats(db)
    
    return BaseResponse(
        message="获取成功",
        data=stats
    )

# 系统配置
@router.get("/api/configs")
async def get_system_configs(db: Session = Depends(get_db)):
    """获取系统配置"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    configs = ConfigService.get_all_configs(db)
    return BaseResponse(
        message="获取成功",
        data=[SystemConfigInfo.from_orm(c).dict() for c in configs]
    )

@router.get("/config/{key}")
async def get_single_config(key: str, db: Session = Depends(get_db)):
    """获取单个配置"""
    config = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    return BaseResponse(
        message="获取成功",
        data=SystemConfigInfo.from_orm(config).dict()
    )

@router.put("/config/{key}")
async def update_single_config(
    key: str, 
    config_data: SystemConfigUpdate, 
    db: Session = Depends(get_db)
):
    """更新单个配置"""
    config = ConfigService.set_config(
        db, key, config_data.config_value, config_data.description
    )
    
    return BaseResponse(
        message="配置更新成功",
        data=SystemConfigInfo.from_orm(config).dict()
    )

@router.put("/api/configs")
async def update_system_configs(
    config_updates: List[SystemConfigUpdate],
    db: Session = Depends(get_db)
):
    """批量更新系统配置"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    success = ConfigService.update_multiple_configs(db, config_updates)
    if success:
        return BaseResponse(message="更新成功")
    else:
        raise HTTPException(status_code=500, detail="更新失败")

# 提现管理
@router.get("/api/withdraws")
async def get_withdraw_requests(
    status: str = None,
    page: int = 1,
    size: int = 20,
    start_date: str = None,
    end_date: str = None,
    min_amount: float = None,
    max_amount: float = None,
    user_id: int = None,
    search: str = None,
    db: Session = Depends(get_db)
):
    """获取提现申请列表（支持高级筛选）"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    query = db.query(WithdrawRequest).join(User)
    
    # 状态筛选
    if status:
        query = query.filter(WithdrawRequest.status == status)
    
    # 时间范围筛选
    if start_date:
        from datetime import datetime
        start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        query = query.filter(WithdrawRequest.request_time >= start_dt)
    
    if end_date:
        from datetime import datetime
        end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        query = query.filter(WithdrawRequest.request_time <= end_dt)
    
    # 金额范围筛选
    if min_amount is not None:
        query = query.filter(WithdrawRequest.amount >= min_amount)
    
    if max_amount is not None:
        query = query.filter(WithdrawRequest.amount <= max_amount)
    
    # 用户ID筛选
    if user_id:
        query = query.filter(WithdrawRequest.user_id == user_id)
    
    # 搜索筛选（用户昵称、支付宝账号、真实姓名）
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (User.nickname.like(search_pattern)) |
            (WithdrawRequest.alipay_account.like(search_pattern)) |
            (WithdrawRequest.real_name.like(search_pattern))
        )
    
    total = query.count()
    skip = (page - 1) * size
    withdraws = query.order_by(WithdrawRequest.request_time.desc()).offset(skip).limit(size).all()
    
    # 组装数据
    items = []
    for w in withdraws:
        item = WithdrawInfo.from_orm(w).dict()
        item["user_nickname"] = w.user.nickname
        items.append(item)
    
    # 计算统计信息
    total_amount = db.query(func.sum(WithdrawRequest.amount)).filter(
        WithdrawRequest.id.in_([w.id for w in withdraws])
    ).scalar() or 0
    
    return BaseResponse(
        message="获取成功",
        data={
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size,
            "statistics": {
                "current_page_amount": float(total_amount),
                "current_page_count": len(items)
            }
        }
    )

# 用户等级管理
@router.get("/api/levels")
async def get_level_configs(db: Session = Depends(get_db)):
    """获取所有等级配置"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    from services.level_service import LevelService
    levels = LevelService.get_all_level_configs(db)
    
    levels_data = []
    for level in levels:
        level_data = {
            "id": level.id,
            "level": level.level,
            "level_name": level.level_name,
            "ad_coin_multiplier": float(level.ad_coin_multiplier),
            "game_coin_multiplier": float(level.game_coin_multiplier),
            "min_experience": level.min_experience,
            "max_experience": level.max_experience,
            "description": level.description,
            "is_active": level.is_active,
            "created_time": level.created_time.isoformat() if level.created_time else None,
            "updated_time": level.updated_time.isoformat() if level.updated_time else None
        }
        levels_data.append(level_data)
    
    return BaseResponse(
        message="获取成功",
        data=levels_data
    )

@router.post("/api/levels")
async def create_level_config(level_data: UserLevelConfigCreate, db: Session = Depends(get_db)):
    """创建等级配置"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    from services.level_service import LevelService
    from models import UserLevelConfig
    
    # 检查等级是否已存在
    existing_level = db.query(UserLevelConfig).filter(UserLevelConfig.level == level_data.level).first()
    if existing_level:
        raise HTTPException(status_code=400, detail="该等级已存在")
    
    level_config = LevelService.create_level_config(db, level_data)
    return BaseResponse(
        message="创建成功",
        data={
            "id": level_config.id,
            "level": level_config.level,
            "level_name": level_config.level_name,
            "ad_coin_multiplier": float(level_config.ad_coin_multiplier),
            "game_coin_multiplier": float(level_config.game_coin_multiplier),
            "min_experience": level_config.min_experience,
            "max_experience": level_config.max_experience,
            "description": level_config.description,
            "is_active": level_config.is_active
        }
    )

@router.put("/api/levels/{level_id}")
async def update_level_config(level_id: int, level_data: UserLevelConfigUpdate, db: Session = Depends(get_db)):
    """更新等级配置"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    from services.level_service import LevelService
    level_config = LevelService.update_level_config(db, level_id, level_data)
    if not level_config:
        raise HTTPException(status_code=404, detail="等级配置不存在")
    
    return BaseResponse(
        message="更新成功",
        data={
            "id": level_config.id,
            "level": level_config.level,
            "level_name": level_config.level_name,
            "ad_coin_multiplier": float(level_config.ad_coin_multiplier),
            "game_coin_multiplier": float(level_config.game_coin_multiplier),
            "min_experience": level_config.min_experience,
            "max_experience": level_config.max_experience,
            "description": level_config.description,
            "is_active": level_config.is_active
        }
    )

@router.delete("/api/levels/{level_id}")
async def delete_level_config(level_id: int, db: Session = Depends(get_db)):
    """删除等级配置"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    from services.level_service import LevelService
    success = LevelService.delete_level_config(db, level_id)
    if not success:
        raise HTTPException(status_code=404, detail="等级配置不存在")
    
    return BaseResponse(message="删除成功")

@router.get("/api/level-stats")
async def get_level_stats(db: Session = Depends(get_db)):
    """获取等级统计信息"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    from services.level_service import LevelService
    stats = LevelService.get_level_stats(db)
    
    return BaseResponse(
        message="获取成功",
        data=stats
    )

@router.get("/api/withdraws/{withdraw_id}")
async def get_withdraw_detail(
    withdraw_id: int,
    db: Session = Depends(get_db)
):
    """获取提现申请详细信息"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    # 查询提现申请
    withdraw = db.query(WithdrawRequest).filter(
        WithdrawRequest.id == withdraw_id
    ).first()
    
    if not withdraw:
        raise HTTPException(status_code=404, detail="提现申请不存在")
    
    # 查询用户信息
    user = db.query(User).filter(User.id == withdraw.user_id).first()
    
    # 查询用户的提现历史
    user_withdraw_history = db.query(WithdrawRequest).filter(
        WithdrawRequest.user_id == withdraw.user_id
    ).order_by(WithdrawRequest.request_time.desc()).limit(10).all()
    
    # 查询用户的金币记录
    from models import CoinTransaction
    coin_transactions = db.query(CoinTransaction).filter(
        CoinTransaction.user_id == withdraw.user_id
    ).order_by(CoinTransaction.created_time.desc()).limit(10).all()
    
    # 计算用户统计
    total_withdraws = db.query(func.count(WithdrawRequest.id)).filter(
        WithdrawRequest.user_id == withdraw.user_id
    ).scalar() or 0
    
    total_withdraw_amount = db.query(func.sum(WithdrawRequest.amount)).filter(
        WithdrawRequest.user_id == withdraw.user_id,
        WithdrawRequest.status.in_(['approved', 'completed'])
    ).scalar() or 0
    
    # 构建详细信息
    detail_info = {
        "withdraw_info": {
            "id": withdraw.id,
            "amount": float(withdraw.amount),
            "coins_used": float(withdraw.coins_used),
            "alipay_account": withdraw.alipay_account,
            "real_name": withdraw.real_name,
            "status": withdraw.status.value if hasattr(withdraw.status, 'value') else str(withdraw.status),
            "admin_note": withdraw.admin_note,
            "request_time": withdraw.request_time.isoformat() if withdraw.request_time else None,
            "process_time": withdraw.process_time.isoformat() if withdraw.process_time else None
        },
        "user_info": {
            "id": user.id,
            "nickname": user.nickname,
            "device_id": user.device_id,
            "current_coins": float(user.coins),
            "total_coins": float(user.total_coins),
            "level": user.level,
            "register_time": user.register_time.isoformat() if user.register_time else None,
            "last_login_time": user.last_login_time.isoformat() if user.last_login_time else None
        },
        "user_statistics": {
            "total_withdraws": total_withdraws,
            "total_withdraw_amount": float(total_withdraw_amount),
            "avg_withdraw_amount": float(total_withdraw_amount / total_withdraws) if total_withdraws > 0 else 0
        },
        "recent_withdraws": [
            {
                "id": w.id,
                "amount": float(w.amount),
                "status": w.status.value if hasattr(w.status, 'value') else str(w.status),
                "request_time": w.request_time.isoformat() if w.request_time else None
            } for w in user_withdraw_history[:5]
        ],
        "recent_transactions": [
            {
                "id": t.id,
                "type": t.type.value if hasattr(t.type, 'value') else str(t.type),
                "amount": float(t.amount),
                "description": t.description,
                "created_time": t.created_time.isoformat() if t.created_time else None
            } for t in coin_transactions[:5]
        ]
    }
    
    return BaseResponse(
        message="获取成功",
        data=detail_info
    )

@router.put("/api/withdraws/{withdraw_id}/approve")
async def approve_withdraw(
    withdraw_id: int,
    request_data: dict = None,
    db: Session = Depends(get_db)
):
    """批准提现申请"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    admin_note = None
    if request_data:
        admin_note = request_data.get("admin_note")
    
    from services.withdraw_service import WithdrawService
    
    result = WithdrawService.approve_withdraw(db, withdraw_id, admin_note)
    if result["success"]:
        return BaseResponse(
            message=result["message"],
            data=result.get("data", {})
        )
    else:
        raise HTTPException(status_code=400, detail=result["message"])

@router.put("/api/withdraws/{withdraw_id}/reject")
async def reject_withdraw(
    withdraw_id: int,
    request_data: dict,
    db: Session = Depends(get_db)
):
    """拒绝提现申请"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    admin_note = request_data.get("admin_note", "").strip()
    if not admin_note:
        raise HTTPException(status_code=400, detail="拒绝时必须填写备注原因")
    
    from services.withdraw_service import WithdrawService
    
    result = WithdrawService.reject_withdraw(db, withdraw_id, admin_note)
    if result["success"]:
        return BaseResponse(
            message=result["message"],
            data=result.get("data", {})
        )
    else:
        raise HTTPException(status_code=400, detail=result["message"])

# 批量操作API
@router.post("/api/withdraws/batch-approve")
async def batch_approve_withdraws(
    request_data: dict,
    db: Session = Depends(get_db)
):
    """批量批准提现申请"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    withdraw_ids = request_data.get("withdraw_ids", [])
    admin_note = request_data.get("admin_note", "批量批准")
    
    if not withdraw_ids:
        raise HTTPException(status_code=400, detail="请选择要批准的申请")
    
    from services.withdraw_service import WithdrawService
    
    success_count = 0
    failed_items = []
    
    for withdraw_id in withdraw_ids:
        result = WithdrawService.approve_withdraw(db, withdraw_id, admin_note)
        if result["success"]:
            success_count += 1
        else:
            failed_items.append({"id": withdraw_id, "error": result["message"]})
    
    return BaseResponse(
        message=f"批量操作完成，成功{success_count}个，失败{len(failed_items)}个",
        data={
            "success_count": success_count,
            "failed_count": len(failed_items),
            "failed_items": failed_items
        }
    )

# 用户等级管理
@router.get("/api/levels")
async def get_level_configs(db: Session = Depends(get_db)):
    """获取所有等级配置"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    from services.level_service import LevelService
    levels = LevelService.get_all_level_configs(db)
    
    levels_data = []
    for level in levels:
        level_data = {
            "id": level.id,
            "level": level.level,
            "level_name": level.level_name,
            "ad_coin_multiplier": float(level.ad_coin_multiplier),
            "game_coin_multiplier": float(level.game_coin_multiplier),
            "min_experience": level.min_experience,
            "max_experience": level.max_experience,
            "description": level.description,
            "is_active": level.is_active,
            "created_time": level.created_time.isoformat() if level.created_time else None,
            "updated_time": level.updated_time.isoformat() if level.updated_time else None
        }
        levels_data.append(level_data)
    
    return BaseResponse(
        message="获取成功",
        data=levels_data
    )

@router.post("/api/levels")
async def create_level_config(level_data: UserLevelConfigCreate, db: Session = Depends(get_db)):
    """创建等级配置"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    from services.level_service import LevelService
    from models import UserLevelConfig
    
    # 检查等级是否已存在
    existing_level = db.query(UserLevelConfig).filter(UserLevelConfig.level == level_data.level).first()
    if existing_level:
        raise HTTPException(status_code=400, detail="该等级已存在")
    
    level_config = LevelService.create_level_config(db, level_data)
    return BaseResponse(
        message="创建成功",
        data={
            "id": level_config.id,
            "level": level_config.level,
            "level_name": level_config.level_name,
            "ad_coin_multiplier": float(level_config.ad_coin_multiplier),
            "game_coin_multiplier": float(level_config.game_coin_multiplier),
            "min_experience": level_config.min_experience,
            "max_experience": level_config.max_experience,
            "description": level_config.description,
            "is_active": level_config.is_active
        }
    )

@router.put("/api/levels/{level_id}")
async def update_level_config(level_id: int, level_data: UserLevelConfigUpdate, db: Session = Depends(get_db)):
    """更新等级配置"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    from services.level_service import LevelService
    level_config = LevelService.update_level_config(db, level_id, level_data)
    if not level_config:
        raise HTTPException(status_code=404, detail="等级配置不存在")
    
    return BaseResponse(
        message="更新成功",
        data={
            "id": level_config.id,
            "level": level_config.level,
            "level_name": level_config.level_name,
            "ad_coin_multiplier": float(level_config.ad_coin_multiplier),
            "game_coin_multiplier": float(level_config.game_coin_multiplier),
            "min_experience": level_config.min_experience,
            "max_experience": level_config.max_experience,
            "description": level_config.description,
            "is_active": level_config.is_active
        }
    )

@router.delete("/api/levels/{level_id}")
async def delete_level_config(level_id: int, db: Session = Depends(get_db)):
    """删除等级配置"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    from services.level_service import LevelService
    success = LevelService.delete_level_config(db, level_id)
    if not success:
        raise HTTPException(status_code=404, detail="等级配置不存在")
    
    return BaseResponse(message="删除成功")

@router.get("/api/level-stats")
async def get_level_stats(db: Session = Depends(get_db)):
    """获取等级统计信息"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    from services.level_service import LevelService
    stats = LevelService.get_level_stats(db)
    
    return BaseResponse(
        message="获取成功",
        data=stats
    )

@router.post("/api/withdraws/batch-reject")
async def batch_reject_withdraws(
    request_data: dict,
    db: Session = Depends(get_db)
):
    """批量拒绝提现申请"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    withdraw_ids = request_data.get("withdraw_ids", [])
    admin_note = request_data.get("admin_note", "批量拒绝")
    
    if not withdraw_ids:
        raise HTTPException(status_code=400, detail="请选择要拒绝的申请")
    
    if not admin_note or admin_note.strip() == "":
        raise HTTPException(status_code=400, detail="拒绝时必须填写备注")
    
    from services.withdraw_service import WithdrawService
    
    success_count = 0
    failed_items = []
    
    for withdraw_id in withdraw_ids:
        result = WithdrawService.reject_withdraw(db, withdraw_id, admin_note)
        if result["success"]:
            success_count += 1
        else:
            failed_items.append({"id": withdraw_id, "error": result["message"]})
    
    return BaseResponse(
        message=f"批量操作完成，成功{success_count}个，失败{len(failed_items)}个",
        data={
            "success_count": success_count,
            "failed_count": len(failed_items),
            "failed_items": failed_items
        }
    )

# 用户等级管理
@router.get("/api/levels")
async def get_level_configs(db: Session = Depends(get_db)):
    """获取所有等级配置"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    from services.level_service import LevelService
    levels = LevelService.get_all_level_configs(db)
    
    levels_data = []
    for level in levels:
        level_data = {
            "id": level.id,
            "level": level.level,
            "level_name": level.level_name,
            "ad_coin_multiplier": float(level.ad_coin_multiplier),
            "game_coin_multiplier": float(level.game_coin_multiplier),
            "min_experience": level.min_experience,
            "max_experience": level.max_experience,
            "description": level.description,
            "is_active": level.is_active,
            "created_time": level.created_time.isoformat() if level.created_time else None,
            "updated_time": level.updated_time.isoformat() if level.updated_time else None
        }
        levels_data.append(level_data)
    
    return BaseResponse(
        message="获取成功",
        data=levels_data
    )

@router.post("/api/levels")
async def create_level_config(level_data: UserLevelConfigCreate, db: Session = Depends(get_db)):
    """创建等级配置"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    from services.level_service import LevelService
    from models import UserLevelConfig
    
    # 检查等级是否已存在
    existing_level = db.query(UserLevelConfig).filter(UserLevelConfig.level == level_data.level).first()
    if existing_level:
        raise HTTPException(status_code=400, detail="该等级已存在")
    
    level_config = LevelService.create_level_config(db, level_data)
    return BaseResponse(
        message="创建成功",
        data={
            "id": level_config.id,
            "level": level_config.level,
            "level_name": level_config.level_name,
            "ad_coin_multiplier": float(level_config.ad_coin_multiplier),
            "game_coin_multiplier": float(level_config.game_coin_multiplier),
            "min_experience": level_config.min_experience,
            "max_experience": level_config.max_experience,
            "description": level_config.description,
            "is_active": level_config.is_active
        }
    )

@router.put("/api/levels/{level_id}")
async def update_level_config(level_id: int, level_data: UserLevelConfigUpdate, db: Session = Depends(get_db)):
    """更新等级配置"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    from services.level_service import LevelService
    level_config = LevelService.update_level_config(db, level_id, level_data)
    if not level_config:
        raise HTTPException(status_code=404, detail="等级配置不存在")
    
    return BaseResponse(
        message="更新成功",
        data={
            "id": level_config.id,
            "level": level_config.level,
            "level_name": level_config.level_name,
            "ad_coin_multiplier": float(level_config.ad_coin_multiplier),
            "game_coin_multiplier": float(level_config.game_coin_multiplier),
            "min_experience": level_config.min_experience,
            "max_experience": level_config.max_experience,
            "description": level_config.description,
            "is_active": level_config.is_active
        }
    )

@router.delete("/api/levels/{level_id}")
async def delete_level_config(level_id: int, db: Session = Depends(get_db)):
    """删除等级配置"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    from services.level_service import LevelService
    success = LevelService.delete_level_config(db, level_id)
    if not success:
        raise HTTPException(status_code=404, detail="等级配置不存在")
    
    return BaseResponse(message="删除成功")

@router.get("/api/level-stats")
async def get_level_stats(db: Session = Depends(get_db)):
    """获取等级统计信息"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    from services.level_service import LevelService
    stats = LevelService.get_level_stats(db)
    
    return BaseResponse(
        message="获取成功",
        data=stats
    ) 