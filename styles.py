import streamlit as st


def apply_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Kufi+Arabic:wght@400;500;600;700;800&display=swap');
        :root{
          --bg:#f4f6f9;--surface:#ffffff;--surface-soft:#f8fafc;--ink:#172033;--muted:#667085;
          --line:#e4e7ec;--blue:#1769e0;--blue-soft:#eaf2ff;--green:#14804a;--green-soft:#e8f7ef;
          --orange:#b54708;--orange-soft:#fff2e5;--red:#b42318;--red-soft:#fff0ef;--purple:#6941c6;
          --shadow:0 10px 30px rgba(16,24,40,.06);--shadow-strong:0 18px 50px rgba(16,24,40,.10);
        }
        html,body,[class*="css"]{font-family:'Inter','Noto Kufi Arabic',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;color:var(--ink)}
        .stApp{background:linear-gradient(180deg,#f7f9fc 0,#f4f6f9 100%)}
        .block-container{max-width:1540px;padding-top:.65rem;padding-bottom:5rem}
        [data-testid="stSidebar"]{background:#fff;border-right:1px solid var(--line)}
        [data-testid="stSidebar"] .stButton>button{text-align:left;justify-content:flex-start;border:0;box-shadow:none;background:transparent;color:var(--ink)}
        [data-testid="stSidebar"] .stButton>button[kind="primary"]{background:var(--blue-soft);color:#0b4aa2;border:1px solid #cfe0ff}
        [data-testid="stSidebar"] .stButton>button:hover{background:#f2f4f7;transform:none;box-shadow:none}

        .app-shell-header{position:sticky;top:.25rem;z-index:700;display:flex;justify-content:space-between;align-items:center;background:rgba(255,255,255,.94);backdrop-filter:blur(18px);border:1px solid var(--line);border-radius:18px;padding:11px 14px;margin-bottom:10px;box-shadow:0 5px 20px rgba(16,24,40,.06)}
        .brand-lockup{display:flex;align-items:center;gap:10px}.brand-mark{width:38px;height:38px;border-radius:12px;background:linear-gradient(145deg,#1d75ef,#0e4ea6);display:flex;align-items:center;justify-content:center;color:white;font-weight:800;font-size:20px;box-shadow:0 8px 18px rgba(23,105,224,.24)}
        .brand-title{font-size:15px;font-weight:800;letter-spacing:-.02em}.brand-subtitle{font-size:11px;color:var(--muted);margin-top:2px}.user-chip{display:flex;align-items:center;gap:8px;border-radius:999px;background:#f2f4f7;padding:7px 10px;font-size:11px}.user-chip b{color:var(--blue)}

        .page-heading{display:flex;justify-content:space-between;align-items:flex-end;margin:18px 0 14px}.page-heading h1{font-size:30px;line-height:1.2;letter-spacing:-.04em;margin:3px 0 0}.page-heading p{margin:6px 0 0;color:var(--muted);font-size:13px}.eyebrow{font-size:10px;font-weight:800;letter-spacing:.12em;color:var(--blue)}

        .patient-context{background:#fff;border:1px solid var(--line);border-radius:20px;padding:16px 18px;margin:10px 0 16px;box-shadow:var(--shadow)}
        .sticky-patient{position:sticky;top:70px;z-index:550}.patient-main{display:flex;align-items:flex-end;gap:18px;flex-wrap:wrap}.patient-main h2{font-size:24px;margin:2px 0}.patient-identifiers{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:3px}.patient-identifiers span{background:var(--surface-soft);border:1px solid var(--line);border-radius:9px;padding:5px 8px;font-size:11px}.patient-alerts{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px}.alert{border-radius:10px;padding:8px 10px;display:flex;gap:8px;font-size:11px}.alert b{min-width:90px}.alert.allergy{background:var(--red-soft);color:#8f1f17}.alert.operation{background:var(--blue-soft);color:#0b4aa2}.patient-counters{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}.patient-counters span{font-size:10px;color:var(--muted)}.patient-counters b{color:var(--ink)}

        .work-item-card{display:grid;grid-template-columns:34px 1fr auto;gap:10px;align-items:center;background:#fff;border:1px solid var(--line);border-radius:14px;padding:11px 12px;margin:7px 0;box-shadow:0 4px 14px rgba(16,24,40,.035)}
        .work-icon{width:30px;height:30px;border-radius:9px;background:var(--blue-soft);color:var(--blue);display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800}.work-copy{display:flex;flex-direction:column;min-width:0}.work-copy b{font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.work-copy span,.work-meta{font-size:10px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.work-meta{margin-top:2px}
        .empty-state{text-align:center;background:#fff;border:1px dashed #d0d5dd;border-radius:16px;padding:24px;color:var(--muted)}.empty-state>div{font-size:26px}.empty-state h3{color:var(--ink);font-size:16px;margin:7px 0 3px}.empty-state p{font-size:11px;margin:0}

        .summary-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}.summary-grid>div{background:#fff;border:1px solid var(--line);border-radius:14px;padding:12px;display:flex;flex-direction:column}.summary-grid span{font-size:10px;color:var(--muted)}.summary-grid b{font-size:26px;line-height:1.1;margin:4px 0}.summary-grid small{color:var(--muted);font-size:9px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
        .key-value-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}.key-value-grid>div{border:1px solid var(--line);border-radius:11px;padding:8px;background:#fff}.key-value-grid span{display:block;color:var(--muted);font-size:9px}.key-value-grid b{font-size:12px}

        .workflow-stepper{display:flex;align-items:flex-start;overflow-x:auto;padding:8px 2px 12px;gap:0}.workflow-node{position:relative;min-width:96px;text-align:center;color:#98a2b3}.workflow-node:not(:last-child):after{content:'';position:absolute;height:3px;background:#e4e7ec;left:58%;right:-42%;top:15px}.workflow-node.done:not(:last-child):after{background:#47b881}.workflow-node span{position:relative;z-index:2;width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 5px;background:#f2f4f7;border:2px solid #d0d5dd;font-size:10px;font-weight:800}.workflow-node small{font-size:8px;font-weight:700;display:block;white-space:nowrap}.workflow-node.done{color:var(--green)}.workflow-node.done span{background:var(--green-soft);border-color:#47b881}.workflow-node.active{color:var(--blue)}.workflow-node.active span{background:var(--blue);border-color:var(--blue);color:#fff;box-shadow:0 0 0 5px rgba(23,105,224,.10)}

        .status,.pill{display:inline-block;border-radius:999px;padding:4px 8px;font-size:9px;font-weight:800;white-space:nowrap}.status.info,.pill.scheduled{background:var(--blue-soft);color:#0b4aa2}.status.success,.pill.postop{background:var(--green-soft);color:#067647}.status.warning,.pill.preop{background:var(--orange-soft);color:#9a3412}.status.danger,.pill.theatre{background:var(--red-soft);color:#9f1d14}.pill.discharged{background:#f2f4f7;color:#344054}
        .risk-low{color:#067647;font-weight:800}.risk-medium{color:#b54708;font-weight:800}.risk-high{color:#b42318;font-weight:800}.muted{color:var(--muted);font-size:11px}.rtl{direction:rtl;text-align:right}

        .record-card,.list-card,.timeline-row,.card{background:#fff;border:1px solid var(--line);box-shadow:0 4px 14px rgba(16,24,40,.035)}
        .card{border-radius:16px;padding:14px;margin-bottom:10px}.record-card{border-radius:14px;padding:12px 14px;margin:7px 0;display:flex;justify-content:space-between;gap:12px;align-items:center}.record-card h4{margin:.1rem 0;font-size:15px}.record-meta{text-align:right;color:var(--muted);font-size:10px}.list-card{border-radius:13px;padding:10px 12px;margin:6px 0;display:flex;justify-content:space-between;gap:10px;align-items:center}.list-card span{color:var(--muted);font-size:10px}.timeline-row{border-radius:13px;padding:10px 12px;margin:6px 0;display:grid;grid-template-columns:90px 1fr auto;gap:10px;align-items:center}.timeline-date{font-weight:700;color:var(--muted);font-size:10px}

        .calendar-header{text-align:center;font-weight:800;color:var(--muted);padding:5px 0;font-size:10px}.calendar-cell,.day-card{background:#fff;border:1px solid var(--line);border-radius:12px;padding:7px;min-height:102px;box-shadow:0 3px 10px rgba(16,24,40,.03);margin-bottom:6px}.today-cell{outline:2px solid rgba(23,105,224,.40)}.date-number{font-size:14px;font-weight:800;margin-bottom:5px}.calendar-count{border-radius:7px;padding:4px 6px;font-size:8px;font-weight:800;margin:3px 0}.clinic-count{background:#edf7ff;color:#0064d8}.theatre-count{background:#f1edff;color:#5b32c7}

        div.stButton>button,div.stDownloadButton>button{border-radius:10px;font-weight:700;min-height:38px;border:1px solid #d0d5dd;transition:.12s ease;font-size:12px}.stButton>button:hover,.stDownloadButton>button:hover{transform:translateY(-1px);box-shadow:0 5px 14px rgba(16,24,40,.08)}
        [data-testid="stMetric"]{background:#fff;border:1px solid var(--line);border-radius:14px;padding:10px 12px;box-shadow:0 4px 14px rgba(16,24,40,.035)}[data-testid="stMetricValue"]{font-weight:800;letter-spacing:-.04em;font-size:1.55rem}
        [data-baseweb="input"]>div,[data-baseweb="select"]>div,textarea{border-radius:9px!important;background:#fff!important;border-color:#d0d5dd!important}
        [data-testid="stTabs"] button{border-radius:9px!important;font-weight:700!important;font-size:11px!important}
        [data-testid="stVerticalBlockBorderWrapper"]{border-radius:14px!important;border-color:var(--line)!important;background:#fff!important}
        details{border-radius:12px!important;border:1px solid var(--line)!important;background:#fff!important}
        [data-testid="stDialog"]>div{border-radius:20px!important}
        .mobile-nav-label,div[class*="st-key-mobile_nav_"]{display:none}

        @media(max-width:1000px){.block-container{padding-left:.75rem;padding-right:.75rem}.patient-alerts{grid-template-columns:1fr}.key-value-grid{grid-template-columns:repeat(2,1fr)}.sticky-patient{position:static}.app-shell-header{position:static}.workflow-node{min-width:84px}.calendar-cell{min-height:82px}.record-meta{display:none}}
        @media(max-width:700px){
          .block-container{padding-top:.35rem}.app-shell-header{border-radius:13px;padding:8px}.brand-mark{width:33px;height:33px}.brand-title{font-size:13px}.brand-subtitle{font-size:9px}.user-chip span{display:none}
          .page-heading{margin:11px 0 8px}.page-heading h1{font-size:23px}.page-heading p{font-size:10px}.patient-context{padding:12px;border-radius:14px}.patient-main h2{font-size:19px}.patient-identifiers{gap:5px}.patient-identifiers span{font-size:9px;padding:4px 6px}.patient-alerts{grid-template-columns:1fr}.patient-counters{display:grid;grid-template-columns:1fr 1fr}
          .summary-grid{grid-template-columns:1fr 1fr}.timeline-row{grid-template-columns:72px 1fr}.timeline-row>.status{grid-column:2}.work-item-card{grid-template-columns:30px 1fr auto;padding:9px}.calendar-header{font-size:8px}.calendar-cell{min-height:63px;padding:4px}.date-number{font-size:12px}.calendar-count{font-size:7px;padding:3px}.record-card{display:block}.list-card{align-items:flex-start}.workflow-node{min-width:72px}.workflow-node small{font-size:7px}
          .mobile-nav-label{display:block;color:var(--muted);font-size:9px;margin:4px 0}.st-key-mobile_nav_اليوم_My_Worklist,.st-key-mobile_nav_ملف_المريض_Patient_chart,.st-key-mobile_nav_العيادة_Clinic,.st-key-mobile_nav_العمليات_Theatre,.st-key-mobile_nav_الردهة_Ward_board{display:block}
          div[class*="st-key-mobile_nav_"]{display:block}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(hospital_name: str, user_role: str) -> None:
    # Backward-compatible compact hero for modules that still import it.
    st.markdown(
        f"""
        <div class="app-shell-header">
          <div class="brand-lockup"><div class="brand-mark">S</div><div><div class="brand-title">SurgiScore Clinical EHR</div><div class="brand-subtitle">{hospital_name}</div></div></div>
          <div class="user-chip"><b>{user_role}</b></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
