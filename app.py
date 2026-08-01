import streamlit as st
import pandas as pd
import base64
import urllib.request
import datetime

# 1. Page Configuration optimized for mobile viewport
st.set_page_config(
    page_title="MyScholar Operation Dashboard",
    page_icon="📦",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for compact header, side-by-side logo/title, and clean 3x4 route button matrix with full counts
st.markdown("""
    <style>
    .main .block-container {
        padding-top: 0.8rem !important;
        padding-bottom: 1rem !important;
    }
    div.stSelectbox > div > div { background-color: #f8f9fa; }
    thead tr th { text-align: center !important; }
    tbody tr td { text-align: center !important; }
    .stDataFrame { text-align: center; }
    
    /* Force Header to Stay Side-by-Side on Mobile */
    .header-flex {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 2px;
    }
    .header-logo img {
        width: 75px !important;
        max-width: 75px !important;
    }
    .header-text h2 {
        margin: 0 !important;
        font-size: 24px !important;
        font-weight: 800 !important;
        letter-spacing: 0.5px !important;
        line-height: 1.1 !important;
    }
    .header-text p {
        margin: 0 !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        color: #333 !important;
    }
    .sync-timestamp {
        font-size: 11px;
        color: #666;
        margin-bottom: 10px;
        font-style: italic;
    }

    /* Clean 3x4 Route Button Grid */
    .route-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
        margin-bottom: 15px;
    }
    .route-btn {
        background-color: #f0f2f6;
        border: 1px solid #d6d9dc;
        border-radius: 6px;
        padding: 8px 4px;
        text-align: center;
        text-decoration: none;
        color: #262730;
        display: block;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .route-btn:hover {
        background-color: #e0e2e6;
        color: #000;
    }
    .route-btn.active {
        background-color: #ff4b4b;
        color: white;
        border-color: #ff4b4b;
    }
    .route-title {
        font-size: 15px;
        font-weight: bold;
        line-height: 1.2;
    }
    .route-sub {
        font-size: 10px;
        margin-top: 3px;
        opacity: 0.9;
        line-height: 1.3;
    }
    .route-btn.active .route-sub {
        opacity: 0.95;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# HEADER: SIDE-BY-SIDE MOBILE FLEX CONTAINER
# ==========================================
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return ""

img_base64 = get_base64_image("logo.png")
logo_html = f"<img src='data:image/png;base64,{img_base64}' style='width: 75px;'/>" if img_base64 else "📦"

st.markdown(f"""
    <div class='header-flex'>
        <div class='header-logo'>{logo_html}</div>
        <div class='header-text'>
            <h2>MYSCHOLAR</h2>
            <p>OPERATION MATRIX DASHBOARD</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# DIRECT GOOGLE DRIVE CSV CLOUD LOADER & TIMESTAMP (Malaysia Time)
# ==========================================
@st.cache_data(ttl=300)
def load_data_from_sheet():
    file_id = "1gbAnm1xYavKT53Rao3zXXUSQG4Fgy2yu"
    csv_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    
    pub_time_str = "Live Sync Active"
    try:
        req = urllib.request.Request(csv_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            last_mod = response.headers.get('Last-Modified')
            if last_mod:
                dt_utc = datetime.datetime.strptime(last_mod, '%a, %d %b %Y %H:%M:%S %Z')
                dt_malaysia = dt_utc + datetime.timedelta(hours=8)
                pub_time_str = dt_malaysia.strftime('%Y-%m-%d %H:%M:%S MYT')
    except:
        malaysia_tz = datetime.timezone(datetime.timedelta(hours=8))
        pub_time_str = datetime.datetime.now(malaysia_tz).strftime('%Y-%m-%d %H:%M:%S MYT')

    df = pd.read_csv(csv_url)
    return df, pub_time_str

try:
    with st.spinner("Syncing live data from cloud..."):
        df, published_time = load_data_from_sheet()

    st.markdown(f"<div class='sync-timestamp'>🕒 Data Published / Updated: <b>{published_time}</b></div>", unsafe_allow_html=True)
    st.divider()

    # Clean up column names safely
    df.columns = df.columns.str.strip()
    
    if "School Name" in df.columns:
        df = df[df["School Name"] != "School Name"]
    
    if len(df) > 136:
        df = df.iloc[0:136]

    if '\\#Delivery' in df.columns:
        df = df.rename(columns={'\\#Delivery': '#Delivery'})

    expected_cols = ["Group", "Date", "School Name", "Teacher", "Task", "Route", "Remark", "Title/Panitia", "Sample", "Qty", "#Delivery"]
    for col in expected_cols:
        if col not in df.columns:
            df[col] = ""
        else:
            df[col] = df[col].fillna("").astype(str)

    def format_qty(val):
        try:
            if pd.isna(val) or str(val).strip() == "" or str(val).lower() == "nan":
                return "0"
            return str(int(float(val)))
        except:
            return str(val)

    df["Sample"] = df["Sample"].apply(format_qty)
    df["Qty"] = df["Qty"].apply(format_qty)

    # ==========================================
    # NAVIGATION MENU (Pages)
    # ==========================================
    page_mode = st.radio(
        "Select View Page:",
        options=["🏠 Main Dashboard", "💳 Cheque Details", "📋 Panitia Details"],
        horizontal=True,
        label_visibility="collapsed"
    )
    st.divider()

    valid_df = df[df["School Name"].str.strip() != ""].copy()
    
    def is_panitia_row(title, task):
        if str(task).strip().lower() == "cheque":
            return False
        t_str = str(title).strip()
        if "_" in t_str or "." in t_str:
            return False
        panitia_subjects = ['PSV', 'SJH', '3DP', 'SAINS', 'KIMIA', 'MUET', 'RBT', 'GKT', 'SRT']
        return t_str.upper() in panitia_subjects

    valid_df["Is_Panitia"] = valid_df.apply(lambda row: is_panitia_row(row["Title/Panitia"], row["Task"]), axis=1)
    
    cheque_mask = valid_df["Task"].str.strip().str.lower() == "cheque"
    panitia_mask = valid_df["Is_Panitia"]
    stpm_mask = ~panitia_mask & ~cheque_mask & (valid_df["Title/Panitia"].str.strip() != "")

    # ==========================================
    # PAGE 1: MAIN DASHBOARD
    # ==========================================
    if page_mode == "🏠 Main Dashboard":
        st.subheader("📊 Overview Summary")

        exclude_no_stock = st.checkbox("🚫 Exclude 'No Sample' / 'No Stock'", value=True)
        exclude_pending = st.checkbox("🚫 Exclude 'Pending' Tasks", value=True)
        
        filtered_df = df.copy()
        if exclude_no_stock:
            filtered_df = filtered_df[~filtered_df["Remark"].str.lower().str.contains("no sample|no stock", na=False)]
        if exclude_pending:
            filtered_df = filtered_df[filtered_df["Task"].str.strip().str.lower() != "pending"]

        f_valid_df = filtered_df[filtered_df["School Name"].str.strip() != ""].copy()
        f_valid_df["Is_Panitia"] = f_valid_df.apply(lambda row: is_panitia_row(row["Title/Panitia"], row["Task"]), axis=1)

        f_cheque_mask = f_valid_df["Task"].str.strip().str.lower() == "cheque"
        f_panitia_mask = f_valid_df["Is_Panitia"]
        f_stpm_mask = ~f_panitia_mask & ~f_cheque_mask & (f_valid_df["Title/Panitia"].str.strip() != "")

        total_schools_visit = f_valid_df["School Name"].nunique()
        cheque_schools_count = f_valid_df[f_cheque_mask]["School Name"].nunique()
        
        valid_teachers = f_valid_df[(f_valid_df["Teacher"].str.strip() != "") & (f_valid_df["Teacher"].str.strip() != "Pjbt")]
        stpm_teachers_count = valid_teachers[f_stpm_mask[valid_teachers.index]]["Teacher"].nunique()
        panitia_teachers_count = valid_teachers[f_panitia_mask[valid_teachers.index]]["Teacher"].nunique()

        summary_data = {
            "Total Schools": [total_schools_visit],
            "Cheques": [cheque_schools_count],
            "STPM": [stpm_teachers_count],
            "Panitia": [panitia_teachers_count]
        }
        summary_df = pd.DataFrame(summary_data)

        st.dataframe(
            summary_df,
            use_container_width=True,
            hide_index=True
        )

        st.divider()
        st.info(f"💡 Active records: **{len(filtered_df)}** across all routes.")
        st.divider()

        # ==========================================
        # INFORMATIVE 3x4 ROUTE MATRIX WITH SCHOOLS, TEACHERS & CHEQUES
        # ==========================================
        st.subheader("🛣️ Route Breakdown & Task Inspector")
        
        if "selected_route" not in st.session_state:
            st.session_state.selected_route = "A"

        query_params = st.query_params
        if "route" in query_params:
            r_val = query_params["route"]
            if r_val in ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]:
                st.session_state.selected_route = r_val

        routes = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]

        grid_html = "<div class='route-grid'>"
        for r in routes:
            active_class = "active" if st.session_state.selected_route == r else ""
            
            # Calculate counts for this route from filtered dataset
            r_sub_df = filtered_df[filtered_df["Route"].str.upper().str.startswith(r)]
            r_sch_count = r_sub_df[r_sub_df["School Name"].str.strip() != ""]["School Name"].nunique()
            r_tch_count = r_sub_df[(r_sub_df["Teacher"].str.strip() != "") & (r_sub_df["Teacher"].str.strip() != "Pjbt")]["Teacher"].nunique()
            r_chq_count = r_sub_df[r_sub_df["Task"].str.strip().str.lower() == "cheque"].shape[0]
            
            title_prefix = "⭐ " if active_class else ""
            grid_html += f"""
                <a href='?route={r}' target='_self' class='route-btn {active_class}'>
                    <div class='route-title'>{title_prefix}Route {r}</div>
                    <div class='route-sub'>🏫 {r_sch_count} &nbsp;|&nbsp; 👨‍🏫 {r_tch_count}<br>💳 {r_chq_count} Cheques</div>
                </a>
            """
        grid_html += "</div>"

        st.markdown(grid_html, unsafe_allow_html=True)

        selected_route = st.session_state.selected_route
        route_df = filtered_df[filtered_df["Route"].str.upper().str.startswith(selected_route.upper())].reset_index(drop=True)

        r_schools = route_df[route_df["School Name"].str.strip() != ""]["School Name"].nunique()
        r_teachers = route_df[route_df["Teacher"].str.strip() != ""]["Teacher"].nunique()
        r_cheques = route_df[route_df["Task"].str.strip().str.lower() == "cheque"].shape[0]

        st.markdown(f"### Route {selected_route} Summary")
        st.info(f"🏫 Schools: **{r_schools}** | 👨‍🏫 Teachers: **{r_teachers}** | 💳 Cheques: **{r_cheques}** | 📋 Tasks: **{len(route_df)}**")

        if not route_df.empty:
            st.write(f"**Task List (Route {selected_route})** — *Click any row below to view details:*")
            
            display_list = route_df[["School Name", "Teacher", "Title/Panitia", "Task"]]

            def highlight_full_row(row):
                task_val = str(row["Task"]).strip().lower()
                if "delivery" in task_val:
                    return ['background-color: #d1e7dd; color: #0f5132'] * len(row)
                elif "cheque" in task_val:
                    return ['background-color: #fff3cd; color: #664d03'] * len(row)
                elif "payment" in task_val:
                    return ['background-color: #e2d9f3; color: #3b1f6e'] * len(row)
                elif "return" in task_val:
                    return ['background-color: #cfe2ff; color: #084298'] * len(row)
                else:
                    return ['background-color: #f8f9fa; color: #383d41'] * len(row)

            styled_table = display_list.style.apply(highlight_full_row, axis=1)

            event = st.dataframe(
                styled_table, 
                use_container_width=True, 
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row",
                key=f"table_route_{selected_route}"
            )

            st.divider()

            st.subheader("🔍 Individual Task Details")
            selected_rows = event.selection.rows if event and event.selection else []
            task_detail = route_df.iloc[selected_rows[0]] if selected_rows else route_df.iloc[0]

            task_type = task_detail['Task'].strip()
            badge_style = "background-color: #d1e7dd; color: #0f5132; padding: 2px 8px; border-radius: 4px; font-weight: bold;" if task_type.lower() == "delivery" else ("background-color: #fff3cd; color: #664d03; padding: 2px 8px; border-radius: 4px; font-weight: bold;" if task_type.lower() == "cheque" else ("background-color: #e2d9f3; color: #3b1f6e; padding: 2px 8px; border-radius: 4px; font-weight: bold;" if task_type.lower() == "payment" else "background-color: #cfe2ff; color: #084298; padding: 2px 8px; border-radius: 4px; font-weight: bold;"))

            with st.container(border=True):
                st.markdown(f"### 🏢 {task_detail['School Name']}")
                st.markdown(f"**Route:** {task_detail['Route']}  |  **Task Type:** <span style='{badge_style}'>{task_type}</span>", unsafe_allow_html=True)
                st.markdown(f"**Teacher/Contact:** {task_detail['Teacher'] if task_detail['Teacher'] else 'N/A'}")
                st.markdown(f"**Book / Panitia:** {task_detail['Title/Panitia']}")
                
                col_a, col_b = st.columns(2)
                col_a.metric("Sample Qty", task_detail['Sample'])
                col_b.metric("Actual Qty", task_detail['Qty'])
                
                if task_detail['Remark']:
                    st.warning(f"📝 **Remark:** {task_detail['Remark']}")
                else:
                    st.success("📝 **Remark:** None")
        else:
            st.warning(f"No records found for Route {selected_route}.")

    # ==========================================
    # PAGE 2: CHEQUE DETAILS REVIEW (Sorted & Deduplicated)
    # ==========================================
    elif page_mode == "💳 Cheque Details":
        st.subheader("💳 Cheque Collection Tasks Review")
        
        cheque_df = valid_df[cheque_mask].copy()
        cheque_df = cheque_df.drop_duplicates(subset=["Date", "School Name", "Teacher", "Route", "Remark"])
        cheque_df = cheque_df.sort_values(by="Date", na_position="last").reset_index(drop=True)
        
        st.info(f"Total Cheque Collection Tasks: **{len(cheque_df)}** across **{cheque_df['School Name'].nunique()}** schools.")

        if not cheque_df.empty:
            cheque_display = cheque_df[["Date", "School Name", "Teacher", "Route", "Remark"]]
            st.dataframe(cheque_display, use_container_width=True, hide_index=True)
        else:
            st.success("No cheque tasks found.")

    # ==========================================
    # PAGE 3: PANITIA DETAILS REVIEW (Deduplicated, School Name instead of Route Alphabet)
    # ==========================================
    elif page_mode == "📋 Panitia Details":
        st.subheader("📋 Panitia Order Overview")
        
        panitia_df = valid_df[panitia_mask].copy()
        
        pending_df = panitia_df[panitia_df["Task"].astype(str).str.strip().str.lower() == "pending"].drop_duplicates(subset=["Date", "School Name", "Teacher", "Title/Panitia", "#Delivery", "Remark"])
        pending_df = pending_df.sort_values(by="Date", na_position="last").reset_index(drop=True)
        
        other_df = panitia_df[panitia_df["Task"].astype(str).str.strip().str.lower() != "pending"].drop_duplicates(subset=["Date", "School Name", "Teacher", "Title/Panitia", "Task", "#Delivery", "Remark"])
        other_df = other_df.sort_values(by="Date", na_position="last").reset_index(drop=True)

        st.info(f"Total Unique Panitia Tasks: **{len(pending_df) + len(other_df)}** (Pending: **{len(pending_df)}** | Other: **{len(other_df)}**)")

        # Section A: Pending Tasks
        st.markdown("### ⏳ Order Pending Incoming Items")
        if not pending_df.empty:
            pending_display = pending_df[["Date", "School Name", "Teacher", "Title/Panitia", "#Delivery", "Remark"]]
            pending_display.columns = ["Date", "School Name", "Teacher", "Panitia", "#Delivery", "Remark"]
            st.dataframe(pending_display, use_container_width=True, hide_index=True)
        else:
            st.success("No pending Panitia tasks.")

        st.divider()

        # Section B: Other Panitia Tasks
        st.markdown("### ✅ Outstanding Operation Assignment")
        if not other_df.empty:
            other_display = other_df[["Date", "School Name", "Teacher", "Title/Panitia", "Task", "#Delivery", "Remark"]]
            other_display.columns = ["Date", "School Name", "Teacher", "Panitia", "Task", "#Delivery", "Remark"]
            
            p_event = st.dataframe(
                other_display, 
                use_container_width=True, 
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row",
                key="table_panitia_other"
            )

            st.divider()
            st.subheader("🔍 Panitia Task Detail Box")

            p_selected_rows = p_event.selection.rows if p_event and p_event.selection else []
            p_task_detail = other_df.iloc[p_selected_rows[0]] if p_selected_rows else other_df.iloc[0]

            p_task_type = p_task_detail['Task'].strip()
            p_badge_style = "background-color: #d1e7dd; color: #0f5132; padding: 2px 8px; border-radius: 4px; font-weight: bold;" if p_task_type.lower() == "delivery" else "background-color: #cfe2ff; color: #084298; padding: 2px 8px; border-radius: 4px; font-weight: bold;"

            with st.container(border=True):
                st.markdown(f"### 🏫 Route {p_task_detail['Route']} Task")
                st.markdown(f"**Task Type:** <span style='{p_badge_style}'>{p_task_type}</span>", unsafe_allow_html=True)
                st.markdown(f"**Teacher/Contact:** {p_task_detail['Teacher'] if p_task_detail['Teacher'] else 'N/A'}")
                st.markdown(f"**Book / Panitia:** {p_task_detail['Title/Panitia']}")
                
                col_a, col_b = st.columns(2)
                col_a.metric("Sample Qty", p_task_detail['Sample'])
                col_b.metric("Actual Qty", p_task_detail['Qty'])
                
                if p_task_detail['Remark']:
                    st.warning(f"📝 **Remark:** {p_task_detail['Remark']}")
                else:
                    st.success("📝 **Remark:** None")
        else:
            st.success("No other Panitia tasks found.")

except Exception as e:
    st.error(f"Error loading dashboard data: {e}")