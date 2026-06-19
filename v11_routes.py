from __future__ import annotations

import streamlit as st

TODAY = "اليوم"
PATIENTS = "المرضى"
SURGERY = "العمليات"
WARD = "الردهة"
MORE = "المزيد"

MAIN_SECTIONS = [TODAY, PATIENTS, SURGERY, WARD, MORE]

SECTION_ICONS = {
    TODAY: "⌂",
    PATIENTS: "♙",
    SURGERY: "✚",
    WARD: "▦",
    MORE: "•••",
}

SECTION_EN = {
    TODAY: "Today",
    PATIENTS: "Patients",
    SURGERY: "Surgery",
    WARD: "Ward",
    MORE: "More",
}


def set_section(
    section: str,
    *,
    patient_id: int | None = None,
    operation_id: int | None = None,
) -> None:
    st.session_state["v11_section"] = section
    st.session_state["v11_legacy_mode"] = False
    if patient_id is not None:
        st.session_state["selected_patient_id"] = int(patient_id)
    if operation_id is not None:
        st.session_state["selected_operation_id"] = int(operation_id)
    st.rerun()


def open_legacy(
    route: str,
    *,
    return_section: str = MORE,
    patient_id: int | None = None,
    operation_id: int | None = None,
) -> None:
    st.session_state["v11_legacy_mode"] = True
    st.session_state["v11_return_section"] = return_section
    st.session_state["nav_page"] = route
    if patient_id is not None:
        st.session_state["selected_patient_id"] = int(patient_id)
    if operation_id is not None:
        st.session_state["selected_operation_id"] = int(operation_id)
    st.rerun()


def close_legacy() -> None:
    st.session_state["v11_legacy_mode"] = False
    st.session_state["v11_section"] = st.session_state.get("v11_return_section", TODAY)
    st.rerun()
