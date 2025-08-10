#!/bin/bash

# 卡密查询系统部署脚本

set -e

echo "🚀 开始部署卡密查询系统..."

# 检查Docker和Docker Compose
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 检查环境变量文件
if [ ! -f .env ]; then
    echo "⚠️  未找到.env文件，从.env.example复制..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ 已创建.env文件，请编辑其中的配置"
        echo "⚠️  请务必修改SECRET_KEY和数据库密码！"
    else
        echo "❌ 未找到.env.example文件"
        exit 1
    fi
fi

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p logs/nginx
mkdir -p nginx/ssl

# 停止现有容器
echo "🛑 停止现有容器..."
docker-compose down

# 构建镜像
echo "🔨 构建Docker镜像..."
docker-compose build

# 启动服务
echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 健康检查
echo "🏥 进行健康检查..."
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ 应用服务健康检查通过"
else
    echo "❌ 应用服务健康检查失败"
    echo "📋 查看日志："
    docker-compose logs web
    exit 1
fi

echo "🎉 部署完成！"
echo "📱 应用访问地址: http://localhost:5000"
echo "🔧 管理员登录: admin/admin123"
echo "📊 查看日志: docker-compose logs -f"
echo "🛑 停止服务: docker-compose down"
