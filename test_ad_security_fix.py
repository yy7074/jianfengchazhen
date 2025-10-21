#!/usr/bin/env python3
"""
测试广告观看安全修复
验证即使客户端发送 is_completed=True，服务端也会验证实际观看时长
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_ad_security():
    print("=" * 60)
    print("测试广告观看安全修复")
    print("=" * 60)
    
    # 1. 先注册一个测试用户
    print("\n1. 注册测试用户...")
    register_data = {
        "device_id": "test_device_security_001",
        "device_name": "Security Test Device",
        "nickname": "安全测试用户"
    }
    
    response = requests.post(f"{BASE_URL}/api/users/register", json=register_data)
    print(f"注册响应: {response.status_code}")
    if response.status_code == 200:
        user_data = response.json()
        user_id = str(user_data['data']['id'])
        print(f"用户ID: {user_id}")
        print(f"初始金币: {user_data['data']['coins']}")
    else:
        print(f"注册失败: {response.text}")
        return
    
    # 2. 获取一个广告
    print("\n2. 获取随机广告...")
    response = requests.get(f"{BASE_URL}/api/ads/random/{user_id}")
    print(f"响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        ad_data = response.json()['data']
        ad_id = str(ad_data['id'])
        min_watch_duration = ad_data['min_watch_duration']
        print(f"广告ID: {ad_id}")
        print(f"广告名称: {ad_data['name']}")
        print(f"最小观看时长: {min_watch_duration}秒")
        print(f"奖励金币: {ad_data['reward_coins']}")
    else:
        print(f"获取广告失败: {response.text}")
        return
    
    # 3. 测试1：发送观看时长不够但is_completed=True的请求（应该被拒绝）
    print("\n3. 测试1：观看时长不够但is_completed=True")
    print(f"   发送观看时长: {min_watch_duration - 5}秒 (不足要求)")
    print(f"   发送is_completed: True (尝试欺骗)")
    
    watch_data = {
        "ad_id": ad_id,
        "watch_duration": min_watch_duration - 5,  # 故意发送不够的时长
        "is_completed": True,  # 但声称已完成
        "device_info": "Security Test"
    }
    
    response = requests.post(f"{BASE_URL}/api/ads/watch/{user_id}", json=watch_data)
    print(f"响应状态码: {response.status_code}")
    result = response.json()
    print(f"响应数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if result.get('data'):
        reward_coins = result['data'].get('reward_coins', 0)
        is_completed = result['data'].get('is_completed', False)
        user_coins = result['data'].get('user_coins', 0)
        
        print(f"\n结果分析:")
        print(f"  是否完成: {is_completed}")
        print(f"  获得金币: {reward_coins}")
        print(f"  用户总金币: {user_coins}")
        
        if is_completed or reward_coins > 0:
            print(f"  ❌ 测试失败！观看时长不够却获得了奖励！")
            print(f"  这是一个安全漏洞，需要修复！")
        else:
            print(f"  ✅ 测试通过！观看时长不够，正确地没有获得奖励")
    
    # 4. 测试2：发送足够的观看时长（应该获得奖励）
    print("\n4. 测试2：观看时长足够")
    print(f"   发送观看时长: {min_watch_duration + 2}秒 (满足要求)")
    
    watch_data = {
        "ad_id": ad_id,
        "watch_duration": min_watch_duration + 2,  # 发送足够的时长
        "is_completed": False,  # 即使声称未完成
        "device_info": "Security Test"
    }
    
    response = requests.post(f"{BASE_URL}/api/ads/watch/{user_id}", json=watch_data)
    print(f"响应状态码: {response.status_code}")
    result = response.json()
    print(f"响应数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if result.get('data'):
        reward_coins = result['data'].get('reward_coins', 0)
        is_completed = result['data'].get('is_completed', False)
        user_coins = result['data'].get('user_coins', 0)
        
        print(f"\n结果分析:")
        print(f"  是否完成: {is_completed}")
        print(f"  获得金币: {reward_coins}")
        print(f"  用户总金币: {user_coins}")
        
        if is_completed and reward_coins > 0:
            print(f"  ✅ 测试通过！观看时长足够，正确地获得了奖励")
        else:
            print(f"  ❌ 测试失败！观看时长足够却没有获得奖励！")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_ad_security()
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()

