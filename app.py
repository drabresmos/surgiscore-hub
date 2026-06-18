import streamlit as st
import pandas as pd
from datetime import datetime
from styles import apply_styles
from database import init_state, add_patient, get_patient, update_patient, delete_patient, save_result
from scores_library import SCORES, calc_score
from reports import clinical_summary

st.set_page_config(page_title='SurgiScore Hub v2', page_icon='🏥', layout='wide')
init_state()
apply_styles()

st.markdown('''
<div class="hero">
  <div class="title">🏥 SurgiScore Hub v2</div>
  <div class="subtitle">Apple-style surgical score platform with patient timeline, attachments, summaries, and export.</div>
</div>
''', unsafe_allow_html=True)

st.sidebar.title('SurgiScore')
page = st.sidebar.radio('Navigation', ['Dashboard','Add Patient','Patient Registry','Patient Timeline','Score Calculator','Attachments','Saved Results'])

all_scores = [s for group in SCORES.values() for s in group]

if page == 'Dashboard':
    c1,c2,c3,c4 = st.columns(4)
    c1.metric('Patients', len(st.session_state.patients))
    c2.metric('Saved Scores', len(st.session_state.results))
    c3.metric('High Risk', sum(1 for r in st.session_state.results if r['risk']=='High'))
    c4.metric('Scores Library', len(all_scores))
    st.markdown('### Score Categories')
    cols = st.columns(3)
    for i,(cat,items) in enumerate(SCORES.items()):
        with cols[i%3]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f'**{cat}**')
            st.caption(f'{len(items)} scores')
            st.write(', '.join(items[:5]) + ('...' if len(items)>5 else ''))
            st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('### Recent Results')
    if st.session_state.results:
        st.dataframe(pd.DataFrame(st.session_state.results).tail(10), use_container_width=True)
    else:
        st.info('No results yet.')

elif page == 'Add Patient':
    st.markdown('### Add Patient')
    with st.form('add_patient_form'):
        c1,c2 = st.columns(2)
        with c1:
            code = st.text_input('Patient Code / ID')
            name = st.text_input('Patient Name')
            age = st.number_input('Age',0,120,30)
            sex = st.selectbox('Sex',['Male','Female'])
        with c2:
            diagnosis = st.text_input('Diagnosis')
            operation = st.text_input('Planned / Performed Operation')
            notes = st.text_area('Clinical Notes')
        if st.form_submit_button('Save Patient'):
            if not code: st.error('Patient code is required.')
            elif get_patient(code): st.error('Patient code already exists.')
            else:
                add_patient(code,name,age,sex,diagnosis,operation,notes)
                st.success('Patient added.')

elif page == 'Patient Registry':
    st.markdown('### Patient Registry')
    if not st.session_state.patients:
        st.info('No patients added yet.')
    else:
        search = st.text_input('Search by code/name/diagnosis')
        patients = st.session_state.patients
        if search:
            q=search.lower(); patients=[p for p in patients if q in p['code'].lower() or q in p['name'].lower() or q in p['diagnosis'].lower()]
        for p in patients:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            c1,c2,c3=st.columns([3,3,1])
            c1.write(f"**{p['code']} — {p['name']}**")
            c1.caption(f"{p['age']} years | {p['sex']}")
            c2.write(f"**Diagnosis:** {p['diagnosis']}")
            c2.write(f"**Operation:** {p['operation']}")
            c2.caption(f"Created: {p['created_at']}")
            if c3.button('Delete', key='del_'+p['code']):
                delete_patient(p['code']); st.rerun()
            with st.expander('Edit patient'):
                name=st.text_input('Name',p['name'],key='en'+p['code'])
                age=st.number_input('Age',0,120,p['age'],key='ea'+p['code'])
                sex=st.selectbox('Sex',['Male','Female'],index=['Male','Female'].index(p['sex']),key='es'+p['code'])
                diagnosis=st.text_input('Diagnosis',p['diagnosis'],key='ed'+p['code'])
                operation=st.text_input('Operation',p['operation'],key='eo'+p['code'])
                notes=st.text_area('Notes',p['notes'],key='et'+p['code'])
                if st.button('Update',key='up'+p['code']):
                    update_patient(p['code'],name,age,sex,diagnosis,operation,notes); st.success('Updated.'); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

