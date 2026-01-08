@echo off
echo ========================================
echo  Yjs Collaboration Server Launcher
echo ========================================
echo.

REM Check if node_modules exists
if not exist "node_modules" (
    echo [INFO] Installing dependencies...
    call npm install
    echo.
)

echo [INFO] Starting Yjs WebSocket server...
echo.
node server.js

pause

