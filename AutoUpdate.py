import os
import subprocess
import pandas as pd
from datetime import datetime

# ==========================================
# CONFIGURATION & PATHS (Google Shared Drive)
# ==========================================
EXCEL_PATH = r"H:\Shared drives\OPERATION\Delivery Plan\LOTask.xlsx"
CSV_OUTPUT_PATH = "Extract_Dispatch_Data.csv"

def compile_excel_to_csv():
    print(f"[{datetime.now()}] Starting compilation and GitHub sync pipeline...")
    
    if not os.path.exists(EXCEL_PATH):
        print(f"Error: Could not find source Excel file at {EXCEL_PATH}")
        return False

    try:
        # Read the Excel file from your Google Shared Drive path
        df = pd.read_excel(EXCEL_PATH, sheet_name=0)
        
        # Save out to CSV locally in your script repository directory
        df.to_csv(CSV_OUTPUT_PATH, index=False)
        print(f"Successfully saved local CSV copy at: {os.path.abspath(CSV_OUTPUT_PATH)}")
        return True
    except Exception as e:
        print(f"Error reading Excel or writing CSV: {e}")
        return False

def git_auto_sync():
    try:
        # Check if there are changes to the CSV or repository
        status_result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True)
        
        if not status_result.stdout.strip():
            print(f"[{datetime.now()}] No content changes found in CSV for Git sync.")
            return

        # Stage the updated CSV file
        subprocess.run(["git", "add", CSV_OUTPUT_PATH], check=True)
        
        # Commit with dynamic timestamp
        commit_message = f"Auto-update operation data: {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        # Push to GitHub
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print(f"[{datetime.now()}] Successfully pushed fresh data to GitHub!")
        
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")

if __name__ == "__main__":
    success = compile_excel_to_csv()
    if success:
        git_auto_sync()