from __future__ import annotations

import json
import os
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Iterable

import streamlit as st
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
    Time,
    create_engine,
    func,
    select,
)
from sqlalchemy.orm import DeclarativeBase, Session, relationship, sessionmaker


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class Staff(Base, TimestampMixin):
    __tablename__ = "staff"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    display_name = Column(String(255), nullable=False)
    role = Column(String(32), nullable=False, default="viewer")
    active = Column(Boolean, nullable=False, default=True)


class Patient(Base, TimestampMixin):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True)
    mrn = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    age = Column(Integer, nullable=True)
    sex = Column(String(32), nullable=False)
    phone = Column(String(64), nullable=True)
    blood_group = Column(String(16), nullable=True)
    allergies = Column(Text, nullable=True)
    emergency_contact = Column(Text, nullable=True)
    active = Column(Boolean, nullable=False, default=True)
    created_by = Column(String(255), nullable=True)
    operations = relationship("Operation", back_populates="patient")


class Operation(Base, TimestampMixin):
    __tablename__ = "operations"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    operation_code = Column(String(64), nullable=False)
    operation_name = Column(String(255), nullable=False)
    category = Column(String(128), nullable=False)
    diagnosis = Column(Text, nullable=False)
    operation_date = Column(Date, nullable=False, index=True)
    start_time = Column(Time, nullable=True)
    expected_duration_min = Column(Integer, nullable=True)
    status = Column(String(64), nullable=False, default="Scheduled", index=True)
    urgency = Column(String(32), nullable=False)
    laterality = Column(String(32), nullable=True)
    surgical_site = Column(String(255), nullable=True)
    surgeon = Column(String(255), nullable=False)
    assistant = Column(String(255), nullable=True)
    anesthetist = Column(String(255), nullable=True)
    planned_anesthesia = Column(String(64), nullable=True)
    ward = Column(String(128), nullable=True)
    bed = Column(String(64), nullable=True)
    or_room = Column(String(64), nullable=True)
    wound_class = Column(String(64), nullable=True)
    anticipated_blood_loss_ml = Column(Integer, nullable=True)
    blood_products_planned = Column(String(255), nullable=True)
    admission_date = Column(Date, nullable=True)
    discharge_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    archived = Column(Boolean, nullable=False, default=False)
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)
    patient = relationship("Patient", back_populates="operations")


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    operation_id = Column(Integer, ForeignKey("operations.id"), nullable=False, index=True)
    phase = Column(String(64), nullable=False, index=True)
    code = Column(String(128), nullable=False)
    label_ar = Column(String(500), nullable=False)
    label_en = Column(String(500), nullable=False)
    status = Column(String(32), nullable=False, default="pending")  # pending/done/overridden/na
    override_reason = Column(Text, nullable=True)
    completed_by = Column(String(255), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)


class ChecklistItem(Base, TimestampMixin):
    __tablename__ = "checklist_items"
    id = Column(Integer, primary_key=True)
    operation_id = Column(Integer, ForeignKey("operations.id"), nullable=False, index=True)
    phase = Column(String(32), nullable=False, index=True)  # sign-in/time-out/sign-out
    code = Column(String(128), nullable=False)
    text_ar = Column(String(500), nullable=False)
    text_en = Column(String(500), nullable=False)
    answer = Column(String(32), nullable=False, default="pending")  # pending/yes/no/na
    comment = Column(Text, nullable=True)
    signed_by = Column(String(255), nullable=True)
    signed_at = Column(DateTime(timezone=True), nullable=True)


class ClinicalRecord(Base, TimestampMixin):
    __tablename__ = "clinical_records"
    id = Column(Integer, primary_key=True)
    operation_id = Column(Integer, ForeignKey("operations.id"), nullable=False, index=True)
    record_type = Column(String(64), nullable=False, index=True)
    payload = Column(JSON, nullable=False, default=dict)
    entered_by = Column(String(255), nullable=True)
    signed_by = Column(String(255), nullable=True)
    signed_at = Column(DateTime(timezone=True), nullable=True)


class VitalSign(Base, TimestampMixin):
    __tablename__ = "vital_signs"
    id = Column(Integer, primary_key=True)
    operation_id = Column(Integer, ForeignKey("operations.id"), nullable=False, index=True)
    observed_at = Column(DateTime(timezone=True), nullable=False, index=True)
    shift = Column(String(32), nullable=False)
    respiratory_rate = Column(Float, nullable=False)
    spo2 = Column(Float, nullable=False)
    spo2_scale = Column(Integer, nullable=False, default=1)
    supplemental_oxygen = Column(Boolean, nullable=False, default=False)
    systolic_bp = Column(Float, nullable=False)
    diastolic_bp = Column(Float, nullable=True)
    pulse = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)
    consciousness = Column(String(32), nullable=False, default="Alert")
    pain_score = Column(Integer, nullable=True)
    urine_output_ml = Column(Float, nullable=True)
    news2 = Column(Integer, nullable=False)
    escalation = Column(Text, nullable=False)
    entered_by = Column(String(255), nullable=True)


class WardRound(Base, TimestampMixin):
    __tablename__ = "ward_rounds"
    id = Column(Integer, primary_key=True)
    operation_id = Column(Integer, ForeignKey("operations.id"), nullable=False, index=True)
    round_date = Column(Date, nullable=False, index=True)
    shift = Column(String(32), nullable=False)
    post_op_day = Column(Integer, nullable=True)
    payload = Column(JSON, nullable=False, default=dict)
    entered_by = Column(String(255), nullable=True)
    consultant_signed_by = Column(String(255), nullable=True)
    consultant_signed_at = Column(DateTime(timezone=True), nullable=True)


class ScoreResult(Base, TimestampMixin):
    __tablename__ = "score_results"
    id = Column(Integer, primary_key=True)
    operation_id = Column(Integer, ForeignKey("operations.id"), nullable=False, index=True)
    score_name = Column(String(128), nullable=False, index=True)
    result = Column(String(255), nullable=False)
    interpretation = Column(Text, nullable=False)
    risk = Column(String(32), nullable=False)
    inputs = Column(JSON, nullable=False, default=dict)
    completed_by = Column(String(255), nullable=True)


class Attachment(Base, TimestampMixin):
    __tablename__ = "attachments"
    id = Column(Integer, primary_key=True)
    operation_id = Column(Integer, ForeignKey("operations.id"), nullable=False, index=True)
    category = Column(String(64), nullable=False)
    filename = Column(String(255), nullable=False)
    mime_type = Column(String(128), nullable=False)
    file_size = Column(Integer, nullable=False)
    data = Column(LargeBinary, nullable=False)
    uploaded_by = Column(String(255), nullable=True)


