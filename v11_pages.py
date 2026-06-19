from __future__ import annotations

import calendar
from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone
from html import escape
from typing import Any

import pandas as pd
import streamlit as st

from auth import UserContext, can
from clinical_logic import news2_score
from database import (
    acknowledge_result,
    add_patient_attachment,
    add_vitals,
    add_ward_round,
    create_followup,
    create_patient_task,
    get_attachment,
    get_operation,
    get_operations,
    get_patient,
    get_patient_attachment,
    list_allergies,
    list_appointments,
    list_checklist,
    list_encounters,
    list_followups,
    list_operations_for_patient,
    list_patient_attachments,
    list_patient_tasks,
    list_patients,
    list_prescriptions,
    list_problems,
    list_results,
    list_score_results,
    list_tasks,
    list_vitals,
    list_ward_rounds,
    operations_for_month,
    patient_snapshot,
    patient_timeline,
    update_appointment,
    update_operation,
    update_patient_task,
)
from navigation import (
    CLINIC,
    FOLLOWUP,
    NEW_OPERATION,
    PRESCRIBING,
    QUALITY,
    RESULTS,
    SCORES,
    STANDARDS,
    SURGICAL_JOURNEY,
    TASKS,
    THEATRE,
    WARD as LEGACY_WARD,
)
from ui_components import (
    SURGICAL_STAGES,
    calculate_pod,
    empty_state,
    patient_context_banner,
    status_badge,
    workflow_stepper,
)
from v11_routes import MORE, PATIENTS, SURGERY, TODAY, WARD, open_legacy, set_section


ACTIVE_WARD_STATUSES = {"PACU/Recovery", "Post-op ward"}
ACTIVE_SURGERY_STATUSES = {
    "Decision",
    "Pre-op assessment",
    "Scheduled",
    "Ready for theatre",
    "In theatre",
    "PACU/Recovery",
    "Post-op ward",
}


def _parse_datetime(value: Any) -> datetime | None:
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
    observed = _parse_datetime(last.get("observed_at"))
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
    due_at = observed.astimezone(timezone.utc) + interval
    now = datetime.now(timezone.utc)
    if now >= due_at:
        return "Overdue", f"Due since {due_at.strftime('%Y-%m-%d %H:%M UTC')}"
    return "Due", f"Next by {due_at.strftime('%Y-%m-%d %H:%M UTC')}"


def _h(value: Any) -> str:
    return escape(str(value if value not in (None, "") else "—"))


def _as_date(value: Any) -> date | None:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if value:
        try:
            return date.fromisoformat(str(value)[:10])
        except ValueError:
            return None
    return None


def _as_time(value: Any) -> str:
    if isinstance(value, time):
        return value.strftime("%H:%M")
    text = str(value or "")
    return text[:5] if text else "—"


def _title(ar: str, en: str, description: str | None = None) -> None:
    desc = f"<p>{_h(description)}</p>" if description else ""
    st.markdown(
        f"<div class='v11-title'><h1>{_h(ar)} <span style='color:#98a2b3;font-weight:600'>· {_h(en)}</span></h1>{desc}</div>",
        unsafe_allow_html=True,
    )


def _kpi(label: str, value: Any, note: str = "") -> None:
    st.markdown(
        f"<div class='v11-kpi'><span>{_h(label)}</span><b>{_h(value)}</b><small>{_h(note)}</small></div>",
        unsafe_allow_html=True,
    )


