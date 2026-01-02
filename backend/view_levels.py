#!/usr/bin/env python3
"""
查看当前等级配置
"""

from database import get_db
from models import UserLevelConfig
from sqlalchemy import asc

def view_levels():
    """查看并显示所有等级配置"""
    db = next(get_db())

    try:
        levels = db.query(UserLevelConfig).order_by(asc(UserLevelConfig.level)).all()

        if not levels:
            print("⚠️  未找到等级配置")
            return

        print(f"\n📊 当前等级系统: 共 {len(levels)} 级\n")
        print("="*100)
        print(f"{'等级':<4} {'名称':<12} {'经验范围':<25} {'广告倍数':<10} {'游戏倍数':<10} {'状态':<6}")
        print("="*100)

        for level in levels:
            exp_range = f"{level.min_experience:,}"
            if level.max_experience:
                exp_range += f" - {level.max_experience:,}"
            else:
                exp_range += " - 无上限"

            status = "✅ 启用" if level.is_active else "❌ 禁用"

            print(f"{level.level:<4} {level.level_name:<12} {exp_range:<25} "
                  f"{float(level.ad_coin_multiplier):<10.2f} "
                  f"{float(level.game_coin_multiplier):<10.2f} {status:<6}")

        print("="*100)

        # 统计信息
        print(f"\n📈 统计信息:")
        print(f"  - 最低等级: {levels[0].level} ({levels[0].level_name})")
        print(f"  - 最高等级: {levels[-1].level} ({levels[-1].level_name})")
        print(f"  - 启用等级: {sum(1 for l in levels if l.is_active)}")
        print(f"  - 禁用等级: {sum(1 for l in levels if not l.is_active)}")

        # 倍数信息
        ad_multipliers = [float(l.ad_coin_multiplier) for l in levels if l.is_active]
        game_multipliers = [float(l.game_coin_multiplier) for l in levels if l.is_active]

        print(f"\n💰 奖励倍数范围:")
        print(f"  - 广告金币: {min(ad_multipliers):.2f}x - {max(ad_multipliers):.2f}x")
        print(f"  - 游戏金币: {min(game_multipliers):.2f}x - {max(game_multipliers):.2f}x")

        # 经验值信息
        max_exp_level = [l for l in levels if l.max_experience is not None]
        if max_exp_level:
            highest_exp = max(l.max_experience for l in max_exp_level)
            print(f"\n📊 经验值范围:")
            print(f"  - 到达最高有限等级需要: {highest_exp:,} 经验")
            print(f"  - 最高等级 ({levels[-1].level}级) 起始经验: {levels[-1].min_experience:,}")

    except Exception as e:
        print(f"❌ 查询失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("="*100)
    print("等级系统查看工具")
    print("="*100)
    view_levels()
    print()
