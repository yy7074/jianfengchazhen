#!/usr/bin/env python3
"""
清理恶意数据脚本 - 删除恶意IP相关的用户和记录
使用方法:
  python cleanup_malicious_data.py              # 交互模式（推荐）
  python cleanup_malicious_data.py --dry-run    # 预览模式（不实际删除）
  python cleanup_malicious_data.py --auto       # 自动模式（无需确认）
"""

import sys
import argparse
from database import get_db
from sqlalchemy import text
from datetime import datetime, timedelta
from models import User, AdWatchRecord, CoinTransaction, GameRecord, IPBlacklist

def analyze_malicious_data(db):
    """分析恶意数据规模"""
    print("\n" + "="*60)
    print("📊 恶意数据分析")
    print("="*60 + "\n")

    # 1. 获取所有被封禁的IP
    blocked_ips = db.query(IPBlacklist).filter(
        IPBlacklist.is_active == True
    ).all()

    if not blocked_ips:
        print("✅ 没有被封禁的IP，无需清理")
        return None

    ip_addresses = [ip.ip_address for ip in blocked_ips]
    print(f"发现 {len(ip_addresses)} 个被封禁的IP:\n")

    for ip_record in blocked_ips[:10]:  # 只显示前10个
        print(f"  • {ip_record.ip_address} - {ip_record.reason}")
    if len(blocked_ips) > 10:
        print(f"  ... 还有 {len(blocked_ips) - 10} 个")
    print()

    # 2. 统计关联的恶意数据
    stats = {}

    # 查找关联的用户（通过广告观看记录关联）
    malicious_users = db.execute(text("""
        SELECT DISTINCT u.id, u.device_id, u.nickname, u.register_time
        FROM users u
        INNER JOIN ad_watch_records awr ON awr.user_id = u.id
        WHERE awr.ip_address IN :ips
    """), {'ips': tuple(ip_addresses)}).fetchall()

    stats['users'] = len(malicious_users)

    if stats['users'] > 0:
        user_ids = [u.id for u in malicious_users]

        # 统计广告观看记录
        ad_records = db.execute(text("""
            SELECT COUNT(*) as count
            FROM ad_watch_records
            WHERE user_id IN :user_ids
        """), {'user_ids': tuple(user_ids)}).scalar()
        stats['ad_records'] = ad_records

        # 统计金币交易记录
        coin_transactions = db.execute(text("""
            SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total_coins
            FROM coin_transactions
            WHERE user_id IN :user_ids
        """), {'user_ids': tuple(user_ids)}).fetchone()
        stats['coin_transactions'] = coin_transactions.count
        stats['total_coins'] = coin_transactions.total_coins

        # 统计游戏记录
        game_records = db.execute(text("""
            SELECT COUNT(*) as count
            FROM game_records
            WHERE user_id IN :user_ids
        """), {'user_ids': tuple(user_ids)}).scalar()
        stats['game_records'] = game_records
    else:
        stats['ad_records'] = 0
        stats['coin_transactions'] = 0
        stats['total_coins'] = 0
        stats['game_records'] = 0

    # 显示统计
    print("【恶意数据统计】")
    print("-" * 60)
    print(f"  恶意用户数量: {stats['users']}")
    print(f"  广告观看记录: {stats['ad_records']}")
    print(f"  金币交易记录: {stats['coin_transactions']}")
    print(f"  游戏记录数量: {stats['game_records']}")
    print(f"  涉及金币总额: {stats['total_coins']}")
    print()

    return {
        'stats': stats,
        'blocked_ips': ip_addresses,
        'malicious_users': malicious_users
    }

def cleanup_data(db, data, dry_run=False):
    """清理恶意数据"""
    if dry_run:
        print("【预览模式】以下数据将被删除（但不会实际执行）:\n")
    else:
        print("【清理模式】正在删除数据...\n")

    stats = data['stats']
    malicious_users = data['malicious_users']

    if stats['users'] == 0:
        print("✅ 没有需要清理的数据")
        return

    user_ids = [u.id for u in malicious_users]
    deleted = {
        'ad_records': 0,
        'coin_transactions': 0,
        'game_records': 0,
        'users': 0
    }

    try:
        # 1. 删除广告观看记录
        if not dry_run:
            result = db.execute(text("""
                DELETE FROM ad_watch_records
                WHERE user_id IN :user_ids
            """), {'user_ids': tuple(user_ids)})
            deleted['ad_records'] = result.rowcount
            db.commit()
        else:
            deleted['ad_records'] = stats['ad_records']
        print(f"  ✓ 删除广告观看记录: {deleted['ad_records']}")

        # 2. 删除金币交易记录
        if not dry_run:
            result = db.execute(text("""
                DELETE FROM coin_transactions
                WHERE user_id IN :user_ids
            """), {'user_ids': tuple(user_ids)})
            deleted['coin_transactions'] = result.rowcount
            db.commit()
        else:
            deleted['coin_transactions'] = stats['coin_transactions']
        print(f"  ✓ 删除金币交易记录: {deleted['coin_transactions']}")

        # 3. 删除游戏记录
        if not dry_run:
            result = db.execute(text("""
                DELETE FROM game_records
                WHERE user_id IN :user_ids
            """), {'user_ids': tuple(user_ids)})
            deleted['game_records'] = result.rowcount
            db.commit()
        else:
            deleted['game_records'] = stats['game_records']
        print(f"  ✓ 删除游戏记录: {deleted['game_records']}")

        # 4. 删除用户账号
        if not dry_run:
            result = db.execute(text("""
                DELETE FROM users
                WHERE id IN :user_ids
            """), {'user_ids': tuple(user_ids)})
            deleted['users'] = result.rowcount
            db.commit()
        else:
            deleted['users'] = stats['users']
        print(f"  ✓ 删除用户账号: {deleted['users']}")

        print("\n" + "="*60)
        if dry_run:
            print("【预览完成】实际清理请运行:")
            print("  python cleanup_malicious_data.py")
        else:
            print("✅ 清理完成！")
            print(f"总计删除: {deleted['users']} 用户, "
                  f"{deleted['ad_records']} 广告记录, "
                  f"{deleted['coin_transactions']} 金币记录, "
                  f"{deleted['game_records']} 游戏记录")
        print("="*60 + "\n")

        return deleted

    except Exception as e:
        db.rollback()
        print(f"\n❌ 清理失败: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description='清理恶意数据工具')
    parser.add_argument('--dry-run', action='store_true', help='预览模式（不实际删除）')
    parser.add_argument('--auto', action='store_true', help='自动模式（无需确认）')

    args = parser.parse_args()

    db = next(get_db())

    try:
        # 分析数据
        data = analyze_malicious_data(db)

        if not data:
            db.close()
            return

        stats = data['stats']

        # 确认清理
        if not args.dry_run and not args.auto:
            print("⚠️  警告：此操作将永久删除数据，无法恢复！\n")
            confirm = input("确认清理以上数据？(yes/no): ").strip().lower()

            if confirm not in ['yes', 'y']:
                print("\n❌ 已取消")
                db.close()
                return

        # 执行清理
        print()
        cleanup_data(db, data, dry_run=args.dry_run)

        # 建议
        if not args.dry_run:
            print("\n💡 后续建议:")
            print("  1. 检查服务器日志，确认攻击已停止")
            print("  2. 启用速率限制中间件防止未来攻击")
            print("  3. 定期运行 check_historical_attacks.py 监控异常")
            print("  4. 考虑添加验证码到注册接口")
            print()

    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
