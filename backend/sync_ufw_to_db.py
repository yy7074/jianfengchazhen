#!/usr/bin/env python3
"""
从UFW防火墙同步被封IP到数据库
这样后台管理界面就能显示所有被封的IP
"""
import subprocess
import re
from datetime import datetime
from database import get_db
from models import IPBlacklist


def get_ufw_blocked_ips():
    """从UFW获取所有被DENY的IP"""
    try:
        result = subprocess.run(
            ['ufw', 'status', 'numbered'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"❌ 无法读取UFW状态: {result.stderr}")
            return []
        
        blocked_ips = []
        lines = result.stdout.split('\n')
        
        for line in lines:
            # 匹配类似: [1] DENY IN 192.168.1.1
            match = re.search(r'DENY.*?(\d+\.\d+\.\d+\.\d+)', line)
            if match:
                ip = match.group(1)
                blocked_ips.append(ip)
        
        return list(set(blocked_ips))  # 去重
        
    except FileNotFoundError:
        print("❌ UFW未安装或未在PATH中")
        return []
    except Exception as e:
        print(f"❌ 读取UFW失败: {e}")
        return []


def sync_to_database():
    """同步UFW中的IP到数据库"""
    db = next(get_db())
    try:
        # 获取UFW中被封的IP
        ufw_ips = get_ufw_blocked_ips()
        
        if not ufw_ips:
            print("ℹ️  UFW中没有被封的IP")
            return 0
        
        print(f"📋 从UFW读取到 {len(ufw_ips)} 个被封IP")
        
        # 获取数据库中已有的IP
        existing_ips = {ip.ip_address for ip in db.query(IPBlacklist).all()}
        
        # 找出数据库中没有的IP
        new_ips = set(ufw_ips) - existing_ips
        
        if not new_ips:
            print("✅ 所有IP已在数据库中，无需同步")
            return 0
        
        print(f"📝 发现 {len(new_ips)} 个新IP需要同步到数据库")
        
        # 将新IP添加到数据库
        synced_count = 0
        for ip in new_ips:
            blacklist_entry = IPBlacklist(
                ip_address=ip,
                reason="从UFW同步的封禁IP",
                blocked_time=datetime.now(),
                is_active=1
            )
            db.add(blacklist_entry)
            synced_count += 1
            print(f"  ✓ {ip}")
        
        db.commit()
        print(f"\n✅ 成功同步 {synced_count} 个IP到数据库")
        return synced_count
        
    except Exception as e:
        print(f"❌ 同步失败: {e}")
        db.rollback()
        return 0
    finally:
        db.close()


def main():
    print("=" * 50)
    print("🔄 UFW IP同步工具")
    print("=" * 50)
    print()
    
    synced = sync_to_database()
    
    print()
    print("=" * 50)
    if synced > 0:
        print(f"✅ 完成！同步了 {synced} 个IP")
        print("💡 现在刷新后台管理页面即可看到所有被封IP")
    else:
        print("✅ 无需同步")
    print("=" * 50)


if __name__ == "__main__":
    main()
