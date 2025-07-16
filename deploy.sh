#!/bin/bash

# 医学考试系统 - 自动部署脚本

echo "🚀 医学考试系统 - Vercel自动部署"
echo "=================================="

# 检查是否安装了Vercel CLI
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI未安装，正在安装..."
    npm install -g vercel
    echo "✅ Vercel CLI安装完成"
fi

# 检查是否已登录
echo "🔐 检查Vercel登录状态..."
if ! vercel whoami &> /dev/null; then
    echo "⚠️  未登录Vercel，请先登录："
    echo "   vercel login"
    echo ""
    echo "登录后重新运行此脚本"
    exit 1
fi

echo "✅ Vercel登录状态正常"

# 部署代理服务器
echo ""
echo "📡 部署代理服务器..."
cd qwen-proxy
echo "部署目录: $(pwd)"

# 设置项目名称
PROXY_PROJECT_NAME="neurogen-qwen-proxy"

vercel --prod --name $PROXY_PROJECT_NAME --yes
PROXY_URL=$(vercel --prod --name $PROXY_PROJECT_NAME 2>/dev/null | grep -o 'https://[^[:space:]]*' | tail -1)

if [ -z "$PROXY_URL" ]; then
    echo "⚠️  无法获取代理服务器URL，请手动检查部署状态"
    PROXY_URL="https://your-proxy.vercel.app"
fi

echo "✅ 代理服务器部署完成: $PROXY_URL"

# 部署主应用
echo ""
echo "🎯 部署主应用..."
cd ../neurogen-exam-system
echo "部署目录: $(pwd)"

# 设置项目名称
MAIN_PROJECT_NAME="neurogen-exam-system"

vercel --prod --name $MAIN_PROJECT_NAME --yes
MAIN_URL=$(vercel --prod --name $MAIN_PROJECT_NAME 2>/dev/null | grep -o 'https://[^[:space:]]*' | tail -1)

if [ -z "$MAIN_URL" ]; then
    echo "⚠️  无法获取主应用URL，请手动检查部署状态"
    MAIN_URL="https://your-app.vercel.app"
fi

echo "✅ 主应用部署完成: $MAIN_URL"

# 显示部署总结
echo ""
echo "🎉 部署完成！"
echo "==============="
echo ""
echo "📱 应用地址:"
echo "   主页: $MAIN_URL"
echo "   考试: $MAIN_URL/exam"
echo "   管理: $MAIN_URL/admin"
echo ""
echo "📡 代理服务器:"
echo "   地址: $PROXY_URL/api/proxy"
echo ""
echo "🔧 下一步配置:"
echo "1. 访问 $MAIN_URL/admin 进入后台管理"
echo "2. 配置API服务："
echo "   - 选择'代理服务器'"
echo "   - API地址填入: $PROXY_URL/api/proxy"
echo "   - 输入你的通义千问API Key"
echo "3. 导入Excel题库文件"
echo "4. 开始使用考试系统"
echo ""
echo "📖 详细文档: ./DEPLOYMENT.md"
echo ""
echo "✨ 部署成功！享受你的智能考试系统吧！"