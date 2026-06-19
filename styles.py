import streamlit as st

def apply_styles():
    st.markdown('''
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"]{font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;}
.stApp{background:linear-gradient(180deg,#f5f7fb 0%,#ffffff 70%);} 
.block-container{padding-top:1.4rem;max-width:1180px;}
.hero{background:linear-gradient(135deg,#fff 0%,#eef4ff 100%);border:1px solid #e5e7eb;border-radius:32px;padding:28px;margin-bottom:22px;box-shadow:0 18px 50px rgba(0,0,0,.06)}
.title{font-size:42px;font-weight:800;letter-spacing:-1.2px;color:#111827;line-height:1.05}.subtitle{color:#6b7280;font-size:16px;margin-top:8px}.pill{display:inline-block;background:#eef2ff;color:#3730a3;border-radius:999px;padding:6px 12px;font-size:13px;font-weight:700;margin-top:10px}
.card{background:rgba(255,255,255,.92);border:1px solid rgba(230,230,235,.95);box-shadow:0 12px 34px rgba(0,0,0,.055);border-radius:26px;padding:20px;margin-bottom:16px}.soft{background:#f8fafc;border-radius:18px;padding:14px;border:1px solid #e5e7eb}.risk-low{color:#12805c;font-weight:800}.risk-medium{color:#b76e00;font-weight:800}.risk-high{color:#b42318;font-weight:800}.muted{color:#6b7280}.small{font-size:13px;color:#6b7280}
div.stButton > button{border-radius:16px;border:1px solid #d1d5db;background:#111827;color:white;font-weight:700;padding:.62rem 1rem} div.stDownloadButton > button{border-radius:16px;font-weight:700} [data-testid="stMetricValue"]{font-size:30px;font-weight:800}
@media(max-width:700px){.title{font-size:30px}.hero{padding:20px;border-radius:24px}.card{padding:16px;border-radius:22px}.block-container{padding-left:1rem;padding-right:1rem}}
</style>
''', unsafe_allow_html=True)

def risk_badge(risk):
    cls={'Low':'risk-low','Medium':'risk-medium','High':'risk-high'}.get(risk,'muted')
    st.markdown(f"<span class='{cls}'>Risk: {risk}</span>", unsafe_allow_html=True)

def hero():
    st.markdown('''<div class="hero"><div class="title">🏥 SurgiScore Hub</div><div class="subtitle">Board-ready surgical scoring platform for mobile, iPad, and desktop use.</div><span class="pill">General Surgery • Emergency • HPB • Trauma • Post-op</span></div>''', unsafe_allow_html=True)
