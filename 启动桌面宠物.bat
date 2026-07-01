@echo off
title 🐱 桌面宠物
cd /d "%~dp0"
echo 正在启动桌面宠物...
python desktop_pet.py
if errorlevel 1 (
    echo.
    echo 启动失败！请确认已安装 Python 3.x
    echo 下载: https://www.python.org/downloads/
    pause
)
