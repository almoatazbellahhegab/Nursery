@echo off
cd /d "%~dp0"
echo Stop the application review server before rebuilding the clients.
node tools/check-clients.mjs
set "NURSERY_CLIENT_EXIT=%ERRORLEVEL%"
echo.
echo Client check exit code: %NURSERY_CLIENT_EXIT%
pause
exit /b %NURSERY_CLIENT_EXIT%
