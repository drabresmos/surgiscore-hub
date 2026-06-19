import streamlit as st
import pandas as pd
import calendar
from datetime import date, datetime
from pathlib import Path

from styles import apply_styles, hero
from data import COMMON_OPERATIONS, STATUS_OPTIONS, URGENCY_OPTIONS, WOUND_OPTIONS, ASA_OPTIONS, recommended_scores, SCORE_DESCRIPTIONS
from database import *
from scores import render_score

st.set_page_config(page_title='SurgiScore Ward', page_icon='🏥', layout='wide')
apply_styles(); init_db(); hero()

st.sidebar.title('SurgiScore Ward')
page = st.sidebar.radio('Navigation', ['Monthly Calendar', 'Add Operation', 'Patient Journey', 'Ward Rounds', 'Score Library', 'Attachments', 'Archive / Backup'])

ops = get_operations()

def status_class(s):
    return {'Scheduled':'status-scheduled','Pre-op':'status-preop','Intra-op':'status-intraop','Post-op':'status-postop'}.get(s,'status-scheduled')

def op_label(op):
    return f"#{op['id']} • {op['patient_name']} • {op['operation_type']} • {op['operation_date']} {op['start_time']}"

# ------------------ Calendar ------------------
if page == 'Monthly Calendar':
    st.markdown('### التقويم الشهري للعمليات Monthly Operation Calendar')
    today = date.today()
    c1,c2,c3 = st.columns([1,1,2])
    month = c1.selectbox('Month', list(range(1,13)), index=today.month-1)
    year = c2.number_input('Year', 2020, 2100, today.year)
    c3.info('داخل كل يوم يظهر عدد العمليات حسب الحالة. يمكن إضافة موعد جديد من الزر أدناه.')
    if st.button('➕ إضافة موعد عملية جديد Add operation'):
        st.session_state['go_add']=True
        st.switch_page('app.py') if False else None
    month_ops = get_ops_by_month(int(year), int(month))
    by_day = {}
    for o in month_ops:
        by_day.setdefault(o['operation_date'], []).append(o)
    cal = calendar.monthcalendar(int(year), int(month))
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write(f'**{calendar.month_name[int(month)]} {int(year)}**')
    weekdays = st.columns(7)
    for i,w in enumerate(['Mon','Tue','Wed','Thu','Fri','Sat','Sun']): weekdays[i].markdown(f'**{w}**')
    for week in cal:
        cols = st.columns(7)
        for i,d in enumerate(week):
            with cols[i]:
                if d==0:
                    st.write('')
                else:
                    ds=f'{int(year):04d}-{int(month):02d}-{d:02d}'
                    dayops=by_day.get(ds, [])
                    st.markdown('<div class="day-card">', unsafe_allow_html=True)
                    st.markdown(f'**{d}**')
                    if dayops:
                        counts={}
                        for o in dayops: counts[o['status']]=counts.get(o['status'],0)+1
                        for k,v in counts.items(): st.markdown(f"<span class='{status_class(k)}'>{k}: {v}</span>", unsafe_allow_html=True)
                        with st.expander('Cases'):
                            for o in dayops: st.caption(f"{o['start_time']} • {o['patient_name']} • {o['operation_type']}")
                    else:
                        st.caption('No cases')
                    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    with st.expander('➕ إضافة موعد مباشر من التقويم'):
        default_day = st.date_input('Operation date', value=today)
        st.info('بعد الحفظ، افتح Patient Journey لإكمال Pre-op / Intra-op / Post-op.')
        with st.form('quick_add'):
            q1,q2=st.columns(2)
            patient_code=q1.text_input('Patient code / رقم المريض')
            patient_name=q1.text_input('Patient name / اسم المريض')
            age=q1.number_input('Age',0,120,30); sex=q1.selectbox('Sex',['Male','Female'])
            phone=q1.text_input('Phone')
            diagnosis=q2.text_input('Diagnosis')
            op_type=q2.selectbox('Operation type', COMMON_OPERATIONS)
            start_time=q2.time_input('Start time')
            surgeon=q2.text_input('Responsible surgeon')
            urgency=q2.selectbox('Urgency', URGENCY_OPTIONS)
            if st.form_submit_button('Save operation'):
                opid=add_operation({'patient_code':patient_code,'patient_name':patient_name,'age':age,'sex':sex,'phone':phone,'diagnosis':diagnosis,'operation_type':op_type,'operation_date':str(default_day),'start_time':start_time.strftime('%H:%M'),'surgeon':surgeon,'assistant':'','anesthesia':'','urgency':urgency,'wound_class':'','status':'Scheduled','bed':'','notes':''})
                st.success(f'Operation archived. ID: {opid}')
                st.rerun()

