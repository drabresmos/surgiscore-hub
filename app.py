import streamlit as st
import pandas as pd

from database import (
    init_db, add_patient, update_patient, get_patients, get_patient, delete_patient,
    add_result, get_results, delete_result, add_attachment, get_attachments,
    get_attachment_data, delete_attachment
)
from scores_library import CATEGORIES, render_score
from styles import apply_styles, hero, risk_badge

init_db()
st.set_page_config(page_title='SurgiScore Hub', page_icon='🏥', layout='wide')
apply_styles()
hero()

st.sidebar.title('SurgiScore Hub')
page = st.sidebar.radio('Navigation', ['Dashboard','Board Study Mode','Patients','Score Calculator','Attachments','Results / Backup'])

patients = get_patients()
results = get_results()

if page == 'Dashboard':
    c1,c2,c3,c4 = st.columns(4)
    c1.metric('Patients', len(patients))
    c2.metric('Saved Scores', len(results))
    c3.metric('High Risk', sum(1 for r in results if r.get('risk')=='High'))
    c4.metric('Score Categories', len(CATEGORIES))

    st.markdown('### Quick start for board trainees')
    st.markdown('''
<div class="card">
<b>Workflow:</b> Add patient → choose clinical category → calculate score → save result → attach labs/images → export backup.
<br><br>
<span class="small">This app is an educational and documentation aid. It does not replace consultant judgment, local guidelines, or hospital policy.</span>
</div>
''', unsafe_allow_html=True)

    st.markdown('### Recent Results')
    if results:
        st.dataframe(pd.DataFrame(results), use_container_width=True)
    else:
        st.info('No results yet.')

elif page == 'Board Study Mode':
    st.markdown('### Board Study Mode')
    category = st.selectbox('Select surgical domain', list(CATEGORIES.keys()))
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write(f'**{category}**')
    for score in CATEGORIES[category]:
        st.markdown(f'- **{score}**')
    st.markdown('</div>', unsafe_allow_html=True)
    st.info('Use this page as a checklist before exams, ER shifts, and case discussions.')

elif page == 'Patients':
    tab1, tab2 = st.tabs(['Add Patient','Registry / Edit / Delete'])

    with tab1:
        st.markdown('### Add Patient')
        with st.form('add_patient_form'):
            col1,col2 = st.columns(2)
            with col1:
                code = st.text_input('Patient code / ID')
                name = st.text_input('Name')
                age = st.number_input('Age', 0, 120, 30)
                sex = st.selectbox('Sex', ['Male','Female'])
            with col2:
                diagnosis = st.text_input('Diagnosis')
                operation = st.text_input('Operation / plan')
                notes = st.text_area('Clinical notes')
            if st.form_submit_button('Save Patient'):
                if not code.strip():
                    st.error('Patient code is required.')
                else:
                    try:
                        add_patient(code.strip(), name, age, sex, diagnosis, operation, notes)
                        st.success('Patient added.')
                        st.rerun()
                    except Exception as e:
                        st.error(f'Could not add patient. Code may already exist. Details: {e}')

    with tab2:
        st.markdown('### Patient Registry')
        patients = get_patients()
        if not patients:
            st.info('No patients yet.')
        else:
            search = st.text_input('Search by code/name/diagnosis')
            shown = patients
            if search:
                s=search.lower()
                shown=[p for p in patients if s in str(p.get('code','')).lower() or s in str(p.get('name','')).lower() or s in str(p.get('diagnosis','')).lower()]
            for p in shown:
                with st.expander(f"{p['code']} — {p.get('name','')} | {p.get('diagnosis','')}"):
                    with st.form(f'edit_{p["id"]}'):
                        col1,col2=st.columns(2)
                        with col1:
                            code=st.text_input('Code', p.get('code',''), key=f'code_{p["id"]}')
                            name=st.text_input('Name', p.get('name',''), key=f'name_{p["id"]}')
                            age=st.number_input('Age',0,120,int(p.get('age') or 0), key=f'age_{p["id"]}')
                            sex=st.selectbox('Sex',['Male','Female'], index=0 if p.get('sex')!='Female' else 1, key=f'sex_{p["id"]}')
                        with col2:
                            diagnosis=st.text_input('Diagnosis', p.get('diagnosis',''), key=f'dx_{p["id"]}')
                            operation=st.text_input('Operation', p.get('operation',''), key=f'op_{p["id"]}')
                            notes=st.text_area('Notes', p.get('notes',''), key=f'notes_{p["id"]}')
                        a,b=st.columns(2)
                        if a.form_submit_button('Update'):
                            update_patient(p['id'], code, name, age, sex, diagnosis, operation, notes)
                            st.success('Updated.')
                            st.rerun()
                        if b.form_submit_button('Delete patient and all data'):
                            delete_patient(p['id'])
                            st.warning('Deleted.')
                            st.rerun()

