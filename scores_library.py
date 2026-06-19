import math
import streamlit as st

COMMON_OPERATIONS = [
    'Laparoscopic cholecystectomy','Open cholecystectomy','Appendectomy - laparoscopic','Appendectomy - open',
    'Inguinal hernia repair','Ventral/incisional hernia repair','Umbilical hernia repair','Hemorrhoidectomy',
    'Fistula surgery','Perianal abscess drainage','Diagnostic laparoscopy','Exploratory laparotomy',
    'Bowel resection and anastomosis','Right hemicolectomy','Left hemicolectomy','Sigmoid colectomy','Hartmann procedure','Stoma creation/closure',
    'Perforated peptic ulcer repair','Adhesiolysis for bowel obstruction','Small bowel obstruction surgery',
    'Thyroidectomy','Breast lumpectomy','Mastectomy','Pilonidal sinus surgery','Hydatid cyst liver surgery',
    'Splenectomy','Pancreatic pseudocyst drainage','Whipple procedure','Distal pancreatectomy',
    'Trauma laparotomy','Soft tissue debridement','Abscess incision and drainage','Other general surgery operation'
]

SCORE_INFO = {
 'ASA':'Preoperative anesthesia risk classification based on systemic disease burden.',
 'Caprini VTE':'Estimates venous thromboembolism risk and supports thromboprophylaxis planning.',
 'RCRI':'Predicts major cardiac complications after non-cardiac surgery.',
 'STOP-Bang':'Screens for obstructive sleep apnea risk before anesthesia.',
 'Clinical Frailty Scale':'Assesses frailty in elderly or physiologically weak surgical patients.',
 'Alvarado':'Clinical score for suspected acute appendicitis.',
 'AIR Appendicitis':'Appendicitis inflammatory response score using symptoms, exam, WBC, neutrophils, CRP.',
 'BISAP':'Early severity score for acute pancreatitis within first 24 hours.',
 'Ranson Admission':'Admission criteria for severity in acute pancreatitis.',
 'Glasgow-Blatchford':'Risk stratification for upper GI bleeding before endoscopy.',
 'AIMS65':'Mortality risk score in upper GI bleeding.',
 'qSOFA':'Bedside risk screen in suspected sepsis.',
 'SIRS':'Systemic inflammatory response screening.',
 'NEWS2':'Early warning score for clinical deterioration.',
 'Shock Index':'HR/SBP, useful in bleeding, trauma, and shock assessment.',
 'Mannheim Peritonitis Index':'Mortality risk in secondary peritonitis.',
 'Boey Score':'Risk score in perforated peptic ulcer.',
 'ASGE CBD Stone Risk':'Probability category for common bile duct stone.',
 'Tokyo Cholecystitis Grade':'Severity grading for acute cholecystitis.',
 'Tokyo Cholangitis Grade':'Severity grading for acute cholangitis.',
 'Child-Pugh':'Severity of chronic liver disease and operative risk context.',
 'MELD-Na':'Short-term liver-related mortality estimate.',
 'GCS':'Neurologic assessment in trauma and critical illness.',
 'RTS':'Physiologic trauma severity score.',
 'Clavien-Dindo':'Standard classification of postoperative complications.',
 'CDC SSI':'Classifies surgical site infection as superficial, deep, or organ-space.'
}

ALL_SCORES = list(SCORE_INFO.keys())

