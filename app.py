import streamlit as st
import pandas as pd
import database as db
from styles import apply_style, hero
from scores_library import SCORES, ALL_SCORES, render_score

st.set_page_config(page_title='SurgiScore Hub', page_icon='🏥', layout='wide')
db.init_db(); apply_style(); hero()

st.sidebar.title('SurgiScore')
page = st.sidebar.radio('Navigation', ['Dashboard','Add Patient','Patient Registry','Score Calculator','Attachments','Saved Results'])
patients = db.list_patients()

if page == 'Dashboard':
    st.markdown('### Dashboard')
    results = db.list_results()
    c1,c2,c3,c4 = st.columns(4)
    c1.metric('Patients', len(patients))
    c2.metric('Saved Scores', len(results))
    c3.metric('High Risk', sum(1 for r in results if r['risk']=='High'))
    c4.metric('Available Scores', len(ALL_SCORES))
    st.markdown('### Score Library')
    for category, items in SCORES.items():
        with st.expander(category, expanded=False):
            st.write(' · '.join(items))
    st.markdown('### Recent Results')
    if results:
        st.dataframe(pd.DataFrame(results), use_container_width=True)
    else:
        st.info('No saved results yet.')

elif page == 'Add Patient':
    st.markdown('### Add Patient')
    with st.form('add_patient_form'):
        col1,col2 = st.columns(2)
        with col1:
            code = st.text_input('Patient Code / ID')
            name = st.text_input('Patient Name')
            age = st.number_input('Age', 0, 120, 30)
            sex = st.selectbox('Sex', ['Male','Female'])
        with col2:
            diagnosis = st.text_input('Diagnosis')
            operation = st.text_input('Operation')
            notes = st.text_area('Clinical Notes')
        if st.form_submit_button('Save Patient'):
            if not code:
                st.error('Patient code is required.')
            elif db.get_patient(code):
                st.error('This patient code already exists.')
            else:
                db.add_patient(code,name,age,sex,diagnosis,operation,notes)
                st.success('Patient added successfully.')
                st.rerun()

elif page == 'Patient Registry':
    st.markdown('### Patient Registry')
    if not patients:
        st.info('No patients added yet.')
    else:
        search = st.text_input('Search patient by code or name')
        shown = patients
        if search:
            shown = [p for p in patients if search.lower() in p['code'].lower() or search.lower() in (p['name'] or '').lower()]
        for p in shown:
            st.markdown('<div class="apple-card">', unsafe_allow_html=True)
            c1,c2,c3 = st.columns([3,3,1])
            c1.write(f"**{p['code']} — {p['name']}**")
            c1.caption(f"{p['age']} years | {p['sex']}")
            c2.write(f"**Diagnosis:** {p['diagnosis']}")
            c2.write(f"**Operation:** {p['operation']}")
            c2.caption(f"Created: {p['created_at']}")
            if c3.button('Delete', key=f"del_{p['code']}"):
                db.delete_patient(p['code']); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

elif page == 'Score Calculator':
    st.markdown('### Score Calculator')
    if not patients:
        st.warning('Add a patient first.')
    else:
        patient_code = st.selectbox('Select Patient', [p['code'] for p in patients])
        p = db.get_patient(patient_code)
        st.markdown('<div class="apple-card">', unsafe_allow_html=True)
        st.write(f"**Patient:** {p['name']} | **Age:** {p['age']} | **Sex:** {p['sex']} | **Diagnosis:** {p['diagnosis']}")
        st.markdown('</div>', unsafe_allow_html=True)
        category = st.selectbox('Category', list(SCORES.keys()))
        score_name = st.selectbox('Choose Score', SCORES[category])
        st.divider()
        render_score(score_name, patient_code, db)

elif page == 'Attachments':
    st.markdown('### Attachments')
    if not patients:
        st.warning('Add a patient first.')
    else:
        patient_code = st.selectbox('Select Patient', [p['code'] for p in patients])
        files = st.file_uploader('Attach labs, CT images, photos, PDF reports', type=['png','jpg','jpeg','pdf','txt','csv'], accept_multiple_files=True)
        if files:
            for f in files:
                db.add_attachment(patient_code, f)
            st.success('Files attached.')
            st.rerun()
        attachments = db.list_attachments(patient_code)
        if not attachments:
            st.info('No attachments for this patient.')
        for a in attachments:
            full = db.get_attachment(a['id'])
            st.markdown('<div class="apple-card">', unsafe_allow_html=True)
            c1,c2,c3 = st.columns([4,2,1])
            c1.write(f"**{a['filename']}**")
            c1.caption(f"{a['mime']} | {a['size_kb']} KB | {a['created_at']}")
            c2.download_button('Download', full['data'], a['filename'], a['mime'], key=f"down_{a['id']}")
            if c3.button('Delete', key=f"attdel_{a['id']}"):
                db.delete_attachment(a['id']); st.rerun()
            if a['mime'] and a['mime'].startswith('image'):
                st.image(full['data'], width=360)
            st.markdown('</div>', unsafe_allow_html=True)

elif page == 'Saved Results':
    st.markdown('### Saved Results')
    results = db.list_results()
    if not results:
        st.info('No saved results yet.')
    else:
        df = pd.DataFrame(results)
        search = st.text_input('Search by patient code or score')
        if search:
            df = df[df['patient_code'].str.contains(search, case=False, na=False) | df['score'].str.contains(search, case=False, na=False)]
        st.dataframe(df, use_container_width=True)
        st.download_button('Download CSV', df.to_csv(index=False).encode('utf-8'), 'surgiscore_results.csv', 'text/csv')
