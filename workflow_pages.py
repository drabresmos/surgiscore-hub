from __future__ import annotations

import calendar
from collections import defaultdict
from datetime import date, datetime, timedelta
from html import escape
from typing import Any

import pandas as pd
import streamlit as st

from auth import UserContext, can, require
from clinic_catalog import COMMON_INVESTIGATIONS, INVESTIGATION_CATEGORIES
from database import (
    acknowledge_result,
    add_allergy,
    add_patient_attachment,
    add_problem,
    create_followup,
    create_patient_task,
    create_service_request,
    get_patient,
    get_patient_attachment,
    get_prescription,
    list_allergies,
    list_appointments,
    list_encounters,
    list_followups,
    list_medication_reconciliations,
    list_operations_for_patient,
    list_patient_attachments,
    list_patient_tasks,
    list_patients,
    list_prescriptions,
    list_problems,
    list_results,
    list_service_requests,
    operations_for_month,
    patient_snapshot,
    patient_timeline,
    update_allergy,
    update_patient_task,
    update_problem,
)
from navigation import (
    CLINIC,
    FOLLOWUP,
    PATIENTS,
    PRESCRIBING,
    RESULTS,
    SURGICAL_JOURNEY,
    TASKS,
    THEATRE,
    WARD,
    navigate,
)
from ui_components import (
    calculate_pod,
    empty_state,
    page_heading,
    patient_context_banner,
    priority_badge,
    status_badge,
    status_class,
    work_item_card,
    workflow_stepper,
)




def _h(value: Any) -> str:
    return escape(str(value if value not in (None, "") else "—"))

def _patient_options() -> tuple[list[dict[str, Any]], dict[str, int]]:
    patients = list_patients()
    labels = {f"{p['mrn']} · {p['full_name']}": int(p["id"]) for p in patients}
    return patients, labels


def _select_patient(key: str = "patient_chart_selector") -> tuple[int | None, dict[str, Any] | None]:
    patients, labels = _patient_options()
    if not labels:
        st.info("No patients recorded.")
        return None, None
    selected_id = st.session_state.get("selected_patient_id")
    options = list(labels.keys())
    default_index = 0
    if selected_id:
        for index, label in enumerate(options):
            if labels[label] == int(selected_id):
                default_index = index
                break
    selected = st.selectbox("Select patient", options, index=default_index, key=key)
    patient_id = labels[selected]
    st.session_state["selected_patient_id"] = patient_id
    return patient_id, get_patient(patient_id)


def _calendar_summary() -> None:
    today = date.today()
    c1, c2 = st.columns(2)
    month = c1.selectbox("Month", list(range(1, 13)), index=today.month - 1, key="worklist_month")
    year = int(c2.number_input("Year", 2024, 2100, today.year, key="worklist_year"))
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
    for index, weekday in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
        header[index].markdown(f"<div class='calendar-header'>{weekday}</div>", unsafe_allow_html=True)
    for week in calendar.monthcalendar(year, int(month)):
        columns = st.columns(7)
        for index, day_number in enumerate(week):
            with columns[index]:
                if not day_number:
                    st.write("")
                    continue
                day_key = f"{year:04d}-{int(month):02d}-{day_number:02d}"
                day_appointments = appt_by_day.get(day_key, [])
                day_operations = op_by_day.get(day_key, [])
                today_class = "today-cell" if day_key == today.isoformat() else ""
                st.markdown(
                    f"<div class='calendar-cell {today_class}'><div class='date-number'>{day_number}</div>",
                    unsafe_allow_html=True,
                )
                if day_appointments:
                    st.markdown(
                        f"<div class='calendar-count clinic-count'>Clinic {len(day_appointments)}</div>",
                        unsafe_allow_html=True,
                    )
                if day_operations:
                    st.markdown(
                        f"<div class='calendar-count theatre-count'>OR {len(day_operations)}</div>",
                        unsafe_allow_html=True,
                    )
                if not day_appointments and not day_operations:
                    st.caption("—")
                if day_appointments or day_operations:
                    with st.popover("View"):
                        for appointment in day_appointments:
                            st.write(
                                f"🩺 {appointment['start_time']} · {appointment['patient_name']} · "
                                f"{appointment['appointment_type']} · {appointment['status']}"
                            )
                        for operation in day_operations:
                            st.write(
                                f"🔵 {operation.get('start_time') or ''} · {operation['patient_name']} · "
                                f"{operation['operation_name']} · {operation['status']}"
                            )
                st.markdown("</div>", unsafe_allow_html=True)


