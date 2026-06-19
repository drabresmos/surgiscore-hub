from __future__ import annotations

import calendar
import io
import json
import os
from collections import Counter, defaultdict
from datetime import date, datetime, time, timezone, timedelta
from zoneinfo import ZoneInfo
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

from auth import UserContext, can, require
from clinical_logic import calculate_age, news2_score
from clinical_standards import DISCHARGE_RED_FLAGS, POSTOP_HANDOFF_FIELDS, PRACTICAL_ERAS_ELEMENTS, PREOP_TASKS, WHO_CHECKLIST
from database import (
    add_attachment,
    add_clinical_record,
    add_score_result,
    add_vitals,
    add_ward_round,
    archive_operation,
    export_all_tables,
    get_attachment,
    get_audit_logs,
    get_operation,
    get_operations,
    get_or_create_patient,
    list_attachments,
    list_checklist,
    list_clinical_records,
    list_score_results,
    list_staff,
    list_tasks,
    list_vitals,
    list_ward_rounds,
    operations_for_month,
    seed_checklist,
    seed_tasks,
    update_checklist_item,
    update_operation,
    update_staff_role,
    update_task,
    create_operation,
)
from fhir_export import build_fhir_bundle
from operations_catalog import (
    ANESTHESIA_OPTIONS,
    LABEL_TO_CODE,
    LATERALITY_OPTIONS,
    OPERATION_BY_CODE,
    OPERATION_LABELS,
    STATUS_OPTIONS,
    URGENCY_OPTIONS,
    WOUND_CLASSES,
    SCORE_DESCRIPTIONS,
    suggested_scores,
)
from scores import ALL_SCORES, SCORE_CATEGORIES, render_score
from ui_components import calculate_pod, empty_state, page_heading, patient_context_banner, status_badge, workflow_stepper
from database import patient_snapshot
from navigation import PATIENTS, SURGICAL_JOURNEY, navigate



def _configured_timezone() -> ZoneInfo:
    try:
        name = str(st.secrets.get("TIMEZONE", "Asia/Baghdad"))
    except Exception:
        name = os.getenv("TIMEZONE", "Asia/Baghdad")
    try:
        return ZoneInfo(name)
    except Exception:
        return ZoneInfo("UTC")


def _parse_iso_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        try:
            dt = datetime.fromisoformat(str(value))
        except ValueError:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _observation_due_status(last: dict[str, Any] | None) -> tuple[str, str]:
    if not last:
        return "Overdue", "No observations recorded"
    observed = _parse_iso_datetime(last.get("observed_at"))
    if not observed:
        return "Review", "Invalid observation timestamp"
    text = str(last.get("escalation") or "")
    if "Continuous monitoring" in text:
        return "Continuous", "Continuous monitoring required"
    if "Minimum hourly" in text:
        interval = timedelta(hours=1)
    elif "Minimum 4–6 hourly" in text:
        interval = timedelta(hours=6)
    else:
        interval = timedelta(hours=12)
    now = datetime.now(timezone.utc)
    due_at = observed.astimezone(timezone.utc) + interval
    if now >= due_at:
        return "Overdue", f"Due since {due_at.astimezone(_configured_timezone()).strftime('%Y-%m-%d %H:%M')}"
    return "Due", f"Next by {due_at.astimezone(_configured_timezone()).strftime('%Y-%m-%d %H:%M')}"


def _checklist_phase_complete(operation_id: int, phase: str) -> bool:
    items = list_checklist(operation_id, phase)
    return bool(items) and all(item["answer"] in {"yes", "na"} for item in items)


def _tasks_complete(operation_id: int, phase: str) -> bool:
    tasks = list_tasks(operation_id, phase)
    return bool(tasks) and all(task["status"] in {"done", "na", "overridden"} for task in tasks)

def _status_css(status: str) -> str:
    if status == "Scheduled": return "scheduled"
    if status in {"Pre-op assessment", "Ready for theatre"}: return "preop"
    if status == "In theatre": return "theatre"
    if status in {"PACU/Recovery", "Post-op ward"}: return "postop"
    return "discharged"


def _operation_label(operation_id: int) -> str:
    op = get_operation(operation_id)
    if not op:
        return f"#{operation_id}"
    return f"#{operation_id} · {op['patient']['full_name']} · {op['operation_name']} · {op['operation_date']}"


def _safe_json_download(data: Any, filename: str, label: str):
    raw = json.dumps(data, ensure_ascii=False, indent=2, default=str).encode("utf-8")
    st.download_button(label, raw, filename, "application/json")


def _risk_html(risk: str) -> str:
    css = {"Low": "risk-low", "Medium": "risk-medium", "High": "risk-high"}.get(risk, "muted")
    return f"<span class='{css}'>{risk}</span>"


def _create_case_from_form(values: dict[str, Any], user: UserContext) -> int:
    patient = get_or_create_patient(
        {
            "mrn": values["mrn"].strip(),
            "full_name": values["full_name"].strip(),
            "date_of_birth": values.get("date_of_birth"),
            "age": values.get("age"),
            "sex": values["sex"],
            "phone": values.get("phone") or None,
            "blood_group": values.get("blood_group") or None,
            "allergies": values.get("allergies") or None,
            "emergency_contact": values.get("emergency_contact") or None,
        },
        user.email,
    )
    operation_code = values["operation_code"]
    meta = OPERATION_BY_CODE[operation_code]
    op = create_operation(
        {
            "patient_id": patient.id,
            "operation_code": operation_code,
            "operation_name": meta["name"],
            "category": meta["category"],
            "diagnosis": values["diagnosis"].strip(),
            "operation_date": values["operation_date"],
            "start_time": values["start_time"],
            "expected_duration_min": values.get("expected_duration_min"),
            "status": values.get("status", "Scheduled"),
            "urgency": values["urgency"],
            "laterality": values.get("laterality"),
            "surgical_site": values.get("surgical_site") or None,
            "surgeon": values["surgeon"].strip(),
            "assistant": values.get("assistant") or None,
            "anesthetist": values.get("anesthetist") or None,
            "planned_anesthesia": values.get("planned_anesthesia"),
            "ward": values.get("ward") or None,
            "bed": values.get("bed") or None,
            "or_room": values.get("or_room") or None,
            "wound_class": values.get("wound_class"),
            "anticipated_blood_loss_ml": values.get("anticipated_blood_loss_ml"),
            "blood_products_planned": values.get("blood_products_planned") or None,
            "admission_date": values.get("admission_date"),
            "notes": values.get("notes") or None,
        },
        user.email,
    )
    seed_tasks(op.id, PREOP_TASKS, user.email)
    seed_checklist(op.id, WHO_CHECKLIST, user.email)
    for score_name in suggested_scores(operation_code, values["urgency"], values.get("age")):
        seed_tasks(
            op.id,
            [{"phase": "Scores", "code": f"score::{score_name}", "label_ar": f"إكمال {score_name} أو توثيق سبب عدم الانطباق", "label_en": f"Complete {score_name} or document why it is not applicable"}],
            user.email,
        )
    return op.id


