import streamlit as st


def apply_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Kufi+Arabic:wght@400;500;600;700;800&display=swap');
        :root{
          --bg:#f5f5f7;--surface:rgba(255,255,255,.92);--surface-solid:#fff;--ink:#1d1d1f;
          --muted:#6e6e73;--line:rgba(0,0,0,.08);--blue:#0a84ff;--green:#30a46c;
          --orange:#f59e0b;--red:#e5484d;--purple:#7c5cff;--shadow:0 16px 50px rgba(0,0,0,.07);
        }
        html,body,[class*="css"]{font-family:'Inter','Noto Kufi Arabic',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;color:var(--ink)}
        .stApp{background:radial-gradient(circle at top right,#eef5ff 0,#f5f5f7 32%,#fff 100%)}
        .block-container{max-width:1420px;padding-top:1rem;padding-bottom:4rem}
        [data-testid="stSidebar"]{background:rgba(255,255,255,.88);backdrop-filter:blur(22px);border-right:1px solid var(--line)}
        [data-testid="stSidebarNav"]{padding-top:.6rem}
        .hero{background:linear-gradient(135deg,rgba(255,255,255,.98),rgba(240,247,255,.94));border:1px solid var(--line);border-radius:32px;padding:28px;box-shadow:var(--shadow);margin-bottom:18px;position:relative;overflow:hidden}
        .hero:after{content:'';position:absolute;width:220px;height:220px;border-radius:50%;background:rgba(10,132,255,.08);right:-80px;top:-100px}
        .hero h1{font-size:38px;letter-spacing:-1.4px;margin:0;color:var(--ink);position:relative;z-index:2}
        .hero p{margin:8px 0 0;color:var(--muted);direction:rtl;text-align:right;position:relative;z-index:2}
        .card,.record-card,.patient-banner,.list-card,.timeline-row{background:var(--surface);border:1px solid var(--line);box-shadow:0 8px 30px rgba(0,0,0,.045);backdrop-filter:blur(16px)}
        .card{border-radius:22px;padding:18px;margin-bottom:14px}
        .patient-banner{border-radius:26px;padding:20px;margin:12px 0 18px}.patient-banner h3{margin:.2rem 0 .8rem;font-size:28px}.patient-grid{display:grid;grid-template-columns:repeat(4,minmax(90px,1fr));gap:10px}.patient-grid span{background:#f8f8fa;border-radius:14px;padding:10px}.allergy-strip{margin-top:12px;border-radius:14px;background:#fff4f4;color:#9f1239;padding:10px 12px}
        .eyebrow{font-size:11px;font-weight:800;letter-spacing:.12em;color:var(--blue)}
        .record-card{border-radius:20px;padding:16px 18px;margin:10px 0;display:flex;justify-content:space-between;gap:18px;align-items:center}.record-card h4{margin:.2rem 0;font-size:20px}.record-meta{text-align:right;color:var(--muted);font-size:13px}
        .list-card{border-radius:18px;padding:14px 16px;margin:9px 0;display:flex;justify-content:space-between;gap:12px;align-items:center}.list-card span{color:var(--muted);font-size:13px}
        .timeline-row{border-radius:18px;padding:14px 16px;margin:8px 0;display:grid;grid-template-columns:100px 1fr auto;gap:14px;align-items:center}.timeline-date{font-weight:700;color:var(--muted);font-size:13px}
        .status,.pill{display:inline-block;border-radius:999px;padding:5px 10px;font-size:11px;font-weight:800;white-space:nowrap}.status.info,.pill.scheduled{background:#eaf3ff;color:#0057d9}.status.success,.pill.postop{background:#e8f8ef;color:#067647}.status.warning,.pill.preop{background:#fff1e7;color:#b54708}.status.danger,.pill.theatre{background:#fdecec;color:#b42318}.pill.discharged{background:#f2f4f7;color:#344054}
        .risk-low{color:#067647;font-weight:800}.risk-medium{color:#b54708;font-weight:800}.risk-high{color:#b42318;font-weight:800}.muted{color:var(--muted);font-size:13px}.rtl{direction:rtl;text-align:right}
        .calendar-header{text-align:center;font-weight:800;color:var(--muted);padding:8px 0}.calendar-cell,.day-card{background:var(--surface-solid);border:1px solid var(--line);border-radius:18px;padding:10px;min-height:132px;box-shadow:0 5px 18px rgba(0,0,0,.035);margin-bottom:8px}.today-cell{outline:2px solid rgba(10,132,255,.45)}.date-number{font-size:18px;font-weight:800;margin-bottom:8px}.calendar-count{border-radius:10px;padding:5px 8px;font-size:11px;font-weight:800;margin:4px 0}.clinic-count{background:#edf7ff;color:#0064d8}.theatre-count{background:#f1edff;color:#5b32c7}
        div.stButton>button,div.stDownloadButton>button{border-radius:14px;font-weight:700;min-height:44px;border:1px solid rgba(0,0,0,.1);transition:.15s ease}.stButton>button:hover,.stDownloadButton>button:hover{transform:translateY(-1px);box-shadow:0 8px 20px rgba(0,0,0,.08)}
        [data-testid="stMetric"]{background:var(--surface);border:1px solid var(--line);border-radius:20px;padding:14px;box-shadow:0 8px 24px rgba(0,0,0,.04)}[data-testid="stMetricValue"]{font-weight:800;letter-spacing:-.04em}
        [data-baseweb="input"]>div,[data-baseweb="select"]>div,textarea{border-radius:13px!important;background:rgba(255,255,255,.94)!important}
        [data-testid="stTabs"] button{border-radius:12px!important;font-weight:700!important}
        details{border-radius:16px!important;border:1px solid var(--line)!important;background:rgba(255,255,255,.78)!important}
        @media(max-width:900px){.block-container{padding-left:.75rem;padding-right:.75rem}.hero{padding:20px;border-radius:24px}.hero h1{font-size:29px}.patient-grid{grid-template-columns:repeat(2,1fr)}.timeline-row{grid-template-columns:78px 1fr}.timeline-row>.status{grid-column:2}.calendar-cell,.day-card{min-height:92px;padding:7px}.calendar-count{font-size:9px;padding:4px}.record-card{align-items:flex-start}.record-meta{display:none}}
        @media(max-width:560px){.patient-grid{grid-template-columns:1fr 1fr}.calendar-header{font-size:10px}.date-number{font-size:15px}.calendar-cell{min-height:72px}.calendar-cell button{padding:.2rem!important;font-size:10px!important}.hero p{font-size:13px}.record-card{display:block}.list-card{align-items:flex-start}.timeline-row{display:block}.timeline-date{margin-bottom:5px}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(hospital_name: str, user_role: str):
    st.markdown(
        f"""
        <div class="hero">
          <span class="eyebrow">SURGICAL CLINIC · THEATRE · WARD · FOLLOW-UP</span>
          <h1>🏥 SurgiScore Clinical EHR</h1>
          <p>{hospital_name} — إدارة متكاملة للمريض الجراحي من العيادة والتشخيص إلى العملية والمتابعة والوصفة</p>
          <span class="pill scheduled">Clinic</span>
          <span class="pill preop">WHO Safety</span>
          <span class="pill postop">Ward & Follow-up</span>
          <span class="pill discharged">FHIR-ready</span>
          <span class="pill scheduled">Role: {user_role}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