class Appointment(Base, TimestampMixin):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    appointment_date = Column(Date, nullable=False, index=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=True)
    appointment_type = Column(String(64), nullable=False, index=True)
    status = Column(String(32), nullable=False, default="Scheduled", index=True)
    clinician = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)


class ClinicEncounter(Base, TimestampMixin):
    __tablename__ = "clinic_encounters"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True, index=True)
    encounter_date = Column(Date, nullable=False, index=True)
    encounter_type = Column(String(64), nullable=False, default="Consultation")
    status = Column(String(32), nullable=False, default="Draft", index=True)
    chief_complaint = Column(Text, nullable=True)
    hpi = Column(Text, nullable=True)
    pmh = Column(Text, nullable=True)
    psh = Column(Text, nullable=True)
    current_medications = Column(Text, nullable=True)
    social_history = Column(Text, nullable=True)
    examination = Column(Text, nullable=True)
    assessment = Column(Text, nullable=True)
    diagnosis = Column(Text, nullable=True)
    plan = Column(Text, nullable=True)
    weight_kg = Column(Float, nullable=True)
    height_cm = Column(Float, nullable=True)
    systolic_bp = Column(Float, nullable=True)
    diastolic_bp = Column(Float, nullable=True)
    pulse = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    respiratory_rate = Column(Float, nullable=True)
    spo2 = Column(Float, nullable=True)
    followup_date = Column(Date, nullable=True)
    entered_by = Column(String(255), nullable=True)
    signed_by = Column(String(255), nullable=True)
    signed_at = Column(DateTime(timezone=True), nullable=True)


class Problem(Base, TimestampMixin):
    __tablename__ = "problem_list"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    description = Column(String(500), nullable=False)
    code = Column(String(64), nullable=True)
    status = Column(String(32), nullable=False, default="Active", index=True)
    severity = Column(String(32), nullable=True)
    certainty = Column(String(32), nullable=True)
    onset_date = Column(Date, nullable=True)
    recorded_by = Column(String(255), nullable=True)


class Allergy(Base, TimestampMixin):
    __tablename__ = "allergies"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    substance = Column(String(255), nullable=False)
    reaction = Column(String(500), nullable=True)
    severity = Column(String(32), nullable=True)
    verification = Column(String(32), nullable=False, default="Unconfirmed")
    status = Column(String(32), nullable=False, default="Active")
    recorded_by = Column(String(255), nullable=True)


class Prescription(Base, TimestampMixin):
    __tablename__ = "prescriptions"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    encounter_id = Column(Integer, ForeignKey("clinic_encounters.id"), nullable=True, index=True)
    status = Column(String(32), nullable=False, default="Draft", index=True)
    indication = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    prescribed_by = Column(String(255), nullable=True)
    signed_by = Column(String(255), nullable=True)
    signed_at = Column(DateTime(timezone=True), nullable=True)


class PrescriptionItem(Base, TimestampMixin):
    __tablename__ = "prescription_items"
    id = Column(Integer, primary_key=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=False, index=True)
    medication_name = Column(String(255), nullable=False, index=True)
    brand_name = Column(String(255), nullable=True)
    strength = Column(String(64), nullable=True)
    dosage_form = Column(String(64), nullable=True)
    dose = Column(String(64), nullable=True)
    dose_unit = Column(String(32), nullable=True)
    route = Column(String(64), nullable=True)
    frequency = Column(String(128), nullable=True)
    duration_days = Column(Integer, nullable=True)
    quantity = Column(String(64), nullable=True)
    prn = Column(Boolean, nullable=False, default=False)
    prn_indication = Column(String(255), nullable=True)
    instructions_ar = Column(Text, nullable=True)
    instructions_en = Column(Text, nullable=True)
    item_status = Column(String(32), nullable=False, default="Active")


class MedicationReconciliation(Base, TimestampMixin):
    __tablename__ = "medication_reconciliations"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    encounter_id = Column(Integer, ForeignKey("clinic_encounters.id"), nullable=True, index=True)
    medication_name = Column(String(255), nullable=False)
    home_regimen = Column(String(255), nullable=True)
    action = Column(String(32), nullable=False)
    reason = Column(Text, nullable=True)
    transition = Column(String(64), nullable=False, default="Clinic")
    reconciled_by = Column(String(255), nullable=True)


class ServiceRequest(Base, TimestampMixin):
    __tablename__ = "service_requests"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    encounter_id = Column(Integer, ForeignKey("clinic_encounters.id"), nullable=True, index=True)
    category = Column(String(64), nullable=False, index=True)
    test_name = Column(String(255), nullable=False)
    indication = Column(Text, nullable=True)
    priority = Column(String(32), nullable=False, default="Routine")
    status = Column(String(32), nullable=False, default="Requested", index=True)
    requested_by = Column(String(255), nullable=True)
    reviewed_by = Column(String(255), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)


class DiagnosticResult(Base, TimestampMixin):
    __tablename__ = "diagnostic_results"
    id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey("service_requests.id"), nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    result_text = Column(Text, nullable=True)
    numeric_value = Column(Float, nullable=True)
    unit = Column(String(64), nullable=True)
    reference_range = Column(String(128), nullable=True)
    abnormal_flag = Column(String(32), nullable=True)
    resulted_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    entered_by = Column(String(255), nullable=True)


class FollowUp(Base, TimestampMixin):
    __tablename__ = "followups"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    operation_id = Column(Integer, ForeignKey("operations.id"), nullable=True, index=True)
    encounter_id = Column(Integer, ForeignKey("clinic_encounters.id"), nullable=True, index=True)
    followup_type = Column(String(64), nullable=False)
    due_date = Column(Date, nullable=False, index=True)
    status = Column(String(32), nullable=False, default="Due", index=True)
    pain_score = Column(Integer, nullable=True)
    fever = Column(Boolean, nullable=True)
    wound_status = Column(String(128), nullable=True)
    drain_status = Column(String(255), nullable=True)
    oral_intake = Column(String(128), nullable=True)
    bowel_function = Column(String(128), nullable=True)
    urinary_function = Column(String(128), nullable=True)
    mobility = Column(String(128), nullable=True)
    medication_adherence = Column(String(128), nullable=True)
    adverse_effects = Column(Text, nullable=True)
    assessment = Column(Text, nullable=True)
    plan = Column(Text, nullable=True)
    next_followup_date = Column(Date, nullable=True)
    completed_by = Column(String(255), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)


