#!/bin/bash

# 穆桥销售测验系统 - 移动端快速启动

echo "=================================================="
echo "      穆桥销售测验系统 - 移动端启动"
echo "=================================================="

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

# 获取本机IP
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)

if [ -z "$LOCAL_IP" ]; then
    echo "❌ 无法获取本机IP地址"
    echo "请确保电脑已连接到WiFi网络"
    exit 1
fi

# 停止现有服务
pkill -f "python.*8000" || true

# 启动服务器
echo "🚀 启动移动端友好的Web服务器..."
python3 -m http.server 8000 --bind 0.0.0.0 &
HTTP_PID=$!

sleep 3

echo ""
echo "✅ 启动成功！"
echo ""
echo "📱 手机访问地址："
echo "┌─────────────────────────────────────────────────────────────┐"
echo "│  销售考试：http://${LOCAL_IP}:8000/exam.html?mode=sales    │"
echo "│  管理后台：http://${LOCAL_IP}:8000/admin.html              │"
echo "└─────────────────────────────────────────────────────────────┘"
echo ""
echo "📋 使用步骤："
echo "1️⃣  确保手机和电脑在同一WiFi网络"
echo "2️⃣  在手机浏览器打开上面的销售考试地址"
echo "3️⃣  建议将地址添加到手机主屏幕"
echo ""
echo "💡 添加到主屏幕方法："
echo "   iOS: 浏览器菜单 → 添加到主屏幕"
echo "   Android: 浏览器菜单 → 添加快捷方式"
echo ""
echo "🛑 停止服务：按 Ctrl+C"
echo ""

# 等待用户中断
trap "echo ''; echo '正在停止服务...'; kill $HTTP_PID 2>/dev/null; exit 0" INT

# 保持脚本运行
wait