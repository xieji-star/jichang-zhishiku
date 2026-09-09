@echo off
chcp 65001 >nul
title 飞书消息监听服务

echo ============================================
echo   启动飞书消息监听服务
echo ============================================
echo.

set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

echo [1/2] 清理旧日志...
del /f /q "%SCRIPT_DIR%\logs\lark-service.log" 2>nul
echo   完成

echo [2/2] 启动服务...
cd /d "%SCRIPT_DIR%"
start "LarkService" /B python server.py > "%SCRIPT_DIR%\logs\service-output.log" 2>&1
echo   服务已启动
echo.

echo ============================================
echo   服务启动完成！
echo ============================================
echo.
echo 请在飞书中给机器人"谢积昌的飞书CLI"发送消息测试
echo 日志文件: %SCRIPT_DIR%\logs\lark-service.log
echo.
pause
