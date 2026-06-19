from medication_safety import assess_medication


def test_direct_allergy_conflict_is_hard_stop():
    alerts = assess_medication(
        "Amoxicillin/clavulanate",
        [{"substance": "Penicillin", "reaction": "Anaphylaxis"}],
        [],
    )
    assert any(a["severity"] == "Hard stop" for a in alerts)


def test_duplicate_active_medication_warns():
    alerts = assess_medication("Paracetamol", [], ["Paracetamol"])
    assert any(a["severity"] == "Warning" for a in alerts)


def test_high_risk_information_is_shown():
    alerts = assess_medication("Enoxaparin", [], [])
    assert any(a["severity"] == "Information" for a in alerts)
