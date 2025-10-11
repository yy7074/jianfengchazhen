#!/usr/bin/env python3
"""
测试提现API修复
"""

import requests
import json

def test_withdraw_api():
    """测试提现API"""
    base_url = "https://8089.dachaonet.com"
    
    print("=== 提现API测试 ===\n")
    
    # 使用已知的用户ID进行测试
    test_user_id = 32
    
    print(f"1. 测试提现申请 (用户ID: {test_user_id}):")
    
    try:
        # 测试提现申请
        withdraw_data = {
            "amount": 1.0,
            "alipay_account": "test@example.com",
            "real_name": "测试用户"
        }
        
        # 使用查询参数传递user_id
        response = requests.post(
            f"{base_url}/api/user/withdraw",
            params={"user_id": test_user_id},  # 作为查询参数
            json=withdraw_data
        )
        
        print(f"   POST /api/user/withdraw?user_id={test_user_id}: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
            print(f"   ✅ 提现申请成功")
        elif response.status_code == 400:
            data = response.json()
            print(f"   响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # 检查是否还有参数验证错误
            if "请求参数验证失败" in data.get("message", ""):
                print(f"   ❌ 仍有参数验证错误")
            else:
                print(f"   ⚠️  业务逻辑错误（如余额不足、已提现等）")
        else:
            print(f"   ❌ 请求失败: {response.text}")
            
    except Exception as e:
        print(f"   ❌ 测试异常: {e}")

def test_other_apis():
    """测试其他相关API"""
    base_url = "https://8089.dachaonet.com"
    test_user_id = 32
    
    print(f"\n2. 测试其他用户相关API:")
    
    # 测试获取用户信息
    try:
        response = requests.get(f"{base_url}/api/user/{test_user_id}")
        print(f"   GET /api/user/{test_user_id}: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ 获取用户信息成功")
        else:
            print(f"   ❌ 获取用户信息失败")
    except Exception as e:
        print(f"   ❌ 获取用户信息异常: {e}")
    
    # 测试获取提现历史
    try:
        response = requests.get(f"{base_url}/api/user/{test_user_id}/withdraws")
        print(f"   GET /api/user/{test_user_id}/withdraws: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ 获取提现历史成功")
        else:
            print(f"   ❌ 获取提现历史失败")
    except Exception as e:
        print(f"   ❌ 获取提现历史异常: {e}")

def show_fix_summary():
    """显示修复总结"""
    print(f"\n=== 提现API修复总结 ===")
    print(f"")
    print(f"🔧 问题:")
    print(f"   Android端传递 user_id 为 String 类型")
    print(f"   后端期望 user_id 为 int 类型")
    print(f"   导致参数验证失败: 'unable to parse string as an integer'")
    print(f"")
    print(f"🛠️ 修复:")
    print(f"   1. ApiService.kt - 修改 submitWithdrawRequest 参数类型")
    print(f"      @Query(\"user_id\") userId: String → userId: Int")
    print(f"")
    print(f"   2. WithdrawViewModel.kt - 修改调用方式")
    print(f"      currentUser.id.toString() → currentUser.id.toInt()")
    print(f"")
    print(f"✅ 预期效果:")
    print(f"   • 提现申请正常提交")
    print(f"   • 不再出现参数验证错误")
    print(f"   • 用户可以正常提现")

if __name__ == "__main__":
    test_withdraw_api()
    test_other_apis()
    show_fix_summary()
