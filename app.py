import streamlit as st
import pandas as pd
from datetime import date, time
from database import *
from styles import apply_styles
from scores_library import CATEGORIES, run_score

init_db()
st.set_page_config(page_title='SurgiScore Hub', page_icon='🏥', layout='wide')
apply_styles()

st.markdown('''<div class="hero"><div class="title">🏥 SurgiScore Hub</div><div class="subtitle">منصة Board-ready لحساب Surgical Scores، حفظ المرضى، المرفقات، وجدولة العمليات.</div><span class="pill">Arabic UI • English Medical Terms • Mobile/iPad ready</span></div>''', unsafe_allow_html=True)

st.sidebar.title('SurgiScore Hub')
lang = st.sidebar.radio('Language / اللغة', ['العربية + English terms','English'], index=0)
page = st.sidebar.radio('Navigation', ['Dashboard','Board Study Mode','Patients','Score Calculator','Operation Schedule','Calendar View','Attachments','Results / Backup'])

patients = get_patients()
patient_options = {f"{p['code']} — {p['name']}": p['id'] for p in patients}

def risk_badge(risk):
    cls = 'low' if risk=='Low' else 'medium' if risk=='Medium' else 'high'
    st.markdown(f"<span class='{cls}'>Risk: {risk}</span>", unsafe_allow_html=True)

if page == 'Dashboard':
    st.subheader('لوحة التحكم Dashboard')
    ops = get_operations(); results = get_results()
    c1,c2,c3,c4 = st.columns(4)
    c1.metric('Patients', len(patients)); c2.metric('Scores', len(results)); c3.metric('Scheduled Operations', len(ops)); c4.metric('High Risk', sum(1 for r in results if r.get('risk')=='High'))
    st.markdown('### عمليات قادمة Upcoming Operations')
    if ops: st.dataframe(pd.DataFrame(ops), use_container_width=True)
    else: st.info('لا توجد عمليات مجدولة بعد.')

elif page == 'Board Study Mode':
    st.subheader('وضع طلبة البورد Board Study Mode')
    st.info('اختر category ثم score. المصطلحات الطبية تبقى English لتناسب الامتحانات والـ rounds.')
    for cat, scores in CATEGORIES.items():
        with st.expander(cat, expanded=False):
            for s in scores:
                st.write(f'• **{s}**')

elif page == 'Patients':
    st.subheader('المرضى Patients')
    tab1, tab2 = st.tabs(['إضافة مريض Add Patient','السجل Registry'])
    with tab1:
        with st.form('add_patient'):
            col1,col2 = st.columns(2)
            with col1:
                code=st.text_input('Patient Code / ID'); name=st.text_input('Patient Name'); age=st.number_input('Age',0,120,30); sex=st.selectbox('Sex',['Male','Female'])
            with col2:
                diagnosis=st.text_input('Diagnosis'); operation=st.text_input('Planned / Performed Operation'); notes=st.text_area('Clinical Notes')
            if st.form_submit_button('Save Patient'):
                if not code: st.error('Patient Code مطلوب')
                else: add_patient(code,name,age,sex,diagnosis,operation,notes); st.success('تم حفظ المريض'); st.rerun()
    with tab2:
        q=st.text_input('Search by code/name/diagnosis')
        rows=patients
        if q: rows=[p for p in rows if q.lower() in str(p).lower()]
        for p in rows:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            c1,c2,c3=st.columns([3,3,1])
            c1.write(f"**{p['code']} — {p['name']}**"); c1.caption(f"{p['age']} years | {p['sex']}")
            c2.write(f"**Diagnosis:** {p['diagnosis']}"); c2.write(f"**Operation:** {p['operation']}")
            if c3.button('Delete', key=f"delp{p['id']}"):
                delete_patient(p['id']); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

elif page == 'Score Calculator':
    st.subheader('حاسبة السكورات Score Calculator')
    if not patients: st.warning('أضف مريض أولاً.')
    else:
        selected=st.selectbox('Select Patient', list(patient_options.keys()))
        pid=patient_options[selected]; p=get_patient(pid)
        st.markdown(f"<div class='card'><b>{p['code']} — {p['name']}</b><br>Diagnosis: {p['diagnosis']}<br>Operation: {p['operation']}</div>", unsafe_allow_html=True)
        cat=st.selectbox('Category', list(CATEGORIES.keys()))
        score=st.selectbox('Score', CATEGORIES[cat])
        result, interp, risk = run_score(score)
        st.metric(score, result); st.write(interp); risk_badge(risk)
        if st.button('Save Result'):
            add_result(pid, score, result, interp, risk); st.success('تم حفظ النتيجة')

