#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户等级系统逻辑演示
"""

def get_user_level_by_experience(experience: int) -> dict:
    """根据经验值计算用户等级"""
    level_configs = [
        {"level": 1, "name": "新手", "min_exp": 0, "max_exp": 999, "ad_mult": 1.0, "game_mult": 1.0},
        {"level": 2, "name": "青铜", "min_exp": 1000, "max_exp": 2999, "ad_mult": 1.2, "game_mult": 1.1},
        {"level": 3, "name": "白银", "min_exp": 3000, "max_exp": 5999, "ad_mult": 1.5, "game_mult": 1.2},
        {"level": 4, "name": "黄金", "min_exp": 6000, "max_exp": 9999, "ad_mult": 1.8, "game_mult": 1.3},
        {"level": 5, "name": "铂金", "min_exp": 10000, "max_exp": 19999, "ad_mult": 2.0, "game_mult": 1.5},
        {"level": 6, "name": "钻石", "min_exp": 20000, "max_exp": 39999, "ad_mult": 2.5, "game_mult": 1.8},
        {"level": 7, "name": "大师", "min_exp": 40000, "max_exp": None, "ad_mult": 3.0, "game_mult": 2.0},
    ]
    
    for config in level_configs:
        if experience >= config["min_exp"]:
            if config["max_exp"] is None or experience <= config["max_exp"]:
                return config
    
    return level_configs[0]  # 默认返回新手等级

def calculate_ad_reward(base_reward: float, user_level: int) -> float:
    """计算广告奖励"""
    experience_map = {1: 0, 2: 1500, 3: 4000, 4: 7500, 5: 15000, 6: 25000, 7: 50000}
    exp = experience_map.get(user_level, 0)
    level_config = get_user_level_by_experience(exp)
    return round(base_reward * level_config["ad_mult"], 2)

def demo_level_progression():
    """演示等级升级过程"""
    print("🏆 用户等级系统设定逻辑")
    print("=" * 80)
    
    print("\n📋 等级配置表:")
    print("-" * 80)
    print(f"{'等级':<4} {'名称':<6} {'经验范围':<15} {'广告倍数':<8} {'游戏倍数':<8} {'说明':<20}")
    print("-" * 80)
    
    test_experiences = [0, 1500, 4000, 7500, 15000, 25000, 50000]
    for exp in test_experiences:
        config = get_user_level_by_experience(exp)
        max_exp = config["max_exp"] if config["max_exp"] else "∞"
        exp_range = f"{config['min_exp']}-{max_exp}"
        
        print(f"{config['level']:<4} {config['name']:<6} {exp_range:<15} {config['ad_mult']:<8.1f} {config['game_mult']:<8.1f} 广告金币x{config['ad_mult']}")
    
    print("\n🎯 等级升级机制:")
    print("• 用户通过游戏和活动获得经验值")
    print("• 系统自动根据经验值计算用户等级")
    print("• 等级越高，观看广告和游戏获得的金币越多")
    print("• APP端用户看不到具体等级，但享受等级加成")
    
    print("\n💰 广告奖励计算示例 (基础奖励: 10金币):")
    print("-" * 50)
    base_reward = 10
    
    for level in range(1, 8):
        actual_reward = calculate_ad_reward(base_reward, level)
        config = get_user_level_by_experience({1: 0, 2: 1500, 3: 4000, 4: 7500, 5: 15000, 6: 25000, 7: 50000}[level])
        bonus = actual_reward - base_reward
        
        print(f"等级{level} ({config['name']}): {base_reward}金币 × {config['ad_mult']} = {actual_reward}金币 (+{bonus}金币)")
    
    print("\n🎮 实际应用场景:")
    print("1. 用户观看广告 → 获得基础金币 × 等级倍数")
    print("2. 用户完成游戏 → 获得基础金币 × 等级倍数") 
    print("3. 系统定期检查经验值 → 自动升级用户等级")
    print("4. 后台管理员可以查看用户等级分布")
    
    print("\n⚙️  管理员设置:")
    print("• 可以调整每个等级的经验值要求")
    print("• 可以修改广告和游戏金币倍数")
    print("• 可以查看用户等级分布统计")
    print("• 可以启用/禁用特定等级")

if __name__ == "__main__":
    demo_level_progression()
