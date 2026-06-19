from __future__ import annotations

import math
from typing import Any

import streamlit as st

from clinical_logic import meld_na
from operations_catalog import SCORE_DESCRIPTIONS


SCORE_CATEGORIES = {
    "Perioperative": ["ASA Physical Status", "Caprini VTE", "RCRI", "Clinical Frailty Scale", "STOP-Bang"],
    "Deterioration & Sepsis": ["NEWS2", "qSOFA", "SIRS", "Shock Index"],
    "Appendicitis": ["Alvarado", "AIR Appendicitis"],
    "Biliary & Pancreas": ["Tokyo Cholecystitis Grade", "ASGE CBD Stone Risk", "BISAP", "Ranson"],
    "GI Bleeding": ["Glasgow-Blatchford", "AIMS65", "Rockall Pre-Endoscopy"],
    "Peritonitis": ["Mannheim Peritonitis Index", "Boey"],
    "Liver": ["Child-Pugh", "MELD-Na"],
    "Trauma & Postoperative": ["GCS", "Clavien-Dindo", "CDC SSI Classification"],
}
ALL_SCORES = [x for values in SCORE_CATEGORIES.values() for x in values]


def _cb(label: str, points: int, key: str) -> int:
    return points if st.checkbox(f"{label} (+{points})", key=key) else 0


def _show_description(name: str) -> None:
    st.caption(SCORE_DESCRIPTIONS.get(name, "أداة دعم سريري يجب تفسيرها ضمن الحالة السريرية وسياسة المؤسسة."))


