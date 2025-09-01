#!/usr/bin/env python3
"""
测试提现功能集成
"""

import requests
import json
import time
from datetime import datetime
import os

# 禁用代理
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'

BASE_URL = "http://localhost:3001"

def test_withdraw_flow():
    """测试完整的提现流程"""
    print("🔄 开始测试提现功能...\n")

    # 1. 创建测试用户
    print("1. 创建测试用户...")
    register_data = {
        "device_id": "test_device_withdraw",
        "device_name": "Test Device",
        "nickname": "测试用户"
    }

    try:
        response = requests.post(f"{BASE_URL}/api/user/register", json=register_data)
        print(f"注册响应: {response.status_code}")

        if response.status_code == 200:
            user_data = response.json()
            user_id = user_data["data"]["user_id"]
            print(f"✅ 用户创建成功: ID={user_id}")
        else:
            print(f"❌ 用户创建失败: {response.text}")
            return False

    except Exception as e:
        print(f"❌ 注册请求失败: {e}")
        return False

    # 2. 通过游戏奖励给用户添加金币
    print("\n2. 通过游戏奖励添加金币...")
    try:
        game_data = {
            "score": 100,
            "duration": 30,
            "needles_inserted": 5,
            "game_type": "normal",
            "difficulty_level": 1
        }

        # 提交多次游戏记录来积累金币
        total_coins = 0
        for i in range(5):  # 提交5次游戏
            response = requests.post(
                f"{BASE_URL}/api/game/submit/{user_id}",
                json=game_data
            )
            if response.status_code == 200:
                result = response.json()
                reward = result["data"]["reward_coins"]
                total_coins += reward
                print(f"第{i+1}次游戏奖励: {reward} 金币")
            else:
                print(f"第{i+1}次游戏提交失败: {response.text}")

        print(f"✅ 总共获得金币: {total_coins}")

        # 获取用户当前金币数
        response = requests.get(f"{BASE_URL}/api/user/info/{user_id}")
        if response.status_code == 200:
            user_info = response.json()
            current_coins = user_info["data"]["coins"]
            print(f"当前金币总数: {current_coins}")
        else:
            print(f"获取用户信息失败: {response.text}")
            return False

    except Exception as e:
        print(f"❌ 添加金币失败: {e}")
        return False

    # 3. 测试提现申请
    print("\n3. 测试提现申请...")
    withdraw_data = {
        "amount": 15.0,
        "alipay_account": "test_alipay@163.com",
        "real_name": "测试用户"
    }

    try:
        response = requests.post(f"{BASE_URL}/api/user/{user_id}/withdraw", json=withdraw_data)
        print(f"提现响应: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 200:
                print("✅ 提现申请成功!")
                print(f"响应数据: {result['data']}")
            else:
                print(f"❌ 提现申请失败: {result.get('message', '未知错误')}")
                return False
        else:
            print(f"❌ 提现请求失败: {response.text}")
            return False

    except Exception as e:
        print(f"❌ 提现请求失败: {e}")
        return False

    # 4. 测试获取提现历史
    print("\n4. 测试获取提现历史...")
    try:
        response = requests.get(f"{BASE_URL}/api/user/{user_id}/withdraws")
        print(f"历史响应: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 200:
                history = result.get("data", [])
                print(f"✅ 获取提现历史成功，共 {len(history)} 条记录")
                for record in history:
                    print(f"  - 金额: ¥{record.get('amount', 0)}, 状态: {record.get('status', '未知')}")
            else:
                print(f"❌ 获取历史失败: {result.get('message', '未知错误')}")
        else:
            print(f"❌ 获取历史请求失败: {response.text}")

    except Exception as e:
        print(f"❌ 获取历史请求失败: {e}")

    # 5. 测试重复提现（应该失败）
    print("\n5. 测试重复提现...")
    try:
        response = requests.post(f"{BASE_URL}/api/user/{user_id}/withdraw", json=withdraw_data)
        print(f"重复提现响应: {response.status_code}")

        if response.status_code == 400:
            result = response.json()
            print(f"✅ 重复提现正确被阻止: {result.get('detail', '未知原因')}")
        else:
            print(f"⚠️ 重复提现响应异常: {response.text}")

    except Exception as e:
        print(f"❌ 重复提现测试失败: {e}")

    print("\n🎉 提现功能测试完成!")
    return True

def test_ad_flow():
    """测试广告观看流程"""
    print("\n🎬 开始测试广告功能...\n")

    # 1. 创建测试用户
    print("1. 创建测试用户...")
    register_data = {
        "device_id": "test_device_ad",
        "device_name": "Test Device",
        "nickname": "广告测试用户"
    }

    try:
        response = requests.post(f"{BASE_URL}/api/user/register", json=register_data)
        print(f"注册响应: {response.status_code}")

        if response.status_code == 200:
            user_data = response.json()
            user_id = user_data["data"]["user_id"]
            print(f"✅ 用户创建成功: ID={user_id}")
        else:
            print(f"❌ 用户创建失败: {response.text}")
            return False

    except Exception as e:
        print(f"❌ 注册请求失败: {e}")
        return False

    # 2. 测试获取可用广告
    print("\n2. 测试获取可用广告...")
    try:
        response = requests.get(f"{BASE_URL}/api/ad/available/{user_id}")
        print(f"广告响应: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 200:
                ads_data = result.get("data", {})
                ads = ads_data.get("ads", [])
                print(f"✅ 获取可用广告成功，共 {len(ads)} 个广告")
                for ad in ads[:3]:  # 只显示前3个
                    print(f"  - {ad.get('name', '未知')} (奖励: {ad.get('reward_coins', 0)} 金币)")
            else:
                print(f"❌ 获取广告失败: {result.get('message', '未知错误')}")
                return False
        else:
            print(f"❌ 获取广告请求失败: {response.text}")
            return False

    except Exception as e:
        print(f"❌ 获取广告请求失败: {e}")
        return False

    print("\n🎉 广告功能测试完成!")
    return True

if __name__ == "__main__":
    print("🚀 开始集成测试...\n")

    # 测试提现功能
    withdraw_success = test_withdraw_flow()

    # 测试广告功能
    ad_success = test_ad_flow()

    print("\n" + "="*50)
    print("📊 测试结果汇总:")
    print(f"  提现功能: {'✅ 通过' if withdraw_success else '❌ 失败'}")
    print(f"  广告功能: {'✅ 通过' if ad_success else '❌ 失败'}")

    if withdraw_success and ad_success:
        print("\n🎉 所有测试通过！")
    else:
        print("\n⚠️ 部分测试失败，请检查相关功能。")