def page_calendar(user: UserContext):
    page_heading(
        "قائمة وتقويم العمليات",
        "Theatre schedule",
        "عرض شهري أو قائمة تشغيلية لعمليات اليوم والأسبوع مع الوصول المباشر لمسار الحالة.",
    )
    today = date.today()
    top1, top2, top3 = st.columns([1, 1, 2])
    month = top1.selectbox("Month", list(range(1, 13)), index=today.month - 1)
    year = int(top2.number_input("Year", 2024, 2100, today.year))
    view_mode = top3.segmented_control("View", ["Calendar", "List"], default="Calendar")

    rows = operations_for_month(year, int(month))
    if view_mode == "List":
        if not rows:
            empty_state("No operations", "No cases are scheduled for the selected month.", "OR")
        else:
            frame = pd.DataFrame(rows)
            c1, c2, c3 = st.columns(3)
            status_filter = c1.selectbox("Status", ["All"] + sorted(frame["status"].dropna().unique().tolist()))
            surgeon_filter = c2.selectbox("Surgeon", ["All"] + sorted(frame["surgeon"].dropna().unique().tolist()))
            urgency_filter = c3.selectbox("Urgency", ["All"] + sorted(frame["urgency"].dropna().unique().tolist()))
            filtered = rows
            if status_filter != "All": filtered = [x for x in filtered if x["status"] == status_filter]
            if surgeon_filter != "All": filtered = [x for x in filtered if x["surgeon"] == surgeon_filter]
            if urgency_filter != "All": filtered = [x for x in filtered if x["urgency"] == urgency_filter]
            for op in filtered:
                with st.container(border=True):
                    a, b, c = st.columns([5, 2, 1])
                    a.markdown(f"**{op['operation_date']} {op.get('start_time') or ''} · {op['patient_name']}**  \n{op['operation_name']} · {op['surgeon']} · OR {op.get('or_room') or 'TBC'}")
                    b.markdown(status_badge(op["status"]), unsafe_allow_html=True)
                    if c.button("Open", key=f"theatre_list_open_{op['id']}"):
                        navigate(SURGICAL_JOURNEY, patient_id=int(op["patient_id"]), operation_id=int(op["id"]))
    else:
        by_day: dict[str, list[dict]] = defaultdict(list)
        for op in rows:
            by_day[str(op["operation_date"])].append(op)

        header = st.columns(7)
        for i, day_name in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            header[i].markdown(f"<div class='calendar-header'>{day_name}</div>", unsafe_allow_html=True)

        for week in calendar.monthcalendar(year, int(month)):
            cols = st.columns(7)
            for idx, day in enumerate(week):
                with cols[idx]:
                    if day == 0:
                        st.write("")
                        continue
                    ds = f"{year:04d}-{int(month):02d}-{day:02d}"
                    day_ops = by_day.get(ds, [])
                    today_class = "today-cell" if ds == today.isoformat() else ""
                    st.markdown(f'<div class="calendar-cell {today_class}"><div class="date-number">{day}</div>', unsafe_allow_html=True)
                    if day_ops:
                        counts = Counter(op["status"] for op in day_ops)
                        for status, count in counts.items():
                            st.markdown(f"<div class='calendar-count theatre-count'>{status}: {count}</div>", unsafe_allow_html=True)
                        with st.popover(f"Cases ({len(day_ops)})"):
                            for op in day_ops:
                                st.write(f"**{op.get('start_time') or ''} · {op['patient_name']}**")
                                st.caption(f"{op['operation_name']} · {op['surgeon']} · {op['status']}")
                                if st.button("Open pathway", key=f"calendar_open_{op['id']}", width="stretch"):
                                    navigate(SURGICAL_JOURNEY, patient_id=int(op["patient_id"]), operation_id=int(op["id"]))
                    else:
                        st.caption("—")
                    st.markdown("</div>", unsafe_allow_html=True)

    if can(user, "write"):
        with st.expander("➕ إضافة عملية مباشرة Quick add", expanded=False):
            with st.form("quick_add_case", clear_on_submit=True):
                q1, q2, q3 = st.columns(3)
                mrn = q1.text_input("MRN / رقم الملف")
                full_name = q1.text_input("Patient name / اسم المريض")
                age = int(q1.number_input("Age", 0, 120, 30))
                sex = q1.selectbox("Sex", ["Male", "Female", "Other/Unknown"])
                diagnosis = q2.text_input("Diagnosis")
                op_label = q2.selectbox("Operation", OPERATION_LABELS)
                operation_date = q2.date_input("Date", value=today)
                start_time = q2.time_input("Start time", value=time(8, 0))
                surgeon = q3.text_input("Responsible surgeon")
                urgency = q3.selectbox("Urgency", URGENCY_OPTIONS)
                ward = q3.text_input("Ward")
                submit = st.form_submit_button("Save case", type="primary")
                if submit:
                    if not all([mrn.strip(), full_name.strip(), diagnosis.strip(), surgeon.strip()]):
                        st.error("MRN, patient name, diagnosis and surgeon are required.")
                    else:
                        op_id = _create_case_from_form(
                            {
                                "mrn": mrn, "full_name": full_name, "age": age, "sex": sex,
                                "diagnosis": diagnosis, "operation_code": LABEL_TO_CODE[op_label],
                                "operation_date": operation_date, "start_time": start_time,
                                "surgeon": surgeon, "urgency": urgency, "ward": ward,
                                "status": "Scheduled", "laterality": "Not applicable",
                            },
                            user,
                        )
                        st.session_state["selected_operation_id"] = int(op_id)
                        st.success(f"Saved operation #{op_id}")
                        st.rerun()

