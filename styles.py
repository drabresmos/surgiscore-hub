import streamlit as st

def apply_styles():
    st.markdown('''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] {font-family: 'Cairo', -apple-system, BlinkMacSystemFont, sans-serif;}
    .stApp {background: linear-gradient(180deg,#f5f7fb 0%,#ffffff 100%);}
    .hero {background:linear-gradient(135deg,#fff 0%,#eef4ff 100%);border:1px solid #e5e7eb;border-radius:32px;padding:26px;box-shadow:0 18px 50px rgba(0,0,0,.06);margin-bottom:22px;}
    .title {font-size:42px;font-weight:800;letter-spacing:-1px;color:#111827;}
    .subtitle {color:#6b7280;font-size:16px;}
    .pill {display:inline-block;background:#eef2ff;color:#1d4ed8;border-radius:999px;padding:6px 12px;font-weight:800;font-size:13px;margin-top:10px;}
    .card {background:rgba(255,255,255,.92);border:1px solid #e5e7eb;border-radius:24px;padding:20px;box-shadow:0 12px 34px rgba(0,0,0,.06);margin-bottom:16px;}
    .arabic {direction:rtl;text-align:right;}
    .low{color:#12805c;font-weight:800}.medium{color:#b76e00;font-weight:800}.high{color:#b42318;font-weight:800}
    div.stButton > button {border-radius:16px;background:#111827;color:white;font-weight:800;border:0;padding:.6rem 1rem;}
    div.stDownloadButton > button {border-radius:16px;font-weight:800;}
    [data-testid="stMetricValue"] {font-size:30px;font-weight:800;}
    @media (max-width: 768px) {.title{font-size:30px}.hero{padding:18px;border-radius:22px}.card{padding:14px;border-radius:18px}.block-container{padding-left:1rem;padding-right:1rem}}
    </style>
    ''', unsafe_allow_html=True)
