@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Run INSTALL.bat first.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" MainC.py
if errorlevel 1 echo Analysis failed. Read the message above.
pause
