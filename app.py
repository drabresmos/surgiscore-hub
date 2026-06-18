import streamlit as st
import pandas as pd
import math
from datetime import datetime

st.set_page_config(page_title="SurgiScore Hub", page_icon="🏥", layout="wide")

if "patients" not in st.session_state:
    st.session_state.patients = []
if "results" not in st.session_state:
    st.session_state.results = []
if "attachments" not in st.session_state:
    st.session_state.attachments = {}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.stApp {
    background: linear-gradient(180deg, #f5f7fb 0%, #ffffff 100%);
}

.apple-card {
    background: rgba(255,255,255,0.86);
    border: 1px solid rgba(230,230,235,0.9);
    box-shadow: 0 12px 34px rgba(0,0,0,0.06);
    border-radius: 26px;
    padding: 24px;
    margin-bottom: 18px;
}

.hero {
    background: linear-gradient(135deg, #ffffff 0%, #eef4ff 100%);
    border-radius: 32px;
    padding: 30px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 18px 50px rgba(0,0,0,0.06);
}

.title {
    font-size: 42px;
    font-weight: 800;
    letter-spacing: -1.2px;
    color: #111827;
}

.subtitle {
    color: #6b7280;
    font-size: 16px;
}

.risk-low {
    color: #12805c;
    font-weight: 800;
}
.risk-medium {
    color: #b76e00;
    font-weight: 800;
}
.risk-high {
    color: #b42318;
    font-weight: 800;
}

div.stButton > button {
    border-radius: 14px;
    border: 1px solid #d1d5db;
    background: #111827;
    color: white;
    font-weight: 700;
    padding: 0.6rem 1rem;
}

div.stDownloadButton > button {
    border-radius: 14px;
}

[data-testid="stMetricValue"] {
    font-size: 30px;
    font-weight: 800;
}
</style>
""", unsafe_allow_html=True)

def add_patient(code, name, age, sex, diagnosis, operation, notes):
    st.session_state.patients.append({
        "code": code,
        "name": name,
        "age": age,
        "sex": sex,
        "diagnosis": diagnosis,
        "operation": operation,
        "notes": notes,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    st.session_state.attachments[code] = []

def get_patient(code):
    for p in st.session_state.patients:
        if p["code"] == code:
            return p
    return None

def delete_patient(code):
    st.session_state.patients = [p for p in st.session_state.patients if p["code"] != code]
    st.session_state.results = [r for r in st.session_state.results if r["patient_code"] != code]
    st.session_state.attachments.pop(code, None)

def save_result(patient_code, score_name, result, interpretation, risk):
    st.session_state.results.append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "patient_code": patient_code,
        "score": score_name,
        "result": result,
        "interpretation": interpretation,
        "risk": risk
    })
    st.success("Saved successfully.")

def risk_badge(risk):
    css = {"Low": "risk-low", "Medium": "risk-medium", "High": "risk-high"}.get(risk, "")
    st.markdown(f"<span class='{css}'>Risk: {risk}</span>", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <div class="title">🏥 SurgiScore Hub</div>
    <div class="subtitle">Apple-style surgical scoring platform for general surgery</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.title("SurgiScore")
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Add Patient", "Patient Registry", "Score Calculator", "Attachments", "Saved Results"]
)

scores_list = [
    "ASA",
    "Alvarado",
    "AIR Appendicitis",
    "Caprini VTE",
    "RCRI",
    "qSOFA",
    "BISAP",
    "Ranson Admission",
    "Glasgow-Blatchford",
    "Shock Index",
    "Mannheim Peritonitis Index",
    "Boey Score",
    "ASGE CBD Stone Risk",
    "Tokyo Cholecystitis Grade",
    "Child-Pugh",
    "MELD-Na",
    "Clavien-Dindo"
]

if page == "Dashboard":
    st.markdown("### Dashboard")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Patients", len(st.session_state.patients))
    c2.metric("Scores", len(st.session_state.results))
    c3.metric("High Risk", sum(1 for r in st.session_state.results if r["risk"] == "High"))
    c4.metric("Available Scores", len(scores_list))

    st.markdown("### Recent Results")
    if st.session_state.results:
        st.dataframe(pd.DataFrame(st.session_state.results), use_container_width=True)
    else:
        st.info("No saved results yet.")

elif page == "Add Patient":
    st.markdown("### Add Patient")
    with st.form("add_patient"):
        col1, col2 = st.columns(2)
        with col1:
            code = st.text_input("Patient Code / ID")
            name = st.text_input("Name")
            age = st.number_input("Age", 0, 120, 30)
            sex = st.selectbox("Sex", ["Male", "Female"])
        with col2:
            diagnosis = st.text_input("Diagnosis")
            operation = st.text_input("Operation")
            notes = st.text_area("Notes")
        if st.form_submit_button("Save Patient"):
            if not code:
                st.error("Patient code is required.")
            elif get_patient(code):
                st.error("Patient code already exists.")
            else:
                add_patient(code, name, age, sex, diagnosis, operation, notes)
                st.success("Patient added.")

elif page == "Patient Registry":
    st.markdown("### Patient Registry")
    if not st.session_state.patients:
        st.info("No patients yet.")
    else:
        search = st.text_input("Search")
        patients = st.session_state.patients
        if search:
            patients = [p for p in patients if search.lower() in p["code"].lower() or search.lower() in p["name"].lower()]

        for p in patients:
            st.markdown('<div class="apple-card">', unsafe_allow_html=True)
            c1, c2, c3 = st.columns([3, 3, 1])
            c1.write(f"**{p['code']} — {p['name']}**")
            c1.caption(f"{p['age']} years | {p['sex']}")
            c2.write(f"**Diagnosis:** {p['diagnosis']}")
            c2.write(f"**Operation:** {p['operation']}")
            c2.caption(p["created_at"])
            if c3.button("Delete", key=f"del_{p['code']}"):
                delete_patient(p["code"])
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

elif page == "Score Calculator":
    st.markdown("### Score Calculator")

    if not st.session_state.patients:
        st.warning("Add a patient first.")
    else:
        patient_code = st.selectbox("Patient", [p["code"] for p in st.session_state.patients])
        patient = get_patient(patient_code)

        st.markdown('<div class="apple-card">', unsafe_allow_html=True)
        st.write(f"**Patient:** {patient['name']} | **Age:** {patient['age']} | **Diagnosis:** {patient['diagnosis']}")
        st.markdown('</div>', unsafe_allow_html=True)

        score_type = st.selectbox("Choose surgical score", scores_list)
        st.divider()

        if score_type == "ASA":
            asa = st.radio("ASA Physical Status", [
                "ASA I - Normal healthy patient",
                "ASA II - Mild systemic disease",
                "ASA III - Severe systemic disease",
                "ASA IV - Severe systemic disease constant threat to life",
                "ASA V - Moribund patient"
            ])
            result = asa.split(" - ")[0]
            risk = "Low" if result in ["ASA I", "ASA II"] else "High"
            st.metric("ASA", result)
            st.write(asa)
            risk_badge(risk)
            if st.button("Save Result"):
                save_result(patient_code, "ASA", result, asa, risk)

        elif score_type == "Alvarado":
            score = 0
            if st.checkbox("Migration of pain"): score += 1
            if st.checkbox("Anorexia"): score += 1
            if st.checkbox("Nausea / vomiting"): score += 1
            if st.checkbox("RIF tenderness"): score += 2
            if st.checkbox("Rebound tenderness"): score += 1
            if st.checkbox("Fever"): score += 1
            if st.checkbox("Leukocytosis"): score += 2
            if st.checkbox("Neutrophilia"): score += 1
            if score <= 4:
                interp, risk = "Unlikely appendicitis", "Low"
            elif score <= 6:
                interp, risk = "Possible appendicitis", "Medium"
            else:
                interp, risk = "Probable / very probable appendicitis", "High"
            st.metric("Alvarado", f"{score}/10")
            st.write(interp)
            risk_badge(risk)
            if st.button("Save Result"):
                save_result(patient_code, "Alvarado", score, interp, risk)

        elif score_type == "AIR Appendicitis":
            score = 0
            vomiting = st.checkbox("Vomiting")
            rif = st.selectbox("RIF pain/tenderness", ["None", "Mild", "Moderate", "Strong"])
            rebound = st.selectbox("Rebound / muscular defense", ["None", "Light", "Medium", "Strong"])
            temp = st.checkbox("Temperature ≥ 38.5°C")
            wbc = st.selectbox("WBC", ["<10", "10–14.9", "≥15"])
            neut = st.selectbox("Neutrophils %", ["<70", "70–84", "≥85"])
            crp = st.selectbox("CRP mg/L", ["<10", "10–49", "≥50"])
            if vomiting: score += 1
            score += {"None":0, "Mild":1, "Moderate":2, "Strong":3}[rif]
            score += {"None":0, "Light":1, "Medium":2, "Strong":3}[rebound]
            if temp: score += 1
            score += {"<10":0, "10–14.9":1, "≥15":2}[wbc]
            score += {"<70":0, "70–84":1, "≥85":2}[neut]
            score += {"<10":0, "10–49":1, "≥50":2}[crp]
            if score <= 4:
                interp, risk = "Low probability", "Low"
            elif score <= 8:
                interp, risk = "Intermediate probability", "Medium"
            else:
                interp, risk = "High probability", "High"
            st.metric("AIR Score", f"{score}/12")
            st.write(interp)
            risk_badge(risk)
            if st.button("Save Result"):
                save_result(patient_code, "AIR Appendicitis", score, interp, risk)

        elif score_type == "Caprini VTE":
            score = 0
            items = {
                "Age 41–60": 1,
                "Age 61–74": 2,
                "Age ≥75": 3,
                "Minor surgery": 1,
                "Major surgery >45 min": 2,
                "BMI >25": 1,
                "Swollen legs": 1,
                "Varicose veins": 1,
                "Pregnancy/postpartum": 1,
                "History of malignancy": 2,
                "Bed rest >72h": 2,
                "Central venous access": 2,
                "Prior DVT/PE": 3,
                "Known thrombophilia": 3,
                "Stroke <1 month": 5,
                "Elective lower limb arthroplasty": 5,
                "Hip/pelvis/leg fracture": 5
            }
            for item, pts in items.items():
                if st.checkbox(f"{item} (+{pts})"):
                    score += pts
            if score <= 1:
                interp, risk = "Very low VTE risk", "Low"
            elif score == 2:
                interp, risk = "Low VTE risk", "Low"
            elif score <= 4:
                interp, risk = "Moderate VTE risk", "Medium"
            else:
                interp, risk = "High VTE risk", "High"
            st.metric("Caprini", score)
            st.write(interp)
            risk_badge(risk)
            if st.button("Save Result"):
                save_result(patient_code, "Caprini VTE", score, interp, risk)

        elif score_type == "RCRI":
            score = 0
            for item in [
                "High-risk surgery",
                "Ischemic heart disease",
                "Heart failure",
                "Cerebrovascular disease",
                "Insulin-dependent diabetes",
                "Creatinine >2 mg/dL"
            ]:
                if st.checkbox(item): score += 1
            if score == 0:
                interp, risk = "Low cardiac risk", "Low"
            elif score == 1:
                interp, risk = "Intermediate cardiac risk", "Medium"
            else:
                interp, risk = "High cardiac risk", "High"
            st.metric("RCRI", score)
            st.write(interp)
            risk_badge(risk)
            if st.button("Save Result"):
                save_result(patient_code, "RCRI", score, interp, risk)

        elif score_type == "qSOFA":
            score = 0
            if st.checkbox("RR ≥22/min"): score += 1
            if st.checkbox("Altered mentation"): score += 1
            if st.checkbox("SBP ≤100 mmHg"): score += 1
            interp, risk = ("High risk in suspected sepsis", "High") if score >= 2 else ("Lower risk", "Low")
            st.metric("qSOFA", f"{score}/3")
            st.write(interp)
            risk_badge(risk)
            if st.button("Save Result"):
                save_result(patient_code, "qSOFA", score, interp, risk)

        elif score_type == "BISAP":
            score = 0
            if st.checkbox("BUN >25 mg/dL"): score += 1
            if st.checkbox("Impaired mental status"): score += 1
            if st.checkbox("SIRS present"): score += 1
            if st.checkbox("Age >60"): score += 1
            if st.checkbox("Pleural effusion"): score += 1
            interp, risk = ("High risk severe pancreatitis/mortality", "High") if score >= 3 else ("Lower risk", "Low")
            st.metric("BISAP", f"{score}/5")
            st.write(interp)
            risk_badge(risk)
            if st.button("Save Result"):
                save_result(patient_code, "BISAP", score, interp, risk)

        elif score_type == "Ranson Admission":
            score = 0
            if st.checkbox("Age >55 years"): score += 1
            if st.checkbox("WBC >16,000"): score += 1
            if st.checkbox("Glucose >200 mg/dL"): score += 1
            if st.checkbox("LDH >350 IU/L"): score += 1
            if st.checkbox("AST >250 IU/L"): score += 1
            if score <= 2:
                interp, risk = "Mild risk on admission criteria", "Low"
            else:
                interp, risk = "Higher severity risk", "High"
            st.metric("Ranson Admission", f"{score}/5")
            st.write(interp)
            risk_badge(risk)
            if st.button("Save Result"):
                save_result(patient_code, "Ranson Admission", score, interp, risk)

        elif score_type == "Glasgow-Blatchford":
            score = 0
            bun = st.number_input("BUN mg/dL", 0.0, 200.0, 20.0)
            hb = st.number_input("Hemoglobin g/dL", 0.0, 25.0, 12.0)
            sbp = st.number_input("Systolic BP", 40, 250, 120)
            pulse = st.number_input("Pulse", 30, 220, 80)
            if bun >= 28: score += 2
            if hb < 12: score += 2
            if sbp < 100: score += 2
            if pulse >= 100: score += 1
            if st.checkbox("Melena"): score += 1
            if st.checkbox("Syncope"): score += 2
            if st.checkbox("Liver disease"): score += 2
            if st.checkbox("Cardiac failure"): score += 2
            if score == 0:
                interp, risk = "Very low risk", "Low"
            elif score <= 5:
                interp, risk = "Moderate risk", "Medium"
            else:
                interp, risk = "High risk, admission/endoscopy likely required", "High"
            st.metric("GBS simplified", score)
            st.write(interp)
            risk_badge(risk)
            if st.button("Save Result"):
                save_result(patient_code, "Glasgow-Blatchford", score, interp, risk)

        elif score_type == "Shock Index":
            hr = st.number_input("Heart rate", 20, 250, 90)
            sbp = st.number_input("Systolic BP", 40, 250, 120)
            value = round(hr / sbp, 2)
            if value < 0.7:
                interp, risk = "Normal range", "Low"
            elif value <= 0.9:
                interp, risk = "Borderline", "Medium"
            else:
                interp, risk = "Possible shock / significant physiological stress", "High"
            st.metric("Shock Index", value)
            st.write(interp)
            risk_badge(risk)
            if st.button("Save Result"):
                save_result(patient_code, "Shock Index", value, interp, risk)

        elif score_type == "Mannheim Peritonitis Index":
            score = 0
            mpi_items = {
                "Age >50": 5,
                "Female sex": 5,
                "Organ failure": 7,
                "Malignancy": 4,
                "Preoperative duration >24h": 4,
                "Origin not colonic": 4,
                "Diffuse generalized peritonitis": 6,
                "Exudate: clear": 0,
                "Exudate: cloudy/purulent": 6,
                "Exudate: fecal": 12
            }
            for item, pts in mpi_items.items():
                if st.checkbox(f"{item} (+{pts})"):
                    score += pts
            if score < 21:
                interp, risk = "Lower mortality risk", "Low"
            elif score <= 29:
                interp, risk = "Intermediate mortality risk", "Medium"
            else:
                interp, risk = "High mortality risk", "High"
            st.metric("MPI", score)
            st.write(interp)
            risk_badge(risk)
            if st.button("Save Result"):
                save_result(patient_code, "Mannheim Peritonitis Index", score, interp, risk)

        elif score_type == "Boey Score":
            score = 0
            if st.checkbox("Major medical illness"): score += 1
            if st.checkbox("Preoperative shock"): score += 1
            if st.checkbox("Perforation >24h"): score += 1
            interp, risk = ("Lower risk", "Low") if score <= 1 else ("High risk perforated peptic ulcer", "High")
            st.metric("Boey", f"{score}/3")
            st.write(interp)
            risk_badge(risk)
            if st.button("Save Result"):
                save_result(patient_code, "Boey Score", score, interp, risk)

        elif score_type == "ASGE CBD Stone Risk":
            very_strong = st.checkbox("CBD stone seen on imaging")
            cholangitis = st.checkbox("Clinical ascending cholangitis")
            bilirubin4_cbd = st.checkbox("Bilirubin >4 mg/dL AND dilated CBD")
            intermediate = st.checkbox("Abnormal LFTs OR age >55 OR dilated CBD alone")
            if very_strong or cholangitis or bilirubin4_cbd:
                interp, risk = "High probability CBD stone — ERCP usually considered", "High"
                result = "High"
            elif intermediate:
                interp, risk = "Intermediate probability — MRCP/EUS/IOC usually considered", "Medium"
                result = "Intermediate"
            else:
                interp, risk = "Low probability", "Low"
                result = "Low"
            st.metric("ASGE CBD Risk", result)
            st.write(interp)
            risk_badge(risk)
            if st.button("Save Result"):
                save_result(patient_code, "ASGE CBD Stone Risk", result, interp, risk)

        elif score_type == "Tokyo Cholecystitis Grade":
            organ = st.checkbox("Organ dysfunction")
            wbc = st.checkbox("Marked inflammatory response")
            mass = st.checkbox("Palpable tender RUQ mass")
            duration = st.checkbox("Symptoms >72h")
            local = st.checkbox("Marked local inflammation/gangrene/abscess/peritonitis")
            if organ:
                result, interp, risk = "Grade III", "Severe acute cholecystitis with organ dysfunction", "High"
            elif wbc or mass or duration or local:
                result, interp, risk = "Grade II", "Moderate acute cholecystitis", "Medium"
            else:
                result, interp, risk = "Grade I", "Mild acute cholecystitis", "Low"
            st.metric("Tokyo Grade", result)
            st.write(interp)
            risk_badge(risk)
            if st.button("Save Result"):
                save_result(patient_code, "Tokyo Cholecystitis Grade", result, interp, risk)

        elif score_type == "Child-Pugh":
            ascites = st.selectbox("Ascites", ["None", "Mild", "Moderate/Severe"])
            enceph = st.selectbox("Encephalopathy", ["None", "Grade I-II", "Grade III-IV"])
            bili = st.selectbox("Bilirubin", ["<2", "2–3", ">3"])
            albumin = st.selectbox("Albumin", [">3.5", "2.8–3.5", "<2.8"])
            inr = st.selectbox("INR", ["<1.7", "1.7–2.3", ">2.3"])
            score = (
                {"None":1, "Mild":2, "Moderate/Severe":3}[ascites] +
                {"None":1, "Grade I-II":2, "Grade III-IV":3}[enceph] +
                {"<2":1, "2–3":2, ">3":3}[bili] +
                {">3.5":1, "2.8–3.5":2, "<2.8":3}[albumin] +
                {"<1.7":1, "1.7–2.3":2, ">2.3":3}[inr]
            )
            if score <= 6:
                result, interp, risk = "Class A", "Well compensated liver disease", "Low"
            elif score <= 9:
                result, interp, risk = "Class B", "Significant functional compromise", "Medium"
            else:
                result, interp, risk = "Class C", "Decompensated liver disease", "High"
            st.metric("Child-Pugh", f"{score} / {result}")
            st.write(interp)
            risk_badge(risk)
            if st.button("Save Result"):
                save_result(patient_code, "Child-Pugh", f"{score} {result}", interp, risk)

        elif score_type == "MELD-Na":
            bili = st.number_input("Bilirubin mg/dL", 0.1, 50.0, 1.0)
            inr = st.number_input("INR", 0.8, 10.0, 1.0)
            creat = st.number_input("Creatinine mg/dL", 0.1, 15.0, 1.0)
            sodium = st.number_input("Sodium mmol/L", 120, 150, 137)

            b = max(bili, 1.0)
            i = max(inr, 1.0)
            c = max(creat, 1.0)
            meld = 3.78 * math.log(b) + 11.2 * math.log(i) + 9.57 * math.log(c) + 6.43
            meld = round(meld)
            sodium_capped = min(max(sodium, 125), 137)
            meld_na = round(meld + 1.32 * (137 - sodium_capped) - (0.033 * meld * (137 - sodium_capped)))

            if meld_na < 10:
                interp, risk = "Lower short-term mortality", "Low"
            elif meld_na < 20:
                interp, risk = "Moderate liver-related mortality risk", "Medium"
            else:
                interp, risk = "High liver-related mortality risk", "High"

            st.metric("MELD-Na", meld_na)
            st.write(interp)
            risk_badge(risk)
            if st.button("Save Result"):
                save_result(patient_code, "MELD-Na", meld_na, interp, risk)

        elif score_type == "Clavien-Dindo":
            grade = st.selectbox("Grade", [
                "Grade I - Minor deviation",
                "Grade II - Pharmacological treatment",
                "Grade IIIa - Intervention without GA",
                "Grade IIIb - Intervention under GA",
                "Grade IV - Life-threatening / ICU",
                "Grade V - Death"
            ])
            result = grade.split(" - ")[0]
            risk = "High" if result in ["Grade IIIb", "Grade IV", "Grade V"] else "Medium"
            st.metric("Clavien-Dindo", result)
            st.write(grade)
            risk_badge(risk)
            if st.button("Save Result"):
                save_result(patient_code, "Clavien-Dindo", result, grade, risk)

elif page == "Attachments":
    st.markdown("### Attachments")
    if not st.session_state.patients:
        st.warning("Add a patient first.")
    else:
        patient_code = st.selectbox("Patient", [p["code"] for p in st.session_state.patients])
        files = st.file_uploader(
            "Attach labs, CT images, photos, PDF reports",
            type=["png", "jpg", "jpeg", "pdf", "txt", "csv"],
            accept_multiple_files=True
        )
        if files:
            for f in files:
                item = {
                    "name": f.name,
                    "type": f.type,
                    "size_kb": round(f.size / 1024, 1),
                    "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "bytes": f.getvalue()
                }
                existing = [x["name"] for x in st.session_state.attachments[patient_code]]
                if f.name not in existing:
                    st.session_state.attachments[patient_code].append(item)
            st.success("Files attached.")

        for i, f in enumerate(st.session_state.attachments.get(patient_code, [])):
            st.markdown('<div class="apple-card">', unsafe_allow_html=True)
            c1, c2, c3 = st.columns([4, 2, 1])
            c1.write(f"**{f['name']}**")
            c1.caption(f"{f['type']} | {f['size_kb']} KB | {f['uploaded_at']}")
            c2.download_button("Download", f["bytes"], f["name"], f["type"], key=f"down_{i}")
            if c3.button("Delete", key=f"fdel_{i}"):
                st.session_state.attachments[patient_code].pop(i)
                st.rerun()
            if f["type"].startswith("image"):
                st.image(f["bytes"], width=340)
            st.markdown('</div>', unsafe_allow_html=True)

elif page == "Saved Results":
    st.markdown("### Saved Results")
    if not st.session_state.results:
        st.info("No saved results.")
    else:
        df = pd.DataFrame(st.session_state.results)
        search = st.text_input("Search")
        if search:
            df = df[
                df["patient_code"].str.contains(search, case=False, na=False) |
                df["score"].str.contains(search, case=False, na=False)
            ]
        st.dataframe(df, use_container_width=True)
        st.download_button(
            "Download CSV",
            df.to_csv(index=False).encode("utf-8"),
            "surgiscore_results.csv",
            "text/csv"
        )
