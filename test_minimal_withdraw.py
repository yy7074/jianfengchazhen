#!/usr/bin/env python3
"""
最小提现功能测试 - 直接测试核心逻辑
"""

import subprocess
import json
import os

# 禁用代理
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

def create_user_with_coins():
    """创建有足够金币的用户"""
    user_data = {
        "device_id": "withdraw_test_final",
        "device_name": "Test Device",
        "nickname": "提现测试用户Final"
    }
    
    cmd = ['curl', '-s', '-X', 'POST', 
           'http://localhost:3001/api/user/register',
           '-H', 'Content-Type: application/json',
           '-d', json.dumps(user_data)]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    if result.returncode == 0:
        response = json.loads(result.stdout)
        if response.get("code") == 200:
            user_id = response["data"]["user_id"]
            print(f"✅ 用户创建成功: ID={user_id}")
            
            # 手动给用户添加很多金币（通过多次游戏奖励）
            for i in range(200):  # 200次游戏
                game_data = {
                    "score": 1000 + i,
                    "duration": 60,
                    "needles": 20,
                    "level": 5
                }
                
                cmd2 = ['curl', '-s', '-X', 'POST', 
                       f'http://localhost:3001/api/game/reward/{user_id}',
                       '-H', 'Content-Type: application/json',
                       '-d', json.dumps(game_data)]
                
                subprocess.run(cmd2, capture_output=True, text=True, timeout=5)
                
                if i % 50 == 0:
                    print(f"已完成 {i} 次游戏奖励...")
            
            return user_id
    
    print("❌ 用户创建失败")
    return None

def check_user_coins(user_id):
    """检查用户金币"""
    cmd = ['curl', '-s', f'http://localhost:3001/api/user/{user_id}/stats']
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    if result.returncode == 0:
        response = json.loads(result.stdout)
        if response.get("code") == 200:
            coins = response["data"]["current_coins"]
            print(f"💰 用户当前金币: {coins}")
            return coins
    return 0

def test_withdraw_direct(user_id):
    """直接测试提现"""
    print("\n💸 开始提现测试...")
    
    # 先检查金币
    coins = check_user_coins(user_id)
    if coins < 5000:
        print(f"❌ 金币不足，需要至少5000金币，当前只有{coins}")
        return False
    
    # 测试提现
    withdraw_data = {
        "amount": 1.0,  # 提现1元，需要1000金币
        "alipay_account": "test@example.com",
        "real_name": "测试用户"
    }
    
    cmd = ['curl', '-s', '-X', 'POST', 
           f'http://localhost:3001/api/user/withdraw?user_id={user_id}',
           '-H', 'Content-Type: application/json',
           '-d', json.dumps(withdraw_data)]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    if result.returncode == 0:
        print(f"提现响应: {result.stdout}")
        try:
            response = json.loads(result.stdout)
            if response.get("code") == 200:
                print("✅ 提现成功!")
                return True
        except:
            pass
    
    print("❌ 提现失败")
    return False

def main():
    print("🚀 最小提现功能测试...")
    
    # 1. 创建用户并添加金币
    user_id = create_user_with_coins()
    if not user_id:
        return
    
    # 2. 检查金币
    coins = check_user_coins(user_id)
    
    # 3. 测试提现
    if coins >= 1000:
        test_withdraw_direct(user_id)
    else:
        print(f"❌ 测试失败：金币不足 ({coins} < 1000)")

if __name__ == "__main__":
    main()