def page_today_worklist(user: UserContext) -> None:
    page_heading(
        "مساحة العمل اليومية",
        "My worklist",
        "المهام والحالات التي تحتاج إجراء الآن، مرتبة حسب الأولوية ودور المستخدم.",
    )
    today = date.today()
    appointments = list_appointments(today, today)
    operations = [
        x for x in operations_for_month(today.year, today.month)
        if str(x["operation_date"]) == today.isoformat()
    ]
    due_followups = list_followups(status="Due", due_before=today)
    unreviewed_results = list_results(unreviewed_only=True)
    open_tasks = list_patient_tasks(status="Open", due_before=today)
    active_inpatients = [
        op for op in operations_for_month(today.year, today.month)
        if op.get("status") in {"PACU/Recovery", "Post-op ward", "Ready for theatre", "In theatre"}
    ]

    metrics = st.columns(6)
    metrics[0].metric("Clinic today", len(appointments))
    metrics[1].metric("Operations", len(operations))
    metrics[2].metric("Ward patients", len(active_inpatients))
    metrics[3].metric("Results", len(unreviewed_results))
    metrics[4].metric("Follow-ups due", len(due_followups))
    metrics[5].metric("Overdue tasks", len(open_tasks))

    if user.role == "nurse":
        default_focus = "Ward"
    elif user.role in {"consultant", "resident"}:
        default_focus = "Clinical work"
    else:
        default_focus = "Overview"
    focus = st.segmented_control(
        "Focus",
        ["Overview", "Clinical work", "Clinic", "Theatre", "Ward", "Calendar"],
        default=default_focus,
        key="worklist_focus",
    )

    if focus in {"Overview", "Clinical work"}:
        left, right = st.columns([1, 1])
        with left:
            st.markdown("### Due now / مستحق الآن")
            items_shown = 0
            for task in open_tasks[:8]:
                work_item_card(
                    task["title"],
                    f"{task['patient_name']} · {task.get('category') or 'Clinical task'}",
                    "Overdue" if task.get("due_date") and str(task["due_date"]) < today.isoformat() else "Due",
                    f"Due {task.get('due_date') or 'not set'} · Assigned to {task.get('assigned_to') or 'unassigned'}",
                    "✓",
                )
                c1, c2 = st.columns([1, 1])
                if c1.button("Open patient", key=f"work_task_patient_{task['id']}", width="stretch"):
                    navigate(PATIENTS, patient_id=int(task["patient_id"]))
                if can(user, "write") and c2.button("Mark done", key=f"work_task_done_{task['id']}", width="stretch"):
                    update_patient_task(task["id"], "Completed", user.email)
                    st.rerun()
                items_shown += 1
            for followup in due_followups[:5]:
                work_item_card(
                    followup["followup_type"],
                    f"{followup['patient_name']} · Post-operative follow-up",
                    "Due",
                    f"Due {followup['due_date']}",
                    "↻",
                )
                if st.button("Open follow-up", key=f"work_followup_{followup['id']}", width="stretch"):
                    navigate(FOLLOWUP, patient_id=int(followup["patient_id"]))
                items_shown += 1
            if not items_shown:
                empty_state("No overdue work", "There are no overdue tasks or follow-ups for today.")

        with right:
            st.markdown("### Results requiring review")
            if not unreviewed_results:
                empty_state("Inbox clear", "No unreviewed diagnostic results.")
            for result in unreviewed_results[:10]:
                flag = result.get("abnormal_flag") or "Result available"
                work_item_card(
                    result["test_name"],
                    f"{result['patient_name']} · {result.get('result_text') or 'Result available'}",
                    flag,
                    f"{result.get('numeric_value') or ''} {result.get('unit') or ''}".strip(),
                    "!",
                )
                c1, c2 = st.columns([1, 1])
                if c1.button("Open patient", key=f"work_result_patient_{result['id']}", width="stretch"):
                    navigate(PATIENTS, patient_id=int(result["patient_id"]))
                if can(user, "write") and c2.button("Acknowledge", key=f"work_result_ack_{result['id']}", width="stretch"):
                    acknowledge_result(int(result["request_id"]), user.email)
                    st.rerun()

    elif focus == "Clinic":
        st.markdown("### Today’s clinic queue")
        if not appointments:
            empty_state("No clinic appointments", "No appointments are scheduled for today.", "🩺")
        for appointment in appointments:
            c1, c2, c3 = st.columns([6, 2, 1])
            c1.markdown(
                f"**{appointment['start_time']} · {appointment['patient_name']}**  \n"
                f"{appointment['appointment_type']} · {appointment.get('reason') or 'No reason documented'}"
            )
            c2.markdown(status_badge(appointment["status"]), unsafe_allow_html=True)
            if c3.button("Open", key=f"today_clinic_{appointment['id']}"):
                navigate(PATIENTS, patient_id=int(appointment["patient_id"]))
            st.divider()
        if st.button("Open Clinic workspace", type="primary"):
            navigate(CLINIC)

    elif focus == "Theatre":
        st.markdown("### Today’s operating list")
        if not operations:
            empty_state("No operations today", "The operating list is empty.", "🔵")
        for operation in operations:
            work_item_card(
                operation["operation_name"],
                f"{operation['patient_name']} · {operation['surgeon']} · OR {operation.get('or_room') or 'TBC'}",
                operation["status"],
                f"{operation.get('start_time') or 'Time TBC'} · {operation['urgency']}",
                "OR",
            )
            c1, c2 = st.columns([1, 1])
            if c1.button("Open patient", key=f"today_op_patient_{operation['id']}", width="stretch"):
                navigate(PATIENTS, patient_id=int(operation["patient_id"]))
            if c2.button("Open pathway", key=f"today_op_path_{operation['id']}", width="stretch"):
                navigate(SURGICAL_JOURNEY, patient_id=int(operation["patient_id"]), operation_id=int(operation["id"]))

    elif focus == "Ward":
        st.markdown("### Surgical ward")
        if not active_inpatients:
            empty_state("No active ward patients", "No current surgical inpatient episode was found.", "▦")
        for operation in active_inpatients:
            pod = calculate_pod(operation.get("operation_date"))
            work_item_card(
                operation["patient_name"],
                f"{operation['operation_name']} · POD {pod if pod is not None else '—'}",
                operation["status"],
                f"{operation.get('ward') or 'Ward TBC'} / {operation.get('bed') or 'Bed TBC'}",
                "▦",
            )
            if st.button("Open ward pathway", key=f"today_ward_{operation['id']}", width="stretch"):
                navigate(SURGICAL_JOURNEY, patient_id=int(operation["patient_id"]), operation_id=int(operation["id"]))
        if st.button("Open Ward board", type="primary"):
            navigate(WARD)

    else:
        _calendar_summary()


