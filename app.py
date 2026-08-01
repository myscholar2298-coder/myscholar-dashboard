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

    /* FORCE 3-COLUMN GRID ON MOBILE PHONES */
    @media (max-width: 768px) {
        [data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            gap: 4px !important;
        }
        [data-testid="stHorizontalBlock"] > [data-testid="column"] {
            width: 33.333% !important;
            flex: 1 1 33.333% !important;
            min-width: 0 !important;
        }
        /* Compact button font size for mobile grid fitting */
        button[kind="secondary"], button[kind="primary"] {
            font-size: 10px !important;
            padding: 4px 1px !important;
        }
    }
    </style>
""", unsafe_allow_html=True)