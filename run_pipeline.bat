@echo off
C:
cd /d "H:\My Drive\Coding Script\Streamlit"

REM 1. Run Python compilation script
python AutoUpdate.py

REM 2. Pull remote changes first to prevent rejections
git reset --hard HEAD
git pull origin main --no-rebase

echo === Committing & Pushing to GitHub ===
git add Extract_Dispatch_Data.csv
git commit -m "Automated dispatch CSV update"
git push origin main

exit