#!/bin/bash

# 穆桥销售测验系统 - Python后端环境设置脚本

echo "🐍 穆桥销售测验系统 - Python后端环境设置"
echo "================================================"

# 检查Python版本
python_version=$(python3 --version 2>&1)
echo "✅ Python版本: $python_version"

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建Python虚拟环境..."
    python3 -m venv venv
    echo "✅ 虚拟环境创建完成"
else
    echo "✅ 虚拟环境已存在"
fi

# 激活虚拟环境并安装依赖
echo "🔄 激活虚拟环境并安装依赖..."
source venv/bin/activate

# 升级pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt

echo ""
echo "✅ 环境设置完成！"
echo ""
echo "📋 下一步操作："
echo "1. 激活虚拟环境: source venv/bin/activate"
echo "2. 配置API密钥: cp .env.example .env && nano .env"
echo "3. 迁移数据: python migrate_data.py"
echo "4. 启动服务: python start.py"
echo ""
echo "💡 提示："
echo "- 每次使用前都需要先激活虚拟环境"
echo "- 虚拟环境激活后提示符会显示 (venv)"
echo ""