#!/usr/bin/env python3
"""
Redis缓存优化测试脚本
测试IP黑名单、系统配置和广告列表的缓存性能
"""

import time
from database import get_db, redis_client
from services.ip_service import IPService
from services.config_service import ConfigService
from services.ad_service import AdService


def test_ip_blacklist_cache():
    """测试IP黑名单缓存"""
    print("\n" + "="*60)
    print("测试 1: IP黑名单检查缓存")
    print("="*60)

    db = next(get_db())
    test_ip = "192.168.1.100"

    try:
        # 清除缓存
        redis_client.delete(f"ip_blocked:{test_ip}")

        # 第一次查询（数据库）
        start = time.time()
        result1 = IPService.is_ip_blocked(db, test_ip)
        time1 = (time.time() - start) * 1000

        # 第二次查询（缓存）
        start = time.time()
        result2 = IPService.is_ip_blocked(db, test_ip)
        time2 = (time.time() - start) * 1000

        # 检查Redis缓存
        cached = redis_client.get(f"ip_blocked:{test_ip}")

        print(f"测试IP: {test_ip}")
        print(f"第一次查询（数据库）: {time1:.2f}ms - 结果: {result1}")
        print(f"第二次查询（缓存）: {time2:.2f}ms - 结果: {result2}")
        print(f"Redis缓存值: {cached}")
        print(f"性能提升: {((time1 - time2) / time1 * 100):.1f}%")

        if time2 < time1:
            print("✅ IP黑名单缓存工作正常！")
        else:
            print("⚠️  缓存可能未生效")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
    finally:
        db.close()


def test_config_cache():
    """测试系统配置缓存"""
    print("\n" + "="*60)
    print("测试 2: 系统配置缓存")
    print("="*60)

    db = next(get_db())
    config_key = "daily_ad_limit"

    try:
        # 清除缓存
        redis_client.delete(f"config:{config_key}")

        # 第一次查询（数据库）
        start = time.time()
        result1 = ConfigService.get_config(db, config_key, "20")
        time1 = (time.time() - start) * 1000

        # 第二次查询（缓存）
        start = time.time()
        result2 = ConfigService.get_config(db, config_key, "20")
        time2 = (time.time() - start) * 1000

        # 检查Redis缓存
        cached = redis_client.get(f"config:{config_key}")

        print(f"配置键: {config_key}")
        print(f"第一次查询（数据库）: {time1:.2f}ms - 结果: {result1}")
        print(f"第二次查询（缓存）: {time2:.2f}ms - 结果: {result2}")
        print(f"Redis缓存值: {cached}")
        print(f"性能提升: {((time1 - time2) / time1 * 100):.1f}%")

        if time2 < time1:
            print("✅ 系统配置缓存工作正常！")
        else:
            print("⚠️  缓存可能未生效")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
    finally:
        db.close()


def test_active_ads_cache():
    """测试活跃广告列表缓存"""
    print("\n" + "="*60)
    print("测试 3: 活跃广告列表缓存")
    print("="*60)

    db = next(get_db())

    try:
        # 清除缓存
        redis_client.delete("active_ads")

        # 第一次查询（数据库）
        start = time.time()
        result1 = AdService._get_active_ads_cached(db)
        time1 = (time.time() - start) * 1000

        # 第二次查询（缓存）
        start = time.time()
        result2 = AdService._get_active_ads_cached(db)
        time2 = (time.time() - start) * 1000

        # 检查Redis缓存
        cached = redis_client.get("active_ads")

        print(f"第一次查询（数据库）: {time1:.2f}ms - 广告数量: {len(result1)}")
        print(f"第二次查询（缓存）: {time2:.2f}ms - 广告数量: {len(result2)}")
        print(f"Redis缓存存在: {'是' if cached else '否'}")
        print(f"性能提升: {((time1 - time2) / time1 * 100):.1f}%")

        if time2 < time1:
            print("✅ 活跃广告缓存工作正常！")
        else:
            print("⚠️  缓存可能未生效")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
    finally:
        db.close()


def test_random_ad_performance():
    """测试获取随机广告的整体性能"""
    print("\n" + "="*60)
    print("测试 4: 获取随机广告整体性能")
    print("="*60)

    db = next(get_db())
    test_user_id = 1

    try:
        # 预热缓存
        AdService.get_random_ad(db, test_user_id)

        # 测试10次请求
        times = []
        for i in range(10):
            start = time.time()
            ad = AdService.get_random_ad(db, test_user_id)
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)

        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        print(f"测试次数: 10次")
        print(f"平均响应时间: {avg_time:.2f}ms")
        print(f"最快: {min_time:.2f}ms")
        print(f"最慢: {max_time:.2f}ms")

        if avg_time < 10:
            print("✅ 性能优秀！平均响应时间 < 10ms")
        elif avg_time < 20:
            print("✅ 性能良好！平均响应时间 < 20ms")
        else:
            print("⚠️  性能一般，可能需要进一步优化")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
    finally:
        db.close()


def check_redis_connection():
    """检查Redis连接"""
    print("\n" + "="*60)
    print("Redis连接检查")
    print("="*60)

    try:
        redis_client.ping()
        print("✅ Redis连接正常")

        # 获取一些Redis信息
        info = redis_client.info("stats")
        print(f"Redis命令统计:")
        print(f"  - 总命令数: {info.get('total_commands_processed', 'N/A')}")
        print(f"  - 命中次数: {info.get('keyspace_hits', 'N/A')}")
        print(f"  - 未命中次数: {info.get('keyspace_misses', 'N/A')}")

        return True
    except Exception as e:
        print(f"❌ Redis连接失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "🚀 " + "="*58)
    print("   Redis缓存优化测试")
    print("="*60 + "\n")

    if not check_redis_connection():
        print("\n❌ Redis未连接，无法继续测试")
        print("请确保Redis服务正在运行: redis-server")
        return

    # 运行所有测试
    test_ip_blacklist_cache()
    test_config_cache()
    test_active_ads_cache()
    test_random_ad_performance()

    print("\n" + "="*60)
    print("✅ 所有测试完成！")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
