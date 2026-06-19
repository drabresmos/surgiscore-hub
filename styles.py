import streamlit as st

def apply_styles():
    st.markdown('''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Noto+Kufi+Arabic:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] {font-family: 'Inter','Noto Kufi Arabic',-apple-system,BlinkMacSystemFont,sans-serif;}
    .stApp {background: linear-gradient(180deg,#F5F7FB 0%,#FFFFFF 65%);} 
    .block-container {padding-top: 1.4rem; max-width: 1180px;}
    .hero {background: linear-gradient(135deg,#ffffff 0%,#eef4ff 100%); border:1px solid #E5E7EB; border-radius:32px; padding:28px; box-shadow:0 18px 50px rgba(17,24,39,.06); margin-bottom:20px;}
    .hero-title {font-size:40px; font-weight:900; letter-spacing:-1.2px; color:#111827;}
    .hero-sub {font-size:15px;color:#667085;margin-top:8px;}
    .pill {display:inline-block;background:#EEF2FF;color:#3730A3;border-radius:999px;padding:6px 12px;font-size:12px;font-weight:800;margin-top:12px;}
    .card {background:rgba(255,255,255,.92); border:1px solid rgba(229,231,235,.95); border-radius:24px; padding:20px; box-shadow:0 12px 30px rgba(17,24,39,.055); margin-bottom:16px;}
    .mini-card {background:white;border:1px solid #EAECF0;border-radius:20px;padding:15px;box-shadow:0 8px 24px rgba(16,24,40,.04);}
    .day-card {background:white;border:1px solid #EAECF0;border-radius:18px;padding:12px;min-height:145px;box-shadow:0 6px 16px rgba(16,24,40,.035);}
    .muted {color:#667085;font-size:13px;}
    .ar {direction:rtl;text-align:right;}
    .low {color:#067647;font-weight:900;} .medium {color:#B54708;font-weight:900;} .high {color:#B42318;font-weight:900;}
    .status-scheduled {background:#EEF4FF;color:#3538CD;padding:3px 8px;border-radius:999px;font-size:11px;font-weight:800;}
    .status-preop {background:#FDF2FA;color:#C11574;padding:3px 8px;border-radius:999px;font-size:11px;font-weight:800;}
    .status-intraop {background:#FFF6ED;color:#C4320A;padding:3px 8px;border-radius:999px;font-size:11px;font-weight:800;}
    .status-postop {background:#ECFDF3;color:#027A48;padding:3px 8px;border-radius:999px;font-size:11px;font-weight:800;}
    div.stButton > button {border-radius:14px; font-weight:800; border:1px solid #D0D5DD;}
    div.stButton > button[kind="primary"] {background:#111827;color:white;}
    div.stDownloadButton > button {border-radius:14px;font-weight:800;}
    [data-testid="stMetricValue"] {font-weight:900;}
    @media (max-width: 720px) {
      .hero-title {font-size:30px;} .block-container {padding-left:0.8rem;padding-right:0.8rem;} .day-card {min-height:100px;}
    }
    </style>
    ''', unsafe_allow_html=True)

def hero():
    st.markdown('''
    <div class="hero">
      <div class="hero-title">🏥 SurgiScore Ward</div>
      <div class="hero-sub ar">نظام إدارة مرضى الجراحة: Pre-op • Intra-op • Post-op • Vitals • Wound • Scores</div>
      <span class="pill">Board-ready • Mobile/iPad friendly • Arabic UI + English terms</span>
    </div>
    ''', unsafe_allow_html=True)

def risk_label(risk: str):
    cls = {"Low":"low","Medium":"medium","High":"high"}.get(risk,"muted")
    st.markdown(f"<span class='{cls}'>Risk: {risk}</span>", unsafe_allow_html=True)
