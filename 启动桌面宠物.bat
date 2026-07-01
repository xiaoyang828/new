@echo off
title 🐱 桌面宠物
cd /d "%~dp0"

:: 尝试多个可能的 Python 路径
set PYTHON_CMD=
where python >nul 2>nul && set PYTHON_CMD=python
if not defined PYTHON_CMD (
    if exist "C:\Users\Lenovo\AppData\Local\Programs\Python\Python312\python.exe" set PYTHON_CMD=C:\Users\Lenovo\AppData\Local\Programs\Python\Python312\python.exe
)
if not defined PYTHON_CMD (
    if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe
)

if not defined PYTHON_CMD (
    echo [X] 未找到 Python，请安装 Python 3.x
    echo     下载: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo 正在启动桌面宠物...
start /B "" "%PYTHON_CMD%" desktop_pet.py
exit
