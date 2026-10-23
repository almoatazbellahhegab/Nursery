@echo off
cd /d "%~dp0"
node --test tests/system/review.test.mjs
set "NURSERY_TEST_EXIT=%ERRORLEVEL%"
echo.
echo Test exit code: %NURSERY_TEST_EXIT%
pause
exit /b %NURSERY_TEST_EXIT%
