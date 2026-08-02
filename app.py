# ==========================================
        # TRUE 2x6 MOBILE / 3x4 DESKTOP GRID
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

        # Loop in pairs of 2 so mobile perfectly forms a clean 2x6 grid
        for i in range(0, len(routes), 2):
            col1, col2 = st.columns(2)
            row_routes = [routes[i], routes[i+1] if i+1 < len(routes) else None]
            
            for idx, r in enumerate(row_routes):
                if r is not None:
                    r_sub_df = filtered_df[filtered_df["Route"].str.upper().str.startswith(r)]
                    r_sch_count = r_sub_df[r_sub_df["School Name"].str.strip() != ""]["School Name"].nunique()
                    r_tch_count = r_sub_df[(r_sub_df["Teacher"].str.strip() != "") & (r_sub_df["Teacher"].str.strip() != "Pjbt")]["Teacher"].nunique()
                    r_chq_count = r_sub_df[r_sub_df["Task"].str.strip().str.lower() == "cheque"].shape[0]
                    
                    is_selected = (st.session_state.selected_route == r)
                    btn_label = f"{r} | 🏫{r_sch_count} 👨‍🏫{r_tch_count} 💳{r_chq_count}"
                    
                    target_col = [col1, col2][idx]
                    with target_col:
                        if st.button(btn_label, key=f"btn_route_{r}", use_container_width=True, type="primary" if is_selected else "secondary"):
                            st.session_state.selected_route = r
                            st.rerun()