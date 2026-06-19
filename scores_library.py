import math
import streamlit as st

def risk_badge(risk):
    css={'Low':'risk-low','Medium':'risk-medium','High':'risk-high'}.get(risk,'')
    st.markdown(f"<span class='{css}'>Risk: {risk}</span>", unsafe_allow_html=True)

def cb(label, pts=1):
    return pts if st.checkbox(f"{label} (+{pts})") else 0

def render_score(name):
    if name == 'ASA':
        asa=st.radio('ASA Physical Status',[ 'ASA I - Normal healthy patient','ASA II - Mild systemic disease','ASA III - Severe systemic disease','ASA IV - Severe systemic disease constant threat to life','ASA V - Moribund patient'])
        res=asa.split(' - ')[0]; risk='Low' if res in ['ASA I','ASA II'] else 'High'; return res, asa, risk
    if name == 'RCRI':
        s=sum(cb(x) for x in ['High-risk surgery','Ischemic heart disease','Heart failure','Cerebrovascular disease','Insulin-dependent diabetes','Creatinine >2 mg/dL'])
        return s, ('Low cardiac risk' if s==0 else 'Intermediate cardiac risk' if s==1 else 'High cardiac risk'), ('Low' if s==0 else 'Medium' if s==1 else 'High')
    if name == 'Caprini VTE':
        items={'Age 41–60':1,'Age 61–74':2,'Age ≥75':3,'Minor surgery':1,'Major surgery >45 min':2,'BMI >25':1,'Swollen legs':1,'Varicose veins':1,'Pregnancy/postpartum':1,'History of malignancy':2,'Bed rest >72h':2,'Central venous access':2,'Prior DVT/PE':3,'Known thrombophilia':3,'Stroke <1 month':5,'Hip/pelvis/leg fracture':5}
        s=sum(cb(k,v) for k,v in items.items()); risk='Low' if s<=2 else 'Medium' if s<=4 else 'High'; return s, f'{risk} VTE risk', risk
    if name == 'Charlson Comorbidity Index':
        items={'MI':1,'CHF':1,'Peripheral vascular disease':1,'Cerebrovascular disease':1,'Dementia':1,'COPD':1,'Connective tissue disease':1,'Peptic ulcer disease':1,'Mild liver disease':1,'Diabetes':1,'Hemiplegia':2,'Moderate/severe renal disease':2,'Diabetes with end organ damage':2,'Any tumor':2,'Leukemia/Lymphoma':2,'Moderate/severe liver disease':3,'Metastatic solid tumor':6,'AIDS':6}
        s=sum(cb(k,v) for k,v in items.items()); risk='Low' if s<=2 else 'Medium' if s<=4 else 'High'; return s, 'Comorbidity burden estimate', risk
    if name == 'Clinical Frailty Scale':
        val=st.slider('CFS 1 very fit — 9 terminally ill',1,9,3); return val, 'Frailty increases postoperative risk' if val>=5 else 'Non-frail / lower frailty burden', 'High' if val>=7 else 'Medium' if val>=5 else 'Low'
    if name == 'STOP-Bang':
        s=sum(cb(x) for x in ['Snoring','Tiredness','Observed apnea','High blood pressure','BMI >35','Age >50','Neck circumference high','Male gender'])
        return s, 'High OSA risk' if s>=5 else 'Intermediate OSA risk' if s>=3 else 'Low OSA risk', 'High' if s>=5 else 'Medium' if s>=3 else 'Low'
    if name == 'Shock Index':
        hr=st.number_input('Heart rate',20,250,90); sbp=st.number_input('Systolic BP',40,250,120); v=round(hr/sbp,2)
        return v, 'Possible shock / physiological stress' if v>0.9 else 'Borderline' if v>=0.7 else 'Normal range', 'High' if v>0.9 else 'Medium' if v>=0.7 else 'Low'
    if name == 'SIRS':
        s=sum(cb(x) for x in ['Temp >38 or <36','HR >90','RR >20 or PaCO2 <32','WBC >12k or <4k or bands >10%'])
        return f'{s}/4', 'SIRS positive' if s>=2 else 'SIRS negative', 'Medium' if s>=2 else 'Low'
    if name == 'qSOFA':
        s=sum(cb(x) for x in ['RR ≥22/min','Altered mentation','SBP ≤100 mmHg'])
        return f'{s}/3','High risk in suspected sepsis' if s>=2 else 'Lower risk','High' if s>=2 else 'Low'
    if name == 'NEWS2':
        s=0
        s += st.selectbox('Respiration score',[0,1,2,3], index=0)
        s += st.selectbox('SpO2 score',[0,1,2,3], index=0)
        s += st.selectbox('Temperature score',[0,1,2,3], index=0)
        s += st.selectbox('Systolic BP score',[0,1,2,3], index=0)
        s += st.selectbox('Pulse score',[0,1,2,3], index=0)
        s += st.selectbox('Consciousness score',[0,3], index=0)
        return s, 'Urgent clinical review' if s>=5 else 'Routine/low escalation' if s<=4 else 'Monitor', 'High' if s>=7 else 'Medium' if s>=5 else 'Low'
    if name == 'SOFA Simplified':
        s=sum(st.selectbox(x,[0,1,2,3,4],index=0) for x in ['Respiratory','Coagulation/platelet','Liver/bilirubin','Cardiovascular','CNS/GCS','Renal/creatinine'])
        return s, 'Organ dysfunction severity estimate', 'High' if s>=8 else 'Medium' if s>=3 else 'Low'
    if name == 'Alvarado':
        s=0
        for label,pts in [('Migration',1),('Anorexia',1),('Nausea/vomiting',1),('RIF tenderness',2),('Rebound',1),('Fever',1),('Leukocytosis',2),('Neutrophilia',1)]: s+=cb(label,pts)
        return f'{s}/10', 'Probable appendicitis' if s>=7 else 'Possible appendicitis' if s>=5 else 'Unlikely appendicitis', 'High' if s>=7 else 'Medium' if s>=5 else 'Low'
    if name == 'AIR Appendicitis':
        vomiting = cb('Vomiting',1)
        rif = st.selectbox('RIF pain/tenderness points',[0,1,2,3], index=1)
        rebound = st.selectbox('Rebound/defense points',[0,1,2,3], index=0)
        temp = cb('Temp ≥38.5',1)
        wbc = st.selectbox('WBC points',[0,1,2],index=0)
        neut = st.selectbox('Neutrophil points',[0,1,2],index=0)
        crp = st.selectbox('CRP points',[0,1,2],index=0)
        s = vomiting + rif + rebound + temp + wbc + neut + crp
        return f'{s}/12','High probability' if s>=9 else 'Intermediate probability' if s>=5 else 'Low probability','High' if s>=9 else 'Medium' if s>=5 else 'Low'
    if name == 'RIPASA':
        s=0.0
        for label,pts in [('Male',1),('Female',0.5),('Age <40',1),('RIF pain',0.5),('Migration',0.5),('Anorexia',1),('Nausea/vomiting',1),('Duration <48h',1),('RIF tenderness',1),('Guarding',2),('Rebound',1),('Rovsing',2),('Fever',1),('Raised WBC',1),('Negative urine',1)]:
            if st.checkbox(f'{label} (+{pts})'): s+=pts
        return s, 'High probability appendicitis' if s>=7.5 else 'Low probability', 'High' if s>=7.5 else 'Low'
    if name == 'Pediatric Appendicitis Score':
        s=sum(cb(k,v) for k,v in {'Anorexia':1,'Nausea/vomiting':1,'Migration':1,'Fever':1,'Cough/percussion/hopping tenderness':2,'RLQ tenderness':2,'Leukocytosis':1,'Neutrophilia':1}.items())
        return f'{s}/10','Likely appendicitis' if s>=7 else 'Equivocal' if s>=4 else 'Low probability','High' if s>=7 else 'Medium' if s>=4 else 'Low'
    if name in ['Tokyo Cholecystitis Grade','Tokyo Cholangitis Grade']:
        organ=st.checkbox('Organ dysfunction'); moderate=sum(cb(x) for x in ['Marked inflammatory response','Symptoms >72h','Local complication/mass','Age ≥75 or bilirubin/albumin issue'])
        if organ: return 'Grade III','Severe with organ dysfunction','High'
        if moderate: return 'Grade II','Moderate disease','Medium'
        return 'Grade I','Mild disease','Low'
    if name == 'ASGE CBD Stone Risk':
        high=st.checkbox('CBD stone on imaging') or st.checkbox('Ascending cholangitis') or st.checkbox('Bilirubin >4 and dilated CBD')
        inter=st.checkbox('Abnormal LFTs / age >55 / CBD dilation')
        return ('High','ERCP usually considered','High') if high else ('Intermediate','MRCP/EUS/IOC usually considered','Medium') if inter else ('Low','Low probability CBD stone','Low')
    if name in ['Nassar Difficulty Grade','Parkland Cholecystitis Grade','Csendes Mirizzi Classification','AAST Organ Injury Grade','Hinchey Diverticulitis','WSES Diverticulitis Classification','Atlanta Pancreatitis Classification','CDC SSI Classification','Clavien-Dindo']:
        grade=st.selectbox('Classification grade / class',[ 'Grade I','Grade II','Grade III','Grade IV','Grade V'])
        risk='High' if grade in ['Grade IV','Grade V'] else 'Medium' if grade=='Grade III' else 'Low'
        return grade, 'Anatomical/severity classification', risk
    if name == 'BISAP':
        s=sum(cb(x) for x in ['BUN >25','Impaired mental status','SIRS','Age >60','Pleural effusion'])
        return f'{s}/5','High risk severe pancreatitis' if s>=3 else 'Lower risk','High' if s>=3 else 'Low'
    if name == 'Ranson Admission':
        s=sum(cb(x) for x in ['Age >55','WBC >16k','Glucose >200','LDH >350','AST >250'])
        return f'{s}/5','Higher severity risk' if s>=3 else 'Lower admission risk','High' if s>=3 else 'Low'
    if name == 'Glasgow-Imrie Pancreatitis':
        s=sum(cb(x) for x in ['PaO2 <60','Age >55','Neutrophils/WBC high','Calcium <2 mmol/L','Renal urea high','Enzymes LDH/AST high','Albumin <32','Sugar >10 mmol/L'])
        return f'{s}/8','Severe pancreatitis likely' if s>=3 else 'Lower severity','High' if s>=3 else 'Low'
    if name == 'Modified CT Severity Index':
        infl=st.selectbox('Inflammation points',[0,2,4]); nec=st.selectbox('Necrosis points',[0,2,4]); comp=st.selectbox('Extrapancreatic complications',[0,2]); s=infl+nec+comp
        return f'{s}/10','Severe CT pancreatitis' if s>=8 else 'Moderate' if s>=4 else 'Mild','High' if s>=8 else 'Medium' if s>=4 else 'Low'
    if name == 'Glasgow-Blatchford':
        s=0; bun=st.number_input('BUN mg/dL',0.0,200.0,20.0); hb=st.number_input('Hb g/dL',0.0,25.0,12.0); sbp=st.number_input('SBP',40,250,120); pulse=st.number_input('Pulse',30,220,80)
        if bun>=28: s+=2
        if hb<12: s+=2
        if sbp<100: s+=2
        if pulse>=100: s+=1
        s+=sum(cb(x,v) for x,v in {'Melena':1,'Syncope':2,'Liver disease':2,'Cardiac failure':2}.items())
        return s,'High risk; admission/endoscopy likely' if s>5 else 'Moderate' if s>0 else 'Very low risk','High' if s>5 else 'Medium' if s>0 else 'Low'
    if name == 'AIMS65':
        s=sum(cb(x) for x in ['Albumin <3.0','INR >1.5','Altered mental status','SBP ≤90','Age >65'])
        return f'{s}/5','Higher UGIB mortality risk' if s>=2 else 'Lower risk','High' if s>=2 else 'Low'
    if name == 'Rockall Pre-Endoscopy':
        s=st.selectbox('Age points',[0,1,2])+st.selectbox('Shock points',[0,1,2])+st.selectbox('Comorbidity points',[0,2,3])
        return s,'Higher risk' if s>=4 else 'Lower/intermediate risk','High' if s>=4 else 'Medium' if s>=2 else 'Low'
    if name == 'Oakland Lower GI Bleeding':
        s=st.number_input('Oakland calculated/manual value',0,40,8)
        return s,'Possible safe discharge if low and clinically stable' if s<=8 else 'Admission/assessment usually required','Low' if s<=8 else 'High'
    if name == 'Mannheim Peritonitis Index':
        items={'Age >50':5,'Female sex':5,'Organ failure':7,'Malignancy':4,'Duration >24h':4,'Origin not colonic':4,'Diffuse peritonitis':6,'Cloudy/purulent exudate':6,'Fecal exudate':12}
        s=sum(cb(k,v) for k,v in items.items())
        return s,'High mortality risk' if s>29 else 'Intermediate' if s>=21 else 'Lower risk','High' if s>29 else 'Medium' if s>=21 else 'Low'
    if name == 'Boey Score':
        s=sum(cb(x) for x in ['Major medical illness','Pre-op shock','Perforation >24h'])
        return f'{s}/3','High risk perforated peptic ulcer' if s>=2 else 'Lower risk','High' if s>=2 else 'Low'
    if name == 'Child-Pugh':
        s=st.selectbox('Ascites',[1,2,3])+st.selectbox('Encephalopathy',[1,2,3])+st.selectbox('Bilirubin',[1,2,3])+st.selectbox('Albumin',[1,2,3])+st.selectbox('INR',[1,2,3])
        cls='A' if s<=6 else 'B' if s<=9 else 'C'
        return f'{s} Class {cls}','Liver functional reserve','High' if cls=='C' else 'Medium' if cls=='B' else 'Low'
    if name == 'MELD-Na':
        bili=max(st.number_input('Bilirubin',0.1,50.0,1.0),1); inr=max(st.number_input('INR',0.8,10.0,1.0),1); cr=max(st.number_input('Creatinine',0.1,15.0,1.0),1); na=st.number_input('Sodium',120,150,137)
        meld=round(3.78*math.log(bili)+11.2*math.log(inr)+9.57*math.log(cr)+6.43); nac=min(max(na,125),137); mn=round(meld+1.32*(137-nac)-0.033*meld*(137-nac))
        return mn,'Liver-related mortality estimate','High' if mn>=20 else 'Medium' if mn>=10 else 'Low'
    if name == 'ALBI Grade':
        alb=st.number_input('Albumin g/L',10.0,60.0,35.0); bili=st.number_input('Bilirubin µmol/L',1.0,800.0,20.0); val=round((math.log10(bili)*0.66)+(alb*-0.085),2)
        grade='1' if val<=-2.60 else '2' if val<=-1.39 else '3'
        return f'{val} Grade {grade}','Albumin-bilirubin liver function grade','High' if grade=='3' else 'Medium' if grade=='2' else 'Low'
    if name == 'LARS Score':
        s=st.number_input('LARS score value',0,42,0); return s,'Major LARS' if s>=30 else 'Minor LARS' if s>=21 else 'No LARS','High' if s>=30 else 'Medium' if s>=21 else 'Low'
    if name == 'Wexner Incontinence Score':
        s=st.number_input('Wexner score value',0,20,0); return s,'Severe incontinence' if s>=10 else 'Mild/moderate' if s>0 else 'No incontinence','High' if s>=10 else 'Medium' if s>0 else 'Low'
    if name == 'GCS':
        e=st.selectbox('Eye',[1,2,3,4],index=3); v=st.selectbox('Verbal',[1,2,3,4,5],index=4); m=st.selectbox('Motor',[1,2,3,4,5,6],index=5); s=e+v+m
        return f'{s}/15','Severe head injury' if s<=8 else 'Moderate' if s<=12 else 'Mild','High' if s<=8 else 'Medium' if s<=12 else 'Low'
    if name == 'RTS':
        g=st.selectbox('GCS coded',[0,1,2,3,4],index=4); sbp=st.selectbox('SBP coded',[0,1,2,3,4],index=4); rr=st.selectbox('RR coded',[0,1,2,3,4],index=4); val=round(0.9368*g+0.7326*sbp+0.2908*rr,2)
        return val,'Lower RTS indicates higher trauma severity','High' if val<4 else 'Medium' if val<6 else 'Low'
    return 'N/A','Calculator not implemented yet; use as classification reference','Medium'
