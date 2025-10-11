#!/usr/bin/env python3
"""
设置每日提现次数为5次
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from database import get_db
from services.config_service import ConfigService
from sqlalchemy import text

def set_daily_limit_to_5():
    """设置每日提现次数为5次"""
    print("🔧 设置每日提现次数为 5 次...")
    
    db = next(get_db())
    
    try:
        # 更新配置为5次
        config = ConfigService.set_config(
            db, 
            "daily_withdraw_limit", 
            "5", 
            "每日提现次数限制"
        )
        
        print(f"✅ 配置已更新: {config.config_key} = {config.config_value}")
        
        # 验证更新
        current_limit = ConfigService.get_daily_withdraw_limit(db)
        print(f"✅ 验证成功: 当前每日提现次数限制 = {current_limit}")
        
        # 检查用户32今天的提现记录
        withdraw_result = db.execute(text("""
            SELECT COUNT(*) as count, 
                   GROUP_CONCAT(CONCAT('¥', amount, '(', status, ')') SEPARATOR ', ') as records
            FROM withdraw_requests 
            WHERE user_id = 32 
            AND DATE(request_time) = CURDATE()
        """))
        
        result = withdraw_result.fetchone()
        today_count = result.count
        records = result.records or "无记录"
        
        print(f"\n📊 用户32今天的提现情况:")
        print(f"   已提现次数: {today_count}")
        print(f"   提现记录: {records}")
        print(f"   新的限制: {current_limit} 次")
        print(f"   剩余次数: {current_limit - today_count}")
        
        if today_count < current_limit:
            print(f"✅ 用户现在可以继续提现！还可以提现 {current_limit - today_count} 次")
        else:
            print(f"⚠️  用户今天已达到新的限制次数")
        
        # 检查API配置是否已更新
        print(f"\n🌐 验证API配置:")
        try:
            import requests
            response = requests.get("https://8089.dachaonet.com/api/user/app-config")
            if response.status_code == 200:
                api_config = response.json()
                api_limit = api_config.get('data', {}).get('daily_withdraw_limit', 'N/A')
                print(f"   API返回的每日提现次数: {api_limit}")
                if str(api_limit) == "5":
                    print(f"   ✅ API配置已同步")
                else:
                    print(f"   ⚠️  API配置可能需要时间同步")
            else:
                print(f"   ❌ API请求失败: {response.status_code}")
        except Exception as e:
            print(f"   ❌ API请求异常: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 设置失败: {e}")
        return False
    
    finally:
        db.close()

def show_android_effect():
    """显示Android端效果"""
    print(f"\n📱 Android端效果:")
    print(f"   • 提现规则将显示: '每天最多可提现5次'")
    print(f"   • 用户可以一天内提现5次")
    print(f"   • 超过5次时显示: '您今天已达到提现次数上限(5次)，请明天再来'")
    print(f"   • 配置会在用户下次打开提现页面时自动更新")

if __name__ == "__main__":
    print("=== 设置每日提现次数为5次 ===\n")
    
    success = set_daily_limit_to_5()
    
    if success:
        show_android_effect()
        print(f"\n🎯 配置完成！用户现在每天可以提现5次")
    else:
        print("❌ 设置失败，请检查数据库连接")
