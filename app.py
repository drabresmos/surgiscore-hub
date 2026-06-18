import streamlit as st
from datetime import datetime
import pandas as pd

st.set_page_config(
    page_title="SurgiScore Hub",
    page_icon="🏥",
    layout="wide"
)

# ---------------------------
# Session storage
# ---------------------------
if "patients" not in st.session_state:
    st.session_state.patients = []

if "results" not in st.session_state:
    st.session_state.results = []

if "attachments" not in st.session_state:
    st.session_state.attachments = {}

# ---------------------------
# Styling
# ---------------------------
st.markdown("""
<style>
.main-title {
    font-size: 38px;
    font-weight: 800;
}
.card {
    padding: 20px;
    border-radius: 18px;
    background-color: #f8f9fb;
    border: 1px solid #e6e8ec;
    margin-bottom: 15px;
}
.high-risk {
    color: #b00020;
    font-weight: 700;
}
.medium-risk {
    color: #c77700;
    font-weight: 700;
}
.low-risk {
    color: #087f23;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Helper functions
# ---------------------------
def add_patient(code, name, age, sex, diagnosis, operation, notes):
    patient = {
        "code": code,
        "name": name,
        "age": age,
        "sex": sex,
        "diagnosis": diagnosis,
        "operation": operation,
        "notes": notes,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    st.session_state.patients.append(patient)
    st.session_state.attachments[code] = []

def delete_patient(code):
    st.session_state.patients = [
        p for p in st.session_state.patients if p["code"] != code
    ]
    st.session_state.results = [
        r for r in st.session_state.results if r["patient_code"] != code
    ]
    if code in st.session_state.attachments:
        del st.session_state.attachments[code]

def save_result(patient_code, score_name, score_value, interpretation, risk):
    st.session_state.results.append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "patient_code": patient_code,
        "score": score_name,
        "result": score_value,
        "interpretation": interpretation,
        "risk": risk
    })
    st.success("Result saved successfully.")

def get_patient(code):
    for p in st.session_state.patients:
        if p["code"] == code:
            return p
    return None

# ---------------------------
# Header
# ---------------------------
st.markdown('<div class="main-title">🏥 SurgiScore Hub</div>', unsafe_allow_html=True)
st.caption("Professional surgical score calculator with patient registry and attachments")

# ---------------------------
# Sidebar
# ---------------------------
page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Add Patient",
        "Patient Registry",
        "Score Calculator",
        "Attachments",
        "Saved Results"
    ]
)

# ---------------------------
# Dashboard
# ---------------------------
if page == "Dashboard":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Patients", len(st.session_state.patients))

    with col2:
        st.metric("Saved Scores", len(st.session_state.results))

    with col3:
        high_risk_count = sum(1 for r in st.session_state.results if r["risk"] == "High")
        st.metric("High Risk Results", high_risk_count)

    st.divider()

    st.subheader("Recent Results")
    if st.session_state.results:
        st.dataframe(pd.DataFrame(st.session_state.results), use_container_width=True)
    else:
        st.info("No results saved yet.")

# ---------------------------
# Add Patient
# ---------------------------
elif page == "Add Patient":
    st.subheader("Add New Patient")

    with st.form("add_patient_form"):
        col1, col2 = st.columns(2)

        with col1:
            code = st.text_input("Patient Code / ID")
            name = st.text_input("Patient Name")
            age = st.number_input("Age", 0, 120, 30)
            sex = st.selectbox("Sex", ["Male", "Female"])

        with col2:
            diagnosis = st.text_input("Diagnosis")
            operation = st.text_input("Planned / Performed Operation")
            notes = st.text_area("Clinical Notes")

        submitted = st.form_submit_button("Save Patient")

        if submitted:
            if not code:
                st.error("Patient code is required.")
            elif get_patient(code):
                st.error("This patient code already exists.")
            else:
                add_patient(code, name, age, sex, diagnosis, operation, notes)
                st.success("Patient added successfully.")

# ---------------------------
# Patient Registry
# ---------------------------
elif page == "Patient Registry":
    st.subheader("Patient Registry")

    if not st.session_state.patients:
        st.info("No patients added yet.")
    else:
        search = st.text_input("Search patient by code or name")

        patients = st.session_state.patients
        if search:
            patients = [
                p for p in patients
                if search.lower() in p["code"].lower()
                or search.lower() in p["name"].lower()
            ]

        for p in patients:
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                col1, col2, col3 = st.columns([3, 3, 1])

                with col1:
                    st.write(f"**Code:** {p['code']}")
                    st.write(f"**Name:** {p['name']}")
                    st.write(f"**Age/Sex:** {p['age']} / {p['sex']}")

                with col2:
                    st.write(f"**Diagnosis:** {p['diagnosis']}")
                    st.write(f"**Operation:** {p['operation']}")
                    st.write(f"**Created:** {p['created_at']}")

                with col3:
                    if st.button("Delete", key=f"delete_{p['code']}"):
                        delete_patient(p["code"])
                        st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# Score Calculator
# ---------------------------
elif page == "Score Calculator":
    st.subheader("Score Calculator")

    if not st.session_state.patients:
        st.warning("Add a patient first.")
    else:
        patient_codes = [p["code"] for p in st.session_state.patients]
        patient_code = st.selectbox("Select Patient", patient_codes)
        patient = get_patient(patient_code)

        st.info(
            f"Patient: {patient['name']} | Age: {patient['age']} | Diagnosis: {patient['diagnosis']}"
        )

        score_type = st.selectbox(
            "Choose Score",
            [
                "ASA",
                "Alvarado",
                "RCRI",
                "qSOFA",
                "BISAP",
                "Glasgow-Blatchford",
                "Clavien-Dindo"
            ]
        )

        st.divider()

        if score_type == "ASA":
            asa = st.radio(
                "ASA Physical Status",
                [
                    "ASA I - Normal healthy patient",
                    "ASA II - Mild systemic disease",
                    "ASA III - Severe systemic disease",
                    "ASA IV - Severe systemic disease that is a constant threat to life",
                    "ASA V - Moribund patient not expected to survive without operation"
                ]
            )

            result = asa.split(" - ")[0]
            interpretation = asa
            risk = "Low" if result in ["ASA I", "ASA II"] else "High"

            st.metric("Result", result)
            st.write(interpretation)

            if st.button("Save Result"):
                save_result(patient_code, "ASA", result, interpretation, risk)

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
                interpretation = "Unlikely appendicitis"
                risk = "Low"
            elif score <= 6:
                interpretation = "Possible appendicitis"
                risk = "Medium"
            elif score <= 8:
                interpretation = "Probable appendicitis"
                risk = "High"
            else:
                interpretation = "Very probable appendicitis"
                risk = "High"

            st.metric("Alvarado Score", f"{score}/10")
            st.write(interpretation)

            if st.button("Save Result"):
                save_result(patient_code, "Alvarado", score, interpretation, risk)

        elif score_type == "RCRI":
            score = 0
            items = [
                "High-risk surgery",
                "History of ischemic heart disease",
                "History of heart failure",
                "History of cerebrovascular disease",
                "Insulin-dependent diabetes",
                "Creatinine > 2 mg/dL"
            ]

            for item in items:
                if st.checkbox(item):
                    score += 1

            if score == 0:
                interpretation = "Low cardiac risk"
                risk = "Low"
            elif score == 1:
                interpretation = "Intermediate cardiac risk"
                risk = "Medium"
            else:
                interpretation = "High cardiac risk"
                risk = "High"

            st.metric("RCRI", score)
            st.write(interpretation)

            if st.button("Save Result"):
                save_result(patient_code, "RCRI", score, interpretation, risk)

        elif score_type == "qSOFA":
            score = 0
            if st.checkbox("Respiratory rate ≥ 22/min"): score += 1
            if st.checkbox("Altered mentation"): score += 1
            if st.checkbox("Systolic BP ≤ 100 mmHg"): score += 1

            if score >= 2:
                interpretation = "High risk of poor outcome in suspected sepsis"
                risk = "High"
            else:
                interpretation = "Lower risk"
                risk = "Low"

            st.metric("qSOFA", f"{score}/3")
            st.write(interpretation)

            if st.button("Save Result"):
                save_result(patient_code, "qSOFA", score, interpretation, risk)

        elif score_type == "BISAP":
            score = 0
            if st.checkbox("BUN > 25 mg/dL"): score += 1
            if st.checkbox("Impaired mental status"): score += 1
            if st.checkbox("SIRS present"): score += 1
            if st.checkbox("Age > 60 years"): score += 1
            if st.checkbox("Pleural effusion"): score += 1

            if score >= 3:
                interpretation = "Higher risk of severe pancreatitis or mortality"
                risk = "High"
            else:
                interpretation = "Lower risk"
                risk = "Low"

            st.metric("BISAP", f"{score}/5")
            st.write(interpretation)

            if st.button("Save Result"):
                save_result(patient_code, "BISAP", score, interpretation, risk)

        elif score_type == "Glasgow-Blatchford":
            st.warning("Simplified GBS version")

            bun = st.number_input("BUN mg/dL", 0.0, 200.0, 20.0)
            hb = st.number_input("Hemoglobin g/dL", 0.0, 25.0, 12.0)
            sbp = st.number_input("Systolic BP", 40, 250, 120)
            pulse = st.number_input("Pulse", 30, 220, 80)
            melena = st.checkbox("Melena")
            syncope = st.checkbox("Syncope")
            liver = st.checkbox("Liver disease")
            cardiac = st.checkbox("Cardiac failure")

            score = 0
            if bun >= 28: score += 2
            if hb < 12: score += 2
            if sbp < 100: score += 2
            if pulse >= 100: score += 1
            if melena: score += 1
            if syncope: score += 2
            if liver: score += 2
            if cardiac: score += 2

            if score == 0:
                interpretation = "Very low risk; outpatient management may be considered"
                risk = "Low"
            elif score <= 5:
                interpretation = "Moderate risk"
                risk = "Medium"
            else:
                interpretation = "High risk; admission/endoscopy usually required"
                risk = "High"

            st.metric("Simplified GBS", score)
            st.write(interpretation)

            if st.button("Save Result"):
                save_result(patient_code, "Glasgow-Blatchford", score, interpretation, risk)

        elif score_type == "Clavien-Dindo":
            grade = st.selectbox(
                "Complication Grade",
                [
                    "Grade I - Minor deviation, no pharmacological/surgical intervention",
                    "Grade II - Pharmacological treatment required",
                    "Grade IIIa - Intervention without general anesthesia",
                    "Grade IIIb - Intervention under general anesthesia",
                    "Grade IV - Life-threatening complication requiring ICU",
                    "Grade V - Death"
                ]
            )

            result = grade.split(" - ")[0]
            interpretation = grade
            risk = "High" if result in ["Grade IIIb", "Grade IV", "Grade V"] else "Medium"

            st.metric("Clavien-Dindo", result)
            st.write(interpretation)

            if st.button("Save Result"):
                save_result(patient_code, "Clavien-Dindo", result, interpretation, risk)

# ---------------------------
# Attachments
# ---------------------------
elif page == "Attachments":
    st.subheader("Patient Attachments")

    if not st.session_state.patients:
        st.warning("Add a patient first.")
    else:
        patient_codes = [p["code"] for p in st.session_state.patients]
        patient_code = st.selectbox("Select Patient", patient_codes)

        uploaded_files = st.file_uploader(
            "Upload lab results, CT images, operative notes, or photos",
            type=["png", "jpg", "jpeg", "pdf", "txt", "csv"],
            accept_multiple_files=True
        )

        if uploaded_files:
            for file in uploaded_files:
                file_data = {
                    "name": file.name,
                    "type": file.type,
                    "size_kb": round(file.size / 1024, 2),
                    "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "bytes": file.getvalue()
                }

                if file.name not in [f["name"] for f in st.session_state.attachments[patient_code]]:
                    st.session_state.attachments[patient_code].append(file_data)

            st.success("Files attached successfully.")

        st.divider()
        st.subheader("Current Attachments")

        files = st.session_state.attachments.get(patient_code, [])

        if not files:
            st.info("No attachments for this patient.")
        else:
            for i, f in enumerate(files):
                col1, col2, col3 = st.columns([4, 2, 1])

                with col1:
                    st.write(f"**{f['name']}**")
                    st.caption(f"{f['type']} | {f['size_kb']} KB | {f['uploaded_at']}")

                with col2:
                    st.download_button(
                        "Download",
                        data=f["bytes"],
                        file_name=f["name"],
                        mime=f["type"],
                        key=f"download_{patient_code}_{i}"
                    )

                with col3:
                    if st.button("Delete", key=f"delete_file_{patient_code}_{i}"):
                        st.session_state.attachments[patient_code].pop(i)
                        st.rerun()

                if f["type"].startswith("image"):
                    st.image(f["bytes"], width=300)

# ---------------------------
# Saved Results
# ---------------------------
elif page == "Saved Results":
    st.subheader("Saved Results")

    if not st.session_state.results:
        st.info("No saved results yet.")
    else:
        df = pd.DataFrame(st.session_state.results)

        search = st.text_input("Search by patient code or score")

        if search:
            df = df[
                df["patient_code"].str.contains(search, case=False, na=False)
                | df["score"].str.contains(search, case=False, na=False)
            ]

        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Results as CSV",
            csv,
            "surgiscore_results.csv",
            "text/csv"
        )
