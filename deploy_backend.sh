#!/bin/bash

# 后端代码部署脚本
# 用于将本地修改的backend代码同步到服务器

echo "========================================="
echo "   游戏后端代码部署脚本"
echo "========================================="
echo ""

# 服务器配置
SERVER_IP="8.137.103.175"
SERVER_USER="root"
SERVER_PORT="22"
REMOTE_PATH="/www/wwwroot/backend"

# 本地路径
LOCAL_PATH="./backend"

# 检查本地backend目录是否存在
if [ ! -d "$LOCAL_PATH" ]; then
    echo "❌ 错误: 找不到 $LOCAL_PATH 目录"
    exit 1
fi

echo "📦 准备部署..."
echo "   本地路径: $LOCAL_PATH"
echo "   服务器: $SERVER_USER@$SERVER_IP:$SERVER_PORT"
echo "   远程路径: $REMOTE_PATH"
echo ""

# 询问确认
read -p "是否继续部署？(y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "❌ 取消部署"
    exit 0
fi

echo ""
echo "🚀 开始上传文件..."

# 使用rsync同步代码（排除某些目录）
rsync -avz --progress \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude 'logs/' \
    --exclude 'uploads/' \
    --exclude '.git' \
    --exclude 'venv/' \
    -e "ssh -p $SERVER_PORT" \
    $LOCAL_PATH/ $SERVER_USER@$SERVER_IP:$REMOTE_PATH/

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 文件上传成功！"
    echo ""
    echo "📝 接下来需要在服务器上重启后端服务："
    echo ""
    echo "   ssh $SERVER_USER@$SERVER_IP"
    echo "   sudo systemctl restart game-backend"
    echo "   sudo systemctl status game-backend"
    echo ""
    
    # 询问是否自动重启
    read -p "是否自动重启后端服务？(y/n): " restart_confirm
    if [ "$restart_confirm" = "y" ]; then
        echo ""
        echo "🔄 重启后端服务..."
        ssh -p $SERVER_PORT $SERVER_USER@$SERVER_IP "sudo systemctl restart game-backend && sudo systemctl status game-backend"
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ 后端服务重启成功！"
        else
            echo ""
            echo "❌ 后端服务重启失败，请手动检查"
        fi
    fi
else
    echo ""
    echo "❌ 文件上传失败"
    exit 1
fi

echo ""
echo "========================================="
echo "   部署完成"
echo "========================================="

