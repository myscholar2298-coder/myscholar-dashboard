@echo off
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
"C:\Users\SERVER\AppData\Local\Python\pythoncore-3.14-64\python.exe" AutoUpdate.py >> "C:\MyScholar Script\logs\autoupdate_console.log" 2>&1 || exit /b 1
"C:\Users\SERVER\AppData\Local\Python\pythoncore-3.14-64\python.exe" backend_sync.py >> "C:\MyScholar Script\logs\autoupdate_console.log" 2>&1 || exit /b 1