# ------------------ Add Operation ------------------
elif page == 'Add Operation':
    st.markdown('### إضافة موعد/حالة عملية New Operation')
    with st.form('add_full_operation'):
        st.markdown('#### Patient basics')
        a,b,c=st.columns(3)
        patient_code=a.text_input('Patient code')
        patient_name=a.text_input('Patient name')
        age=a.number_input('Age',0,120,30); sex=a.selectbox('Sex',['Male','Female'])
        phone=b.text_input('Phone'); bed=b.text_input('Ward/Bed')
        diagnosis=b.text_input('Diagnosis')
        operation_type=c.selectbox('Operation type', COMMON_OPERATIONS)
        operation_date=c.date_input('Operation date')
        start_time=c.time_input('Start time')
        st.markdown('#### Operation details')
        d,e,f=st.columns(3)
        surgeon=d.text_input('Responsible surgeon')
        assistant=d.text_input('Assistant / team')
        anesthesia=e.selectbox('Anesthesia',["GA","Spinal","Local","Sedation","Other"])
        urgency=e.selectbox('Urgency', URGENCY_OPTIONS)
        wound_class=f.selectbox('Wound class', WOUND_OPTIONS)
        status=f.selectbox('Status', STATUS_OPTIONS)
        notes=st.text_area('Clinical / operation notes')
        st.markdown('#### Suggested scores')
        rec = recommended_scores(operation_type, urgency)
        st.write(' • '.join(rec))
        submit=st.form_submit_button('Save and archive procedure')
        if submit:
            opid=add_operation({'patient_code':patient_code,'patient_name':patient_name,'age':age,'sex':sex,'phone':phone,'diagnosis':diagnosis,'operation_type':operation_type,'operation_date':str(operation_date),'start_time':start_time.strftime('%H:%M'),'surgeon':surgeon,'assistant':assistant,'anesthesia':anesthesia,'urgency':urgency,'wound_class':wound_class,'status':status,'bed':bed,'notes':notes})
            # default checklist tasks
            defaults=['Confirm identity + consent','Check allergies','Review labs/imaging','Antibiotic prophylaxis plan','VTE prophylaxis plan','WHO Sign-in / Time-out / Sign-out','Post-op analgesia + fluids plan']
            for t in defaults: execute('INSERT INTO tasks(operation_id,phase,task,done) VALUES(?,?,?,0)',(opid,'Pre-op',t))
            st.success(f'Saved operation #{opid}. Continue in Patient Journey.')

