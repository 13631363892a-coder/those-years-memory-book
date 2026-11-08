@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 正在启动青春纪念册...
python serve.py
pause
