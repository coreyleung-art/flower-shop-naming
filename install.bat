@echo off
chcp 65001 >nul
REM ============================================================
REM 花店物品命名审查工具 - Windows安装脚本
REM ============================================================

setlocal enabledelayedexpansion

echo ========================================
echo   花店物品命名审查工具 安装程序
echo ========================================
echo.

REM 检查Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    where python3 >nul 2>&1
    if %errorlevel% neq 0 (
        echo 错误: 未找到Python，请先安装Python 3.8+
        echo 下载地址: https://www.python.org/downloads/
        pause
        exit /b 1
    )
    set PYTHON_CMD=python3
) else (
    set PYTHON_CMD=python
)

for /f "tokens=2" %%i in ('%PYTHON_CMD% --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✓ 检测到Python版本: %PYTHON_VERSION%
echo.

echo 请选择安装方式:
echo   1) 本地安装 (当前目录)
echo   2) pip安装
echo.
set /p choice="请输入选项 [1-2]: "

if "%choice%"=="1" (
    echo.
    echo 本地安装模式...

    REM 创建批处理文件
    (
        echo @echo off
        echo %PYTHON_CMD% "%~dp0item_naming_cli.py" %%*
    ) > flower-naming.bat

    echo.
    echo ✓ 安装完成!
    echo.
    echo 使用方法:
    echo   flower-naming.bat "商品名称"
    echo.
) else if "%choice%"=="2" (
    echo.
    echo 使用pip安装...
    %PYTHON_CMD% -m pip install git+https://github.com/coreyleung-art/flower-shop-naming.git

    echo.
    echo ✓ 安装完成!
    echo.
    echo 使用方法:
    echo   flower-naming "商品名称"
    echo.
) else (
    echo 无效选项
    pause
    exit /b 1
)

echo ========================================
echo   感谢使用花店物品命名审查工具!
echo ========================================
pause
