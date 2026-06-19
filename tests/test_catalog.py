from operations_catalog import LABEL_TO_CODE, OPERATION_BY_CODE, OPERATION_LABELS, suggested_scores


def test_operation_catalog_is_consistent():
    assert len(OPERATION_LABELS) == len(OPERATION_BY_CODE)
    assert len(LABEL_TO_CODE) == len(OPERATION_BY_CODE)


def test_emergency_appendectomy_suggestions():
    scores = suggested_scores("APP-LAP", "Emergency", 70)
    for expected in ["ASA Physical Status", "Caprini VTE", "RCRI", "NEWS2", "Alvarado", "AIR Appendicitis", "Clinical Frailty Scale"]:
        assert expected in scores
