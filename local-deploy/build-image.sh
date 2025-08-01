#!/bin/bash

# 穆桥销售测验系统 - Docker镜像构建脚本

set -e

echo "=================================================="
echo "      穆桥销售测验系统 - 构建Docker镜像"
echo "=================================================="
echo ""

# 配置变量
IMAGE_NAME="neurogen-exam-system"
IMAGE_TAG="latest"
FULL_IMAGE_NAME="$IMAGE_NAME:$IMAGE_TAG"

# 显示系统信息
echo "🔍 系统信息："
echo "   Docker版本: $(docker --version)"
echo "   当前目录: $(pwd)"
echo "   镜像名称: $FULL_IMAGE_NAME"
echo ""

# 清理旧镜像（可选）
read -p "是否清理旧镜像？(y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧹 清理旧镜像..."
    docker rmi $FULL_IMAGE_NAME 2>/dev/null || true
    docker system prune -f
fi

# 构建镜像
echo "🏗️  开始构建Docker镜像..."
echo "   这可能需要几分钟时间..."
echo ""

docker build -t $FULL_IMAGE_NAME . --no-cache

# 验证镜像
echo ""
echo "✅ 镜像构建完成！"
echo ""
echo "📊 镜像信息："
docker images | grep $IMAGE_NAME

# 测试运行
echo ""
read -p "是否测试运行镜像？(y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧪 启动测试容器..."
    
    # 停止可能存在的测试容器
    docker stop neurogen-test 2>/dev/null || true
    docker rm neurogen-test 2>/dev/null || true
    
    # 启动测试容器
    docker run -d --name neurogen-test -p 8888:80 $FULL_IMAGE_NAME
    
    echo "⏳ 等待服务启动..."
    sleep 5
    
    # 检查服务状态
    if curl -s http://localhost:8888/health > /dev/null; then
        echo "✅ 测试成功！服务正常运行"
        echo "🌐 测试地址: http://localhost:8888/exam.html"
        echo ""
        echo "⚠️  记得停止测试容器:"
        echo "   docker stop neurogen-test"
        echo "   docker rm neurogen-test"
    else
        echo "❌ 测试失败，检查日志:"
        docker logs neurogen-test
    fi
fi

echo ""
echo "=================================================="
echo "           🎉 构建完成！"
echo "=================================================="
echo ""
echo "📦 接下来你可以："
echo "   1. 使用 docker-compose up -d 启动完整服务"
echo "   2. 将镜像推送到Docker Hub:"
echo "      docker tag $FULL_IMAGE_NAME yourusername/neurogen-exam-system"
echo "      docker push yourusername/neurogen-exam-system"
echo "   3. 将整个目录打包发给开发团队:"
echo "      tar -czf neurogen-exam-system.tar.gz ."
echo ""
echo "🚀 部署到服务器时运行: bash deploy.sh"
echo "=================================================="