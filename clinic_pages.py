from __future__ import annotations

import calendar
import json
import os
from collections import Counter, defaultdict
from datetime import date, datetime, time, timedelta
from typing import Any

import pandas as pd
import streamlit as st

from auth import UserContext, can, require
from clinic_catalog import (
    APPOINTMENT_STATUSES,
    APPOINTMENT_TYPES,
    CLINIC_TEMPLATES,
    COMMON_INVESTIGATIONS,
    COMMON_MEDICATIONS,
    DOSAGE_FORMS,
    ENCOUNTER_TYPES,
    FOLLOWUP_TYPES,
    FREQUENCIES,
    INVESTIGATION_CATEGORIES,
    ROUTES,
)
from clinical_standards import PREOP_TASKS, WHO_CHECKLIST
from database import (
    acknowledge_result,
    add_allergy,
    add_diagnostic_result,
    add_medication_reconciliation,
    add_patient_attachment,
    add_prescription_item,
    add_problem,
    create_appointment,
    create_encounter,
    create_followup,
    create_operation,
    create_patient_task,
    create_prescription,
    get_or_create_patient,
    get_patient,
    get_patient_attachment,
    get_prescription,
    list_active_medication_names,
    list_allergies,
    list_appointments,
    list_encounters,
    list_followups,
    list_medication_reconciliations,
    list_patient_attachments,
    list_patient_tasks,
    list_patients,
    list_prescriptions,
    list_problems,
    list_results,
    list_service_requests,
    operations_for_month,
    patient_timeline,
    seed_checklist,
    seed_tasks,
    sign_prescription,
    update_allergy,
    update_appointment,
    update_followup,
    update_patient,
    update_patient_task,
    update_problem,
    create_service_request,
)
from medication_safety import assess_medication
from operations_catalog import (
    LABEL_TO_CODE,
    OPERATION_BY_CODE,
    OPERATION_LABELS,
    URGENCY_OPTIONS,
    suggested_scores,
)
from reports import prescription_html
from ui_components import page_heading, patient_context_banner
from database import patient_snapshot


def _hospital_name() -> str:
    try:
        return str(st.secrets.get("HOSPITAL_NAME", "SurgiScore Clinic"))
    except Exception:
        return os.getenv("HOSPITAL_NAME", "SurgiScore Clinic")


def _patients_map() -> tuple[list[dict[str, Any]], dict[str, int]]:
    patients = list_patients()
    labels = {f"{p['mrn']} · {p['full_name']}": int(p["id"]) for p in patients}
    return patients, labels


def _default_patient_index(labels: dict[str, int]) -> int:
    selected_id = st.session_state.get("selected_patient_id")
    if selected_id is None:
        return 0
    for index, label in enumerate(labels.keys()):
        if int(labels[label]) == int(selected_id):
            return index
    return 0


def _status_class(status: str) -> str:
    if status in {"Completed", "Signed", "Reviewed"}:
        return "success"
    if status in {"Cancelled", "No-show", "Abnormal", "Critical"}:
        return "danger"
    if status in {"Waiting", "With doctor", "Result available", "Due"}:
        return "warning"
    return "info"


