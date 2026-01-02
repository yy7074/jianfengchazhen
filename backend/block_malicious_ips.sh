#!/bin/bash
# 从数据库读取黑名单IP并添加到iptables防火墙

echo "========================================"
echo "开始封禁恶意IP - 系统层面防火墙"
echo "========================================"

# 数据库连接信息
DB_USER="root"
DB_PASS="SJKdjksal652"
DB_NAME="game_db"

# 从数据库读取所有活跃的黑名单IP
echo "正在从数据库读取黑名单IP..."
mysql -u $DB_USER -p$DB_PASS -N -e "USE $DB_NAME; SELECT ip_address FROM ip_blacklist WHERE is_active=1;" | while read ip; do
  # 检查规则是否已存在
  if ! iptables -C INPUT -s $ip -j DROP 2>/dev/null; then
    # 添加DROP规则
    iptables -A INPUT -s $ip -j DROP
    echo "✅ 已封禁: $ip"
  else
    echo "ℹ️  已存在: $ip"
  fi
done

# 统计封禁数量
BLOCKED_COUNT=$(iptables -L INPUT -n | grep DROP | wc -l)
echo ""
echo "========================================"
echo "✅ 完成！当前防火墙封禁IP数量: $BLOCKED_COUNT"
echo "========================================"

# 保存规则（持久化）
echo "正在保存iptables规则..."

# 检查系统类型并保存规则
if command -v iptables-save > /dev/null; then
    # 创建保存目录
    mkdir -p /etc/iptables

    # 保存规则
    iptables-save > /etc/iptables/rules.v4
    echo "✅ 规则已保存到: /etc/iptables/rules.v4"

    # 同时保存一份备份
    BACKUP_FILE="/root/iptables_backup_$(date +%Y%m%d_%H%M%S).rules"
    iptables-save > $BACKUP_FILE
    echo "✅ 备份已保存到: $BACKUP_FILE"
else
    echo "⚠️  iptables-save命令不可用"
fi

echo ""
echo "========================================"
echo "查看当前封禁的IP（前20个）:"
echo "========================================"
iptables -L INPUT -n | grep DROP | head -20

echo ""
echo "========================================"
echo "封禁统计:"
echo "========================================"
echo "总封禁IP数: $(iptables -L INPUT -n | grep DROP | wc -l)"
echo ""
echo "如需解除某个IP的封禁，使用:"
echo "iptables -D INPUT -s <IP地址> -j DROP"
echo "iptables-save > /etc/iptables/rules.v4"
