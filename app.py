import streamlit as st
import pandas as pd
import calendar
from datetime import date
from database import *
from styles import inject_styles
from data_library import GENERAL_SURGERY_OPERATIONS, SCORE_CATEGORIES, SCORE_DESCRIPTIONS, suggested_scores_for_operation
from scores_library import render_score, risk_badge

st.set_page_config(page_title='SurgiScore Hub', page_icon='🏥', layout='wide')
init_db(); inject_styles(st)

st.markdown('''<div class="hero"><div class="title">🏥 SurgiScore Hub</div><div class="subtitle">منصة Board-ready لجدولة العمليات وحساب Surgical Scores — مناسبة للموبايل والآيباد واللابتوب</div><span class="pill">Calendar • Operation Archive • Surgical Scores • Attachments</span></div>''', unsafe_allow_html=True)

st.sidebar.title('SurgiScore Hub')
page=st.sidebar.radio('Navigation',['الواجهة الرئيسية / Monthly Calendar','إضافة موعد عملية','تفاصيل عملية / Archive','Score Library','المرضى','النتائج والنسخ الاحتياطي'])

patients=get_patients(); ops_all=get_operations()

STATUS_CLASSES={'Planned':'status-planned','Done':'status-done','Cancelled':'status-cancelled','Delayed':'status-delayed'}

def patient_select_or_create(prefix=''):
    mode=st.radio('Patient mode',['اختيار مريض موجود','إضافة مريض جديد'], horizontal=True, key=prefix+'pmode')
    if mode=='اختيار مريض موجود' and patients:
        label_map={f"{p['code']} — {p['name']} ({p['age']}y)":p['id'] for p in patients}
        chosen=st.selectbox('Patient', list(label_map.keys()), key=prefix+'existing')
        return label_map[chosen]
    st.markdown('#### معلومات المريض الأساسية')
    c1,c2=st.columns(2)
    with c1:
        code=st.text_input('Patient Code / ID', key=prefix+'code')
        name=st.text_input('Patient Name', key=prefix+'name')
        age=st.number_input('Age',0,120,30,key=prefix+'age')
        sex=st.selectbox('Sex',['Male','Female'],key=prefix+'sex')
    with c2:
        phone=st.text_input('Phone optional', key=prefix+'phone')
        diagnosis=st.text_input('Diagnosis', key=prefix+'dx')
        notes=st.text_area('Patient Notes', key=prefix+'notes')
    if not code:
        code=f'AUTO-{date.today().strftime("%Y%m%d")}-{len(patients)+1}'
    return add_patient(code,name,age,sex,phone,diagnosis,notes)

def save_uploaded_files(pid, oid, key):
    files=st.file_uploader('رفع صور التحاليل أو الأشعة أو PDF / Upload labs, imaging, reports', type=['png','jpg','jpeg','pdf','txt','csv'], accept_multiple_files=True, key=key)
    if files:
        for f in files:
            add_attachment(pid, oid, f.name, f.type, f.getvalue())
        st.success('تم حفظ المرفقات')