elif page == 'Patient Timeline':
    st.markdown('### Patient Timeline')
    if not st.session_state.patients: st.warning('Add a patient first.')
    else:
        code=st.selectbox('Patient',[p['code'] for p in st.session_state.patients])
        p=get_patient(code)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write(f"**{p['name']}** | {p['age']} years | {p['sex']}")
        st.write(f"Diagnosis: {p['diagnosis']} | Operation: {p['operation']}")
        st.markdown('</div>', unsafe_allow_html=True)
        rows=[r for r in st.session_state.results if r['patient_code']==code]
        st.markdown('#### Scores Timeline')
        if rows: st.dataframe(pd.DataFrame(rows), use_container_width=True)
        else: st.info('No scores for this patient.')
        st.markdown('#### Attachments')
        for f in st.session_state.attachments.get(code,[]): st.write(f"• {f['name']} — {f['uploaded_at']}")

elif page == 'Score Calculator':
    st.markdown('### Score Calculator')
    if not st.session_state.patients: st.warning('Add a patient first.')
    else:
        code=st.selectbox('Patient',[p['code'] for p in st.session_state.patients])
        p=get_patient(code)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write(f"**Patient:** {p['name']} | **Age:** {p['age']} | **Diagnosis:** {p['diagnosis']}")
        st.markdown('</div>', unsafe_allow_html=True)
        category=st.selectbox('Category', list(SCORES.keys()))
        score_name=st.selectbox('Score', SCORES[category])
        st.divider()
        result, interp, rec, risk = calc_score(score_name)
        st.metric('Result', result)
        color = {'Low':'low','Medium':'medium','High':'high'}.get(risk,'')
        st.markdown(f"<span class='{color}'>Risk: {risk}</span>", unsafe_allow_html=True)
        st.info(interp)
        st.write('**Recommendation:**', rec)
        if st.button('Save Result'):
            save_result(code,score_name,category,result,interp,rec,risk)
            st.rerun()

elif page == 'Attachments':
    st.markdown('### Attachments')
    if not st.session_state.patients: st.warning('Add a patient first.')
    else:
        code=st.selectbox('Patient',[p['code'] for p in st.session_state.patients])
        files=st.file_uploader('Attach labs, CT images, photos, PDF reports', type=['png','jpg','jpeg','pdf','txt','csv'], accept_multiple_files=True)
        if files:
            for f in files:
                item={'name':f.name,'type':f.type,'size_kb':round(f.size/1024,1),'uploaded_at':datetime.now().strftime('%Y-%m-%d %H:%M'),'bytes':f.getvalue()}
                if f.name not in [x['name'] for x in st.session_state.attachments.setdefault(code,[])]: st.session_state.attachments[code].append(item)
            st.success('Files attached.')
        for i,f in enumerate(st.session_state.attachments.get(code,[])):
            st.markdown('<div class="card">', unsafe_allow_html=True)
            c1,c2,c3=st.columns([4,2,1])
            c1.write(f"**{f['name']}**"); c1.caption(f"{f['type']} | {f['size_kb']} KB | {f['uploaded_at']}")
            c2.download_button('Download',f['bytes'],f['name'],f['type'],key=f'down{i}')
            if c3.button('Delete',key=f'fdel{i}'):
                st.session_state.attachments[code].pop(i); st.rerun()
            if f['type'].startswith('image'): st.image(f['bytes'], width=360)
            st.markdown('</div>', unsafe_allow_html=True)

elif page == 'Saved Results':
    st.markdown('### Saved Results')
    if not st.session_state.results: st.info('No saved results.')
    else:
        df=pd.DataFrame(st.session_state.results)
        q=st.text_input('Search')
        if q:
            df=df[df.apply(lambda row: q.lower() in ' '.join(map(str,row.values)).lower(), axis=1)]
        st.dataframe(df,use_container_width=True)
        st.download_button('Download CSV', df.to_csv(index=False).encode('utf-8'), 'surgiscore_results.csv', 'text/csv')
        st.markdown('#### Clinical Summary')
        idx=st.number_input('Select row number from filtered table',0,max(len(df)-1,0),0)
        if len(df)>0:
            r=df.iloc[int(idx)].to_dict(); p=get_patient(r['patient_code']) or {}
            summary=clinical_summary(p,r)
            st.text_area('Copy clinical summary',summary,height=260)
            st.download_button('Download Summary TXT',summary.encode('utf-8'),'clinical_summary.txt','text/plain')
