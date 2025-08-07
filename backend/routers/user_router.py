from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
from schemas import *
from services.user_service import UserService
from services.ad_service import AdService
from typing import List

router = APIRouter()

@router.post("/register", response_model=BaseResponse)
async def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """用户注册"""
    try:
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
    transactions = db.query(CoinTransaction).filter(
        CoinTransaction.user_id == user_id
    ).order_by(CoinTransaction.created_time.desc()).offset(skip).limit(size).all()
    
    total = db.query(CoinTransaction).filter(CoinTransaction.user_id == user_id).count()
    
    return BaseResponse(
        message="获取成功",
        data={
            "items": [CoinTransaction.from_orm(t).dict() for t in transactions],
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
    withdraws = db.query(WithdrawRequest).filter(
        WithdrawRequest.user_id == user_id
    ).order_by(WithdrawRequest.request_time.desc()).offset(skip).limit(size).all()
    
    total = db.query(WithdrawRequest).filter(WithdrawRequest.user_id == user_id).count()
    
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