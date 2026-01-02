#!/usr/bin/env python3
"""
等级系统升级脚本
将现有的7级系统升级到40级系统
"""

from database import get_db, engine
from models import UserLevelConfig
from services.level_service import LevelService
from sqlalchemy.orm import Session

def upgrade_levels():
    """升级等级系统到40级"""
    print("🔄 开始升级等级系统...")

    db = next(get_db())

    try:
        # 1. 检查当前等级数量
        current_level_count = db.query(UserLevelConfig).count()
        print(f"📊 当前等级数量: {current_level_count}")

        if current_level_count == 0:
            print("⚠️  未发现等级配置，将直接初始化40级系统")
            LevelService.init_default_levels(db)
            return

        # 2. 清除旧的等级配置
        print("🗑️  清除旧的等级配置...")
        db.query(UserLevelConfig).delete()
        db.commit()
        print(f"✅ 已清除 {current_level_count} 个旧等级配置")

        # 3. 初始化新的40级系统
        print("📝 初始化40级等级系统...")
        LevelService.init_default_levels(db)

        # 4. 验证新系统
        new_level_count = db.query(UserLevelConfig).count()
        print(f"✅ 成功创建 {new_level_count} 个等级配置")

        print("\n🎉 等级系统升级完成！")
        print("\n等级系统概览:")
        print("  1-10级:  新手 → 黄金I (广告1-6倍)")
        print("  11-20级: 黄金II → 大师II (广告7-18倍)")
        print("  21-30级: 大师III → 终极王者 (广告20-40倍)")
        print("\n最高等级奖励 (30级 - 终极王者):")
        print("  广告金币: 40倍 (+3900%)")
        print("  游戏金币: 20倍 (+1900%)")

    except Exception as e:
        print(f"❌ 升级失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("="*60)
    print("等级系统升级工具 - 升级到30级系统")
    print("="*60)
    print()

    confirm = input("确认要升级等级系统吗？这将清除所有现有等级配置。(yes/no): ")

    if confirm.lower() in ['yes', 'y']:
        upgrade_levels()
    else:
        print("❌ 取消升级")
