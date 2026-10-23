@echo off
cd /d "%~dp0"
if not exist "services\api\.venv\Scripts\python.exe" (
  echo Set up the API project environment first. See services\api\README.md.
  pause
  exit /b 1
)
node tools/run-attendance-checks.mjs
set "NURSERY_ATTENDANCE_EXIT=%ERRORLEVEL%"
echo.
echo Attendance check exit code: %NURSERY_ATTENDANCE_EXIT%
pause
exit /b %NURSERY_ATTENDANCE_EXIT%
