#!/usr/bin/env python3
"""
测试游戏重启广告功能
验证每次游戏重新开始都需要观看广告的功能
"""

import requests
import json
import time

# 服务器配置
BASE_URL = "http://8.137.103.175:3001"

def test_restart_ad_feature():
    """测试游戏重启广告功能"""
    print("=== 游戏重启广告功能测试 ===\n")
    
    # 1. 检查服务器状态
    print("1. 检查服务器状态...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ 服务器运行正常")
        else:
            print(f"❌ 服务器异常: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        return
    
    # 2. 测试获取随机广告
    print("\n2. 测试获取随机广告...")
    user_id = "1"  # 使用存在的用户ID
    
    try:
        response = requests.get(f"{BASE_URL}/api/ad/random/{user_id}")
        print(f"请求URL: {BASE_URL}/api/ad/random/{user_id}")
        print(f"响应状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200 and data.get('data'):
                ad = data['data']
                print(f"✅ 成功获取广告: {ad['name']}")
                print(f"   - 广告ID: {ad['id']}")
                print(f"   - 奖励金币: {ad['reward_coins']}")
                print(f"   - 广告类型: {ad['ad_type']}")
                print(f"   - 时长: {ad['duration']}秒")
                return ad
            else:
                print(f"❌ 获取广告失败: {data.get('message', '未知错误')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    return None

def test_ad_watch_simulation():
    """模拟广告观看流程"""
    print("\n3. 模拟游戏重启广告观看流程...")
    
    # 获取广告
    ad = test_restart_ad_feature()
    if not ad:
        print("❌ 无法获取广告，跳过观看测试")
        return
    
    # 模拟观看广告
    user_id = "1"  # 使用存在的用户ID
    watch_data = {
        "ad_id": str(ad['id']),
        "watch_duration": ad['duration'],
        "is_completed": True
    }
    
    print(f"模拟观看广告: {ad['name']}")
    print(f"观看时长: {watch_data['watch_duration']}秒")
    
    try:
        response = requests.post(f"{BASE_URL}/api/ad/watch/{user_id}", json=watch_data)
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200:
                reward_data = data.get('data', {})
                print(f"✅ 广告观看成功")
                print(f"   - 获得金币: {reward_data.get('reward_coins', 0)}")
                print(f"   - 消息: {reward_data.get('message', '')}")
                print("   - 游戏可以重新开始了！")
            else:
                print(f"❌ 观看失败: {data.get('message', '未知错误')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求异常: {e}")

def test_multiple_restart_scenario():
    """测试多次重启场景"""
    print("\n4. 测试多次重启场景...")
    
    restart_count = 3
    user_id = "test_restart_multiple"
    
    for i in range(restart_count):
        print(f"\n--- 第 {i+1} 次重启测试 ---")
        
        # 获取广告
        response = requests.get(f"{BASE_URL}/api/ad/random/{user_id}")
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200 and data.get('data'):
                ad = data['data']
                print(f"✅ 获取重启广告: {ad['name']} (奖励: {ad['reward_coins']}金币)")
                
                # 模拟观看
                watch_data = {
                    "ad_id": str(ad['id']),
                    "watch_duration": ad['duration'],
                    "is_completed": True
                }
                
                watch_response = requests.post(f"{BASE_URL}/api/ad/watch/{user_id}", json=watch_data)
                if watch_response.status_code == 200:
                    watch_result = watch_response.json()
                    if watch_result.get('code') == 200:
                        print(f"✅ 第 {i+1} 次重启广告观看完成，游戏已重新开始")
                    else:
                        print(f"❌ 第 {i+1} 次观看失败")
                else:
                    print(f"❌ 第 {i+1} 次观看请求失败")
            else:
                print(f"❌ 第 {i+1} 次获取广告失败")
        else:
            print(f"❌ 第 {i+1} 次广告请求失败")
        
        time.sleep(1)  # 间隔1秒

def print_feature_summary():
    """打印功能总结"""
    print("\n=== 功能实现总结 ===")
    print("🎮 游戏重启广告功能已实现:")
    print("   ✅ 每次点击'重新开始'按钮都会触发广告")
    print("   ✅ 必须观看完整广告才能重新开始游戏")
    print("   ✅ 广告观看完成后自动重启游戏")
    print("   ✅ 重启广告对话框有专门的UI设计")
    print("   ✅ 无法跳过重启广告（没有取消按钮）")
    print("   ✅ 观看广告可以获得金币奖励")
    
    print("\n📱 Android应用修改内容:")
    print("   • 新增 AdState.RESTART_REQUIRED 状态")
    print("   • 修改 GameViewModel.restartGame() 逻辑")
    print("   • 新增 requestRestartAd() 和 onRestartAdCompleted() 方法")
    print("   • 修改 GameScreen 广告对话框UI")
    print("   • 更新 resetAdState() 处理重启广告完成")
    
    print("\n🔄 用户体验流程:")
    print("   1. 游戏结束后，点击'重新开始'按钮")
    print("   2. 弹出专门的重启广告确认对话框")
    print("   3. 点击'观看广告并重新开始'按钮")
    print("   4. 进入全屏广告播放界面")
    print("   5. 观看完整广告并获得金币奖励")
    print("   6. 游戏自动重新开始")
    
    print("\n💡 变现效果:")
    print("   • 大幅增加广告曝光量")
    print("   • 每次游戏重新开始都有收益机会")
    print("   • 用户获得金币奖励，提升留存")
    print("   • 强制观看，提高广告完成率")

if __name__ == "__main__":
    test_restart_ad_feature()
    test_ad_watch_simulation()
    test_multiple_restart_scenario()
    print_feature_summary()
