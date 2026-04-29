@echo off
echo ========================================
echo AIData Backend - 环境安装脚本
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    echo 下载地址: https://www.python.org/downloads/
    echo 安装时请勾选 "Add Python to PATH"
    pause
    exit /b 1
)

echo [OK] Python 已找到
python --version
echo.

REM 创建虚拟环境（可选）
echo 是否创建虚拟环境？(Y/N)
set /p create_venv=
if /i "%create_venv%"=="Y" (
    echo 创建虚拟环境...
    python -m venv venv
    echo 激活虚拟环境...
    call venv\Scripts\activate
)

echo.
echo [1/2] 安装 Python 依赖...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)
echo [OK] 依赖安装完成

echo.
echo [2/2] 初始化业务数据库...
python scripts\init_db.py
if %errorlevel% neq 0 (
    echo [错误] 数据库初始化失败
    pause
    exit /b 1
)
echo [OK] 数据库初始化完成

echo.
echo ========================================
echo 环境安装成功！
echo.
echo 启动后端服务：
echo   cd backend
echo   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo.
echo 访问 API 文档：http://localhost:8000/docs
echo ========================================
pause
