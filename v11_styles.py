from __future__ import annotations

import streamlit as st


def apply_v11_styles() -> None:
    st.markdown(
        """
        <style>
        :root{
          --v11-blue:#1769e0;--v11-blue-soft:#eaf2ff;--v11-ink:#172033;--v11-muted:#667085;
          --v11-line:#e5e7eb;--v11-bg:#f5f7fa;--v11-surface:#ffffff;--v11-danger:#b42318;
          --v11-warning:#b54708;--v11-success:#067647;
        }
        .stApp{background:var(--v11-bg)}
        .block-container{max-width:1440px;padding-top:.45rem;padding-bottom:5.5rem}
        [data-testid="stSidebar"]{min-width:220px!important;max-width:220px!important;background:#fff}
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p{font-size:11px}
        .v11-topbar{position:sticky;top:.2rem;z-index:800;display:flex;align-items:center;justify-content:space-between;
          gap:10px;background:rgba(255,255,255,.96);backdrop-filter:blur(16px);border:1px solid var(--v11-line);
          border-radius:14px;padding:8px 11px;margin-bottom:8px;box-shadow:0 4px 18px rgba(16,24,40,.05)}
        .v11-brand{display:flex;align-items:center;gap:9px;min-width:200px}.v11-logo{width:34px;height:34px;border-radius:10px;
          display:flex;align-items:center;justify-content:center;background:var(--v11-blue);color:#fff;font-weight:800}
        .v11-brand b{font-size:13px}.v11-brand small{display:block;color:var(--v11-muted);font-size:9px;margin-top:1px}
        .v11-user{font-size:10px;color:var(--v11-muted);white-space:nowrap}.v11-user b{color:var(--v11-blue)}
        .v11-title{margin:12px 0 10px}.v11-title h1{font-size:25px;letter-spacing:-.035em;margin:0}.v11-title p{font-size:11px;color:var(--v11-muted);margin:3px 0 0}
        .v11-section-label{font-size:10px;color:var(--v11-muted);font-weight:800;letter-spacing:.08em;text-transform:uppercase;margin:14px 0 5px}
        .v11-kpi{background:#fff;border:1px solid var(--v11-line);border-radius:13px;padding:11px 12px;min-height:82px}
        .v11-kpi span{font-size:9px;color:var(--v11-muted);display:block}.v11-kpi b{font-size:24px;line-height:1.15;display:block;margin:4px 0}.v11-kpi small{font-size:9px;color:var(--v11-muted)}
        .v11-row{display:grid;grid-template-columns:34px minmax(0,1fr) auto;align-items:center;gap:9px;background:#fff;
          border:1px solid var(--v11-line);border-radius:12px;padding:9px 10px;margin:5px 0}
        .v11-row-icon{width:30px;height:30px;border-radius:9px;background:var(--v11-blue-soft);color:var(--v11-blue);
          display:flex;align-items:center;justify-content:center;font-weight:800;font-size:11px}
        .v11-row-copy{min-width:0}.v11-row-copy b{font-size:12px;display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
        .v11-row-copy span{font-size:9px;color:var(--v11-muted);display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:2px}
        .v11-row-meta{font-size:9px;color:var(--v11-muted);text-align:right;white-space:nowrap}
        .v11-card{background:#fff;border:1px solid var(--v11-line);border-radius:14px;padding:12px;margin:6px 0}
        .v11-card h3{font-size:14px;margin:0 0 7px}.v11-card p{font-size:10px;color:var(--v11-muted);margin:3px 0}
        .v11-patient-list{max-height:68vh;overflow:auto;padding-right:3px}
        .v11-alert{border-left:3px solid var(--v11-warning);background:#fff8ed;border-radius:8px;padding:8px 10px;font-size:10px;margin:5px 0}
        .v11-alert.danger{border-left-color:var(--v11-danger);background:#fff1f0}.v11-alert.success{border-left-color:var(--v11-success);background:#ecfdf3}
        .v11-plan-item{display:flex;align-items:flex-start;gap:8px;border-bottom:1px solid #f0f1f3;padding:7px 0;font-size:10px}
        .v11-plan-item:last-child{border-bottom:0}.v11-plan-dot{width:18px;height:18px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:#f2f4f7;color:#667085;font-size:8px;flex:0 0 18px}
        .v11-plan-dot.done{background:#dcfae6;color:#067647}.v11-plan-dot.due{background:#fff0e0;color:#b54708}
        .v11-op-header{background:#fff;border:1px solid var(--v11-line);border-radius:14px;padding:12px 14px;margin-bottom:8px}
        .v11-op-header h2{font-size:19px;margin:0 0 3px}.v11-op-header p{font-size:10px;color:var(--v11-muted);margin:0}
        .v11-stage-panel{background:#fff;border:1px solid var(--v11-line);border-radius:14px;padding:13px;margin-top:8px}
        .v11-stage-panel h3{font-size:14px;margin:0 0 6px}.v11-stage-panel p{font-size:10px;color:var(--v11-muted)}
        .v11-ward-header,.v11-ward-row{display:grid;grid-template-columns:58px minmax(150px,1.5fr) 48px 58px 58px 78px 64px;gap:6px;align-items:center}
        .v11-ward-header{font-size:9px;color:var(--v11-muted);font-weight:700;padding:4px 8px}.v11-ward-row{background:#fff;border:1px solid var(--v11-line);border-radius:11px;padding:8px;margin:5px 0;font-size:10px}
        .v11-ward-row b{font-size:11px}.v11-news{display:inline-flex;min-width:28px;height:25px;border-radius:8px;align-items:center;justify-content:center;font-weight:800;background:#eaf2ff;color:#1769e0}
        .v11-news.high{background:#fff0ef;color:#b42318}.v11-news.mid{background:#fff4e5;color:#b54708}
        .v11-more-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin-top:8px}.v11-more-card{background:#fff;border:1px solid var(--v11-line);border-radius:13px;padding:12px}.v11-more-card b{font-size:12px}.v11-more-card p{font-size:9px;color:var(--v11-muted);margin:5px 0 0}
        .v11-bottom-space{height:48px}.v11-mobile-nav{display:none}
        .st-key-v11_mobile_nav{display:none}
        div.stButton>button{min-height:38px;border-radius:9px;font-size:11px}
        [data-testid="stTabs"] button{font-size:10px!important;min-height:38px!important}
        [data-testid="stMetric"]{box-shadow:none!important}
        .v11-compact-banner .patient-context{position:static!important;margin:4px 0 9px!important;padding:11px 13px!important;border-radius:13px!important;box-shadow:none!important}
        .v11-compact-banner .patient-main h2{font-size:19px!important}.v11-compact-banner .patient-alerts{margin-top:6px!important}.v11-compact-banner .patient-counters{margin-top:6px!important}

        @media(max-width:850px){
          [data-testid="stSidebar"]{display:none}.block-container{padding-left:.55rem;padding-right:.55rem;padding-bottom:6.2rem}
          .v11-topbar{position:static;border-radius:11px}.v11-brand{min-width:auto}.v11-user{display:none}.v11-title h1{font-size:22px}
          .v11-more-grid{grid-template-columns:1fr 1fr}.v11-ward-header{display:none}.v11-ward-row{grid-template-columns:52px minmax(0,1fr) 44px 54px;gap:5px}.v11-ward-row .ward-hide-mobile{display:none}
          .v11-mobile-nav{display:block;position:fixed;left:0;right:0;bottom:0;z-index:1100;background:rgba(255,255,255,.98);border-top:1px solid var(--v11-line);padding:5px 7px calc(5px + env(safe-area-inset-bottom));box-shadow:0 -5px 20px rgba(16,24,40,.08)}
          .st-key-v11_mobile_nav{display:block;position:fixed;left:0;right:0;bottom:0;z-index:1100;background:rgba(255,255,255,.98);border-top:1px solid var(--v11-line);padding:5px 7px calc(5px + env(safe-area-inset-bottom));box-shadow:0 -5px 20px rgba(16,24,40,.08)}
          .st-key-v11_mobile_nav [data-testid="stHorizontalBlock"]{gap:4px!important}.st-key-v11_mobile_nav button{min-height:48px!important;padding:4px 2px!important;font-size:9px!important;white-space:pre-line!important}
          .v11-mobile-nav-inner{display:grid;grid-template-columns:repeat(5,1fr);gap:4px}.v11-mobile-item{text-align:center;font-size:9px;color:#667085}.v11-mobile-item b{display:block;font-size:14px;color:#344054;line-height:1.1}.v11-mobile-item.active{color:#1769e0;font-weight:800}.v11-mobile-item.active b{color:#1769e0}
          .v11-patient-list{max-height:none}.v11-row-meta{display:none}
        }
        @media(max-width:520px){.v11-more-grid{grid-template-columns:1fr}.v11-kpi b{font-size:21px}.v11-card{padding:10px}.v11-topbar{padding:7px}.v11-logo{width:31px;height:31px}.v11-brand small{display:none}}
        </style>
        """,
        unsafe_allow_html=True,
    )

# End of v11 style module.
