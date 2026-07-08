@echo off
title 🐱 桌面宠物
cd /d "%~dp0"

:: 尝试多个可能的 Python 路径（优先用 Python Launcher，自动适配版本）
set PYTHON_CMD=
for /f "tokens=2 delims=:" %%P in ('py --list-paths 2^>nul') do (
    if not defined PYTHON_CMD set PYTHON_CMD=%%P
)

if not defined PYTHON_CMD (
    where python >nul 2>nul && set PYTHON_CMD=python
)

if not defined PYTHON_CMD (
    for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
        if exist "%%D\python.exe" set PYTHON_CMD=%%D\python.exe
    )
)

if not defined PYTHON_CMD (
    if exist "C:\Users\Lenovo\AppData\Local\Programs\Python\Python312\python.exe" set PYTHON_CMD=C:\Users\Lenovo\AppData\Local\Programs\Python\Python312\python.exe
)

if not defined PYTHON_CMD (
    echo [X] 未找到 Python，请安装 Python 3.x
    echo     下载: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 检查脚本是否存在
if not exist "desktop_pet.py" (
    echo [X] 未找到 desktop_pet.py
    pause
    exit /b 1
)

:: 预检 Python 和脚本语法
"%PYTHON_CMD%" -c "import tkinter" 2>nul
if errorlevel 1 (
    echo [X] Python 缺少 tkinter 模块，请安装：python -m pip install tk
    pause
    exit /b 1
)

"%PYTHON_CMD%" -m py_compile "desktop_pet.py" 2>nul
if errorlevel 1 (
    echo [X] desktop_pet.py 语法错误，请检查代码
    pause
    exit /b 1
)

echo 正在启动桌面宠物...
start /B "" "%PYTHON_CMD%" desktop_pet.py
exit
