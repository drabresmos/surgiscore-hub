import math
import streamlit as st
from styles import risk_badge

def save_button(db, patient_code, name, result, interp, risk):
    st.metric(name, str(result)); st.write(interp); risk_badge(risk)
    if st.button('Save Result'):
        db.save_result(patient_code, name, result, interp, risk)
        st.success('Result saved.')

def cb(label, pts=1):
    return pts if st.checkbox(f'{label} (+{pts})') else 0

SCORES = {
'General / Pre-op':['ASA','Clinical Frailty Scale','Charlson Comorbidity Index','STOP-Bang','Caprini VTE','RCRI'],
'Emergency / Sepsis':['SIRS','qSOFA','NEWS2','Shock Index','SOFA Simplified'],
'Appendicitis':['Alvarado','AIR Appendicitis','RIPASA','Pediatric Appendicitis Score'],
'Gallbladder / CBD':['Tokyo Cholecystitis Grade','Tokyo Cholangitis Grade','ASGE CBD Stone Risk','Nassar Difficulty Grade','Parkland Cholecystitis Grade','Csendes Mirizzi Classification'],
'Pancreas':['BISAP','Ranson Admission','Glasgow-Imrie Pancreatitis','Modified CT Severity Index','Atlanta Pancreatitis Classification'],
'GI Bleeding':['Glasgow-Blatchford','AIMS65','Rockall Pre-Endoscopy','Oakland Lower GI Bleeding'],
'Peritonitis / Perforation':['Mannheim Peritonitis Index','Boey Score'],
'Liver / HPB':['Child-Pugh','MELD-Na','ALBI Grade'],
'Colorectal':['Hinchey Diverticulitis','WSES Diverticulitis Classification','LARS Score','Wexner Incontinence Score'],
'Trauma':['GCS','RTS','AAST Organ Injury Grade'],
'Post-op':['Clavien-Dindo','CDC SSI Classification']
}

ALL_SCORES = [x for group in SCORES.values() for x in group]