def _compact_row(icon: str, title: str, subtitle: str, meta: str = "") -> None:
    st.markdown(
        f"""
        <div class='v11-row'>
          <div class='v11-row-icon'>{_h(icon)}</div>
          <div class='v11-row-copy'><b>{_h(title)}</b><span>{_h(subtitle)}</span></div>
          <div class='v11-row-meta'>{_h(meta)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _alert(text: str, level: str = "warning") -> None:
    css = "danger" if level == "danger" else "success" if level == "success" else ""
    st.markdown(f"<div class='v11-alert {css}'>{_h(text)}</div>", unsafe_allow_html=True)


def _task_complete(status: str | None) -> bool:
    return str(status or "").lower() in {"done", "na", "overridden", "completed"}


def _operation_missing_items(operation_id: int) -> tuple[int, list[str]]:
    tasks = list_tasks(operation_id)
    pending = [x for x in tasks if not _task_complete(x.get("status"))]
    labels = [str(x.get("label_ar") or x.get("label_en") or x.get("code")) for x in pending[:4]]
    return len(pending), labels


def _status_next_action(status: str) -> tuple[str, str]:
    mapping = {
        "Decision": ("أكمل قرار العملية والتحضير", "Open pre-operative assessment"),
        "Pre-op assessment": ("أكمل النواقص قبل الجدولة", "Complete pre-op requirements"),
        "Scheduled": ("راجع الجاهزية قبل دخول العمليات", "Review readiness for theatre"),
        "Ready for theatre": ("ابدأ WHO Sign-in", "Start WHO Sign-in"),
        "In theatre": ("أكمل Time-out وOperative note", "Complete intra-operative documentation"),
        "PACU/Recovery": ("وثّق handoff وخطة المراقبة", "Complete recovery handoff"),
        "Post-op ward": ("سجل العلامات الحيوية والجولة", "Record observations and ward round"),
        "Discharged": ("جدول المتابعة بعد العملية", "Schedule follow-up"),
        "Follow-up": ("وثّق النتيجة وأغلق المسار عند الاكتمال", "Document outcome and close pathway"),
        "Closed": ("المسار مكتمل", "Pathway completed"),
    }
    return mapping.get(status, ("راجع الحالة", "Review case"))


def _patient_button_list(search: str) -> list[dict[str, Any]]:
    patients = list_patients()
    if search.strip():
        q = search.strip().lower()
        patients = [
            p
            for p in patients
            if q in str(p.get("full_name") or "").lower()
            or q in str(p.get("mrn") or "").lower()
            or q in str(p.get("phone") or "").lower()
        ]
    return patients[:40]


@st.dialog("تسجيل العلامات الحيوية / Record observations", width="large")
def record_vitals_dialog(operation_id: int, user: UserContext) -> None:
    op = get_operation(operation_id)
    if not op:
        st.error("Operation not found")
        return
    st.caption(f"{op['patient']['full_name']} · {op['operation_name']}")
    with st.form(f"v11_vitals_{operation_id}"):
        c1, c2, c3 = st.columns(3)
        observed_date = c1.date_input("Date", date.today())
        observed_time = c1.time_input("Time", datetime.now().time().replace(second=0, microsecond=0))
        shift = c1.selectbox("Shift", ["Morning", "Evening", "Night", "Other"])
        rr = c2.number_input("Respiratory rate", 1.0, 80.0, 16.0)
        spo2 = c2.number_input("SpO₂ %", 50.0, 100.0, 98.0)
        scale = c2.selectbox("SpO₂ scale", [1, 2])
        oxygen = c2.checkbox("Supplemental oxygen")
        sbp = c3.number_input("Systolic BP", 30.0, 300.0, 120.0)
        dbp = c3.number_input("Diastolic BP", 20.0, 200.0, 75.0)
        pulse = c3.number_input("Pulse", 20.0, 250.0, 80.0)
        temp = c3.number_input("Temperature °C", 30.0, 45.0, 37.0)
        consciousness = st.selectbox("Consciousness", ["Alert", "New confusion", "Voice", "Pain", "Unresponsive"])
        pain = st.slider("Pain 0–10", 0, 10, 2)
        urine = st.number_input("Urine output mL (optional)", 0.0, 10000.0, 0.0)
        score, monitoring, escalation = news2_score(rr, spo2, scale, oxygen, sbp, pulse, temp, consciousness)
        c4, c5 = st.columns([1, 3])
        c4.metric("NEWS2", score)
        c5.info(f"{monitoring}. {escalation}")
        if st.form_submit_button(
            "حفظ القياسات",
            type="primary",
            disabled=not (can(user, "vitals") or can(user, "write")),
        ):
            observed_at = datetime.combine(observed_date, observed_time).replace(tzinfo=timezone.utc)
            add_vitals(
                {
                    "operation_id": operation_id,
                    "observed_at": observed_at,
                    "shift": shift,
                    "respiratory_rate": rr,
                    "spo2": spo2,
                    "spo2_scale": scale,
                    "supplemental_oxygen": oxygen,
                    "systolic_bp": sbp,
                    "diastolic_bp": dbp,
                    "pulse": pulse,
                    "temperature": temp,
                    "consciousness": consciousness,
                    "pain_score": pain,
                    "urine_output_ml": urine,
                    "news2": score,
                    "escalation": f"{monitoring}. {escalation}",
                },
                user.email,
            )
            st.success("تم حفظ العلامات الحيوية وNEWS2.")
            st.rerun()


@st.dialog("جولة سريعة / Quick ward round", width="large")
def ward_round_dialog(operation_id: int, user: UserContext) -> None:
    op = get_operation(operation_id)
    if not op:
        st.error("Operation not found")
        return
    pod = max(calculate_pod(op.get("operation_date")) or 0, 0)
    st.caption(f"{op['patient']['full_name']} · {op['operation_name']} · POD {pod}")
    with st.form(f"v11_round_{operation_id}"):
        c1, c2, c3 = st.columns(3)
        shift = c1.selectbox("Round", ["Morning", "Evening", "Night/On-call"])
        pain = c1.slider("Pain 0–10", 0, 10, 2)
        oral = c1.selectbox("Oral intake", ["NPO", "Sips", "Clear fluids", "Soft diet", "Regular diet", "Not tolerated"])
        nausea = c2.selectbox("Nausea/vomiting", ["None", "Mild", "Moderate", "Severe"])
        bowel = c2.selectbox("Bowel function", ["No flatus", "Flatus", "Bowel movement", "Stoma functioning", "Not applicable"])
        mobility = c2.selectbox("Mobility", ["Bedbound", "Sits out", "Walks with help", "Independent"])
        wound = c3.selectbox("Wound", ["Not reviewed", "Clean/dry", "Erythema", "Serous discharge", "Purulent discharge", "Dehiscence", "Other"])
        urine = c3.text_input("Urinary status")
        drain = c3.text_input("Drain amount/character")
        assessment = st.text_area("Assessment / active problems")
        plan = st.text_area("Plan for next 24 hours")
        consultant_review = st.checkbox("Consultant reviewed/signed")
        if st.form_submit_button(
            "حفظ الجولة",
            type="primary",
            disabled=not (can(user, "ward") or can(user, "write")),
        ):
            add_ward_round(
                {
                    "operation_id": operation_id,
                    "round_date": date.today(),
                    "shift": shift,
                    "post_op_day": pod,
                    "payload": {
                        "pain": pain,
                        "nausea_vomiting": nausea,
                        "oral_intake": oral,
                        "urinary": urine,
                        "bowel_function": bowel,
                        "mobility": mobility,
                        "wound": wound,
                        "drain": drain,
                        "assessment": assessment,
                        "plan": plan,
                    },
                    "consultant_signed_by": user.email if consultant_review and can(user, "sign") else None,
                    "consultant_signed_at": datetime.now(timezone.utc) if consultant_review and can(user, "sign") else None,
                },
                user.email,
            )
            st.success("تم حفظ الجولة.")
            st.rerun()


@st.dialog("إضافة مهمة للمريض", width="medium")
def add_task_dialog(patient_id: int, user: UserContext) -> None:
    with st.form(f"v11_add_task_{patient_id}"):
        title = st.text_input("Task / المهمة")
        c1, c2 = st.columns(2)
        category = c1.selectbox("Category", ["Results", "Follow-up", "Medication", "Pre-op", "Pathology", "Wound", "Other"])
        due_date = c2.date_input("Due date", date.today())
        priority = c1.selectbox("Priority", ["Routine", "Urgent", "Critical"])
        assigned_to = c2.text_input("Assigned to", user.name)
        notes = st.text_area("Notes")
        if st.form_submit_button("Save", type="primary"):
            if not title.strip():
                st.error("Task title is required.")
            else:
                create_patient_task(
                    {
                        "patient_id": patient_id,
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
                st.success("Task saved.")
                st.rerun()


@st.dialog("جدولة متابعة / Schedule follow-up", width="medium")
def add_followup_dialog(patient_id: int, user: UserContext) -> None:
    with st.form(f"v11_add_followup_{patient_id}"):
        followup_type = st.selectbox(
            "Follow-up type",
            ["Follow-up visit", "Wound review", "Suture/staple removal", "Drain review/removal", "Pathology review", "Telephone review"],
        )
        due_date = st.date_input("Due date", date.today() + timedelta(days=7))
        plan = st.text_area("Plan / reason")
        if st.form_submit_button("Schedule", type="primary"):
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
            st.success("Follow-up scheduled.")
            st.rerun()


def page_today(user: UserContext) -> None:
    _title("اليوم", "Today", "قائمة عمل مختصرة تعرض ما يحتاج تدخلاً الآن.")
    today = date.today()
    appointments = list_appointments(today, today)
    all_operations = get_operations()
    operations_today = [op for op in all_operations if _as_date(op.get("operation_date")) == today]
    ward_operations = [op for op in all_operations if op.get("status") in ACTIVE_WARD_STATUSES]
    unreviewed_results = list_results(unreviewed_only=True)
    overdue_tasks = list_patient_tasks(status="Open", due_before=today)
    due_followups = list_followups(status="Due", due_before=today)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        _kpi("Clinic today", len(appointments), "مواعيد العيادة")
    with k2:
        _kpi("Operations", len(operations_today), "عمليات اليوم")
    with k3:
        _kpi("Ward", len(ward_operations), "مرضى ما بعد العملية")
    with k4:
        _kpi("Needs review", len(unreviewed_results) + len(overdue_tasks), "نتائج ومهام")

    focus = st.segmented_control(
        "عرض",
        ["مطلوب الآن", "العيادة", "العمليات", "الردهة"],
        default="مطلوب الآن",
        label_visibility="collapsed",
        key="v11_today_focus",
    )

    if focus == "مطلوب الآن":
        left, right = st.columns(2)
        with left:
            st.markdown("<div class='v11-section-label'>Priority work</div>", unsafe_allow_html=True)
            shown = 0
            sorted_results = sorted(
                unreviewed_results,
                key=lambda x: 0 if str(x.get("abnormal_flag")) == "Critical" else 1 if str(x.get("abnormal_flag")) == "Abnormal" else 2,
            )
            for result in sorted_results[:5]:
                level = result.get("abnormal_flag") or "New"
                _compact_row(
                    "!",
                    f"{result['patient_name']} · {result['test_name']}",
                    result.get("result_text") or "Result available",
                    level,
                )
                b1, b2 = st.columns(2)
                if b1.button("فتح المريض", key=f"v11_today_result_open_{result['id']}", width="stretch"):
                    set_section(PATIENTS, patient_id=int(result["patient_id"]))
                if can(user, "write") and b2.button("تمت المراجعة", key=f"v11_today_result_ack_{result['id']}", width="stretch"):
                    acknowledge_result(int(result["request_id"]), user.email)
                    st.rerun()
                shown += 1
            for task in overdue_tasks[:5]:
                _compact_row(
                    "✓",
                    f"{task['patient_name']} · {task['title']}",
                    task.get("category") or "Clinical task",
                    f"{task.get('priority') or 'Routine'} · {task.get('due_date') or ''}",
                )
                b1, b2 = st.columns(2)
                if b1.button("فتح المريض", key=f"v11_today_task_open_{task['id']}", width="stretch"):
                    set_section(PATIENTS, patient_id=int(task["patient_id"]))
                if can(user, "write") and b2.button("إكمال", key=f"v11_today_task_done_{task['id']}", width="stretch"):
                    update_patient_task(int(task["id"]), "Completed", user.email)
                    st.rerun()
                shown += 1
            if shown == 0:
                empty_state("لا توجد أعمال متأخرة", "No urgent or overdue items.")

        with right:
            st.markdown("<div class='v11-section-label'>Upcoming today</div>", unsafe_allow_html=True)
            for op in operations_today[:6]:
                missing_count, _ = _operation_missing_items(int(op["id"]))
                _compact_row(
                    _as_time(op.get("start_time")),
                    f"{op['patient_name']} · {op['operation_name']}",
                    f"{op.get('or_room') or 'OR not set'} · {op.get('surgeon') or 'Surgeon not set'}",
                    f"{op['status']} · {missing_count} pending",
                )
                if st.button("فتح مسار العملية", key=f"v11_today_op_{op['id']}", width="stretch"):
                    set_section(SURGERY, patient_id=int(op["patient_id"]), operation_id=int(op["id"]))
            for followup in due_followups[:4]:
                _compact_row(
                    "↻",
                    f"{followup['patient_name']} · {followup['followup_type']}",
                    followup.get("plan") or "Post-operative follow-up",
                    str(followup.get("due_date") or ""),
                )
                if st.button("فتح الملف", key=f"v11_today_followup_{followup['id']}", width="stretch"):
                    set_section(PATIENTS, patient_id=int(followup["patient_id"]))
            if not operations_today and not due_followups:
                empty_state("لا توجد عناصر قادمة", "No operations or follow-ups due today.")

    elif focus == "العيادة":
        st.markdown("<div class='v11-section-label'>Clinic queue</div>", unsafe_allow_html=True)
        if not appointments:
            empty_state("لا توجد مواعيد اليوم", "Add an appointment from Quick add.")
        for appt in appointments:
            _compact_row(
                _as_time(appt.get("start_time")),
                f"{appt['patient_name']} · {appt['appointment_type']}",
                appt.get("reason") or appt.get("location") or "Clinic visit",
                appt["status"],
            )
            cols = st.columns([1, 1, 1])
            if cols[0].button("فتح المريض", key=f"v11_appt_open_{appt['id']}", width="stretch"):
                set_section(PATIENTS, patient_id=int(appt["patient_id"]))
            if can(user, "write") and appt["status"] in {"Scheduled", "Confirmed"}:
                if cols[1].button("Check-in", key=f"v11_appt_checkin_{appt['id']}", width="stretch"):
                    update_appointment(int(appt["id"]), {"status": "Checked-in"}, user.email)
                    st.rerun()
            if can(user, "write") and appt["status"] in {"Checked-in", "Waiting"}:
                if cols[2].button("Start visit", key=f"v11_appt_start_{appt['id']}", width="stretch"):
                    st.session_state["selected_patient_id"] = int(appt["patient_id"])
                    open_legacy(CLINIC, return_section=TODAY, patient_id=int(appt["patient_id"]))

    elif focus == "العمليات":
        st.markdown("<div class='v11-section-label'>Theatre list</div>", unsafe_allow_html=True)
        if not operations_today:
            empty_state("لا توجد عمليات اليوم", "Use New operation to schedule a case.")
        for op in operations_today:
            missing_count, missing_labels = _operation_missing_items(int(op["id"]))
            _compact_row(
                _as_time(op.get("start_time")),
                f"{op['patient_name']} · {op['operation_name']}",
                f"{op.get('or_room') or 'OR not set'} · {op.get('surgeon') or 'Surgeon not set'}",
                f"{op['status']} · {missing_count} pending",
            )
            if missing_labels:
                st.caption("Pending: " + " · ".join(missing_labels))
            if st.button("فتح العملية", key=f"v11_today_theatre_{op['id']}", width="stretch"):
                set_section(SURGERY, patient_id=int(op["patient_id"]), operation_id=int(op["id"]))

    else:
        _render_ward_rows(ward_operations, user, compact=False)


def page_patients(user: UserContext) -> None:
    _title("المرضى", "Patients", "ملف موحد يلخص الحالة والخطة والسجل والنتائج.")
    left, right = st.columns([0.32, 0.68], gap="medium")
    with left:
        search = st.text_input("بحث عن مريض", placeholder="Name, MRN, phone…", key="v11_patient_search")
        patients = _patient_button_list(search)
        st.markdown("<div class='v11-patient-list'>", unsafe_allow_html=True)
        for patient in patients:
            selected = int(st.session_state.get("selected_patient_id") or 0) == int(patient["id"])
            label = f"{patient['full_name']}\n{patient['mrn']} · {patient.get('age') or '—'} y"
            if st.button(
                label,
                key=f"v11_patient_pick_{patient['id']}",
                width="stretch",
                type="primary" if selected else "secondary",
            ):
                st.session_state["selected_patient_id"] = int(patient["id"])
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        if not patients:
            st.info("No matching patient.")

    with right:
        patient_id = st.session_state.get("selected_patient_id")
        if not patient_id:
            empty_state("اختر مريضاً", "Select a patient from the list or use global search.", "♙")
            return
        snapshot = patient_snapshot(int(patient_id))
        if not snapshot:
            st.error("Patient not found.")
            return
        st.markdown("<div class='v11-compact-banner'>", unsafe_allow_html=True)
        patient_context_banner(snapshot)
        st.markdown("</div>", unsafe_allow_html=True)

        tabs = st.tabs(["الملخص Overview", "الخطة Plan", "السجل Timeline", "النتائج Results", "المستندات Documents"])
        with tabs[0]:
            _patient_overview(int(patient_id), snapshot, user)
        with tabs[1]:
            _patient_plan(int(patient_id), snapshot, user)
        with tabs[2]:
            _patient_timeline(int(patient_id))
        with tabs[3]:
            _patient_results(int(patient_id), user)
        with tabs[4]:
            _patient_documents(int(patient_id), user)


def _patient_overview(patient_id: int, snapshot: dict[str, Any], user: UserContext) -> None:
    patient = snapshot["patient"]
    active_operation = snapshot.get("active_operation")
    problems = snapshot.get("active_problems") or []
    meds = snapshot.get("active_medications") or []
    allergies = snapshot.get("allergies") or []
    encounters = list_encounters(patient_id=patient_id, limit=5)
    prescriptions = list_prescriptions(patient_id=patient_id)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='v11-section-label'>Current clinical context</div>", unsafe_allow_html=True)
        if allergies:
            _alert("Allergy: " + ", ".join(str(x.get("substance")) for x in allergies), "danger")
        elif patient.get("allergies"):
            _alert("Allergy status: " + str(patient.get("allergies")))
        else:
            _alert("Allergy status not confirmed", "danger")
        if problems:
            st.markdown("<div class='v11-card'><h3>Active problems</h3>", unsafe_allow_html=True)
            for item in problems[:6]:
                st.markdown(f"• **{_h(item.get('description'))}** · {_h(item.get('severity') or '')}")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No active problem list entries.")
        st.markdown("<div class='v11-card'><h3>Current medications</h3>", unsafe_allow_html=True)
        if meds:
            for med in meds[:8]:
                st.markdown(f"• {_h(med)}")
        else:
            st.caption("No active medication list.")
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='v11-section-label'>Current pathway</div>", unsafe_allow_html=True)
        if active_operation:
            st.markdown(
                f"<div class='v11-op-header'><h2>{_h(active_operation['operation_name'])}</h2>"
                f"<p>{_h(active_operation['operation_date'])} · {_h(active_operation.get('surgeon'))} · {_h(active_operation['status'])}</p></div>",
                unsafe_allow_html=True,
            )
            workflow_stepper(str(active_operation["status"]), compact=True)
            next_ar, next_en = _status_next_action(str(active_operation["status"]))
            _alert(f"Next: {next_ar} · {next_en}", "success")
            if st.button("فتح مسار العملية", key=f"v11_overview_open_op_{active_operation['id']}", width="stretch", type="primary"):
                set_section(SURGERY, patient_id=patient_id, operation_id=int(active_operation["id"]))
        else:
            empty_state("لا توجد عملية فعالة", "No active surgical pathway.", "OR")
        if encounters:
            latest = encounters[0]
            st.markdown("<div class='v11-card'><h3>Latest visit</h3>", unsafe_allow_html=True)
            st.write(f"**{latest.get('encounter_type')}** · {latest.get('encounter_date')} · {latest.get('status')}")
            st.caption(latest.get("assessment") or latest.get("chief_complaint") or "No summary documented")
            st.markdown("</div>", unsafe_allow_html=True)
        if prescriptions:
            latest_rx = prescriptions[0]
            st.caption(f"Latest prescription #{latest_rx['id']} · {latest_rx['status']} · {str(latest_rx['created_at'])[:10]}")

    st.markdown("<div class='v11-section-label'>Quick actions</div>", unsafe_allow_html=True)
    a1, a2, a3, a4 = st.columns(4)
    if a1.button("زيارة عيادة", width="stretch"):
        open_legacy(CLINIC, return_section=PATIENTS, patient_id=patient_id)
    if a2.button("وصفة علاج", width="stretch"):
        open_legacy(PRESCRIBING, return_section=PATIENTS, patient_id=patient_id)
    if a3.button("طلب/نتيجة", width="stretch"):
        open_legacy(RESULTS, return_section=PATIENTS, patient_id=patient_id)
    if a4.button("عملية جديدة", width="stretch"):
        open_legacy(NEW_OPERATION, return_section=PATIENTS, patient_id=patient_id)


def _patient_plan(patient_id: int, snapshot: dict[str, Any], user: UserContext) -> None:
    tasks = list_patient_tasks(patient_id=patient_id, status="Open")
    followups = list_followups(patient_id=patient_id, status="Due")
    active_operation = snapshot.get("active_operation")

    top1, top2 = st.columns(2)
    if top1.button("＋ مهمة", width="stretch", disabled=not can(user, "write")):
        add_task_dialog(patient_id, user)
    if top2.button("＋ متابعة", width="stretch", disabled=not can(user, "write")):
        add_followup_dialog(patient_id, user)

    st.markdown("<div class='v11-section-label'>Care plan</div>", unsafe_allow_html=True)
    if active_operation:
        pending_count, labels = _operation_missing_items(int(active_operation["id"]))
        dot = "done" if pending_count == 0 else "due"
        st.markdown(
            f"<div class='v11-plan-item'><span class='v11-plan-dot {dot}'>{'✓' if pending_count == 0 else '!'}</span>"
            f"<div><b>{_h(active_operation['operation_name'])}</b><br><span>{_h(active_operation['status'])} · {pending_count} pending items</span></div></div>",
            unsafe_allow_html=True,
        )
        for label in labels:
            st.markdown(
                f"<div class='v11-plan-item'><span class='v11-plan-dot due'>○</span><div>{_h(label)}</div></div>",
                unsafe_allow_html=True,
            )
    for task in tasks:
        due = _as_date(task.get("due_date"))
        cls = "due" if due and due <= date.today() else ""
        st.markdown(
            f"<div class='v11-plan-item'><span class='v11-plan-dot {cls}'>○</span>"
            f"<div><b>{_h(task['title'])}</b><br><span>{_h(task.get('category'))} · Due {_h(task.get('due_date'))} · {_h(task.get('priority'))}</span></div></div>",
            unsafe_allow_html=True,
        )
        if can(user, "write") and st.button("Mark completed", key=f"v11_plan_done_{task['id']}"):
            update_patient_task(int(task["id"]), "Completed", user.email)
            st.rerun()
    for followup in followups:
        st.markdown(
            f"<div class='v11-plan-item'><span class='v11-plan-dot due'>↻</span>"
            f"<div><b>{_h(followup['followup_type'])}</b><br><span>Due {_h(followup['due_date'])} · {_h(followup.get('plan'))}</span></div></div>",
            unsafe_allow_html=True,
        )
    if not active_operation and not tasks and not followups:
        empty_state("الخطة فارغة", "Add a task or follow-up to build the patient plan.")


def _patient_timeline(patient_id: int) -> None:
    rows = patient_timeline(patient_id)
    if not rows:
        empty_state("لا يوجد سجل زمني", "Clinical activity will appear here.")
        return
    for row in rows[:80]:
        _compact_row(
            str(row.get("icon") or "•"),
            str(row.get("title") or row.get("type") or "Clinical event"),
            str(row.get("detail") or row.get("description") or ""),
            str(row.get("date") or row.get("created_at") or "")[:16],
        )


def _patient_results(patient_id: int, user: UserContext) -> None:
    results = list_results(patient_id=patient_id)
    if not results:
        empty_state("لا توجد نتائج", "Orders and diagnostic results will appear here.")
        return
    for result in results[:40]:
        flag = result.get("abnormal_flag") or result.get("request_status") or "Result"
        _compact_row(
            "!" if flag in {"Critical", "Abnormal"} else "R",
            result["test_name"],
            result.get("result_text") or f"{result.get('numeric_value') or ''} {result.get('unit') or ''}".strip(),
            flag,
        )
        if can(user, "write") and result.get("request_status") == "Result available":
            if st.button("Acknowledge / تمت المراجعة", key=f"v11_patient_ack_{result['id']}", width="stretch"):
                acknowledge_result(int(result["request_id"]), user.email)
                st.rerun()
    if st.button("فتح Orders & Results", type="primary", width="stretch"):
        open_legacy(RESULTS, return_section=PATIENTS, patient_id=patient_id)


def _patient_documents(patient_id: int, user: UserContext) -> None:
    if can(user, "files") or can(user, "write"):
        category = st.selectbox(
            "Category",
            ["Laboratory", "Radiology", "Pathology", "Clinical photo", "Referral", "Consent", "Other"],
            key="v11_patient_doc_category",
        )
        files = st.file_uploader(
            "Upload document or image",
            type=["pdf", "png", "jpg", "jpeg", "txt", "csv"],
            accept_multiple_files=True,
            key=f"v11_patient_upload_{patient_id}",
        )
        if st.button("رفع الملفات", disabled=not files, type="primary"):
            for file in files or []:
                raw = file.getvalue()
                if len(raw) > 20 * 1024 * 1024:
                    st.error(f"{file.name}: exceeds 20 MB")
                    continue
                add_patient_attachment(
                    patient_id,
                    None,
                    category,
                    file.name,
                    file.type or "application/octet-stream",
                    raw,
                    user.email,
                )
            st.success("Files uploaded.")
            st.rerun()
    rows = list_patient_attachments(patient_id)
    if not rows:
        empty_state("لا توجد مستندات", "Upload reports, imaging exports or clinical photos.")
        return
    for row in rows:
        _compact_row("↧", row["filename"], row.get("category") or "Document", f"{round((row.get('file_size') or 0)/1024,1)} KB")
        obj = get_patient_attachment(int(row["id"]))
        if obj:
            st.download_button(
                "Download",
                data=obj.data,
                file_name=obj.filename,
                mime=obj.mime_type,
                key=f"v11_doc_download_{row['id']}",
                width="stretch",
            )


def page_surgery(user: UserContext) -> None:
    _title("العمليات", "Surgery", "قائمة تشغيلية ومسار واحد لكل عملية من القرار إلى المتابعة.")
    selected_operation_id = st.session_state.get("selected_operation_id")
    if selected_operation_id:
        _surgery_workspace(int(selected_operation_id), user)
        return

    top1, top2 = st.columns([4, 1])
    view = top1.segmented_control("View", ["اليوم", "القادمة", "التقويم"], default="اليوم", label_visibility="collapsed")
    if top2.button("＋ عملية", type="primary", width="stretch"):
        open_legacy(NEW_OPERATION, return_section=SURGERY)

    today = date.today()
    operations = get_operations()
    if view == "اليوم":
        rows = [x for x in operations if _as_date(x.get("operation_date")) == today]
        _operation_list(rows, user)
    elif view == "القادمة":
        rows = [x for x in operations if (_as_date(x.get("operation_date")) or today) >= today]
        rows.sort(key=lambda x: (_as_date(x.get("operation_date")) or today, str(x.get("start_time") or "")))
        _operation_list(rows[:40], user)
    else:
        _surgery_calendar(user)


def _operation_list(rows: list[dict[str, Any]], user: UserContext) -> None:
    if not rows:
        empty_state("لا توجد عمليات", "Create or schedule a surgical case.", "OR")
        return
    for op in rows:
        pending, _ = _operation_missing_items(int(op["id"]))
        _compact_row(
            _as_time(op.get("start_time")),
            f"{op['patient_name']} · {op['operation_name']}",
            f"{op.get('operation_date')} · {op.get('surgeon') or 'Surgeon not set'} · {op.get('or_room') or 'OR not set'}",
            f"{op['status']} · {pending} pending",
        )
        if st.button("فتح المسار", key=f"v11_open_surgery_{op['id']}", width="stretch"):
            set_section(SURGERY, patient_id=int(op["patient_id"]), operation_id=int(op["id"]))


def _surgery_calendar(user: UserContext) -> None:
    today = date.today()
    c1, c2 = st.columns(2)
    month = c1.selectbox("Month", list(range(1, 13)), index=today.month - 1, key="v11_surgery_month")
    year = int(c2.number_input("Year", 2024, 2100, today.year, key="v11_surgery_year"))
    rows = operations_for_month(year, int(month))
    by_day: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        d = _as_date(row.get("operation_date"))
        if d:
            by_day[d.day].append(row)
    headers = st.columns(7)
    for col, label in zip(headers, ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
        col.caption(label)
    for week in calendar.monthcalendar(year, int(month)):
        cols = st.columns(7)
        for col, day_number in zip(cols, week):
            with col:
                if not day_number:
                    st.write("")
                    continue
                day_rows = by_day.get(day_number, [])
                st.markdown(f"**{day_number}**")
                if day_rows:
                    st.caption(f"{len(day_rows)} operation(s)")
                    with st.popover("عرض"):
                        for op in day_rows:
                            st.write(f"{_as_time(op.get('start_time'))} · {op['patient_name']} · {op['operation_name']}")
                            if st.button("Open", key=f"v11_calendar_open_{op['id']}"):
                                set_section(SURGERY, patient_id=int(op["patient_id"]), operation_id=int(op["id"]))
                else:
                    st.caption("—")


def _surgery_workspace(operation_id: int, user: UserContext) -> None:
    op = get_operation(operation_id)
    if not op:
        st.session_state.pop("selected_operation_id", None)
        st.error("Operation not found.")
        return
    if st.button("← الرجوع إلى قائمة العمليات", key="v11_back_surgery_list"):
        st.session_state.pop("selected_operation_id", None)
        st.rerun()

    patient = op["patient"]
    st.markdown(
        f"<div class='v11-op-header'><h2>{_h(op['operation_name'])}</h2>"
        f"<p>{_h(patient['full_name'])} · {_h(patient['mrn'])} · {_h(op['operation_date'])} {_h(_as_time(op.get('start_time')))} · "
        f"{_h(op.get('surgeon'))} · {_h(op.get('or_room'))}</p></div>",
        unsafe_allow_html=True,
    )
    workflow_stepper(str(op["status"]), compact=False)

    pending_count, pending_labels = _operation_missing_items(operation_id)
    score_results = list_score_results(operation_id)
    c1, c2, c3 = st.columns(3)
    c1.metric("Status", op["status"])
    c2.metric("Pending", pending_count)
    c3.metric("Scores", len(score_results))

    next_ar, next_en = _status_next_action(str(op["status"]))
    st.markdown("<div class='v11-stage-panel'>", unsafe_allow_html=True)
    st.markdown(f"### الخطوة التالية · Next action")
    st.write(f"**{next_ar}**")
    st.caption(next_en)
    if pending_labels and op["status"] in {"Decision", "Pre-op assessment", "Scheduled", "Ready for theatre"}:
        st.warning("النواقص الحالية: " + " · ".join(pending_labels))
    st.markdown("</div>", unsafe_allow_html=True)

    stage = str(op["status"])
    if stage in {"Decision", "Pre-op assessment", "Scheduled", "Ready for theatre"}:
        _preop_summary(operation_id)
    elif stage == "In theatre":
        _theatre_summary(operation_id)
    elif stage == "PACU/Recovery":
        _recovery_summary(operation_id)
    elif stage == "Post-op ward":
        _postop_summary(operation_id, user)
    else:
        _followup_summary(int(op["patient_id"]))

    a1, a2, a3 = st.columns(3)
    if a1.button("فتح السجل الكامل", type="primary", width="stretch"):
        open_legacy(SURGICAL_JOURNEY, return_section=SURGERY, patient_id=int(op["patient_id"]), operation_id=operation_id)
    if a2.button("فتح ملف المريض", width="stretch"):
        set_section(PATIENTS, patient_id=int(op["patient_id"]))
    if a3.button("جدول العمليات", width="stretch"):
        open_legacy(THEATRE, return_section=SURGERY, operation_id=operation_id)


def _preop_summary(operation_id: int) -> None:
    tasks = list_tasks(operation_id)
    completed = sum(1 for x in tasks if _task_complete(x.get("status")))
    total = len(tasks)
    st.progress(completed / total if total else 0, text=f"Pre-op completion {completed}/{total}")
    for task in tasks[:12]:
        done = _task_complete(task.get("status"))
        st.markdown(
            f"<div class='v11-plan-item'><span class='v11-plan-dot {'done' if done else 'due'}'>{'✓' if done else '○'}</span>"
            f"<div><b>{_h(task.get('label_ar'))}</b><br><span>{_h(task.get('label_en'))}</span></div></div>",
            unsafe_allow_html=True,
        )


def _theatre_summary(operation_id: int) -> None:
    phases = ["Sign-in", "Time-out", "Sign-out"]
    cols = st.columns(3)
    for col, phase in zip(cols, phases):
        items = list_checklist(operation_id, phase)
        done = sum(1 for x in items if str(x.get("answer")) in {"yes", "na"})
        with col:
            _kpi(phase, f"{done}/{len(items)}", "WHO checklist")


def _recovery_summary(operation_id: int) -> None:
    vitals = list_vitals(operation_id)
    if vitals:
        latest = vitals[0]
        c1, c2, c3 = st.columns(3)
        c1.metric("NEWS2", latest.get("news2"))
        c2.metric("SpO₂", latest.get("spo2"))
        c3.metric("BP", f"{latest.get('systolic_bp')}/{latest.get('diastolic_bp')}")
        st.caption(latest.get("escalation") or "")
    else:
        st.warning("No post-operative observations recorded.")


def _postop_summary(operation_id: int, user: UserContext) -> None:
    vitals = list_vitals(operation_id)
    rounds = list_ward_rounds(operation_id)
    latest = vitals[0] if vitals else None
    due_status, due_text = _observation_due_status(latest)
    c1, c2, c3 = st.columns(3)
    c1.metric("NEWS2", latest.get("news2") if latest else "—")
    c2.metric("Pain", latest.get("pain_score") if latest else "—")
    c3.metric("Rounds", len(rounds))
    if due_status == "Overdue":
        _alert(due_text, "danger")
    else:
        _alert(due_text, "success")
    a1, a2 = st.columns(2)
    if a1.button("تسجيل العلامات الحيوية", width="stretch"):
        record_vitals_dialog(operation_id, user)
    if a2.button("جولة سريعة", width="stretch"):
        ward_round_dialog(operation_id, user)


def _followup_summary(patient_id: int) -> None:
    followups = list_followups(patient_id=patient_id)
    if not followups:
        st.warning("No follow-up plan recorded.")
        return
    for followup in followups[:10]:
        _compact_row("↻", followup["followup_type"], followup.get("plan") or "Follow-up", f"{followup['due_date']} · {followup['status']}")


def _render_ward_rows(rows: list[dict[str, Any]], user: UserContext, compact: bool = True) -> None:
    if not rows:
        empty_state("لا يوجد مرضى في الردهة", "Post-operative ward cases will appear here.", "▦")
        return
    st.markdown(
        "<div class='v11-ward-header'><span>Bed</span><span>Patient</span><span>POD</span><span>NEWS2</span><span>Pain</span><span>Obs</span><span>Actions</span></div>",
        unsafe_allow_html=True,
    )
    for op in rows:
        vitals = list_vitals(int(op["id"]))
        latest = vitals[0] if vitals else None
        news = int(latest.get("news2") or 0) if latest else None
        pain = latest.get("pain_score") if latest else None
        due_status, due_text = _observation_due_status(latest)
        news_class = "high" if news is not None and news >= 7 else "mid" if news is not None and news >= 5 else ""
        st.markdown(
            f"""
            <div class='v11-ward-row'>
              <span>{_h(op.get('bed') or '—')}</span>
              <span><b>{_h(op['patient_name'])}</b><br><span style='color:#667085'>{_h(op['operation_name'])}</span></span>
              <span>{_h(calculate_pod(op.get('operation_date')))}</span>
              <span><span class='v11-news {news_class}'>{_h(news if news is not None else '—')}</span></span>
              <span>{_h(pain if pain is not None else '—')}</span>
              <span class='ward-hide-mobile'>{_h(due_status)}</span>
              <span>{_h(op.get('ward') or 'Ward')}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if due_status == "Overdue":
            st.caption("⚠ " + due_text)
        a1, a2, a3 = st.columns(3)
        if a1.button("Vitals", key=f"v11_ward_vitals_{op['id']}", width="stretch"):
            record_vitals_dialog(int(op["id"]), user)
        if a2.button("Round", key=f"v11_ward_round_{op['id']}", width="stretch"):
            ward_round_dialog(int(op["id"]), user)
        if a3.button("Open", key=f"v11_ward_open_{op['id']}", width="stretch"):
            set_section(SURGERY, patient_id=int(op["patient_id"]), operation_id=int(op["id"]))


def page_ward(user: UserContext) -> None:
    _title("الردهة", "Ward", "لوحة مختصرة للعلامات الحيوية والجولات ومتابعة مرضى ما بعد العملية.")
    operations = [x for x in get_operations() if x.get("status") in ACTIVE_WARD_STATUSES]
    c1, c2, c3 = st.columns(3)
    overdue = 0
    high_news = 0
    for op in operations:
        vitals = list_vitals(int(op["id"]))
        latest = vitals[0] if vitals else None
        due_status, _ = _observation_due_status(latest)
        if due_status == "Overdue":
            overdue += 1
        if latest and int(latest.get("news2") or 0) >= 5:
            high_news += 1
    with c1:
        _kpi("Ward patients", len(operations), "Active post-op cases")
    with c2:
        _kpi("Overdue observations", overdue, "Needs recording")
    with c3:
        _kpi("NEWS2 ≥5", high_news, "Needs review")
    _render_ward_rows(operations, user, compact=False)
    if st.button("فتح Ward board الكامل", width="stretch"):
        open_legacy(LEGACY_WARD, return_section=WARD)


def page_more(user: UserContext) -> None:
    _title("المزيد", "More", "الوحدات الأقل استخداماً مجمعة في مكان واحد لتقليل تشتيت الواجهة.")
    groups = [
        (
            "العيادة والرعاية",
            [
                ("Clinic", "المواعيد والزيارات وقائمة الانتظار", CLINIC),
                ("Orders & Results", "الطلبات والنتائج والمراجعة", RESULTS),
                ("Medications", "الوصفات وMedication reconciliation", PRESCRIBING),
                ("Follow-up", "المتابعات والجروح والنتائج", FOLLOWUP),
                ("Tasks", "المهام السريرية", TASKS),
            ],
        ),
        (
            "الجراحة والأدوات",
            [
                ("New operation", "إنشاء حالة جراحية جديدة", NEW_OPERATION),
                ("Theatre schedule", "تقويم وقائمة العمليات التفصيلية", THEATRE),
                ("Score library", "السكورات والتفسيرات", SCORES),
                ("Quality", "مؤشرات الجودة والنتائج", QUALITY),
                ("Standards", "المعايير والحوكمة", STANDARDS),
            ],
        ),
    ]
    for heading, items in groups:
        st.markdown(f"<div class='v11-section-label'>{_h(heading)}</div>", unsafe_allow_html=True)
        for title, description, route in items:
            c1, c2 = st.columns([5, 1])
            c1.markdown(f"<div class='v11-card'><h3>{_h(title)}</h3><p>{_h(description)}</p></div>", unsafe_allow_html=True)
            if c2.button("فتح", key=f"v11_more_{route}", width="stretch"):
                open_legacy(route, return_section=MORE)

    st.markdown("<div class='v11-section-label'>System</div>", unsafe_allow_html=True)
    st.caption("Advanced modules remain available without appearing in the main daily navigation.")
