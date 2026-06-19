from datetime import date, timedelta

from ui_components import SURGICAL_STAGES, calculate_pod, status_class


def test_surgical_pathway_has_expected_order():
    assert SURGICAL_STAGES[0] == "Decision"
    assert SURGICAL_STAGES.index("In theatre") < SURGICAL_STAGES.index("Post-op ward")
    assert SURGICAL_STAGES[-1] == "Closed"


def test_calculate_pod():
    assert calculate_pod(date.today()) == 0
    assert calculate_pod(date.today() - timedelta(days=3)) == 3
    assert calculate_pod("not-a-date") is None


def test_status_classes():
    assert status_class("Reviewed") == "success"
    assert status_class("Critical") == "danger"
    assert status_class("Due") == "warning"
    assert status_class("Scheduled") == "info"