def render_score(name, patient_code, db):
    st.subheader(name)
    if name=='ASA':
        val=st.radio('ASA Physical Status',['ASA I - Normal healthy patient','ASA II - Mild systemic disease','ASA III - Severe systemic disease','ASA IV - Severe systemic disease constant threat to life','ASA V - Moribund patient'])
        res=val.split(' - ')[0]; risk='Low' if res in ['ASA I','ASA II'] else 'High'; save_button(db,patient_code,name,res,val,risk)
    elif name=='Clinical Frailty Scale':
        grade=st.slider('CFS grade',1,9,3); risk='Low' if grade<=3 else 'Medium' if grade<=5 else 'High'; save_button(db,patient_code,name,grade,'Frailty severity grade',risk)
    elif name=='Charlson Comorbidity Index':
        score=0
        for label,pts in [('MI',1),('CHF',1),('Peripheral vascular disease',1),('CVA/TIA',1),('Dementia',1),('COPD',1),('Connective tissue disease',1),('Peptic ulcer disease',1),('Mild liver disease',1),('Diabetes',1),('Diabetes with end-organ damage',2),('Hemiplegia',2),('Moderate/severe renal disease',2),('Tumor',2),('Leukemia/lymphoma',2),('Moderate/severe liver disease',3),('Metastatic solid tumor',6),('AIDS',6)]: score+=cb(label,pts)
        risk='Low' if score<=2 else 'Medium' if score<=4 else 'High'; save_button(db,patient_code,name,score,'Comorbidity burden index',risk)
    elif name=='STOP-Bang':
        score=sum([st.checkbox(x) for x in ['Snoring','Tiredness','Observed apnea','Pressure: hypertension','BMI >35','Age >50','Neck circumference high','Male gender']])
        risk='Low' if score<=2 else 'Medium' if score<=4 else 'High'; save_button(db,patient_code,name,f'{score}/8','OSA screening risk',risk)
    elif name=='Caprini VTE':
        score=0
        for label,pts in [('Age 41-60',1),('Age 61-74',2),('Age ≥75',3),('Minor surgery',1),('Major surgery >45 min',2),('BMI >25',1),('Swollen legs',1),('Varicose veins',1),('History of malignancy',2),('Bed rest >72h',2),('Central venous access',2),('Prior DVT/PE',3),('Known thrombophilia',3),('Stroke <1 month',5),('Hip/pelvis/leg fracture',5)]: score+=cb(label,pts)
        risk='Low' if score<=2 else 'Medium' if score<=4 else 'High'; save_button(db,patient_code,name,score,'VTE risk stratification',risk)
    elif name=='RCRI':
        score=sum([st.checkbox(x) for x in ['High-risk surgery','Ischemic heart disease','Heart failure','Cerebrovascular disease','Insulin-dependent diabetes','Creatinine >2 mg/dL']])
        risk='Low' if score==0 else 'Medium' if score==1 else 'High'; save_button(db,patient_code,name,score,'Major cardiac event risk screen',risk)
    elif name=='SIRS':
        score=sum([st.checkbox(x) for x in ['Temp >38 or <36','HR >90','RR >20 or PaCO2 <32','WBC >12k, <4k, or bands >10%']])
        risk='High' if score>=2 else 'Low'; save_button(db,patient_code,name,f'{score}/4','SIRS positive if ≥2',risk)
    elif name=='qSOFA':
        score=sum([st.checkbox(x) for x in ['RR ≥22/min','Altered mentation','SBP ≤100 mmHg']])
        risk='High' if score>=2 else 'Low'; save_button(db,patient_code,name,f'{score}/3','Poor outcome screen in suspected sepsis',risk)
    elif name=='NEWS2':
        score=0
        score += st.selectbox('Respiratory rate points',[0,1,2,3])
        score += st.selectbox('SpO2 points',[0,1,2,3])
        score += st.selectbox('Temperature points',[0,1,2,3])
        score += st.selectbox('Systolic BP points',[0,1,2,3])
        score += st.selectbox('Heart rate points',[0,1,2,3])
        score += st.selectbox('Consciousness points',[0,3])
        risk='Low' if score<=4 else 'Medium' if score<=6 else 'High'; save_button(db,patient_code,name,score,'Early warning score',risk)
    elif name=='Shock Index':
        hr=st.number_input('Heart rate',20,250,90); sbp=st.number_input('Systolic BP',40,260,120); val=round(hr/sbp,2)
        risk='Low' if val<0.7 else 'Medium' if val<=0.9 else 'High'; save_button(db,patient_code,name,val,'HR/SBP physiological stress index',risk)
    elif name=='SOFA Simplified':
        score=sum([st.selectbox(x,[0,1,2,3,4]) for x in ['Respiratory','Coagulation','Liver','Cardiovascular','CNS','Renal']])
        risk='Low' if score<=5 else 'Medium' if score<=10 else 'High'; save_button(db,patient_code,name,score,'Organ failure severity',risk)
    elif name=='Alvarado':
        score=cb('Migration',1)+cb('Anorexia',1)+cb('Nausea/vomiting',1)+cb('RIF tenderness',2)+cb('Rebound',1)+cb('Fever',1)+cb('Leukocytosis',2)+cb('Neutrophilia',1)
        risk='Low' if score<=4 else 'Medium' if score<=6 else 'High'; save_button(db,patient_code,name,f'{score}/10','Appendicitis probability',risk)
    elif name=='AIR Appendicitis':
        score=cb('Vomiting',1); score += {'None':0,'Mild':1,'Moderate':2,'Strong':3}[st.selectbox('RIF tenderness',['None','Mild','Moderate','Strong'])]; score += {'None':0,'Light':1,'Medium':2,'Strong':3}[st.selectbox('Rebound/defense',['None','Light','Medium','Strong'])]; score += cb('Temp ≥38.5',1); score += {'<10':0,'10-14.9':1,'≥15':2}[st.selectbox('WBC',['<10','10-14.9','≥15'])]; score += {'<70':0,'70-84':1,'≥85':2}[st.selectbox('Neutrophils %',['<70','70-84','≥85'])]; score += {'<10':0,'10-49':1,'≥50':2}[st.selectbox('CRP mg/L',['<10','10-49','≥50'])]
        risk='Low' if score<=4 else 'Medium' if score<=8 else 'High'; save_button(db,patient_code,name,f'{score}/12','Appendicitis inflammatory response score',risk)
    elif name=='RIPASA':
        score=0
        for label,pts in [('Male',1),('Female',0.5),('Age <40',1),('RIF pain',0.5),('Migration',0.5),('Anorexia',1),('Nausea/vomiting',1),('Duration <48h',1),('RIF tenderness',1),('Guarding',2),('Rebound',1),('Rovsing',2),('Fever',1),('Raised WBC',1),('Negative urine',1)]: score+=cb(label,pts)
        risk='Low' if score<5 else 'Medium' if score<7.5 else 'High'; save_button(db,patient_code,name,score,'RIPASA appendicitis score',risk)
    elif name=='Pediatric Appendicitis Score':
        score=cb('RIF tenderness',2)+cb('Cough/percussion/hopping tenderness',2)+cb('Anorexia',1)+cb('Fever',1)+cb('Nausea/vomiting',1)+cb('Migration',1)+cb('Leukocytosis',1)+cb('Neutrophilia',1)
        risk='Low' if score<=3 else 'Medium' if score<=6 else 'High'; save_button(db,patient_code,name,f'{score}/10','Pediatric appendicitis probability',risk)
    elif name=='Tokyo Cholecystitis Grade':
        organ=st.checkbox('Organ dysfunction'); moderate=any([st.checkbox(x) for x in ['WBC >18k','Palpable tender RUQ mass','Symptoms >72h','Marked local inflammation/gangrene/abscess']])
        res,interp,risk=('Grade III','Severe with organ dysfunction','High') if organ else ('Grade II','Moderate acute cholecystitis','Medium') if moderate else ('Grade I','Mild acute cholecystitis','Low'); save_button(db,patient_code,name,res,interp,risk)
    elif name=='Tokyo Cholangitis Grade':
        organ=st.checkbox('Organ dysfunction'); moderate=sum([st.checkbox(x) for x in ['WBC abnormal','Fever ≥39','Age ≥75','Bilirubin ≥5','Hypoalbuminemia']])
        res,interp,risk=('Grade III','Severe cholangitis','High') if organ else ('Grade II','Moderate cholangitis','Medium') if moderate>=2 else ('Grade I','Mild cholangitis','Low'); save_button(db,patient_code,name,res,interp,risk)
    elif name=='ASGE CBD Stone Risk':
        high=any([st.checkbox('CBD stone on imaging'),st.checkbox('Ascending cholangitis'),st.checkbox('Bilirubin >4 + dilated CBD')]); interm=st.checkbox('Abnormal LFTs / age >55 / dilated CBD alone')
        res,interp,risk=('High','ERCP usually considered','High') if high else ('Intermediate','MRCP/EUS/IOC usually considered','Medium') if interm else ('Low','Low probability CBD stone','Low'); save_button(db,patient_code,name,res,interp,risk)
    elif name=='Nassar Difficulty Grade':
        grade=st.selectbox('Grade',['Grade 1','Grade 2','Grade 3','Grade 4','Grade 5']); risk='Low' if grade in ['Grade 1','Grade 2'] else 'Medium' if grade=='Grade 3' else 'High'; save_button(db,patient_code,name,grade,'Laparoscopic cholecystectomy difficulty grade',risk)
    elif name=='Parkland Cholecystitis Grade':
        grade=st.selectbox('Grade',['1 Normal','2 Minor adhesions','3 Hyperemia/edema','4 Severe adhesions/necrosis','5 Perforation/abscess/fistula']); risk='Low' if grade[0] in ['1','2'] else 'Medium' if grade[0]=='3' else 'High'; save_button(db,patient_code,name,grade,'Operative severity of gallbladder inflammation',risk)
    elif name=='Csendes Mirizzi Classification':
        res=st.selectbox('Type',['Type I external compression','Type II fistula <1/3 CBD','Type III fistula up to 2/3 CBD','Type IV complete CBD destruction','Type V cholecystoenteric fistula']); risk='High' if not res.startswith('Type I') else 'Medium'; save_button(db,patient_code,name,res,'Mirizzi classification',risk)
    elif name=='BISAP':
        score=sum([st.checkbox(x) for x in ['BUN >25','Impaired mental status','SIRS','Age >60','Pleural effusion']]); risk='High' if score>=3 else 'Low'; save_button(db,patient_code,name,f'{score}/5','Acute pancreatitis severity',risk)
    elif name=='Ranson Admission':
        score=sum([st.checkbox(x) for x in ['Age >55','WBC >16k','Glucose >200','LDH >350','AST >250']]); risk='High' if score>=3 else 'Low'; save_button(db,patient_code,name,f'{score}/5','Admission Ranson criteria',risk)
    elif name=='Glasgow-Imrie Pancreatitis':
        score=sum([st.checkbox(x) for x in ['PaO2 <60','Age >55','Neutrophils/WBC >15k','Calcium <8','Renal urea elevated','Enzymes LDH/AST high','Albumin <3.2','Sugar >180']]); risk='High' if score>=3 else 'Low'; save_button(db,patient_code,name,score,'Severe pancreatitis if ≥3',risk)
    elif name=='Modified CT Severity Index':
        infl=st.selectbox('Pancreatic inflammation',[0,2,4]); nec=st.selectbox('Necrosis',[0,2,4]); extra=2 if st.checkbox('Extrapancreatic complication') else 0; score=infl+nec+extra; risk='Low' if score<=2 else 'Medium' if score<=6 else 'High'; save_button(db,patient_code,name,f'{score}/10','CT severity index',risk)
    elif name=='Atlanta Pancreatitis Classification':
        res=st.selectbox('Classification',['Mild','Moderately severe','Severe']); risk={'Mild':'Low','Moderately severe':'Medium','Severe':'High'}[res]; save_button(db,patient_code,name,res,'Revised Atlanta severity classification',risk)
    elif name=='Glasgow-Blatchford':
        score=0; bun=st.number_input('BUN mg/dL',0.0,200.0,20.0); hb=st.number_input('Hb g/dL',0.0,25.0,12.0); sbp=st.number_input('SBP',40,260,120); pulse=st.number_input('Pulse',30,220,80)
        if bun>=28: score+=2
        if hb<12: score+=2
        if sbp<100: score+=2
        if pulse>=100: score+=1
        score += cb('Melena',1)+cb('Syncope',2)+cb('Liver disease',2)+cb('Cardiac failure',2); risk='Low' if score==0 else 'Medium' if score<=5 else 'High'; save_button(db,patient_code,name,score,'UGIB intervention/admission risk screen',risk)
    elif name=='AIMS65':
        score=sum([st.checkbox(x) for x in ['Albumin <3.0','INR >1.5','Altered mental status','SBP ≤90','Age >65']]); risk='Low' if score<=1 else 'Medium' if score==2 else 'High'; save_button(db,patient_code,name,f'{score}/5','UGIB mortality score',risk)
    elif name=='Rockall Pre-Endoscopy':
        score=st.selectbox('Age points',[0,1,2])+st.selectbox('Shock points',[0,1,2])+st.selectbox('Comorbidity points',[0,2,3]); risk='Low' if score<=2 else 'Medium' if score<=4 else 'High'; save_button(db,patient_code,name,score,'Pre-endoscopy UGIB risk',risk)
    elif name=='Oakland Lower GI Bleeding':
        score=st.number_input('Oakland calculated/estimated score',0,50,8); risk='Low' if score<=8 else 'High'; save_button(db,patient_code,name,score,'Lower GI bleeding safe discharge screen',risk)
    elif name=='Mannheim Peritonitis Index':
        score=0
        for label,pts in [('Age >50',5),('Female',5),('Organ failure',7),('Malignancy',4),('Duration >24h',4),('Non-colonic origin',4),('Diffuse peritonitis',6),('Cloudy/purulent exudate',6),('Fecal exudate',12)]: score+=cb(label,pts)
        risk='Low' if score<21 else 'Medium' if score<=29 else 'High'; save_button(db,patient_code,name,score,'Peritonitis mortality risk',risk)
    elif name=='Boey Score':
        score=sum([st.checkbox(x) for x in ['Major medical illness','Preoperative shock','Perforation >24h']]); risk='Low' if score<=1 else 'High'; save_button(db,patient_code,name,f'{score}/3','Perforated peptic ulcer risk',risk)
    elif name=='Child-Pugh':
        score={'None':1,'Mild':2,'Moderate/Severe':3}[st.selectbox('Ascites',['None','Mild','Moderate/Severe'])]+{'None':1,'Grade I-II':2,'Grade III-IV':3}[st.selectbox('Encephalopathy',['None','Grade I-II','Grade III-IV'])]+{'<2':1,'2-3':2,'>3':3}[st.selectbox('Bilirubin',['<2','2-3','>3'])]+{'>3.5':1,'2.8-3.5':2,'<2.8':3}[st.selectbox('Albumin',['>3.5','2.8-3.5','<2.8'])]+{'<1.7':1,'1.7-2.3':2,'>2.3':3}[st.selectbox('INR',['<1.7','1.7-2.3','>2.3'])]
        res='Class A' if score<=6 else 'Class B' if score<=9 else 'Class C'; risk='Low' if res=='Class A' else 'Medium' if res=='Class B' else 'High'; save_button(db,patient_code,name,f'{score} {res}','Cirrhosis functional reserve',risk)
    elif name=='MELD-Na':
        bili=st.number_input('Bilirubin',0.1,50.0,1.0); inr=st.number_input('INR',0.8,10.0,1.0); cr=st.number_input('Creatinine',0.1,15.0,1.0); na=st.number_input('Sodium',120,150,137)
        meld=round(3.78*math.log(max(bili,1))+11.2*math.log(max(inr,1))+9.57*math.log(max(cr,1))+6.43); nac=min(max(na,125),137); val=round(meld+1.32*(137-nac)-0.033*meld*(137-nac)); risk='Low' if val<10 else 'Medium' if val<20 else 'High'; save_button(db,patient_code,name,val,'Liver short-term mortality estimate',risk)
    elif name=='ALBI Grade':
        alb=st.number_input('Albumin g/L',10.0,60.0,35.0); bili=st.number_input('Bilirubin μmol/L',1.0,800.0,20.0); val=round((math.log10(bili)*0.66)+(alb*-0.085),2); grade='Grade 1' if val<=-2.60 else 'Grade 2' if val<=-1.39 else 'Grade 3'; risk='Low' if grade=='Grade 1' else 'Medium' if grade=='Grade 2' else 'High'; save_button(db,patient_code,name,f'{val} {grade}','Albumin-bilirubin liver function grade',risk)
    elif name=='Hinchey Diverticulitis':
        res=st.selectbox('Stage',['Ia confined pericolic inflammation','Ib pericolic abscess','II pelvic/distant abscess','III purulent peritonitis','IV fecal peritonitis']); risk='Low' if res.startswith('Ia') else 'Medium' if res.startswith(('Ib','II')) else 'High'; save_button(db,patient_code,name,res,'Diverticulitis severity',risk)
    elif name=='WSES Diverticulitis Classification':
        res=st.selectbox('Stage',['0 uncomplicated','1A pericolic air/fluid','1B abscess ≤4 cm','2A abscess >4 cm','2B distant gas','3 diffuse fluid no distant gas','4 diffuse fluid with distant gas']); risk='Low' if res[0]=='0' else 'Medium' if res[:2] in ['1A','1B','2A'] else 'High'; save_button(db,patient_code,name,res,'WSES acute diverticulitis classification',risk)
    elif name=='LARS Score':
        score=st.number_input('LARS score',0,42,0); risk='Low' if score<=20 else 'Medium' if score<=29 else 'High'; save_button(db,patient_code,name,score,'Low anterior resection syndrome',risk)
    elif name=='Wexner Incontinence Score':
        score=sum([st.slider(x,0,4,0) for x in ['Solid stool','Liquid stool','Gas','Wears pad','Lifestyle alteration']]); risk='Low' if score<=4 else 'Medium' if score<=12 else 'High'; save_button(db,patient_code,name,f'{score}/20','Fecal incontinence severity',risk)
    elif name=='GCS':
        e=st.selectbox('Eye',[4,3,2,1]); v=st.selectbox('Verbal',[5,4,3,2,1]); m=st.selectbox('Motor',[6,5,4,3,2,1]); score=e+v+m; risk='Low' if score>=13 else 'Medium' if score>=9 else 'High'; save_button(db,patient_code,name,score,'Level of consciousness',risk)
    elif name=='RTS':
        g=st.selectbox('GCS coded',[4,3,2,1,0]); sbp=st.selectbox('SBP coded',[4,3,2,1,0]); rr=st.selectbox('RR coded',[4,3,2,1,0]); val=round(0.9368*g+0.7326*sbp+0.2908*rr,2); risk='Low' if val>6 else 'Medium' if val>4 else 'High'; save_button(db,patient_code,name,val,'Revised trauma score',risk)
    elif name=='AAST Organ Injury Grade':
        organ=st.selectbox('Organ',['Spleen','Liver','Kidney','Pancreas','Bowel']); grade=st.selectbox('Grade',['I','II','III','IV','V']); risk='Low' if grade in ['I','II'] else 'Medium' if grade=='III' else 'High'; save_button(db,patient_code,name,f'{organ} Grade {grade}','AAST injury grade selector',risk)
    elif name=='Clavien-Dindo':
        res=st.selectbox('Grade',['Grade I','Grade II','Grade IIIa','Grade IIIb','Grade IV','Grade V']); risk='High' if res in ['Grade IIIb','Grade IV','Grade V'] else 'Medium' if res in ['Grade II','Grade IIIa'] else 'Low'; save_button(db,patient_code,name,res,'Postoperative complication classification',risk)
    elif name=='CDC SSI Classification':
        res=st.selectbox('SSI type',['No SSI','Superficial incisional','Deep incisional','Organ/space']); risk='Low' if res=='No SSI' else 'Medium' if res=='Superficial incisional' else 'High'; save_button(db,patient_code,name,res,'Surgical site infection classification',risk)
    else:
        st.warning('Score not implemented yet.')
