from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from database import get_db
from schemas import *
from services.user_service import UserService
from services.config_service import ConfigService
from models import GameRecord, User, TransactionType
from typing import List
from datetime import date, datetime

router = APIRouter()

@router.post("/submit/{user_id}", response_model=BaseResponse)
async def submit_game_result(
    user_id: int,
    game_data: GameResultSubmit,
    db: Session = Depends(get_db)
):
    """提交游戏结果"""
    # 验证用户存在
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 检查今日游戏奖励次数限制
    today = date.today()
    today_rewards = db.query(func.count(GameRecord.id)).filter(
        GameRecord.user_id == user_id,
        func.date(GameRecord.play_time) == today,
        GameRecord.reward_coins > 0
    ).scalar() or 0
    
    max_daily_rewards = int(ConfigService.get_config(db, "max_daily_game_rewards", "10"))
    
    # 计算奖励金币
    reward_coins = 0
    if today_rewards < max_daily_rewards:
        base_reward = ConfigService.get_game_reward_coins(db)
        # 根据分数给予额外奖励
        score_bonus = min(game_data.score // 100, 10)  # 每100分额外1金币，最多10金币
        reward_coins = base_reward + score_bonus
    
    # 创建游戏记录
    game_record = GameRecord(
        user_id=user_id,
        score=game_data.score,
        duration=game_data.duration,
        needles_inserted=game_data.needles_inserted,
        reward_coins=reward_coins
    )
    
    db.add(game_record)
    db.commit()
    db.refresh(game_record)
    
    # 更新用户游戏统计
    UserService.update_game_stats(db, user_id, game_data.score, game_data.duration, game_data.needles_inserted)
    
    # 发放奖励金币
    if reward_coins > 0:
        UserService.add_coins(
            db, user_id, float(reward_coins),
            TransactionType.GAME_REWARD,
            f"游戏奖励 - 得分: {game_data.score}",
            game_record.id
        )
    
    return BaseResponse(
        message="游戏结果提交成功",
        data={
            "game_id": game_record.id,
            "score": game_data.score,
            "reward_coins": float(reward_coins),
            "is_new_record": game_data.score > (user.best_score or 0),
            "remaining_rewards_today": max(0, max_daily_rewards - today_rewards - (1 if reward_coins > 0 else 0))
        }
    )

@router.get("/leaderboard")
async def get_leaderboard(
    limit: int = 50,
    period: str = "all",  # all, today, week, month
    db: Session = Depends(get_db)
):
    """获取排行榜"""
    # 参数验证和清理
    limit = max(1, min(limit, 100))  # 限制在1-100之间
    valid_periods = ["all", "today", "week", "month"]
    if period not in valid_periods:
        period = "all"
    
    query = db.query(
        GameRecord.user_id,
        User.nickname,
        func.max(GameRecord.score).label('best_score'),
        func.max(GameRecord.play_time).label('latest_play')
    ).join(User, GameRecord.user_id == User.id)
    
    # 根据时间范围过滤
    if period == "today":
        today = date.today()
        query = query.filter(func.date(GameRecord.play_time) == today)
    elif period == "week":
        from datetime import timedelta
        week_ago = datetime.now() - timedelta(days=7)
        query = query.filter(GameRecord.play_time >= week_ago)
    elif period == "month":
        from datetime import timedelta
        month_ago = datetime.now() - timedelta(days=30)
        query = query.filter(GameRecord.play_time >= month_ago)
    
    # 按用户分组，按最高分排序
    leaderboard = query.group_by(
        GameRecord.user_id, User.nickname
    ).order_by(desc('best_score')).limit(limit).all()
    
    # 组装排行榜数据
    result = []
    for rank, (user_id, nickname, best_score, latest_play) in enumerate(leaderboard, 1):
        # 获取用户详细信息
        user_info = db.query(User).filter(User.id == user_id).first()
        result.append({
            "rank": rank,
            "user_id": user_id,
            "nickname": nickname or f"用户{user_id}",
            "best_score": best_score,
            "latest_play": latest_play.isoformat() if latest_play else None,
            "level": user_info.level if user_info else 1,
            "game_count": user_info.game_count if user_info else 0,
            "coins": float(user_info.coins) if user_info else 0
        })
    
    return BaseResponse(
        message="获取成功",
        data={
            "leaderboard": result,
            "period": period,
            "total": len(result)
        }
    )

@router.get("/history/{user_id}")
async def get_game_history(
    user_id: int,
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db)
):
    """获取用户游戏历史"""
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    skip = (page - 1) * size
    records = db.query(GameRecord).filter(
        GameRecord.user_id == user_id
    ).order_by(GameRecord.play_time.desc()).offset(skip).limit(size).all()
    
    total = db.query(GameRecord).filter(GameRecord.user_id == user_id).count()
    
    return BaseResponse(
        message="获取成功",
        data={
            "items": [GameRecord.from_orm(r).dict() for r in records],
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    )

@router.get("/stats/{user_id}")
async def get_user_game_stats(user_id: int, db: Session = Depends(get_db)):
    """获取用户游戏统计"""
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 基础统计
    today = date.today()
    
    # 今日游戏次数
    today_games = db.query(func.count(GameRecord.id)).filter(
        GameRecord.user_id == user_id,
        func.date(GameRecord.play_time) == today
    ).scalar() or 0
    
    # 今日获得金币
    today_coins = db.query(func.sum(GameRecord.reward_coins)).filter(
        GameRecord.user_id == user_id,
        func.date(GameRecord.play_time) == today
    ).scalar() or 0
    
    # 今日已获得奖励次数
    today_rewards = db.query(func.count(GameRecord.id)).filter(
        GameRecord.user_id == user_id,
        func.date(GameRecord.play_time) == today,
        GameRecord.reward_coins > 0
    ).scalar() or 0
    
    # 总统计
    total_games = db.query(func.count(GameRecord.id)).filter(
        GameRecord.user_id == user_id
    ).scalar() or 0
    
    total_coins = db.query(func.sum(GameRecord.reward_coins)).filter(
        GameRecord.user_id == user_id
    ).scalar() or 0
    
    # 平均分数
    avg_score = db.query(func.avg(GameRecord.score)).filter(
        GameRecord.user_id == user_id
    ).scalar() or 0
    
    # 最近7天游戏次数
    from datetime import timedelta
    week_ago = datetime.now() - timedelta(days=7)
    week_games = db.query(func.count(GameRecord.id)).filter(
        GameRecord.user_id == user_id,
        GameRecord.play_time >= week_ago
    ).scalar() or 0
    
    # 配置信息
    max_daily_rewards = int(ConfigService.get_config(db, "max_daily_game_rewards", "10"))
    game_reward_coins = ConfigService.get_game_reward_coins(db)
    
    return BaseResponse(
        message="获取成功",
        data={
            "today_stats": {
                "games": today_games,
                "coins": float(today_coins),
                "rewards_used": today_rewards,
                "rewards_remaining": max(0, max_daily_rewards - today_rewards)
            },
            "total_stats": {
                "games": total_games,
                "coins": float(total_coins),
                "avg_score": round(float(avg_score), 2),
                "best_score": user.best_score,
                "week_games": week_games
            },
            "config": {
                "max_daily_rewards": max_daily_rewards,
                "base_reward_coins": float(game_reward_coins)
            }
        }
    )

@router.get("/daily-stats")
async def get_daily_game_stats(
    days: int = 7,
    db: Session = Depends(get_db)
):
    """获取每日游戏统计（用于图表展示）"""
    from datetime import timedelta
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days-1)
    
    # 查询每日游戏数据
    daily_stats = db.query(
        func.date(GameRecord.play_time).label('date'),
        func.count(GameRecord.id).label('games'),
        func.count(func.distinct(GameRecord.user_id)).label('players'),
        func.avg(GameRecord.score).label('avg_score'),
        func.max(GameRecord.score).label('max_score'),
        func.sum(GameRecord.reward_coins).label('total_coins')
    ).filter(
        func.date(GameRecord.play_time) >= start_date,
        func.date(GameRecord.play_time) <= end_date
    ).group_by(func.date(GameRecord.play_time)).all()
    
    # 补充没有数据的日期
    result = []
    current_date = start_date
    stats_dict = {stat.date: stat for stat in daily_stats}
    
    while current_date <= end_date:
        stat = stats_dict.get(current_date)
        if stat:
            result.append({
                "date": current_date.isoformat(),
                "games": stat.games,
                "players": stat.players,
                "avg_score": round(float(stat.avg_score or 0), 2),
                "max_score": stat.max_score or 0,
                "total_coins": float(stat.total_coins or 0)
            })
        else:
            result.append({
                "date": current_date.isoformat(),
                "games": 0,
                "players": 0,
                "avg_score": 0,
                "max_score": 0,
                "total_coins": 0
            })
        current_date += timedelta(days=1)
    
    return BaseResponse(
        message="获取成功",
        data={
            "daily_stats": result,
            "period": f"{start_date} 到 {end_date}"
        }
    ) 