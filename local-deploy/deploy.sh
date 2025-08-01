#!/bin/bash

# 穆桥销售测验系统 - 服务器部署脚本
# 适用于 Linux/Ubuntu/CentOS 等服务器环境

set -e  # 遇到错误立即退出

echo "=================================================="
echo "    穆桥销售测验系统 - 服务器部署脚本"
echo "=================================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为root用户
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "请使用root用户运行此脚本"
        log_info "使用命令: sudo bash deploy.sh"
        exit 1
    fi
}

# 检查系统类型
detect_os() {
    if [[ -f /etc/redhat-release ]]; then
        OS="centos"
        PACKAGE_MANAGER="yum"
    elif [[ -f /etc/lsb-release ]] || [[ -f /etc/debian_version ]]; then
        OS="ubuntu"
        PACKAGE_MANAGER="apt-get"
    else
        log_warn "未能识别操作系统，默认使用Ubuntu命令"
        OS="ubuntu"
        PACKAGE_MANAGER="apt-get"
    fi
    log_info "检测到操作系统: $OS"
}

# 安装Docker
install_docker() {
    log_info "检查Docker安装状态..."
    
    if command -v docker &> /dev/null; then
        log_info "Docker已安装: $(docker --version)"
    else
        log_info "开始安装Docker..."
        
        if [[ "$OS" == "ubuntu" ]]; then
            apt-get update
            apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
            curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
            echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
            apt-get update
            apt-get install -y docker-ce docker-ce-cli containerd.io
        elif [[ "$OS" == "centos" ]]; then
            yum install -y yum-utils
            yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
            yum install -y docker-ce docker-ce-cli containerd.io
        fi
        
        systemctl start docker
        systemctl enable docker
        log_info "Docker安装完成"
    fi
}

# 安装Docker Compose
install_docker_compose() {
    log_info "检查Docker Compose安装状态..."
    
    if command -v docker-compose &> /dev/null; then
        log_info "Docker Compose已安装: $(docker-compose --version)"
    else
        log_info "开始安装Docker Compose..."
        curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
        ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
        log_info "Docker Compose安装完成"
    fi
}

# 配置防火墙
configure_firewall() {
    log_info "配置防火墙..."
    
    if command -v ufw &> /dev/null; then
        ufw allow 80/tcp
        ufw allow 443/tcp
        ufw allow 8080/tcp
        log_info "UFW防火墙规则已添加"
    elif command -v firewall-cmd &> /dev/null; then
        firewall-cmd --permanent --add-port=80/tcp
        firewall-cmd --permanent --add-port=443/tcp
        firewall-cmd --permanent --add-port=8080/tcp
        firewall-cmd --reload
        log_info "Firewalld防火墙规则已添加"
    else
        log_warn "未检测到防火墙，请手动开放80、443、8080端口"
    fi
}

# 停止现有服务
stop_existing() {
    log_info "停止现有服务..."
    docker-compose down 2>/dev/null || true
    docker stop neurogen-exam-system 2>/dev/null || true
    docker rm neurogen-exam-system 2>/dev/null || true
}

# 构建并启动服务
build_and_start() {
    log_info "构建Docker镜像..."
    docker-compose build --no-cache
    
    log_info "启动服务..."
    docker-compose up -d
    
    # 等待服务启动
    sleep 10
    
    # 检查服务状态
    if docker-compose ps | grep -q "Up"; then
        log_info "✅ 服务启动成功！"
    else
        log_error "❌ 服务启动失败"
        docker-compose logs
        exit 1
    fi
}

# 获取服务器IP
get_server_ip() {
    # 尝试多种方法获取公网IP
    SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || curl -s icanhazip.com 2>/dev/null || echo "")
    
    if [[ -z "$SERVER_IP" ]]; then
        # 获取本机IP
        SERVER_IP=$(ip route get 8.8.8.8 | awk '{print $7}' | head -n1)
    fi
    
    if [[ -z "$SERVER_IP" ]]; then
        SERVER_IP="你的服务器IP"
    fi
}

# 显示部署信息
show_deploy_info() {
    get_server_ip
    
    echo ""
    echo "=================================================="
    echo "           🎉 部署完成！"
    echo "=================================================="
    echo ""
    echo "📋 访问地址："
    echo "   考试系统：  http://$SERVER_IP/exam.html"
    echo "   销售链接：  http://$SERVER_IP/exam.html?mode=sales"
    echo "   管理后台：  http://$SERVER_IP/admin.html"
    echo ""
    echo "🔧 备用端口 (如果80端口被占用)："
    echo "   考试系统：  http://$SERVER_IP:8080/exam.html"
    echo "   销售链接：  http://$SERVER_IP:8080/exam.html?mode=sales"
    echo "   管理后台：  http://$SERVER_IP:8080/admin.html"
    echo ""
    echo "🛠️ 管理命令："
    echo "   查看状态：  docker-compose ps"
    echo "   查看日志：  docker-compose logs -f"
    echo "   重启服务：  docker-compose restart"
    echo "   停止服务：  docker-compose down"
    echo ""
    echo "📱 移动端支持："
    echo "   手机、平板、微信浏览器均可正常访问"
    echo ""
    echo "⚙️  下一步："
    echo "   1. 访问管理后台配置通义千问API"
    echo "   2. 将销售链接分享给销售人员"
    echo ""
    echo "=================================================="
}

# 主函数
main() {
    log_info "开始部署流程..."
    
    check_root
    detect_os
    install_docker
    install_docker_compose
    configure_firewall
    stop_existing
    build_and_start
    show_deploy_info
    
    log_info "部署流程完成！"
}

# 执行主函数
main "$@"