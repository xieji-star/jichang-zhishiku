@echo off
chcp 65001 >nul
title 企业微信消息回调服务

echo ============================================
echo   企业微信消息回调服务 v1.0.0
echo ============================================
echo.
echo 启动模式: 仅服务（需单独启动 Cloudflare Tunnel）
echo 监听端口: 8800
echo.
set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
echo 请确保已配置 %SCRIPT_DIR%\config.json
echo.

echo [%date% %time%] 启动服务...
cd /d "%SCRIPT_DIR%"
python server.py

pause
