@echo off
cd /d C:\
echo ============================================================
echo  Flask server (Window A). Keep it open while demonstrating.
echo  It logs each request as you type commands in the other window.
echo  Close this window or press Ctrl+C when you are done.
echo ============================================================
powershell -NoProfile -ExecutionPolicy Bypass -Command "Set-Location -LiteralPath '%~dp0'; & '.\.venv\Scripts\python.exe' app.py"
pause