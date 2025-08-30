#!/usr/bin/env python3
"""
完整功能测试脚本 - 广告观看和提现功能
"""
import requests
import json
import time

BASE_URL = "http://8089.dachaonet.com"
USER_ID = 9

def test_ad_watch():
    """测试广告观看功能"""
    print("🎬 测试广告观看功能...")
    
    # 1. 获取可用广告
    response = requests.get(f"{BASE_URL}/api/ad/available/{USER_ID}")
    if response.status_code == 200:
        ads = response.json()['data']['ads']
        print(f"✅ 获取到 {len(ads)} 个可用广告")
        
        if ads:
            # 选择第一个广告进行测试
            ad = ads[0]
            print(f"📺 测试观看广告: {ad['name']} (奖励 {ad['reward_coins']} 金币)")
            
            # 2. 观看广告
            watch_data = {
                "ad_id": str(ad['id']),
                "watch_duration": 15,
                "is_completed": True,
                "device_info": "Test"
            }
            
            watch_response = requests.post(
                f"{BASE_URL}/api/ad/watch/{USER_ID}",
                json=watch_data,
                headers={"Content-Type": "application/json"}
            )
            
            if watch_response.status_code == 200:
                result = watch_response.json()
                reward = result['data']['reward_coins']
                new_coins = result['data']['user_coins']
                print(f"✅ 广告观看成功! 获得 {reward} 金币，当前总金币: {new_coins}")
                return new_coins
            else:
                error = watch_response.json()
                print(f"❌ 广告观看失败: {error.get('detail', '未知错误')}")
                return None
    else:
        print(f"❌ 获取广告失败: {response.status_code}")
        return None

def test_withdraw(current_coins):
    """测试提现功能"""
    print(f"\n💸 测试提现功能 (当前金币: {current_coins})...")
    
    if current_coins < 100:
        print("❌ 金币不足，无法测试提现")
        return
    
    # 提现申请
    withdraw_data = {
        "amount": 10.0,  # 提现10元
        "alipay_account": "test@example.com",
        "real_name": "测试用户"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/user/withdraw?user_id={USER_ID}",
            json=withdraw_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📡 提现申请状态: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 提现申请成功!")
            print(f"   申请ID: {result['data']['request_id']}")
            print(f"   申请金额: {result['data']['amount']} 元")
            print(f"   消耗金币: {result['data']['coins_used']}")
            print(f"   状态: {result['data']['status']}")
            return result['data']['request_id']
        else:
            error_text = response.text
            print(f"❌ 提现申请失败: {error_text}")
            return None
            
    except Exception as e:
        print(f"❌ 提现请求异常: {e}")
        return None

def check_user_stats():
    """检查用户统计信息"""
    print("\n📊 检查用户统计信息...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/user/{USER_ID}/stats")
        if response.status_code == 200:
            stats = response.json()['data']
            print(f"💰 当前金币: {stats['current_coins']}")
            print(f"🎯 最高分: {stats['best_score']}")
            print(f"🎮 游戏次数: {stats['game_count']}")
            return stats['current_coins']
        else:
            print(f"❌ 获取统计失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None

def main():
    """主测试流程"""
    print("🎯 完整功能测试开始\n")
    
    # 1. 检查初始状态
    initial_coins = check_user_stats()
    
    # 2. 测试广告观看
    new_coins = test_ad_watch()
    
    # 3. 再次检查金币变化
    if new_coins:
        time.sleep(1)
        current_coins = check_user_stats()
        if current_coins and initial_coins:
            earned = current_coins - initial_coins
            if earned > 0:
                print(f"🎉 广告观看成功，获得 {earned} 金币!")
    
    # 4. 测试提现功能
    if current_coins:
        withdraw_id = test_withdraw(current_coins)
        
        if withdraw_id:
            print(f"\n🔍 查看提现历史...")
            try:
                history_response = requests.get(f"{BASE_URL}/api/user/{USER_ID}/withdraws")
                if history_response.status_code == 200:
                    withdraws = history_response.json()['data']
                    print(f"📋 提现记录 ({len(withdraws)} 条):")
                    for w in withdraws[:3]:
                        print(f"   ID {w['id']}: {w['amount']}元 - {w['status']} ({w['request_time']})")
            except Exception as e:
                print(f"❌ 获取提现历史失败: {e}")
    
    # 5. 最终统计
    final_coins = check_user_stats()
    
    print(f"\n📈 测试总结:")
    print(f"  💰 初始金币: {initial_coins}")
    print(f"  💰 最终金币: {final_coins}")
    if initial_coins and final_coins:
        change = final_coins - initial_coins
        print(f"  📊 金币变化: {change:+}")
    print(f"  🎉 功能测试完成!")

if __name__ == "__main__":
    main()
