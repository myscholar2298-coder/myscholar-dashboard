"""
AutoUpdate_AR.py - Receivables CSV feed for MOC.
Writes AROutstanding.csv + ARPayments.csv (from the ProductMaster Sheet tabs
that bridge_sync maintains) and payments.csv (straight from AutoCount SQL,
replacing the manual ReceivePayment.xlsx export). Then pushes to GitHub.
Run AFTER bridge_sync. Requires token.json beside this script (or in
C:\\MyScholar Script).
"""
import pickle
import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
GIT_NAME = "myscholar2298-coder"
GIT_EMAIL = "myscholar2298@gmail.com"
SHEET_ID = "1Y-n-EW5dsm9QKGFEE--AKocfxLn_9RxMzvylfugJ1ps"
SQL_SERVER = r"(local)\A2006"
SQL_DB = "AED_AED_0"


def run_git(args, check=True):
    r = subprocess.run(["git"] + args, capture_output=True)
    if check and r.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed (exit {r.returncode}):\n"
            f"{r.stderr.decode(errors='replace')}"
        )
    return r


def ensure_git_identity():
    name = run_git(["config", "--get", "user.name"], check=False)
    email = run_git(["config", "--get", "user.email"], check=False)
    if not name.stdout.strip() or not email.stdout.strip():
        run_git(["config", "user.name", GIT_NAME])
        run_git(["config", "user.email", GIT_EMAIL])


def push_files(commit_msg, paths):
    os.chdir(BASE_DIR)
    ensure_git_identity()
    run_git(["add"] + list(paths))
    if run_git(["diff", "--cached", "--quiet"], check=False).returncode == 0:
        print(f"[{datetime.now()}] No staged changes; nothing to commit.")
        return False
    run_git(["commit", "-m", commit_msg])
    try:
        run_git(["pull", "--rebase", "--autostash", "-X", "theirs", "origin", "main"])
    except RuntimeError:
        run_git(["rebase", "--abort"], check=False)
        raise
    run_git(["push", "origin", "main"])
    return True


def gs_client():
    import gspread
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    for tok in [BASE_DIR / "token.json", Path(r"C:\MyScholar\ProductSystem\token.json")]:
        if tok.exists():
            creds = pickle.loads(tok.read_bytes())
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                tok.write_bytes(pickle.dumps(creds))
            return gspread.authorize(creds)
    raise SystemExit("token.json not found - copy it from C:\\MyScholar Script")


def main():
    ss = gs_client().open_by_key(SHEET_ID)
    inv = pd.DataFrame(ss.worksheet("AROutstanding").get_all_records())
    pay = pd.DataFrame(ss.worksheet("ARPayments").get_all_records())
    inv.to_csv(BASE_DIR / "AROutstanding.csv", index=False, encoding="utf-8-sig")
    pay.to_csv(BASE_DIR / "ARPayments.csv", index=False, encoding="utf-8-sig")
    print(f"[{datetime.now()}] AROutstanding: {len(inv)} rows | ARPayments: {len(pay)} rows")

    # payments.csv from AutoCount ARPayment - replaces the manual export.
    # Column layout mirrors the old ReceivePayment.xlsx so MOC Module 2 needs
    # NO code change - dates are written ISO so the app's year filter sees them.
    import pyodbc
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SQL_SERVER};"
        f"DATABASE={SQL_DB};Trusted_Connection=yes;", timeout=30)
    rows = conn.cursor().execute("""
        SELECT p.DocNo, p.DocDate, COALESCE(p.DocNo2,''), p.DebtorCode,
               COALESCE(d.CompanyName,''), COALESCE(p.Description,''),
               p.PaymentAmt, p.LocalUnappliedAmount
        FROM ARPayment p
        LEFT JOIN Debtor d ON d.AccNo = p.DebtorCode
        WHERE p.Cancelled = 'F'
          AND p.DocDate >= DATEADD(month, -12, CAST(GETDATE() AS date))
        ORDER BY p.DocDate DESC
    """).fetchall()
    conn.close()
    payments = pd.DataFrame(
        [tuple(r) for r in rows],
        columns=["OR No.", "Date", "2nd Receipt No.", "Debtor", "Company Name",
                 "Description", "Amount", "Unapplied Amount"])
    payments["Date"] = pd.to_datetime(payments["Date"]).dt.strftime("%Y-%m-%d")
    payments.to_csv(BASE_DIR / "payments.csv", index=False, encoding="utf-8-sig")
    print(f"[{datetime.now()}] payments.csv: {len(payments)} receipts (12 months)")

    commit_msg = (f"AR + payments sync at "
                  f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    pushed = push_files(commit_msg, ["AROutstanding.csv", "ARPayments.csv", "payments.csv"])
    print(f"[{datetime.now()}] {'Pushed to GitHub.' if pushed else 'Nothing new to push.'}")


if __name__ == "__main__":
    print("Running AR CSV sync...")
    main()
    print("Done.")
    sys.exit(0)