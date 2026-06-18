import streamlit as st

APPLE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] {font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;}
.stApp {background: linear-gradient(180deg,#f5f7fb 0%,#ffffff 100%); color:#111827;}
.block-container {padding-top: 1.6rem; max-width: 1280px;}
.hero {background:linear-gradient(135deg,#fff 0%,#eef4ff 100%);border-radius:32px;padding:30px;border:1px solid #e5e7eb;box-shadow:0 18px 50px rgba(0,0,0,.06);margin-bottom:22px;}
.title {font-size:42px;font-weight:800;letter-spacing:-1.2px;color:#111827;}
.subtitle {color:#6b7280;font-size:16px;margin-top:4px;}
.apple-card {background:rgba(255,255,255,.92);border:1px solid rgba(230,230,235,.95);box-shadow:0 12px 34px rgba(0,0,0,.06);border-radius:26px;padding:22px;margin-bottom:16px;}
.small-muted {color:#6b7280;font-size:13px;}
.risk-low {color:#12805c;font-weight:800}.risk-medium {color:#b76e00;font-weight:800}.risk-high {color:#b42318;font-weight:800}
div.stButton > button {border-radius:16px;border:1px solid #d1d5db;background:#111827;color:white;font-weight:700;padding:.65rem 1rem;}
div.stDownloadButton > button {border-radius:16px;font-weight:700;}
[data-testid="stMetricValue"] {font-size:30px;font-weight:800;}
[data-testid="stSidebar"] {background:#fbfbfd;}
</style>
"""

def apply_style():
    st.markdown(APPLE_CSS, unsafe_allow_html=True)

def hero():
    st.markdown('''<div class="hero"><div class="title">🏥 SurgiScore Hub</div><div class="subtitle">Apple-style surgical scoring platform for general surgery</div></div>''', unsafe_allow_html=True)

def risk_badge(risk: str):
    css = {"Low":"risk-low","Medium":"risk-medium","High":"risk-high"}.get(risk, "")
    st.markdown(f"<span class='{css}'>Risk: {risk}</span>", unsafe_allow_html=True)
