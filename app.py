import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="MYSCHOLAR Operation Matrix Dashboard",
    page_icon="📊",
    layout="wide"
)

# ==========================================
# LOAD DATA DIRECTLY FROM GITHUB RAW URL (Auto-Syncs)
# ==========================================
CSV_URL = "https://raw.githubusercontent.com/myscholar2298-coder/myscholar-dashboard/main/Extract_Dispatch_Data.csv"

@st.cache_data(ttl=60)  # Automatically checks for fresh data from GitHub every 60 seconds
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        return df
    except Exception as e:
        st.error(f"Error loading data from GitHub: {e}")
        return pd.DataFrame()

df = load_data()

# ==========================================
# APP HEADER & TIMESTAMP
# ==========================================
st.title("MYSCHOLAR")
st.subheader("OPERATION MATRIX DASHBOARD")

current_time_str = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p MYT")
st.markdown(f"🕒 *Data Published / Updated: {current_time_str}*")
st.markdown("---")

# ==========================================
# NAVIGATION / TABS
# ==========================================
tab_selection = st.radio(
    "Navigation", 
    ["🏠 Main Dashboard", "💳 Cheque Details", "📋 Panitia Details"], 
    horizontal=True
)

st.markdown("---")

# ==========================================
# OVERVIEW SUMMARY SECTION
# ==========================================
st.markdown("### 📊 Overview Summary")

col_filter1, col_filter2 = st.columns(2)
with col_filter1:
    exclude_no_sample_stock = st.checkbox("Exclude 'No Sample' / 'No Stock'", value=True)
with col_filter2:
    exclude_pending = st.checkbox("Exclude 'Pending' Tasks", value=True)

filtered_df = df.copy()
if not filtered_df.empty:
    if exclude_no_sample_stock and "Remark" in filtered_df.columns:
        filtered_df = filtered_df[~filtered_df["Remark"].str.contains("NO SAMPLE|NO STOCK", case=False, na=False)]
    if exclude_pending and "Task" in filtered_df.columns:
        filtered_df = filtered_df[~filtered_df["Task"].str.contains("Pending", case=False, na=False)]

    total_schools = filtered_df["School Name"].nunique() if "School Name" in filtered_df.columns else 0
    
    cheques_count = 0
    if "Task" in filtered_df.columns:
        cheques_count = len(filtered_df[filtered_df["Task"].str.contains("Cheque", case=False, na=False)])
    
    stpm_count = 0
    if "Title/Panitia" in filtered_df.columns:
        stpm_count = len(filtered_df[filtered_df["Title/Panitia"].str.contains("STPM", case=False, na=False)])
        
    panitia_count = filtered_df["Title/Panitia"].nunique() if "Title/Panitia" in filtered_df.columns else 0

    summary_data = {
        "Total Schools": [total_schools],
        "Cheques": [cheques_count],
        "STPM": [stpm_count],
        "Panitia": [panitia_count]
    }
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, hide_index=True)

    st.info(f"💡 Active records: {len(filtered_df)} across all routes.")

else:
    st.warning("No data found in the CSV file.")

# ==========================================
# DETAILED SECTIONS BASED ON TABS
# ==========================================
if tab_selection == "💳 Cheque Details":
    st.markdown("### Cheque Records")
    if not df.empty and "Task" in df.columns:
        cheque_df = df[df["Task"].str.contains("Cheque", case=False, na=False)]
        st.dataframe(cheque_df, use_container_width=True)
    else:
        st.write("No cheque records available.")

elif tab_selection == "📋 Panitia Details":
    st.markdown("### Panitia Breakdown")
    if not df.empty:
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.write("No records available.")