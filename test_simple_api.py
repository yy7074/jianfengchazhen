#!/usr/bin/env python3
"""
简单API连接测试
"""

import requests
import os

# 禁用代理
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'

def test_api_connection():
    """测试API连接"""
    try:
        response = requests.get("http://localhost:3001/")
        print(f"根路径响应: {response.status_code}")
        print(f"响应内容: {response.text[:200]}...")
        return True
    except Exception as e:
        print(f"连接失败: {e}")
        return False

def test_user_register():
    """测试用户注册"""
    try:
        register_data = {
            "device_id": "test_device_simple",
            "device_name": "Test Device",
            "nickname": "测试用户"
        }

        response = requests.post(
            "http://localhost:3001/api/user/register",
            json=register_data,
            timeout=10
        )
        print(f"注册响应: {response.status_code}")
        if response.status_code == 200:
            print(f"注册成功: {response.json()}")
        else:
            print(f"注册失败: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"注册请求失败: {e}")
        return False

if __name__ == "__main__":
    print("🔄 开始简单API测试...\n")

    print("1. 测试API连接...")
    if test_api_connection():
        print("✅ API连接正常\n")
    else:
        print("❌ API连接失败\n")
        exit(1)

    print("2. 测试用户注册...")
    if test_user_register():
        print("✅ 用户注册正常")
    else:
        print("❌ 用户注册失败")
