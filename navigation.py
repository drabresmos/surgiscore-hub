from __future__ import annotations

import streamlit as st

TODAY = "اليوم My Worklist"
PATIENTS = "ملف المريض Patient chart"
CLINIC = "العيادة Clinic"
RESULTS = "الطلبات والنتائج Orders & results"
PRESCRIBING = "الوصفات Medications"
FOLLOWUP = "المتابعة Follow-up"
TASKS = "المهام Tasks"
THEATRE = "العمليات Theatre"
NEW_OPERATION = "إضافة عملية New operation"
WARD = "الردهة Ward board"
SURGICAL_JOURNEY = "مسار العملية Surgical journey"
SCORES = "السكورات Score library"
QUALITY = "الجودة Quality"
STANDARDS = "المعايير Standards"
ADMIN = "الإدارة Admin"

PRIMARY_PAGES = [TODAY, PATIENTS, CLINIC, THEATRE, WARD]

NAV_GROUPS = {
    "Workspace / مساحة العمل": [TODAY, PATIENTS, TASKS],
    "Clinic / العيادة": [CLINIC, RESULTS, PRESCRIBING, FOLLOWUP],
    "Surgery / الجراحة": [THEATRE, NEW_OPERATION, WARD, SURGICAL_JOURNEY],
    "Clinical tools / أدوات": [SCORES, QUALITY, STANDARDS],
}

ROLE_HOME = {
    "admin": TODAY,
    "consultant": TODAY,
    "resident": TODAY,
    "nurse": WARD,
    "viewer": TODAY,
}


def navigate(page: str, *, patient_id: int | None = None, operation_id: int | None = None) -> None:
    st.session_state["nav_page"] = page
    if patient_id is not None:
        st.session_state["selected_patient_id"] = int(patient_id)
    if operation_id is not None:
        st.session_state["selected_operation_id"] = int(operation_id)
    st.rerun()
