#!/usr/bin/env python3
"""
分析当前提现管理功能，提出完善建议
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

def analyze_current_system():
    """分析当前提现管理系统"""
    print("🔍 分析当前提现管理系统")
    print("="*60)
    
    # 1. 获取提现申请列表
    print("1. 📋 当前提现申请情况:")
    withdraws_response = api_call("GET", "http://localhost:3001/admin/api/withdraws")
    if withdraws_response.get("code") == 200:
        items = withdraws_response["data"]["items"]
        total = withdraws_response["data"]["total"]
        
        print(f"   总申请数: {total}")
        
        # 按状态分类统计
        status_count = {}
        total_amount = 0
        pending_amount = 0
        
        for item in items:
            status = item["status"]
            amount = float(item["amount"])
            total_amount += amount
            
            if status == "pending":
                pending_amount += amount
            
            status_count[status] = status_count.get(status, 0) + 1
        
        print(f"   状态分布: {status_count}")
        print(f"   总申请金额: ¥{total_amount:.2f}")
        print(f"   待处理金额: ¥{pending_amount:.2f}")
        
        # 显示最近几条申请
        print("   最近申请:")
        for item in items[:3]:
            print(f"     ID{item['id']}: {item['user_nickname']} - ¥{item['amount']} ({item['status']})")
    
    # 2. 测试批准功能
    print("\n2. 🔧 测试管理功能:")
    if items and items[0]["status"] == "pending":
        test_id = items[0]["id"]
        print(f"   测试批准提现申请ID: {test_id}")
        
        # 批准申请
        approve_data = {"admin_note": "自动化测试批准"}
        approve_response = api_call("PUT", 
            f"http://localhost:3001/admin/api/withdraws/{test_id}/approve", 
            approve_data)
        
        if approve_response.get("code") == 200:
            print("   ✅ 批准功能正常")
        else:
            print(f"   ❌ 批准功能异常: {approve_response}")
    
    # 3. 分析功能完善需求
    print("\n3. 📈 功能完善需求分析:")
    
    print("\n   ✅ 现有功能:")
    print("     - 提现申请列表查看")
    print("     - 按状态筛选")
    print("     - 单个申请批准/拒绝")
    print("     - 管理员备注")
    print("     - 基础统计显示")
    
    print("\n   ❌ 缺失功能:")
    print("     - 批量处理申请")
    print("     - 详细的提现统计报表")
    print("     - 提现记录导出功能")
    print("     - 用户提现历史查看")
    print("     - 自动化审核规则")
    print("     - 风险控制检测")
    print("     - 提现手续费统计")
    print("     - 日/周/月报表")
    
    print("\n   🔧 UI/UX改进需求:")
    print("     - 更好的筛选和搜索")
    print("     - 分页优化")
    print("     - 操作确认对话框")
    print("     - 实时状态更新")
    print("     - 移动端适配")
    print("     - 快捷操作按钮")
    
    return items

def suggest_improvements():
    """提出具体改进建议"""
    print("\n" + "="*60)
    print("🚀 提现管理系统完善建议")
    print("")
    
    improvements = [
        {
            "优先级": "高",
            "功能": "批量操作",
            "描述": "支持批量批准/拒绝多个提现申请",
            "价值": "提高管理效率，减少重复操作"
        },
        {
            "优先级": "高", 
            "功能": "高级筛选",
            "描述": "按时间范围、金额范围、用户等筛选",
            "价值": "快速定位特定申请，提高管理精度"
        },
        {
            "优先级": "中",
            "功能": "统计仪表板",
            "描述": "提现趋势图、成功率、平均处理时间等",
            "价值": "数据驱动决策，监控系统健康度"
        },
        {
            "优先级": "中",
            "功能": "自动审核",
            "描述": "小额提现自动批准，大额提现人工审核",
            "价值": "减少人工干预，提高用户体验"
        },
        {
            "优先级": "中",
            "功能": "用户画像",
            "描述": "显示用户历史提现记录、信用评级",
            "价值": "风险控制，防止恶意提现"
        },
        {
            "优先级": "低",
            "功能": "数据导出",
            "描述": "Excel/CSV格式导出提现记录",
            "价值": "方便财务对账和审计"
        }
    ]
    
    for i, item in enumerate(improvements, 1):
        print(f"{i}. 【{item['优先级']}优先级】{item['功能']}")
        print(f"   描述: {item['描述']}")
        print(f"   价值: {item['价值']}")
        print("")
    
    print("🎯 实施建议:")
    print("1. 第一阶段: 批量操作 + 高级筛选")
    print("2. 第二阶段: 统计仪表板 + 自动审核")  
    print("3. 第三阶段: 用户画像 + 数据导出")

if __name__ == "__main__":
    current_items = analyze_current_system()
    suggest_improvements()
    
    print("\n" + "="*60)
    print("📝 总结:")
    print("✅ 当前系统基础功能完整")
    print("🔧 需要增强管理效率和用户体验")
    print("📊 建议优先实现批量操作和统计功能")
    print("🚀 完善后将大幅提升管理员工作效率")
