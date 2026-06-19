import streamlit as st
from datetime import datetime


def init_state():
    st.session_state.setdefault('patients', [])
    st.session_state.setdefault('results', [])
    st.session_state.setdefault('attachments', {})


def get_patient(code):
    return next((p for p in st.session_state.patients if p['code'] == code), None)


def add_patient(code, name, age, sex, diagnosis, operation, notes):
    st.session_state.patients.append({
        'code': code, 'name': name, 'age': age, 'sex': sex,
        'diagnosis': diagnosis, 'operation': operation, 'notes': notes,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M')
    })
    st.session_state.attachments.setdefault(code, [])


def update_patient(code, name, age, sex, diagnosis, operation, notes):
    p = get_patient(code)
    if p:
        p.update({'name': name, 'age': age, 'sex': sex, 'diagnosis': diagnosis, 'operation': operation, 'notes': notes})


def delete_patient(code):
    st.session_state.patients = [p for p in st.session_state.patients if p['code'] != code]
    st.session_state.results = [r for r in st.session_state.results if r['patient_code'] != code]
    st.session_state.attachments.pop(code, None)


def save_result(patient_code, score_name, category, result, interpretation, recommendation, risk):
    st.session_state.results.append({
        'time': datetime.now().strftime('%Y-%m-%d %H:%M'), 'patient_code': patient_code,
        'category': category, 'score': score_name, 'result': result,
        'interpretation': interpretation, 'recommendation': recommendation, 'risk': risk
    })
