@echo off
cd /d C:\
echo ============================================================
echo  Running secure API demo (6 checks). Keep this window open.
echo ============================================================
powershell -NoProfile -ExecutionPolicy Bypass -Command "Set-Location -LiteralPath '%~dp0'; & '.\demo-api.ps1'"
echo.
echo Done. Press any key to close.
pause >nul