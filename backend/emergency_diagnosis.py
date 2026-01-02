#!/usr/bin/env python3
"""
紧急诊断脚本 - 检测恶意注册和批量操作
"""

from database import get_db
from sqlalchemy import func, text
from models import User, AdWatchRecord
from datetime import datetime, timedelta, date
from collections import defaultdict

def diagnose_malicious_activity():
    """诊断恶意活动"""
    db = next(get_db())

    print("\n" + "="*60)
    print("🚨 恶意活动诊断报告")
    print("="*60 + "\n")

    # 1. 检查今日注册数量
    print("【1】今日注册情况")
    print("-" * 60)
    today = date.today()
    today_users = db.query(User).filter(
        func.date(User.register_time) == today
    ).count()
    print(f"今日注册用户数: {today_users}")

    # 最近1小时注册
    one_hour_ago = datetime.now() - timedelta(hours=1)
    recent_users = db.query(User).filter(
        User.register_time >= one_hour_ago
    ).count()
    print(f"最近1小时注册: {recent_users}")
    print()

    # 2. 检查相同IP的用户数量（高危）
    print("【2】可疑IP检测（同一IP多个用户）")
    print("-" * 60)
    ip_users = db.execute(text("""
        SELECT ip_address, COUNT(DISTINCT user_id) as user_count,
               COUNT(*) as request_count
        FROM ad_watch_records
        WHERE DATE(watch_time) = CURDATE()
        GROUP BY ip_address
        HAVING user_count > 5
        ORDER BY user_count DESC
        LIMIT 20
    """)).fetchall()

    if ip_users:
        print(f"发现 {len(ip_users)} 个可疑IP:\n")
        for row in ip_users:
            print(f"  IP: {row.ip_address}")
            print(f"  关联用户数: {row.user_count}")
            print(f"  请求次数: {row.request_count}")
            print(f"  🚨 严重程度: {'极高' if row.user_count > 20 else '高' if row.user_count > 10 else '中'}")
            print()
    else:
        print("✅ 未发现可疑IP")
    print()

    # 3. 检查批量观看广告的用户
    print("【3】异常广告观看行为")
    print("-" * 60)
    heavy_watchers = db.execute(text("""
        SELECT user_id, COUNT(*) as watch_count,
               SUM(reward_coins) as total_coins
        FROM ad_watch_records
        WHERE DATE(watch_time) = CURDATE()
        GROUP BY user_id
        HAVING watch_count > 50
        ORDER BY watch_count DESC
        LIMIT 20
    """)).fetchall()

    if heavy_watchers:
        print(f"发现 {len(heavy_watchers)} 个异常用户:\n")
        for row in heavy_watchers:
            print(f"  用户ID: {row.user_id}")
            print(f"  今日观看次数: {row.watch_count}")
            print(f"  获得金币: {row.total_coins}")
            print()
    else:
        print("✅ 未发现异常观看行为")
    print()

    # 4. 检查数据库表大小
    print("【4】数据库规模")
    print("-" * 60)
    total_users = db.query(User).count()
    total_records = db.query(AdWatchRecord).count()
    today_records = db.query(AdWatchRecord).filter(
        func.date(AdWatchRecord.watch_time) == today
    ).count()

    print(f"总用户数: {total_users}")
    print(f"总观看记录: {total_records}")
    print(f"今日观看记录: {today_records}")
    print()

    # 5. 检查设备ID重复
    print("【5】设备ID重复检测")
    print("-" * 60)
    duplicate_devices = db.execute(text("""
        SELECT device_id, COUNT(*) as count
        FROM users
        GROUP BY device_id
        HAVING count > 1
        ORDER BY count DESC
        LIMIT 10
    """)).fetchall()

    if duplicate_devices:
        print(f"发现 {len(duplicate_devices)} 个重复设备ID:\n")
        for row in duplicate_devices:
            print(f"  设备ID: {row.device_id}")
            print(f"  账号数量: {row.count}")
            print()
    else:
        print("✅ 未发现设备ID重复")
    print()

    # 6. 数据库连接数
    print("【6】数据库连接状态")
    print("-" * 60)
    try:
        connections = db.execute(text("""
            SHOW STATUS LIKE 'Threads_connected'
        """)).fetchone()
        print(f"当前连接数: {connections[1] if connections else 'N/A'}")
    except:
        print("无法获取连接数")
    print()

    db.close()

    print("="*60)
    print("诊断完成！")
    print("="*60 + "\n")

    return {
        'today_users': today_users,
        'recent_users': recent_users,
        'suspicious_ips': len(ip_users) if ip_users else 0,
        'heavy_watchers': len(heavy_watchers) if heavy_watchers else 0
    }

def get_top_malicious_ips(limit=10):
    """获取最恶意的IP列表"""
    db = next(get_db())

    print("\n" + "="*60)
    print("🎯 需要封禁的IP列表")
    print("="*60 + "\n")

    malicious_ips = db.execute(text("""
        SELECT ip_address,
               COUNT(DISTINCT user_id) as user_count,
               COUNT(*) as request_count,
               SUM(reward_coins) as total_coins
        FROM ad_watch_records
        WHERE DATE(watch_time) = CURDATE()
        GROUP BY ip_address
        HAVING user_count > 5
        ORDER BY user_count DESC
        LIMIT :limit
    """), {'limit': limit}).fetchall()

    if malicious_ips:
        print("建议封禁以下IP:\n")
        ips_to_block = []
        for i, row in enumerate(malicious_ips, 1):
            print(f"{i}. IP: {row.ip_address}")
            print(f"   关联用户: {row.user_count}")
            print(f"   请求次数: {row.request_count}")
            print(f"   获得金币: {row.total_coins}")
            print()
            ips_to_block.append(row.ip_address)

        db.close()
        return ips_to_block
    else:
        print("✅ 暂无需要封禁的IP")
        db.close()
        return []

if __name__ == "__main__":
    # 运行诊断
    result = diagnose_malicious_activity()

    # 获取需要封禁的IP
    ips = get_top_malicious_ips(20)

    # 给出建议
    print("\n" + "="*60)
    print("💡 处理建议")
    print("="*60 + "\n")

    if result['suspicious_ips'] > 0:
        print("⚠️  发现恶意IP，建议立即执行:")
        print("   python emergency_block_ips.py")
        print()

    if result['today_users'] > 1000:
        print("⚠️  今日注册量异常，建议:")
        print("   1. 开启注册验证码")
        print("   2. 限制单IP注册频率")
        print()

    if result['heavy_watchers'] > 0:
        print("⚠️  发现异常观看行为，建议:")
        print("   1. 降低每日广告上限")
        print("   2. 增加观看时长验证")
        print()

    print("="*60)
