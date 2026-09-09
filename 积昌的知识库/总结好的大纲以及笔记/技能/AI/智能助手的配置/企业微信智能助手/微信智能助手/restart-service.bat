@echo off
chcp 65001 >nul
title 重启企业微信服务（需要管理员权限）

echo ============================================
echo   重启企业微信消息回调服务
echo ============================================
echo.
setlocal

REM 获取脚本所在目录
set "SCRIPT_DIR=%~dp0"
REM 去掉末尾的反斜杠
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

>nul 2>&1 net session || (
    echo [错误] 请右键此文件 → "以管理员身份运行"
    pause
    exit /b 1
)

echo [1/3] 停止旧进程...
taskkill /f /im python.exe 2>nul
taskkill /f /im node.exe 2>nul
timeout /t 3 /nobreak >nul
echo   完成

echo [2/3] 清理旧日志...
del /f /q "%SCRIPT_DIR%\logs\tunnel.log" 2>nul
del /f /q "%SCRIPT_DIR%\logs\wecom-service.log" 2>nul
echo   完成

echo [3/3] 启动服务...
cd /d "%SCRIPT_DIR%"
start "WeComService" /B python server.py --with-tunnel > "%SCRIPT_DIR%\logs\service-output.log" 2>&1
echo   服务已启动（PID 请查看任务管理器）
echo.

REM 等待服务初始化
echo 等待 Tunnel 就绪...
for /l %%i in (1,1,20) do (
    timeout /t 3 /nobreak >nul
    if exist "%SCRIPT_DIR%\current-tunnel-url.txt" (
        echo.
        echo ============================================
        echo   当前 Tunnel URL:
        type "%SCRIPT_DIR%\current-tunnel-url.txt"
        echo ============================================
        goto :SHOW_INFO
    )
)

echo.
echo ⚠️ 超时未检测到 Tunnel URL，请查看日志:
echo   %SCRIPT_DIR%\logs\service-output.log
echo   %SCRIPT_DIR%\logs\tunnel.log
echo.
goto :END

:SHOW_INFO
echo.
echo ============================================
echo   服务启动完成！
echo ============================================
echo.
echo 请将上面的 URL 复制，然后执行以下步骤：
echo.
echo 1. 打开企业微信管理后台
echo    https://work.weixin.qq.com/wework_admin/frame
echo.
echo 2. 进入 应用管理 → 知识库助手 → 接收消息 → 设置API接收
echo.
echo 3. 将 URL 改为上方显示的 URL + "/wecom/callback"
echo.
echo 4. 在微信/企业微信中发送 "/帮助" 测试
echo.

:END
endlocal
pause
