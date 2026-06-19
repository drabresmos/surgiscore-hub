import streamlit as st
import pandas as pd
import calendar, json
from datetime import date, datetime
from database import *
from styles import inject_css
from scores_library import COMMON_OPERATIONS, SCORE_INFO, ALL_SCORES, recommended_scores, render_score

init_db()
st.set_page_config(page_title='SurgiScore Hub', page_icon='🏥', layout='wide')
inject_css(st)

st.markdown('''<div class="hero"><div class="title">🏥 SurgiScore Hub</div><div class="subtitle">منصة جدولة العمليات وحساب Surgical Scores لطلبة البورد والجراحين — Mobile & iPad ready</div><span class="pill">Arabic UI • English medical terms • Mandatory/Skip workflow</span></div>''', unsafe_allow_html=True)

page = st.sidebar.radio('Navigation', ['Monthly Calendar','Add Operation','Operation Archive','Mandatory Scores','Attachments','Results / Backup'])
ops = get_operations()

def parse_required(op):
    try: return json.loads(op.get('required_scores') or '[]')
    except Exception: return []

def score_completion(op_id, required):
    results = get_score_results(op_id)
    done = {r['score_name']: r for r in results}
    completed = [s for s in required if s in done]
    missing = [s for s in required if s not in done]
    return completed, missing, done

def status_counts(day_ops):
    planned=sum(1 for o in day_ops if o['status']=='Planned')
    done=sum(1 for o in day_ops if o['status']=='Done')
    cancelled=sum(1 for o in day_ops if o['status']=='Cancelled')
    return planned, done, cancelled

