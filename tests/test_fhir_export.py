import json

from fhir_export import build_fhir_bundle


def test_fhir_bundle_is_json_serializable():
    operation = {
        "id": 1,
        "patient": {"id": 1, "mrn": "T001", "full_name": "Test Patient", "sex": "Male", "date_of_birth": "1980-01-01", "phone": None},
        "status": "Post-op ward",
        "operation_code": "APP-LAP",
        "operation_name": "Laparoscopic appendectomy",
        "operation_date": "2026-01-01",
        "start_time": "08:00:00",
        "diagnosis": "Acute appendicitis",
        "surgeon": "Test Surgeon",
        "admission_date": "2026-01-01",
        "discharge_date": None,
    }
    vitals = [{
        "observed_at": "2026-01-01T12:00:00+00:00", "respiratory_rate": 16, "spo2": 98,
        "systolic_bp": 120, "diastolic_bp": 75, "pulse": 80, "temperature": 37.0,
        "news2": 0, "escalation": "Routine monitoring",
    }]
    attachments = [{
        "id": 1, "category": "Laboratory", "filename": "cbc.pdf", "mime_type": "application/pdf",
        "file_size": 1234, "created_at": "2026-01-01T10:00:00+00:00",
    }]
    bundle = build_fhir_bundle(operation, vitals, [], [], attachments)
    encoded = json.dumps(bundle)
    assert '"resourceType": "Bundle"' in encoded
    assert "cbc.pdf" in encoded