class PatientTask(Base, TimestampMixin):
    __tablename__ = "patient_tasks"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    encounter_id = Column(Integer, ForeignKey("clinic_encounters.id"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(64), nullable=True)
    due_date = Column(Date, nullable=True, index=True)
    priority = Column(String(32), nullable=False, default="Routine")
    status = Column(String(32), nullable=False, default="Open", index=True)
    assigned_to = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(String(255), nullable=True)


class PatientAttachment(Base, TimestampMixin):
    __tablename__ = "patient_attachments"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    encounter_id = Column(Integer, ForeignKey("clinic_encounters.id"), nullable=True, index=True)
    category = Column(String(64), nullable=False)
    filename = Column(String(255), nullable=False)
    mime_type = Column(String(128), nullable=False)
    file_size = Column(Integer, nullable=False)
    data = Column(LargeBinary, nullable=False)
    uploaded_by = Column(String(255), nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)
    user_email = Column(String(255), nullable=True, index=True)
    action = Column(String(64), nullable=False)
    entity_type = Column(String(64), nullable=False, index=True)
    entity_id = Column(String(64), nullable=True)
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)


@st.cache_resource
def get_engine():
    try:
        database_url = st.secrets.get("DATABASE_URL", "")
    except Exception:
        database_url = ""
    database_url = database_url or os.getenv("DATABASE_URL", "") or "sqlite:///surgiscore_v9.db"
    kwargs: dict[str, Any] = {"pool_pre_ping": True, "future": True}
    if database_url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    return create_engine(database_url, **kwargs)


@st.cache_resource
def get_session_factory():
    return sessionmaker(bind=get_engine(), expire_on_commit=False, class_=Session)


def init_db() -> None:
    Base.metadata.create_all(get_engine())


@contextmanager
def session_scope():
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def model_to_dict(obj: Any) -> dict[str, Any]:
    result = {}
    for column in obj.__table__.columns:
        value = getattr(obj, column.name)
        if isinstance(value, (datetime,)):
            value = value.isoformat()
        elif hasattr(value, "isoformat"):
            value = value.isoformat()
        result[column.name] = value
    return result


def audit(session: Session, user_email: str | None, action: str, entity_type: str, entity_id: Any, old: Any = None, new: Any = None) -> None:
    session.add(
        AuditLog(
            user_email=user_email,
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id is not None else None,
            old_value=old,
            new_value=new,
        )
    )


def ensure_staff(email: str, display_name: str, default_role: str = "viewer") -> Staff:
    with session_scope() as s:
        staff = s.scalar(select(Staff).where(Staff.email == email))
        if staff:
            return staff
        any_staff = s.scalar(select(func.count(Staff.id))) or 0
        role = "admin" if any_staff == 0 else default_role
        staff = Staff(email=email, display_name=display_name or email, role=role, active=True)
        s.add(staff)
        s.flush()
        audit(s, email, "create", "staff", staff.id, new=model_to_dict(staff))
        return staff


def list_staff() -> list[dict[str, Any]]:
    with session_scope() as s:
        return [model_to_dict(x) for x in s.scalars(select(Staff).order_by(Staff.display_name)).all()]


def update_staff_role(staff_id: int, role: str, active: bool, actor: str) -> None:
    with session_scope() as s:
        obj = s.get(Staff, staff_id)
        old = model_to_dict(obj)
        obj.role, obj.active = role, active
        s.flush()
        audit(s, actor, "update", "staff", obj.id, old=old, new=model_to_dict(obj))


def get_or_create_patient(data: dict[str, Any], actor: str) -> Patient:
    with session_scope() as s:
        patient = s.scalar(select(Patient).where(Patient.mrn == data["mrn"]))
        if patient:
            old = model_to_dict(patient)
            for key, value in data.items():
                if value not in (None, ""):
                    setattr(patient, key, value)
            patient.created_by = patient.created_by or actor
            s.flush()
            audit(s, actor, "update", "patient", patient.id, old=old, new=model_to_dict(patient))
            return patient
        patient = Patient(**data, created_by=actor)
        s.add(patient)
        s.flush()
        audit(s, actor, "create", "patient", patient.id, new=model_to_dict(patient))
        return patient


def create_operation(data: dict[str, Any], actor: str) -> Operation:
    with session_scope() as s:
        obj = Operation(**data, created_by=actor, updated_by=actor)
        s.add(obj)
        s.flush()
        audit(s, actor, "create", "operation", obj.id, new=model_to_dict(obj))
        return obj


def update_operation(operation_id: int, changes: dict[str, Any], actor: str) -> Operation:
    with session_scope() as s:
        obj = s.get(Operation, operation_id)
        if not obj:
            raise ValueError("Operation not found")
        old = model_to_dict(obj)
        for k, v in changes.items():
            setattr(obj, k, v)
        obj.updated_by = actor
        s.flush()
        audit(s, actor, "update", "operation", obj.id, old=old, new=model_to_dict(obj))
        return obj


def get_operations(include_archived: bool = False) -> list[dict[str, Any]]:
    with session_scope() as s:
        stmt = select(Operation, Patient).join(Patient, Patient.id == Operation.patient_id)
        if not include_archived:
            stmt = stmt.where(Operation.archived.is_(False))
        stmt = stmt.order_by(Operation.operation_date.desc(), Operation.start_time.desc())
        rows = []
        for op, patient in s.execute(stmt).all():
            d = model_to_dict(op)
            d.update({"patient_name": patient.full_name, "mrn": patient.mrn, "age": patient.age, "sex": patient.sex, "allergies": patient.allergies})
            rows.append(d)
        return rows


def get_operation(operation_id: int) -> dict[str, Any] | None:
    with session_scope() as s:
        row = s.execute(select(Operation, Patient).join(Patient).where(Operation.id == operation_id)).first()
        if not row:
            return None
        op, patient = row
        d = model_to_dict(op)
        d["patient"] = model_to_dict(patient)
        return d


def operations_for_month(year: int, month: int) -> list[dict[str, Any]]:
    with session_scope() as s:
        rows = s.execute(
            select(Operation, Patient)
            .join(Patient)
            .where(func.extract("year", Operation.operation_date) == year)
            .where(func.extract("month", Operation.operation_date) == month)
            .where(Operation.archived.is_(False))
            .order_by(Operation.operation_date, Operation.start_time)
        ).all()
        result = []
        for op, patient in rows:
            d = model_to_dict(op)
            d["patient_name"] = patient.full_name
            d["mrn"] = patient.mrn
            result.append(d)
        return result