elif page == 'Operation Schedule':
    st.subheader('جدولة العمليات Operation Schedule')
    if not patients: st.warning('أضف مريض أولاً.')
    else:
        with st.form('schedule_op'):
            selected=st.selectbox('Patient', list(patient_options.keys()))
            pid=patient_options[selected]
            col1,col2=st.columns(2)
            with col1:
                title=st.text_input('Operation Title', value='Laparoscopic cholecystectomy')
                op_type=st.selectbox('Operation Type',['Elective','Emergency','Day-case','Major','Minor'])
                op_date=st.date_input('Date', value=date.today())
                op_time=st.time_input('Time', value=time(9,0))
            with col2:
                surgeon=st.text_input('Surgeon / Team'); hospital=st.text_input('Hospital / Theater'); status=st.selectbox('Status',['Planned','Confirmed','Done','Cancelled','Postponed']); notes=st.text_area('Notes')
            if st.form_submit_button('Save Operation'):
                add_operation(pid,title,op_type,str(op_date),str(op_time),surgeon,hospital,status,notes); st.success('تمت جدولة العملية')
        st.markdown('### Scheduled Operations')
        ops=get_operations()
        if ops: st.dataframe(pd.DataFrame(ops), use_container_width=True)

elif page == 'Calendar View':
    st.subheader('Calendar View / استعراض المرضى حسب تاريخ العملية')
    ops=get_operations()
    if not ops: st.info('لا توجد عمليات مجدولة.')
    else:
        df=pd.DataFrame(ops)
        selected_date=st.date_input('Choose date', value=date.today())
        day=df[df['operation_date']==str(selected_date)]
        st.markdown(f'### Operations on {selected_date}')
        if day.empty: st.info('لا توجد عمليات في هذا اليوم.')
        else:
            for _,r in day.iterrows():
                st.markdown(f"<div class='card'><b>{r['operation_time']} — {r['operation_title']}</b><br>Patient: {r['code']} — {r['name']} | Age: {r['age']} | Sex: {r['sex']}<br>Diagnosis: {r['diagnosis']}<br>Surgeon: {r['surgeon']} | Hospital: {r['hospital']}<br>Status: {r['status']}</div>", unsafe_allow_html=True)
        st.markdown('### Full Calendar Table')
        st.dataframe(df, use_container_width=True)
        st.download_button('Download Operations CSV', df.to_csv(index=False).encode('utf-8'), 'operations_calendar.csv', 'text/csv')

elif page == 'Attachments':
    st.subheader('المرفقات Attachments')
    if not patients: st.warning('أضف مريض أولاً.')
    else:
        selected=st.selectbox('Patient', list(patient_options.keys()))
        pid=patient_options[selected]
        files=st.file_uploader('Upload labs / CT / photos / PDF', type=['png','jpg','jpeg','pdf','txt','csv'], accept_multiple_files=True)
        if files:
            for f in files: add_attachment(pid, f.name, f.type, f.getvalue())
            st.success('تم رفع المرفقات')
        for a in get_attachments(pid):
            st.markdown('<div class="card">', unsafe_allow_html=True)
            c1,c2,c3=st.columns([4,2,1])
            c1.write(f"**{a['filename']}**"); c1.caption(a['filetype'])
            c2.download_button('Download', a['data'], a['filename'], a['filetype'], key=f"down{a['id']}")
            if c3.button('Delete', key=f"dela{a['id']}"):
                delete_attachment(a['id']); st.rerun()
            if str(a['filetype']).startswith('image'): st.image(a['data'], width=320)
            st.markdown('</div>', unsafe_allow_html=True)

elif page == 'Results / Backup':
    st.subheader('النتائج والنسخ الاحتياطي Results / Backup')
    res=get_results(); ops=get_operations(); pts=get_patients()
    if res: st.dataframe(pd.DataFrame(res), use_container_width=True)
    else: st.info('لا توجد نتائج محفوظة.')
    c1,c2,c3=st.columns(3)
    c1.download_button('Patients CSV', pd.DataFrame(pts).to_csv(index=False).encode('utf-8'), 'patients.csv', 'text/csv')
    c2.download_button('Results CSV', pd.DataFrame(res).to_csv(index=False).encode('utf-8'), 'results.csv', 'text/csv')
    c3.download_button('Operations CSV', pd.DataFrame(ops).to_csv(index=False).encode('utf-8'), 'operations.csv', 'text/csv')