def render_score(name: str, prefix: str, patient: dict[str, Any] | None = None) -> dict[str, Any]:
    patient = patient or {}
    _show_description(name)
    inputs: dict[str, Any] = {}
    result: str | int | float = ""
    interpretation = ""
    risk = "Medium"

    if name == "ASA Physical Status":
        choice = st.selectbox(
            "ASA class",
            [
                "ASA I — Normal healthy patient",
                "ASA II — Mild systemic disease",
                "ASA III — Severe systemic disease",
                "ASA IV — Severe systemic disease that is a constant threat to life",
                "ASA V — Moribund patient not expected to survive without the operation",
                "ASA VI — Declared brain-dead organ donor",
            ],
            key=f"{prefix}_asa",
        )
        emergency = st.checkbox("Emergency modifier (E)", key=f"{prefix}_asa_e")
        result = choice.split(" — ")[0] + ("E" if emergency else "")
        interpretation = choice
        risk = "Low" if result.startswith(("ASA I", "ASA II")) else "High" if result.startswith(("ASA IV", "ASA V")) else "Medium"
        inputs = {"class": choice, "emergency": emergency}

    elif name == "RCRI":
        s = sum(
            [
                _cb("High-risk surgery", 1, f"{prefix}r1"),
                _cb("History of ischemic heart disease", 1, f"{prefix}r2"),
                _cb("History of congestive heart failure", 1, f"{prefix}r3"),
                _cb("History of cerebrovascular disease", 1, f"{prefix}r4"),
                _cb("Preoperative treatment with insulin", 1, f"{prefix}r5"),
                _cb("Preoperative creatinine >2 mg/dL", 1, f"{prefix}r6"),
            ]
        )
        result = s
        interpretation = f"RCRI class {min(s + 1, 4)}; interpret with procedure type, functional capacity and current perioperative guidelines."
        risk = "Low" if s == 0 else "Medium" if s == 1 else "High"
        inputs = {"points": s}

    elif name == "STOP-Bang":
        age = int(patient.get("age") or 0)
        s = sum(
            [
                _cb("Snoring", 1, f"{prefix}s1"),
                _cb("Tiredness", 1, f"{prefix}s2"),
                _cb("Observed apnea", 1, f"{prefix}s3"),
                _cb("High blood pressure", 1, f"{prefix}s4"),
                _cb("BMI >35 kg/m²", 1, f"{prefix}s5"),
                1 if age > 50 else 0,
                _cb("Neck circumference >40 cm", 1, f"{prefix}s7"),
                1 if str(patient.get("sex", "")).lower() == "male" else 0,
            ]
        )
        result = f"{s}/8"
        interpretation = "Low risk" if s <= 2 else "Intermediate risk" if s <= 4 else "High risk for OSA"
        risk = "Low" if s <= 2 else "Medium" if s <= 4 else "High"
        inputs = {"score": s, "age_auto": age, "sex_auto": patient.get("sex")}

    elif name == "Clinical Frailty Scale":
        s = st.slider("Clinical Frailty Scale", 1, 9, 3, key=f"{prefix}_cfs")
        labels = {1: "Very fit", 2: "Fit", 3: "Managing well", 4: "Living with very mild frailty", 5: "Mild frailty", 6: "Moderate frailty", 7: "Severe frailty", 8: "Very severe frailty", 9: "Terminally ill"}
        result = s
        interpretation = labels[s]
        risk = "Low" if s <= 3 else "Medium" if s <= 5 else "High"
        inputs = {"scale": s}

    elif name == "Caprini VTE":
        st.info("Caprini requires careful item-by-item review. Do not select mutually exclusive age bands together.")
        age_band = st.selectbox("Age points", ["≤40 (0)", "41–60 (1)", "61–74 (2)", "≥75 (3)"], key=f"{prefix}_cap_age")
        age_pts = {"≤40 (0)": 0, "41–60 (1)": 1, "61–74 (2)": 2, "≥75 (3)": 3}[age_band]
        s = age_pts
        items = [
            ("BMI >25", 1), ("Swollen legs", 1), ("Varicose veins", 1), ("Pregnancy or postpartum", 1),
            ("History of unexplained/recurrent abortion", 1), ("Oral contraceptives or HRT", 1), ("Sepsis <1 month", 1),
            ("Serious lung disease including pneumonia <1 month", 1), ("Abnormal pulmonary function", 1),
            ("Acute myocardial infarction <1 month", 1), ("Medical patient on bed rest", 1),
            ("Minor surgery planned", 1), ("Major surgery >45 min", 2), ("Laparoscopic surgery >45 min", 2),
            ("Malignancy", 2), ("Confined to bed >72 h", 2), ("Central venous access", 2),
            ("Prior DVT/PE", 3), ("Family history of thrombosis", 3), ("Known thrombophilia", 3),
            ("Stroke <1 month", 5), ("Elective lower-extremity arthroplasty", 5), ("Hip/pelvis/leg fracture", 5),
            ("Acute spinal cord injury <1 month", 5),
        ]
        selected = []
        for i, (label, pts) in enumerate(items):
            if st.checkbox(f"{label} (+{pts})", key=f"{prefix}_cap_{i}"):
                s += pts
                selected.append(label)
        result = s
        interpretation = "Very low" if s == 0 else "Low" if s <= 2 else "Moderate" if s <= 4 else "High VTE risk"
        risk = "Low" if s <= 2 else "Medium" if s <= 4 else "High"
        inputs = {"age_band": age_band, "selected": selected, "points": s}

    elif name == "qSOFA":
        s = sum([
            _cb("Respiratory rate ≥22/min", 1, f"{prefix}q1"),
            _cb("Altered mentation", 1, f"{prefix}q2"),
            _cb("Systolic BP ≤100 mmHg", 1, f"{prefix}q3"),
        ])
        result = f"{s}/3"
        interpretation = "Higher risk of poor outcome in suspected infection" if s >= 2 else "Lower qSOFA; do not exclude sepsis"
        risk = "High" if s >= 2 else "Low"
        inputs = {"score": s}

    elif name == "SIRS":
        s = sum([
            _cb("Temperature >38°C or <36°C", 1, f"{prefix}si1"),
            _cb("Heart rate >90/min", 1, f"{prefix}si2"),
            _cb("RR >20/min or PaCO₂ <32 mmHg", 1, f"{prefix}si3"),
            _cb("WBC >12,000 or <4,000 or bands >10%", 1, f"{prefix}si4"),
        ])
        result = f"{s}/4"
        interpretation = "SIRS criteria met" if s >= 2 else "SIRS criteria not met"
        risk = "Medium" if s >= 2 else "Low"
        inputs = {"score": s}

    elif name == "Shock Index":
        hr = st.number_input("Heart rate /min", 20.0, 250.0, 90.0, key=f"{prefix}_si_hr")
        sbp = st.number_input("Systolic BP mmHg", 30.0, 260.0, 120.0, key=f"{prefix}_si_sbp")
        value = round(hr / sbp, 2)
        result = value
        interpretation = "Within usual range" if value < 0.7 else "Borderline" if value <= 0.9 else "Possible significant circulatory stress"
        risk = "Low" if value < 0.7 else "Medium" if value <= 0.9 else "High"
        inputs = {"heart_rate": hr, "systolic_bp": sbp}

    elif name == "Alvarado":
        s = sum([
            _cb("Migration of pain to RIF", 1, f"{prefix}a1"), _cb("Anorexia", 1, f"{prefix}a2"),
            _cb("Nausea/vomiting", 1, f"{prefix}a3"), _cb("RIF tenderness", 2, f"{prefix}a4"),
            _cb("Rebound tenderness", 1, f"{prefix}a5"), _cb("Temperature elevation", 1, f"{prefix}a6"),
            _cb("Leukocytosis", 2, f"{prefix}a7"), _cb("Neutrophil left shift", 1, f"{prefix}a8"),
        ])
        result = f"{s}/10"
        interpretation = "Low probability" if s <= 4 else "Intermediate probability" if s <= 6 else "High probability"
        risk = "Low" if s <= 4 else "Medium" if s <= 6 else "High"
        inputs = {"score": s}

    elif name == "AIR Appendicitis":
        vomiting = st.checkbox("Vomiting (+1)", key=f"{prefix}air1")
        rif = st.selectbox("RIF pain/tenderness", ["None 0", "Mild 1", "Moderate 2", "Strong 3"], key=f"{prefix}air2")
        defense = st.selectbox("Muscular defense/rebound", ["None 0", "Light 1", "Medium 2", "Strong 3"], key=f"{prefix}air3")
        temp = st.checkbox("Temperature ≥38.5°C (+1)", key=f"{prefix}air4")
        wbc = st.selectbox("WBC ×10⁹/L", ["<10 (0)", "10–14.9 (1)", "≥15 (2)"], key=f"{prefix}air5")
        neut = st.selectbox("Neutrophils %", ["<70 (0)", "70–84 (1)", "≥85 (2)"], key=f"{prefix}air6")
        crp = st.selectbox("CRP mg/L", ["<10 (0)", "10–49 (1)", "≥50 (2)"], key=f"{prefix}air7")
        s = int(vomiting) + int(rif.split()[-1]) + int(defense.split()[-1]) + int(temp)
        s += {"<10 (0)": 0, "10–14.9 (1)": 1, "≥15 (2)": 2}[wbc]
        s += {"<70 (0)": 0, "70–84 (1)": 1, "≥85 (2)": 2}[neut]
        s += {"<10 (0)": 0, "10–49 (1)": 1, "≥50 (2)": 2}[crp]
        result = f"{s}/12"
        interpretation = "Low probability" if s <= 4 else "Indeterminate" if s <= 8 else "High probability"
        risk = "Low" if s <= 4 else "Medium" if s <= 8 else "High"
        inputs = {"score": s}

    elif name == "Tokyo Cholecystitis Grade":
        organ = st.checkbox("Organ dysfunction", key=f"{prefix}tg1")
        moderate = sum([
            _cb("WBC >18,000/mm³", 1, f"{prefix}tg2"),
            _cb("Palpable tender RUQ mass", 1, f"{prefix}tg3"),
            _cb("Symptoms >72 hours", 1, f"{prefix}tg4"),
            _cb("Marked local inflammation (gangrene/abscess/peritonitis)", 1, f"{prefix}tg5"),
        ])
        result = "Grade III" if organ else "Grade II" if moderate else "Grade I"
        interpretation = "Severe with organ dysfunction" if organ else "Moderate" if moderate else "Mild"
        risk = "High" if organ else "Medium" if moderate else "Low"
        inputs = {"organ_dysfunction": organ, "moderate_features": moderate}

    elif name == "ASGE CBD Stone Risk":
        stone = st.checkbox("CBD stone on imaging", key=f"{prefix}cbd1")
        cholangitis = st.checkbox("Clinical ascending cholangitis", key=f"{prefix}cbd2")
        bili_dilated = st.checkbox("Total bilirubin >4 mg/dL AND dilated CBD", key=f"{prefix}cbd3")
        intermediate = st.checkbox("Abnormal liver tests, age >55, or dilated CBD alone", key=f"{prefix}cbd4")
        if stone or cholangitis or bili_dilated:
            result, interpretation, risk = "High", "High probability; therapeutic ERCP pathway may be appropriate after clinical review", "High"
        elif intermediate:
            result, interpretation, risk = "Intermediate", "Further evaluation with MRCP/EUS/IOC according to local pathway", "Medium"
        else:
            result, interpretation, risk = "Low", "Low probability", "Low"
        inputs = {"stone": stone, "cholangitis": cholangitis, "bilirubin_gt4_dilated_cbd": bili_dilated, "intermediate_predictor": intermediate}

    elif name == "BISAP":
        s = sum([
            _cb("BUN >25 mg/dL", 1, f"{prefix}b1"), _cb("Impaired mental status", 1, f"{prefix}b2"),
            _cb("SIRS present", 1, f"{prefix}b3"), _cb("Age >60", 1, f"{prefix}b4"),
            _cb("Pleural effusion", 1, f"{prefix}b5"),
        ])
        result = f"{s}/5"
        interpretation = "Higher risk of severe disease/mortality" if s >= 3 else "Lower risk"
        risk = "High" if s >= 3 else "Low"
        inputs = {"score": s}

    elif name == "Ranson":
        st.warning("أدخل نقاط admission و48-hour معاً للحصول على المجموع الكامل؛ لا تفسر admission-only على أنه Ranson كامل.")
        admission = sum([
            _cb("Age >55", 1, f"{prefix}ra1"), _cb("WBC >16,000", 1, f"{prefix}ra2"),
            _cb("Glucose >200 mg/dL", 1, f"{prefix}ra3"), _cb("LDH >350 IU/L", 1, f"{prefix}ra4"),
            _cb("AST >250 IU/L", 1, f"{prefix}ra5"),
        ])
        after48 = sum([
            _cb("Hematocrit fall >10%", 1, f"{prefix}r48a"), _cb("BUN rise >5 mg/dL", 1, f"{prefix}r48b"),
            _cb("Calcium <8 mg/dL", 1, f"{prefix}r48c"), _cb("PaO₂ <60 mmHg", 1, f"{prefix}r48d"),
            _cb("Base deficit >4 mEq/L", 1, f"{prefix}r48e"), _cb("Fluid sequestration >6 L", 1, f"{prefix}r48f"),
        ])
        total = admission + after48
        result = f"{total}/11"
        interpretation = "Lower severity" if total <= 2 else "Increasing severity" if total <= 4 else "High severity"
        risk = "Low" if total <= 2 else "Medium" if total <= 4 else "High"
        inputs = {"admission": admission, "at_48h": after48, "total": total}

    elif name == "AIMS65":
        s = sum([
            _cb("Albumin <3.0 g/dL", 1, f"{prefix}ai1"), _cb("INR >1.5", 1, f"{prefix}ai2"),
            _cb("Altered mental status", 1, f"{prefix}ai3"), _cb("SBP ≤90 mmHg", 1, f"{prefix}ai4"),
            _cb("Age ≥65", 1, f"{prefix}ai5"),
        ])
        result = f"{s}/5"
        interpretation = "Higher risk" if s >= 2 else "Lower risk"
        risk = "High" if s >= 2 else "Low"
        inputs = {"score": s}

    elif name == "Rockall Pre-Endoscopy":
        age = st.selectbox("Age", ["<60 (0)", "60–79 (1)", "≥80 (2)"], key=f"{prefix}_rk_age")
        shock = st.selectbox("Shock", ["No shock (0)", "Tachycardia SBP≥100 (1)", "Hypotension SBP<100 (2)"], key=f"{prefix}_rk_shock")
        comorb = st.selectbox("Comorbidity", ["None (0)", "Cardiac failure/IHD/major comorbidity (2)", "Renal/liver failure or disseminated malignancy (3)"], key=f"{prefix}_rk_com")
        s = {"<60 (0)": 0, "60–79 (1)": 1, "≥80 (2)": 2}[age]
        s += {"No shock (0)": 0, "Tachycardia SBP≥100 (1)": 1, "Hypotension SBP<100 (2)": 2}[shock]
        s += {"None (0)": 0, "Cardiac failure/IHD/major comorbidity (2)": 2, "Renal/liver failure or disseminated malignancy (3)": 3}[comorb]
        result = f"{s}/7"
        interpretation = "Higher pre-endoscopy risk" if s >= 3 else "Lower pre-endoscopy risk"
        risk = "High" if s >= 3 else "Low"
        inputs = {"age": age, "shock": shock, "comorbidity": comorb}

    elif name == "Glasgow-Blatchford":
        sex = st.selectbox("Sex used for hemoglobin thresholds", ["Male", "Female"], index=0 if str(patient.get("sex", "")).lower() == "male" else 1, key=f"{prefix}_gbs_sex")
        bun = st.number_input("BUN mg/dL", 0.0, 200.0, 18.0, key=f"{prefix}_gbs_bun")
        hb = st.number_input("Hemoglobin g/dL", 1.0, 25.0, 12.0, key=f"{prefix}_gbs_hb")
        sbp = st.number_input("Systolic BP mmHg", 40, 260, 120, key=f"{prefix}_gbs_sbp")
        pulse = st.number_input("Pulse /min", 20, 220, 80, key=f"{prefix}_gbs_pulse")
        melena = st.checkbox("Melena", key=f"{prefix}_gbs_melena")
        syncope = st.checkbox("Syncope", key=f"{prefix}_gbs_syncope")
        liver = st.checkbox("Hepatic disease", key=f"{prefix}_gbs_liver")
        heart = st.checkbox("Cardiac failure", key=f"{prefix}_gbs_heart")
        # BUN mg/dL thresholds equivalent to mmol/L bands
        if bun < 18.2: bun_pts = 0
        elif bun < 22.4: bun_pts = 2
        elif bun < 28.0: bun_pts = 3
        elif bun < 41.0: bun_pts = 4
        else: bun_pts = 6
        if sex == "Male":
            hb_pts = 0 if hb >= 13 else 1 if hb >= 12 else 3 if hb >= 10 else 6
        else:
            hb_pts = 0 if hb >= 12 else 1 if hb >= 10 else 6
        sbp_pts = 0 if sbp >= 110 else 1 if sbp >= 100 else 2 if sbp >= 90 else 3
        s = bun_pts + hb_pts + sbp_pts + (1 if pulse >= 100 else 0) + (1 if melena else 0) + (2 if syncope else 0) + (2 if liver else 0) + (2 if heart else 0)
        result = s
        interpretation = "Very low risk only when score is 0–1 in appropriately selected patients; otherwise assess for admission/intervention."
        risk = "Low" if s <= 1 else "Medium" if s <= 5 else "High"
        inputs = {"sex": sex, "bun": bun, "hemoglobin": hb, "sbp": sbp, "pulse": pulse, "melena": melena, "syncope": syncope, "liver_disease": liver, "heart_failure": heart}

    elif name == "Mannheim Peritonitis Index":
        s = sum([
            _cb("Age >50", 5, f"{prefix}mpi1"), _cb("Female sex", 5, f"{prefix}mpi2"),
            _cb("Organ failure", 7, f"{prefix}mpi3"), _cb("Malignancy", 4, f"{prefix}mpi4"),
            _cb("Preoperative duration >24 h", 4, f"{prefix}mpi5"), _cb("Origin not colonic", 4, f"{prefix}mpi6"),
            _cb("Diffuse generalized peritonitis", 6, f"{prefix}mpi7"),
        ])
        exudate = st.selectbox("Exudate", ["Clear (0)", "Cloudy/purulent (6)", "Fecal (12)"], key=f"{prefix}_mpi_ex")
        s += {"Clear (0)": 0, "Cloudy/purulent (6)": 6, "Fecal (12)": 12}[exudate]
        result = s
        interpretation = "Lower risk" if s < 21 else "Intermediate" if s <= 29 else "High mortality risk"
        risk = "Low" if s < 21 else "Medium" if s <= 29 else "High"
        inputs = {"score": s, "exudate": exudate}

    elif name == "Boey":
        s = sum([
            _cb("Major medical illness", 1, f"{prefix}bo1"),
            _cb("Preoperative shock", 1, f"{prefix}bo2"),
            _cb("Perforation >24 hours", 1, f"{prefix}bo3"),
        ])
        result = f"{s}/3"
        interpretation = "Higher risk" if s >= 2 else "Lower risk"
        risk = "High" if s >= 2 else "Low"
        inputs = {"score": s}

    elif name == "Child-Pugh":
        bilirubin = st.selectbox("Bilirubin", ["<2 mg/dL (1)", "2–3 mg/dL (2)", ">3 mg/dL (3)"], key=f"{prefix}_cp_b")
        albumin = st.selectbox("Albumin", [">3.5 g/dL (1)", "2.8–3.5 g/dL (2)", "<2.8 g/dL (3)"], key=f"{prefix}_cp_a")
        inr = st.selectbox("INR", ["<1.7 (1)", "1.7–2.3 (2)", ">2.3 (3)"], key=f"{prefix}_cp_i")
        ascites = st.selectbox("Ascites", ["None (1)", "Mild/moderate controlled (2)", "Severe/refractory (3)"], key=f"{prefix}_cp_as")
        enceph = st.selectbox("Encephalopathy", ["None (1)", "Grade I–II (2)", "Grade III–IV (3)"], key=f"{prefix}_cp_e")
        def last_int(x): return int(x[-2])
        s = sum(map(last_int, [bilirubin, albumin, inr, ascites, enceph]))
        cls = "A" if s <= 6 else "B" if s <= 9 else "C"
        result = f"{s} (Class {cls})"
        interpretation = "Compensated" if cls == "A" else "Significant functional compromise" if cls == "B" else "Decompensated"
        risk = "Low" if cls == "A" else "Medium" if cls == "B" else "High"
        inputs = {"bilirubin": bilirubin, "albumin": albumin, "inr": inr, "ascites": ascites, "encephalopathy": enceph}

    elif name == "MELD-Na":
        bili = st.number_input("Bilirubin mg/dL", 0.1, 60.0, 1.0, key=f"{prefix}_mn_b")
        inr = st.number_input("INR", 0.8, 10.0, 1.0, key=f"{prefix}_mn_i")
        cr = st.number_input("Creatinine mg/dL", 0.1, 15.0, 1.0, key=f"{prefix}_mn_c")
        na = st.number_input("Sodium mmol/L", 110.0, 160.0, 137.0, key=f"{prefix}_mn_n")
        dialysis = st.checkbox("Dialysis at least twice in past week", key=f"{prefix}_mn_d")
        s = meld_na(bili, inr, cr, na, dialysis)
        result = s
        interpretation = "Lower short-term risk" if s < 10 else "Moderate" if s < 20 else "High liver-related risk"
        risk = "Low" if s < 10 else "Medium" if s < 20 else "High"
        inputs = {"bilirubin": bili, "inr": inr, "creatinine": cr, "sodium": na, "dialysis": dialysis}

    elif name == "GCS":
        eye = st.selectbox("Eye response", ["4 Spontaneous", "3 To speech", "2 To pain", "1 None"], key=f"{prefix}_gcs_e")
        verbal = st.selectbox("Verbal response", ["5 Oriented", "4 Confused", "3 Inappropriate words", "2 Incomprehensible sounds", "1 None"], key=f"{prefix}_gcs_v")
        motor = st.selectbox("Motor response", ["6 Obeys commands", "5 Localizes pain", "4 Withdraws", "3 Abnormal flexion", "2 Extension", "1 None"], key=f"{prefix}_gcs_m")
        s = int(eye.split()[0]) + int(verbal.split()[0]) + int(motor.split()[0])
        result = f"{s}/15"
        interpretation = "Mild" if s >= 13 else "Moderate" if s >= 9 else "Severe impairment"
        risk = "Low" if s >= 13 else "Medium" if s >= 9 else "High"
        inputs = {"eye": eye, "verbal": verbal, "motor": motor}

    elif name == "Clavien-Dindo":
        result = st.selectbox("Grade", ["No complication", "Grade I", "Grade II", "Grade IIIa", "Grade IIIb", "Grade IVa", "Grade IVb", "Grade V"], key=f"{prefix}_cd")
        interpretation = "Postoperative complication severity based on required therapy/intervention."
        risk = "Low" if result in {"No complication", "Grade I"} else "Medium" if result in {"Grade II", "Grade IIIa"} else "High"
        inputs = {"grade": result}

    elif name == "CDC SSI Classification":
        result = st.selectbox("SSI classification", ["No SSI", "Superficial incisional SSI", "Deep incisional SSI", "Organ/space SSI", "Insufficient information"], key=f"{prefix}_ssi")
        interpretation = "Use current CDC/NHSN surveillance definitions and surveillance period; this selector does not independently establish the diagnosis."
        risk = "Low" if result == "No SSI" else "Medium" if result == "Superficial incisional SSI" else "High" if "SSI" in result else "Medium"
        inputs = {"classification": result}

    elif name == "NEWS2":
        st.info("NEWS2 is calculated in the Vitals page from actual observations. Save it there to preserve time, units and escalation advice.")
        result, interpretation, risk, inputs = "Use Vitals", "Enter a complete observation set in Vitals & NEWS2.", "Medium", {}

    else:
        result = st.text_input("Result", key=f"{prefix}_manual")
        interpretation = st.text_area("Interpretation", key=f"{prefix}_manual_i")
        risk = st.selectbox("Risk", ["Low", "Medium", "High"], key=f"{prefix}_manual_r")
        inputs = {"manual": True}

    st.metric("Result", result)
    if risk == "High":
        st.error(interpretation)
    elif risk == "Medium":
        st.warning(interpretation)
    else:
        st.success(interpretation)
    return {"score_name": name, "result": str(result), "interpretation": interpretation, "risk": risk, "inputs": inputs}
