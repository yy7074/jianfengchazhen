#!/usr/bin/env python3
"""
检查今日统计数据
"""

from database import get_db
from models import *
from sqlalchemy import func
from datetime import date, datetime, timedelta

db = next(get_db())

print("=" * 60)
print("检查今日统计数据")
print("=" * 60)

# 获取当前日期和时间
now = datetime.now()
today = date.today()
print(f"\n当前时间: {now}")
print(f"今日日期: {today}")
print(f"今日日期（字符串）: {today.strftime('%Y-%m-%d')}")

# 检查广告观看记录
print("\n" + "=" * 60)
print("1. 广告观看记录统计")
print("=" * 60)

# 查询今日广告记录
today_ad_records = db.query(AdWatchRecord).filter(
    func.date(AdWatchRecord.watch_time) == today
).all()

print(f"今日广告观看记录数: {len(today_ad_records)}")

if today_ad_records:
    print("\n最近5条今日记录:")
    for i, record in enumerate(today_ad_records[:5], 1):
        print(f"  {i}. 时间: {record.watch_time}, 金币: {record.reward_coins}, 用户: {record.user_id}")
    
    # 计算今日广告金币
    today_ad_coins_sum = sum(float(r.reward_coins) for r in today_ad_records)
    print(f"\n今日广告金币总计: {today_ad_coins_sum:.0f}")
else:
    print("今日没有广告观看记录")

# 查询所有广告记录（最近10条）
print("\n最近10条广告记录（所有日期）:")
all_recent_ads = db.query(AdWatchRecord).order_by(AdWatchRecord.watch_time.desc()).limit(10).all()
for i, record in enumerate(all_recent_ads, 1):
    is_today = record.watch_time.date() == today
    marker = "✅ 今日" if is_today else ""
    print(f"  {i}. 时间: {record.watch_time} {marker}, 金币: {record.reward_coins}")

# 检查金币交易记录
print("\n" + "=" * 60)
print("2. 金币交易记录统计")
print("=" * 60)

# 查询今日金币交易
today_coin_trans = db.query(CoinTransaction).filter(
    CoinTransaction.amount > 0,
    func.date(CoinTransaction.created_time) == today
).all()

print(f"今日金币交易记录数: {len(today_coin_trans)}")

if today_coin_trans:
    print("\n最近5条今日交易:")
    for i, trans in enumerate(today_coin_trans[:5], 1):
        print(f"  {i}. 时间: {trans.created_time}, 金币: {trans.amount}, 类型: {trans.type.value if trans.type else 'N/A'}")
    
    # 计算今日金币总计
    today_coins_sum = sum(float(t.amount) for t in today_coin_trans)
    print(f"\n今日金币交易总计: {today_coins_sum:.0f}")
else:
    print("今日没有金币交易记录")

# 查询所有交易记录（最近10条）
print("\n最近10条金币交易（所有日期）:")
all_recent_trans = db.query(CoinTransaction).filter(
    CoinTransaction.amount > 0
).order_by(CoinTransaction.created_time.desc()).limit(10).all()
for i, trans in enumerate(all_recent_trans, 1):
    is_today = trans.created_time.date() == today
    marker = "✅ 今日" if is_today else ""
    print(f"  {i}. 时间: {trans.created_time} {marker}, 金币: {trans.amount}, 类型: {trans.type.value if trans.type else 'N/A'}")

# 使用SQL查询检查
print("\n" + "=" * 60)
print("3. 使用SQL直接查询今日数据")
print("=" * 60)

# 广告金币
result = db.execute(f"""
    SELECT 
        COUNT(*) as count,
        SUM(reward_coins) as total_coins,
        DATE(watch_time) as watch_date
    FROM ad_watch_records 
    WHERE DATE(watch_time) = '{today}'
    GROUP BY DATE(watch_time)
""").fetchone()

if result:
    print(f"今日广告观看: {result[0]} 次")
    print(f"今日广告金币: {result[1] or 0:.0f}")
else:
    print("今日无广告观看记录")

# 金币交易
result2 = db.execute(f"""
    SELECT 
        COUNT(*) as count,
        SUM(amount) as total_amount,
        DATE(created_time) as trans_date
    FROM coin_transactions 
    WHERE amount > 0 AND DATE(created_time) = '{today}'
    GROUP BY DATE(created_time)
""").fetchone()

if result2:
    print(f"今日金币交易: {result2[0]} 笔")
    print(f"今日金币总计: {result2[1] or 0:.0f}")
else:
    print("今日无金币交易记录")

# 检查是否有日期范围异常的数据
print("\n" + "=" * 60)
print("4. 检查数据日期分布")
print("=" * 60)

# 广告记录日期分布
ad_dates = db.execute("""
    SELECT DATE(watch_time) as date, COUNT(*) as count, SUM(reward_coins) as coins
    FROM ad_watch_records 
    GROUP BY DATE(watch_time)
    ORDER BY date DESC
    LIMIT 7
""").fetchall()

print("\n最近7天广告记录:")
for row in ad_dates:
    date_str = str(row[0])
    is_today = date_str == str(today)
    marker = "← 今日" if is_today else ""
    print(f"  {date_str}: {row[1]}次观看, {row[2] or 0:.0f}金币 {marker}")

# 金币交易日期分布
coin_dates = db.execute("""
    SELECT DATE(created_time) as date, COUNT(*) as count, SUM(amount) as total
    FROM coin_transactions 
    WHERE amount > 0
    GROUP BY DATE(created_time)
    ORDER BY date DESC
    LIMIT 7
""").fetchall()

print("\n最近7天金币交易:")
for row in coin_dates:
    date_str = str(row[0])
    is_today = date_str == str(today)
    marker = "← 今日" if is_today else ""
    print(f"  {date_str}: {row[1]}笔交易, {row[2] or 0:.0f}金币 {marker}")

print("\n" + "=" * 60)
print("检查完成")
print("=" * 60)

db.close()

