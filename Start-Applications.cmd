@echo off
cd /d "%~dp0"
set "NODE_OPTIONS=--preserve-symlinks --preserve-symlinks-main"
node tools/start-connected.mjs
pause
