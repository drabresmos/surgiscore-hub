import streamlit as st
import pandas as pd
import os, json
from database import *
from scores_library import CATEGORIES, render_score
from styles import inject_css

st.set_page_config(page_title='SurgiScore Hub v3', page_icon='🏥', layout='wide')
st.markdown(inject_css(), unsafe_allow_html=True)
init_db()

st.markdown('''<div class="hero"><span class="pill">Board Surgery Edition • Mobile & iPad ready</span><h1>🏥 SurgiScore Hub</h1><p>Professional surgical scoring, patient timeline, attachments, and board-student learning tools.</p></div>''', unsafe_allow_html=True)

with st.sidebar:
    st.title('SurgiScore')
    page = st.radio('Menu', ['Home','Patients','Score Calculator','Patient Timeline','Attachments','Board Study','Data Export'], label_visibility='collapsed')
    st.caption('v3 • Streamlit Cloud compatible')

patients = get_patients()
patient_codes = [p['code'] for p in patients]

def pick_patient():
    if not patient_codes:
        st.warning('Add a patient first from Patients page.'); return None
    code=st.selectbox('Select patient', patient_codes)
    p=get_patient(code)
    st.markdown(f'''<div class="card"><b>{p['code']} — {p['name']}</b><br><span class="muted">{p['age']} years • {p['sex']} • {p['diagnosis']} • {p['operation']}</span></div>''', unsafe_allow_html=True)
    return p

def risk_html(r):
    cls={'Low':'risk-low','Medium':'risk-medium','High':'risk-high'}.get(r,'')
    return f"<span class='{cls}'>{r}</span>"

if page=='Home':
    results=get_results()
    c1,c2,c3,c4=st.columns(4)
    c1.metric('Patients',len(patients)); c2.metric('Saved scores',len(results)); c3.metric('High risk',sum(1 for r in results if r['risk']=='High')); c4.metric('Score groups',len(CATEGORIES))
    st.markdown('<div class="section-title">Quick workflow</div>', unsafe_allow_html=True)
    a,b,c=st.columns(3)
    a.markdown('<div class="mini-card"><b>1. Register patient</b><br><span class="muted">Code, diagnosis, operation, notes.</span></div>', unsafe_allow_html=True)
    b.markdown('<div class="mini-card"><b>2. Calculate score</b><br><span class="muted">Choose category and score.</span></div>', unsafe_allow_html=True)
    c.markdown('<div class="mini-card"><b>3. Review timeline</b><br><span class="muted">Saved results + attachments.</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Recent results</div>', unsafe_allow_html=True)
    if results: st.dataframe(pd.DataFrame(results).drop(columns=['inputs_json'], errors='ignore'), use_container_width=True)
    else: st.info('No scores yet.')

elif page=='Patients':
    tab1,tab2=st.tabs(['Add / Edit','Registry'])
    with tab1:
        st.markdown('<div class="section-title">Add new patient</div>', unsafe_allow_html=True)
        with st.form('add_patient'):
            col1,col2=st.columns(2)
            with col1:
                code=st.text_input('Patient code / ID'); name=st.text_input('Name'); age=st.number_input('Age',0,120,30); sex=st.selectbox('Sex',['Male','Female'])
            with col2:
                diagnosis=st.text_input('Diagnosis'); operation=st.text_input('Operation / plan'); notes=st.text_area('Clinical notes')
            if st.form_submit_button('Save patient'):
                if not code: st.error('Patient code is required.')
                elif get_patient(code): st.error('Code already exists.')
                else: add_patient(code,name,age,sex,diagnosis,operation,notes); st.success('Saved.'); st.rerun()
        st.markdown('<div class="section-title">Edit existing patient</div>', unsafe_allow_html=True)
        if patient_codes:
            code=st.selectbox('Patient to edit', patient_codes, key='edit_patient'); p=get_patient(code)
            with st.form('edit_form'):
                col1,col2=st.columns(2)
                with col1:
                    name=st.text_input('Name',p['name']); age=st.number_input('Age',0,120,int(p['age'] or 0)); sex=st.selectbox('Sex',['Male','Female'], index=0 if p['sex']=='Male' else 1)
                with col2:
                    diagnosis=st.text_input('Diagnosis',p['diagnosis']); operation=st.text_input('Operation',p['operation']); notes=st.text_area('Notes',p['notes'])
                if st.form_submit_button('Update patient'):
                    update_patient(code,name,age,sex,diagnosis,operation,notes); st.success('Updated.'); st.rerun()
    with tab2:
        st.markdown('<div class="section-title">Patient registry</div>', unsafe_allow_html=True)
        q=st.text_input('Search by code/name/diagnosis')
        data=patients
        if q: data=[p for p in data if q.lower() in (p['code']+p['name']+p['diagnosis']).lower()]
        for p in data:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            col1,col2,col3=st.columns([3,3,1])
            col1.write(f"**{p['code']} — {p['name']}**"); col1.caption(f"{p['age']} years • {p['sex']}")
            col2.write(f"**Diagnosis:** {p['diagnosis']}"); col2.write(f"**Operation:** {p['operation']}"); col2.caption(p['created_at'])
            if col3.button('Delete', key=f"delp{p['code']}"):
                delete_patient(p['code']); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

