from __future__ import annotations

from datetime import date, time
from html import escape
from typing import Callable

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
from navigation import (
    ADMIN,
    CLINIC,
    NAV_GROUPS,
    NEW_OPERATION,
    PATIENTS,
    PRIMARY_PAGES,
    TASKS,
    THEATRE,
    TODAY,
    WARD,
    navigate,
)
from ui_components import compact_app_header, status_badge


def _h(value) -> str:
    return escape(str(value if value not in (None, "") else "—"))


def _patient_labels() -> tuple[list[dict], dict[str, int]]:
    patients = list_patients()
    return patients, {f"{x['mrn']} · {x['full_name']}": int(x["id"]) for x in patients}


@st.dialog("إضافة سريعة Quick add", width="large")
def quick_add_dialog(user: UserContext) -> None:
    if not can(user, "write"):
        st.info("This account is read-only.")
        return
    action = st.segmented_control(
        "Action",
        ["Patient", "Appointment", "Task", "Operation"],
        default="Appointment",
        key="quick_add_action",
    )
    if action == "Patient":
        with st.form("quick_add_patient", clear_on_submit=True):
            c1, c2 = st.columns(2)
            mrn = c1.text_input("MRN / رقم الملف")
            full_name = c1.text_input("Patient name / اسم المريض")
            age = int(c1.number_input("Age", 0, 120, 30))
            sex = c1.selectbox("Sex", ["Male", "Female", "Other/Unknown"])
            phone = c2.text_input("Phone")
            blood = c2.selectbox("Blood group", ["", "O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
            allergy_status = c2.selectbox("Allergy status", ["Unknown", "No known allergies", "Allergy recorded"])
            allergy_note = c2.text_input("Allergy note", disabled=allergy_status != "Allergy recorded")
            if st.form_submit_button("Save patient", type="primary"):
                if not mrn.strip() or not full_name.strip():
                    st.error("MRN and patient name are required.")
                else:
                    patient = get_or_create_patient(
                        {
                            "mrn": mrn.strip(),
                            "full_name": full_name.strip(),
                            "age": age,
                            "sex": sex,
                            "phone": phone or None,
                            "blood_group": blood or None,
                            "allergies": (
                                "No known allergies"
                                if allergy_status == "No known allergies"
                                else allergy_note or "Allergy status unknown"
                            ),
                        },
                        user.email,
                    )
                    st.session_state["selected_patient_id"] = int(patient.id)
                    st.success("Patient saved.")
                    st.rerun()

    elif action == "Appointment":
        _, labels = _patient_labels()
        if not labels:
            st.warning("Add a patient first.")
            return
        with st.form("quick_add_appointment", clear_on_submit=True):
            c1, c2 = st.columns(2)
            selected = c1.selectbox("Patient", list(labels.keys()))
            appointment_date = c1.date_input("Date", date.today())
            start_time = c1.time_input("Start time", time(9, 0))
            appointment_type = c1.selectbox("Type", APPOINTMENT_TYPES)
            clinician = c2.text_input("Clinician", user.name)
            location = c2.text_input("Clinic / room")
            status = c2.selectbox("Status", APPOINTMENT_STATUSES)
            reason = c2.text_area("Reason")
            if st.form_submit_button("Save appointment", type="primary"):
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
                st.success("Appointment created.")
                st.rerun()

    elif action == "Task":
        _, labels = _patient_labels()
        if not labels:
            st.warning("Add a patient first.")
            return
        with st.form("quick_add_task", clear_on_submit=True):
            selected = st.selectbox("Patient", list(labels.keys()))
            title = st.text_input("Task")
            c1, c2, c3 = st.columns(3)
            category = c1.selectbox("Category", ["Results", "Follow-up", "Medication", "Pre-op", "Pathology", "Wound", "Other"])
            due_date = c2.date_input("Due date", date.today())
            priority = c3.selectbox("Priority", ["Routine", "Urgent", "Critical"])
            assigned_to = st.text_input("Assigned to", user.name)
            notes = st.text_area("Notes")
            if st.form_submit_button("Create task", type="primary"):
                if not title.strip():
                    st.error("Task title is required.")
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
                    st.success("Task created.")
                    st.rerun()

    else:
        st.info("Open the structured surgical case form to capture the full pre-operative dataset.")
        if st.button("Open New operation", type="primary", width="stretch"):
            navigate(NEW_OPERATION)


def render_global_toolbar(hospital_name: str, user: UserContext) -> None:
    compact_app_header(hospital_name, user.name, user.role)
    left, middle, right = st.columns([7, 1, 1])
    with left:
        query = st.text_input(
            "Global search",
            placeholder="Search patient, MRN, phone, operation, clinician or result…",
            label_visibility="collapsed",
            key="global_search_query",
        )
    with middle:
        if st.button("Search", width="stretch", key="global_search_button"):
            st.session_state["show_global_results"] = True
    with right:
        if st.button("＋ New", type="primary", width="stretch", key="quick_add_button"):
            quick_add_dialog(user)

    if query and len(query.strip()) >= 2 and (st.session_state.get("show_global_results") or len(query.strip()) >= 3):
        results = search_records(query.strip(), limit=8)
        total = sum(len(v) for v in results.values())
        with st.container(border=True):
            top_left, top_right = st.columns([6, 1])
            top_left.markdown(f"**Search results** · {total}")
            if top_right.button("Close", key="close_global_results"):
                st.session_state["show_global_results"] = False
                st.session_state["global_search_query"] = ""
                st.rerun()
            if total == 0:
                st.caption("No matching record.")
            for patient in results["patients"]:
                c1, c2 = st.columns([7, 1])
                c1.markdown(f"**{_h(patient['full_name'])}** · {_h(patient['mrn'])} · {_h(patient.get('phone') or 'No phone')}")
                if c2.button("Open", key=f"search_patient_{patient['id']}"):
                    navigate(PATIENTS, patient_id=int(patient["id"]))
            for operation in results["operations"]:
                c1, c2 = st.columns([7, 1])
                c1.markdown(
                    f"🔵 **{_h(operation['patient_name'])}** · {_h(operation['operation_name'])} · "
                    f"{_h(operation['operation_date'])} · {status_badge(operation['status'])}",
                    unsafe_allow_html=True,
                )
                if c2.button("Open", key=f"search_operation_{operation['id']}"):
                    navigate(THEATRE, patient_id=int(operation["patient_id"]), operation_id=int(operation["id"]))
            for appointment in results["appointments"]:
                c1, c2 = st.columns([7, 1])
                c1.markdown(
                    f"🩺 **{_h(appointment['patient_name'])}** · {_h(appointment['appointment_type'])} · "
                    f"{appointment['appointment_date']} {appointment['start_time']}"
                )
                if c2.button("Open", key=f"search_appointment_{appointment['id']}"):
                    navigate(PATIENTS, patient_id=int(appointment["patient_id"]))


def render_sidebar_navigation(user: UserContext, available_pages: set[str]) -> str:
    current = st.session_state.get("nav_page", TODAY)
    if current not in available_pages:
        current = TODAY if TODAY in available_pages else next(iter(available_pages))
        st.session_state["nav_page"] = current

    st.sidebar.markdown("### Navigation")
    for group, pages in NAV_GROUPS.items():
        visible = [page for page in pages if page in available_pages]
        if not visible:
            continue
        st.sidebar.caption(group)
        for page in visible:
            label = page.split(" ", 1)[0] if len(page) > 28 else page
            if st.sidebar.button(
                label,
                key=f"nav_button_{page}",
                width="stretch",
                type="primary" if page == current else "secondary",
            ):
                st.session_state["nav_page"] = page
                st.rerun()
    if ADMIN in available_pages:
        st.sidebar.caption("System")
        if st.sidebar.button(
            ADMIN,
            key="nav_button_admin",
            width="stretch",
            type="primary" if ADMIN == current else "secondary",
        ):
            st.session_state["nav_page"] = ADMIN
            st.rerun()
    return current


def render_mobile_quick_navigation(available_pages: set[str]) -> None:
    visible = [page for page in PRIMARY_PAGES if page in available_pages]
    if not visible:
        return
    st.markdown("<div class='mobile-nav-label'>Quick navigation</div>", unsafe_allow_html=True)
    cols = st.columns(len(visible))
    for column, page in zip(cols, visible):
        short = {
            TODAY: "Today",
            PATIENTS: "Patients",
            CLINIC: "Clinic",
            THEATRE: "Theatre",
            WARD: "Ward",
        }.get(page, page)
        if column.button(short, key=f"mobile_nav_{page}", width="stretch"):
            st.session_state["nav_page"] = page
            st.rerun()
