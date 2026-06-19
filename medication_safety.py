from __future__ import annotations

from typing import Iterable


HIGH_RISK_KEYWORDS = {
    "morphine": "Opioid: review sedation, respiratory risk, renal function, and monitoring.",
    "tramadol": "Opioid-like analgesic: review interactions, seizure risk, and renal/hepatic function.",
    "enoxaparin": "Anticoagulant: confirm weight, renal function, bleeding risk, and peri-operative timing.",
    "heparin": "Anticoagulant: confirm indication, bleeding risk, platelet monitoring, and peri-operative timing.",
    "ketorolac": "NSAID: review renal function, GI bleeding risk, and duration.",
    "diclofenac": "NSAID: review renal function, cardiovascular risk, and GI bleeding risk.",
    "ibuprofen": "NSAID: review renal function, GI bleeding risk, and contraindications.",
    "piperacillin": "Antibiotic: document indication, cultures, renal dose review, and review/stop date.",
    "meropenem": "Broad-spectrum antibiotic: document indication, cultures, antimicrobial review, and renal dose review.",
    "ceftriaxone": "Antibiotic: document indication, allergy status, cultures when appropriate, and duration.",
    "amoxicillin": "Beta-lactam antibiotic: check penicillin allergy and document indication/duration.",
}

BETA_LACTAM_KEYWORDS = ("amoxicillin", "penicillin", "piperacillin", "cefazolin", "ceftriaxone", "cefuroxime", "meropenem")
NSAID_KEYWORDS = ("ibuprofen", "diclofenac", "ketorolac", "celecoxib")


def assess_medication(medication_name: str, allergies: Iterable[dict], active_medications: Iterable[str]) -> list[dict[str, str]]:
    name = (medication_name or "").strip().lower()
    alerts: list[dict[str, str]] = []

    for allergy in allergies:
        substance = str(allergy.get("substance") or "").lower()
        if not substance:
            continue
        direct_match = substance in name or name in substance
        beta_lactam_match = ("penicillin" in substance or "beta-lactam" in substance) and any(k in name for k in BETA_LACTAM_KEYWORDS)
        nsaid_match = "nsaid" in substance and any(k in name for k in NSAID_KEYWORDS)
        if direct_match or beta_lactam_match or nsaid_match:
            alerts.append({
                "severity": "Hard stop",
                "message": f"Potential allergy conflict: {allergy.get('substance')} — {allergy.get('reaction') or 'reaction not documented'}.",
            })

    for existing in active_medications:
        existing_name = str(existing).strip().lower()
        if existing_name and (existing_name == name or existing_name in name or name in existing_name):
            alerts.append({"severity": "Warning", "message": f"Possible duplicate active therapy: {existing}."})

    for keyword, message in HIGH_RISK_KEYWORDS.items():
        if keyword in name:
            alerts.append({"severity": "Information", "message": message})

    if not name:
        alerts.append({"severity": "Warning", "message": "Medication name is required."})
    return alerts
