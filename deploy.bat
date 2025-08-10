@echo off
chcp 65001 >nul
echo 🚀 开始部署卡密查询系统...

REM 检查Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker未安装，请先安装Docker Desktop
    pause
    exit /b 1
)

REM 检查Docker Compose
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose未安装，请先安装Docker Compose
    pause
    exit /b 1
)

REM 检查环境变量文件
if not exist .env (
    echo ⚠️  未找到.env文件，从.env.example复制...
    if exist .env.example (
        copy .env.example .env >nul
        echo ✅ 已创建.env文件，请编辑其中的配置
        echo ⚠️  请务必修改SECRET_KEY和数据库密码！
    ) else (
        echo ❌ 未找到.env.example文件
        pause
        exit /b 1
    )
)

REM 创建必要的目录
echo 📁 创建必要的目录...
if not exist logs mkdir logs
if not exist logs\nginx mkdir logs\nginx
if not exist nginx\ssl mkdir nginx\ssl

REM 停止现有容器
echo 🛑 停止现有容器...
docker-compose down

REM 构建镜像
echo 🔨 构建Docker镜像...
docker-compose build

REM 启动服务
echo 🚀 启动服务...
docker-compose up -d

REM 等待服务启动
echo ⏳ 等待服务启动...
timeout /t 10 /nobreak >nul

REM 检查服务状态
echo 🔍 检查服务状态...
docker-compose ps

REM 健康检查
echo 🏥 进行健康检查...
curl -f http://localhost:5000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ 应用服务健康检查通过
) else (
    echo ❌ 应用服务健康检查失败
    echo 📋 查看日志：
    docker-compose logs web
    pause
    exit /b 1
)

echo 🎉 部署完成！
echo 📱 应用访问地址: http://localhost:5000
echo 🔧 管理员登录: admin/admin123
echo 📊 查看日志: docker-compose logs -f
echo 🛑 停止服务: docker-compose down
pause
