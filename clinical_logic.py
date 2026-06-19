from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any


def news2_score(
    respiratory_rate: float,
    spo2: float,
    spo2_scale: int,
    supplemental_oxygen: bool,
    systolic_bp: float,
    pulse: float,
    temperature: float,
    consciousness: str,
) -> tuple[int, str, str]:
    """Calculate NEWS2 and apply the single-parameter red-score rule.

    Returns ``(aggregate_score, monitoring_frequency, escalation_summary)``.
    The local escalation policy and clinical judgement always take precedence.
    """
    components: list[int] = []

    if respiratory_rate <= 8:
        components.append(3)
    elif respiratory_rate <= 11:
        components.append(1)
    elif respiratory_rate <= 20:
        components.append(0)
    elif respiratory_rate <= 24:
        components.append(2)
    else:
        components.append(3)

    if spo2_scale == 2:
        if supplemental_oxygen:
            if spo2 <= 83: components.append(3)
            elif spo2 <= 85: components.append(2)
            elif spo2 <= 87: components.append(1)
            elif spo2 <= 92: components.append(0)
            elif spo2 <= 94: components.append(1)
            elif spo2 <= 96: components.append(2)
            else: components.append(3)
        else:
            if spo2 <= 83: components.append(3)
            elif spo2 <= 85: components.append(2)
            elif spo2 <= 87: components.append(1)
            else: components.append(0)
    else:
        if spo2 <= 91: components.append(3)
        elif spo2 <= 93: components.append(2)
        elif spo2 <= 95: components.append(1)
        else: components.append(0)

    oxygen_score = 2 if supplemental_oxygen else 0
    components.append(oxygen_score)

    if systolic_bp <= 90: components.append(3)
    elif systolic_bp <= 100: components.append(2)
    elif systolic_bp <= 110: components.append(1)
    elif systolic_bp <= 219: components.append(0)
    else: components.append(3)

    if pulse <= 40: components.append(3)
    elif pulse <= 50: components.append(1)
    elif pulse <= 90: components.append(0)
    elif pulse <= 110: components.append(1)
    elif pulse <= 130: components.append(2)
    else: components.append(3)

    components.append(0 if consciousness == "Alert" else 3)

    if temperature <= 35.0: components.append(3)
    elif temperature <= 36.0: components.append(1)
    elif temperature <= 38.0: components.append(0)
    elif temperature <= 39.0: components.append(1)
    else: components.append(2)

    score = sum(components)
    single_red = any(value == 3 for value in components)

    if score == 0:
        monitoring = "Minimum 12-hourly"
        escalation = "Routine NEWS2 monitoring; continue clinical assessment."
    elif score >= 7:
        monitoring = "Continuous monitoring"
        escalation = "Emergency assessment by a team with critical-care competencies; consider transfer to a higher level of care."
    elif score >= 5 or single_red:
        monitoring = "Minimum hourly"
        escalation = "Urgent clinical review and documented escalation plan. A score of 3 in any single parameter is a red trigger."
    else:
        monitoring = "Minimum 4–6 hourly"
        escalation = "Registered nurse assessment; consider increased monitoring and inform the medical team according to local policy."
    return score, monitoring, escalation


def meld_na(bilirubin: float, inr: float, creatinine: float, sodium: float, dialysis: bool = False) -> int:
    """Standard adult MELD-Na calculation with conventional caps.

    This function is for educational/clinical-support use and requires local validation.
    """
    b = max(1.0, float(bilirubin))
    i = max(1.0, float(inr))
    c = 4.0 if dialysis else min(max(float(creatinine), 1.0), 4.0)
    meld = round(10 * (0.957 * math.log(c) + 0.378 * math.log(b) + 1.120 * math.log(i) + 0.643))
    meld = min(max(meld, 6), 40)
    na = min(max(float(sodium), 125), 137)
    adjusted = round(meld + 1.32 * (137 - na) - (0.033 * meld * (137 - na)))
    return min(max(adjusted, 6), 40)


def calculate_age(date_of_birth, on_date=None) -> int | None:
    if not date_of_birth:
        return None
    on_date = on_date or datetime.now(timezone.utc).date()
    years = on_date.year - date_of_birth.year - ((on_date.month, on_date.day) < (date_of_birth.month, date_of_birth.day))
    return max(years, 0)


def risk_label_from_three(score: float, low_max: float, medium_max: float) -> str:
    if score <= low_max:
        return "Low"
    if score <= medium_max:
        return "Medium"
    return "High"


def jsonify_form(values: dict[str, Any]) -> dict[str, Any]:
    out = {}
    for key, value in values.items():
        if hasattr(value, "isoformat"):
            out[key] = value.isoformat()
        else:
            out[key] = value
    return out
