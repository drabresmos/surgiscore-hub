def inject_css(st):
    st.markdown('''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] {font-family: Inter, -apple-system, BlinkMacSystemFont, sans-serif;}
    .stApp {background: linear-gradient(180deg,#f5f7fb 0%,#ffffff 100%);} 
    .block-container {padding-top:1.3rem; max-width:1180px;}
    .hero {background:linear-gradient(135deg,#ffffff 0%,#eef4ff 100%); border:1px solid #e5e7eb; border-radius:30px; padding:24px; box-shadow:0 18px 50px rgba(0,0,0,.06); margin-bottom:18px;}
    .title {font-size:38px; font-weight:800; letter-spacing:-1px; color:#111827;}
    .subtitle {color:#667085; font-size:15px; margin-top:6px;}
    .pill {display:inline-block; padding:7px 12px; border-radius:999px; background:#eef2ff; color:#3730a3; font-weight:700; font-size:12px; margin-top:12px;}
    .card {background:rgba(255,255,255,.92); border:1px solid rgba(230,230,235,.95); box-shadow:0 12px 34px rgba(0,0,0,.055); border-radius:24px; padding:18px; margin-bottom:14px;}
    .calendar-day {background:#fff; border:1px solid #e7e9ee; border-radius:18px; padding:12px; min-height:135px; box-shadow:0 6px 18px rgba(0,0,0,.04);}
    .day-number {font-weight:800; font-size:18px; color:#111827;}
    .muted {color:#667085; font-size:13px;}
    .status-planned {color:#2563eb; font-weight:800;}
    .status-done {color:#12805c; font-weight:800;}
    .status-cancelled {color:#b42318; font-weight:800;}
    .risk-low {color:#12805c; font-weight:800;}
    .risk-medium {color:#b76e00; font-weight:800;}
    .risk-high {color:#b42318; font-weight:800;}
    div.stButton > button {border-radius:15px; border:1px solid #d1d5db; background:#111827; color:white; font-weight:800; padding:.62rem 1rem;}
    div.stDownloadButton > button {border-radius:15px; font-weight:800;}
    [data-testid="stMetricValue"] {font-size:28px; font-weight:800;}
    @media (max-width: 768px){.title{font-size:30px}.hero{padding:18px}.calendar-day{min-height:auto}}
    </style>
    ''', unsafe_allow_html=True)