def _patient_banner(patient: dict[str, Any]) -> None:
    allergy_text = patient.get("allergies") or "Structured allergy record required"
    st.markdown(
        f"""
        <div class="patient-banner">
          <div><span class="eyebrow">PATIENT</span><h3>{patient.get('full_name','')}</h3></div>
          <div class="patient-grid">
            <span><b>MRN</b><br>{patient.get('mrn','')}</span>
            <span><b>Age</b><br>{patient.get('age') or '—'}</span>
            <span><b>Sex</b><br>{patient.get('sex','')}</span>
            <span><b>Blood</b><br>{patient.get('blood_group') or '—'}</span>
          </div>
          <div class="allergy-strip"><b>Allergy status:</b> {allergy_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _quick_patient_form(user: UserContext, key: str) -> int | None:
    with st.form(f"quick_patient_{key}", clear_on_submit=True):
        st.markdown("#### مريض جديد New patient")
        c1, c2 = st.columns(2)
        mrn = c1.text_input("MRN / رقم الملف", key=f"mrn_{key}")
        name = c1.text_input("Patient name / اسم المريض", key=f"name_{key}")
        age = int(c1.number_input("Age", 0, 120, 30, key=f"age_{key}"))
        sex = c1.selectbox("Sex", ["Male", "Female", "Other/Unknown"], key=f"sex_{key}")
        phone = c2.text_input("Phone", key=f"phone_{key}")
        blood_group = c2.selectbox("Blood group", ["", "O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"], key=f"blood_{key}")
        allergy_status = c2.selectbox("Allergy status", ["Unknown", "No known allergies", "Allergy recorded"], key=f"algstat_{key}")
        allergy_text = c2.text_input("Legacy allergy note", disabled=allergy_status != "Allergy recorded", key=f"alg_{key}")
        if st.form_submit_button("حفظ المريض Save patient", type="primary"):
            if not mrn.strip() or not name.strip():
                st.error("MRN and patient name are required.")
                return None
            p = get_or_create_patient(
                {
                    "mrn": mrn.strip(), "full_name": name.strip(), "age": age, "sex": sex,
                    "phone": phone or None, "blood_group": blood_group or None,
                    "allergies": "No known allergies" if allergy_status == "No known allergies" else (allergy_text or "Allergy status unknown"),
                },
                user.email,
            )
            st.success("Patient saved.")
            return int(p.id)
    return None


def page_command_center(user: UserContext) -> None:
    st.markdown("## مركز العمل Clinic & Surgical Command Center")
    today = date.today()
    appointments_today = list_appointments(today, today)
    operations_today = [x for x in operations_for_month(today.year, today.month) if str(x["operation_date"]) == today.isoformat()]
    due_followups = list_followups(status="Due", due_before=today)
    unreviewed = list_results(unreviewed_only=True)
    open_tasks = list_patient_tasks(status="Open", due_before=today)

    cols = st.columns(5)
    cols[0].metric("Clinic today", len(appointments_today))
    cols[1].metric("Operations today", len(operations_today))
    cols[2].metric("Follow-ups due", len(due_followups))
    cols[3].metric("New results", len(unreviewed))
    cols[4].metric("Overdue tasks", len(open_tasks))

    cal_tab, today_tab, action_tab = st.tabs(["📅 Monthly calendar", "🩺 Today", "➕ Quick action"])

    with cal_tab:
        c1, c2 = st.columns([1, 1])
        month = c1.selectbox("Month", list(range(1, 13)), index=today.month - 1, key="clinic_month")
        year = int(c2.number_input("Year", 2024, 2100, today.year, key="clinic_year"))
        start = date(year, int(month), 1)
        end = date(year, int(month), calendar.monthrange(year, int(month))[1])
        appointments = list_appointments(start, end)
        operations = operations_for_month(year, int(month))
        appt_by_day: dict[str, list[dict]] = defaultdict(list)
        op_by_day: dict[str, list[dict]] = defaultdict(list)
        for item in appointments:
            appt_by_day[str(item["appointment_date"])].append(item)
        for item in operations:
            op_by_day[str(item["operation_date"])].append(item)

        header = st.columns(7)
        for i, d in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            header[i].markdown(f"<div class='calendar-header'>{d}</div>", unsafe_allow_html=True)
        for week in calendar.monthcalendar(year, int(month)):
            cols = st.columns(7)
            for i, day in enumerate(week):
                with cols[i]:
                    if not day:
                        st.write("")
                        continue
                    ds = f"{year:04d}-{int(month):02d}-{day:02d}"
                    day_appts, day_ops = appt_by_day.get(ds, []), op_by_day.get(ds, [])
                    is_today = ds == today.isoformat()
                    st.markdown(f"<div class='calendar-cell {'today-cell' if is_today else ''}'><div class='date-number'>{day}</div>", unsafe_allow_html=True)
                    if day_appts:
                        st.markdown(f"<div class='calendar-count clinic-count'>Clinic {len(day_appts)}</div>", unsafe_allow_html=True)
                    if day_ops:
                        st.markdown(f"<div class='calendar-count theatre-count'>OR {len(day_ops)}</div>", unsafe_allow_html=True)
                    if not day_appts and not day_ops:
                        st.caption("—")
                    if day_appts or day_ops:
                        with st.popover("View"):
                            for a in day_appts:
                                st.write(f"🩺 {a['start_time']} · {a['patient_name']} · {a['appointment_type']} · {a['status']}")
                            for o in day_ops:
                                st.write(f"🔵 {o.get('start_time') or ''} · {o['patient_name']} · {o['operation_name']} · {o['status']}")
                    st.markdown("</div>", unsafe_allow_html=True)

    with today_tab:
        left, right = st.columns(2)
        with left:
            st.markdown("### Clinic queue")
            if not appointments_today:
                st.info("No clinic appointments today.")
            for a in appointments_today:
                st.markdown(
                    f"<div class='list-card'><div><b>{a['start_time']} · {a['patient_name']}</b><br><span>{a['appointment_type']} · {a['clinician']}</span></div><span class='status {_status_class(a['status'])}'>{a['status']}</span></div>",
                    unsafe_allow_html=True,
                )
        with right:
            st.markdown("### Theatre list")
            if not operations_today:
                st.info("No operations today.")
            for o in operations_today:
                st.markdown(
                    f"<div class='list-card'><div><b>{o.get('start_time') or ''} · {o['patient_name']}</b><br><span>{o['operation_name']} · {o['surgeon']}</span></div><span class='status info'>{o['status']}</span></div>",
                    unsafe_allow_html=True,
                )

    with action_tab:
        if not can(user, "write"):
            st.info("Read-only account.")
            return
        patients, pmap = _patients_map()
        mode = st.segmented_control("Action", ["New appointment", "New patient"], default="New appointment")
        if mode == "New patient":
            _quick_patient_form(user, "home")
        else:
            if not pmap:
                st.warning("Add a patient first.")
                _quick_patient_form(user, "home_appt")
            else:
                with st.form("quick_appointment", clear_on_submit=True):
                    c1, c2, c3 = st.columns(3)
                    label = c1.selectbox("Patient", list(pmap.keys()), index=_default_patient_index(pmap))
                    appt_date = c1.date_input("Date", today)
                    start_time = c1.time_input("Start", time(9, 0))
                    appt_type = c2.selectbox("Type", APPOINTMENT_TYPES)
                    clinician = c2.text_input("Clinician", user.name)
                    location = c2.text_input("Clinic / room")
                    reason = c3.text_area("Reason")
                    status = c3.selectbox("Status", APPOINTMENT_STATUSES)
                    if st.form_submit_button("Save appointment", type="primary"):
                        create_appointment({
                            "patient_id": pmap[label], "appointment_date": appt_date, "start_time": start_time,
                            "appointment_type": appt_type, "status": status, "clinician": clinician,
                            "location": location or None, "reason": reason or None,
                        }, user.email)
                        st.success("Appointment created.")
                        st.rerun()


def page_patients(user: UserContext) -> None:
    st.markdown("## سجل المرضى Longitudinal Patient Record")
    registry_tab, chart_tab = st.tabs(["Patients", "Patient chart"])

    with registry_tab:
        top1, top2 = st.columns([3, 1])
        search = top1.text_input("Search MRN, name or phone")
        add_new = top2.toggle("Add patient", value=False)
        if add_new and can(user, "write"):
            _quick_patient_form(user, "registry")
        patients = list_patients()
        if search:
            q = search.lower().strip()
            patients = [p for p in patients if q in str(p.get("mrn", "")).lower() or q in str(p.get("full_name", "")).lower() or q in str(p.get("phone", "")).lower()]
        for p in patients:
            st.markdown(
                f"<div class='record-card'><div><span class='eyebrow'>{p['mrn']}</span><h4>{p['full_name']}</h4><span>{p.get('age') or '—'} y · {p['sex']} · {p.get('phone') or 'No phone'}</span></div><div class='record-meta'>Blood {p.get('blood_group') or '—'}<br>{p.get('allergies') or 'Allergy unknown'}</div></div>",
                unsafe_allow_html=True,
            )

    with chart_tab:
        patients, pmap = _patients_map()
        if not pmap:
            st.info("No patients.")
            return
        selected = st.selectbox("Select patient", list(pmap.keys()), key="chart_patient")
        patient_id = pmap[selected]
        st.session_state["selected_patient_id"] = int(patient_id)
        patient = get_patient(patient_id)
        patient_context_banner(patient_snapshot(patient_id))

        overview, problems_tab, meds_tab, tests_tab, files_tab = st.tabs(["Timeline", "Problems & allergies", "Medications", "Investigations", "Files"])
        with overview:
            events = patient_timeline(patient_id)
            if not events:
                st.info("No events recorded.")
            for event in events:
                st.markdown(
                    f"<div class='timeline-row'><div class='timeline-date'>{event['date']}</div><div><b>{event['type']} · {event['title']}</b><br><span>{event['detail']}</span></div><span class='status {_status_class(event['status'])}'>{event['status']}</span></div>",
                    unsafe_allow_html=True,
                )

        with problems_tab:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### Problem list")
                for item in list_problems(patient_id):
                    x1, x2 = st.columns([5, 1])
                    x1.write(f"**{item['description']}** · {item['status']} · {item.get('severity') or ''}")
                    if can(user, "write") and item["status"] == "Active" and x2.button("Resolve", key=f"resolve_problem_{item['id']}"):
                        update_problem(item["id"], "Resolved", user.email); st.rerun()
                if can(user, "write"):
                    with st.form("add_problem"):
                        description = st.text_input("Problem / diagnosis")
                        pc1, pc2, pc3 = st.columns(3)
                        code = pc1.text_input("ICD/SNOMED code (optional)")
                        severity = pc2.selectbox("Severity", ["", "Mild", "Moderate", "Severe"])
                        certainty = pc3.selectbox("Certainty", ["Confirmed", "Suspected", "Differential"])
                        if st.form_submit_button("Add problem") and description.strip():
                            add_problem({"patient_id": patient_id, "description": description.strip(), "code": code or None, "severity": severity or None, "certainty": certainty}, user.email); st.rerun()
            with c2:
                st.markdown("### Allergies")
                allergies = list_allergies(patient_id, active_only=False)
                if not allergies:
                    st.warning("No structured allergy record. Confirm status before prescribing.")
                for item in allergies:
                    a1, a2 = st.columns([5, 1])
                    a1.write(f"**{item['substance']}** · {item.get('reaction') or 'Reaction not documented'} · {item['status']}")
                    if can(user, "write") and item["status"] == "Active" and a2.button("Inactivate", key=f"inactive_allergy_{item['id']}"):
                        update_allergy(item["id"], "Inactive", user.email); st.rerun()
                if can(user, "write"):
                    with st.form("add_allergy"):
                        substance = st.text_input("Substance / medication")
                        reaction = st.text_input("Reaction")
                        ac1, ac2 = st.columns(2)
                        severity = ac1.selectbox("Severity", ["Unknown", "Mild", "Moderate", "Severe", "Life-threatening"])
                        verification = ac2.selectbox("Verification", ["Unconfirmed", "Confirmed", "Refuted"])
                        if st.form_submit_button("Add allergy") and substance.strip():
                            add_allergy({"patient_id": patient_id, "substance": substance.strip(), "reaction": reaction or None, "severity": severity, "verification": verification}, user.email); st.rerun()

        with meds_tab:
            prescriptions = list_prescriptions(patient_id=patient_id)
            if not prescriptions:
                st.info("No prescriptions.")
            for rx in prescriptions:
                st.markdown(f"**Prescription #{rx['id']}** · {rx['status']} · {rx.get('indication') or ''} · {str(rx['created_at'])[:10]}")
                detail = get_prescription(rx["id"])
                for item in detail.get("items", []):
                    st.caption(f"{item['medication_name']} {item.get('strength') or ''} · {item.get('dose') or ''} {item.get('dose_unit') or ''} · {item.get('route') or ''} · {item.get('frequency') or ''}")

        with tests_tab:
            requests = list_service_requests(patient_id=patient_id)
            results = list_results(patient_id=patient_id)
            st.markdown("#### Requests")
            if requests: st.dataframe(pd.DataFrame(requests).drop(columns=[c for c in ["updated_at"] if c in pd.DataFrame(requests).columns]), width="stretch", hide_index=True)
            else: st.info("No requests.")
            st.markdown("#### Results")
            if results: st.dataframe(pd.DataFrame(results), width="stretch", hide_index=True)
            else: st.info("No results.")

        with files_tab:
            if can(user, "write"):
                category = st.selectbox("Category", ["Laboratory", "Radiology", "Pathology", "Clinical photo", "Referral", "Other"], key="patient_file_category")
                uploaded = st.file_uploader("Upload document or image", type=["pdf", "png", "jpg", "jpeg", "csv", "txt"], accept_multiple_files=True)
                if uploaded and st.button("Save files", type="primary"):
                    for f in uploaded:
                        if f.size > 10 * 1024 * 1024:
                            st.error(f"{f.name}: exceeds 10 MB pilot limit.")
                            continue
                        add_patient_attachment(patient_id, None, category, f.name, f.type or "application/octet-stream", f.getvalue(), user.email)
                    st.success("Files saved."); st.rerun()
            for item in list_patient_attachments(patient_id):
                c1, c2 = st.columns([4, 1])
                c1.write(f"**{item['filename']}** · {item['category']} · {round(item['file_size']/1024,1)} KB")
                obj = get_patient_attachment(item["id"])
                c2.download_button("Download", obj.data, item["filename"], item["mime_type"], key=f"patient_file_{item['id']}")


def page_clinic(user: UserContext) -> None:
    page_heading("مسار العيادة", "Clinic workflow", "قائمة الانتظار، المواعيد، والزيارة السريرية المنظمة ضمن سياق المريض.")
    today = date.today()
    queue_tab, appointments_tab, encounter_tab = st.tabs(["Today's queue", "Appointments", "Clinical encounter"])

    with queue_tab:
        rows = list_appointments(today, today)
        if not rows:
            st.info("No appointments today.")
        for a in rows:
            c1, c2, c3 = st.columns([5, 2, 2])
            c1.markdown(f"**{a['start_time']} · {a['patient_name']}**  \n{a['appointment_type']} · {a.get('reason') or ''}")
            c2.markdown(f"<span class='status {_status_class(a['status'])}'>{a['status']}</span>", unsafe_allow_html=True)
            if can(user, "write"):
                next_status = c3.selectbox("Update", APPOINTMENT_STATUSES, index=APPOINTMENT_STATUSES.index(a["status"]) if a["status"] in APPOINTMENT_STATUSES else 0, key=f"qstatus_{a['id']}", label_visibility="collapsed")
                if next_status != a["status"]:
                    update_appointment(a["id"], {"status": next_status}, user.email); st.rerun()
            st.divider()

    with appointments_tab:
        patients, pmap = _patients_map()
        if not pmap:
            st.warning("Add a patient first from Patient Registry.")
        elif can(user, "write"):
            with st.form("new_appointment_full", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                label = c1.selectbox("Patient", list(pmap.keys()), index=_default_patient_index(pmap), key="appt_patient")
                appt_date = c1.date_input("Date", today, key="appt_date")
                start_time = c1.time_input("Start time", time(9, 0), key="appt_time")
                appt_type = c2.selectbox("Appointment type", APPOINTMENT_TYPES, key="appt_type")
                clinician = c2.text_input("Clinician", user.name, key="appt_clinician")
                location = c2.text_input("Location", key="appt_location")
                status = c3.selectbox("Status", APPOINTMENT_STATUSES, key="appt_status")
                reason = c3.text_area("Reason / referral question", key="appt_reason")
                notes = c3.text_area("Administrative notes", key="appt_notes")
                if st.form_submit_button("Create appointment", type="primary"):
                    create_appointment({"patient_id": pmap[label], "appointment_date": appt_date, "start_time": start_time, "appointment_type": appt_type, "status": status, "clinician": clinician, "location": location or None, "reason": reason or None, "notes": notes or None}, user.email)
                    st.success("Appointment created."); st.rerun()

        upcoming = list_appointments(today, today + timedelta(days=60))
        if upcoming:
            st.dataframe(pd.DataFrame(upcoming), width="stretch", hide_index=True)

    with encounter_tab:
        require(user, "write")
        patients, pmap = _patients_map()
        if not pmap:
            st.info("No patients.")
            return
        today_appts = [a for a in list_appointments(today, today) if a["status"] not in {"Cancelled", "No-show", "Completed"}]
        source = st.radio("Start from", ["Patient", "Today's appointment"], horizontal=True)
        appointment_id = None
        if source == "Today's appointment" and today_appts:
            amap = {f"{a['start_time']} · {a['patient_name']} · {a['appointment_type']}": a for a in today_appts}
            alabel = st.selectbox("Appointment", list(amap.keys()))
            chosen = amap[alabel]; patient_id = int(chosen["patient_id"]); appointment_id = int(chosen["id"])
        else:
            plabel = st.selectbox("Patient", list(pmap.keys()), index=_default_patient_index(pmap), key="enc_patient")
            patient_id = pmap[plabel]
        st.session_state["selected_patient_id"] = int(patient_id)
        patient = get_patient(patient_id); patient_context_banner(patient_snapshot(patient_id))

        template_name = st.selectbox("Clinical template", ["Blank"] + list(CLINIC_TEMPLATES.keys()))
        template = CLINIC_TEMPLATES.get(template_name, {})
        with st.form("clinic_encounter_form", clear_on_submit=False):
            encounter_type = st.selectbox("Encounter type", ENCOUNTER_TYPES)
            st.markdown("#### History")
            c1, c2 = st.columns(2)
            chief = c1.text_area("Chief complaint")
            hpi = c1.text_area("History of presenting illness", height=160)
            pmh = c2.text_area("Past medical history")
            psh = c2.text_area("Past surgical history")
            current_meds = c2.text_area("Current medications")
            social = c2.text_area("Social history")

            st.markdown("#### Vital signs")
            v1, v2, v3, v4 = st.columns(4)
            weight = v1.number_input("Weight kg", 0.0, 300.0, 0.0)
            height = v1.number_input("Height cm", 0.0, 250.0, 0.0)
            sbp = v2.number_input("SBP", 0.0, 300.0, 0.0)
            dbp = v2.number_input("DBP", 0.0, 200.0, 0.0)
            pulse = v3.number_input("Pulse", 0.0, 250.0, 0.0)
            temp = v3.number_input("Temperature", 30.0, 45.0, 37.0)
            rr = v4.number_input("Respiratory rate", 0.0, 80.0, 0.0)
            spo2 = v4.number_input("SpO₂", 0.0, 100.0, 0.0)

            st.markdown("#### Examination & decision")
            examination = st.text_area("Physical examination", value=template.get("exam", ""), height=180)
            assessment = st.text_area("Assessment / differential diagnosis")
            diagnosis = st.text_area("Working or final diagnosis")
            plan = st.text_area("Plan", value=template.get("plan", ""), height=180)
            followup_date = st.date_input("Follow-up date", value=None)

            st.markdown("#### Surgical decision")
            surgery_decision = st.checkbox("Create a surgical case from this encounter")
            if surgery_decision:
                s1, s2, s3 = st.columns(3)
                operation_label = s1.selectbox("Planned operation", OPERATION_LABELS)
                operation_date = s1.date_input("Proposed date", today + timedelta(days=7))
                start = s1.time_input("Start time", time(8, 0))
                surgeon = s2.text_input("Responsible surgeon", user.name)
                urgency = s2.selectbox("Urgency", URGENCY_OPTIONS)
                ward = s2.text_input("Ward / day case")
                planned_diagnosis = s3.text_area("Surgical diagnosis", value=diagnosis)
                op_notes = s3.text_area("Special requirements")

            save_col, sign_col = st.columns(2)
            save_draft = save_col.form_submit_button("Save draft")
            sign = sign_col.form_submit_button("Sign encounter", type="primary")
            if save_draft or sign:
                data = {
                    "patient_id": patient_id, "appointment_id": appointment_id, "encounter_date": today,
                    "encounter_type": encounter_type, "chief_complaint": chief or None, "hpi": hpi or None,
                    "pmh": pmh or None, "psh": psh or None, "current_medications": current_meds or None,
                    "social_history": social or None, "examination": examination or None,
                    "assessment": assessment or None, "diagnosis": diagnosis or None, "plan": plan or None,
                    "weight_kg": weight or None, "height_cm": height or None, "systolic_bp": sbp or None,
                    "diastolic_bp": dbp or None, "pulse": pulse or None, "temperature": temp or None,
                    "respiratory_rate": rr or None, "spo2": spo2 or None, "followup_date": followup_date,
                }
                enc = create_encounter(data, user.email, signed=bool(sign))
                if followup_date:
                    create_followup({"patient_id": patient_id, "encounter_id": enc.id, "followup_type": "Follow-up visit", "due_date": followup_date, "status": "Due"}, user.email)
                if surgery_decision:
                    op_code = LABEL_TO_CODE[operation_label]
                    meta = OPERATION_BY_CODE[op_code]
                    op = create_operation({
                        "patient_id": patient_id, "operation_code": op_code, "operation_name": meta["name"],
                        "category": meta["category"], "diagnosis": planned_diagnosis or diagnosis or "Surgical diagnosis pending",
                        "operation_date": operation_date, "start_time": start, "status": "Scheduled", "urgency": urgency,
                        "surgeon": surgeon, "ward": ward or None, "notes": op_notes or None,
                    }, user.email)
                    seed_tasks(op.id, PREOP_TASKS, user.email); seed_checklist(op.id, WHO_CHECKLIST, user.email)
                    for score_name in suggested_scores(op_code, urgency, patient.get("age")):
                        seed_tasks(op.id, [{"phase":"Scores","code":f"score::{score_name}","label_ar":f"إكمال {score_name} أو توثيق سبب عدم الانطباق","label_en":f"Complete {score_name} or document why not applicable"}], user.email)
                st.success("Encounter saved and linked workflow created.")
                st.rerun()


def page_prescriptions(user: UserContext) -> None:
    page_heading("الوصفات والعلاج", "Prescribing", "وصفة منظمة، مراجعة الحساسية، وسجل Medication reconciliation.")
    patients, pmap = _patients_map()
    if not pmap:
        st.info("No patients.")
        return
    create_tab, history_tab, reconciliation_tab = st.tabs(["New prescription", "Prescription history", "Medication reconciliation"])

    with create_tab:
        require(user, "write")
        selected = st.selectbox("Patient", list(pmap.keys()), index=_default_patient_index(pmap), key="rx_patient")
        patient_id = pmap[selected]
        st.session_state["selected_patient_id"] = int(patient_id)
        patient = get_patient(patient_id); patient_context_banner(patient_snapshot(patient_id))
        allergies = list_allergies(patient_id)
        active_meds = list_active_medication_names(patient_id)
        if not allergies and "No known allergies" not in str(patient.get("allergies") or ""):
            st.error("Allergy status is not adequately documented. Confirm it before signing a prescription.")

        if "rx_cart" not in st.session_state:
            st.session_state.rx_cart = []
        indication = st.text_input("Clinical indication")
        notes = st.text_area("Prescription notes / reconciliation comments")
        st.markdown("### Add medication")
        c1, c2, c3 = st.columns(3)
        med = c1.selectbox("Generic medication", COMMON_MEDICATIONS)
        if med == "Other medication":
            med = c1.text_input("Medication name")
        strength = c1.text_input("Strength")
        dosage_form = c1.selectbox("Dosage form", DOSAGE_FORMS)
        dose = c2.text_input("Dose")
        dose_unit = c2.text_input("Dose unit")
        route = c2.selectbox("Route", ROUTES)
        frequency = c2.selectbox("Frequency", FREQUENCIES)
        duration = int(c3.number_input("Duration days", 0, 365, 0))
        quantity = c3.text_input("Quantity")
        prn = c3.checkbox("PRN")
        prn_indication = c3.text_input("PRN indication", disabled=not prn)
        instructions_ar = st.text_area("Patient instructions — Arabic")
        instructions_en = st.text_area("Patient instructions — English")

        alerts = assess_medication(med, allergies, active_meds)
        hard_stop = any(x["severity"] == "Hard stop" for x in alerts)
        for alert in alerts:
            if alert["severity"] == "Hard stop": st.error(alert["message"])
            elif alert["severity"] == "Warning": st.warning(alert["message"])
            else: st.info(alert["message"])
        override_reason = st.text_area("Override justification", disabled=not hard_stop)
        if st.button("Add medication to prescription"):
            if not med.strip():
                st.error("Medication name is required.")
            elif hard_stop and not override_reason.strip():
                st.error("A documented override justification is required for an allergy conflict.")
            else:
                st.session_state.rx_cart.append({
                    "medication_name": med.strip(), "strength": strength or None, "dosage_form": dosage_form,
                    "dose": dose or None, "dose_unit": dose_unit or None, "route": route, "frequency": frequency,
                    "duration_days": duration or None, "quantity": quantity or None, "prn": prn,
                    "prn_indication": prn_indication or None, "instructions_ar": instructions_ar or None,
                    "instructions_en": instructions_en or None, "item_status": "Active",
                    "override_reason": override_reason or None,
                })
                st.rerun()

        if st.session_state.rx_cart:
            st.markdown("### Prescription items")
            for i, item in enumerate(st.session_state.rx_cart):
                x1, x2 = st.columns([6, 1])
                x1.write(f"**{item['medication_name']} {item.get('strength') or ''}** · {item.get('dose') or ''} {item.get('dose_unit') or ''} · {item['route']} · {item['frequency']}")
                if x2.button("Remove", key=f"remove_rx_{i}"):
                    st.session_state.rx_cart.pop(i); st.rerun()
            sign_now = st.checkbox("Sign and activate prescription", value=can(user, "sign"))
            if st.button("Save prescription", type="primary"):
                if not allergies and "No known allergies" not in str(patient.get("allergies") or ""):
                    st.error("Document allergy status before saving.")
                else:
                    overrides = [x.get("override_reason") for x in st.session_state.rx_cart if x.get("override_reason")]
                    final_notes = notes + (("\nSafety override: " + " | ".join(overrides)) if overrides else "")
                    rx = create_prescription(patient_id, None, indication, final_notes, user.email)
                    for item in st.session_state.rx_cart:
                        payload = {k:v for k,v in item.items() if k != "override_reason"}
                        add_prescription_item(rx.id, payload, user.email)
                    if sign_now and can(user, "sign"):
                        sign_prescription(rx.id, user.email)
                    st.session_state.rx_cart = []
                    st.success(f"Prescription #{rx.id} saved."); st.rerun()

    with history_tab:
        selected = st.selectbox("Filter patient", ["All patients"] + list(pmap.keys()), key="rx_history_patient")
        patient_id = None if selected == "All patients" else pmap[selected]
        rows = list_prescriptions(patient_id=patient_id)
        if not rows:
            st.info("No prescriptions.")
        for rx in rows:
            detail = get_prescription(rx["id"])
            with st.expander(f"#{rx['id']} · {rx['patient_name']} · {rx['status']} · {str(rx['created_at'])[:10]}"):
                for item in detail.get("items", []):
                    st.write(f"• {item['medication_name']} {item.get('strength') or ''} — {item.get('dose') or ''} {item.get('dose_unit') or ''} {item.get('route') or ''} {item.get('frequency') or ''}")
                html = prescription_html(detail, _hospital_name()).encode("utf-8")
                st.download_button("Download printable prescription", html, f"prescription_{rx['id']}.html", "text/html", key=f"rxhtml_{rx['id']}")


    with reconciliation_tab:
        require(user, "write")
        selected = st.selectbox("Patient for reconciliation", list(pmap.keys()), index=_default_patient_index(pmap), key="recon_patient")
        patient_id = pmap[selected]
        st.session_state["selected_patient_id"] = int(patient_id)
        patient = get_patient(patient_id)
        patient_context_banner(patient_snapshot(patient_id))
        rows = list_medication_reconciliations(patient_id)
        if rows:
            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
        with st.form("medication_reconciliation_form", clear_on_submit=True):
            st.markdown("#### Reconcile a home medication")
            c1, c2, c3 = st.columns(3)
            medication_name = c1.text_input("Medication name")
            home_regimen = c1.text_input("Home dose / regimen")
            action = c2.selectbox("Action", ["Continue", "Stop", "Hold temporarily", "Change dose", "Replace", "Uncertain — clarify"])
            transition = c2.selectbox("Transition", ["Clinic", "Admission", "Pre-operative", "Ward transfer", "Discharge", "Post-operative follow-up"])
            reason = c3.text_area("Reason / reconciliation note")
            if st.form_submit_button("Save reconciliation", type="primary"):
                if not medication_name.strip():
                    st.error("Medication name is required.")
                else:
                    add_medication_reconciliation({"patient_id":patient_id,"encounter_id":None,"medication_name":medication_name.strip(),"home_regimen":home_regimen or None,"action":action,"reason":reason or None,"transition":transition}, user.email)
                    st.success("Medication reconciliation saved."); st.rerun()

def page_investigations(user: UserContext) -> None:
    page_heading("الطلبات والنتائج", "Investigations & results", "إدارة الطلبات ونتائج المختبر والأشعة.")
    patients, pmap = _patients_map()
    request_tab, inbox_tab, all_tab = st.tabs(["New request", "Results inbox", "All requests"])

    with request_tab:
        require(user, "write")
        if not pmap:
            st.info("No patients."); return
        with st.form("new_service_request", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            plabel = c1.selectbox("Patient", list(pmap.keys()), index=_default_patient_index(pmap))
            category = c1.selectbox("Category", INVESTIGATION_CATEGORIES)
            options = COMMON_INVESTIGATIONS.get(category, ["Other request"])
            test = c2.selectbox("Test / service", options)
            if test.startswith("Other"):
                test = c2.text_input("Specify test")
            priority = c2.selectbox("Priority", ["Routine", "Urgent", "STAT"])
            indication = c3.text_area("Clinical indication / question")
            if st.form_submit_button("Submit request", type="primary"):
                if not test.strip(): st.error("Test name required.")
                else:
                    create_service_request({"patient_id":pmap[plabel],"encounter_id":None,"category":category,"test_name":test.strip(),"indication":indication or None,"priority":priority,"status":"Requested"}, user.email)
                    st.success("Request created."); st.rerun()

    with inbox_tab:
        rows = list_results(unreviewed_only=True)
        if not rows:
            st.success("No unreviewed results.")
        for result in rows:
            severity = result.get("abnormal_flag") or "Not flagged"
            with st.expander(f"{result['patient_name']} · {result['test_name']} · {severity}"):
                st.write(result.get("result_text") or "")
                if result.get("numeric_value") is not None:
                    st.metric(result["test_name"], f"{result['numeric_value']} {result.get('unit') or ''}", result.get("reference_range") or None)
                if can(user, "write") and st.button("Acknowledge / mark reviewed", key=f"ack_result_{result['request_id']}"):
                    acknowledge_result(result["request_id"], user.email); st.rerun()

    with all_tab:
        requests = list_service_requests()
        if requests:
            st.dataframe(pd.DataFrame(requests), width="stretch", hide_index=True)
            require(user, "write")
            pending = [r for r in requests if r["status"] in {"Requested", "Scheduled", "Collected", "In progress"}]
            if pending:
                rmap = {f"#{r['id']} · {r['patient_name']} · {r['test_name']}": r for r in pending}
                selected = st.selectbox("Enter result for", list(rmap.keys()))
                req = rmap[selected]
                with st.form("result_entry"):
                    result_text = st.text_area("Result / report")
                    c1, c2, c3 = st.columns(3)
                    value = c1.number_input("Numeric value", value=None, placeholder="Optional")
                    unit = c2.text_input("Unit")
                    ref = c3.text_input("Reference range")
                    flag = st.selectbox("Flag", ["Normal", "Abnormal", "Critical", "Not applicable"])
                    if st.form_submit_button("Save result", type="primary"):
                        add_diagnostic_result(req["id"], req["patient_id"], {"result_text":result_text or None,"numeric_value":value,"unit":unit or None,"reference_range":ref or None,"abnormal_flag":flag}, user.email)
                        st.success("Result saved."); st.rerun()
        else:
            st.info("No requests.")


def page_followups(user: UserContext) -> None:
    page_heading("المتابعة بعد العملية", "Post-operative follow-up", "الجروح، الألم، الالتزام بالعلاج، والعودة غير المخطط لها.")
    today = date.today()
    due_tab, new_tab, completed_tab = st.tabs(["Due follow-ups", "Schedule follow-up", "Completed"])

    with due_tab:
        rows = list_followups(status="Due", due_before=today + timedelta(days=7))
        if not rows:
            st.success("No follow-ups due in the next 7 days.")
        for f in rows:
            with st.expander(f"{f['due_date']} · {f['patient_name']} · {f['followup_type']}"):
                if can(user, "write"):
                    with st.form(f"complete_followup_{f['id']}"):
                        c1, c2, c3 = st.columns(3)
                        pain = c1.slider("Pain score", 0, 10, int(f.get("pain_score") or 0))
                        fever = c1.selectbox("Fever", ["No", "Yes", "Unknown"])
                        wound = c2.selectbox("Wound", ["Clean/dry", "Mild erythema", "Discharge", "Dehiscence", "Concern for SSI", "Not assessed"])
                        drain = c2.text_input("Drain status")
                        intake = c3.selectbox("Oral intake", ["Normal", "Reduced", "Unable", "Not assessed"])
                        mobility = c3.selectbox("Mobility", ["Independent", "Assisted", "Limited", "Bedbound", "Not assessed"])
                        bowel = st.text_input("Bowel function")
                        urinary = st.text_input("Urinary function")
                        adherence = st.selectbox("Medication adherence", ["Good", "Partial", "Poor", "Not assessed"])
                        adverse = st.text_area("Medication adverse effects")
                        assessment = st.text_area("Clinical assessment")
                        plan = st.text_area("Plan and safety-net advice")
                        next_date = st.date_input("Next follow-up", value=None)
                        if st.form_submit_button("Complete follow-up", type="primary"):
                            update_followup(f["id"], {"pain_score":pain,"fever":fever=="Yes","wound_status":wound,"drain_status":drain or None,"oral_intake":intake,"bowel_function":bowel or None,"urinary_function":urinary or None,"mobility":mobility,"medication_adherence":adherence,"adverse_effects":adverse or None,"assessment":assessment or None,"plan":plan or None,"next_followup_date":next_date}, user.email, complete=True)
                            if next_date:
                                create_followup({"patient_id":f["patient_id"],"operation_id":f.get("operation_id"),"followup_type":"Follow-up visit","due_date":next_date,"status":"Due"}, user.email)
                            st.success("Follow-up completed."); st.rerun()

    with new_tab:
        require(user, "write")
        patients, pmap = _patients_map()
        if pmap:
            with st.form("schedule_followup"):
                c1, c2 = st.columns(2)
                plabel = c1.selectbox("Patient", list(pmap.keys()), index=_default_patient_index(pmap))
                ftype = c1.selectbox("Follow-up type", FOLLOWUP_TYPES)
                due = c2.date_input("Due date", today + timedelta(days=7))
                notes = c2.text_area("Reason / plan")
                if st.form_submit_button("Schedule", type="primary"):
                    create_followup({"patient_id":pmap[plabel],"followup_type":ftype,"due_date":due,"status":"Due","plan":notes or None}, user.email)
                    st.success("Follow-up scheduled."); st.rerun()

    with completed_tab:
        rows = list_followups(status="Completed")
        if rows:
            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
        else:
            st.info("No completed follow-ups.")


def page_tasks(user: UserContext) -> None:
    page_heading("المهام السريرية", "Clinical tasks", "قائمة مهام مرتبطة بالمريض مع تاريخ استحقاق وأولوية ومسؤول.")
    today = date.today()
    open_tab, create_tab = st.tabs(["Open tasks", "Create task"])
    with open_tab:
        rows = list_patient_tasks(status="Open")
        if not rows:
            st.success("No open tasks.")
        for task in rows:
            c1, c2, c3 = st.columns([5, 2, 1])
            c1.write(f"**{task['title']}** · {task['patient_name']} · {task.get('category') or ''}")
            c2.caption(f"Due: {task.get('due_date') or 'No date'} · {task['priority']}")
            if can(user, "write") and c3.button("Done", key=f"task_done_{task['id']}"):
                update_patient_task(task["id"], "Completed", user.email); st.rerun()
    with create_tab:
        require(user, "write")
        patients, pmap = _patients_map()
        if pmap:
            with st.form("create_patient_task"):
                plabel = st.selectbox("Patient", list(pmap.keys()), index=_default_patient_index(pmap))
                title = st.text_input("Task")
                c1, c2, c3 = st.columns(3)
                category = c1.selectbox("Category", ["Results", "Follow-up", "Medication", "Pre-op", "Pathology", "Wound", "Other"])
                due = c2.date_input("Due date", today)
                priority = c3.selectbox("Priority", ["Routine", "Urgent", "Critical"])
                assigned = st.text_input("Assigned to", user.name)
                notes = st.text_area("Notes")
                if st.form_submit_button("Create task", type="primary") and title.strip():
                    create_patient_task({"patient_id":pmap[plabel],"title":title.strip(),"category":category,"due_date":due,"priority":priority,"status":"Open","assigned_to":assigned,"notes":notes or None}, user.email)
                    st.success("Task created."); st.rerun()
