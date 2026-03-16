@echo off
cd /d "%~dp0"
REM Start the app then open browser after short delay
start "" cmd /k "python app.py"
ping localhost -n 3 >nul
start http://127.0.0.1:5000
pause
