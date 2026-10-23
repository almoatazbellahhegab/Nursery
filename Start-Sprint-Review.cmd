@echo off
cd /d "%~dp0"
where node >nul 2>nul
if errorlevel 1 (
  echo Node.js 20.9 or newer is required. Install Node.js then try again.
  pause
  exit /b 1
)
echo Starting the Nursery sprint review. Keep this window open.
echo Windows: http://localhost:3100
echo iPhone: use the Wi-Fi URL printed below, on the same network.
start "" "http://localhost:3100"
node tools/review-server.mjs
pause
