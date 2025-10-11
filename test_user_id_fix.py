#!/usr/bin/env python3
"""
测试用户ID修复
"""
import requests
import json

BASE_URL = "https://8089.dachaonet.com"

def test_register_user():
    """测试用户注册，检查返回的user_id字段"""
    print("=" * 60)
    print("测试1: 用户注册")
    print("=" * 60)
    
    url = f"{BASE_URL}/api/user/register"
    data = {
        "device_id": f"test_device_{int(requests.get('https://worldtimeapi.org/api/timezone/Etc/UTC').json()['unixtime'])}",
        "device_name": "Test Device",
        "nickname": "测试用户"
    }
    
    response = requests.post(url, json=data)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if "data" in result:
            user_data = result["data"]
            print(f"\n字段检查:")
            print(f"  - 包含 'id' 字段: {'id' in user_data}")
            print(f"  - 包含 'user_id' 字段: {'user_id' in user_data}")
            
            if 'user_id' in user_data:
                print(f"  - user_id 值: {user_data['user_id']}")
                print(f"  - user_id 类型: {type(user_data['user_id'])}")
                print(f"  ✓ user_id字段存在且有效")
                return user_data['user_id']
            else:
                print(f"  ✗ 缺少user_id字段")
                return None
    else:
        print(f"请求失败: {response.text}")
        return None

def test_get_user_info(user_id):
    """测试获取用户信息"""
    print("\n" + "=" * 60)
    print("测试2: 获取用户信息")
    print("=" * 60)
    
    url = f"{BASE_URL}/api/user/{user_id}"
    
    response = requests.get(url)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if "data" in result:
            user_data = result["data"]
            print(f"\n字段检查:")
            print(f"  - 包含 'id' 字段: {'id' in user_data}")
            print(f"  - 包含 'user_id' 字段: {'user_id' in user_data}")
            
            if 'user_id' in user_data:
                print(f"  - user_id 值: {user_data['user_id']}")
                print(f"  - user_id 类型: {type(user_data['user_id'])}")
                
                if str(user_data['user_id']) == str(user_id):
                    print(f"  ✓ user_id正确匹配")
                else:
                    print(f"  ✗ user_id不匹配 (期望: {user_id}, 实际: {user_data['user_id']})")
            else:
                print(f"  ✗ 缺少user_id字段 - 这会导致Android端用户ID为空!")
    else:
        print(f"请求失败: {response.text}")

def test_login_user():
    """测试用户登录"""
    print("\n" + "=" * 60)
    print("测试3: 用户登录")
    print("=" * 60)
    
    # 先注册一个用户
    device_id = f"login_test_{int(requests.get('https://worldtimeapi.org/api/timezone/Etc/UTC').json()['unixtime'])}"
    register_url = f"{BASE_URL}/api/user/register"
    register_data = {
        "device_id": device_id,
        "nickname": "登录测试用户"
    }
    
    requests.post(register_url, json=register_data)
    
    # 再登录
    login_url = f"{BASE_URL}/api/user/login"
    login_data = {
        "device_id": device_id
    }
    
    response = requests.post(login_url, json=login_data)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if "data" in result:
            user_data = result["data"]
            print(f"\n字段检查:")
            print(f"  - 包含 'user_id' 字段: {'user_id' in user_data}")
            
            if 'user_id' in user_data and user_data['user_id']:
                print(f"  - user_id 值: {user_data['user_id']}")
                print(f"  ✓ user_id字段存在且有效")
            else:
                print(f"  ✗ user_id字段缺失或为空")
    else:
        print(f"请求失败: {response.text}")

if __name__ == "__main__":
    print("开始测试用户ID字段修复...")
    print()
    
    # 测试注册
    user_id = test_register_user()
    
    # 测试获取用户信息
    if user_id:
        test_get_user_info(user_id)
    
    # 测试登录
    test_login_user()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

