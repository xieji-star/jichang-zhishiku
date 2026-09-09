@echo off
chcp 65001 >nul
title 安装企业微信服务（需要管理员权限）

echo ============================================
echo   企业微信消息回调服务 — 安装为 Windows 服务
echo ============================================
echo.
set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
echo 当前目录: %SCRIPT_DIR%
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 请右键此文件 → "以管理员身份运行"
    echo.
    pause
    exit /b 1
)

echo [1/4] 停止旧服务（如果存在）...
nssm stop WeComService 2>nul
nssm remove WeComService confirm 2>nul
echo 完成

echo [2/4] 注册新服务...
nssm install WeComService python "%SCRIPT_DIR%\server.py --with-tunnel"
if %errorlevel% neq 0 (
    echo [错误] 服务注册失败
    pause
    exit /b 1
)
echo 完成

echo [3/4] 配置服务参数...
nssm set WeComService AppDirectory "%SCRIPT_DIR%"
nssm set WeComService DisplayName "企业微信消息回调服务"
nssm set WeComService Description "接收企业微信消息并调用 Claude AI 处理，结果写入 Obsidian Vault"
nssm set WeComService Start SERVICE_AUTO_START
nssm set WeComService AppStdout "%SCRIPT_DIR%\logs\service-stdout.log"
nssm set WeComService AppStderr "%SCRIPT_DIR%\logs\service-stderr.log"
nssm set WeComService AppRotateFiles 1
nssm set WeComService AppRotateOnline 1
nssm set WeComService AppRotateSeconds 86400
nssm set WeComService AppRotateBytes 1048576
echo 完成

echo [4/4] 启动服务...
nssm start WeComService
if %errorlevel% neq 0 (
    echo [警告] 服务启动可能失败，查看日志:
    echo   %SCRIPT_DIR%\logs\service-stderr.log
)
echo.

echo ============================================
echo   安装完成！
echo ============================================
echo.
echo 服务名称: WeComService
echo 服务状态: 应已启动
echo.
echo 常用命令:
echo   查看状态: nssm status WeComService
echo   停止服务: nssm stop WeComService
echo   重启服务: nssm restart WeComService
echo   查看日志: type %SCRIPT_DIR%\logs\wecom-service.log
echo   卸载服务: nssm remove WeComService confirm
echo.
echo 注意: 每次电脑重启后，Tunnel URL 会变化。
echo 你需要在企业微信后台更新回调 URL。
echo.

pause
