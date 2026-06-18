import streamlit as st
from datetime import datetime

st.set_page_config(page_title="SurgiScore Hub", layout="wide")

if "results" not in st.session_state:
    st.session_state.results = []

st.title("🏥 SurgiScore Hub")
st.caption("Surgical scores calculator for general surgery")

patient = st.sidebar.text_input("Patient name / code")
age = st.sidebar.number_input("Age", 0, 120, 30)
sex = st.sidebar.selectbox("Sex", ["Male", "Female"])

score_type = st.sidebar.selectbox(
    "Choose score",
    ["ASA", "Alvarado", "RCRI", "qSOFA", "BISAP"]
)

def save_result(name, score, interpretation):
    st.session_state.results.append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "patient": patient,
        "age": age,
        "sex": sex,
        "score": name,
        "result": score,
        "interpretation": interpretation
    })
    st.success("Result saved")

st.header(score_type)

if score_type == "ASA":
    asa = st.radio(
        "ASA Physical Status",
        [
            "ASA I - Normal healthy patient",
            "ASA II - Mild systemic disease",
            "ASA III - Severe systemic disease",
            "ASA IV - Severe disease constant threat to life",
            "ASA V - Moribund patient"
        ]
    )
    result = asa.split(" - ")[0]
    interp = asa
    st.metric("Result", result)
    if st.button("Save result"):
        save_result("ASA", result, interp)

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
        interp = "Unlikely appendicitis"
    elif score <= 6:
        interp = "Possible appendicitis"
    elif score <= 8:
        interp = "Probable appendicitis"
    else:
        interp = "Very probable appendicitis"

    st.metric("Alvarado Score", f"{score}/10")
    st.info(interp)
    if st.button("Save result"):
        save_result("Alvarado", score, interp)

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
        interp = "Low cardiac risk"
    elif score == 1:
        interp = "Intermediate cardiac risk"
    else:
        interp = "High cardiac risk"

    st.metric("RCRI", score)
    st.warning(interp)
    if st.button("Save result"):
        save_result("RCRI", score, interp)

elif score_type == "qSOFA":
    score = 0
    if st.checkbox("Respiratory rate ≥ 22/min"): score += 1
    if st.checkbox("Altered mentation"): score += 1
    if st.checkbox("Systolic BP ≤ 100 mmHg"): score += 1

    interp = "High risk of poor outcome in suspected sepsis" if score >= 2 else "Lower risk"
    st.metric("qSOFA", f"{score}/3")
    st.info(interp)
    if st.button("Save result"):
        save_result("qSOFA", score, interp)

elif score_type == "BISAP":
    score = 0
    if st.checkbox("BUN > 25 mg/dL"): score += 1
    if st.checkbox("Impaired mental status"): score += 1
    if st.checkbox("SIRS present"): score += 1
    if st.checkbox("Age > 60 years"): score += 1
    if st.checkbox("Pleural effusion"): score += 1

    interp = "Higher risk severe pancreatitis/mortality" if score >= 3 else "Lower risk"
    st.metric("BISAP", f"{score}/5")
    st.info(interp)
    if st.button("Save result"):
        save_result("BISAP", score, interp)

st.divider()
st.subheader("Saved Results")

if st.session_state.results:
    st.dataframe(st.session_state.results, use_container_width=True)
else:
    st.write("No saved results yet.")
