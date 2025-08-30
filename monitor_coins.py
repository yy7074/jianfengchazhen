#!/usr/bin/env python3
"""
实时监控用户金币变化
"""
import requests
import time
import json

def get_user_coins(user_id=9):
    """获取用户当前金币"""
    try:
        response = requests.get(f"http://8089.dachaonet.com/api/user/{user_id}/stats")
        if response.status_code == 200:
            data = response.json()
            return data['data']['current_coins']
        return None
    except:
        return None

def monitor_coins():
    """监控金币变化"""
    print("🔍 开始监控用户9的金币变化...")
    print("💡 在Android设备上观看广告，这里会实时显示金币变化")
    print("🛑 按 Ctrl+C 停止监控\n")
    
    last_coins = None
    
    try:
        while True:
            current_coins = get_user_coins()
            
            if current_coins is not None:
                if last_coins is None:
                    print(f"💰 初始金币: {current_coins}")
                elif current_coins != last_coins:
                    change = current_coins - last_coins
                    if change > 0:
                        print(f"🎉 金币增加! {last_coins} → {current_coins} (+{change})")
                    else:
                        print(f"📉 金币变化: {last_coins} → {current_coins} ({change:+})")
                
                last_coins = current_coins
            else:
                print("❌ 获取金币失败")
            
            time.sleep(2)  # 每2秒检查一次
            
    except KeyboardInterrupt:
        print(f"\n🛑 监控结束，最终金币: {last_coins}")

if __name__ == "__main__":
    monitor_coins()