if page=='الواجهة الرئيسية / Monthly Calendar':
    today=date.today()
    colA,colB,colC=st.columns([1,1,2])
    month=colA.selectbox('Month', list(range(1,13)), index=today.month-1)
    year=colB.number_input('Year',2020,2035,today.year)
    month_key=f'{int(year):04d}-{int(month):02d}'
    ops=get_operations(month_key)
    st.markdown('### التقويم الشهري للعمليات')
    cal=calendar.Calendar(firstweekday=5)  # Saturday start
    weeks=cal.monthdatescalendar(int(year), int(month))
    by_day={}
    for o in ops: by_day.setdefault(o['op_date'],[]).append(o)
    headers=['Sat','Sun','Mon','Tue','Wed','Thu','Fri']
    cols=st.columns(7)
    for i,h in enumerate(headers): cols[i].markdown(f'**{h}**')
    for wk in weeks:
        cols=st.columns(7)
        for i,d in enumerate(wk):
            day_ops=by_day.get(d.isoformat(),[])
            muted=' day-muted' if d.month!=month else ''
            with cols[i]:
                st.markdown(f"<div class='day-card{muted}'><div class='day-number'>{d.day}</div>", unsafe_allow_html=True)
                if day_ops:
                    counts={s:sum(1 for x in day_ops if x['status']==s) for s in ['Planned','Done','Delayed','Cancelled']}
                    for s,n in counts.items():
                        if n: st.markdown(f"<span class='status-badge {STATUS_CLASSES[s]}'>{s}: {n}</span>", unsafe_allow_html=True)
                    for x in day_ops[:3]: st.caption(f"{x['start_time']} • {x['operation_type'][:24]}")
                else: st.caption('No cases')
                st.markdown('</div>', unsafe_allow_html=True)
    st.divider()
    st.markdown('### إضافة موعد جديد مباشرة')
    with st.expander('➕ New operation appointment', expanded=False):
        pid=patient_select_or_create('quick_')
        c1,c2,c3=st.columns(3)
        op_date=c1.date_input('Operation Date', today, key='quickdate')
        start_time=c2.time_input('Start Time', key='quicktime')
        status=c3.selectbox('Status',['Planned','Done','Delayed','Cancelled'], key='quickstatus')
        op_type=st.selectbox('Operation Type', GENERAL_SURGERY_OPERATIONS, key='quickop')
        c4,c5,c6=st.columns(3)
        surgeon=c4.text_input('Responsible Surgeon', key='quicksurgeon')
        assistant=c5.text_input('Assistant / Resident', key='quickassistant')
        theatre=c6.text_input('Theatre / OR', key='quickor')
        anesthesia=st.selectbox('Anesthesia',['General anesthesia','Spinal anesthesia','Local anesthesia','Sedation','TBD'], key='quickan')
        priority=st.selectbox('Priority',['Elective','Urgent','Emergency'], key='quickpriority')
        indication=st.text_area('Indication', key='quickind')
        details=st.text_area('Operation details / plan', key='quickdetails')
        suggested=suggested_scores_for_operation(op_type)
        selected_scores=st.multiselect('السكورات المقترحة للمريض / Suggested Scores', sum(SCORE_CATEGORIES.values(),[]), default=suggested, key='quickscores')
        if st.button('حفظ الإجراء وأرشفته'):
            oid=add_operation(pid, op_date.isoformat(), start_time.strftime('%H:%M'), op_type, surgeon, assistant, anesthesia, priority, status, theatre, indication, details)
            st.session_state['last_operation_id']=oid
            st.success('تم حفظ موعد العملية. انتقل إلى تفاصيل العملية لحساب السكورات ورفع الملفات.')

elif page=='إضافة موعد عملية':
    st.markdown('### إضافة موعد عملية جديد')
    with st.form('new_operation_form'):
        pid=patient_select_or_create('new_')
        st.markdown('#### تفاصيل العملية')
        c1,c2,c3=st.columns(3)
        op_date=c1.date_input('Operation Date', date.today())
        start_time=c2.time_input('Start Time')
        status=c3.selectbox('Status',['Planned','Done','Delayed','Cancelled'])
        op_type=st.selectbox('Operation Type / نوع العملية', GENERAL_SURGERY_OPERATIONS)
        c4,c5,c6=st.columns(3)
        surgeon=c4.text_input('Responsible Surgeon')
        assistant=c5.text_input('Assistant / Resident')
        theatre=c6.text_input('Theatre / OR')
        anesthesia=st.selectbox('Anesthesia',['General anesthesia','Spinal anesthesia','Local anesthesia','Sedation','TBD'])
        priority=st.selectbox('Priority',['Elective','Urgent','Emergency'])
        indication=st.text_area('Indication')
        details=st.text_area('Other operation details')
        suggested=suggested_scores_for_operation(op_type)
        selected_scores=st.multiselect('Suggested scores to calculate after saving', sum(SCORE_CATEGORIES.values(),[]), default=suggested)
        submitted=st.form_submit_button('Save operation')
    if submitted:
        oid=add_operation(pid, op_date.isoformat(), start_time.strftime('%H:%M'), op_type, surgeon, assistant, anesthesia, priority, status, theatre, indication, details)
        st.session_state['last_operation_id']=oid
        st.success('Saved. افتح صفحة تفاصيل عملية / Archive لإضافة السكورات والمرفقات.')

