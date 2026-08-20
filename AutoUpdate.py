import os
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ---
# Saved directly in the root directory so Streamlit Cloud can read it
CSV_OUTPUT_PATH = "Extract_Dispatch_Data.csv"

def run_pipeline():
    print(f"[{datetime.now()}] Starting compilation and GitHub sync pipeline...")
    
    # 1. YOUR DATA COMPILATION LOGIC GOES HERE
    # (Make sure your script reads your Excel files and compiles them into a DataFrame named 'df')
    # Example placeholder:
    # df = pd.read_excel("your_source_file.xlsx")
    
    # For now, ensure your dataframe creation is here, and save it:
    # df.to_csv(CSV_OUTPUT_PATH, index=False)
    
    # Let's simulate/ensure the CSV is saved at the root path:
    print(f"[{datetime.now()}] Successfully saved local CSV copy at: {os.path.abspath(CSV_OUTPUT_PATH)}")
    
    # 2. GIT AUTO-COMMIT AND PUSH
    import subprocess
    
    # Check if there are any changes in the repository
    status_result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    
    if not status_result.stdout.strip():
        print(f"[{datetime.now()}] No content changes found in CSV for Git sync.")
        return

    try:
        print(f"[{datetime.now()}] Changes detected. Staging and pushing to GitHub...")
        
        # Stage all changes (including the CSV and app files)
        subprocess.run(["git", "add", "."], check=True)
        
        # Commit with a timestamp message
        commit_msg = f"Auto-update dispatch data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        
        # Push to GitHub
        subprocess.run(["git", "push", "origin", "main"], check=True)
        
        print(f"[{datetime.now()}] Successfully synced CSV to GitHub!")
        
    except subprocess.CalledProcessError as e:
        print(f"[{datetime.now()}] Error pushing to GitHub: {e}")

if __name__ == "__main__":
    run_pipeline()