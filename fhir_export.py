from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _ref(resource_type: str, resource_id: Any) -> dict[str, str]:
    return {"reference": f"{resource_type}/{resource_id}"}


def build_fhir_bundle(operation: dict, vitals: list[dict], scores: list[dict], records: list[dict], attachments: list[dict]) -> dict:
    """Create a basic HL7 FHIR R4-style transaction-independent Bundle.

    This export is intentionally conservative and must be profiled/validated against the
    receiving EHR's implementation guide before interoperability use.
    """
    patient = operation["patient"]
    patient_id = str(patient["id"])
    op_id = str(operation["id"])
    entries: list[dict] = []

    patient_resource = {
        "resourceType": "Patient",
        "id": patient_id,
        "identifier": [{"system": "urn:surgiscore:mrn", "value": patient["mrn"]}],
        "name": [{"text": patient["full_name"]}],
        "gender": {"Male": "male", "Female": "female"}.get(patient.get("sex"), "unknown"),
    }
    if patient.get("date_of_birth"):
        patient_resource["birthDate"] = str(patient["date_of_birth"])
    if patient.get("phone"):
        patient_resource["telecom"] = [{"system": "phone", "value": patient["phone"]}]
    entries.append({"resource": patient_resource})

    encounter = {
        "resourceType": "Encounter",
        "id": f"enc-{op_id}",
        "status": "finished" if operation.get("status") == "Discharged" else "in-progress",
        "class": {"system": "http://terminology.hl7.org/CodeSystem/v3-ActCode", "code": "IMP", "display": "inpatient encounter"},
        "subject": _ref("Patient", patient_id),
        "period": {"start": str(operation.get("admission_date") or operation.get("operation_date"))},
    }
    if operation.get("discharge_date"):
        encounter["period"]["end"] = str(operation["discharge_date"])
    entries.append({"resource": encounter})

    procedure = {
        "resourceType": "Procedure",
        "id": f"proc-{op_id}",
        "status": "completed" if operation.get("status") in {"Post-op ward", "Discharged"} else "preparation",
        "code": {
            "coding": [{"system": "urn:surgiscore:procedure-catalog", "code": operation["operation_code"], "display": operation["operation_name"]}],
            "text": operation["operation_name"],
        },
        "subject": _ref("Patient", patient_id),
        "encounter": _ref("Encounter", f"enc-{op_id}"),
        "performedDateTime": f"{operation['operation_date']}T{operation.get('start_time') or '00:00:00'}",
        "reasonCode": [{"text": operation.get("diagnosis", "")}],
        "performer": [{"actor": {"display": operation.get("surgeon") or ""}}],
    }
    entries.append({"resource": procedure})

    vital_code_map = {
        "respiratory_rate": ("9279-1", "Respiratory rate"),
        "spo2": ("59408-5", "Oxygen saturation in Arterial blood by Pulse oximetry"),
        "systolic_bp": ("8480-6", "Systolic blood pressure"),
        "diastolic_bp": ("8462-4", "Diastolic blood pressure"),
        "pulse": ("8867-4", "Heart rate"),
        "temperature": ("8310-5", "Body temperature"),
    }
    units = {"respiratory_rate": "/min", "spo2": "%", "systolic_bp": "mm[Hg]", "diastolic_bp": "mm[Hg]", "pulse": "/min", "temperature": "Cel"}
    for vital in vitals:
        for field, (code, display) in vital_code_map.items():
            if vital.get(field) is None:
                continue
            entries.append({
                "resource": {
                    "resourceType": "Observation",
                    "status": "final",
                    "category": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/observation-category", "code": "vital-signs"}]}],
                    "code": {"coding": [{"system": "http://loinc.org", "code": code, "display": display}]},
                    "subject": _ref("Patient", patient_id),
                    "encounter": _ref("Encounter", f"enc-{op_id}"),
                    "effectiveDateTime": vital["observed_at"],
                    "valueQuantity": {"value": vital[field], "unit": units[field]},
                }
            })
        entries.append({
            "resource": {
                "resourceType": "Observation",
                "status": "final",
                "code": {"text": "NEWS2 score"},
                "subject": _ref("Patient", patient_id),
                "encounter": _ref("Encounter", f"enc-{op_id}"),
                "effectiveDateTime": vital["observed_at"],
                "valueInteger": vital["news2"],
                "note": [{"text": vital["escalation"]}],
            }
        })

    for score in scores:
        entries.append({
            "resource": {
                "resourceType": "Observation",
                "status": "final",
                "code": {"text": score["score_name"]},
                "subject": _ref("Patient", patient_id),
                "encounter": _ref("Encounter", f"enc-{op_id}"),
                "effectiveDateTime": score["created_at"],
                "valueString": score["result"],
                "interpretation": [{"text": score["risk"]}],
                "note": [{"text": score["interpretation"]}],
            }
        })

    for record in records:
        entries.append({
            "resource": {
                "resourceType": "DocumentReference",
                "status": "current",
                "type": {"text": record["record_type"]},
                "subject": _ref("Patient", patient_id),
                "context": {"encounter": [_ref("Encounter", f"enc-{op_id}")]},
                "date": record["created_at"],
                "description": str(record.get("payload", {}))[:4000],
            }
        })

    for attachment in attachments:
        entries.append({
            "resource": {
                "resourceType": "DocumentReference",
                "status": "current",
                "type": {"text": attachment["category"]},
                "subject": _ref("Patient", patient_id),
                "context": {"encounter": [_ref("Encounter", f"enc-{op_id}")]},
                "date": attachment["created_at"],
                "content": [{"attachment": {"contentType": attachment["mime_type"], "title": attachment["filename"], "size": attachment["file_size"]}}],
            }
        })

    return {
        "resourceType": "Bundle",
        "type": "collection",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "entry": entries,
    }
