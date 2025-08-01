#!/bin/bash

# 穆桥销售测验系统 - 单文件版本管理脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 显示帮助信息
show_help() {
    echo -e "${BLUE}穆桥销售测验系统 - 单文件版本管理工具${NC}"
    echo "=============================================="
    echo ""
    echo "用法: ./manage.sh [命令] [选项]"
    echo ""
    echo "可用命令:"
    echo "  update-questions    更新题库数据"
    echo "  start-sync          启动数据同步服务器"
    echo "  deploy-docker       Docker部署"
    echo "  test                运行功能测试"
    echo "  backup              备份重要文件"
    echo "  status              显示系统状态"
    echo "  help                显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  ./manage.sh update-questions    # 更新题库"
    echo "  ./manage.sh start-sync          # 启动同步服务"
    echo "  ./manage.sh deploy-docker       # Docker部署"
    echo ""
}

# 更新题库
update_questions() {
    echo -e "${YELLOW}🔄 更新题库数据...${NC}"
    
    if [ ! -f "update-questions.js" ]; then
        echo -e "${RED}❌ 找不到题库更新脚本${NC}"
        exit 1
    fi
    
    if [ ! -f "../local-deploy/data/master-questions.json" ]; then
        echo -e "${RED}❌ 找不到源题库文件${NC}"
        exit 1
    fi
    
    node update-questions.js
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 题库更新完成${NC}"
        echo -e "${BLUE}💡 建议运行测试: ./manage.sh test${NC}"
    else
        echo -e "${RED}❌ 题库更新失败${NC}"
        exit 1
    fi
}

# 启动同步服务器
start_sync() {
    echo -e "${YELLOW}🚀 启动数据同步服务器...${NC}"
    
    if [ ! -f "sync-server.js" ]; then
        echo -e "${RED}❌ 找不到同步服务器脚本${NC}"
        exit 1
    fi
    
    # 检查端口是否被占用
    if lsof -i :3001 > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  端口3001已被占用${NC}"
        read -p "是否强制停止现有进程？(y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            pkill -f "sync-server.js"
            sleep 2
        else
            echo -e "${RED}❌ 取消启动${NC}"
            exit 1
        fi
    fi
    
    echo -e "${GREEN}🌐 同步服务器启动中...${NC}"
    echo -e "${BLUE}💡 使用方法: 在HTML中添加 ?api=http://your-server:3001${NC}"
    echo -e "${BLUE}⌨️  按 Ctrl+C 停止服务器${NC}"
    echo ""
    
    node sync-server.js
}

# Docker部署
deploy_docker() {
    echo -e "${YELLOW}🐳 Docker部署...${NC}"
    
    if [ ! -f "exam-standalone.html" ]; then
        echo -e "${RED}❌ 找不到exam-standalone.html文件${NC}"
        exit 1
    fi
    
    if [ ! -f "deploy-single.sh" ]; then
        echo -e "${RED}❌ 找不到Docker部署脚本${NC}"
        exit 1
    fi
    
    ./deploy-single.sh
}

# 运行测试
run_test() {
    echo -e "${YELLOW}🧪 运行功能测试...${NC}"
    
    if [ ! -f "exam-standalone.html" ]; then
        echo -e "${RED}❌ 找不到exam-standalone.html文件${NC}"
        exit 1
    fi
    
    # 检查文件大小
    size=$(stat -f%z "exam-standalone.html" 2>/dev/null || stat -c%s "exam-standalone.html" 2>/dev/null)
    if [ $size -lt 50000 ]; then
        echo -e "${RED}❌ HTML文件过小，可能数据缺失${NC}"
        echo "   文件大小: $(echo "scale=1; $size/1024" | bc)KB"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 文件大小检查通过: $(echo "scale=1; $size/1024" | bc)KB${NC}"
    
    # 检查内嵌数据
    if grep -q "const EMBEDDED_QUESTIONS = " "exam-standalone.html"; then
        echo -e "${GREEN}✅ 内嵌题库数据检查通过${NC}"
    else
        echo -e "${RED}❌ 内嵌题库数据缺失${NC}"
        exit 1
    fi
    
    if grep -q "const EMBEDDED_CONFIG = " "exam-standalone.html"; then
        echo -e "${GREEN}✅ 内嵌配置数据检查通过${NC}"
    else
        echo -e "${RED}❌ 内嵌配置数据缺失${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}🎉 基础功能测试通过${NC}"
    echo -e "${BLUE}💡 建议在浏览器中测试完整功能${NC}"
    
    if [ -f "test-standalone.html" ]; then
        echo -e "${BLUE}🌐 可以打开 test-standalone.html 进行详细测试${NC}"
    fi
}