def page_new_case(user: UserContext):
    require(user, "write")
    st.markdown("## إضافة حالة جراحية New surgical case")
    st.caption("الحقول الأساسية منظمة وفق patient identification, procedure verification, perioperative planning and local documentation needs.")

    with st.form("new_case_form", clear_on_submit=False):
        st.markdown("### 1. معلومات المريض Patient identity")
        a, b, c = st.columns(3)
        mrn = a.text_input("MRN / رقم الملف *")
        full_name = a.text_input("Full name / اسم المريض *")
        dob = a.date_input("Date of birth", value=None)
        age = calculate_age(dob) if dob else int(a.number_input("Age if DOB unavailable", 0, 120, 30))
        sex = b.selectbox("Sex", ["Male", "Female", "Other/Unknown"])
        phone = b.text_input("Phone")
        blood_group = b.selectbox("Blood group", ["Unknown", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
        allergies = c.text_area("Allergies / الحساسية")
        emergency_contact = c.text_area("Emergency contact")

        st.markdown("### 2. العملية Operation")
        d, e, f = st.columns(3)
        diagnosis = d.text_area("Diagnosis *")
        operation_label = d.selectbox("Planned procedure *", OPERATION_LABELS)
        operation_date = d.date_input("Operation date", value=date.today())
        start_time = d.time_input("Planned start", value=time(8, 0))
        expected_duration = e.number_input("Expected duration (minutes)", 0, 1440, 60)
        urgency = e.selectbox("Urgency", URGENCY_OPTIONS)
        laterality = e.selectbox("Laterality", LATERALITY_OPTIONS)
        surgical_site = e.text_input("Specific site")
        surgeon = f.text_input("Responsible surgeon *")
        assistant = f.text_input("Assistant/team")
        anesthetist = f.text_input("Anesthetist")
        anesthesia = f.selectbox("Planned anesthesia", ANESTHESIA_OPTIONS)

        st.markdown("### 3. المكان والخطة Perioperative logistics")
        g, h, i = st.columns(3)
        ward = g.text_input("Ward")
        bed = g.text_input("Bed")
        or_room = g.text_input("Operating room")
        wound_class = h.selectbox("Planned wound class", WOUND_CLASSES)
        anticipated_blood_loss = h.number_input("Anticipated blood loss mL", 0, 20000, 0)
        blood_products = h.text_input("Blood products planned")
        admission_date = i.date_input("Admission date", value=date.today())
        notes = i.text_area("Clinical notes")

        operation_code = LABEL_TO_CODE[operation_label]
        proposed = suggested_scores(operation_code, urgency, age)
        st.markdown("### 4. السكورات المقترحة Suggested scores")
        st.info(" · ".join(proposed))
        st.caption("بعد الحفظ ستظهر السكورات ضمن Patient Journey. يمكن إكمالها أو توثيق Not applicable/deferred مع السبب وفق سياسة القسم.")

        submit = st.form_submit_button("Save and create patient journey", type="primary")
        if submit:
            if not mrn.strip() or not full_name.strip() or not diagnosis.strip() or not surgeon.strip():
                st.error("Complete all required fields marked with *.")
            else:
                op_id = _create_case_from_form(
                    {
                        "mrn": mrn, "full_name": full_name, "date_of_birth": dob, "age": age,
                        "sex": sex, "phone": phone, "blood_group": blood_group, "allergies": allergies,
                        "emergency_contact": emergency_contact, "diagnosis": diagnosis,
                        "operation_code": operation_code, "operation_date": operation_date,
                        "start_time": start_time, "expected_duration_min": int(expected_duration),
                        "urgency": urgency, "laterality": laterality, "surgical_site": surgical_site,
                        "surgeon": surgeon, "assistant": assistant, "anesthetist": anesthetist,
                        "planned_anesthesia": anesthesia, "ward": ward, "bed": bed, "or_room": or_room,
                        "wound_class": wound_class, "anticipated_blood_loss_ml": int(anticipated_blood_loss),
                        "blood_products_planned": blood_products, "admission_date": admission_date,
                        "notes": notes, "status": "Scheduled",
                    },
                    user,
                )
                st.success(f"Case #{op_id} created with pre-op, WHO checklist, score tasks and archive trail.")


def page_ward_board(user: UserContext):
    page_heading(
        "لوحة الردهة الجراحية",
        "Surgical ward board",
        "عرض عملي للحالات الراقدة، NEWS2، استحقاق العلامات الحيوية، والجولة التالية.",
    )
    ops = [x for x in get_operations() if x["status"] not in {"Discharged", "Cancelled", "Closed"}]
    if not ops:
        empty_state("No active inpatients", "No current surgical ward or peri-operative episode was found.", "▦")
        return

    rows = []
    for op in ops:
        vitals = list_vitals(op["id"])
        last = vitals[0] if vitals else None
        due_status, due_detail = _observation_due_status(last)
        rows.append({
            "ID": op["id"],
            "Patient ID": op["patient_id"],
            "MRN": op["mrn"],
            "Patient": op["patient_name"],
            "Ward": op.get("ward") or "Unassigned",
            "Bed": op.get("bed") or "—",
            "POD": calculate_pod(op.get("operation_date")),
            "Procedure": op["operation_name"],
            "Status": op["status"],
            "NEWS2": last["news2"] if last else None,
            "Pain": last.get("pain_score") if last else None,
            "Last observations": last["observed_at"] if last else "Not recorded",
            "Observation status": due_status,
            "Next observation": due_detail,
            "Escalation": last["escalation"] if last else "No observations recorded",
        })
    frame = pd.DataFrame(rows)

    f1, f2, f3 = st.columns(3)
    ward_filter = f1.selectbox("Ward", ["All"] + sorted(frame["Ward"].dropna().unique().tolist()))
    status_filter = f2.selectbox("Pathway status", ["All"] + sorted(frame["Status"].dropna().unique().tolist()))
    observation_filter = f3.selectbox("Observation status", ["All", "Overdue", "Continuous", "Due", "Review"])
    filtered = frame.copy()
    if ward_filter != "All":
        filtered = filtered[filtered["Ward"] == ward_filter]
    if status_filter != "All":
        filtered = filtered[filtered["Status"] == status_filter]
    if observation_filter != "All":
        filtered = filtered[filtered["Observation status"] == observation_filter]

    metrics = st.columns(5)
    metrics[0].metric("Patients", len(filtered))
    metrics[1].metric("Overdue observations", int((filtered["Observation status"] == "Overdue").sum()))
    metrics[2].metric("NEWS2 ≥5", int((pd.to_numeric(filtered["NEWS2"], errors="coerce") >= 5).sum()))
    metrics[3].metric("In theatre/PACU", int(filtered["Status"].isin(["In theatre", "PACU/Recovery"]).sum()))
    metrics[4].metric("Post-op ward", int((filtered["Status"] == "Post-op ward").sum()))

    display_columns = ["Ward", "Bed", "Patient", "MRN", "POD", "Procedure", "Status", "NEWS2", "Pain", "Observation status", "Next observation"]
    st.dataframe(
        filtered[display_columns],
        width="stretch",
        hide_index=True,
        column_config={
            "NEWS2": st.column_config.NumberColumn("NEWS2", format="%d"),
            "Pain": st.column_config.NumberColumn("Pain", format="%d/10"),
        },
    )

    st.markdown("### Patient workspace")
    operation_map = {
        f"{row['Ward']}/{row['Bed']} · {row['Patient']} · {row['Procedure']}": int(row["ID"])
        for _, row in filtered.iterrows()
    }
    if not operation_map:
        st.info("No patient matches the selected filters.")
        return
    selected_label = st.selectbox("Select ward patient", list(operation_map.keys()), key="ward_patient_selector")
    operation_id = operation_map[selected_label]
    operation = get_operation(operation_id)
    snapshot = patient_snapshot(int(operation["patient"]["id"]))
    patient_context_banner(snapshot)
    workflow_stepper(operation.get("status") or "Decision", compact=True)

    latest_vitals = list_vitals(operation_id)
    last = latest_vitals[0] if latest_vitals else None
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("NEWS2", last["news2"] if last else "—")
    c2.metric("Pain", f"{last.get('pain_score')}/10" if last and last.get("pain_score") is not None else "—")
    c3.metric("POD", calculate_pod(operation.get("operation_date")) if calculate_pod(operation.get("operation_date")) is not None else "—")
    due_status, due_detail = _observation_due_status(last)
    c4.metric("Observations", due_status, due_detail)

    a1, a2 = st.columns(2)
    if a1.button("Open full patient chart", width="stretch"):
        navigate(PATIENTS, patient_id=int(operation["patient"]["id"]))
    if a2.button("Open surgical journey", type="primary", width="stretch"):
        navigate(SURGICAL_JOURNEY, patient_id=int(operation["patient"]["id"]), operation_id=operation_id)

    with st.expander("Quick observations / العلامات الحيوية", expanded=user.role == "nurse"):
        _render_vitals(operation_id, user)

    if frame["NEWS2"].notna().any():
        with st.expander("NEWS2 distribution"):
            fig = px.histogram(frame.dropna(subset=["NEWS2"]), x="NEWS2", title="Current NEWS2 distribution")
            st.plotly_chart(fig, width="stretch")

def _render_task_phase(op_id: int, phase: str, user: UserContext):
    tasks = list_tasks(op_id, phase)
    if not tasks:
        st.info("No tasks configured.")
        return
    pending = sum(1 for t in tasks if t["status"] == "pending")
    st.progress((len(tasks) - pending) / len(tasks), text=f"{len(tasks)-pending}/{len(tasks)} completed or dispositioned")
    changes = []
    for task in tasks:
        with st.container(border=True):
            st.write(f"**{task['label_ar']}**")
            st.caption(task["label_en"])
            c1, c2 = st.columns([1, 2])
            status = c1.selectbox("Status", ["pending", "done", "na", "overridden"], index=["pending", "done", "na", "overridden"].index(task["status"]), key=f"task_status_{task['id']}")
            reason = c2.text_input("Reason/comment", value=task.get("override_reason") or "", key=f"task_reason_{task['id']}")
            changes.append((task["id"], status, reason))
    if can(user, "write") and st.button(f"Save {phase} tasks", key=f"save_tasks_{phase}"):
        for task_id, status, reason in changes:
            if status in {"na", "overridden"} and not reason.strip():
                st.error("A reason is required for Not applicable/Overridden items.")
                return
            update_task(task_id, status, reason, user.email)
        st.success("Tasks updated")
        st.rerun()


def _render_who_checklist(op_id: int, user: UserContext):
    for phase in ["Sign-in", "Time-out", "Sign-out"]:
        st.markdown(f"### {phase}")
        if phase == "Time-out":
            st.caption("The final time-out should occur immediately before incision with active participation of the procedure team.")
        items = list_checklist(op_id, phase)
        changes = []
        for item in items:
            with st.container(border=True):
                st.write(f"**{item['text_ar']}**")
                st.caption(item["text_en"])
                c1, c2 = st.columns([1, 2])
                options = ["pending", "yes", "no", "na"]
                answer = c1.selectbox("Answer", options, index=options.index(item["answer"]), key=f"who_ans_{item['id']}")
                comment = c2.text_input("Comment", value=item.get("comment") or "", key=f"who_com_{item['id']}")
                changes.append((item["id"], answer, comment))
        if can(user, "write") and st.button(f"Save {phase}", key=f"save_who_{phase}"):
            for item_id, answer, comment in changes:
                if answer == "no" and not comment.strip():
                    st.error("Document a comment for every No answer.")
                    return
                update_checklist_item(item_id, answer, comment, user.email)
            st.success(f"{phase} saved")
            st.rerun()


def _render_intraop(op_id: int, user: UserContext):
    st.caption("Structured operative note; local medical-record requirements remain authoritative.")
    with st.form(f"intraop_{op_id}"):
        c1, c2, c3 = st.columns(3)
        incision_time = c1.time_input("Incision time", value=time(8, 30))
        closure_time = c1.time_input("Closure time", value=time(9, 30))
        blood_loss = c1.number_input("Estimated blood loss mL", 0, 30000, 0)
        fluids = c2.text_input("IV fluids")
        transfusion = c2.text_input("Blood products/transfusion")
        urine_output = c2.number_input("Urine output mL", 0, 20000, 0)
        specimens = c3.text_area("Specimens and destination")
        drains = c3.text_area("Drains/tubes")
        counts = c3.selectbox("Instrument/sponge/needle counts", ["Correct", "Discrepancy resolved", "Outstanding concern", "Not applicable"])
        findings = st.text_area("Operative findings")
        procedure_done = st.text_area("Procedure performed / key steps")
        complications = st.text_area("Intraoperative complications")
        postop_plan = st.text_area("Immediate postoperative plan")
        sign = st.checkbox("Sign this operative record", value=True)
        submitted = st.form_submit_button("Save intraoperative note", type="primary", disabled=not can(user, "write"))
        if submitted:
            add_clinical_record(op_id, "intraoperative_note", {
                "incision_time": str(incision_time), "closure_time": str(closure_time), "estimated_blood_loss_ml": blood_loss,
                "fluids": fluids, "transfusion": transfusion, "urine_output_ml": urine_output, "specimens": specimens,
                "drains": drains, "counts": counts, "findings": findings, "procedure_performed": procedure_done,
                "complications": complications, "postop_plan": postop_plan,
            }, user.email, signed=sign)
            update_operation(op_id, {"status": "PACU/Recovery"}, user.email)
            st.success("Intraoperative note saved")
    records = list_clinical_records(op_id, "intraoperative_note")
    if records:
        st.dataframe(pd.DataFrame([{"created_at": r["created_at"], "entered_by": r["entered_by"], **r["payload"]} for r in records]), width="stretch")


def _render_pacu(op_id: int, user: UserContext):
    with st.form(f"pacu_{op_id}"):
        st.markdown("### OR → PACU/Ward structured handoff")
        patient_procedure = st.text_area("Patient and procedure")
        history_allergies = st.text_area("Relevant history and allergies")
        airway = st.text_area("Airway/respiratory status")
        circulation = st.text_area("Hemodynamics, blood loss, fluids and transfusion")
        analgesia = st.text_area("Analgesia, antiemetics and antibiotics")
        devices = st.text_area("Lines, tubes, drains and catheters")
        pending = st.text_area("Specimens and pending tests")
        concerns = st.text_area("Complications/special concerns")
        plan = st.text_area("Immediate plan and escalation criteria")
        disposition = st.selectbox("Destination", ["Ward", "HDU", "ICU", "Day-case discharge", "Other"])
        sign = st.checkbox("Sign handoff", value=True)
        if st.form_submit_button("Save PACU handoff", type="primary", disabled=not can(user, "write")):
            add_clinical_record(op_id, "pacu_handoff", {
                "patient_procedure": patient_procedure, "history_allergies": history_allergies, "airway": airway,
                "circulation": circulation, "analgesia_antibiotics": analgesia, "devices": devices,
                "pending": pending, "concerns": concerns, "plan": plan, "disposition": disposition,
            }, user.email, signed=sign)
            update_operation(op_id, {"status": "Post-op ward" if disposition == "Ward" else "PACU/Recovery"}, user.email)
            st.success("Handoff saved")
    records = list_clinical_records(op_id, "pacu_handoff")
    if records:
        st.dataframe(pd.DataFrame([{"created_at": r["created_at"], "entered_by": r["entered_by"], **r["payload"]} for r in records]), width="stretch")


def _render_vitals(op_id: int, user: UserContext):
    st.caption("Morning/evening observations can be entered, but NEWS2 determines whether more frequent monitoring is required.")
    with st.form(f"vitals_{op_id}"):
        c1, c2, c3 = st.columns(3)
        observed_date = c1.date_input("Date", value=date.today())
        observed_time = c1.time_input("Time", value=datetime.now().time().replace(second=0, microsecond=0))
        shift = c1.selectbox("Shift", ["Morning", "Evening", "Night", "Other"])
        rr = c2.number_input("Respiratory rate /min", 1.0, 80.0, 16.0)
        spo2 = c2.number_input("SpO₂ %", 50.0, 100.0, 98.0)
        spo2_scale = c2.selectbox("NEWS2 SpO₂ scale", [1, 2], help="Scale 2 should only be used for patients with a clinician-confirmed target saturation range.")
        oxygen = c2.checkbox("Supplemental oxygen")
        sbp = c3.number_input("Systolic BP mmHg", 30.0, 300.0, 120.0)
        dbp = c3.number_input("Diastolic BP mmHg", 20.0, 200.0, 75.0)
        pulse = c3.number_input("Pulse /min", 20.0, 250.0, 80.0)
        temp = c3.number_input("Temperature °C", 30.0, 45.0, 37.0)
        consciousness = st.selectbox("Consciousness", ["Alert", "New confusion", "Voice", "Pain", "Unresponsive"])
        pain = st.slider("Pain score 0–10", 0, 10, 2)
        urine = st.number_input("Urine output since last review mL (optional)", 0.0, 10000.0, 0.0)
        score, monitoring, escalation = news2_score(rr, spo2, spo2_scale, oxygen, sbp, pulse, temp, consciousness)
        st.metric("Calculated NEWS2", score)
        st.info(f"Monitoring: {monitoring}\n\n{escalation}")
        if st.form_submit_button("Save observation set", type="primary", disabled=not (can(user, "vitals") or can(user, "write"))):
            observed_at = datetime.combine(observed_date, observed_time).replace(tzinfo=_configured_timezone()).astimezone(timezone.utc)
            add_vitals({
                "operation_id": op_id, "observed_at": observed_at, "shift": shift, "respiratory_rate": rr,
                "spo2": spo2, "spo2_scale": spo2_scale, "supplemental_oxygen": oxygen,
                "systolic_bp": sbp, "diastolic_bp": dbp, "pulse": pulse, "temperature": temp,
                "consciousness": consciousness, "pain_score": pain, "urine_output_ml": urine,
                "news2": score, "escalation": f"{monitoring}. {escalation}",
            }, user.email)
            st.success("Vitals and NEWS2 saved")
    vitals = list_vitals(op_id)
    if vitals:
        df = pd.DataFrame(vitals)
        st.dataframe(df[["observed_at", "shift", "respiratory_rate", "spo2", "supplemental_oxygen", "systolic_bp", "diastolic_bp", "pulse", "temperature", "consciousness", "pain_score", "news2", "escalation", "entered_by"]], width="stretch", hide_index=True)
        trend = df.sort_values("observed_at")
        fig = px.line(trend, x="observed_at", y="news2", markers=True, title="NEWS2 trend")
        st.plotly_chart(fig, width="stretch")


def _render_ward_rounds(op_id: int, op: dict, user: UserContext):
    op_date = date.fromisoformat(str(op["operation_date"]))
    pod_default = max((date.today() - op_date).days, 0)
    with st.form(f"ward_round_{op_id}"):
        c1, c2, c3 = st.columns(3)
        round_date = c1.date_input("Round date", value=date.today())
        shift = c1.selectbox("Round", ["Morning", "Evening", "Night/On-call"])
        pod = c1.number_input("Post-op day", 0, 365, pod_default)
        pain = c2.slider("Pain 0–10", 0, 10, 2)
        nausea = c2.selectbox("Nausea/vomiting", ["None", "Mild", "Moderate", "Severe"])
        oral = c2.selectbox("Oral intake", ["NPO", "Sips", "Clear fluids", "Soft diet", "Regular diet", "Not tolerated"])
        urine = c3.text_input("Urine output / urinary status")
        bowel = c3.selectbox("Bowel function", ["No flatus", "Flatus", "Bowel movement", "Stoma functioning", "Not applicable"])
        mobility = c3.selectbox("Mobility", ["Bedbound", "Sits out", "Walks with help", "Independent"])
        symptoms = st.text_area("Symptoms / patient concerns")
        examination = st.text_area("Examination including chest, abdomen and limbs")
        wound = st.selectbox("Wound", ["Not reviewed", "Clean/dry", "Erythema", "Serous discharge", "Purulent discharge", "Dehiscence", "Other"])
        drain = st.text_area("Drains/tubes: type, amount, character")
        labs = st.text_area("Labs/imaging reviewed and pending")
        assessment = st.text_area("Assessment / active problems")
        plan = st.text_area("Plan: fluids, analgesia, antibiotics, VTE prophylaxis, nutrition, mobility, investigations, discharge goals")
        consultant_review = st.checkbox("Reviewed/signed by consultant")
        if st.form_submit_button("Save ward round", type="primary", disabled=not (can(user, "ward") or can(user, "write"))):
            add_ward_round({
                "operation_id": op_id, "round_date": round_date, "shift": shift, "post_op_day": int(pod),
                "payload": {"pain": pain, "nausea_vomiting": nausea, "oral_intake": oral, "urinary": urine,
                            "bowel_function": bowel, "mobility": mobility, "symptoms": symptoms, "examination": examination,
                            "wound": wound, "drain": drain, "labs_imaging": labs, "assessment": assessment, "plan": plan},
                "consultant_signed_by": user.email if consultant_review and can(user, "sign") else None,
                "consultant_signed_at": datetime.now(timezone.utc) if consultant_review and can(user, "sign") else None,
            }, user.email)
            st.success("Ward round saved")
    rounds = list_ward_rounds(op_id)
    if rounds:
        table = []
        for r in rounds:
            table.append({"date": r["round_date"], "shift": r["shift"], "POD": r["post_op_day"], "entered_by": r["entered_by"], **r["payload"]})
        st.dataframe(pd.DataFrame(table), width="stretch", hide_index=True)


def _render_scores(op_id: int, op: dict, user: UserContext):
    patient = op["patient"]
    recommended = suggested_scores(op["operation_code"], op["urgency"], patient.get("age"))
    st.info("Suggested for this case: " + " · ".join(recommended))
    completed = list_score_results(op_id)
    completed_names = {x["score_name"] for x in completed}
    pending = [x for x in recommended if x not in completed_names]
    if pending:
        st.warning("Pending suggested scores: " + " · ".join(pending))
    else:
        st.success("All suggested scores have at least one saved result.")
    selected = st.selectbox("Choose score", recommended + [x for x in ALL_SCORES if x not in recommended])
    result = render_score(selected, prefix=f"op{op_id}_{selected}_", patient=patient)
    if can(user, "write") and st.button("Save score result", type="primary", key=f"save_score_{op_id}_{selected}"):
        add_score_result({"operation_id": op_id, **result}, user.email)
        score_tasks = [t for t in list_tasks(op_id, "Scores") if t["code"] == f"score::{selected}"]
        for task in score_tasks:
            update_task(task["id"], "done", "Calculated and saved", user.email)
        st.success("Score saved")
        st.rerun()
    if completed:
        st.dataframe(pd.DataFrame(completed)[["created_at", "score_name", "result", "risk", "interpretation", "completed_by"]], width="stretch", hide_index=True)


def _render_attachments(op_id: int, user: UserContext):
    if can(user, "files") or can(user, "write"):
        category = st.selectbox("Category", ["Laboratory", "Radiology", "Consent", "Operative document", "Pathology", "Discharge document", "Other"])
        files = st.file_uploader("Upload PDF/JPG/PNG/DICOM-exported PDF", type=["pdf", "png", "jpg", "jpeg", "txt", "csv"], accept_multiple_files=True)
        if st.button("Upload selected files", disabled=not files):
            for file in files:
                raw = file.getvalue()
                if len(raw) > 20 * 1024 * 1024:
                    st.error(f"{file.name}: exceeds 20 MB")
                    continue
                add_attachment(op_id, category, file.name, file.type or "application/octet-stream", raw, user.email)
            st.success("Files uploaded")
            st.rerun()
    rows = list_attachments(op_id)
    for row in rows:
        with st.container(border=True):
            st.write(f"**{row['filename']}**")
            st.caption(f"{row['category']} · {round(row['file_size']/1024,1)} KB · {row['uploaded_by']} · {row['created_at']}")
            obj = get_attachment(row["id"])
            if obj:
                st.download_button("Download", obj.data, obj.filename, obj.mime_type, key=f"download_att_{row['id']}")


def _render_discharge(op_id: int, op: dict, user: UserContext):
    with st.form(f"discharge_{op_id}"):
        discharge_date = st.date_input("Discharge date", value=date.today())
        final_diagnosis = st.text_area("Final diagnosis", value=op.get("diagnosis") or "")
        hospital_course = st.text_area("Hospital course")
        complications = st.text_area("Complications")
        medications = st.text_area("Discharge medications — names, doses and duration")
        wound_care = st.text_area("Wound/drain care")
        diet = st.text_area("Diet")
        activity = st.text_area("Activity and restrictions")
        pathology = st.text_area("Pathology/specimens and pending results")
        followup = st.text_area("Follow-up plan and date")
        red_flags = st.multiselect("Red flags explained", DISCHARGE_RED_FLAGS, default=DISCHARGE_RED_FLAGS[:4])
        sign = st.checkbox("Sign discharge summary", value=True)
        if st.form_submit_button("Save discharge summary", type="primary", disabled=not can(user, "write")):
            add_clinical_record(op_id, "discharge_summary", {
                "discharge_date": str(discharge_date), "final_diagnosis": final_diagnosis, "hospital_course": hospital_course,
                "complications": complications, "medications": medications, "wound_care": wound_care, "diet": diet,
                "activity": activity, "pathology_pending": pathology, "followup": followup, "red_flags": red_flags,
            }, user.email, signed=sign)
            update_operation(op_id, {"status": "Discharged", "discharge_date": discharge_date}, user.email)
            st.success("Discharge summary saved")
    records = list_clinical_records(op_id, "discharge_summary")
    if records:
        _safe_json_download(records[0], f"discharge_operation_{op_id}.json", "Download latest discharge summary")



def _render_followup(op_id: int, op: dict, user: UserContext):
    st.caption("Post-discharge surveillance supports continuity of care and SSI review. Local infection-control definitions remain authoritative.")
    op_date = date.fromisoformat(str(op["operation_date"]))
    with st.form(f"followup_{op_id}"):
        c1, c2, c3 = st.columns(3)
        follow_date = c1.date_input("Follow-up date", value=date.today())
        days_postop = max((follow_date - op_date).days, 0)
        c1.metric("Days after operation", days_postop)
        contact_mode = c1.selectbox("Contact mode", ["Clinic", "Telephone", "Ward/readmission", "Emergency department", "Other"])
        fever = c2.checkbox("Fever/rigors")
        wound_pain = c2.checkbox("Increasing wound pain/tenderness")
        redness = c2.checkbox("Redness/swelling")
        discharge = c2.selectbox("Wound discharge", ["None", "Serous", "Blood-stained", "Purulent", "Unknown"])
        dehiscence = c2.checkbox("Wound separation/dehiscence")
        antibiotics = c3.checkbox("Antibiotics started for suspected infection")
        culture = c3.checkbox("Wound/organ-space culture obtained")
        readmission = c3.checkbox("Readmission")
        reoperation = c3.checkbox("Return to theatre/intervention")
        pathology_reviewed = c3.checkbox("Pathology/pending results reviewed")
        ssi_class = st.selectbox("SSI surveillance classification", ["No SSI identified", "Possible SSI — needs infection-control review", "Superficial incisional SSI", "Deep incisional SSI", "Organ/space SSI", "Insufficient information"])
        symptoms = st.text_area("Other symptoms and examination")
        management = st.text_area("Management, advice and escalation")
        next_followup = st.text_input("Next follow-up / responsible service")
        if st.form_submit_button("Save follow-up", type="primary", disabled=not can(user, "write")):
            add_clinical_record(op_id, "post_discharge_followup", {
                "followup_date": str(follow_date), "days_postop": days_postop, "contact_mode": contact_mode,
                "fever_rigors": fever, "wound_pain": wound_pain, "redness_swelling": redness,
                "wound_discharge": discharge, "dehiscence": dehiscence, "antibiotics_started": antibiotics,
                "culture_obtained": culture, "readmission": readmission, "return_to_theatre": reoperation,
                "pathology_reviewed": pathology_reviewed, "ssi_classification": ssi_class,
                "symptoms_examination": symptoms, "management": management, "next_followup": next_followup,
            }, user.email, signed=True)
            st.success("Follow-up saved")
            st.rerun()
    records = list_clinical_records(op_id, "post_discharge_followup")
    if records:
        table = [{"created_at": r["created_at"], "entered_by": r["entered_by"], **r["payload"]} for r in records]
        st.dataframe(pd.DataFrame(table), width="stretch", hide_index=True)

def page_patient_journey(user: UserContext):
    page_heading(
        "مسار المريض الجراحي",
        "Surgical patient journey",
        "مسار موحد من القرار والتحضير إلى العملية والردهة والخروج والمتابعة.",
    )
    ops = get_operations(include_archived=True)
    if not ops:
        empty_state("No surgical cases", "Add a surgical case first.", "OR")
        return
    option_ids = [int(x["id"]) for x in ops]
    requested_id = st.session_state.get("selected_operation_id")
    default_index = option_ids.index(int(requested_id)) if requested_id and int(requested_id) in option_ids else 0
    op_id = st.selectbox("Select case", option_ids, index=default_index, format_func=_operation_label)
    st.session_state["selected_operation_id"] = int(op_id)
    op = get_operation(op_id)
    patient = op["patient"]
    st.session_state["selected_patient_id"] = int(patient["id"])
    patient_context_banner(patient_snapshot(int(patient["id"])))
    workflow_stepper(op.get("status") or "Decision")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Procedure", op["operation_name"])
    c2.metric("Date", str(op["operation_date"]))
    c3.metric("Surgeon", op["surgeon"])
    c4.metric("Ward / Bed", f"{op.get('ward') or '—'} / {op.get('bed') or '—'}")
    st.caption(f"Diagnosis: {op['diagnosis']} · Urgency: {op['urgency']} · Current status: {op['status']}")

    preop_ready = _tasks_complete(op_id, "Pre-op")
    sign_in_ready = _checklist_phase_complete(op_id, "Sign-in")
    timeout_ready = _checklist_phase_complete(op_id, "Time-out")
    signout_ready = _checklist_phase_complete(op_id, "Sign-out")
    g1, g2, g3, g4 = st.columns(4)
    g1.metric("Pre-op disposition", "Complete" if preop_ready else "Pending")
    g2.metric("WHO Sign-in", "Complete" if sign_in_ready else "Pending")
    g3.metric("WHO Time-out", "Complete" if timeout_ready else "Pending")
    g4.metric("WHO Sign-out", "Complete" if signout_ready else "Pending")
    if op["status"] in {"In theatre", "PACU/Recovery", "Post-op ward", "Discharged"} and not timeout_ready:
        st.error("Safety gate: WHO Time-out is incomplete. Document the team time-out and resolve all concerns according to local policy.")
    if op["status"] in {"PACU/Recovery", "Post-op ward", "Discharged"} and not signout_ready:
        st.warning("WHO Sign-out is incomplete for a case that has left or is leaving theatre.")

    status_col, archive_col = st.columns([3, 1])
    new_status = status_col.selectbox("Case status", STATUS_OPTIONS, index=STATUS_OPTIONS.index(op["status"]) if op["status"] in STATUS_OPTIONS else 0)
    if can(user, "write") and status_col.button("Update status"):
        update_operation(op_id, {"status": new_status}, user.email)
        st.rerun()
    if can(user, "archive") and archive_col.button("Archive case"):
        archive_operation(op_id, user.email)
        st.success("Case archived")
        st.rerun()

    tabs = st.tabs(["Pre-op", "WHO Safety", "Intra-op", "PACU Handoff", "Vitals & NEWS2", "Ward Rounds", "Scores", "Files", "Discharge", "Follow-up", "FHIR & Audit"])
    with tabs[0]:
        _render_task_phase(op_id, "Pre-op", user)
        st.markdown("### ERAS-oriented care elements")
        for item in PRACTICAL_ERAS_ELEMENTS:
            st.caption("• " + item)
    with tabs[1]: _render_who_checklist(op_id, user)
    with tabs[2]: _render_intraop(op_id, user)
    with tabs[3]: _render_pacu(op_id, user)
    with tabs[4]: _render_vitals(op_id, user)
    with tabs[5]: _render_ward_rounds(op_id, op, user)
    with tabs[6]:
        _render_task_phase(op_id, "Scores", user)
        _render_scores(op_id, op, user)
    with tabs[7]: _render_attachments(op_id, user)
    with tabs[8]: _render_discharge(op_id, op, user)
    with tabs[9]: _render_followup(op_id, op, user)
    with tabs[10]:
        vitals = list_vitals(op_id)
        scores = list_score_results(op_id)
        records = list_clinical_records(op_id)
        attachments = list_attachments(op_id)
        bundle = build_fhir_bundle(op, vitals, scores, records, attachments)
        _safe_json_download(bundle, f"operation_{op_id}_fhir_bundle.json", "Download FHIR-style Bundle")
        st.warning("FHIR export requires profiling and conformance testing against the receiving EHR before live integration.")
        logs = [x for x in get_audit_logs(limit=500) if str(x.get("entity_id")) == str(op_id) or x.get("entity_type") in {"vital_sign", "score_result", "ward_round", "attachment", "intraoperative_note", "pacu_handoff", "discharge_summary"}]
        st.dataframe(pd.DataFrame(logs), width="stretch", hide_index=True)


def page_score_library(user: UserContext):
    st.markdown("## Surgical score library")
    st.caption("Each score includes a short Arabic explanation while preserving English medical terminology. Calculators require local clinical validation before formal use.")
    category = st.selectbox("Category", list(SCORE_CATEGORIES))
    selected = st.selectbox("Score", SCORE_CATEGORIES[category])
    st.info(SCORE_DESCRIPTIONS.get(selected, ""))
    result = render_score(selected, prefix=f"library_{selected}_", patient={})
    st.caption("Library calculations are not linked to a patient unless performed inside Patient Journey.")


def page_quality(user: UserContext):
    st.markdown("## Quality, safety and audit")
    ops = get_operations(include_archived=True)
    if not ops:
        st.info("No data available.")
        return
    active = [x for x in ops if not x["archived"]]
    statuses = Counter(x["status"] for x in active)
    high_news = 0
    overdue_observations = 0
    discharged_cases = [x for x in ops if x["status"] == "Discharged"]
    followup_completed = 0
    timeout_completed = 0
    for op in ops:
        vitals = list_vitals(op["id"])
        if any(v["news2"] >= 5 for v in vitals):
            high_news += 1
        if op in active:
            due_status, _ = _observation_due_status(vitals[0] if vitals else None)
            if due_status == "Overdue":
                overdue_observations += 1
        if _checklist_phase_complete(op["id"], "Time-out"):
            timeout_completed += 1
        if op in discharged_cases and list_clinical_records(op["id"], "post_discharge_followup"):
            followup_completed += 1

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total cases", len(ops))
    c2.metric("Active", len(active))
    c3.metric("NEWS2 ≥5", high_news)
    c4.metric("Observations overdue", overdue_observations)
    c5.metric("Discharged", len(discharged_cases))

    q1, q2 = st.columns(2)
    q1.metric("Time-out completion", f"{round(100 * timeout_completed / len(ops), 1)}%" if ops else "0%")
    q2.metric("Discharge follow-up recorded", f"{round(100 * followup_completed / len(discharged_cases), 1)}%" if discharged_cases else "N/A")

    status_df = pd.DataFrame([{"Status": k, "Cases": v} for k, v in statuses.items()])
    if not status_df.empty:
        st.plotly_chart(px.bar(status_df, x="Status", y="Cases", title="Case status"), width="stretch")

    compliance_rows = []
    for op in ops:
        tasks = list_tasks(op["id"], "Pre-op")
        checklist = list_checklist(op["id"])
        followups = list_clinical_records(op["id"], "post_discharge_followup")
        compliance_rows.append({
            "Case": op["id"], "Patient": op["patient_name"], "Procedure": op["operation_name"],
            "Pre-op completion %": round(100 * sum(t["status"] != "pending" for t in tasks) / len(tasks), 1) if tasks else 0,
            "WHO completion %": round(100 * sum(x["answer"] != "pending" for x in checklist) / len(checklist), 1) if checklist else 0,
            "Time-out complete": _checklist_phase_complete(op["id"], "Time-out"),
            "Post-discharge follow-up": bool(followups),
        })
    st.dataframe(pd.DataFrame(compliance_rows), width="stretch", hide_index=True)

    if can(user, "admin"):
        st.markdown("### Audit log")
        st.dataframe(pd.DataFrame(get_audit_logs(limit=500)), width="stretch", hide_index=True)


def page_admin(user: UserContext):
    require(user, "admin")
    st.markdown("## Administration & deployment readiness")
    st.markdown("### Staff roles")
    staff = list_staff()
    for member in staff:
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.write(f"**{member['display_name']}**")
            c1.caption(member["email"])
            role = c2.selectbox("Role", ["admin", "consultant", "resident", "nurse", "viewer"], index=["admin", "consultant", "resident", "nurse", "viewer"].index(member["role"]), key=f"role_{member['id']}")
            active = c3.checkbox("Active", value=member["active"], key=f"active_{member['id']}")
            if st.button("Save staff", key=f"save_staff_{member['id']}"):
                update_staff_role(member["id"], role, active, user.email)
                st.success("Updated")
                st.rerun()

    st.markdown("### Structured backup")
    backup = export_all_tables()
    _safe_json_download(backup, f"surgiscore_backup_{date.today()}.json", "Download JSON backup")
    st.error("Do not treat browser downloads as the only backup. Production deployment requires scheduled encrypted database backups and restore testing.")


def page_governance(user: UserContext):
    st.markdown("## المعايير والجاهزية Standards & readiness")
    st.caption("هذه الصفحة توضح ما تم تطبيقه وما يزال يحتاج اعتماداً واختباراً مؤسسياً. لا تمثل شهادة مطابقة.")

    implemented = [
        ("WHO Surgical Safety workflow", "Sign-in, Time-out and Sign-out with signer, timestamp, comments and audit trail."),
        ("Universal Protocol concepts", "Two identifiers, procedure/site/laterality verification, site marking and documented final time-out."),
        ("ERAS-oriented pathway", "Pre-op optimization, multimodal care elements, early nutrition/mobility and discharge readiness."),
        ("NEWS2", "Scale 1/2, supplemental oxygen, ACVPU, single-red trigger, monitoring frequency and escalation summary."),
        ("Role-based access", "Admin, consultant, resident, nurse and viewer permissions with OIDC-ready authentication."),
        ("Auditability", "Create/update actions recorded with user, timestamp, entity and before/after values where appropriate."),
        ("FHIR R4-style export", "Patient, Encounter, Procedure, Observation and DocumentReference resources for conformance testing."),
    ]
    gaps = [
        "Local multidisciplinary clinical-content approval and signed governance pack",
        "Independent verification of every clinical score and boundary value",
        "Managed PostgreSQL, private object storage and encrypted backup/restore testing",
        "Institutional OIDC/MFA and formal access-review process",
        "FHIR profiling, terminology service and receiving-EHR conformance testing",
        "CDC/NHSN procedure-category mapping and 30/90-day SSI surveillance engine",
        "OWASP ASVS assessment, penetration testing and remediation evidence",
        "Formal health-software lifecycle, hazard log and requirements-to-test traceability",
        "Validated downtime, incident-response and business-continuity procedures",
    ]

    st.markdown("### Implemented in the pilot")
    for title, detail in implemented:
        with st.container(border=True):
            st.write(f"**{title}**")
            st.caption(detail)

    st.markdown("### Required before real clinical adoption")
    for item in gaps:
        st.warning(item)

    st.markdown("### Deployment mode")
    if user.clinical_mode:
        st.success("Clinical mode is enabled. This does not by itself prove production readiness.")
    else:
        st.error("Demo mode is enabled. Identifiable patient data must not be entered.")

    st.markdown("### Governance documents included in the repository")
    st.code(
        "docs/GLOBAL_STANDARDS_MAPPING.md\n"
        "docs/DEPLOYMENT_CHECKLIST.md\n"
        "docs/VALIDATION_AND_GOVERNANCE.md\n"
        "SECURITY.md"
    )
