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

echo ""
echo "🚀 启动Web服务器..."

# 启动Python HTTP服务器（绑定所有IP地址）
echo "启动本地文件服务器..."
python3 -m http.server 8000 --bind 0.0.0.0 &
HTTP_PID=$!

# 等待服务器启动
sleep 2

echo ""
echo "=================================================="
echo "           🎉 启动成功！"
echo "=================================================="
# 获取本机IP地址
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)

echo ""
echo "📋 电脑端访问地址："
echo "   后台管理：  http://localhost:8000/admin.html"
echo "   考试系统：  http://localhost:8000/exam.html"
echo "   销售链接：  http://localhost:8000/exam.html?mode=sales"
echo ""
echo "📱 手机端访问地址："
echo "   后台管理：  http://${LOCAL_IP}:8000/admin.html"
echo "   考试系统：  http://${LOCAL_IP}:8000/exam.html"
echo "   销售链接：  http://${LOCAL_IP}:8000/exam.html?mode=sales"
echo ""
echo "📁 数据存储："
echo "   题库数据：  data/master-questions.json"
echo "   系统配置：  data/master-config.json"
echo "   考试记录：  浏览器localStorage"
echo ""
echo "⚙️  管理说明："
echo "   1. 题库修改：直接编辑 data/master-questions.json 文件"
echo "   2. API配置：编辑 data/master-config.json 文件"
echo "   3. 考试记录：通过后台管理页面查看和导出"
echo ""
echo "🛑 停止服务："
echo "   按 Ctrl+C 或运行 ./stop.sh"
echo ""
echo "📋 移动端使用说明："
echo "   1. 确保手机和电脑在同一WiFi网络"
echo "   2. 在手机浏览器中输入上面的手机端地址"
echo "   3. 建议将销售链接添加到手机桌面快捷方式"
echo ""

# 创建停止脚本
cat > stop.sh << 'EOF'
#!/bin/bash
echo "停止穆桥销售测验系统..."
pkill -f "python.*8000" 2>/dev/null
echo "Web服务器已停止"
EOF
chmod +x stop.sh

echo "=================================================="
echo ""
echo "服务正在运行中，按 Ctrl+C 停止..."

# 等待用户中断
trap "echo ''; echo '正在停止服务...'; kill $HTTP_PID 2>/dev/null; exit 0" INT

# 保持脚本运行
wait