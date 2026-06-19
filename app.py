from __future__ import annotations

import os

import streamlit as st

from app_pages import (
    page_admin,
    page_calendar,
    page_governance,
    page_new_case,
    page_patient_journey,
    page_quality,
    page_score_library,
    page_ward_board,
)
from auth import can, get_user_context
from clinic_pages import page_clinic, page_followups, page_prescriptions, page_tasks
from database import init_db
from navigation import (
    ADMIN,
    CLINIC,
    FOLLOWUP,
    NEW_OPERATION,
    PATIENTS as LEGACY_PATIENTS,
    PRESCRIBING,
    QUALITY,
    RESULTS,
    SCORES,
    STANDARDS,
    SURGICAL_JOURNEY,
    TASKS,
    THEATRE,
    TODAY as LEGACY_TODAY,
    WARD as LEGACY_WARD,
)
from styles import apply_styles
from v11_pages import page_more, page_patients, page_surgery, page_today, page_ward
from v11_routes import MORE, PATIENTS, SURGERY, TODAY, WARD, close_legacy
from v11_shell import render_desktop_navigation, render_mobile_navigation, render_topbar
from v11_styles import apply_v11_styles
from workflow_pages import page_patient_chart, page_results_workspace, page_today_worklist


st.set_page_config(
    page_title="SurgiScore Clinical Workspace",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_styles()
apply_v11_styles()

try:
    init_db()
except Exception as exc:
    st.error("تعذر تهيئة قاعدة البيانات / Database initialization failed")
    st.exception(exc)
    st.stop()

user = get_user_context()

try:
    hospital_name = str(st.secrets.get("HOSPITAL_NAME", "Surgical Department Pilot"))
except Exception:
    hospital_name = os.getenv("HOSPITAL_NAME", "Surgical Department Pilot")

render_topbar(hospital_name, user)
current_section = render_desktop_navigation(user)

MAIN_PAGE_FUNCS = {
    TODAY: page_today,
    PATIENTS: page_patients,
    SURGERY: page_surgery,
    WARD: page_ward,
    MORE: page_more,
}

LEGACY_PAGE_FUNCS = {
    LEGACY_TODAY: page_today_worklist,
    LEGACY_PATIENTS: page_patient_chart,
    CLINIC: page_clinic,
    RESULTS: page_results_workspace,
    PRESCRIBING: page_prescriptions,
    FOLLOWUP: page_followups,
    TASKS: page_tasks,
    THEATRE: page_calendar,
    NEW_OPERATION: page_new_case,
    LEGACY_WARD: page_ward_board,
    SURGICAL_JOURNEY: page_patient_journey,
    SCORES: page_score_library,
    QUALITY: page_quality,
    STANDARDS: page_governance,
}
if can(user, "admin"):
    LEGACY_PAGE_FUNCS[ADMIN] = page_admin

if not user.clinical_mode:
    st.caption("⚠ Demo mode — لا تُدخل بيانات مرضى حقيقية. Production use requires institutional authentication and managed infrastructure.")

if st.session_state.get("v11_legacy_mode"):
    route = st.session_state.get("nav_page")
    back_col, title_col = st.columns([1, 5])
    if back_col.button("← رجوع", width="stretch", key="v11_exit_legacy"):
        close_legacy()
    title_col.caption("Advanced workspace · مساحة متقدمة")
    page_fn = LEGACY_PAGE_FUNCS.get(route)
    if page_fn:
        page_fn(user)
    else:
        st.error("The requested module is unavailable.")
        if st.button("Return to main workspace"):
            close_legacy()
else:
    MAIN_PAGE_FUNCS[current_section](user)

render_mobile_navigation(current_section)

st.markdown("<div class='v11-bottom-space'></div>", unsafe_allow_html=True)
st.caption(
    "Clinical documentation and decision support only. Treatment, prescribing and escalation remain the responsibility of an authorized clinician under local policy."
)
