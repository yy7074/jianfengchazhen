#!/bin/bash

echo "🚀 开始构建见缝插针游戏..."

# 检查Gradle Wrapper
if [ ! -f "./gradlew" ]; then
    echo "❌ 找不到gradlew，请检查项目结构"
    exit 1
fi

# 给gradlew执行权限
chmod +x ./gradlew

echo "🧹 清理项目..."
./gradlew clean

echo "🔨 构建Debug版本..."
./gradlew assembleDebug

if [ $? -eq 0 ]; then
    echo "✅ 构建成功！"
    echo "📱 APK文件位置: app/build/outputs/apk/debug/app-debug.apk"
    
    # 检查是否连接了设备
    if command -v adb &> /dev/null; then
        devices=$(adb devices | grep -v "List" | grep "device" | wc -l)
        if [ $devices -gt 0 ]; then
            echo "📲 检测到Android设备，是否安装APK？(y/n)"
            read -r install_choice
            if [ "$install_choice" = "y" ] || [ "$install_choice" = "Y" ]; then
                echo "📲 安装APK到设备..."
                ./gradlew installDebug
                if [ $? -eq 0 ]; then
                    echo "✅ 安装成功！"
                else
                    echo "❌ 安装失败"
                fi
            fi
        else
            echo "ℹ️ 未检测到Android设备"
        fi
    fi
else
    echo "❌ 构建失败，请检查错误信息"
    exit 1
fi

echo "🎯 构建完成！" 