@echo off
title 🌸 像素桌宠
cd /d "%~dp0"

:: 找 Python
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
    echo [X] 未找到 Python
    pause
    exit /b 1
)

:: 确保 Pillow 已安装
"%PYTHON_CMD%" -c "from PIL import Image" 2>nul
if errorlevel 1 (
    echo 正在安装 Pillow...
    "%PYTHON_CMD%" -m pip install Pillow -q
)

if not exist "pixel_pet.py" (
    echo [X] 未找到 pixel_pet.py
    pause
    exit /b 1
)

echo 正在启动像素桌宠...
start /B "" "%PYTHON_CMD%" pixel_pet.py
exit
