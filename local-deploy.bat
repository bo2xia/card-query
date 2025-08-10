@echo off
chcp 65001 >nul
echo 🚀 本地部署卡密查询系统...

REM 检查Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未安装，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 创建必要的目录
echo 📁 创建必要的目录...
if not exist data mkdir data
if not exist logs mkdir logs

REM 检查虚拟环境
if not exist venv (
    echo 🔧 创建Python虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo 🔄 激活虚拟环境...
call venv\Scripts\activate.bat

REM 升级pip
echo ⬆️ 升级pip...
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

REM 安装依赖
echo 📦 安装Python依赖...
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

REM 设置环境变量
echo 🔧 设置环境变量...
set FLASK_ENV=development
set SECRET_KEY=local-dev-secret-key
set DATABASE_URL=sqlite:///data/app.db

REM 启动应用
echo 🚀 启动应用...
echo.
echo 🎉 应用正在启动...
echo 📱 应用访问地址: http://localhost:5000
echo 🔧 管理员登录: admin/admin123
echo 🛑 停止服务: 按 Ctrl+C
echo.

python app.py