# 备份文件
backup_files() {
    echo -e "${YELLOW}💾 备份重要文件...${NC}"
    
    backup_dir="backup-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$backup_dir"
    
    # 备份HTML文件
    if [ -f "exam-standalone.html" ]; then
        cp "exam-standalone.html" "$backup_dir/"
        echo -e "${GREEN}✅ 备份HTML文件${NC}"
    fi
    
    # 备份同步数据
    if [ -d "sync-data" ]; then
        cp -r "sync-data" "$backup_dir/"
        echo -e "${GREEN}✅ 备份同步数据${NC}"
    fi
    
    # 备份源题库
    if [ -f "../local-deploy/data/master-questions.json" ]; then
        cp "../local-deploy/data/master-questions.json" "$backup_dir/"
        echo -e "${GREEN}✅ 备份源题库${NC}"
    fi
    
    echo -e "${GREEN}🎉 备份完成: $backup_dir${NC}"
}

# 显示系统状态
show_status() {
    echo -e "${BLUE}📊 系统状态${NC}"
    echo "=============="
    echo ""
    
    # HTML文件状态
    if [ -f "exam-standalone.html" ]; then
        size=$(stat -f%z "exam-standalone.html" 2>/dev/null || stat -c%s "exam-standalone.html" 2>/dev/null)
        echo -e "${GREEN}✅ HTML文件: 存在 ($(echo "scale=1; $size/1024" | bc)KB)${NC}"
    else
        echo -e "${RED}❌ HTML文件: 不存在${NC}"
    fi
    
    # 源题库状态
    if [ -f "../local-deploy/data/master-questions.json" ]; then
        questions=$(grep -o '"questionId"' "../local-deploy/data/master-questions.json" | wc -l)
        echo -e "${GREEN}✅ 源题库: 存在 ($questions道题目)${NC}"
    else
        echo -e "${RED}❌ 源题库: 不存在${NC}"
    fi
    
    # 同步数据状态
    if [ -d "sync-data" ] && [ -f "sync-data/exam-records.json" ]; then
        records=$(grep -o '"id"' "sync-data/exam-records.json" | wc -l)
        echo -e "${GREEN}✅ 考试记录: $records条${NC}"
    else
        echo -e "${YELLOW}⚠️  考试记录: 无数据${NC}"
    fi
    
    # 服务状态
    if lsof -i :3001 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 同步服务: 运行中 (端口3001)${NC}"
    else
        echo -e "${YELLOW}⚠️  同步服务: 未运行${NC}"
    fi
    
    # Docker状态
    if docker ps | grep -q "neurogen-exam-single"; then
        echo -e "${GREEN}✅ Docker服务: 运行中${NC}"
    else
        echo -e "${YELLOW}⚠️  Docker服务: 未运行${NC}"
    fi
    
    echo ""
}

# 主程序
main() {
    case "$1" in
        "update-questions")
            update_questions
            ;;
        "start-sync")
            start_sync
            ;;
        "deploy-docker")
            deploy_docker
            ;;
        "test")
            run_test
            ;;
        "backup")
            backup_files
            ;;
        "status")
            show_status
            ;;
        "help"|"--help"|"-h"|"")
            show_help
            ;;
        *)
            echo -e "${RED}❌ 未知命令: $1${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 检查依赖
check_dependencies() {
    # 检查Node.js
    if ! command -v node > /dev/null 2>&1; then
        echo -e "${RED}❌ 需要安装Node.js${NC}"
        exit 1
    fi
    
    # 检查bc (计算器)
    if ! command -v bc > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  建议安装bc命令用于计算${NC}"
    fi
}

# 运行主程序
check_dependencies
main "$@"