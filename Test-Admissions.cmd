@echo off
cd /d "%~dp0"
if not exist "services\api\.venv\Scripts\python.exe" (
  echo Set up the API project environment first. See services\api\README.md.
  pause
  exit /b 1
)
node tools/run-admissions-checks.mjs
set "NURSERY_ADMISSIONS_EXIT=%ERRORLEVEL%"
echo.
echo Admissions check exit code: %NURSERY_ADMISSIONS_EXIT%
pause
exit /b %NURSERY_ADMISSIONS_EXIT%