def seed_tasks(operation_id: int, tasks: Iterable[dict[str, str]], actor: str) -> None:
    task_items = list(tasks)
    with session_scope() as s:
        count = 0
        for item in task_items:
            existing = s.scalar(select(Task).where(Task.operation_id == operation_id, Task.code == item["code"]))
            if not existing:
                s.add(Task(operation_id=operation_id, **item))
                count += 1
        audit(s, actor, "seed", "tasks", operation_id, new={"count": count})


def list_tasks(operation_id: int, phase: str | None = None) -> list[dict[str, Any]]:
    with session_scope() as s:
        stmt = select(Task).where(Task.operation_id == operation_id)
        if phase:
            stmt = stmt.where(Task.phase == phase)
        stmt = stmt.order_by(Task.phase, Task.id)
        return [model_to_dict(x) for x in s.scalars(stmt).all()]


def update_task(task_id: int, status: str, reason: str, actor: str) -> None:
    with session_scope() as s:
        obj = s.get(Task, task_id)
        old = model_to_dict(obj)
        obj.status = status
        obj.override_reason = reason or None
        obj.completed_by = actor if status in {"done", "overridden", "na"} else None
        obj.completed_at = utcnow() if obj.completed_by else None
        s.flush()
        audit(s, actor, "update", "task", task_id, old=old, new=model_to_dict(obj))


def seed_checklist(operation_id: int, items: Iterable[dict[str, str]], actor: str) -> None:
    with session_scope() as s:
        count = 0
        for item in items:
            existing = s.scalar(select(ChecklistItem).where(ChecklistItem.operation_id == operation_id, ChecklistItem.code == item["code"]))
            if not existing:
                s.add(ChecklistItem(operation_id=operation_id, **item))
                count += 1
        audit(s, actor, "seed", "checklist", operation_id, new={"count": count})


def list_checklist(operation_id: int, phase: str | None = None) -> list[dict[str, Any]]:
    with session_scope() as s:
        stmt = select(ChecklistItem).where(ChecklistItem.operation_id == operation_id)
        if phase:
            stmt = stmt.where(ChecklistItem.phase == phase)
        stmt = stmt.order_by(ChecklistItem.phase, ChecklistItem.id)
        return [model_to_dict(x) for x in s.scalars(stmt).all()]


def update_checklist_item(item_id: int, answer: str, comment: str, actor: str) -> None:
    with session_scope() as s:
        obj = s.get(ChecklistItem, item_id)
        old = model_to_dict(obj)
        obj.answer = answer
        obj.comment = comment or None
        if answer in {"yes", "no", "na"}:
            obj.signed_by = actor
            obj.signed_at = utcnow()
        else:
            obj.signed_by = None
            obj.signed_at = None
        s.flush()
        audit(s, actor, "update", "checklist_item", item_id, old=old, new=model_to_dict(obj))


def add_clinical_record(operation_id: int, record_type: str, payload: dict[str, Any], actor: str, signed: bool = False) -> ClinicalRecord:
    with session_scope() as s:
        obj = ClinicalRecord(
            operation_id=operation_id,
            record_type=record_type,
            payload=payload,
            entered_by=actor,
            signed_by=actor if signed else None,
            signed_at=utcnow() if signed else None,
        )
        s.add(obj)
        s.flush()
        audit(s, actor, "create", record_type, obj.id, new=model_to_dict(obj))
        return obj


def list_clinical_records(operation_id: int, record_type: str | None = None) -> list[dict[str, Any]]:
    with session_scope() as s:
        stmt = select(ClinicalRecord).where(ClinicalRecord.operation_id == operation_id)
        if record_type:
            stmt = stmt.where(ClinicalRecord.record_type == record_type)
        stmt = stmt.order_by(ClinicalRecord.created_at.desc())
        return [model_to_dict(x) for x in s.scalars(stmt).all()]


def add_vitals(data: dict[str, Any], actor: str) -> VitalSign:
    with session_scope() as s:
        obj = VitalSign(**data, entered_by=actor)
        s.add(obj)
        s.flush()
        audit(s, actor, "create", "vital_sign", obj.id, new=model_to_dict(obj))
        return obj


def list_vitals(operation_id: int) -> list[dict[str, Any]]:
    with session_scope() as s:
        stmt = select(VitalSign).where(VitalSign.operation_id == operation_id).order_by(VitalSign.observed_at.desc())
        return [model_to_dict(x) for x in s.scalars(stmt).all()]


def add_ward_round(data: dict[str, Any], actor: str) -> WardRound:
    with session_scope() as s:
        obj = WardRound(**data, entered_by=actor)
        s.add(obj)
        s.flush()
        audit(s, actor, "create", "ward_round", obj.id, new=model_to_dict(obj))
        return obj


def list_ward_rounds(operation_id: int) -> list[dict[str, Any]]:
    with session_scope() as s:
        stmt = select(WardRound).where(WardRound.operation_id == operation_id).order_by(WardRound.round_date.desc(), WardRound.created_at.desc())
        return [model_to_dict(x) for x in s.scalars(stmt).all()]


def add_score_result(data: dict[str, Any], actor: str) -> ScoreResult:
    with session_scope() as s:
        obj = ScoreResult(**data, completed_by=actor)
        s.add(obj)
        s.flush()
        audit(s, actor, "create", "score_result", obj.id, new=model_to_dict(obj))
        return obj


def list_score_results(operation_id: int) -> list[dict[str, Any]]:
    with session_scope() as s:
        stmt = select(ScoreResult).where(ScoreResult.operation_id == operation_id).order_by(ScoreResult.created_at.desc())
        return [model_to_dict(x) for x in s.scalars(stmt).all()]


def add_attachment(operation_id: int, category: str, filename: str, mime_type: str, data: bytes, actor: str) -> Attachment:
    with session_scope() as s:
        obj = Attachment(operation_id=operation_id, category=category, filename=filename, mime_type=mime_type, file_size=len(data), data=data, uploaded_by=actor)
        s.add(obj)
        s.flush()
        audit(s, actor, "create", "attachment", obj.id, new={"filename": filename, "mime_type": mime_type, "file_size": len(data)})
        return obj


def list_attachments(operation_id: int) -> list[dict[str, Any]]:
    """Return attachment metadata only; binary payload is fetched separately."""
    with session_scope() as s:
        stmt = (
            select(
                Attachment.id, Attachment.operation_id, Attachment.category,
                Attachment.filename, Attachment.mime_type, Attachment.file_size,
                Attachment.uploaded_by, Attachment.created_at, Attachment.updated_at,
            )
            .where(Attachment.operation_id == operation_id)
            .order_by(Attachment.created_at.desc())
        )
        rows = []
        for row in s.execute(stmt).mappings().all():
            item = dict(row)
            for key in ("created_at", "updated_at"):
                if item.get(key) is not None:
                    item[key] = item[key].isoformat()
            rows.append(item)
        return rows


