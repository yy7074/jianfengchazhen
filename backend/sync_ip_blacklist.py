#!/usr/bin/env python3
"""
同步IP黑名单到Redis - 定期运行此脚本或在启动时运行
使用方法:
  python sync_ip_blacklist.py          # 同步一次
  python sync_ip_blacklist.py --watch  # 持续监控并同步
"""
import sys
import time
import argparse
from database import get_db
from services.ip_service_optimized import IPServiceOptimized


def sync_once():
    """同步一次"""
    db = next(get_db())
    try:
        count = IPServiceOptimized.sync_blocked_ips_to_redis(db)
        print(f"✅ 同步完成: {count}个封禁IP已加载到Redis")
        return count
    except Exception as e:
        print(f"❌ 同步失败: {e}")
        return 0
    finally:
        db.close()


def sync_watch(interval=60):
    """持续监控并同步"""
    print(f"🔄 开始监控模式，每{interval}秒同步一次...")
    print("按 Ctrl+C 停止\n")

    try:
        while True:
            sync_once()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n✋ 已停止监控")


def main():
    parser = argparse.ArgumentParser(description='同步IP黑名单到Redis')
    parser.add_argument('--watch', action='store_true', help='持续监控模式')
    parser.add_argument('--interval', type=int, default=60, help='监控间隔（秒），默认60')

    args = parser.parse_args()

    if args.watch:
        sync_watch(args.interval)
    else:
        sync_once()


if __name__ == "__main__":
    main()
