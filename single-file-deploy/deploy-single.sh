#!/bin/bash

# 单文件Docker部署脚本

echo "🚀 穆桥销售测验系统 - 单文件Docker部署"
echo "============================================"

# 检查文件是否存在
if [ ! -f "exam-standalone.html" ]; then
    echo "❌ 找不到 exam-standalone.html 文件"
    exit 1
fi

# 构建并启动
echo "📦 构建Docker镜像..."
docker-compose -f docker-compose-single.yml build

echo "🚀 启动服务..."
docker-compose -f docker-compose-single.yml up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 检查服务状态
echo "📊 检查服务状态..."
docker-compose -f docker-compose-single.yml ps

echo ""
echo "✅ 部署完成！"
echo ""
echo "🌐 访问地址："
echo "  管理入口: http://localhost/"
echo "  销售链接: http://localhost/?mode=sales"
echo "  或者使用: http://localhost/sales (自动跳转)"
echo ""
echo "🔧 管理命令："
echo "  查看日志: docker-compose -f docker-compose-single.yml logs -f"
echo "  停止服务: docker-compose -f docker-compose-single.yml down"
echo "  重启服务: docker-compose -f docker-compose-single.yml restart"
echo ""
echo "📝 注意事项："
echo "  - 考试记录保存在用户浏览器中"
echo "  - 如需数据同步，请配置外部API服务器"
echo ""