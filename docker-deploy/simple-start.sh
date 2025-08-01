#!/bin/bash

# 穆桥销售测验系统 - 简单启动脚本（不使用Docker）

echo "=================================================="
echo "      穆桥销售测验系统 - 本地启动"
echo "=================================================="
echo ""

# 检查Node.js是否安装
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装 Node.js"
    echo "访问 https://nodejs.org/ 下载安装"
    exit 1
fi

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装 Python3"
    exit 1
fi

echo "✅ 运行环境检查通过"
echo ""

# 检查端口占用
echo "🔍 检查端口占用..."
if netstat -an | grep ":8000.*LISTEN" > /dev/null 2>&1; then
    echo "⚠️  端口 8000 已被占用，正在尝试停止..."
    pkill -f "python.*8000" || true
fi

if netstat -an | grep ":3001.*LISTEN" > /dev/null 2>&1; then
    echo "⚠️  端口 3001 已被占用，正在尝试停止..."
    pkill -f "node.*sync-server" || true
fi

echo ""
echo "🚀 启动服务..."

# 启动Node.js同步服务器
echo "启动集中化管理API服务器..."
node sync-server.js &
NODE_PID=$!

# 等待Node.js服务器启动
sleep 3

# 启动Python HTTP服务器
echo "启动Web服务器..."
python3 -m http.server 8000 &
HTTP_PID=$!

# 等待服务器启动
sleep 2

echo ""
echo "=================================================="
echo "           🎉 启动成功！"
echo "=================================================="
echo ""
echo "📋 访问地址："
echo "   后台管理：  http://localhost:8000/admin.html"
echo "   考试系统：  http://localhost:8000/exam.html"
echo "   销售链接：  http://localhost:8000/exam.html?mode=sales"
echo ""
echo "🔧 API服务："
echo "   配置API：   http://localhost:3001/api/master-config"
echo "   题库API：   http://localhost:3001/api/master-questions"
echo "   销售API：   http://localhost:3001/api/master-questions?sales=1"
echo ""
echo "⚙️  下一步："
echo "   1. 访问后台管理配置通义千问API"
echo "   2. 将销售链接分享给销售人员"
echo ""
echo "🛑 停止服务："
echo "   按 Ctrl+C 或运行 ./stop.sh"
echo ""
echo "📱 移动端访问："
echo "   将 localhost 替换为本机IP地址即可在手机上访问"
echo ""

# 创建停止脚本
cat > stop.sh << 'EOF'
#!/bin/bash
echo "停止穆桥销售测验系统..."
pkill -f "node.*sync-server" 2>/dev/null
pkill -f "python.*8000" 2>/dev/null
echo "服务已停止"
EOF
chmod +x stop.sh

echo "=================================================="
echo ""
echo "服务正在运行中，按 Ctrl+C 停止..."

# 等待用户中断
trap "echo ''; echo '正在停止服务...'; kill $NODE_PID $HTTP_PID 2>/dev/null; exit 0" INT

# 保持脚本运行
wait