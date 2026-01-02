#!/usr/bin/env python3
"""
检查历史攻击记录
"""

from database import get_db
from sqlalchemy import text
from datetime import datetime, timedelta, date

def check_historical_data():
    """检查过去7天的数据"""
    db = next(get_db())

    print("\n" + "="*60)
    print("📊 历史数据分析（最近7天）")
    print("="*60 + "\n")

    # 1. 每日注册趋势
    print("【1】每日注册趋势")
    print("-" * 60)
    daily_registrations = db.execute(text("""
        SELECT DATE(register_time) as date,
               COUNT(*) as count
        FROM users
        WHERE register_time >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        GROUP BY DATE(register_time)
        ORDER BY date DESC
    """)).fetchall()

    if daily_registrations:
        for row in daily_registrations:
            bar = "█" * min(int(row.count / 10), 50)
            print(f"  {row.date}: {row.count:4d} {bar}")
            if row.count > 100:
                print(f"       🚨 异常高峰！")
    print()

    # 2. 每日广告观看趋势
    print("【2】每日广告观看记录趋势")
    print("-" * 60)
    daily_watches = db.execute(text("""
        SELECT DATE(watch_time) as date,
               COUNT(*) as count,
               COUNT(DISTINCT user_id) as users,
               SUM(reward_coins) as coins
        FROM ad_watch_records
        WHERE watch_time >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        GROUP BY DATE(watch_time)
        ORDER BY date DESC
    """)).fetchall()

    if daily_watches:
        for row in daily_watches:
            print(f"  {row.date}:")
            print(f"    观看次数: {row.count}")
            print(f"    活跃用户: {row.users}")
            print(f"    发放金币: {row.coins}")
            if row.count > 1000:
                print(f"    🚨 异常高峰！")
            print()
    print()

    # 3. 历史最恶意的IP
    print("【3】历史最恶意IP（最近7天）")
    print("-" * 60)
    malicious_ips = db.execute(text("""
        SELECT ip_address,
               COUNT(DISTINCT user_id) as user_count,
               COUNT(*) as request_count,
               SUM(reward_coins) as total_coins,
               DATE(MIN(watch_time)) as first_seen,
               DATE(MAX(watch_time)) as last_seen
        FROM ad_watch_records
        WHERE watch_time >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        GROUP BY ip_address
        HAVING user_count > 3
        ORDER BY user_count DESC
        LIMIT 20
    """)).fetchall()

    if malicious_ips:
        print(f"发现 {len(malicious_ips)} 个可疑IP:\n")
        for i, row in enumerate(malicious_ips, 1):
            print(f"  {i}. IP: {row.ip_address}")
            print(f"     关联用户: {row.user_count}")
            print(f"     请求次数: {row.request_count}")
            print(f"     获得金币: {row.total_coins}")
            print(f"     活跃时间: {row.first_seen} 至 {row.last_seen}")
            severity = "极高" if row.user_count > 20 else "高" if row.user_count > 10 else "中"
            print(f"     🚨 严重程度: {severity}")
            print()

        # 返回需要封禁的IP列表
        return [row.ip_address for row in malicious_ips if row.user_count > 5]
    else:
        print("✅ 未发现历史可疑IP")
        print()
        return []

    db.close()

if __name__ == "__main__":
    ips = check_historical_data()

    if ips:
        print("\n" + "="*60)
        print(f"建议封禁 {len(ips)} 个IP")
        print("="*60)
        print("\n执行以下命令封禁:")
        print("  python emergency_block_ips.py")
        print()
