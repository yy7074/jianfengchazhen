#!/usr/bin/env python3
"""
排行榜接口测试脚本
用于验证修复后的排行榜功能
"""

import requests
import json
from datetime import datetime

def test_leaderboard_api():
    """测试排行榜API"""
    base_url = "http://localhost:3000"
    
    print("🧪 开始测试排行榜API...")
    
    try:
        # 测试排行榜接口
        response = requests.get(f"{base_url}/api/game/leaderboard")
        
        print(f"📡 请求URL: {response.url}")
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📋 响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 响应成功")
            print(f"📄 响应数据结构:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # 验证数据结构
            if data.get("code") == 200:
                leaderboard_data = data.get("data", {})
                leaderboard = leaderboard_data.get("leaderboard", [])
                
                print(f"\n🏆 排行榜数据验证:")
                print(f"   - 排行榜条目数: {len(leaderboard)}")
                print(f"   - 时间范围: {leaderboard_data.get('period', 'unknown')}")
                print(f"   - 总数: {leaderboard_data.get('total', 0)}")
                
                if leaderboard:
                    print(f"\n📋 排行榜详情:")
                    for i, player in enumerate(leaderboard[:5]):  # 只显示前5名
                        print(f"   {i+1}. {player.get('nickname', '未知玩家')} - 分数: {player.get('best_score', 0)}")
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
            try:
                error_data = response.json()
                print(f"错误详情: {error_data}")
            except:
                print(f"错误内容: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: 请确保后端服务在 http://localhost:3000 运行")
    except Exception as e:
        print(f"❌ 测试异常: {e}")

def test_with_different_periods():
    """测试不同时间范围的排行榜"""
    base_url = "http://localhost:3000"
    periods = ["all", "today", "week", "month"]
    
    print("\n🔄 测试不同时间范围的排行榜...")
    
    for period in periods:
        print(f"\n📅 测试时间范围: {period}")
        try:
            response = requests.get(f"{base_url}/api/game/leaderboard", params={"period": period})
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 200:
                    leaderboard_data = data.get("data", {})
                    count = len(leaderboard_data.get("leaderboard", []))
                    print(f"   ✅ 成功 - 返回 {count} 条记录")
                else:
                    print(f"   ❌ API错误: {data.get('message')}")
            else:
                print(f"   ❌ 请求失败: {response.status_code}")
        except Exception as e:
            print(f"   ❌ 异常: {e}")

if __name__ == "__main__":
    print("🎯 见缝插针游戏 - 排行榜API测试")
    print("=" * 50)
    
    test_leaderboard_api()
    test_with_different_periods()
    
    print("\n✨ 测试完成!")
    print("\n💡 如果看到空的排行榜，可能是因为:")
    print("   1. 数据库中没有游戏记录")
    print("   2. 需要先提交一些游戏结果")
    print("   3. 数据库连接配置问题")