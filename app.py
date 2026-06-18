# app.py

import streamlit as st

st.set_page_config(page_title="SurgiScore Hub")

st.title("🏥 SurgiScore Hub")

st.header("Alvarado Score")

score = 0

if st.checkbox("Migration of pain"):
    score += 1

if st.checkbox("Anorexia"):
    score += 1

if st.checkbox("Nausea/Vomiting"):
    score += 1

if st.checkbox("RIF Tenderness"):
    score += 2

if st.checkbox("Rebound Tenderness"):
    score += 1

if st.checkbox("Fever"):
    score += 1

if st.checkbox("Leukocytosis"):
    score += 2

if st.checkbox("Neutrophilia"):
    score += 1

st.metric("Score", score)

if score <= 4:
    st.success("Unlikely appendicitis")
elif score <= 6:
    st.warning("Possible appendicitis")
elif score <= 8:
    st.warning("Probable appendicitis")
else:
    st.error("Very probable appendicitis")