elif page=='Score Calculator':
    p=pick_patient()
    if p:
        col1,col2=st.columns([1,1])
        category=col1.selectbox('Category', list(CATEGORIES.keys()))
        score_name=col2.selectbox('Score', CATEGORIES[category])
        st.markdown('<div class="card">', unsafe_allow_html=True)
        result,risk,interp,inputs=render_score(score_name)
        st.metric('Result', result)
        st.markdown(f'Risk category: {risk_html(risk)}', unsafe_allow_html=True)
        st.markdown(f'<div class="clinical-box"><b>Clinical interpretation</b><br>{interp}<br><br><b>Board note:</b> Document the score with the clinical context. Do not use scores as a substitute for senior review or operative judgement.</div>', unsafe_allow_html=True)
        summary=f"Patient {p['code']} ({p['age']}y {p['sex']}), diagnosis: {p['diagnosis']}. {score_name} = {result}. Risk: {risk}. Interpretation: {interp}"
        st.text_area('Copy clinical summary', summary, height=100)
        if st.button('Save result'):
            save_result(p['code'],category,score_name,result,risk,interp,inputs); st.success('Result saved.'); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

elif page=='Patient Timeline':
    p=pick_patient()
    if p:
        st.markdown('<div class="section-title">Timeline</div>', unsafe_allow_html=True)
        results=get_results(p['code']); atts=get_attachments(p['code'])
        tab1,tab2=st.tabs(['Scores','Attachments'])
        with tab1:
            if results:
                for r in results:
                    st.markdown(f'''<div class="card"><b>{r['score_name']}</b> — {r['result']} • {risk_html(r['risk'])}<br><span class="muted">{r['created_at']} • {r['category']}</span><div class="clinical-box">{r['interpretation']}</div></div>''', unsafe_allow_html=True)
                    if st.button('Delete result', key=f"delr{r['id']}"):
                        delete_result(r['id']); st.rerun()
            else: st.info('No saved results for this patient.')
        with tab2:
            if atts:
                for a in atts:
                    st.markdown(f'''<div class="card"><b>{a['filename']}</b><br><span class="muted">{a['filetype']} • {a['size_kb']} KB • {a['created_at']}</span></div>''', unsafe_allow_html=True)
            else: st.info('No attachments.')

elif page=='Attachments':
    p=pick_patient()
    if p:
        files=st.file_uploader('Attach labs, CT images, photos, operative notes, PDF', type=['png','jpg','jpeg','pdf','txt','csv'], accept_multiple_files=True)
        if files:
            for f in files: save_attachment(p['code'],f)
            st.success('Uploaded.'); st.rerun()
        for a in get_attachments(p['code']):
            st.markdown('<div class="card">', unsafe_allow_html=True)
            c1,c2,c3=st.columns([3,2,1])
            c1.write(f"**{a['filename']}**"); c1.caption(f"{a['filetype']} • {a['size_kb']} KB • {a['created_at']}")
            with open(a['path'],'rb') as fh: data=fh.read()
            c2.download_button('Download', data, a['filename'], a['filetype'], key=f"down{a['id']}")
            if c3.button('Delete', key=f"dela{a['id']}"):
                delete_attachment(a['id']); st.rerun()
            if a['filetype'] and a['filetype'].startswith('image'):
                st.image(data, width=360)
            st.markdown('</div>', unsafe_allow_html=True)

elif page=='Board Study':
    st.markdown('<div class="section-title">Board Surgery Study Mode</div>', unsafe_allow_html=True)
    st.info('Use this page during rounds or seminars: pick a score, read its use, then calculate it on a real or simulated case.')
    category=st.selectbox('Score group', list(CATEGORIES.keys()), key='studycat')
    score=st.selectbox('Score to revise', CATEGORIES[category], key='studyscore')
    st.markdown(f'<div class="card"><h3>{score}</h3><p class="muted">Category: {category}</p><div class="clinical-box"><b>How to present in board exam:</b><br>1) State indication. 2) Mention main variables. 3) Give cut-off/risk group. 4) Link result to management, imaging, admission, or senior review.</div></div>', unsafe_allow_html=True)
    note=st.text_area('Your learning note / viva pearl')
    if st.button('Save learning note') and note:
        add_learning_note(score,note); st.success('Saved.')
    notes=get_learning_notes()
    if notes: st.dataframe(pd.DataFrame(notes), use_container_width=True)

elif page=='Data Export':
    st.markdown('<div class="section-title">Export / Backup</div>', unsafe_allow_html=True)
    p_df=pd.DataFrame(get_patients()); r_df=pd.DataFrame(get_results())
    st.download_button('Download patients CSV', p_df.to_csv(index=False).encode('utf-8'), 'patients.csv', 'text/csv')
    st.download_button('Download results CSV', r_df.to_csv(index=False).encode('utf-8'), 'results.csv', 'text/csv')
    st.caption('For production use, migrate from Streamlit local SQLite to Supabase/PostgreSQL for durable multi-user storage.')
