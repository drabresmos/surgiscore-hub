def inject_styles(st):
    st.markdown('''
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
html, body, [class*="css"] {font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;}
.stApp {background: linear-gradient(180deg,#f5f7fb 0%,#ffffff 65%);}
.block-container {padding-top: 1.2rem; max-width: 1250px;}
.hero {background: linear-gradient(135deg,#ffffff 0%,#eef4ff 100%); border:1px solid #e5e7eb; box-shadow:0 18px 55px rgba(17,24,39,.08); border-radius:32px; padding:28px 30px; margin-bottom:20px;}
.title {font-size:42px; font-weight:900; letter-spacing:-1.4px; color:#111827;}
.subtitle {color:#667085; font-size:15px; margin-top:7px;}
.pill {display:inline-block; padding:6px 12px; border-radius:999px; background:#eef2ff; color:#3730a3; font-weight:800; font-size:12px; margin-top:12px;}
.apple-card {background:rgba(255,255,255,.94); border:1px solid rgba(229,231,235,.95); box-shadow:0 12px 34px rgba(17,24,39,.055); border-radius:24px; padding:18px 20px; margin-bottom:14px;}
.day-card {background:#fff; border:1px solid #e5e7eb; border-radius:18px; padding:12px; min-height:122px; box-shadow:0 8px 24px rgba(17,24,39,.04);}
.day-muted {background:#f8fafc; color:#98a2b3;}
.day-number {font-weight:900; font-size:18px; color:#111827;}
.status-badge {border-radius:999px; padding:3px 8px; font-size:11px; font-weight:800; display:inline-block; margin:2px 2px 0 0;}
.status-planned {background:#eef2ff; color:#3730a3;}
.status-done {background:#ecfdf3; color:#027a48;}
.status-cancelled {background:#fff1f3; color:#c01048;}
.status-delayed {background:#fffaeb; color:#b54708;}
.risk-low {color:#027a48; font-weight:900;}
.risk-medium {color:#b54708; font-weight:900;}
.risk-high {color:#b42318; font-weight:900;}
div.stButton > button {border-radius:15px; border:1px solid #d0d5dd; background:#111827; color:white; font-weight:800; padding:.55rem .9rem;}
div.stDownloadButton > button {border-radius:15px; font-weight:800;}
[data-testid="stMetricValue"] {font-size:28px; font-weight:900;}
section[data-testid="stSidebar"] {background:#f8fafc; border-right:1px solid #e5e7eb;}
@media (max-width: 768px){.title{font-size:30px}.hero{padding:20px;border-radius:24px}.day-card{min-height:100px}.block-container{padding-left:.75rem;padding-right:.75rem}}
</style>
''', unsafe_allow_html=True)