def get_attachment(attachment_id: int) -> Attachment | None:
    with session_scope() as s:
        obj = s.get(Attachment, attachment_id)
        if obj:
            s.expunge(obj)
        return obj


def archive_operation(operation_id: int, actor: str) -> None:
    update_operation(operation_id, {"archived": True}, actor)


def get_audit_logs(entity_type: str | None = None, entity_id: str | None = None, limit: int = 500) -> list[dict[str, Any]]:
    with session_scope() as s:
        stmt = select(AuditLog)
        if entity_type:
            stmt = stmt.where(AuditLog.entity_type == entity_type)
        if entity_id:
            stmt = stmt.where(AuditLog.entity_id == str(entity_id))
        stmt = stmt.order_by(AuditLog.created_at.desc()).limit(limit)
        return [model_to_dict(x) for x in s.scalars(stmt).all()]


def export_all_tables() -> dict[str, list[dict[str, Any]]]:
    models = [Staff, Patient, Operation, Task, ChecklistItem, ClinicalRecord, VitalSign, WardRound, ScoreResult, AuditLog]
    out: dict[str, list[dict[str, Any]]] = {}
    with session_scope() as s:
        for model in models:
            out[model.__tablename__] = [model_to_dict(x) for x in s.scalars(select(model)).all()]
    return out

# =========================
# Clinic and longitudinal record functions (v9)
# =========================

def list_patients(active_only: bool = True) -> list[dict[str, Any]]:
    with session_scope() as s:
        stmt = select(Patient)
        if active_only:
            stmt = stmt.where(Patient.active.is_(True))
        stmt = stmt.order_by(Patient.full_name)
        return [model_to_dict(x) for x in s.scalars(stmt).all()]


def get_patient(patient_id: int) -> dict[str, Any] | None:
    with session_scope() as s:
        obj = s.get(Patient, patient_id)
        return model_to_dict(obj) if obj else None


def update_patient(patient_id: int, changes: dict[str, Any], actor: str) -> dict[str, Any]:
    with session_scope() as s:
        obj = s.get(Patient, patient_id)
        if not obj:
            raise ValueError("Patient not found")
        old = model_to_dict(obj)
        for key, value in changes.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        s.flush()
        audit(s, actor, "update", "patient", patient_id, old=old, new=model_to_dict(obj))
        return model_to_dict(obj)


def create_appointment(data: dict[str, Any], actor: str) -> Appointment:
    with session_scope() as s:
        obj = Appointment(**data, created_by=actor, updated_by=actor)
        s.add(obj); s.flush()
        audit(s, actor, "create", "appointment", obj.id, new=model_to_dict(obj))
        return obj


def update_appointment(appointment_id: int, changes: dict[str, Any], actor: str) -> Appointment:
    with session_scope() as s:
        obj = s.get(Appointment, appointment_id)
        if not obj:
            raise ValueError("Appointment not found")
        old = model_to_dict(obj)
        for key, value in changes.items():
            setattr(obj, key, value)
        obj.updated_by = actor
        s.flush(); audit(s, actor, "update", "appointment", obj.id, old=old, new=model_to_dict(obj))
        return obj


def list_appointments(start_date=None, end_date=None, status: str | None = None, patient_id: int | None = None) -> list[dict[str, Any]]:
    with session_scope() as s:
        stmt = select(Appointment, Patient).join(Patient, Patient.id == Appointment.patient_id)
        if start_date:
            stmt = stmt.where(Appointment.appointment_date >= start_date)
        if end_date:
            stmt = stmt.where(Appointment.appointment_date <= end_date)
        if status:
            stmt = stmt.where(Appointment.status == status)
        if patient_id:
            stmt = stmt.where(Appointment.patient_id == patient_id)
        stmt = stmt.order_by(Appointment.appointment_date, Appointment.start_time)
        rows = []
        for appt, patient in s.execute(stmt).all():
            d = model_to_dict(appt)
            d.update({"patient_name": patient.full_name, "mrn": patient.mrn, "patient_phone": patient.phone})
            rows.append(d)
        return rows


def get_appointment(appointment_id: int) -> dict[str, Any] | None:
    with session_scope() as s:
        row = s.execute(select(Appointment, Patient).join(Patient).where(Appointment.id == appointment_id)).first()
        if not row:
            return None
        appt, patient = row
        d = model_to_dict(appt); d["patient"] = model_to_dict(patient)
        return d


def create_encounter(data: dict[str, Any], actor: str, signed: bool = False) -> ClinicEncounter:
    with session_scope() as s:
        payload = dict(data)
        requested_status = payload.pop("status", "Draft")
        obj = ClinicEncounter(
            **payload,
            entered_by=actor,
            signed_by=actor if signed else None,
            signed_at=utcnow() if signed else None,
            status="Signed" if signed else requested_status,
        )
        s.add(obj); s.flush()
        if obj.appointment_id:
            appt = s.get(Appointment, obj.appointment_id)
            if appt:
                appt.status = "Completed" if signed else "With doctor"
                appt.updated_by = actor
        audit(s, actor, "create", "clinic_encounter", obj.id, new=model_to_dict(obj))
        return obj


def update_encounter(encounter_id: int, changes: dict[str, Any], actor: str, sign: bool = False) -> ClinicEncounter:
    with session_scope() as s:
        obj = s.get(ClinicEncounter, encounter_id)
        if not obj:
            raise ValueError("Encounter not found")
        old = model_to_dict(obj)
        for key, value in changes.items():
            if hasattr(obj, key): setattr(obj, key, value)
        if sign:
            obj.status = "Signed"; obj.signed_by = actor; obj.signed_at = utcnow()
        s.flush(); audit(s, actor, "update", "clinic_encounter", obj.id, old=old, new=model_to_dict(obj))
        return obj


def list_encounters(patient_id: int | None = None, limit: int = 200) -> list[dict[str, Any]]:
    with session_scope() as s:
        stmt = select(ClinicEncounter, Patient).join(Patient, Patient.id == ClinicEncounter.patient_id)
        if patient_id:
            stmt = stmt.where(ClinicEncounter.patient_id == patient_id)
        stmt = stmt.order_by(ClinicEncounter.encounter_date.desc(), ClinicEncounter.created_at.desc()).limit(limit)
        rows=[]
        for enc, patient in s.execute(stmt).all():
            d=model_to_dict(enc); d.update({"patient_name":patient.full_name,"mrn":patient.mrn}); rows.append(d)
        return rows


