from __future__ import annotations

from datetime import date, datetime
from html import escape
from typing import Any, Iterable

import streamlit as st


SURGICAL_STAGES = [
    "Decision",
    "Pre-op assessment",
    "Scheduled",
    "Ready for theatre",
    "In theatre",
    "PACU/Recovery",
    "Post-op ward",
    "Discharged",
    "Follow-up",
    "Closed",
]

_STATUS_ALIASES = {
    "Pre-op": "Pre-op assessment",
    "Ready": "Ready for theatre",
    "PACU": "PACU/Recovery",
    "Ward": "Post-op ward",
    "Completed": "Closed",
}


def _e(value: Any) -> str:
    return escape(str(value if value not in (None, "") else "—"))


def compact_app_header(hospital_name: str, user_name: str, user_role: str) -> None:
    st.markdown(
        f"""
        <div class="app-shell-header">
          <div class="brand-lockup">
            <div class="brand-mark">S</div>
            <div>
              <div class="brand-title">SurgiScore Clinical EHR</div>
              <div class="brand-subtitle">{_e(hospital_name)}</div>
            </div>
          </div>
          <div class="user-chip">
            <span>{_e(user_name)}</span>
            <b>{_e(user_role)}</b>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_heading(title_ar: str, title_en: str, description: str | None = None) -> None:
    subtitle = f"<p>{_e(description)}</p>" if description else ""
    st.markdown(
        f"""
        <div class="page-heading">
          <div><span class="eyebrow">{_e(title_en).upper()}</span><h1>{_e(title_ar)}</h1>{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_class(status: str) -> str:
    normalized = (status or "").lower()
    if normalized in {"completed", "signed", "reviewed", "done", "closed", "discharged", "active"}:
        return "success"
    if normalized in {"cancelled", "no-show", "critical", "overdue", "failed"}:
        return "danger"
    if normalized in {"waiting", "with doctor", "result available", "due", "urgent", "abnormal", "pending"}:
        return "warning"
    return "info"


def status_badge(status: str) -> str:
    return f"<span class='status {status_class(status)}'>{_e(status)}</span>"


def priority_badge(priority: str) -> str:
    css = "danger" if priority == "Critical" else "warning" if priority == "Urgent" else "info"
    return f"<span class='status {css}'>{_e(priority)}</span>"


def patient_context_banner(snapshot: dict[str, Any]) -> None:
    patient = snapshot.get("patient") or {}
    allergies = snapshot.get("allergies") or []
    active_operation = snapshot.get("active_operation")
    problems = snapshot.get("active_problems") or []
    active_medications = snapshot.get("active_medications") or []
    allergy_text = ", ".join(
        f"{x.get('substance')} ({x.get('reaction') or 'reaction undocumented'})" for x in allergies
    ) or patient.get("allergies") or "Allergy status not confirmed"
    operation_text = (
        f"{active_operation.get('operation_name')} · {active_operation.get('status')}"
        if active_operation
        else "No active surgical case"
    )
    st.markdown(
        f"""
        <div class="patient-context sticky-patient">
          <div class="patient-main">
            <span class="eyebrow">PATIENT CONTEXT</span>
            <h2>{_e(patient.get('full_name'))}</h2>
            <div class="patient-identifiers">
              <span><b>MRN</b> {_e(patient.get('mrn'))}</span>
              <span><b>Age</b> {_e(patient.get('age'))}</span>
              <span><b>Sex</b> {_e(patient.get('sex'))}</span>
              <span><b>Phone</b> {_e(patient.get('phone'))}</span>
              <span><b>Blood</b> {_e(patient.get('blood_group'))}</span>
            </div>
          </div>
          <div class="patient-alerts">
            <div class="alert allergy"><b>Allergies</b><span>{_e(allergy_text)}</span></div>
            <div class="alert operation"><b>Current pathway</b><span>{_e(operation_text)}</span></div>
          </div>
          <div class="patient-counters">
            <span><b>{len(problems)}</b> active problems</span>
            <span><b>{len(active_medications)}</b> active medicines</span>
            <span><b>{len(snapshot.get('unreviewed_results') or [])}</b> new results</span>
            <span><b>{len(snapshot.get('open_tasks') or [])}</b> open tasks</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def workflow_stepper(current_status: str, compact: bool = False) -> None:
    current = _STATUS_ALIASES.get(current_status, current_status)
    try:
        current_index = SURGICAL_STAGES.index(current)
    except ValueError:
        current_index = 0
    nodes = []
    for index, stage in enumerate(SURGICAL_STAGES):
        state = "done" if index < current_index else "active" if index == current_index else "future"
        label = stage if not compact or state in {"active", "done"} else stage.split()[0]
        nodes.append(
            f"<div class='workflow-node {state}'><span>{index + 1}</span><small>{_e(label)}</small></div>"
        )
    st.markdown(
        "<div class='workflow-stepper'>" + "".join(nodes) + "</div>",
        unsafe_allow_html=True,
    )


def work_item_card(
    title: str,
    subtitle: str,
    status: str,
    meta: str | None = None,
    icon: str = "•",
) -> None:
    meta_html = f"<div class='work-meta'>{_e(meta)}</div>" if meta else ""
    st.markdown(
        f"""
        <div class="work-item-card">
          <div class="work-icon">{_e(icon)}</div>
          <div class="work-copy"><b>{_e(title)}</b><span>{_e(subtitle)}</span>{meta_html}</div>
          <div>{status_badge(status)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def empty_state(title: str, detail: str, icon: str = "✓") -> None:
    st.markdown(
        f"""
        <div class="empty-state"><div>{_e(icon)}</div><h3>{_e(title)}</h3><p>{_e(detail)}</p></div>
        """,
        unsafe_allow_html=True,
    )


def calculate_pod(operation_date: Any) -> int | None:
    if not operation_date:
        return None
    if isinstance(operation_date, str):
        try:
            operation_date = date.fromisoformat(operation_date[:10])
        except ValueError:
            return None
    if isinstance(operation_date, datetime):
        operation_date = operation_date.date()
    if not isinstance(operation_date, date):
        return None
    return (date.today() - operation_date).days


def progress_summary(completed: int, total: int, label: str) -> None:
    total = max(total, 1)
    ratio = min(max(completed / total, 0.0), 1.0)
    st.progress(ratio, text=f"{label}: {completed}/{total}")


def render_key_value_grid(items: Iterable[tuple[str, Any]]) -> None:
    cells = "".join(f"<div><span>{_e(k)}</span><b>{_e(v)}</b></div>" for k, v in items)
    st.markdown(f"<div class='key-value-grid'>{cells}</div>", unsafe_allow_html=True)
