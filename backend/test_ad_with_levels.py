#!/usr/bin/env python3
"""
测试APP广告播放功能，验证等级奖励系统
"""

import requests
import json
import random

# 服务器配置
BASE_URL = "http://8.137.103.175:3001"

def test_ad_system():
    """测试广告系统功能"""
    print("=== APP广告播放测试 ===\n")
    
    # 1. 测试获取可用广告
    print("1. 测试获取可用广告:")
    user_id = "1"  # 使用用户ID 1进行测试
    
    try:
        response = requests.get(f"{BASE_URL}/api/ad/available/{user_id}")
        print(f"请求: GET /api/ad/available/{user_id}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if data.get("data"):
                ads = data["data"]
                print(f"✅ 找到 {len(ads)} 个可用广告")
                for i, ad in enumerate(ads, 1):
                    print(f"  广告 {i}: {ad['name']} (权重: {ad['weight']}, 奖励: {ad['reward_coins']})")
            else:
                print("❌ 没有可用广告")
        else:
            print(f"❌ 获取广告失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 2. 测试获取随机广告
    print("2. 测试获取随机广告:")
    
    try:
        response = requests.get(f"{BASE_URL}/api/ad/random/{user_id}")
        print(f"请求: GET /api/ad/random/{user_id}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if data.get("data"):
                ad = data["data"]
                print(f"✅ 获取到随机广告: {ad['name']}")
                print(f"  类型: {ad['ad_type']}")
                print(f"  时长: {ad['duration']}秒")
                print(f"  奖励金币: {ad['reward_coins']}")
                print(f"  权重: {ad['weight']}")
                
                # 保存广告ID用于后续测试
                selected_ad_id = ad['id']
                
        else:
            print(f"❌ 获取随机广告失败: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return
    
    print("\n" + "="*50 + "\n")
    
    # 3. 模拟广告观看完成
    print("3. 测试广告观看完成:")
    
    watch_data = {
        "ad_id": str(selected_ad_id),  # 转换为字符串
        "watch_duration": 30,  # 观看30秒
        "is_completed": True   # 标记为完成
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/ad/watch/{user_id}",
            json=watch_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"请求: POST /api/ad/watch/{user_id}")
        print(f"数据: {json.dumps(watch_data, indent=2, ensure_ascii=False)}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if data.get("data"):
                result = data["data"]
                print(f"✅ 广告观看成功!")
                print(f"  获得金币: {result.get('reward_coins', 0)}")
                print(f"  观看时长: {result.get('watch_duration', 0)}秒")
                print(f"  是否完成: {result.get('is_completed', False)}")
                print(f"  观看记录ID: {result.get('watch_record_id', 'N/A')}")
                
        else:
            print(f"❌ 广告观看失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 4. 测试不同等级用户的奖励差异
    print("4. 测试不同等级用户的奖励:")
    
    # 创建几个不同等级的测试用户
    test_users = [
        {"id": "1", "level": 1, "name": "新手用户"},
        {"id": "2", "level": 3, "name": "白银用户"},
        {"id": "3", "level": 5, "name": "铂金用户"},
        {"id": "4", "level": 7, "name": "大师用户"}
    ]
    
    for user in test_users:
        try:
            # 获取随机广告
            response = requests.get(f"{BASE_URL}/api/ad/random/{user['id']}")
            if response.status_code == 200:
                ad_data = response.json()
                if ad_data.get("data"):
                    ad = ad_data["data"]
                    
                    # 模拟观看
                    watch_data = {
                        "ad_id": str(ad['id']),  # 转换为字符串
                        "watch_duration": ad['duration'],
                        "is_completed": True
                    }
                    
                    watch_response = requests.post(
                        f"{BASE_URL}/api/ad/watch/{user['id']}",
                        json=watch_data,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if watch_response.status_code == 200:
                        watch_result = watch_response.json()
                        if watch_result.get("data"):
                            reward = watch_result["data"].get("reward_coins", 0)
                            print(f"  {user['name']} (等级{user['level']}): 获得 {reward} 金币")
                        else:
                            print(f"  {user['name']}: 观看失败")
                    else:
                        print(f"  {user['name']}: 请求失败 - {watch_response.status_code}")
            else:
                print(f"  {user['name']}: 获取广告失败")
                
        except Exception as e:
            print(f"  {user['name']}: 测试异常 - {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 5. 测试广告观看限制
    print("5. 测试广告观看限制:")
    
    print("连续观看同一广告5次，测试日限制...")
    for i in range(5):
        try:
            # 获取随机广告
            ad_response = requests.get(f"{BASE_URL}/api/ad/random/{user_id}")
            if ad_response.status_code == 200:
                ad_data = ad_response.json()
                if ad_data.get("data"):
                    ad = ad_data["data"]
                    
                    # 观看广告
                    watch_data = {
                        "ad_id": str(ad['id']),  # 转换为字符串
                        "watch_duration": ad['duration'],
                        "is_completed": True
                    }
                    
                    watch_response = requests.post(
                        f"{BASE_URL}/api/ad/watch/{user_id}",
                        json=watch_data,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    print(f"  第{i+1}次观看: 状态码 {watch_response.status_code}")
                    if watch_response.status_code == 200:
                        result = watch_response.json()
                        if result.get("data"):
                            print(f"    ✅ 成功获得 {result['data'].get('reward_coins', 0)} 金币")
                        else:
                            print(f"    ❌ {result.get('message', '观看失败')}")
                    else:
                        print(f"    ❌ HTTP错误: {watch_response.text}")
                        
        except Exception as e:
            print(f"  第{i+1}次观看异常: {e}")
    
    print("\n✅ 广告播放测试完成!")

if __name__ == "__main__":
    test_ad_system()
