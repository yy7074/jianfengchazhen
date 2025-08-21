from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
from schemas import *
from models import AdWatchRecord, AdConfig
from services.ad_service import AdService
from services.user_service import UserService

router = APIRouter()

@router.get("/random/{user_id}", response_model=BaseResponse)
async def get_random_ad(user_id: int, db: Session = Depends(get_db)):
    """获取随机广告"""
    # 验证用户存在
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 获取随机广告
    ad = AdService.get_random_ad(db, user_id)
    if not ad:
        return BaseResponse(
            code=204,
            message="暂无可观看的广告",
            data=None
        )
    
    return BaseResponse(
        message="获取成功",
        data=AdConfigInfo.from_orm(ad).dict()
    )

@router.post("/watch/{user_id}", response_model=BaseResponse)
async def watch_ad(
    user_id: int,
    watch_request: AdWatchRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """观看广告并获得奖励"""
    # 验证用户存在
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 获取客户端IP
    client_ip = request.client.host
    
    # 处理广告观看
    result = AdService.watch_ad(db, user_id, watch_request, client_ip)
    
    if result["success"]:
        return BaseResponse(
            message=result["message"],
            data={
                "reward_coins": float(result["reward_coins"]),
                "is_completed": result["is_completed"]
            }
        )
    else:
        raise HTTPException(status_code=400, detail=result["message"])

@router.get("/stats/{user_id}", response_model=BaseResponse)
async def get_user_ad_stats(user_id: int, db: Session = Depends(get_db)):
    """获取用户广告观看统计"""
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    stats = AdService.get_user_ad_stats(db, user_id)
    
    return BaseResponse(
        message="获取成功",
        data=stats
    )

@router.get("/history/{user_id}")
async def get_user_ad_history(
    user_id: int,
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db)
):
    """获取用户广告观看历史"""
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    skip = (page - 1) * size
    records = db.query(AdWatchRecord).filter(
        AdWatchRecord.user_id == user_id
    ).order_by(AdWatchRecord.watch_time.desc()).offset(skip).limit(size).all()
    
    total = db.query(AdWatchRecord).filter(AdWatchRecord.user_id == user_id).count()
    
    # 获取广告信息
    ad_ids = [r.ad_id for r in records]
    ads = db.query(AdConfig).filter(AdConfig.id.in_(ad_ids)).all()
    ad_dict = {ad.id: ad for ad in ads}
    
    # 组装数据
    items = []
    for record in records:
        ad_info = ad_dict.get(record.ad_id)
        items.append({
            "id": record.id,
            "ad_id": record.ad_id,
            "ad_name": ad_info.name if ad_info else "已删除广告",
            "watch_duration": record.watch_duration,
            "reward_coins": float(record.reward_coins),
            "is_completed": record.is_completed,
            "watch_time": record.watch_time
        })
    
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

@router.get("/available/{user_id}")
async def get_available_ads(user_id: int, db: Session = Depends(get_db)):
    """获取用户可观看的广告列表"""
    from datetime import date
    from sqlalchemy import func, and_, or_
    
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 获取所有有效广告
    from datetime import datetime
    now = datetime.now()
    all_ads = db.query(AdConfig).filter(
        AdConfig.status == 'ACTIVE',
        or_(AdConfig.start_time.is_(None), AdConfig.start_time <= now),
        or_(AdConfig.end_time.is_(None), AdConfig.end_time >= now)
    ).all()
    
    # 简化的广告数据转换
    available_ads = []
    for ad in all_ads:
        ad_data = {
            "id": ad.id,
            "name": ad.name,
            "ad_type": ad.ad_type or "video",
            "video_url": ad.video_url,
            "webpage_url": ad.webpage_url,
            "image_url": ad.image_url,
            "duration": ad.duration,
            "reward_coins": float(ad.reward_coins or 0),
            "daily_limit": ad.daily_limit or 10,
            "min_watch_duration": ad.min_watch_duration or 15,
            "weight": ad.weight or 1,
            "remaining_today": ad.daily_limit or 10,  # 简化处理
            "watched_today": 0  # 简化处理
        }
        available_ads.append(ad_data)
    
    return BaseResponse(
        message="获取成功",
        data={
            "ads": available_ads,
            "total_available": len(available_ads)
        }
    ) 