@echo off
chcp 65001 >nul
echo 🚀 快速部署卡密查询系统（简化版）...

REM 检查Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker未安装，请先安装Docker Desktop
    pause
    exit /b 1
)

REM 创建必要的目录
echo 📁 创建必要的目录...
if not exist data mkdir data
if not exist logs mkdir logs

REM 停止现有容器
echo 🛑 停止现有容器...
docker-compose -f docker-compose.simple.yml down

REM 构建镜像（使用优化的Dockerfile）
echo 🔨 构建Docker镜像（使用国内镜像源）...
docker-compose -f docker-compose.simple.yml build

REM 启动服务
echo 🚀 启动服务...
docker-compose -f docker-compose.simple.yml up -d

REM 等待服务启动
echo ⏳ 等待服务启动...
timeout /t 15 /nobreak >nul

REM 检查服务状态
echo 🔍 检查服务状态...
docker-compose -f docker-compose.simple.yml ps

REM 健康检查
echo 🏥 进行健康检查...
curl -f http://localhost:5000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ 应用服务健康检查通过
    echo.
    echo 🎉 快速部署完成！
    echo 📱 应用访问地址: http://localhost:5000
    echo 🔧 管理员登录: admin/admin123
    echo 📊 查看日志: docker-compose -f docker-compose.simple.yml logs -f
    echo 🛑 停止服务: docker-compose -f docker-compose.simple.yml down
    echo.
    echo 🌐 正在打开浏览器...
    start http://localhost:5000/admin/login
) else (
    echo ❌ 应用服务健康检查失败
    echo 📋 查看日志：
    docker-compose -f docker-compose.simple.yml logs web
)

pause
