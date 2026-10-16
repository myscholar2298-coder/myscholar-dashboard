@echo off
REM MyScholar AR refresh - pinned script, folder and interpreter. Do not hand-edit.
cd /d "C:\MyScholar\OperationCenter"
"C:\Users\SERVER\AppData\Local\Python\pythoncore-3.14-64\python.exe" AutoUpdate_AR.py >> "logs\ar_refresh.log" 2>&1
