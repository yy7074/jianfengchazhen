#!/bin/bash
# 自动同步防火墙脚本 - 一键部署

echo "========================================"
echo "🚀 安装自动同步防火墙脚本"
echo "========================================"

# 检查是否为root
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用root权限运行"
    echo "使用: sudo bash install_auto_sync.sh"
    exit 1
fi

# 1. 安装Python依赖
echo ""
echo "📦 安装Python依赖..."
pip3 install pymysql sqlalchemy conntrack-tools > /dev/null 2>&1 || pip install pymysql sqlalchemy conntrack-tools

# 2. 复制脚本到系统目录
echo ""
echo "📋 安装脚本文件..."
SCRIPT_PATH="/usr/local/bin/auto_sync_firewall.py"
cp auto_sync_firewall.py $SCRIPT_PATH
chmod +x $SCRIPT_PATH

echo "   ✅ 脚本已安装到: $SCRIPT_PATH"

# 3. 创建systemd服务（持续监控模式）
echo ""
echo "⚙️  创建systemd服务..."

cat > /etc/systemd/system/firewall-sync.service << 'EOF'
[Unit]
Description=Auto Sync Database IP Blacklist to Firewall
After=network.target mysql.service

[Service]
Type=simple
User=root
WorkingDirectory=/www/wwwroot/backend
ExecStart=/usr/bin/python3 /usr/local/bin/auto_sync_firewall.py --mode watch --interval 60
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "   ✅ systemd服务已创建"

# 4. 创建cron定时任务（备选方案）
echo ""
echo "⏰ 创建cron定时任务（每5分钟执行一次）..."

CRON_JOB="*/5 * * * * /usr/bin/python3 /usr/local/bin/auto_sync_firewall.py --mode once >> /var/log/firewall-sync.log 2>&1"

# 检查是否已存在
if ! crontab -l 2>/dev/null | grep -q "auto_sync_firewall.py"; then
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "   ✅ cron任务已添加"
else
    echo "   ℹ️  cron任务已存在"
fi

# 5. 执行一次同步
echo ""
echo "🔄 执行一次初始同步..."
python3 $SCRIPT_PATH --mode once

# 6. 显示使用说明
echo ""
echo "========================================"
echo "✅ 安装完成！"
echo "========================================"
echo ""
echo "📋 使用方式："
echo ""
echo "【方式1】启动后台服务（推荐）"
echo "  启动: systemctl start firewall-sync"
echo "  停止: systemctl stop firewall-sync"
echo "  状态: systemctl status firewall-sync"
echo "  开机自启: systemctl enable firewall-sync"
echo "  查看日志: journalctl -u firewall-sync -f"
echo ""
echo "【方式2】使用cron定时任务（已自动配置，每5分钟执行一次）"
echo "  查看任务: crontab -l"
echo "  查看日志: tail -f /var/log/firewall-sync.log"
echo ""
echo "【方式3】手动执行"
echo "  执行一次: python3 $SCRIPT_PATH --mode once"
echo "  持续监控: python3 $SCRIPT_PATH --mode watch --interval 60"
echo "  查看统计: python3 $SCRIPT_PATH --mode stats"
echo ""
echo "========================================"
echo ""
echo "💡 建议："
echo "  - 使用systemd服务（方式1）实现实时同步"
echo "  - 或者保留cron定时任务（方式2）每5分钟同步一次"
echo ""
echo "🎯 现在，每当你在管理后台封禁IP后，脚本会自动："
echo "  1. 从数据库读取新的黑名单IP"
echo "  2. 自动添加到UFW防火墙"
echo "  3. 自动添加到iptables规则"
echo "  4. 清除该IP的现有连接"
echo "  5. 保存规则（持久化）"
echo ""
echo "========================================"
