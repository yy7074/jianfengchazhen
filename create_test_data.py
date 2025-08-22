#!/usr/bin/env python3
"""
创建测试数据脚本
为排行榜创建一些示例用户和游戏记录
"""

import requests
import json
import random
from datetime import datetime, timedelta
import os

# 设置requests不使用代理
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'

def create_test_data():
    """创建测试数据"""
    base_url = "http://localhost:3000"
    
    print("🧪 开始创建排行榜测试数据...")
    
    # 创建测试用户和游戏记录
    test_players = [
        {"nickname": "游戏高手", "device_id": "test_device_001", "scores": [2580, 2200, 1900, 2100]},
        {"nickname": "针法大师", "device_id": "test_device_002", "scores": [2340, 2000, 1800, 1950]},
        {"nickname": "插针王者", "device_id": "test_device_003", "scores": [2100, 1850, 1750, 1900]},
        {"nickname": "见缝达人", "device_id": "test_device_004", "scores": [1980, 1700, 1600, 1800]},
        {"nickname": "新手玩家", "device_id": "test_device_005", "scores": [680, 550, 420, 600]},
    ]
    
    created_users = []
    
    # 注册用户
    for player in test_players:
        try:
            print(f"📝 注册用户: {player['nickname']}")
            
            # 注册用户
            register_data = {
                "device_id": player["device_id"],
                "nickname": player["nickname"]
            }
            
            response = requests.post(f"{base_url}/api/user/register", json=register_data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 200:
                    user_data = result.get("data", {})
                    user_id = user_data.get("user_id")
                    print(f"   ✅ 用户创建成功，ID: {user_id}")
                    created_users.append({"user_id": user_id, **player})
                else:
                    print(f"   ⚠️ 用户可能已存在: {result.get('message')}")
                    # 尝试登录
                    login_response = requests.post(f"{base_url}/api/user/login", json={"device_id": player["device_id"]})
                    if login_response.status_code == 200:
                        login_result = login_response.json()
                        if login_result.get("code") == 200:
                            user_data = login_result.get("data", {})
                            user_id = user_data.get("user_id")
                            print(f"   ✅ 用户登录成功，ID: {user_id}")
                            created_users.append({"user_id": user_id, **player})
            else:
                print(f"   ❌ 注册失败: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 注册异常: {e}")
    
    # 为每个用户提交游戏记录
    for user in created_users:
        print(f"🎮 为用户 {user['nickname']} 创建游戏记录...")
        
        for i, score in enumerate(user["scores"]):
            try:
                game_data = {
                    "score": score,
                    "duration": random.randint(60, 300),  # 游戏时长60-300秒
                    "needles_inserted": random.randint(10, 50)  # 插入针数10-50
                }
                
                response = requests.post(f"{base_url}/api/game/submit/{user['user_id']}", json=game_data)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("code") == 200:
                        print(f"   ✅ 游戏记录 {i+1}: 分数 {score}")
                    else:
                        print(f"   ❌ 游戏记录失败: {result.get('message')}")
                else:
                    print(f"   ❌ 提交失败: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ 提交异常: {e}")
    
    print("\n🏆 测试数据创建完成！")

def test_leaderboard_with_data():
    """测试有数据的排行榜"""
    base_url = "http://localhost:3000"
    
    print("\n🧪 测试排行榜API（有数据）...")
    
    try:
        response = requests.get(f"{base_url}/api/game/leaderboard")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 响应成功")
            print(f"📄 响应数据:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if data.get("code") == 200:
                leaderboard_data = data.get("data", {})
                leaderboard = leaderboard_data.get("leaderboard", [])
                
                print(f"\n🏆 排行榜数据:")
                print(f"   - 排行榜条目数: {len(leaderboard)}")
                print(f"   - 时间范围: {leaderboard_data.get('period', 'unknown')}")
                print(f"   - 总数: {leaderboard_data.get('total', 0)}")
                
                if leaderboard:
                    print(f"\n📋 排行榜详情:")
                    for player in leaderboard:
                        print(f"   {player.get('rank', '?')}. {player.get('nickname', '未知玩家')} - 分数: {player.get('best_score', 0)}")
                        print(f"      用户ID: {player.get('user_id', 'unknown')}")
                        print(f"      等级: {player.get('level', 1)}")
                        print(f"      游戏次数: {player.get('game_count', 0)}")
                        print(f"      金币: {player.get('coins', 0)}")
                        if player.get('latest_play'):
                            print(f"      最后游戏: {player.get('latest_play')}")
                        print()
                else:
                    print("   ⚠️ 排行榜为空")
            else:
                print(f"❌ API返回错误: {data.get('message', '未知错误')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")

if __name__ == "__main__":
    print("🎯 见缝插针游戏 - 创建测试数据")
    print("=" * 50)
    
    create_test_data()
    test_leaderboard_with_data()
    
    print("\n✨ 测试完成!")
    print("\n🚀 现在可以测试Android客户端的排行榜功能了")