elif page == 'Score Calculator':
    st.markdown('### Score Calculator')
    patients = get_patients()
    if not patients:
        st.warning('Add a patient first.')
    else:
        pmap={f"{p['code']} — {p.get('name','')}":p['id'] for p in patients}
        selected = st.selectbox('Patient', list(pmap.keys()))
        pid = pmap[selected]
        patient = get_patient(pid)
        st.markdown(f"<div class='card'><b>{patient['code']} — {patient.get('name','')}</b><br><span class='muted'>{patient.get('age')} years | {patient.get('sex')} | {patient.get('diagnosis')}</span></div>", unsafe_allow_html=True)

        col1,col2 = st.columns(2)
        category = col1.selectbox('Category', list(CATEGORIES.keys()))
        score_name = col2.selectbox('Score', CATEGORIES[category])
        st.divider()
        result, interpretation, risk = render_score(score_name)
        st.markdown('### Result')
        r1,r2=st.columns([1,2])
        r1.metric(score_name, result)
        with r2:
            st.write(interpretation)
            risk_badge(risk)
        summary = f"Patient {patient['code']} ({patient.get('age')}y, {patient.get('sex')}) — {score_name}: {result}. Interpretation: {interpretation}. Risk: {risk}."
        st.text_area('Clinical summary', summary, height=110)
        if st.button('Save Result'):
            add_result(pid, score_name, category, result, interpretation, risk, summary)
            st.success('Result saved.')

elif page == 'Attachments':
    st.markdown('### Attachments')
    patients = get_patients()
    if not patients:
        st.warning('Add a patient first.')
    else:
        pmap={f"{p['code']} — {p.get('name','')}":p['id'] for p in patients}
        selected = st.selectbox('Patient', list(pmap.keys()))
        pid = pmap[selected]
        files = st.file_uploader('Upload labs, CT photos, operative notes, PDFs', type=['png','jpg','jpeg','pdf','txt','csv'], accept_multiple_files=True)
        if files:
            for f in files:
                add_attachment(pid, f.name, f.type, round(f.size/1024,1), f.getvalue())
            st.success('Uploaded.')
            st.rerun()
        for a in get_attachments(pid):
            st.markdown('<div class="card">', unsafe_allow_html=True)
            c1,c2,c3=st.columns([4,2,1])
            c1.write(f"**{a['filename']}**")
            c1.caption(f"{a['filetype']} | {a['size_kb']} KB | {a['created_at']}")
            data=get_attachment_data(a['id'])
            c2.download_button('Download', data['data'], a['filename'], a['filetype'], key=f'down_{a["id"]}')
            if c3.button('Delete', key=f'delatt_{a["id"]}'):
                delete_attachment(a['id']); st.rerun()
            if a['filetype'] and a['filetype'].startswith('image'):
                st.image(data['data'], width=360)
            st.markdown('</div>', unsafe_allow_html=True)

elif page == 'Results / Backup':
    st.markdown('### Results / Backup')
    results=get_results()
    if not results:
        st.info('No results saved.')
    else:
        df=pd.DataFrame(results)
        search=st.text_input('Search results')
        if search:
            s=search.lower()
            df=df[df.astype(str).apply(lambda row: row.str.lower().str.contains(s).any(), axis=1)]
        st.dataframe(df, use_container_width=True)
        st.download_button('Download results CSV', df.to_csv(index=False).encode('utf-8'), 'surgiscore_results.csv', 'text/csv')
        rid=st.number_input('Delete result by ID', min_value=0, step=1)
        if st.button('Delete selected result') and rid:
            delete_result(int(rid)); st.rerun()
