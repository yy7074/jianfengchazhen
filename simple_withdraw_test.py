#!/usr/bin/env python3
"""
简单的提现功能测试
"""

import subprocess
import json

def test_health():
    """测试健康检查"""
    cmd = ['curl', '-s', 'http://localhost:3001/health']
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ API连接正常")
            return True
        else:
            print(f"❌ API连接失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ API连接异常: {e}")
        return False

def test_user_register():
    """测试用户注册"""
    user_data = {
        "device_id": "test_withdraw_simple_001",
        "device_name": "Test Device",
        "nickname": "提现测试用户"
    }
    
    cmd = ['curl', '-s', '-X', 'POST', 
           'http://localhost:3001/api/user/register',
           '-H', 'Content-Type: application/json',
           '-d', json.dumps(user_data)]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            response = json.loads(result.stdout)
            if response.get("code") == 200:
                user_id = response["data"]["user_id"]
                print(f"✅ 用户注册成功: ID={user_id}")
                return user_id
        print(f"❌ 用户注册失败: {result.stdout}")
        return None
    except Exception as e:
        print(f"❌ 用户注册异常: {e}")
        return None

def add_coins_via_ad(user_id):
    """通过广告观看增加金币"""
    ad_data = {
        "userId": str(user_id),
        "adId": "1",
        "watchDuration": 30,
        "isCompleted": True,
        "skipTime": 0,
        "deviceInfo": "Test Device"
    }
    
    for i in range(20):  # 观看20次广告
        cmd = ['curl', '-s', '-X', 'POST', 
               f'http://localhost:3001/api/ad/watch/{user_id}',
               '-H', 'Content-Type: application/json',
               '-d', json.dumps(ad_data)]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                response = json.loads(result.stdout)
                if response.get("code") == 200:
                    reward = response["data"]["reward_coins"]
                    print(f"第{i+1}次广告观看: +{reward} 金币")
        except:
            pass

def get_user_stats(user_id):
    """获取用户统计"""
    cmd = ['curl', '-s', f'http://localhost:3001/api/user/stats/{user_id}']
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            response = json.loads(result.stdout)
            if response.get("code") == 200:
                return response["data"]
    except:
        pass
    return None

def test_withdraw(user_id, amount):
    """测试提现功能"""
    withdraw_data = {
        "amount": amount,
        "alipay_account": "test@example.com",
        "real_name": "测试用户"
    }
    
    cmd = ['curl', '-s', '-X', 'POST', 
           f'http://localhost:3001/api/user/withdraw?user_id={user_id}',
           '-H', 'Content-Type: application/json',
           '-d', json.dumps(withdraw_data)]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            response = json.loads(result.stdout)
            print(f"提现申请响应: {response}")
            return response
    except Exception as e:
        print(f"❌ 提现申请异常: {e}")
    return None

def get_config(key):
    """获取配置"""
    cmd = ['curl', '-s', f'http://localhost:3001/admin/config/{key}']
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            response = json.loads(result.stdout)
            if response.get("code") == 200:
                return response["data"]["config_value"]
    except:
        pass
    return None

def update_config(key, value):
    """更新配置"""
    config_data = {
        "config_value": str(value),
        "description": f"测试更新{key}"
    }
    
    cmd = ['curl', '-s', '-X', 'PUT', 
           f'http://localhost:3001/admin/config/{key}',
           '-H', 'Content-Type: application/json',
           '-d', json.dumps(config_data)]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            response = json.loads(result.stdout)
            if response.get("code") == 200:
                print(f"✅ 配置更新成功: {key} = {value}")
                return True
    except:
        pass
    
    print(f"❌ 配置更新失败: {key}")
    return False

def main():
    """主测试函数"""
    print("🚀 开始提现功能测试...")
    
    # 1. 测试连接
    if not test_health():
        return
    
    # 2. 测试用户注册
    print("\n👤 注册测试用户...")
    user_id = test_user_register()
    if not user_id:
        return
    
    # 3. 增加金币
    print(f"\n💰 为用户增加金币...")
    add_coins_via_ad(user_id)
    
    # 4. 查看用户统计
    print(f"\n📊 查看用户统计...")
    stats = get_user_stats(user_id)
    if stats:
        print(f"当前金币: {stats['current_coins']}")
        print(f"总金币: {stats['total_coins']}")
    
    # 5. 查看当前提现配置
    print(f"\n🔧 查看提现配置...")
    configs = {
        "min_withdraw_amount": get_config("min_withdraw_amount"),
        "max_withdraw_amount": get_config("max_withdraw_amount"),
        "coin_to_rmb_rate": get_config("coin_to_rmb_rate"),
        "withdrawal_fee_rate": get_config("withdrawal_fee_rate"),
        "withdrawal_min_coins": get_config("withdrawal_min_coins")
    }
    
    for key, value in configs.items():
        print(f"  {key}: {value}")
    
    # 6. 测试提现（应该成功）
    print(f"\n💸 测试提现 5元...")
    result = test_withdraw(user_id, 5.0)
    
    # 7. 测试配置更新
    print(f"\n🔧 测试配置更新...")
    
    # 更新最小金币要求到很高的值
    print(f"设置最小金币要求为 5000...")
    update_config("withdrawal_min_coins", "5000")
    
    # 再次尝试提现（应该失败）
    print(f"再次尝试提现 5元...")
    result = test_withdraw(user_id, 5.0)
    
    # 恢复原配置
    print(f"\n🔄 恢复原配置...")
    update_config("withdrawal_min_coins", configs["withdrawal_min_coins"])
    
    # 8. 测试手续费配置
    print(f"\n💰 测试手续费配置...")
    
    # 设置10%手续费
    update_config("withdrawal_fee_rate", "10")
    
    # 尝试提现
    print(f"设置10%手续费后尝试提现 3元...")
    result = test_withdraw(user_id, 3.0)
    
    # 恢复手续费配置
    update_config("withdrawal_fee_rate", configs["withdrawal_fee_rate"])
    
    print(f"\n🎉 测试完成!")

if __name__ == "__main__":
    main()
