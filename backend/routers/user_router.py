from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from schemas import *
from models import GameRecord, AdWatchRecord, CoinTransaction as CoinTransactionModel, WithdrawRequest as WithdrawRequestModel
from services.user_service import UserService
from services.ad_service import AdService
from typing import List

router = APIRouter()

@router.post("/register", response_model=BaseResponse)
async def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """用户注册（如果用户已存在则直接返回用户信息）"""
    try:
        # 检查用户是否已存在
        existing_user = UserService.get_user_by_device_id(db, user_data.device_id)
        if existing_user:
            # 用户已存在，更新最后登录时间并返回用户信息
            UserService.update_last_login(db, existing_user.id)
            return BaseResponse(
                message="用户已存在，自动登录",
                data={
                    "user_id": existing_user.id,
                    "device_id": existing_user.device_id,
                    "nickname": existing_user.nickname,
                    "coins": float(existing_user.coins)
                }
            )
        
        # 创建新用户
        user = UserService.create_user(db, user_data)
        return BaseResponse(
            message="注册成功",
            data={
                "user_id": user.id,
                "device_id": user.device_id,
                "nickname": user.nickname,
                "coins": float(user.coins)
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="注册失败")

@router.post("/login", response_model=BaseResponse)
async def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    user = UserService.get_user_by_device_id(db, login_data.device_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在，请先注册")
    
    # 更新最后登录时间
    UserService.update_last_login(db, user.id)
    
    return BaseResponse(
        message="登录成功",
        data={
            "user_id": user.id,
            "device_id": user.device_id,
            "nickname": user.nickname,
            "coins": float(user.coins),
            "level": user.level,
            "experience": user.experience
        }
    )

@router.get("/info/{user_id}", response_model=BaseResponse)
async def get_user_info(user_id: int, db: Session = Depends(get_db)):
    """获取用户信息"""
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 获取用户统计信息
    stats = UserService.get_user_stats(db, user_id)
    
    return BaseResponse(
        message="获取成功",
        data={
            "user_info": UserInfo.from_orm(user).dict(),
            "stats": stats
        }
    )

@router.put("/update/{user_id}", response_model=BaseResponse)
async def update_user_info(user_id: int, update_data: UserUpdate, db: Session = Depends(get_db)):
    """更新用户信息"""
    user = UserService.update_user(db, user_id, update_data)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return BaseResponse(
        message="更新成功",
        data=UserInfo.from_orm(user).dict()
    )

@router.get("/coins/history/{user_id}")
async def get_coin_history(
    user_id: int, 
    page: int = 1, 
    size: int = 20,
    db: Session = Depends(get_db)
):
    """获取金币流水记录"""
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 分页查询金币流水
    skip = (page - 1) * size
    transactions = db.query(CoinTransactionModel).filter(
        CoinTransactionModel.user_id == user_id
    ).order_by(CoinTransactionModel.created_time.desc()).offset(skip).limit(size).all()
    
    total = db.query(CoinTransactionModel).filter(CoinTransactionModel.user_id == user_id).count()
    
    # 手动构建响应数据
    transaction_data = []
    for t in transactions:
        transaction_record = {
            "id": t.id,
            "user_id": t.user_id,
            "type": t.type.value if hasattr(t.type, 'value') else str(t.type),
            "amount": float(t.amount),
            "balance_after": float(t.balance_after),
            "description": t.description,
            "created_time": t.created_time.isoformat() if t.created_time else None
        }
        transaction_data.append(transaction_record)
    
    return BaseResponse(
        message="获取成功",
        data={
            "items": transaction_data,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    )

@router.get("/ads/stats/{user_id}")
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

@router.post("/withdraw", response_model=BaseResponse)
async def submit_withdraw_request(
    user_id: int,
    withdraw_data: WithdrawRequest,
    db: Session = Depends(get_db)
):
    """提交提现申请"""
    from services.withdraw_service import WithdrawService
    
    try:
        result = WithdrawService.submit_withdraw_request(db, user_id, withdraw_data)
        if result["success"]:
            return BaseResponse(
                message="提现申请提交成功，请等待审核",
                data=result["data"]
            )
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/withdraw/history/{user_id}")
async def get_withdraw_history(
    user_id: int,
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db)
):
    """获取提现记录"""
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    skip = (page - 1) * size
    withdraws = db.query(WithdrawRequestModel).filter(
        WithdrawRequestModel.user_id == user_id
    ).order_by(WithdrawRequestModel.request_time.desc()).offset(skip).limit(size).all()
    
    total = db.query(WithdrawRequestModel).filter(WithdrawRequestModel.user_id == user_id).count()
    
    return BaseResponse(
        message="获取成功",
        data={
            "items": [WithdrawInfo.from_orm(w).dict() for w in withdraws],
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    )

@router.get("/{user_id}/stats", response_model=BaseResponse)
async def get_user_stats(user_id: int, db: Session = Depends(get_db)):
    """获取用户统计信息"""
    try:
        # 验证用户是否存在
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 获取游戏统计
        game_count = db.query(GameRecord).filter(GameRecord.user_id == user_id).count()
        best_score_result = db.query(func.max(GameRecord.score)).filter(GameRecord.user_id == user_id).scalar()
        avg_score_result = db.query(func.avg(GameRecord.score)).filter(GameRecord.user_id == user_id).scalar()
        
        # 获取广告统计
        ads_watched = db.query(AdWatchRecord).filter(AdWatchRecord.user_id == user_id).count()
        total_ad_coins_result = db.query(func.sum(AdWatchRecord.reward_coins)).filter(AdWatchRecord.user_id == user_id).scalar()
        
        # 获取金币统计
        total_coins_earned = db.query(func.sum(CoinTransactionModel.amount)).filter(
            CoinTransactionModel.user_id == user_id,
            CoinTransactionModel.amount > 0
        ).scalar()
        
        stats = {
            "game_count": game_count or 0,
            "best_score": int(best_score_result or 0),
            "average_score": int(avg_score_result or 0),
            "ads_watched": ads_watched or 0,
            "total_coins": float(total_coins_earned or 0),
            "current_coins": float(user.coins or 0),
            "level": user.level or 1,
            "total_score": int(best_score_result or 0)  # 与best_score相同，保持兼容性
        }
        
        return BaseResponse(message="获取成功", data=stats)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取用户统计失败")

@router.get("/{user_id}/withdraws", response_model=BaseResponse)
async def get_user_withdraw_history(
    user_id: int, 
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取用户提现历史（移动端使用）"""
    try:
        # 验证用户是否存在
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 获取提现记录
        skip = (page - 1) * size
        withdraws = db.query(WithdrawRequestModel).filter(
            WithdrawRequestModel.user_id == user_id
        ).order_by(WithdrawRequestModel.request_time.desc()).offset(skip).limit(size).all()
        
        # 手动构建提现记录数据
        withdraw_data = []
        for withdraw in withdraws:
            record = {
                "id": withdraw.id,
                "amount": float(withdraw.amount),
                "status": withdraw.status.value if hasattr(withdraw.status, 'value') else str(withdraw.status),
                "request_time": withdraw.request_time.isoformat() if withdraw.request_time else None,
                "process_time": withdraw.process_time.isoformat() if withdraw.process_time else None,
                "alipay_account": withdraw.alipay_account,
                "real_name": withdraw.real_name,
                "admin_note": withdraw.admin_note
            }
            withdraw_data.append(record)
        
        total = db.query(WithdrawRequestModel).filter(WithdrawRequestModel.user_id == user_id).count()
        
        return BaseResponse(
            message="获取成功",
            data=withdraw_data  # 直接返回列表，而不是嵌套对象
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取提现历史失败")

@router.get("/{user_id}/coin-records", response_model=BaseResponse)
async def get_coin_records(
    user_id: int,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """获取用户金币获取记录"""
    try:
        # 检查用户是否存在
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 获取广告观看记录
        skip = (page - 1) * size
        ad_records = db.query(AdWatchRecord).filter(
            AdWatchRecord.user_id == user_id,
            AdWatchRecord.is_completed == True
        ).order_by(AdWatchRecord.watch_time.desc()).offset(skip).limit(size).all()
        
        # 构建金币记录数据
        coin_records = []
        for record in ad_records:
            coin_record = {
                "id": record.id,
                "amount": int(record.reward_coins),
                "type": "ad_watch",
                "description": f"观看广告获得金币",
                "created_at": record.watch_time.isoformat() if record.watch_time else None
            }
            coin_records.append(coin_record)
        
        return BaseResponse(
            message="获取成功",
            data=coin_records
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}") 