def get_encounter(encounter_id: int) -> dict[str, Any] | None:
    with session_scope() as s:
        obj=s.get(ClinicEncounter, encounter_id)
        return model_to_dict(obj) if obj else None


def add_problem(data: dict[str, Any], actor: str) -> Problem:
    with session_scope() as s:
        obj=Problem(**data, recorded_by=actor); s.add(obj); s.flush()
        audit(s, actor, "create", "problem", obj.id, new=model_to_dict(obj)); return obj


def list_problems(patient_id: int, include_resolved: bool = True) -> list[dict[str, Any]]:
    with session_scope() as s:
        stmt=select(Problem).where(Problem.patient_id==patient_id)
        if not include_resolved: stmt=stmt.where(Problem.status=="Active")
        return [model_to_dict(x) for x in s.scalars(stmt.order_by(Problem.status, Problem.created_at.desc())).all()]


def update_problem(problem_id: int, status: str, actor: str) -> None:
    with session_scope() as s:
        obj=s.get(Problem, problem_id); old=model_to_dict(obj); obj.status=status; s.flush()
        audit(s, actor, "update", "problem", problem_id, old=old, new=model_to_dict(obj))


def add_allergy(data: dict[str, Any], actor: str) -> Allergy:
    with session_scope() as s:
        obj=Allergy(**data, recorded_by=actor); s.add(obj); s.flush()
        audit(s, actor, "create", "allergy", obj.id, new=model_to_dict(obj)); return obj


def list_allergies(patient_id: int, active_only: bool = True) -> list[dict[str, Any]]:
    with session_scope() as s:
        stmt=select(Allergy).where(Allergy.patient_id==patient_id)
        if active_only: stmt=stmt.where(Allergy.status=="Active")
        return [model_to_dict(x) for x in s.scalars(stmt.order_by(Allergy.created_at.desc())).all()]


def update_allergy(allergy_id: int, status: str, actor: str) -> None:
    with session_scope() as s:
        obj=s.get(Allergy, allergy_id); old=model_to_dict(obj); obj.status=status; s.flush()
        audit(s, actor, "update", "allergy", allergy_id, old=old, new=model_to_dict(obj))


def create_prescription(patient_id: int, encounter_id: int | None, indication: str, notes: str, actor: str) -> Prescription:
    with session_scope() as s:
        obj=Prescription(patient_id=patient_id, encounter_id=encounter_id, indication=indication or None, notes=notes or None, prescribed_by=actor)
        s.add(obj); s.flush(); audit(s, actor, "create", "prescription", obj.id, new=model_to_dict(obj)); return obj


def add_prescription_item(prescription_id: int, data: dict[str, Any], actor: str) -> PrescriptionItem:
    with session_scope() as s:
        obj=PrescriptionItem(prescription_id=prescription_id, **data); s.add(obj); s.flush()
        audit(s, actor, "create", "prescription_item", obj.id, new=model_to_dict(obj)); return obj


def sign_prescription(prescription_id: int, actor: str) -> Prescription:
    with session_scope() as s:
        obj=s.get(Prescription, prescription_id)
        if not obj: raise ValueError("Prescription not found")
        old=model_to_dict(obj); obj.status="Active"; obj.signed_by=actor; obj.signed_at=utcnow(); s.flush()
        audit(s, actor, "sign", "prescription", obj.id, old=old, new=model_to_dict(obj)); return obj


def list_prescriptions(patient_id: int | None = None, status: str | None = None) -> list[dict[str, Any]]:
    with session_scope() as s:
        stmt=select(Prescription, Patient).join(Patient, Patient.id==Prescription.patient_id)
        if patient_id: stmt=stmt.where(Prescription.patient_id==patient_id)
        if status: stmt=stmt.where(Prescription.status==status)
        stmt=stmt.order_by(Prescription.created_at.desc())
        rows=[]
        for rx, patient in s.execute(stmt).all():
            d=model_to_dict(rx); d.update({"patient_name":patient.full_name,"mrn":patient.mrn}); rows.append(d)
        return rows


def get_prescription(prescription_id: int) -> dict[str, Any] | None:
    with session_scope() as s:
        row=s.execute(select(Prescription, Patient).join(Patient).where(Prescription.id==prescription_id)).first()
        if not row: return None
        rx, patient=row; d=model_to_dict(rx); d["patient"]=model_to_dict(patient)
        d["items"]=[model_to_dict(x) for x in s.scalars(select(PrescriptionItem).where(PrescriptionItem.prescription_id==prescription_id)).all()]
        return d


def list_active_medication_names(patient_id: int) -> list[str]:
    with session_scope() as s:
        stmt=(select(PrescriptionItem.medication_name)
              .join(Prescription, Prescription.id==PrescriptionItem.prescription_id)
              .where(Prescription.patient_id==patient_id, Prescription.status=="Active", PrescriptionItem.item_status=="Active"))
        return [str(x) for x in s.scalars(stmt).all()]


def add_medication_reconciliation(data: dict[str, Any], actor: str) -> MedicationReconciliation:
    with session_scope() as s:
        obj=MedicationReconciliation(**data, reconciled_by=actor); s.add(obj); s.flush()
        audit(s, actor, "create", "medication_reconciliation", obj.id, new=model_to_dict(obj)); return obj


def list_medication_reconciliations(patient_id: int) -> list[dict[str, Any]]:
    with session_scope() as s:
        stmt=select(MedicationReconciliation).where(MedicationReconciliation.patient_id==patient_id).order_by(MedicationReconciliation.created_at.desc())
        return [model_to_dict(x) for x in s.scalars(stmt).all()]


def create_service_request(data: dict[str, Any], actor: str) -> ServiceRequest:
    with session_scope() as s:
        obj=ServiceRequest(**data, requested_by=actor); s.add(obj); s.flush()
        audit(s, actor, "create", "service_request", obj.id, new=model_to_dict(obj)); return obj


def list_service_requests(patient_id: int | None = None, status: str | None = None) -> list[dict[str, Any]]:
    with session_scope() as s:
        stmt=select(ServiceRequest, Patient).join(Patient, Patient.id==ServiceRequest.patient_id)
        if patient_id: stmt=stmt.where(ServiceRequest.patient_id==patient_id)
        if status: stmt=stmt.where(ServiceRequest.status==status)
        stmt=stmt.order_by(ServiceRequest.created_at.desc())
        rows=[]
        for req, patient in s.execute(stmt).all():
            d=model_to_dict(req); d.update({"patient_name":patient.full_name,"mrn":patient.mrn}); rows.append(d)
        return rows


