#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动同步数据库黑名单IP到防火墙
- 从数据库读取活跃的黑名单IP
- 自动添加到UFW和iptables防火墙
- 可以作为定时任务运行，或持续监控模式
"""

import os
import sys
import time
import subprocess
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'game_db'
}

# 防火墙封禁记录文件（避免重复封禁）
BANNED_IPS_FILE = '/tmp/firewall_banned_ips.txt'


class FirewallSyncManager:
    """防火墙同步管理器"""

    def __init__(self):
        # 创建数据库连接
        db_url = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        self.engine = create_engine(db_url, pool_pre_ping=True)
        self.Session = sessionmaker(bind=self.engine)

        # 加载已封禁的IP列表
        self.banned_ips = self._load_banned_ips()

    def _load_banned_ips(self):
        """加载已封禁的IP列表"""
        if os.path.exists(BANNED_IPS_FILE):
            with open(BANNED_IPS_FILE, 'r') as f:
                return set(line.strip() for line in f if line.strip())
        return set()

    def _save_banned_ip(self, ip):
        """保存已封禁的IP"""
        self.banned_ips.add(ip)
        with open(BANNED_IPS_FILE, 'a') as f:
            f.write(f"{ip}\n")

    def _run_command(self, cmd, silent=False):
        """执行shell命令"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            if not silent and result.returncode != 0:
                print(f"⚠️  命令执行失败: {cmd}")
                print(f"错误: {result.stderr}")
            return result.returncode == 0
        except Exception as e:
            if not silent:
                print(f"❌ 命令执行异常: {cmd}, 错误: {e}")
            return False

    def get_blocked_ips_from_db(self):
        """从数据库获取所有活跃的黑名单IP"""
        session = self.Session()
        try:
            query = text("""
                SELECT ip_address
                FROM ip_blacklist
                WHERE is_active = 1
                ORDER BY blocked_time DESC
            """)
            result = session.execute(query)
            ips = [row[0] for row in result]
            return ips
        except Exception as e:
            print(f"❌ 查询数据库失败: {e}")
            return []
        finally:
            session.close()

    def convert_to_subnet(self, ip):
        """
        将IP地址转换为子网段（/24）
        例如: 112.82.180.220 -> 112.82.180.0/24
        """
        parts = ip.split('.')
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
        return ip

    def ban_ip_in_firewall(self, ip):
        """在防火墙中封禁IP"""
        # 转换为子网段
        subnet = self.convert_to_subnet(ip)
        return self._ban_subnet(subnet)

    def _ban_subnet(self, subnet):
        """封禁一个子网段"""
        # 检查是否已经封禁过
        if subnet in self.banned_ips:
            return True

        print(f"🔒 正在封禁: {subnet}")

        # 1. 添加到UFW
        ufw_cmd = f"ufw insert 1 deny from {subnet}"
        ufw_success = self._run_command(ufw_cmd, silent=True)

        # 2. 添加到iptables (ufw-before-input链，最高优先级)
        iptables_cmd = f"iptables -I ufw-before-input 1 -s {subnet} -j DROP"
        iptables_success = self._run_command(iptables_cmd, silent=True)

        # 3. 清除该IP的现有连接
        conntrack_cmd = f"conntrack -D -s {subnet} 2>/dev/null"
        self._run_command(conntrack_cmd, silent=True)

        if ufw_success and iptables_success:
            print(f"   ✅ 成功封禁: {subnet}")
            self._save_banned_ip(subnet)
            return True
        else:
            print(f"   ⚠️  部分失败: {subnet}")
            return False

    def save_iptables_rules(self):
        """保存iptables规则（持久化）"""
        print("💾 保存防火墙规则...")
        cmd = "iptables-save > /etc/iptables/rules.v4"
        if self._run_command(cmd):
            print("   ✅ 规则已保存到: /etc/iptables/rules.v4")
            return True
        else:
            print("   ⚠️  保存规则失败")
            return False

    def sync_once(self):
        """执行一次同步"""
        print("=" * 60)
        print(f"🔄 开始同步防火墙规则 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        # 1. 从数据库获取黑名单IP
        db_ips = self.get_blocked_ips_from_db()
        if not db_ips:
            print("ℹ️  数据库中没有黑名单IP")
            return

        print(f"📊 数据库中共有 {len(db_ips)} 个黑名单IP")

        # 2. 转换为子网段并去重
        subnets = set()
        for ip in db_ips:
            subnet = self.convert_to_subnet(ip)
            subnets.add(subnet)

        print(f"📊 转换为 {len(subnets)} 个子网段")

        # 3. 封禁新的IP段
        new_bans = 0
        for subnet in sorted(subnets):
            if subnet not in self.banned_ips:
                # 直接封禁子网段
                if self._ban_subnet(subnet):
                    new_bans += 1

        if new_bans > 0:
            print(f"\n🎉 本次新增封禁: {new_bans} 个IP段")
            # 保存规则
            self.save_iptables_rules()
        else:
            print(f"\nℹ️  没有新的IP需要封禁")

        print(f"📊 当前总共封禁: {len(self.banned_ips)} 个IP段")
        print("=" * 60)

    def watch_mode(self, interval=60):
        """持续监控模式"""
        print("=" * 60)
        print("🔍 启动持续监控模式")
        print(f"⏱️  检查间隔: {interval} 秒")
        print("按 Ctrl+C 停止监控")
        print("=" * 60)
        print()

        try:
            while True:
                self.sync_once()
                print(f"\n⏳ 等待 {interval} 秒后进行下一次检查...\n")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\n👋 监控已停止")

    def show_stats(self):
        """显示统计信息"""
        print("=" * 60)
        print("📊 防火墙封禁统计")
        print("=" * 60)

        # 数据库黑名单数量
        db_ips = self.get_blocked_ips_from_db()
        print(f"数据库黑名单IP数量: {len(db_ips)}")

        # 已封禁的IP段数量
        print(f"防火墙已封禁IP段: {len(self.banned_ips)}")

        # UFW规则数量
        result = subprocess.run(
            "ufw status numbered | grep -c 'DENY' || echo 0",
            shell=True,
            capture_output=True,
            text=True
        )
        ufw_count = result.stdout.strip()
        print(f"UFW规则数量: {ufw_count}")

        # iptables拦截统计
        result = subprocess.run(
            "iptables -L ufw-before-input -n -v | grep '112.82.180.0/24' | awk '{print $1}' || echo 0",
            shell=True,
            capture_output=True,
            text=True
        )
        packets = result.stdout.strip()
        print(f"已拦截数据包: {packets}")

        print("=" * 60)

        # 显示最近10个封禁的IP段
        if self.banned_ips:
            print("\n最近封禁的IP段（前10个）:")
            for ip in list(self.banned_ips)[-10:]:
                print(f"  - {ip}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='自动同步数据库黑名单IP到防火墙')
    parser.add_argument(
        '--mode',
        choices=['once', 'watch', 'stats'],
        default='once',
        help='运行模式: once=执行一次, watch=持续监控, stats=显示统计'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='监控模式下的检查间隔（秒），默认60秒'
    )

    args = parser.parse_args()

    # 检查是否为root权限
    if os.geteuid() != 0:
        print("❌ 此脚本需要root权限运行")
        print("请使用: sudo python3 auto_sync_firewall.py")
        sys.exit(1)

    # 创建管理器
    manager = FirewallSyncManager()

    # 根据模式执行
    if args.mode == 'once':
        manager.sync_once()
    elif args.mode == 'watch':
        manager.watch_mode(interval=args.interval)
    elif args.mode == 'stats':
        manager.show_stats()


if __name__ == '__main__':
    main()
