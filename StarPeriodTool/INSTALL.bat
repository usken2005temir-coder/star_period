@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    py -m venv .venv
    if errorlevel 1 goto failed
)
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
echo Installation complete. Put observations in UPLOAD_DATA_HERE and open RUN.bat.
pause
exit /b 0
:failed
echo Installation failed. Read the message above. Python must be installed.
pause
exit /b 1