# ------------------ Patient Journey ------------------
elif page == 'Patient Journey':
    st.markdown('### مسار المريض الجراحي Surgical Patient Journey')
    if not ops: st.info('No operations yet.')
    else:
        op_id = st.selectbox('Select case', [o['id'] for o in ops], format_func=lambda x: op_label(get_operation(x)))
        op=get_operation(op_id)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write(f"**{op['patient_name']}** | {op['age']}y/{op['sex']} | **{op['operation_type']}** | {op['operation_date']} {op['start_time']}")
        st.caption(f"Surgeon: {op['surgeon']} | Status: {op['status']} | Diagnosis: {op['diagnosis']}")
        st.markdown('</div>', unsafe_allow_html=True)
        tabs=st.tabs(['Pre-op', 'Intra-op', 'Post-op', 'Scores', 'Summary'])
        with tabs[0]:
            st.markdown('#### Pre-op checklist / تحضير ما قبل العملية')
            tasks=query('SELECT * FROM tasks WHERE operation_id=? AND phase=?',(op_id,'Pre-op'))
            if not tasks:
                st.info('No checklist tasks.')
            for t in tasks:
                done=st.checkbox(t['task'], value=bool(t['done']), key=f"task{t['id']}")
                execute('UPDATE tasks SET done=? WHERE id=?',(1 if done else 0,t['id']))
            with st.form('add_preop_task'):
                nt=st.text_input('Add task'); 
                if st.form_submit_button('Add') and nt: execute('INSERT INTO tasks(operation_id,phase,task,done) VALUES(?,?,?,0)',(op_id,'Pre-op',nt)); st.rerun()
            new_status=st.selectbox('Update status', STATUS_OPTIONS, index=STATUS_OPTIONS.index(op['status']) if op['status'] in STATUS_OPTIONS else 0)
            if st.button('Save status'): update_operation(op_id, {'status':new_status}); st.success('Updated'); st.rerun()
        with tabs[1]:
            st.markdown('#### Intra-op note / تفاصيل أثناء العملية')
            with st.form('intraop'):
                c1,c2=st.columns(2)
                incision=c1.time_input('Incision time'); closure=c1.time_input('Closure time')
                findings=st.text_area('Findings')
                procedure_done=st.text_area('Procedure done')
                blood_loss=c2.text_input('Blood loss'); specimens=c2.text_input('Specimens'); drains=c2.text_input('Drains')
                complications=st.text_area('Intra-op complications')
                sign_in=st.checkbox('WHO Sign-in done')
                time_out=st.checkbox('WHO Time-out done')
                sign_out=st.checkbox('WHO Sign-out done')
                if st.form_submit_button('Save intra-op note'):
                    add_intraop({'operation_id':op_id,'incision_time':incision.strftime('%H:%M'),'closure_time':closure.strftime('%H:%M'),'findings':findings,'procedure_done':procedure_done,'blood_loss':blood_loss,'specimens':specimens,'drains':drains,'complications':complications,'sign_in_done':int(sign_in),'time_out_done':int(time_out),'sign_out_done':int(sign_out)})
                    update_operation(op_id, {'status':'Post-op'}); st.success('Saved')
            notes=get_intraop(op_id)
            if notes: st.dataframe(pd.DataFrame(notes), use_container_width=True)
        with tabs[2]:
            st.markdown('#### Post-op recovery / متابعة الشفاء')
            st.info('أدخل العلامات الحيوية صباحاً ومساءً مع wound, drain, oral intake, bowel function, mobility, plan.')
            with st.form('round'):
                r1,r2,r3=st.columns(3)
                round_date=r1.date_input('Round date')
                shift=r1.selectbox('Shift',['Morning','Evening','Night','Extra'])
                temp=r1.number_input('Temp °C',30.0,43.0,37.0)
                pulse=r2.number_input('Pulse',20,220,80); bp=r2.text_input('BP','120/80'); rr=r2.number_input('RR',5,60,18); spo2=r2.number_input('SpO2',50,100,98)
                pain=r3.slider('Pain score',0,10,2); urine=r3.text_input('Urine output'); drain=r3.text_input('Drain output')
                wound=st.selectbox('Wound status',['Dry/clean','Mild erythema','Discharge','Dehiscence concern','Infected concern'])
                oral=st.selectbox('Oral intake',['NPO','Sips','Fluids','Soft diet','Normal diet'])
                bowel=st.selectbox('Bowel function',['No flatus/stool','Flatus','Stool','Diarrhea','Ileus concern'])
                mobility=st.selectbox('Mobility',['Bedbound','Sitting','Walking with help','Independent walking'])
                antibiotics=st.text_input('Antibiotics'); anticoag=st.text_input('Anticoagulation/VTE plan'); plan=st.text_area('Plan')
                if st.form_submit_button('Save ward round'):
                    add_round({'operation_id':op_id,'round_date':str(round_date),'shift':shift,'temp':temp,'pulse':pulse,'bp':bp,'rr':rr,'spo2':spo2,'pain_score':pain,'urine_output':urine,'drain_output':drain,'wound_status':wound,'oral_intake':oral,'bowel_function':bowel,'mobility':mobility,'antibiotics':antibiotics,'anticoagulation':anticoag,'plan':plan})
                    st.success('Ward round saved')
            rounds=get_rounds(op_id)
            if rounds: st.dataframe(pd.DataFrame(rounds), use_container_width=True)
        with tabs[3]:
            st.markdown('#### Recommended scores / السكورات المقترحة')
            rec=recommended_scores(op['operation_type'], op['urgency'])
            selected=st.multiselect('Scores to calculate', list(SCORE_DESCRIPTIONS.keys()), default=rec)
            chosen=st.selectbox('Open calculator', selected if selected else rec)
            res,interp,risk=render_score(chosen)
            notes=st.text_area('Score notes')
            if st.button('Save score'):
                add_score(op_id, chosen, res, interp, risk, notes); st.success('Score saved')
            sc=get_scores(op_id)
            if sc: st.dataframe(pd.DataFrame(sc), use_container_width=True)
        with tabs[4]:
            scores=get_scores(op_id); rounds=get_rounds(op_id); intra=get_intraop(op_id)
            summary=f"""Patient: {op['patient_name']} ({op['age']}y/{op['sex']})\nDiagnosis: {op['diagnosis']}\nOperation: {op['operation_type']} on {op['operation_date']} at {op['start_time']}\nSurgeon: {op['surgeon']} | Status: {op['status']}\nScores: {', '.join([s['score_name']+': '+str(s['result']) for s in scores]) if scores else 'No scores yet'}\nLatest plan: {rounds[0]['plan'] if rounds else 'No ward round yet'}"""
            st.text_area('Clinical summary جاهز للنسخ', summary, height=220)

