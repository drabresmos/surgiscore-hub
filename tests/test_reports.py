from reports import prescription_html


def test_prescription_html_contains_patient_and_medication():
    html = prescription_html({
        "id": 1,
        "patient": {"full_name": "Test Patient", "mrn": "P001"},
        "items": [{"medication_name": "Paracetamol", "strength": "500 mg", "dosage_form": "Tablet"}],
    })
    assert "Test Patient" in html
    assert "Paracetamol" in html
    assert "P001" in html
