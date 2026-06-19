from __future__ import annotations

from datetime import date, time
from html import escape
from typing import Any

import streamlit as st

from auth import UserContext, can
from clinic_catalog import APPOINTMENT_STATUSES, APPOINTMENT_TYPES
from database import (
    create_appointment,
    create_patient_task,
    get_or_create_patient,
    list_patients,
    search_records,
)
from navigation import NEW_OPERATION
from v11_routes import (
    MAIN_SECTIONS,
    MORE,
    PATIENTS,
    SECTION_EN,
    SECTION_ICONS,
    SURGERY,
    TODAY,
    WARD,
    open_legacy,
    set_section,
)


def _h(value: Any) -> str:
    return escape(str(value if value not in (None, "") else "—"))


def _patient_labels() -> dict[str, int]:
    patients = list_patients()
    return {f"{p['mrn']} · {p['full_name']}": int(p["id"]) for p in patients}


@st.dialog("إجراء جديد / Quick add", width="large")
def quick_add_dialog(user: UserContext) -> None:
    if not can(user, "write"):
        st.info("الحساب للقراءة فقط / Read-only account")
        return

    action = st.segmented_control(
        "نوع الإجراء",
        ["مريض", "موعد", "مهمة", "عملية"],
        default="موعد",
        key="v11_quick_add_action",
    )

    if action == "مريض":
        with st.form("v11_quick_patient", clear_on_submit=True):
            c1, c2 = st.columns(2)
            mrn = c1.text_input("MRN / رقم الملف")
            full_name = c1.text_input("اسم المريض / Patient name")
            age = int(c1.number_input("العمر / Age", 0, 120, 30))
            sex = c1.selectbox("الجنس / Sex", ["Male", "Female", "Other/Unknown"])
            phone = c2.text_input("الهاتف / Phone")
            blood_group = c2.selectbox("فصيلة الدم / Blood group", ["", "O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
            allergy_status = c2.selectbox(
                "Allergy status",
                ["Unknown", "No known allergies", "Allergy recorded"],
            )
            allergy_note = c2.text_input(
                "Allergy / الحساسية",
                disabled=allergy_status != "Allergy recorded",
            )
            submitted = st.form_submit_button("حفظ وفتح الملف", type="primary")
            if submitted:
                if not mrn.strip() or not full_name.strip():
                    st.error("MRN واسم المريض مطلوبان.")
                else:
                    patient = get_or_create_patient(
                        {
                            "mrn": mrn.strip(),
                            "full_name": full_name.strip(),
                            "age": age,
                            "sex": sex,
                            "phone": phone or None,
                            "blood_group": blood_group or None,
                            "allergies": (
                                "No known allergies"
                                if allergy_status == "No known allergies"
                                else allergy_note or "Allergy status unknown"
                            ),
                        },
                        user.email,
                    )
                    st.session_state["selected_patient_id"] = int(patient.id)
                    st.session_state["v11_section"] = PATIENTS
                    st.success("تم حفظ المريض.")
                    st.rerun()

    elif action == "موعد":
        labels = _patient_labels()
        if not labels:
            st.warning("أضف مريضاً أولاً.")
            return
        with st.form("v11_quick_appointment", clear_on_submit=True):
            c1, c2 = st.columns(2)
            selected = c1.selectbox("المريض / Patient", list(labels.keys()))
            appointment_date = c1.date_input("التاريخ / Date", date.today())
            start_time = c1.time_input("الوقت / Time", time(9, 0))
            appointment_type = c1.selectbox("نوع الموعد / Type", APPOINTMENT_TYPES)
            clinician = c2.text_input("الطبيب / Clinician", user.name)
            location = c2.text_input("العيادة أو الغرفة / Location")
            status = c2.selectbox("الحالة / Status", APPOINTMENT_STATUSES)
            reason = c2.text_area("سبب الزيارة / Reason")
            if st.form_submit_button("حفظ الموعد", type="primary"):
                create_appointment(
                    {
                        "patient_id": labels[selected],
                        "appointment_date": appointment_date,
                        "start_time": start_time,
                        "appointment_type": appointment_type,
                        "status": status,
                        "clinician": clinician,
                        "location": location or None,
                        "reason": reason or None,
                    },
                    user.email,
                )
                st.success("تم إنشاء الموعد.")
                st.rerun()

    elif action == "مهمة":
        labels = _patient_labels()
        if not labels:
            st.warning("أضف مريضاً أولاً.")
            return
        with st.form("v11_quick_task", clear_on_submit=True):
            selected = st.selectbox("المريض / Patient", list(labels.keys()))
            title = st.text_input("المهمة / Task")
            c1, c2, c3 = st.columns(3)
            category = c1.selectbox("الفئة", ["Results", "Follow-up", "Medication", "Pre-op", "Pathology", "Wound", "Other"])
            due_date = c2.date_input("Due date", date.today())
            priority = c3.selectbox("Priority", ["Routine", "Urgent", "Critical"])
            assigned_to = st.text_input("Assigned to", user.name)
            notes = st.text_area("Notes")
            if st.form_submit_button("إنشاء المهمة", type="primary"):
                if not title.strip():
                    st.error("عنوان المهمة مطلوب.")
                else:
                    create_patient_task(
                        {
                            "patient_id": labels[selected],
                            "title": title.strip(),
                            "category": category,
                            "due_date": due_date,
                            "priority": priority,
                            "status": "Open",
                            "assigned_to": assigned_to,
                            "notes": notes or None,
                        },
                        user.email,
                    )
                    st.success("تم إنشاء المهمة.")
                    st.rerun()

    else:
        st.markdown("### إنشاء Surgical case")
        st.caption("يفتح نموذج العملية الكامل للحفاظ على توثيق التحضير والتخدير وWHO Checklist والسكورات.")
        if st.button("فتح نموذج العملية", type="primary", width="stretch"):
            open_legacy(NEW_OPERATION, return_section=SURGERY)


def render_topbar(hospital_name: str, user: UserContext) -> None:
    st.markdown(
        f"""
        <div class="v11-topbar">
          <div class="v11-brand">
            <div class="v11-logo">S</div>
            <div><b>SurgiScore</b><small>{_h(hospital_name)}</small></div>
          </div>
          <div class="v11-user">{_h(user.name)} · <b>{_h(user.role)}</b></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    search_col, action_col = st.columns([8, 2])
    query = search_col.text_input(
        "بحث شامل",
        placeholder="ابحث بالاسم، MRN، الهاتف، العملية أو النتيجة…",
        label_visibility="collapsed",
        key="v11_global_search",
    )
    if action_col.button("＋ إجراء جديد", type="primary", width="stretch", key="v11_quick_add"):
        quick_add_dialog(user)

    if query and len(query.strip()) >= 2:
        results = search_records(query.strip(), limit=7)
        total = sum(len(group) for group in results.values())
        with st.container(border=True):
            c1, c2 = st.columns([7, 1])
            c1.caption(f"نتائج البحث / Search results · {total}")
            if c2.button("إغلاق", key="v11_close_search"):
                st.session_state["v11_global_search"] = ""
                st.rerun()
            if total == 0:
                st.info("لا توجد نتائج مطابقة.")
            for patient in results.get("patients", []):
                a, b = st.columns([6, 1])
                a.markdown(f"**{_h(patient['full_name'])}** · {_h(patient['mrn'])} · {_h(patient.get('phone') or 'No phone')}")
                if b.button("فتح", key=f"v11_search_patient_{patient['id']}"):
                    set_section(PATIENTS, patient_id=int(patient["id"]))
            for operation in results.get("operations", []):
                a, b = st.columns([6, 1])
                a.markdown(
                    f"**{_h(operation['patient_name'])}** · {_h(operation['operation_name'])} · "
                    f"{_h(operation['operation_date'])} · {_h(operation['status'])}"
                )
                if b.button("فتح", key=f"v11_search_operation_{operation['id']}"):
                    set_section(SURGERY, patient_id=int(operation["patient_id"]), operation_id=int(operation["id"]))
            for appointment in results.get("appointments", []):
                a, b = st.columns([6, 1])
                a.markdown(
                    f"**{_h(appointment['patient_name'])}** · {_h(appointment['appointment_type'])} · "
                    f"{_h(appointment['appointment_date'])} {_h(appointment['start_time'])}"
                )
                if b.button("فتح", key=f"v11_search_appointment_{appointment['id']}"):
                    set_section(PATIENTS, patient_id=int(appointment["patient_id"]))


def render_desktop_navigation(user: UserContext) -> str:
    current = st.session_state.get("v11_section", TODAY)
    if current not in MAIN_SECTIONS:
        current = TODAY
        st.session_state["v11_section"] = current

    st.sidebar.markdown("### SurgiScore")
    st.sidebar.caption("Clinical workspace")
    for section in MAIN_SECTIONS:
        label = f"{SECTION_ICONS[section]}  {section} · {SECTION_EN[section]}"
        if st.sidebar.button(
            label,
            key=f"v11_sidebar_{section}",
            width="stretch",
            type="primary" if section == current else "secondary",
        ):
            set_section(section)
    st.sidebar.divider()
    st.sidebar.caption(f"{user.name} · {user.role}")
    if user.clinical_mode and user.authenticated:
        st.sidebar.button("Log out", on_click=st.logout, width="stretch")
    else:
        st.sidebar.warning("Demo mode — لا تستخدم بيانات مرضى حقيقية")
    return current


def render_mobile_navigation(current: str) -> None:
    # Streamlit buttons are used instead of static HTML so navigation remains accessible.
    with st.container(key="v11_mobile_nav"):
        cols = st.columns(5, gap="small")
        for col, section in zip(cols, MAIN_SECTIONS):
            label = f"{SECTION_ICONS[section]}\n{SECTION_EN[section]}"
            if col.button(
                label,
                key=f"v11_mobile_{section}",
                width="stretch",
                type="primary" if section == current else "secondary",
            ):
                set_section(section)
