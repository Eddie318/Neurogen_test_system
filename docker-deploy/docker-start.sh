#!/bin/bash

# 穆桥销售测验系统 - Docker部署启动脚本

echo "=== 穆桥销售测验系统 Docker部署 ==="
echo "正在启动服务..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 停止并删除现有容器
echo "🔄 清理现有容器..."
docker-compose down --remove-orphans

# 构建并启动服务
echo "🚀 构建并启动服务..."
docker-compose up -d --build

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "📊 检查服务状态..."
docker-compose ps

# 显示访问信息
echo ""
echo "✅ 部署完成！"
echo ""
echo "🌐 访问地址："
echo "  考试系统: http://localhost/exam.html"
echo "  销售链接: http://localhost/exam.html?mode=sales"
echo "  管理后台: http://localhost/admin.html"
echo ""
echo "🔧 管理命令："
echo "  查看日志: docker-compose logs -f"
echo "  停止服务: docker-compose down"
echo "  重启服务: docker-compose restart"
echo ""
echo "📁 数据存储位置: ./data/"
echo ""