@echo off
chcp 65001 >nul
title 企业微信服务 + Cloudflare Tunnel

echo ============================================
echo   企业微信消息回调服务 + Cloudflare Tunnel
echo ============================================
echo.
set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
echo 此脚本将同时启动:
echo   1. Cloudflare Tunnel (内网穿透)
echo   2. 企业微信回调服务 (端口 8800)
echo.
echo 请确保已配置 %SCRIPT_DIR%\config.json
echo.
echo TIP: 启动后，将 Cloudflare 提供的 URL + /wecom/callback
echo      填入企业微信后台的回调 URL 配置中。
echo ============================================
echo.

echo [%date% %time%] 启动 Cloudflare Tunnel...
start "CloudflareTunnel" cmd /c ""C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel --url http://localhost:8800 > "%SCRIPT_DIR%\logs\tunnel.log" 2>&1"

echo 等待 Tunnel 初始化（10秒）...
timeout /t 10 /nobreak >nul

echo.
echo [%date% %time%] 启动企业微信服务...
echo ============================================
echo.
cd /d "%SCRIPT_DIR%"
python server.py

pause