def add_diagnostic_result(request_id: int, patient_id: int, data: dict[str, Any], actor: str) -> DiagnosticResult:
    with session_scope() as s:
        obj=DiagnosticResult(request_id=request_id, patient_id=patient_id, **data, entered_by=actor)
        s.add(obj)
        req=s.get(ServiceRequest, request_id)
        if req: req.status="Result available"
        s.flush(); audit(s, actor, "create", "diagnostic_result", obj.id, new=model_to_dict(obj)); return obj


def list_results(patient_id: int | None = None, unreviewed_only: bool = False) -> list[dict[str, Any]]:
    with session_scope() as s:
        stmt=(select(DiagnosticResult, ServiceRequest, Patient)
              .join(ServiceRequest, ServiceRequest.id==DiagnosticResult.request_id)
              .join(Patient, Patient.id==DiagnosticResult.patient_id))
        if patient_id: stmt=stmt.where(DiagnosticResult.patient_id==patient_id)
        if unreviewed_only: stmt=stmt.where(ServiceRequest.status=="Result available")
        stmt=stmt.order_by(DiagnosticResult.resulted_at.desc())
        rows=[]
        for result, req, patient in s.execute(stmt).all():
            d=model_to_dict(result); d.update({"test_name":req.test_name,"category":req.category,"request_status":req.status,"patient_name":patient.full_name,"mrn":patient.mrn,"priority":req.priority}); rows.append(d)
        return rows


def acknowledge_result(request_id: int, actor: str) -> None:
    with session_scope() as s:
        req=s.get(ServiceRequest, request_id)
        if not req: raise ValueError("Request not found")
        old=model_to_dict(req); req.status="Reviewed"; req.reviewed_by=actor; req.reviewed_at=utcnow(); s.flush()
        audit(s, actor, "review", "service_request", req.id, old=old, new=model_to_dict(req))


def create_followup(data: dict[str, Any], actor: str) -> FollowUp:
    with session_scope() as s:
        obj=FollowUp(**data); s.add(obj); s.flush(); audit(s, actor, "create", "followup", obj.id, new=model_to_dict(obj)); return obj


def update_followup(followup_id: int, changes: dict[str, Any], actor: str, complete: bool = False) -> FollowUp:
    with session_scope() as s:
        obj=s.get(FollowUp, followup_id)
        if not obj: raise ValueError("Follow-up not found")
        old=model_to_dict(obj)
        for key,value in changes.items():
            if hasattr(obj,key): setattr(obj,key,value)
        if complete:
            obj.status="Completed"; obj.completed_by=actor; obj.completed_at=utcnow()
        s.flush(); audit(s, actor, "update", "followup", obj.id, old=old, new=model_to_dict(obj)); return obj


def list_followups(patient_id: int | None = None, status: str | None = None, due_before=None) -> list[dict[str, Any]]:
    with session_scope() as s:
        stmt=select(FollowUp, Patient).join(Patient, Patient.id==FollowUp.patient_id)
        if patient_id: stmt=stmt.where(FollowUp.patient_id==patient_id)
        if status: stmt=stmt.where(FollowUp.status==status)
        if due_before: stmt=stmt.where(FollowUp.due_date<=due_before)
        stmt=stmt.order_by(FollowUp.due_date)
        rows=[]
        for f, patient in s.execute(stmt).all():
            d=model_to_dict(f); d.update({"patient_name":patient.full_name,"mrn":patient.mrn}); rows.append(d)
        return rows


def create_patient_task(data: dict[str, Any], actor: str) -> PatientTask:
    with session_scope() as s:
        obj=PatientTask(**data, created_by=actor); s.add(obj); s.flush(); audit(s, actor, "create", "patient_task", obj.id, new=model_to_dict(obj)); return obj


def list_patient_tasks(patient_id: int | None = None, status: str | None = None, due_before=None) -> list[dict[str, Any]]:
    with session_scope() as s:
        stmt=select(PatientTask, Patient).join(Patient, Patient.id==PatientTask.patient_id)
        if patient_id: stmt=stmt.where(PatientTask.patient_id==patient_id)
        if status: stmt=stmt.where(PatientTask.status==status)
        if due_before: stmt=stmt.where(PatientTask.due_date<=due_before)
        stmt=stmt.order_by(PatientTask.due_date, PatientTask.priority)
        rows=[]
        for task, patient in s.execute(stmt).all():
            d=model_to_dict(task); d.update({"patient_name":patient.full_name,"mrn":patient.mrn}); rows.append(d)
        return rows


def update_patient_task(task_id: int, status: str, actor: str) -> None:
    with session_scope() as s:
        obj=s.get(PatientTask, task_id); old=model_to_dict(obj); obj.status=status; s.flush()
        audit(s, actor, "update", "patient_task", task_id, old=old, new=model_to_dict(obj))


def add_patient_attachment(patient_id: int, encounter_id: int | None, category: str, filename: str, mime_type: str, data: bytes, actor: str) -> PatientAttachment:
    with session_scope() as s:
        obj=PatientAttachment(patient_id=patient_id, encounter_id=encounter_id, category=category, filename=filename, mime_type=mime_type, file_size=len(data), data=data, uploaded_by=actor)
        s.add(obj); s.flush(); audit(s, actor, "create", "patient_attachment", obj.id, new={"filename":filename,"file_size":len(data)}); return obj


def list_patient_attachments(patient_id: int) -> list[dict[str, Any]]:
    with session_scope() as s:
        stmt=select(PatientAttachment.id, PatientAttachment.patient_id, PatientAttachment.encounter_id, PatientAttachment.category, PatientAttachment.filename, PatientAttachment.mime_type, PatientAttachment.file_size, PatientAttachment.uploaded_by, PatientAttachment.created_at).where(PatientAttachment.patient_id==patient_id).order_by(PatientAttachment.created_at.desc())
        rows=[]
        for row in s.execute(stmt).mappings().all():
            d=dict(row)
            if d.get("created_at"): d["created_at"]=d["created_at"].isoformat()
            rows.append(d)
        return rows


def get_patient_attachment(attachment_id: int) -> PatientAttachment | None:
    with session_scope() as s:
        obj=s.get(PatientAttachment, attachment_id)
        if obj: s.expunge(obj)
        return obj


