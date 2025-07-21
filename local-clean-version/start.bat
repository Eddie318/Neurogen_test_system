@echo off
chcp 65001 >nul
title 穆桥销售测验系统 - Docker 一键部署

echo ==================================================
echo       穆桥销售测验系统 - Docker 一键部署
echo ==================================================
echo.

REM 检查Docker是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker 未安装，请先安装 Docker Desktop
    echo 访问 https://docs.docker.com/desktop/windows/ 下载安装
    pause
    exit /b 1
)

REM 检查docker-compose是否安装
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ docker-compose 未安装，请先安装 Docker Desktop
    echo Docker Desktop 包含 docker-compose
    pause
    exit /b 1
)

echo ✅ Docker 环境检查通过
echo.

REM 检查端口占用
netstat -an | findstr :80 >nul 2>&1
if not errorlevel 1 (
    echo ⚠️  警告：端口 80 已被占用
    set /p use_8080=是否要使用 8080 端口？(y/n): 
    if /i "!use_8080!"=="y" (
        powershell -Command "(gc docker-compose.yml) -replace '\"80:80\"', '\"8080:80\"' | sc docker-compose.yml"
        echo ✅ 已配置使用 8080 端口
        set PORT=8080
    ) else (
        echo ❌ 请先停止占用 80 端口的服务，然后重新运行此脚本
        pause
        exit /b 1
    )
) else (
    set PORT=80
)

echo.
echo 🚀 开始构建和启动服务...
echo.

REM 停止并移除旧容器（如果存在）
docker-compose down >nul 2>&1

REM 构建并启动服务
docker-compose up -d --build
if errorlevel 1 (
    echo.
    echo ❌ 部署失败，请检查错误信息
    echo.
    echo 🔍 故障排除：
    echo    1. 确保 Docker Desktop 正在运行
    echo    2. 检查端口占用：netstat -an ^| findstr :%PORT%
    echo    3. 查看详细日志：docker-compose logs
    echo.
    pause
    exit /b 1
)

echo.
echo ==================================================
echo            🎉 部署成功！
echo ==================================================
echo.
echo 📋 访问地址：
echo    后台管理：  http://localhost:%PORT%/admin.html
echo    考试系统：  http://localhost:%PORT%/exam.html
echo    销售链接：  http://localhost:%PORT%/exam.html?mode=sales
echo.
echo 🔧 管理命令：
echo    查看状态：  docker-compose ps
echo    查看日志：  docker-compose logs -f
echo    停止服务：  docker-compose down
echo    重启服务：  docker-compose restart
echo.
echo 📱 移动端访问：
echo    将 localhost 替换为服务器IP地址即可在手机上访问
echo.
echo ⚙️  下一步：
echo    1. 访问后台管理配置通义千问API
echo    2. 导入题库或使用内置的54道题目
echo    3. 将销售链接分享给销售人员
echo.
echo ==================================================
echo.
pause