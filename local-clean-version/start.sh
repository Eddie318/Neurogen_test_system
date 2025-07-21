#!/bin/bash

# 穆桥销售测验系统 - 一键启动脚本

echo "=================================================="
echo "      穆桥销售测验系统 - Docker 一键部署"
echo "=================================================="
echo ""

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    echo "访问 https://docs.docker.com/get-docker/ 下载安装"
    exit 1
fi

# 检查docker-compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose 未安装，请先安装 docker-compose"
    echo "访问 https://docs.docker.com/compose/install/ 下载安装"
    exit 1
fi

echo "✅ Docker 环境检查通过"
echo ""

# 检查端口占用
if netstat -tulpn 2>/dev/null | grep :80 > /dev/null; then
    echo "⚠️  警告：端口 80 已被占用"
    read -p "是否要使用 8080 端口？(y/n): " use_8080
    if [ "$use_8080" = "y" ] || [ "$use_8080" = "Y" ]; then
        sed -i.bak 's/"80:80"/"8080:80"/g' docker-compose.yml
        echo "✅ 已配置使用 8080 端口"
        PORT=8080
    else
        echo "❌ 请先停止占用 80 端口的服务，然后重新运行此脚本"
        exit 1
    fi
else
    PORT=80
fi

echo ""
echo "🚀 开始构建和启动服务..."
echo ""

# 停止并移除旧容器（如果存在）
docker-compose down 2>/dev/null

# 构建并启动服务
if docker-compose up -d --build; then
    echo ""
    echo "=================================================="
    echo "           🎉 部署成功！"
    echo "=================================================="
    echo ""
    echo "📋 访问地址："
    echo "   后台管理：  http://localhost:$PORT/admin.html"
    echo "   考试系统：  http://localhost:$PORT/exam.html"
    echo "   销售链接：  http://localhost:$PORT/exam.html?mode=sales"
    echo ""
    echo "🔧 管理命令："
    echo "   查看状态：  docker-compose ps"
    echo "   查看日志：  docker-compose logs -f"
    echo "   停止服务：  docker-compose down"
    echo "   重启服务：  docker-compose restart"
    echo ""
    echo "📱 移动端访问："
    echo "   将 localhost 替换为服务器IP地址即可在手机上访问"
    echo ""
    echo "⚙️  下一步："
    echo "   1. 访问后台管理配置通义千问API"
    echo "   2. 导入题库或使用内置的54道题目"
    echo "   3. 将销售链接分享给销售人员"
    echo ""
    echo "=================================================="
else
    echo ""
    echo "❌ 部署失败，请检查错误信息"
    echo ""
    echo "🔍 故障排除："
    echo "   1. 检查 Docker 服务是否运行：systemctl status docker"
    echo "   2. 检查端口占用：netstat -tulpn | grep :$PORT"
    echo "   3. 查看详细日志：docker-compose logs"
    echo ""
fi