from clinical_logic import meld_na, news2_score


def test_news2_normal_observations():
    score, frequency, escalation = news2_score(
        respiratory_rate=16,
        spo2=98,
        spo2_scale=1,
        supplemental_oxygen=False,
        systolic_bp=120,
        pulse=75,
        temperature=37.0,
        consciousness="Alert",
    )
    assert score == 0
    assert frequency == "Minimum 12-hourly"


def test_news2_single_red_parameter_requires_hourly_monitoring():
    score, frequency, escalation = news2_score(
        respiratory_rate=8,
        spo2=98,
        spo2_scale=1,
        supplemental_oxygen=False,
        systolic_bp=120,
        pulse=75,
        temperature=37.0,
        consciousness="Alert",
    )
    assert score == 3
    assert frequency == "Minimum hourly"
    assert "single parameter" in escalation


def test_news2_high_score_continuous_monitoring():
    score, frequency, _ = news2_score(
        respiratory_rate=30,
        spo2=88,
        spo2_scale=1,
        supplemental_oxygen=True,
        systolic_bp=85,
        pulse=140,
        temperature=39.5,
        consciousness="Confusion",
    )
    assert score >= 7
    assert frequency == "Continuous monitoring"


def test_meld_na_is_capped():
    assert 6 <= meld_na(0.2, 0.7, 0.4, 150) <= 40
    assert 6 <= meld_na(50, 8, 10, 115, dialysis=True) <= 40
