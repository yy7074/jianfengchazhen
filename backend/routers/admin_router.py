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
            "status": 1 if ad.status == 'ACTIVE' else 0
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
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    ad = AdService.update_ad_config(db, ad_id, ad_data)
    if not ad:
        raise HTTPException(status_code=404, detail="广告不存在")
    
    return BaseResponse(
        message="更新成功",
        data=AdConfigInfo.from_orm(ad).dict()
    )

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
    db: Session = Depends(get_db)
):
    """获取提现申请列表"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    query = db.query(WithdrawRequest).join(User)
    
    if status:
        query = query.filter(WithdrawRequest.status == status)
    
    total = query.count()
    skip = (page - 1) * size
    withdraws = query.order_by(WithdrawRequest.request_time.desc()).offset(skip).limit(size).all()
    
    # 组装数据
    items = []
    for w in withdraws:
        item = WithdrawInfo.from_orm(w).dict()
        item["user_nickname"] = w.user.nickname
        items.append(item)
    
    return BaseResponse(
        message="获取成功",
        data={
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    )

@router.put("/api/withdraws/{withdraw_id}/approve")
async def approve_withdraw(
    withdraw_id: int,
    admin_note: str = None,
    db: Session = Depends(get_db)
):
    """批准提现申请"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    from services.withdraw_service import WithdrawService
    
    result = WithdrawService.approve_withdraw(db, withdraw_id, admin_note)
    if result["success"]:
        return BaseResponse(message=result["message"])
    else:
        raise HTTPException(status_code=400, detail=result["message"])

@router.put("/api/withdraws/{withdraw_id}/reject")
async def reject_withdraw(
    withdraw_id: int,
    admin_note: str,
    db: Session = Depends(get_db)
):
    """拒绝提现申请"""
    if not verify_admin():
        raise HTTPException(status_code=401, detail="需要管理员权限")
    
    from services.withdraw_service import WithdrawService
    
    result = WithdrawService.reject_withdraw(db, withdraw_id, admin_note)
    if result["success"]:
        return BaseResponse(message=result["message"])
    else:
        raise HTTPException(status_code=400, detail=result["message"]) 