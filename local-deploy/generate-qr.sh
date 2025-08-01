#!/bin/bash

# 生成移动端访问二维码

# 获取本机IP
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)

if [ -z "$LOCAL_IP" ]; then
    echo "❌ 无法获取本机IP地址"
    exit 1
fi

SALES_URL="http://${LOCAL_IP}:8000/exam.html?mode=sales"
ADMIN_URL="http://${LOCAL_IP}:8000/admin.html"

echo "📱 移动端访问地址："
echo ""
echo "🎯 销售考试链接："
echo "$SALES_URL"
echo ""
echo "⚙️ 管理后台链接："
echo "$ADMIN_URL"
echo ""

# 检查是否安装了qrencode
if command -v qrencode &> /dev/null; then
    echo "📱 销售考试二维码："
    qrencode -t ansiutf8 "$SALES_URL"
    echo ""
    echo "⚙️ 管理后台二维码："
    qrencode -t ansiutf8 "$ADMIN_URL"
else
    echo "💡 安装qrencode可生成二维码："
    echo "   macOS: brew install qrencode"
    echo "   Ubuntu: sudo apt install qrencode"
fi

echo ""
echo "📋 使用说明："
echo "1. 确保手机和电脑在同一WiFi"
echo "2. 用手机摄像头扫描二维码"
echo "3. 或手动输入上面的网址"