if page == 'Monthly Calendar':
    st.subheader('التقويم الشهري Monthly Operation Calendar')
    c1,c2,c3=st.columns([1,1,2])
    today=date.today()
    month=c1.selectbox('Month', list(range(1,13)), index=today.month-1)
    year=c2.number_input('Year', 2020, 2035, today.year)
    if c3.button('➕ Add operation for today'):
        st.session_state.nav_to_add=True
        st.switch_page('app.py') if False else None
    cal=calendar.monthcalendar(year, month)
    weekdays=['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    cols=st.columns(7)
    for i,w in enumerate(weekdays): cols[i].markdown(f'**{w}**')
    for week in cal:
        cols=st.columns(7)
        for i,day in enumerate(week):
            with cols[i]:
                if day==0:
                    st.write('')
                else:
                    d=f'{year:04d}-{month:02d}-{day:02d}'
                    day_ops=[o for o in ops if o['operation_date']==d]
                    p, dn, ca = status_counts(day_ops)
                    st.markdown('<div class="calendar-day">', unsafe_allow_html=True)
                    st.markdown(f'<div class="day-number">{day}</div>', unsafe_allow_html=True)
                    st.caption(f'Total operations: {len(day_ops)}')
                    if day_ops:
                        st.markdown(f'<span class="status-planned">Planned {p}</span> · <span class="status-done">Done {dn}</span> · <span class="status-cancelled">Cancelled {ca}</span>', unsafe_allow_html=True)
                        for o in day_ops[:3]:
                            st.write(f"{o['start_time']} • {o['patient_name']} • {o['operation_type'][:22]}")
                    if st.button('Add', key=f'add_{d}'):
                        st.session_state.prefill_date=d
                        st.session_state.page_hint='Add Operation'
                        st.info('اذهب إلى Add Operation، التاريخ تم اختياره تلقائياً.')
                    st.markdown('</div>', unsafe_allow_html=True)

elif page == 'Add Operation':
    st.subheader('إضافة موعد عملية جديد Add New Operation')
    with st.form('op_form'):
        st.markdown('### 1) Patient basic information')
        a,b,c,d=st.columns(4)
        patient_code=a.text_input('Patient code / MRN')
        patient_name=b.text_input('Patient name')
        age=c.number_input('Age',0,120,30)
        sex=d.selectbox('Sex',['Male','Female'])
        diagnosis=st.text_input('Diagnosis')
        st.markdown('### 2) Operation details')
        operation_type=st.selectbox('Operation type', COMMON_OPERATIONS)
        odate=st.date_input('Operation date', value=date.fromisoformat(st.session_state.get('prefill_date', str(date.today()))))
        t1,t2,t3=st.columns(3)
        start_time=t1.time_input('Start time', value=datetime.strptime('09:00','%H:%M').time())
        surgeon=t2.text_input('Responsible surgeon')
        assistant=t3.text_input('Assistant / resident')
        anesthesia=st.selectbox('Anesthesia',['General anesthesia','Spinal anesthesia','Local anesthesia','Sedation','TBD'])
        status=st.selectbox('Status',['Planned','Done','Cancelled'])
        details=st.text_area('Operation details / notes')
        rec=recommended_scores(operation_type)
        st.markdown('### 3) Recommended mandatory scores')
        st.info('هذه السكورات ستكون إلزامية: يجب حساب كل score أو اختيار Skip with reason قبل الأرشفة النهائية.')
        required_scores=st.multiselect('Required scores', ALL_SCORES, default=rec)
        submitted=st.form_submit_button('Save operation and open score checklist')
    if submitted:
        if not patient_name or not patient_code or not surgeon:
            st.error('Patient code, patient name, and responsible surgeon are required.')
        elif not required_scores:
            st.error('At least one required score must be selected.')
        else:
            oid=add_operation({'patient_code':patient_code,'patient_name':patient_name,'age':age,'sex':sex,'diagnosis':diagnosis,'operation_type':operation_type,'operation_date':str(odate),'start_time':start_time.strftime('%H:%M'),'surgeon':surgeon,'assistant':assistant,'anesthesia':anesthesia,'status':status,'details':details,'required_scores':required_scores})
            st.success(f'Operation archived as draft. Operation ID: {oid}. أكمل السكورات من صفحة Mandatory Scores.')

elif page == 'Operation Archive':
    st.subheader('أرشيف العمليات Operation Archive')
    if not ops: st.info('No operations yet.')
    else:
        q=st.text_input('Search by patient, surgeon, operation')
        filtered=ops
        if q:
            filtered=[o for o in ops if q.lower() in (o['patient_name'] or '').lower() or q.lower() in (o['surgeon'] or '').lower() or q.lower() in (o['operation_type'] or '').lower()]
        for o in filtered:
            req=parse_required(o); comp, missing, done=score_completion(o['id'], req)
            st.markdown('<div class="card">', unsafe_allow_html=True)
            c1,c2,c3=st.columns([4,4,2])
            c1.write(f"**#{o['id']} — {o['patient_name']} ({o['patient_code']})**")
            c1.caption(f"{o['age']} years | {o['sex']} | {o['diagnosis']}")
            c2.write(f"**{o['operation_type']}**")
            c2.caption(f"{o['operation_date']} at {o['start_time']} | Surgeon: {o['surgeon']}")
            c3.metric('Scores', f'{len(comp)}/{len(req)}')
            if missing: st.warning('Missing/Not skipped: ' + ', '.join(missing))
            else: st.success('All required scores completed or skipped. Ready for final archive.')
            cc1,cc2=st.columns(2)
            new_status=cc1.selectbox('Status',['Planned','Done','Cancelled'], index=['Planned','Done','Cancelled'].index(o['status']), key=f"status_{o['id']}")
            if cc1.button('Update status', key=f"up_{o['id']}"):
                update_operation_status(o['id'], new_status, 'Complete' if not missing else 'Pending'); st.rerun()
            if cc2.button('Delete operation', key=f"del_{o['id']}"):
                delete_operation(o['id']); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

elif page == 'Mandatory Scores':
    st.subheader('Mandatory Scores Checklist')
    if not ops: st.info('Add an operation first.')
    else:
        labels=[f"#{o['id']} | {o['operation_date']} {o['start_time']} | {o['patient_name']} | {o['operation_type']}" for o in ops]
        selected=st.selectbox('Select operation', labels)
        op_id=int(selected.split('|')[0].replace('#','').strip())
        op=get_operation(op_id)
        req=parse_required(op)
        comp, missing, done=score_completion(op_id, req)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write(f"**Patient:** {op['patient_name']} | **Operation:** {op['operation_type']} | **Surgeon:** {op['surgeon']}")
        st.metric('Completion', f'{len(comp)}/{len(req)}')
        st.markdown('</div>', unsafe_allow_html=True)
        for s in req:
            with st.expander(('✅ ' if s in done else '⬜ ') + s, expanded=(s not in done)):
                st.caption(SCORE_INFO.get(s,''))
                mode=st.radio('Action', ['Calculate score','Skip with reason'], key=f'mode_{op_id}_{s}', horizontal=True)
                if mode=='Calculate score':
                    result, interp, risk=render_score(s, key_prefix=f'op{op_id}')
                    st.write(f'**Result:** {result}')
                    st.write(interp)
                    if st.button('Save this score', key=f'save_{op_id}_{s}'):
                        add_score_result(op_id, s, result, interp, risk, 0, '')
                        comp2, missing2, _ = score_completion(op_id, req)
                        update_operation_status(op_id, op['status'], 'Complete' if len(missing2)==0 else 'Pending')
                        st.rerun()
                else:
                    reason=st.text_area('Skip reason is mandatory', key=f'reason_{op_id}_{s}')
                    if st.button('Save skip decision', key=f'skip_{op_id}_{s}'):
                        if len(reason.strip())<5:
                            st.error('اكتب سبب واضح للتجاوز.')
                        else:
                            add_score_result(op_id, s, 'Skipped', 'Skipped with documented reason.', 'Medium', 1, reason.strip())
                            comp2, missing2, _ = score_completion(op_id, req)
                            update_operation_status(op_id, op['status'], 'Complete' if len(missing2)==0 else 'Pending')
                            st.rerun()
        comp, missing, done=score_completion(op_id, req)
        if missing:
            st.error('لا يمكن إنهاء الأرشفة النهائية قبل إكمال أو تجاوز السكورات التالية: ' + ', '.join(missing))
        else:
            st.success('تم إكمال كل السكورات المطلوبة أو توثيق سبب تجاوزها. يمكن اعتماد العملية في الأرشيف.')

elif page == 'Attachments':
    st.subheader('رفع صور التحاليل والأشعة Attachments')
    if not ops: st.info('Add an operation first.')
    else:
        labels=[f"#{o['id']} | {o['patient_name']} | {o['operation_type']}" for o in ops]
        selected=st.selectbox('Operation', labels)
        op_id=int(selected.split('|')[0].replace('#','').strip())
        files=st.file_uploader('Upload labs, X-ray, CT, MRI, PDF reports', type=['png','jpg','jpeg','pdf','txt','csv'], accept_multiple_files=True)
        if files:
            for f in files: add_attachment(op_id, f.name, f.type, f.getvalue())
            st.success('Files uploaded.')
        for a in get_attachments(op_id):
            st.markdown('<div class="card">', unsafe_allow_html=True)
            c1,c2=st.columns([4,2])
            c1.write(f"**{a['filename']}**"); c1.caption(a['filetype'])
            c2.download_button('Download', a['data'], a['filename'], a['filetype'], key=f"att_{a['id']}")
            if (a['filetype'] or '').startswith('image'):
                st.image(a['data'], width=360)
            st.markdown('</div>', unsafe_allow_html=True)

elif page == 'Results / Backup':
    st.subheader('Results / Backup')
    all_rows=[]
    for o in ops:
        for r in get_score_results(o['id']):
            row=dict(o); row.update({'score_name':r['score_name'],'score_result':r['result'],'interpretation':r['interpretation'],'risk':r['risk'],'skipped':r['skipped'],'skip_reason':r['skip_reason']})
            all_rows.append(row)
    if all_rows:
        df=pd.DataFrame(all_rows)
        st.dataframe(df, use_container_width=True)
        st.download_button('Download full archive CSV', df.to_csv(index=False).encode('utf-8'), 'surgiscore_archive.csv','text/csv')
    else:
        st.info('No score results yet.')