elif page=='تفاصيل عملية / Archive':
    st.markdown('### أرشيف العمليات والتفاصيل')
    ops=get_operations()
    if not ops: st.info('لا توجد عمليات محفوظة بعد.')
    else:
        options={f"#{o['id']} | {o['op_date']} {o['start_time']} | {o['code']} — {o['name']} | {o['operation_type']}":o['id'] for o in ops}
        default_id=st.session_state.get('last_operation_id')
        keys=list(options.keys()); idx=0
        if default_id:
            for i,k in enumerate(keys):
                if options[k]==default_id: idx=i
        selected=st.selectbox('Select operation', keys, index=idx)
        oid=options[selected]; o=get_operation(oid)
        st.markdown('<div class="apple-card">', unsafe_allow_html=True)
        c1,c2,c3=st.columns(3)
        c1.write(f"**Patient:** {o['code']} — {o['name']}"); c1.caption(f"{o['age']}y | {o['sex']} | {o['diagnosis']}")
        c2.write(f"**Operation:** {o['operation_type']}"); c2.caption(f"{o['op_date']} at {o['start_time']} | {o['status']}")
        c3.write(f"**Surgeon:** {o['surgeon']}"); c3.caption(f"{o['priority']} | {o['anesthesia']} | {o['theatre']}")
        st.write(f"**Indication:** {o['indication']}"); st.write(f"**Details:** {o['details']}")
        st.markdown('</div>', unsafe_allow_html=True)
        tabs=st.tabs(['Scores', 'Attachments', 'Saved results'])
        with tabs[0]:
            suggested=suggested_scores_for_operation(o['operation_type'])
            score=st.selectbox('Choose score', sum(SCORE_CATEGORIES.values(),[]), index=0)
            if score in suggested: st.success('هذا السكور مقترح لهذه العملية')
            st.info(SCORE_DESCRIPTIONS.get(score,''))
            result, interpretation, risk=render_score(score)
            st.metric(score, result); st.write(interpretation); risk_badge(risk)
            if st.button('Save score result'):
                add_result(o['patient_id'], oid, score, result, interpretation, risk); st.success('Score archived')
        with tabs[1]:
            save_uploaded_files(o['patient_id'], oid, 'archive_upload')
            for a in get_attachments(oid):
                st.markdown('<div class="apple-card">', unsafe_allow_html=True)
                cc1,cc2,cc3=st.columns([4,2,1])
                cc1.write(f"**{a['filename']}**"); cc1.caption(f"{a['filetype']} | {a['created_at']}")
                cc2.download_button('Download', a['data'], a['filename'], a['filetype'], key=f"dl{a['id']}")
                if cc3.button('Delete', key=f"ad{a['id']}"):
                    delete_attachment(a['id']); st.rerun()
                if str(a['filetype']).startswith('image'): st.image(a['data'], width=360)
                st.markdown('</div>', unsafe_allow_html=True)
        with tabs[2]:
            rows=get_results(oid)
            if rows: st.dataframe(pd.DataFrame(rows), use_container_width=True)
            else: st.info('No score results yet.')

elif page=='Score Library':
    st.markdown('### Score Library + شرح مختصر')
    cat=st.selectbox('Category', list(SCORE_CATEGORIES.keys()))
    for s in SCORE_CATEGORIES[cat]:
        st.markdown('<div class="apple-card">', unsafe_allow_html=True)
        st.write(f"**{s}**")
        st.caption(SCORE_DESCRIPTIONS.get(s,''))
        st.markdown('</div>', unsafe_allow_html=True)

elif page=='المرضى':
    st.markdown('### Patient Registry')
    if not patients: st.info('No patients yet.')
    else:
        q=st.text_input('Search patient')
        data=patients
        if q: data=[p for p in patients if q.lower() in str(p['code']).lower() or q.lower() in str(p['name']).lower()]
        for p in data:
            st.markdown('<div class="apple-card">', unsafe_allow_html=True)
            c1,c2,c3=st.columns([3,3,1])
            c1.write(f"**{p['code']} — {p['name']}**"); c1.caption(f"{p['age']}y | {p['sex']} | {p['phone'] or ''}")
            c2.write(f"**Diagnosis:** {p['diagnosis']}"); c2.caption(p['notes'] or '')
            if c3.button('Delete', key=f"dp{p['id']}"):
                delete_patient(p['id']); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

elif page=='النتائج والنسخ الاحتياطي':
    st.markdown('### Results / Backup')
    res=get_results()
    if res:
        df=pd.DataFrame(res); st.dataframe(df, use_container_width=True)
        st.download_button('Download results CSV', df.to_csv(index=False).encode('utf-8-sig'), 'surgiscore_results.csv', 'text/csv')
    ops=get_operations()
    if ops:
        odf=pd.DataFrame(ops); st.download_button('Download operations CSV', odf.to_csv(index=False).encode('utf-8-sig'), 'operations.csv', 'text/csv')
