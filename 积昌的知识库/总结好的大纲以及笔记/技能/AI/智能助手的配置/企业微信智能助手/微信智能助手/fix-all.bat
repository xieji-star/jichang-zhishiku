@echo off
chcp 437 >nul
title Fix Service - Run as Admin
echo ============================================
echo Start WeCom Callback Service
echo (Using LocalTunnel - compatible with WARP)
echo ============================================
echo.

>nul 2>&1 net session || (
    echo ERROR: Right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo [1/3] Killing old processes...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
timeout /t 3 >nul
echo Done

echo [2/3] Cleaning old logs...
del /f /q "%~dp0logs\tunnel.log" >nul 2>&1
del /f /q "%~dp0logs\wecom-service.log" >nul 2>&1
echo Done

echo [3/3] Starting service with LocalTunnel...
cd /d "%~dp0"
start /B python server.py --with-tunnel > logs\service-output.log 2>&1

echo.
echo Waiting for tunnel to be ready...
setlocal enabledelayedexpansion
for /l %%i in (1,1,20) do (
    timeout /t 3 >nul
    if exist "%~dp0current-tunnel-url.txt" (
        echo.
        echo ============================================
        echo TUNNEL URL:
        type "%~dp0current-tunnel-url.txt"
        echo ============================================
        echo.
        echo IMPORTANT: Copy the URL above, then:
        echo 1. Go to WeCom admin console
        echo 2. App Management - Knowledge Base Assistant
        echo 3. Receive Messages - Setup API Receiving
        echo 4. Paste URL + "/wecom/callback"
        echo 5. Click Save
        echo.
        echo Then send "/help" or "/帮助" in WeChat/WeCom to test.
        goto :END
    )
)
echo Timed out waiting for tunnel URL
echo Check logs\service-output.log and logs\tunnel.log

:END
endlocal
pause
