#!/usr/bin/env python3
"""
测试后台统计数据修复
验证广告金币统计是否准确
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_admin_stats():
    print("=" * 60)
    print("测试后台统计数据")
    print("=" * 60)
    
    # 注意：这个测试需要先登录管理后台
    # 可以手动在浏览器中访问 http://localhost:8000/admin/ 查看效果
    
    print("\n请手动测试以下内容：")
    print("\n1. 登录管理后台:")
    print(f"   访问: {BASE_URL}/admin/")
    print(f"   用户名: admin")
    print(f"   密码: (你的管理员密码)")
    
    print("\n2. 查看仪表盘统计:")
    print("   ✓ 检查是否显示 '广告金币总计'")
    print("   ✓ 检查是否显示 '今日广告发放'")
    print("   ✓ 验证数字只统计广告奖励")
    
    print("\n3. 验证数据准确性:")
    print("   方法1: 查看数据库")
    print("   SELECT SUM(reward_coins) FROM ad_watch_records;  -- 广告金币总计")
    print("   SELECT SUM(reward_coins) FROM ad_watch_records WHERE DATE(watch_time) = CURDATE();  -- 今日广告金币")
    
    print("\n4. Android APP提现信息保存测试:")
    print("   步骤1: 打开APP，进入提现页面")
    print("   步骤2: 输入支付宝账号和真实姓名")
    print("   步骤3: 选择提现金额并提交")
    print("   步骤4: 返回首页，再次进入提现页面")
    print("   预期: 支付宝账号和真实姓名应该自动填充 ✅")
    
    print("\n" + "=" * 60)
    print("测试说明完成")
    print("=" * 60)

def check_api_health():
    """检查API是否正常运行"""
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务运行正常")
            return True
    except:
        pass
    
    print("❌ 后端服务未运行")
    print(f"   请先启动后端服务：cd backend && python main.py")
    return False

if __name__ == "__main__":
    print("\n检查后端服务状态...")
    if check_api_health():
        print()
        test_admin_stats()
    else:
        print("\n请先启动后端服务，然后重新运行此脚本。")