# ------------------ Ward Rounds page ------------------
elif page == 'Ward Rounds':
    st.markdown('### صباحاً ومساءً Morning/Evening Ward Rounds')
    if not ops: st.info('No operations yet.')
    else:
        filt=st.date_input('Show date', value=date.today())
        todays=[o for o in ops if o['operation_date']<=str(filt) and o['status'] in ['Pre-op','Post-op','Intra-op','Scheduled']]
        st.caption(f'{len(todays)} active/scheduled cases')
        for o in todays:
            with st.expander(op_label(o)):
                rounds=get_rounds(o['id'])
                if rounds: st.dataframe(pd.DataFrame(rounds).head(5), use_container_width=True)
                else: st.info('No vitals/rounds yet.')

# ------------------ Score Library ------------------
elif page == 'Score Library':
    st.markdown('### Score Library / مكتبة السكورات')
    for name, desc in SCORE_DESCRIPTIONS.items():
        with st.expander(name): st.write(desc)

# ------------------ Attachments ------------------
elif page == 'Attachments':
    st.markdown('### المرفقات Attachments')
    if not ops: st.info('No operations yet.')
    else:
        op_id=st.selectbox('Case', [o['id'] for o in ops], format_func=lambda x: op_label(get_operation(x)))
        desc=st.text_input('Description')
        files=st.file_uploader('Upload labs, X-ray/CT photos, PDF reports', type=['png','jpg','jpeg','pdf','csv','txt'], accept_multiple_files=True)
        if files and st.button('Save attachments'):
            for f in files: add_attachment(op_id, f, desc)
            st.success('Uploaded')
        at=get_attachments(op_id)
        for a in at:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.write(f"**{a['filename']}** — {a['description']}")
            p=Path(a['stored_path'])
            if p.exists(): st.download_button('Download', p.read_bytes(), file_name=a['filename'])
            if a['filetype'] and a['filetype'].startswith('image') and p.exists(): st.image(p.read_bytes(), width=350)
            st.markdown('</div>', unsafe_allow_html=True)

# ------------------ Archive ------------------
elif page == 'Archive / Backup':
    st.markdown('### Archive / Backup')
    if ops: st.dataframe(pd.DataFrame(ops), use_container_width=True)
    c1,c2=st.columns(2)
    c1.download_button('Download operations CSV', pd.DataFrame(ops).to_csv(index=False).encode('utf-8'), 'operations.csv')
    c2.download_button('Download scores CSV', pd.DataFrame(get_all_scores()).to_csv(index=False).encode('utf-8'), 'scores.csv')
    if ops:
        del_id=st.selectbox('Delete case', [o['id'] for o in ops], format_func=lambda x: op_label(get_operation(x)))
        if st.button('Delete selected case permanently'):
            delete_operation(del_id); st.success('Deleted'); st.rerun()