def page_patient_chart(user: UserContext) -> None:
    page_heading(
        "ملف المريض",
        "Longitudinal patient chart",
        "سجل موحد للزيارات والتشخيصات والأدوية والنتائج والعمليات والمتابعة.",
    )
    top_left, top_right = st.columns([5, 1])
    with top_left:
        patient_id, patient = _select_patient()
    with top_right:
        if st.button("Clinic visit", width="stretch", disabled=patient is None):
            navigate(CLINIC, patient_id=patient_id)
        if st.button("New task", width="stretch", disabled=patient is None):
            navigate(TASKS, patient_id=patient_id)
    if not patient_id or not patient:
        return

    snapshot = patient_snapshot(patient_id)
    patient_context_banner(snapshot)

    tabs = st.tabs(
        [
            "Overview",
            "Visits",
            "Problems",
            "Medications",
            "Orders & Results",
            "Surgery",
            "Follow-up",
            "Documents",
        ]
    )

    with tabs[0]:
        left, right = st.columns([1.25, 1])
        with left:
            st.markdown("### Clinical summary")
            problems = snapshot.get("active_problems") or []
            medications = snapshot.get("active_medications") or []
            st.markdown(
                f"""
                <div class='summary-grid'>
                  <div><span>Active problems</span><b>{len(problems)}</b><small>{_h(', '.join(str(x['description']) for x in problems[:3]) or 'None documented')}</small></div>
                  <div><span>Current medicines</span><b>{len(medications)}</b><small>{_h(', '.join(str(x) for x in medications[:3]) or 'None active')}</small></div>
                  <div><span>New results</span><b>{len(snapshot.get('unreviewed_results') or [])}</b><small>Awaiting clinical review</small></div>
                  <div><span>Open tasks</span><b>{len(snapshot.get('open_tasks') or [])}</b><small>Outstanding actions</small></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            active_operation = snapshot.get("active_operation")
            if active_operation:
                st.markdown("### Current surgical pathway")
                workflow_stepper(active_operation.get("status") or "Decision", compact=True)
                c1, c2 = st.columns(2)
                c1.write(f"**{active_operation['operation_name']}**")
                c1.caption(f"{active_operation['operation_date']} · {active_operation['surgeon']}")
                if c2.button("Open surgical journey", key="overview_open_pathway", width="stretch"):
                    navigate(SURGICAL_JOURNEY, patient_id=patient_id, operation_id=int(active_operation["id"]))
        with right:
            st.markdown("### Next actions")
            next_actions = (snapshot.get("open_tasks") or [])[:5]
            for task in next_actions:
                work_item_card(
                    task["title"],
                    task.get("category") or "Clinical task",
                    task.get("priority") or "Routine",
                    f"Due {task.get('due_date') or 'not set'}",
                    "✓",
                )
            for followup in (snapshot.get("due_followups") or [])[:3]:
                work_item_card(
                    followup["followup_type"],
                    "Follow-up",
                    followup["status"],
                    f"Due {followup['due_date']}",
                    "↻",
                )
            if not next_actions and not snapshot.get("due_followups"):
                empty_state("No active actions", "No open tasks or due follow-ups.")
        st.markdown("### Timeline")
        events = patient_timeline(patient_id)
        if not events:
            empty_state("No timeline events", "Start a clinic encounter, investigation or surgical case.", "○")
        for event in events[:20]:
            st.markdown(
                f"<div class='timeline-row'><div class='timeline-date'>{_h(event['date'])}</div>"
                f"<div><b>{_h(event['type'])} · {_h(event['title'])}</b><br><span>{_h(event['detail'])}</span></div>"
                f"{status_badge(event['status'])}</div>",
                unsafe_allow_html=True,
            )

    with tabs[1]:
        st.markdown("### Visits and encounters")
        appointments = list_appointments(patient_id=patient_id)
        encounters = list_encounters(patient_id=patient_id)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Appointments")
            if not appointments:
                st.info("No appointments.")
            for appointment in appointments[:20]:
                st.markdown(
                    f"<div class='list-card'><div><b>{_h(appointment['appointment_date'])} · {_h(appointment['appointment_type'])}</b>"
                    f"<br><span>{_h(appointment.get('reason') or 'No reason')} · {_h(appointment.get('clinician') or '')}</span></div>"
                    f"{status_badge(appointment['status'])}</div>",
                    unsafe_allow_html=True,
                )
        with c2:
            st.markdown("#### Clinical encounters")
            if not encounters:
                st.info("No encounters.")
            for encounter in encounters[:20]:
                st.markdown(
                    f"<div class='list-card'><div><b>{_h(encounter['encounter_date'])} · {_h(encounter['encounter_type'])}</b>"
                    f"<br><span>{_h(encounter.get('diagnosis') or encounter.get('chief_complaint') or 'No diagnosis documented')}</span></div>"
                    f"{status_badge(encounter['status'])}</div>",
                    unsafe_allow_html=True,
                )
        if st.button("Open Clinic workspace", type="primary", width="stretch"):
            navigate(CLINIC, patient_id=patient_id)

    with tabs[2]:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Problem list")
            problems = list_problems(patient_id)
            if not problems:
                st.info("No problems recorded.")
            for problem in problems:
                p1, p2 = st.columns([5, 1])
                p1.markdown(
                    f"**{problem['description']}**  \n{problem.get('certainty') or ''} · {problem.get('severity') or ''} · {problem['status']}"
                )
                if can(user, "write") and problem["status"] == "Active" and p2.button("Resolve", key=f"chart_resolve_{problem['id']}"):
                    update_problem(problem["id"], "Resolved", user.email)
                    st.rerun()
            if can(user, "write"):
                with st.form("chart_add_problem", clear_on_submit=True):
                    description = st.text_input("Problem / diagnosis")
                    c1, c2, c3 = st.columns(3)
                    code = c1.text_input("ICD/SNOMED code")
                    severity = c2.selectbox("Severity", ["", "Mild", "Moderate", "Severe"])
                    certainty = c3.selectbox("Certainty", ["Confirmed", "Suspected", "Differential"])
                    if st.form_submit_button("Add problem") and description.strip():
                        add_problem(
                            {
                                "patient_id": patient_id,
                                "description": description.strip(),
                                "code": code or None,
                                "severity": severity or None,
                                "certainty": certainty,
                            },
                            user.email,
                        )
                        st.rerun()
        with col2:
            st.markdown("### Allergies and intolerances")
            allergies = list_allergies(patient_id, active_only=False)
            if not allergies:
                st.warning("No structured allergy record. Confirm status before prescribing.")
            for allergy in allergies:
                a1, a2 = st.columns([5, 1])
                a1.markdown(
                    f"**{allergy['substance']}**  \n{allergy.get('reaction') or 'Reaction not documented'} · "
                    f"{allergy.get('severity') or 'Severity unknown'} · {allergy['status']}"
                )
                if can(user, "write") and allergy["status"] == "Active" and a2.button("Inactivate", key=f"chart_allergy_{allergy['id']}"):
                    update_allergy(allergy["id"], "Inactive", user.email)
                    st.rerun()
            if can(user, "write"):
                with st.form("chart_add_allergy", clear_on_submit=True):
                    substance = st.text_input("Substance / medication")
                    reaction = st.text_input("Reaction")
                    c1, c2 = st.columns(2)
                    severity = c1.selectbox("Severity", ["Unknown", "Mild", "Moderate", "Severe", "Life-threatening"])
                    verification = c2.selectbox("Verification", ["Unconfirmed", "Confirmed", "Refuted"])
                    if st.form_submit_button("Add allergy") and substance.strip():
                        add_allergy(
                            {
                                "patient_id": patient_id,
                                "substance": substance.strip(),
                                "reaction": reaction or None,
                                "severity": severity,
                                "verification": verification,
                            },
                            user.email,
                        )
                        st.rerun()

    with tabs[3]:
        st.markdown("### Medication record")
        prescriptions = list_prescriptions(patient_id=patient_id)
        if not prescriptions:
            st.info("No prescriptions recorded.")
        for prescription in prescriptions:
            detail = get_prescription(prescription["id"])
            with st.expander(
                f"Prescription #{prescription['id']} · {prescription['status']} · {str(prescription['created_at'])[:10]}"
            ):
                st.caption(prescription.get("indication") or "No indication documented")
                for item in detail.get("items", []):
                    st.write(
                        f"• {item['medication_name']} {item.get('strength') or ''} · "
                        f"{item.get('dose') or ''} {item.get('dose_unit') or ''} · "
                        f"{item.get('route') or ''} · {item.get('frequency') or ''}"
                    )
        reconciliation = list_medication_reconciliations(patient_id)
        if reconciliation:
            st.markdown("#### Medication reconciliation")
            st.dataframe(pd.DataFrame(reconciliation), width="stretch", hide_index=True)
        if st.button("Open prescribing", type="primary", width="stretch"):
            navigate(PRESCRIBING, patient_id=patient_id)

    with tabs[4]:
        st.markdown("### Orders and results")
        requests = list_service_requests(patient_id=patient_id)
        results = list_results(patient_id=patient_id)
        new_count = sum(1 for row in results if row.get("request_status") == "Result available")
        c1, c2, c3 = st.columns(3)
        c1.metric("Requests", len(requests))
        c2.metric("Results", len(results))
        c3.metric("Awaiting review", new_count)
        for result in results[:20]:
            flag = result.get("abnormal_flag") or "Result available"
            with st.container(border=True):
                h1, h2 = st.columns([5, 1])
                h1.markdown(f"**{result['test_name']}** · {str(result['resulted_at'])[:16]}")
                h2.markdown(status_badge(flag), unsafe_allow_html=True)
                st.write(result.get("result_text") or "No narrative result.")
                if result.get("numeric_value") is not None:
                    st.metric(
                        result["test_name"],
                        f"{result['numeric_value']} {result.get('unit') or ''}",
                        result.get("reference_range") or None,
                    )
                if can(user, "write") and result.get("request_status") == "Result available":
                    if st.button("Acknowledge", key=f"chart_ack_{result['id']}"):
                        acknowledge_result(int(result["request_id"]), user.email)
                        st.rerun()
        if requests:
            with st.expander("All requests"):
                st.dataframe(pd.DataFrame(requests), width="stretch", hide_index=True)
        if st.button("Open Orders & Results", type="primary", width="stretch"):
            navigate(RESULTS, patient_id=patient_id)

    with tabs[5]:
        st.markdown("### Surgical episodes")
        operations = list_operations_for_patient(patient_id, include_archived=True)
        if not operations:
            empty_state("No surgical episode", "Create a surgical case from the clinic or theatre module.", "OR")
        for operation in operations:
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                c1.markdown(
                    f"**{operation['operation_name']}**  \n{operation['operation_date']} · {operation['surgeon']} · {operation['diagnosis']}"
                )
                c2.markdown(status_badge(operation["status"]), unsafe_allow_html=True)
                workflow_stepper(operation["status"], compact=True)
                if st.button("Open surgical journey", key=f"chart_pathway_{operation['id']}", width="stretch"):
                    navigate(SURGICAL_JOURNEY, patient_id=patient_id, operation_id=int(operation["id"]))

    with tabs[6]:
        st.markdown("### Follow-up plan")
        followups = list_followups(patient_id=patient_id)
        if not followups:
            st.info("No follow-up plan recorded.")
        for followup in followups:
            st.markdown(
                f"<div class='list-card'><div><b>{_h(followup['due_date'])} · {_h(followup['followup_type'])}</b>"
                f"<br><span>{_h(followup.get('plan') or followup.get('assessment') or 'No plan documented')}</span></div>"
                f"{status_badge(followup['status'])}</div>",
                unsafe_allow_html=True,
            )
        if can(user, "write"):
            with st.form("chart_schedule_followup", clear_on_submit=True):
                c1, c2 = st.columns(2)
                followup_type = c1.selectbox(
                    "Follow-up type",
                    ["Follow-up visit", "Wound review", "Suture/staple removal", "Drain review/removal", "Pathology review", "Telephone review"],
                )
                due_date = c1.date_input("Due date", date.today() + timedelta(days=7))
                plan = c2.text_area("Plan / reason")
                if st.form_submit_button("Schedule follow-up"):
                    create_followup(
                        {
                            "patient_id": patient_id,
                            "followup_type": followup_type,
                            "due_date": due_date,
                            "status": "Due",
                            "plan": plan or None,
                        },
                        user.email,
                    )
                    st.rerun()
        if st.button("Open Follow-up workspace", type="primary", width="stretch"):
            navigate(FOLLOWUP, patient_id=patient_id)

    with tabs[7]:
        st.markdown("### Documents and images")
        if can(user, "write"):
            category = st.selectbox(
                "Category",
                ["Laboratory", "Radiology", "Pathology", "Clinical photo", "Referral", "Consent", "Other"],
                key="chart_document_category",
            )
            uploaded = st.file_uploader(
                "Upload document or image",
                type=["pdf", "png", "jpg", "jpeg", "csv", "txt"],
                accept_multiple_files=True,
                key="chart_document_upload",
            )
            if uploaded and st.button("Save documents", type="primary"):
                for file in uploaded:
                    if file.size > 10 * 1024 * 1024:
                        st.error(f"{file.name}: exceeds 10 MB pilot limit.")
                        continue
                    add_patient_attachment(
                        patient_id,
                        None,
                        category,
                        file.name,
                        file.type or "application/octet-stream",
                        file.getvalue(),
                        user.email,
                    )
                st.success("Documents saved.")
                st.rerun()
        attachments = list_patient_attachments(patient_id)
        if not attachments:
            st.info("No documents uploaded.")
        for attachment in attachments:
            c1, c2 = st.columns([5, 1])
            c1.markdown(
                f"**{attachment['filename']}**  \n{attachment['category']} · {round(attachment['file_size'] / 1024, 1)} KB"
            )
            object_ = get_patient_attachment(attachment["id"])
            c2.download_button(
                "Download",
                object_.data,
                attachment["filename"],
                attachment["mime_type"],
                key=f"chart_file_{attachment['id']}",
            )


def page_results_workspace(user: UserContext) -> None:
    page_heading(
        "الطلبات والنتائج",
        "Orders & results",
        "صندوق نتائج قابل للتنفيذ: مراجعة، إنشاء مهمة، فتح ملف المريض، أو طلب فحص جديد.",
    )
    inbox_tab, request_tab, all_tab = st.tabs(["Results inbox", "New request", "All orders"])

    with inbox_tab:
        all_results = list_results()
        c1, c2, c3 = st.columns(3)
        scope = c1.selectbox("Scope", ["Unreviewed", "Critical", "Abnormal", "All"])
        patient_query = c2.text_input("Patient / MRN")
        category = c3.selectbox("Category", ["All"] + sorted({x.get("category") for x in all_results if x.get("category")}))
        rows = all_results
        if scope == "Unreviewed":
            rows = [x for x in rows if x.get("request_status") == "Result available"]
        elif scope == "Critical":
            rows = [x for x in rows if x.get("abnormal_flag") == "Critical"]
        elif scope == "Abnormal":
            rows = [x for x in rows if x.get("abnormal_flag") in {"Abnormal", "Critical"}]
        if patient_query.strip():
            query = patient_query.lower().strip()
            rows = [
                x for x in rows
                if query in str(x.get("patient_name", "")).lower() or query in str(x.get("mrn", "")).lower()
            ]
        if category != "All":
            rows = [x for x in rows if x.get("category") == category]

        metrics = st.columns(4)
        metrics[0].metric("Displayed", len(rows))
        metrics[1].metric("Unreviewed", sum(x.get("request_status") == "Result available" for x in all_results))
        metrics[2].metric("Abnormal", sum(x.get("abnormal_flag") == "Abnormal" for x in all_results))
        metrics[3].metric("Critical", sum(x.get("abnormal_flag") == "Critical" for x in all_results))

        if not rows:
            empty_state("No matching results", "The selected inbox is clear.")
        for result in rows:
            with st.container(border=True):
                h1, h2 = st.columns([5, 1])
                h1.markdown(
                    f"**{result['patient_name']} · {result['test_name']}**  \n"
                    f"MRN {result['mrn']} · {str(result['resulted_at'])[:16]} · {result.get('category') or ''}"
                )
                h2.markdown(status_badge(result.get("abnormal_flag") or result.get("request_status") or "Result"), unsafe_allow_html=True)
                if result.get("numeric_value") is not None:
                    st.metric(
                        result["test_name"],
                        f"{result['numeric_value']} {result.get('unit') or ''}",
                        result.get("reference_range") or None,
                    )
                st.write(result.get("result_text") or "No narrative report.")
                a1, a2, a3 = st.columns(3)
                if a1.button("Open patient", key=f"inbox_open_{result['id']}", width="stretch"):
                    navigate(PATIENTS, patient_id=int(result["patient_id"]))
                if can(user, "write") and result.get("request_status") == "Result available":
                    if a2.button("Acknowledge", key=f"inbox_ack_{result['id']}", width="stretch"):
                        acknowledge_result(int(result["request_id"]), user.email)
                        st.rerun()
                if can(user, "write"):
                    if a3.button("Create follow-up task", key=f"inbox_task_{result['id']}", width="stretch"):
                        create_patient_task(
                            {
                                "patient_id": int(result["patient_id"]),
                                "title": f"Review/action: {result['test_name']}",
                                "category": "Results",
                                "due_date": date.today(),
                                "priority": "Critical" if result.get("abnormal_flag") == "Critical" else "Urgent",
                                "status": "Open",
                                "assigned_to": user.name,
                                "notes": result.get("result_text") or None,
                            },
                            user.email,
                        )
                        st.success("Task created.")
                        st.rerun()

    with request_tab:
        require(user, "write")
        _, labels = _patient_options()
        if not labels:
            st.info("No patients.")
        else:
            selected_id = st.session_state.get("selected_patient_id")
            options = list(labels.keys())
            default_index = 0
            if selected_id:
                for index, label in enumerate(options):
                    if labels[label] == int(selected_id):
                        default_index = index
                        break
            with st.form("workflow_new_request", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                selected = c1.selectbox("Patient", options, index=default_index)
                request_category = c1.selectbox("Category", INVESTIGATION_CATEGORIES)
                available = COMMON_INVESTIGATIONS.get(request_category, ["Other request"])
                test_name = c2.selectbox("Test / service", available)
                if test_name.startswith("Other"):
                    test_name = c2.text_input("Specify test")
                priority = c2.selectbox("Priority", ["Routine", "Urgent", "STAT"])
                indication = c3.text_area("Clinical indication / question")
                if st.form_submit_button("Submit request", type="primary"):
                    if not test_name.strip():
                        st.error("Test name is required.")
                    else:
                        create_service_request(
                            {
                                "patient_id": labels[selected],
                                "encounter_id": None,
                                "category": request_category,
                                "test_name": test_name.strip(),
                                "indication": indication or None,
                                "priority": priority,
                                "status": "Requested",
                            },
                            user.email,
                        )
                        st.success("Request created.")
                        st.rerun()

    with all_tab:
        requests = list_service_requests()
        if not requests:
            st.info("No service requests.")
        else:
            st.dataframe(pd.DataFrame(requests), width="stretch", hide_index=True)