def patient_timeline(patient_id: int) -> list[dict[str, Any]]:
    events=[]
    for a in list_appointments(patient_id=patient_id):
        events.append({"date":str(a["appointment_date"]),"type":"Appointment","title":a["appointment_type"],"detail":a.get("reason") or a["status"],"status":a["status"]})
    for e in list_encounters(patient_id=patient_id):
        events.append({"date":str(e["encounter_date"]),"type":"Encounter","title":e["encounter_type"],"detail":e.get("diagnosis") or e.get("chief_complaint") or "","status":e["status"]})
    for o in get_operations(include_archived=True):
        if int(o["patient_id"])==int(patient_id):
            events.append({"date":str(o["operation_date"]),"type":"Operation","title":o["operation_name"],"detail":o.get("diagnosis") or "","status":o["status"]})
    for r in list_prescriptions(patient_id=patient_id):
        events.append({"date":str(r["created_at"])[:10],"type":"Prescription","title":f"Prescription #{r['id']}","detail":r.get("indication") or "","status":r["status"]})
    for f in list_followups(patient_id=patient_id):
        events.append({"date":str(f["due_date"]),"type":"Follow-up","title":f["followup_type"],"detail":f.get("assessment") or "","status":f["status"]})
    return sorted(events, key=lambda x:x["date"], reverse=True)


# Extend full backup with v9 clinic tables.
_old_export_all_tables = export_all_tables

def export_all_tables() -> dict[str, list[dict[str, Any]]]:
    out = _old_export_all_tables()
    extra_models = [Appointment, ClinicEncounter, Problem, Allergy, Prescription, PrescriptionItem, MedicationReconciliation, ServiceRequest, DiagnosticResult, FollowUp, PatientTask]
    with session_scope() as s:
        for model in extra_models:
            out[model.__tablename__] = [model_to_dict(x) for x in s.scalars(select(model)).all()]
    return out

# =========================
# Workflow and navigation helpers (v10)
# =========================

def search_records(query: str, limit: int = 12) -> dict[str, list[dict[str, Any]]]:
    """Search the main clinical records used by the global command bar.

    The function intentionally returns only display-safe metadata. It does not
    expose attachment bytes or free-text clinical records in search results.
    """
    q = (query or "").strip()
    if len(q) < 2:
        return {"patients": [], "appointments": [], "operations": [], "results": []}
    pattern = f"%{q}%"
    with session_scope() as s:
        patients_stmt = (
            select(Patient)
            .where(
                Patient.active.is_(True),
                (
                    Patient.full_name.ilike(pattern)
                    | Patient.mrn.ilike(pattern)
                    | func.coalesce(Patient.phone, "").ilike(pattern)
                ),
            )
            .order_by(Patient.full_name)
            .limit(limit)
        )
        patients = [model_to_dict(x) for x in s.scalars(patients_stmt).all()]

        operations_stmt = (
            select(Operation, Patient)
            .join(Patient, Patient.id == Operation.patient_id)
            .where(
                Operation.archived.is_(False),
                (
                    Operation.operation_name.ilike(pattern)
                    | Operation.diagnosis.ilike(pattern)
                    | Patient.full_name.ilike(pattern)
                    | Patient.mrn.ilike(pattern)
                    | func.coalesce(Operation.surgeon, "").ilike(pattern)
                ),
            )
            .order_by(Operation.operation_date.desc())
            .limit(limit)
        )
        operations: list[dict[str, Any]] = []
        for operation, patient in s.execute(operations_stmt).all():
            row = model_to_dict(operation)
            row.update({"patient_name": patient.full_name, "mrn": patient.mrn})
            operations.append(row)

        appointments_stmt = (
            select(Appointment, Patient)
            .join(Patient, Patient.id == Appointment.patient_id)
            .where(
                Patient.full_name.ilike(pattern)
                | Patient.mrn.ilike(pattern)
                | Appointment.appointment_type.ilike(pattern)
                | func.coalesce(Appointment.clinician, "").ilike(pattern)
            )
            .order_by(Appointment.appointment_date.desc(), Appointment.start_time.desc())
            .limit(limit)
        )
        appointments: list[dict[str, Any]] = []
        for appointment, patient in s.execute(appointments_stmt).all():
            row = model_to_dict(appointment)
            row.update({"patient_name": patient.full_name, "mrn": patient.mrn})
            appointments.append(row)

        results_stmt = (
            select(DiagnosticResult, ServiceRequest, Patient)
            .join(ServiceRequest, ServiceRequest.id == DiagnosticResult.request_id)
            .join(Patient, Patient.id == DiagnosticResult.patient_id)
            .where(
                Patient.full_name.ilike(pattern)
                | Patient.mrn.ilike(pattern)
                | ServiceRequest.test_name.ilike(pattern)
            )
            .order_by(DiagnosticResult.resulted_at.desc())
            .limit(limit)
        )
        results: list[dict[str, Any]] = []
        for result, request, patient in s.execute(results_stmt).all():
            row = model_to_dict(result)
            row.update(
                {
                    "test_name": request.test_name,
                    "request_status": request.status,
                    "patient_name": patient.full_name,
                    "mrn": patient.mrn,
                }
            )
            results.append(row)

    return {
        "patients": patients,
        "appointments": appointments,
        "operations": operations,
        "results": results,
    }


def list_operations_for_patient(patient_id: int, include_archived: bool = True) -> list[dict[str, Any]]:
    with session_scope() as s:
        stmt = select(Operation).where(Operation.patient_id == patient_id)
        if not include_archived:
            stmt = stmt.where(Operation.archived.is_(False))
        stmt = stmt.order_by(Operation.operation_date.desc(), Operation.start_time.desc())
        return [model_to_dict(x) for x in s.scalars(stmt).all()]


def patient_snapshot(patient_id: int) -> dict[str, Any]:
    """Return the concise longitudinal context used by the patient banner."""
    patient = get_patient(patient_id)
    if not patient:
        return {}
    operations = list_operations_for_patient(patient_id, include_archived=False)
    active_operation = next(
        (
            op
            for op in operations
            if op.get("status") not in {"Discharged", "Cancelled", "Closed"}
        ),
        None,
    )
    problems = [x for x in list_problems(patient_id, include_resolved=False) if x.get("status") == "Active"]
    allergies = list_allergies(patient_id, active_only=True)
    active_medications = list_active_medication_names(patient_id)
    open_tasks = list_patient_tasks(patient_id=patient_id, status="Open")
    unreviewed_results = list_results(patient_id=patient_id, unreviewed_only=True)
    due_followups = list_followups(patient_id=patient_id, status="Due")
    return {
        "patient": patient,
        "active_operation": active_operation,
        "active_problems": problems,
        "allergies": allergies,
        "active_medications": active_medications,
        "open_tasks": open_tasks,
        "unreviewed_results": unreviewed_results,
        "due_followups": due_followups,
    }
