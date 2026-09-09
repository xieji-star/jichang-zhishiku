@echo off
chcp 65001 >nul
title 修复 WARP DNS（不再需要 - 可选保留）

echo ============================================
echo   当前服务已改用 LocalTunnel
echo   不再受 WARP DNS 劫持影响！
echo ============================================
echo.
echo 此脚本不再需要运行。
echo LocalTunnel 通过 HTTPS WebSocket 连接公网服务器，
echo Cloudflare WARP 不会拦截其流量。
echo.
echo 如果今后恢复使用 Cloudflare Tunnel，可再次使用此脚本。
echo.
set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
echo 现在服务使用的是 LocalTunnel，URL 在：
echo   %SCRIPT_DIR%\current-tunnel-url.txt
echo.
pause