OPERATION_SCORES = {
 'Laparoscopic cholecystectomy':['ASA','Caprini VTE','RCRI','ASGE CBD Stone Risk','Tokyo Cholecystitis Grade'],
 'Open cholecystectomy':['ASA','Caprini VTE','RCRI','ASGE CBD Stone Risk','Tokyo Cholecystitis Grade'],
 'Appendectomy - laparoscopic':['ASA','Alvarado','AIR Appendicitis','qSOFA','SIRS'],
 'Appendectomy - open':['ASA','Alvarado','AIR Appendicitis','qSOFA','SIRS'],
 'Inguinal hernia repair':['ASA','Caprini VTE','RCRI','STOP-Bang'],
 'Ventral/incisional hernia repair':['ASA','Caprini VTE','RCRI','STOP-Bang'],
 'Umbilical hernia repair':['ASA','Caprini VTE','RCRI'],
 'Hemorrhoidectomy':['ASA','Caprini VTE'],
 'Fistula surgery':['ASA','Caprini VTE'],
 'Perianal abscess drainage':['ASA','SIRS','qSOFA'],
 'Diagnostic laparoscopy':['ASA','Caprini VTE','RCRI'],
 'Exploratory laparotomy':['ASA','Caprini VTE','RCRI','qSOFA','Shock Index','Mannheim Peritonitis Index'],
 'Bowel resection and anastomosis':['ASA','Caprini VTE','RCRI','qSOFA','Mannheim Peritonitis Index'],
 'Right hemicolectomy':['ASA','Caprini VTE','RCRI','Clinical Frailty Scale'],
 'Left hemicolectomy':['ASA','Caprini VTE','RCRI','Clinical Frailty Scale'],
 'Sigmoid colectomy':['ASA','Caprini VTE','RCRI','Clinical Frailty Scale'],
 'Hartmann procedure':['ASA','Caprini VTE','RCRI','qSOFA','Mannheim Peritonitis Index'],
 'Stoma creation/closure':['ASA','Caprini VTE','RCRI'],
 'Perforated peptic ulcer repair':['ASA','Boey Score','qSOFA','Shock Index','Mannheim Peritonitis Index'],
 'Adhesiolysis for bowel obstruction':['ASA','Caprini VTE','RCRI','Shock Index'],
 'Small bowel obstruction surgery':['ASA','Caprini VTE','RCRI','Shock Index'],
 'Thyroidectomy':['ASA','RCRI','STOP-Bang'],
 'Breast lumpectomy':['ASA','Caprini VTE'],
 'Mastectomy':['ASA','Caprini VTE','RCRI'],
 'Pilonidal sinus surgery':['ASA'],
 'Hydatid cyst liver surgery':['ASA','Caprini VTE','RCRI','Child-Pugh','MELD-Na'],
 'Splenectomy':['ASA','Caprini VTE','RCRI','Shock Index'],
 'Pancreatic pseudocyst drainage':['ASA','BISAP','Ranson Admission','RCRI'],
 'Whipple procedure':['ASA','Caprini VTE','RCRI','Child-Pugh','MELD-Na','Clinical Frailty Scale'],
 'Distal pancreatectomy':['ASA','Caprini VTE','RCRI','BISAP'],
 'Trauma laparotomy':['ASA','GCS','RTS','Shock Index','qSOFA'],
 'Soft tissue debridement':['ASA','SIRS','qSOFA','Caprini VTE'],
 'Abscess incision and drainage':['ASA','SIRS','qSOFA'],
 'Other general surgery operation':['ASA','Caprini VTE','RCRI']
}

def recommended_scores(operation_type):
    return OPERATION_SCORES.get(operation_type, ['ASA','Caprini VTE','RCRI'])

