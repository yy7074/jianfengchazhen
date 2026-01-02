#!/usr/bin/env python3
"""
紧急封禁恶意IP - 一键封禁所有可疑IP
使用方法:
  python emergency_block_ips.py           # 自动检测并封禁
  python emergency_block_ips.py --ip IP   # 封禁指定IP
  python emergency_block_ips.py --all     # 封禁所有检测到的IP（无需确认）
"""

import sys
import argparse
from database import get_db
from sqlalchemy import text
from services.ip_service import IPService
from datetime import datetime

def find_malicious_ips(db, threshold=5):
    """查找恶意IP"""
    print("\n🔍 扫描恶意IP...")

    malicious_ips = db.execute(text("""
        SELECT ip_address,
               COUNT(DISTINCT user_id) as user_count,
               COUNT(*) as request_count,
               SUM(reward_coins) as total_coins
        FROM ad_watch_records
        WHERE watch_time >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        GROUP BY ip_address
        HAVING user_count > :threshold
        ORDER BY user_count DESC
    """), {'threshold': threshold}).fetchall()

    return malicious_ips

def block_ip(db, ip_address, reason, user_count, request_count):
    """封禁单个IP"""
    try:
        # 检查是否已经被封禁
        if IPService.is_ip_blocked(db, ip_address):
            print(f"  ⏭️  IP {ip_address} 已被封禁，跳过")
            return False

        # 执行封禁
        result = IPService.block_ip(
            db,
            ip_address,
            reason,
            block_type="auto",
            duration_hours=24 * 7  # 封禁7天
        )

        if result['success']:
            print(f"  ✅ 已封禁 {ip_address}")
            print(f"     原因: {reason}")
            print(f"     时长: 7天")
            return True
        else:
            print(f"  ❌ 封禁失败: {result.get('message', '未知错误')}")
            return False

    except Exception as e:
        print(f"  ❌ 封禁IP {ip_address} 时出错: {e}")
        return False

def emergency_block_all(auto_confirm=False):
    """紧急封禁所有恶意IP"""
    db = next(get_db())

    print("\n" + "="*60)
    print("🚨 紧急IP封禁程序")
    print("="*60)

    # 查找恶意IP
    malicious_ips = find_malicious_ips(db, threshold=5)

    if not malicious_ips:
        print("\n✅ 未发现需要封禁的IP")
        db.close()
        return

    print(f"\n发现 {len(malicious_ips)} 个可疑IP:\n")

    # 显示列表
    for i, row in enumerate(malicious_ips, 1):
        severity = "🔴极高" if row.user_count > 20 else "🟠高" if row.user_count > 10 else "🟡中"
        print(f"{i}. {row.ip_address}")
        print(f"   关联用户: {row.user_count}")
        print(f"   请求次数: {row.request_count}")
        print(f"   严重程度: {severity}")
        print()

    # 确认封禁
    if not auto_confirm:
        confirm = input(f"\n是否封禁以上 {len(malicious_ips)} 个IP? (yes/no): ").strip().lower()
        if confirm not in ['yes', 'y']:
            print("\n❌ 已取消")
            db.close()
            return

    # 执行封禁
    print("\n" + "="*60)
    print("开始封禁...")
    print("="*60 + "\n")

    blocked_count = 0
    for row in malicious_ips:
        reason = f"批量攻击检测: 关联{row.user_count}个用户，{row.request_count}次请求"
        if block_ip(db, row.ip_address, reason, row.user_count, row.request_count):
            blocked_count += 1

    print("\n" + "="*60)
    print(f"✅ 完成！成功封禁 {blocked_count}/{len(malicious_ips)} 个IP")
    print("="*60 + "\n")

    db.close()

def block_single_ip(ip_address):
    """封禁单个IP"""
    db = next(get_db())

    print(f"\n封禁IP: {ip_address}")

    reason = input("封禁原因: ").strip() or "手动封禁"
    duration = input("封禁时长(小时，留空=永久): ").strip()

    duration_hours = None
    if duration:
        try:
            duration_hours = int(duration)
        except:
            print("❌ 无效的时长")
            db.close()
            return

    result = IPService.block_ip(
        db,
        ip_address,
        reason,
        block_type="manual",
        duration_hours=duration_hours
    )

    if result['success']:
        print(f"✅ {result['message']}")
    else:
        print(f"❌ {result['message']}")

    db.close()

def main():
    parser = argparse.ArgumentParser(description='紧急IP封禁工具')
    parser.add_argument('--ip', help='封禁指定IP')
    parser.add_argument('--all', action='store_true', help='自动封禁所有恶意IP（无需确认）')
    parser.add_argument('--threshold', type=int, default=5, help='检测阈值（默认5）')

    args = parser.parse_args()

    if args.ip:
        # 封禁单个IP
        block_single_ip(args.ip)
    else:
        # 批量封禁
        emergency_block_all(auto_confirm=args.all)

if __name__ == "__main__":
    main()
