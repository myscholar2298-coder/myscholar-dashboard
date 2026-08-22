import datetime
import pandas as pd
import requests
import streamlit as st

# Replace with your actual raw CSV URL on GitHub
CSV_URL = "https://raw.githubusercontent.com/myscholar2298-coder/myscholar-dashboard/main/Extract_Dispatch_Data.csv"


@st.cache_data(ttl=60)
def load_data_from_github():
  # 1. Load the actual CSV data
  df = pd.read_csv(CSV_URL)

  # 2. Fetch the exact last commit timestamp for this file from GitHub API
  api_url = "https://api.github.com/repos/myscholar2298-coder/myscholar-dashboard/commits?path=Extract_Dispatch_Data.csv&per_page=1"
  try:
    response = requests.get(api_url, timeout=5)
    if response.status_code == 200:
      commit_data = response.json()
      if commit_data and len(commit_data) > 0:
        date_str = commit_data[0]["commit"]["committer"]["date"]
        # Convert UTC string from GitHub to Malaysia Time (UTC+8)
        utc_time = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        utc_time = utc_time.replace(tzinfo=datetime.timezone.utc)
        malaysia_tz = datetime.timezone(datetime.timedelta(hours=8))
        pub_time_str = (
            utc_time.astimezone(malaysia_tz)
            .strftime("%Y-%m-%d %I:%M:%S %p MYT")
        )
      else:
        raise Exception("No commit data found")
    else:
      raise Exception("API limit or error")
  except Exception:
    # Fallback to current time if offline or API fails
    malaysia_tz = datetime.timezone(datetime.timedelta(hours=8))
    pub_time_str = (
        datetime.datetime.now(malaysia_tz)
        .strftime("%Y-%m-%d %I:%M:%S %p MYT")
    )

  return df, pub_time_str


# --- Streamlit Dashboard UI Integration Example ---
st.set_page_config(
    page_title="MyScholar Operation Matrix Dashboard", layout="wide"
)

# Load data and timestamp
df, last_updated = load_data_from_github()

# Header layout
st.title("MYSCHOLAR")
st.subheader("OPERATION MATRIX DASHBOARD")
st.markdown(f"🕒 *Data Published / Updated: {last_updated}*")

# Display your table/data components here...
st.dataframe(df)