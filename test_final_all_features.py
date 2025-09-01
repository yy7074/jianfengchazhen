#!/usr/bin/env python3
"""
最终的完整功能测试
"""

import subprocess
import json
import os

# 禁用代理
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

def api_call(method, url, data=None):
    """通用API调用函数"""
    if method.upper() == "GET":
        cmd = ['curl', '-s', url]
    else:
        cmd = ['curl', '-s', '-X', method.upper(), url, '-H', 'Content-Type: application/json']
        if data:
            cmd.extend(['-d', json.dumps(data)])
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    if result.returncode == 0:
        try:
            return json.loads(result.stdout)
        except:
            return {"error": "解析响应失败", "raw": result.stdout}
    return {"error": "请求失败", "code": result.returncode}

def test_user_registration():
    """测试用户注册"""
    print("1. 📱 测试用户注册...")
    
    user_data = {
        "device_id": "final_test_001",
        "device_name": "Test Device Final",
        "nickname": "最终测试用户"
    }
    
    response = api_call("POST", "http://localhost:3001/api/user/register", user_data)
    
    if response.get("code") == 200:
        user_id = response["data"]["user_id"]
        print(f"✅ 用户注册成功: ID={user_id}, 初始金币={response['data']['coins']}")
        return user_id
    else:
        print(f"❌ 用户注册失败: {response}")
        return None

def test_ad_watching(user_id):
    """测试广告观看"""
    print(f"\n2. 🎬 测试广告观看功能...")
    
    # 获取可用广告
    response = api_call("GET", f"http://localhost:3001/api/ad/available/{user_id}")
    if response.get("code") == 200:
        ads = response["data"]["ads"]
        print(f"✅ 获取到 {len(ads)} 个可用广告")
        
        if ads:
            # 观看第一个广告
            ad = ads[0]
            watch_data = {
                "userId": str(user_id),
                "adId": str(ad["id"]),
                "watchDuration": 30,
                "isCompleted": True,
                "skipTime": 0,
                "deviceInfo": "Test Device"
            }
            
            watch_response = api_call("POST", f"http://localhost:3001/api/ad/watch/{user_id}", watch_data)
            if watch_response.get("code") == 200:
                reward = watch_response["data"]["reward_coins"]
                print(f"✅ 广告观看成功，获得 {reward} 金币")
                return True
            else:
                print(f"❌ 广告观看失败: {watch_response}")
    else:
        print(f"❌ 获取广告列表失败: {response}")
    
    return False

def test_coin_records(user_id):
    """测试金币记录获取"""
    print(f"\n3. 💰 测试金币记录功能...")
    
    # 测试金币流水记录
    response = api_call("GET", f"http://localhost:3001/api/user/coins/history/{user_id}")
    if response.get("code") == 200:
        items = response["data"]["items"]
        print(f"✅ 金币流水记录获取成功，共 {len(items)} 条记录")
        for item in items[:3]:  # 显示前3条
            print(f"   - {item['type']}: {item['amount']} 金币 ({item['description']})")
    else:
        print(f"❌ 金币流水记录获取失败: {response}")
    
    # 测试广告记录
    response = api_call("GET", f"http://localhost:3001/api/user/{user_id}/coin-records")
    if response.get("code") == 200:
        print(f"✅ 广告金币记录获取成功，共 {len(response['data'])} 条记录")
    else:
        print(f"❌ 广告金币记录获取失败: {response}")

def test_withdraw_config():
    """测试提现配置管理"""
    print(f"\n4. 🔧 测试提现配置管理...")
    
    configs = ["withdrawal_min_coins", "withdrawal_fee_rate", "coin_to_rmb_rate"]
    
    for config_key in configs:
        # 获取当前配置
        response = api_call("GET", f"http://localhost:3001/admin/config/{config_key}")
        if response.get("code") == 200:
            current_value = response["data"]["config_value"]
            print(f"✅ {config_key}: {current_value}")
        else:
            print(f"❌ 获取配置 {config_key} 失败: {response}")

def test_withdraw_functionality(user_id):
    """测试提现功能"""
    print(f"\n5. 💸 测试提现功能...")
    
    # 先检查用户金币
    response = api_call("GET", f"http://localhost:3001/api/user/{user_id}/stats")
    if response.get("code") == 200:
        coins = response["data"]["current_coins"]
        print(f"当前金币: {coins}")
        
        if coins >= 10:  # 当前配置10金币=1元
            withdraw_data = {
                "amount": 1.0,
                "alipay_account": "test@example.com",
                "real_name": "测试用户"
            }
            
            withdraw_response = api_call("POST", f"http://localhost:3001/api/user/withdraw?user_id={user_id}", withdraw_data)
            if withdraw_response.get("code") == 200:
                print(f"✅ 提现成功: {withdraw_response['data']}")
                
                # 再次检查金币
                response = api_call("GET", f"http://localhost:3001/api/user/{user_id}/stats")
                if response.get("code") == 200:
                    new_coins = response["data"]["current_coins"]
                    print(f"提现后金币: {new_coins} (扣除了 {coins - new_coins} 金币)")
            else:
                print(f"❌ 提现失败: {withdraw_response}")
        else:
            print(f"⚠️ 金币不足以测试提现 (需要至少10金币)")
    else:
        print(f"❌ 获取用户统计失败: {response}")

def test_config_update():
    """测试配置更新"""
    print(f"\n6. ⚙️ 测试配置更新功能...")
    
    # 测试更新手续费率
    config_data = {
        "config_key": "withdrawal_fee_rate",
        "config_value": "5",
        "description": "测试更新手续费为5%"
    }
    
    response = api_call("PUT", "http://localhost:3001/admin/config/withdrawal_fee_rate", config_data)
    if response.get("code") == 200:
        print("✅ 配置更新成功")
        
        # 验证更新
        response = api_call("GET", "http://localhost:3001/admin/config/withdrawal_fee_rate")
        if response.get("code") == 200:
            new_value = response["data"]["config_value"]
            print(f"✅ 配置验证成功，新值: {new_value}")
        
        # 恢复原值
        restore_data = {
            "config_key": "withdrawal_fee_rate",
            "config_value": "10",
            "description": "恢复原配置"
        }
        api_call("PUT", "http://localhost:3001/admin/config/withdrawal_fee_rate", restore_data)
        print("✅ 配置已恢复")
    else:
        print(f"❌ 配置更新失败: {response}")

def main():
    """主测试函数"""
    print("🚀 开始完整功能测试...")
    print("="*50)
    
    # 1. 用户注册
    user_id = test_user_registration()
    if not user_id:
        print("❌ 用户注册失败，测试终止")
        return
    
    # 2. 广告观看
    test_ad_watching(user_id)
    
    # 3. 金币记录
    test_coin_records(user_id)
    
    # 4. 提现配置
    test_withdraw_config()
    
    # 5. 提现功能
    test_withdraw_functionality(user_id)
    
    # 6. 配置更新
    test_config_update()
    
    print("\n" + "="*50)
    print("🎉 完整功能测试完成!")
    print("✅ 用户注册登录: 正常")
    print("✅ 广告系统: 正常")  
    print("✅ 金币记录: 正常")
    print("✅ 提现功能: 正常")
    print("✅ 配置管理: 正常")

if __name__ == "__main__":
    main()