def render_score(score_name, key_prefix=''):
    st.caption(SCORE_INFO.get(score_name,''))
    k = lambda x: f'{key_prefix}_{score_name}_{x}'
    if score_name == 'ASA':
        v=st.radio('ASA Physical Status',['ASA I','ASA II','ASA III','ASA IV','ASA V'],key=k('asa'))
        risk='Low' if v in ['ASA I','ASA II'] else ('Medium' if v=='ASA III' else 'High')
        return v, f'{v} selected.', risk
    if score_name == 'Caprini VTE':
        items={'Age 41–60':1,'Age 61–74':2,'Age ≥75':3,'Minor surgery':1,'Major surgery >45 min':2,'BMI >25':1,'Malignancy':2,'Bed rest >72h':2,'Central venous access':2,'Prior DVT/PE':3,'Known thrombophilia':3,'Stroke <1 month':5,'Hip/pelvis/leg fracture':5}
        s=sum(pts for item,pts in items.items() if st.checkbox(f'{item} (+{pts})',key=k(item)))
        risk='Low' if s<=2 else ('Medium' if s<=4 else 'High')
        return s, f'Caprini score {s}.', risk
    if score_name == 'RCRI':
        items=['High-risk surgery','Ischemic heart disease','Heart failure','Cerebrovascular disease','Insulin-dependent diabetes','Creatinine >2 mg/dL']
        s=sum(1 for it in items if st.checkbox(it,key=k(it)))
        risk='Low' if s==0 else ('Medium' if s==1 else 'High')
        return s, f'RCRI {s}.', risk
    if score_name == 'STOP-Bang':
        items=['Snoring','Tiredness','Observed apnea','Pressure hypertension','BMI >35','Age >50','Neck circumference high','Male gender']
        s=sum(1 for it in items if st.checkbox(it,key=k(it)))
        risk='Low' if s<=2 else ('Medium' if s<=4 else 'High')
        return s, f'STOP-Bang {s}/8.', risk
    if score_name == 'Clinical Frailty Scale':
        s=st.slider('Clinical Frailty Scale',1,9,3,key=k('cfs'))
        risk='Low' if s<=3 else ('Medium' if s<=5 else 'High')
        return s, f'CFS {s}/9.', risk
    if score_name == 'Alvarado':
        pts=[('Migration',1),('Anorexia',1),('Nausea/vomiting',1),('RIF tenderness',2),('Rebound',1),('Fever',1),('Leukocytosis',2),('Neutrophilia',1)]
        s=sum(p for it,p in pts if st.checkbox(f'{it} (+{p})',key=k(it)))
        risk='Low' if s<=4 else ('Medium' if s<=6 else 'High')
        return s, f'Alvarado {s}/10.', risk
    if score_name == 'AIR Appendicitis':
        s=0
        if st.checkbox('Vomiting (+1)',key=k('vomit')): s+=1
        s += {'None':0,'Mild':1,'Moderate':2,'Strong':3}[st.selectbox('RIF tenderness',['None','Mild','Moderate','Strong'],key=k('rif'))]
        s += {'None':0,'Light':1,'Medium':2,'Strong':3}[st.selectbox('Rebound / defense',['None','Light','Medium','Strong'],key=k('def'))]
        if st.checkbox('Temp ≥38.5 (+1)',key=k('temp')): s+=1
        s += {'<10':0,'10–14.9':1,'≥15':2}[st.selectbox('WBC',['<10','10–14.9','≥15'],key=k('wbc'))]
        s += {'<70':0,'70–84':1,'≥85':2}[st.selectbox('Neutrophils %',['<70','70–84','≥85'],key=k('neut'))]
        s += {'<10':0,'10–49':1,'≥50':2}[st.selectbox('CRP mg/L',['<10','10–49','≥50'],key=k('crp'))]
        risk='Low' if s<=4 else ('Medium' if s<=8 else 'High')
        return s, f'AIR {s}/12.', risk
    if score_name == 'BISAP':
        items=['BUN >25','Impaired mental status','SIRS','Age >60','Pleural effusion']
        s=sum(1 for it in items if st.checkbox(it,key=k(it)))
        risk='High' if s>=3 else 'Low'
        return s, f'BISAP {s}/5.', risk
    if score_name == 'Ranson Admission':
        items=['Age >55','WBC >16000','Glucose >200','LDH >350','AST >250']
        s=sum(1 for it in items if st.checkbox(it,key=k(it)))
        risk='High' if s>=3 else 'Low'
        return s, f'Ranson admission {s}/5.', risk
    if score_name == 'Glasgow-Blatchford':
        s=0
        bun=st.number_input('BUN mg/dL',0.0,200.0,20.0,key=k('bun')); hb=st.number_input('Hb g/dL',0.0,25.0,12.0,key=k('hb')); sbp=st.number_input('SBP',40,250,120,key=k('sbp')); pulse=st.number_input('Pulse',30,220,80,key=k('pulse'))
        if bun>=28:s+=2
        if hb<12:s+=2
        if sbp<100:s+=2
        if pulse>=100:s+=1
        for it,p in [('Melena',1),('Syncope',2),('Liver disease',2),('Heart failure',2)]:
            if st.checkbox(f'{it} (+{p})',key=k(it)): s+=p
        risk='Low' if s==0 else ('Medium' if s<=5 else 'High')
        return s, f'GBS simplified {s}.', risk
    if score_name == 'AIMS65':
        items=['Albumin <3.0','INR >1.5','Altered mental status','SBP ≤90','Age >65']
        s=sum(1 for it in items if st.checkbox(it,key=k(it)))
        risk='Low' if s<=1 else ('Medium' if s==2 else 'High')
        return s, f'AIMS65 {s}/5.', risk
    if score_name == 'qSOFA':
        items=['RR ≥22','Altered mentation','SBP ≤100']
        s=sum(1 for it in items if st.checkbox(it,key=k(it)))
        risk='High' if s>=2 else 'Low'
        return s, f'qSOFA {s}/3.', risk
    if score_name == 'SIRS':
        items=['Temp >38 or <36','HR >90','RR >20 or PaCO2 <32','WBC >12000 or <4000 or bands >10%']
        s=sum(1 for it in items if st.checkbox(it,key=k(it)))
        risk='High' if s>=2 else 'Low'
        return s, f'SIRS {s}/4.', risk
    if score_name == 'NEWS2':
        rr=st.slider('Respiratory rate score',0,3,0,key=k('rr')); spo2=st.slider('SpO2 score',0,3,0,key=k('spo2')); o2=2 if st.checkbox('Supplemental oxygen (+2)',key=k('o2')) else 0; temp=st.slider('Temperature score',0,3,0,key=k('temp')); sbp=st.slider('SBP score',0,3,0,key=k('sbp')); hr=st.slider('Pulse score',0,3,0,key=k('hr')); avpu=3 if st.checkbox('New confusion / V/P/U (+3)',key=k('avpu')) else 0
        s=rr+spo2+o2+temp+sbp+hr+avpu; risk='Low' if s<=4 else ('Medium' if s<=6 else 'High')
        return s, f'NEWS2 {s}.', risk
    if score_name == 'Shock Index':
        hr=st.number_input('Heart rate',20,250,90,key=k('hr')); sbp=st.number_input('Systolic BP',40,250,120,key=k('sbp')); val=round(hr/sbp,2)
        risk='Low' if val<0.7 else ('Medium' if val<=0.9 else 'High')
        return val, f'Shock Index {val}.', risk
    if score_name == 'Mannheim Peritonitis Index':
        items={'Age >50':5,'Female sex':5,'Organ failure':7,'Malignancy':4,'Duration >24h':4,'Origin not colonic':4,'Diffuse peritonitis':6,'Purulent exudate':6,'Fecal exudate':12}
        s=sum(p for it,p in items.items() if st.checkbox(f'{it} (+{p})',key=k(it)))
        risk='Low' if s<21 else ('Medium' if s<=29 else 'High')
        return s, f'MPI {s}.', risk
    if score_name == 'Boey Score':
        items=['Major medical illness','Preoperative shock','Perforation >24h']
        s=sum(1 for it in items if st.checkbox(it,key=k(it)))
        risk='High' if s>=2 else 'Low'
        return s, f'Boey {s}/3.', risk
    if score_name == 'ASGE CBD Stone Risk':
        if st.checkbox('CBD stone on imaging',key=k('stone')) or st.checkbox('Ascending cholangitis',key=k('cholangitis')) or st.checkbox('Bilirubin >4 + dilated CBD',key=k('bili4')):
            return 'High','High probability CBD stone; ERCP usually considered.','High'
        if st.checkbox('Abnormal LFTs / age >55 / dilated CBD alone',key=k('inter')):
            return 'Intermediate','MRCP/EUS/IOC usually considered.','Medium'
        return 'Low','Low probability CBD stone.','Low'
    if score_name == 'Tokyo Cholecystitis Grade':
        if st.checkbox('Organ dysfunction',key=k('organ')): return 'Grade III','Severe acute cholecystitis.','High'
        if st.checkbox('WBC abnormal / palpable mass / >72h / marked local inflammation',key=k('mod')): return 'Grade II','Moderate acute cholecystitis.','Medium'
        return 'Grade I','Mild acute cholecystitis.','Low'
    if score_name == 'Tokyo Cholangitis Grade':
        if st.checkbox('Organ dysfunction',key=k('organ')): return 'Grade III','Severe acute cholangitis.','High'
        positives=sum(1 for it in ['Age ≥75','High fever','WBC abnormal','Bilirubin ≥5','Hypoalbuminemia'] if st.checkbox(it,key=k(it)))
        if positives>=2: return 'Grade II','Moderate acute cholangitis.','Medium'
        return 'Grade I','Mild acute cholangitis.','Low'
    if score_name == 'Child-Pugh':
        s={'None':1,'Mild':2,'Moderate/Severe':3}[st.selectbox('Ascites',['None','Mild','Moderate/Severe'],key=k('asc'))]+{'None':1,'Grade I-II':2,'Grade III-IV':3}[st.selectbox('Encephalopathy',['None','Grade I-II','Grade III-IV'],key=k('enc'))]+{'<2':1,'2–3':2,'>3':3}[st.selectbox('Bilirubin',['<2','2–3','>3'],key=k('bil'))]+{'>3.5':1,'2.8–3.5':2,'<2.8':3}[st.selectbox('Albumin',['>3.5','2.8–3.5','<2.8'],key=k('alb'))]+{'<1.7':1,'1.7–2.3':2,'>2.3':3}[st.selectbox('INR',['<1.7','1.7–2.3','>2.3'],key=k('inr'))]
        cls='A' if s<=6 else ('B' if s<=9 else 'C'); risk='Low' if cls=='A' else ('Medium' if cls=='B' else 'High')
        return f'{s} Class {cls}', f'Child-Pugh class {cls}.', risk
    if score_name == 'MELD-Na':
        bili=max(st.number_input('Bilirubin',0.1,50.0,1.0,key=k('bil')),1.0); inr=max(st.number_input('INR',0.8,10.0,1.0,key=k('inr')),1.0); cr=max(st.number_input('Creatinine',0.1,15.0,1.0,key=k('cr')),1.0); na=st.number_input('Sodium',120,150,137,key=k('na'))
        meld=round(3.78*math.log(bili)+11.2*math.log(inr)+9.57*math.log(cr)+6.43); nac=min(max(na,125),137); val=round(meld + 1.32*(137-nac) - 0.033*meld*(137-nac))
        risk='Low' if val<10 else ('Medium' if val<20 else 'High')
        return val, f'MELD-Na {val}.', risk
    if score_name == 'GCS':
        e=st.selectbox('Eye',['4 Spontaneous','3 Voice','2 Pain','1 None'],key=k('e')); v=st.selectbox('Verbal',['5 Oriented','4 Confused','3 Words','2 Sounds','1 None'],key=k('v')); m=st.selectbox('Motor',['6 Obeys','5 Localizes','4 Withdraws','3 Flexion','2 Extension','1 None'],key=k('m'))
        val=int(e[0])+int(v[0])+int(m[0]); risk='Low' if val>=13 else ('Medium' if val>=9 else 'High')
        return val, f'GCS {val}/15.', risk
    if score_name == 'RTS':
        g=st.slider('GCS coded 0-4',0,4,4,key=k('g')); sbp=st.slider('SBP coded 0-4',0,4,4,key=k('sbp')); rr=st.slider('RR coded 0-4',0,4,4,key=k('rr')); val=round(0.9368*g+0.7326*sbp+0.2908*rr,2); risk='High' if val<4 else ('Medium' if val<6 else 'Low')
        return val, f'Revised Trauma Score {val}.', risk
    if score_name == 'Clavien-Dindo':
        v=st.selectbox('Grade',['Grade I','Grade II','Grade IIIa','Grade IIIb','Grade IV','Grade V'],key=k('cd'))
        risk='High' if v in ['Grade IIIb','Grade IV','Grade V'] else ('Medium' if v in ['Grade II','Grade IIIa'] else 'Low')
        return v, f'Postoperative complication {v}.', risk
    if score_name == 'CDC SSI':
        v=st.selectbox('SSI type',['No SSI','Superficial incisional SSI','Deep incisional SSI','Organ/space SSI'],key=k('ssi'))
        risk='Low' if v=='No SSI' else ('Medium' if v.startswith('Superficial') else 'High')
        return v, f'CDC SSI classification: {v}.', risk
    return 'N/A','Score not implemented yet.','Medium'
