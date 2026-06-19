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
from app_shell import (
    render_global_toolbar,
    render_mobile_quick_navigation,
    render_sidebar_navigation,
)
from auth import can, get_user_context, render_user_sidebar
from clinic_pages import page_clinic, page_followups, page_prescriptions, page_tasks
from database import init_db
from navigation import (
    ADMIN,
    CLINIC,
    FOLLOWUP,
    NEW_OPERATION,
    PATIENTS,
    PRESCRIBING,
    QUALITY,
    RESULTS,
    ROLE_HOME,
    SCORES,
    STANDARDS,
    SURGICAL_JOURNEY,
    TASKS,
    THEATRE,
    TODAY,
    WARD,
)
from styles import apply_styles
from workflow_pages import page_patient_chart, page_results_workspace, page_today_worklist


st.set_page_config(
    page_title="SurgiScore Clinical EHR",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_styles()

try:
    init_db()
except Exception as exc:
    st.error("تعذر تهيئة قاعدة البيانات Database initialization failed")
    st.exception(exc)
    st.stop()

user = get_user_context()

try:
    hospital_name = str(st.secrets.get("HOSPITAL_NAME", "Surgical Department Pilot"))
except Exception:
    hospital_name = os.getenv("HOSPITAL_NAME", "Surgical Department Pilot")

render_global_toolbar(hospital_name, user)
render_user_sidebar(user)

PAGES = {
    TODAY: page_today_worklist,
    PATIENTS: page_patient_chart,
    CLINIC: page_clinic,
    RESULTS: page_results_workspace,
    PRESCRIBING: page_prescriptions,
    FOLLOWUP: page_followups,
    TASKS: page_tasks,
    THEATRE: page_calendar,
    NEW_OPERATION: page_new_case,
    WARD: page_ward_board,
    SURGICAL_JOURNEY: page_patient_journey,
    SCORES: page_score_library,
    QUALITY: page_quality,
    STANDARDS: page_governance,
}

# Role-aware visibility. Detailed record permissions remain enforced inside each page.
if user.role in {"nurse", "viewer"}:
    PAGES.pop(NEW_OPERATION, None)
if user.role not in {"admin", "consultant", "resident"}:
    PAGES.pop(PRESCRIBING, None)
if can(user, "admin"):
    PAGES[ADMIN] = page_admin

if "nav_page" not in st.session_state:
    st.session_state["nav_page"] = ROLE_HOME.get(user.role, TODAY)

selected = render_sidebar_navigation(user, set(PAGES.keys()))
render_mobile_quick_navigation(set(PAGES.keys()))

st.sidebar.divider()
st.sidebar.caption("SurgiScore Clinical EHR v10.0 — workflow-centred pilot")
st.sidebar.caption("Clinic · Theatre · Ward · Results · Follow-up")

if not user.clinical_mode:
    st.warning(
        "نسخة تجريبية Demo mode: لا تُدخل بيانات مرضى حقيقية. "
        "الاستخدام السريري يتطلب تسجيل دخول مؤسسي، PostgreSQL مُداراً، تخزيناً خاصاً للمرفقات، نسخاً احتياطية، مراجعة دوائية، واعتماداً سريرياً وأمنياً."
    )

PAGES[selected](user)

st.divider()
st.caption(
    "Clinical documentation and decision support only. Prescribing, escalation and treatment remain the responsibility of an authorized clinician under local policy."
)
