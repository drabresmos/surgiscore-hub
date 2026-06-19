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
from auth import can, get_user_context, render_user_sidebar
from clinic_pages import (
    page_clinic,
    page_command_center,
    page_followups,
    page_investigations,
    page_patients,
    page_prescriptions,
    page_tasks,
)
from database import init_db
from styles import apply_styles, hero


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

hero(hospital_name, user.role)
render_user_sidebar(user)

PAGES = {
    "الرئيسية Command center": page_command_center,
    "المرضى Patient record": page_patients,
    "العيادة Clinic": page_clinic,
    "الوصفات Prescribing": page_prescriptions,
    "الطلبات والنتائج Investigations": page_investigations,
    "المتابعة Follow-up": page_followups,
    "المهام Tasks": page_tasks,
    "تقويم العمليات Theatre calendar": page_calendar,
    "إضافة عملية New operation": page_new_case,
    "لوحة الردهات Ward board": page_ward_board,
    "مسار العملية Surgical journey": page_patient_journey,
    "السكورات Score library": page_score_library,
    "الجودة Quality": page_quality,
    "المعايير Standards": page_governance,
}
if can(user, "admin"):
    PAGES["الإدارة Admin"] = page_admin

selected = st.sidebar.radio("Navigation / التنقل", list(PAGES.keys()))

st.sidebar.divider()
st.sidebar.caption("SurgiScore Clinical EHR v9.0 — clinic, theatre, ward and follow-up pilot")
st.sidebar.caption("Clinical pilot: local policies and formal governance remain mandatory.")

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
