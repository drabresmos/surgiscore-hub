import math
import streamlit as st

SCORES = {
 'Perioperative': ['ASA','RCRI','Caprini VTE','Charlson Comorbidity Index','Clinical Frailty Scale','STOP-Bang'],
 'Sepsis / Emergency': ['SIRS','qSOFA','NEWS2','Shock Index','SOFA Simplified'],
 'Appendicitis': ['Alvarado','AIR Appendicitis','RIPASA','Pediatric Appendicitis Score'],
 'Biliary': ['Tokyo Cholecystitis Grade','Tokyo Cholangitis Grade','ASGE CBD Stone Risk','Nassar Difficulty Grade','Parkland Grade','Csendes Mirizzi'],
 'Pancreas': ['BISAP','Ranson Admission','Glasgow-Imrie','Modified CTSI','Atlanta Classification'],
 'GI Bleeding': ['Glasgow-Blatchford','AIMS65','Rockall Pre-Endoscopy','Oakland Lower GI Bleeding'],
 'Peritonitis / Perforation': ['Mannheim Peritonitis Index','Boey Score'],
 'Liver': ['Child-Pugh','MELD-Na','ALBI Grade'],
 'Colorectal': ['Hinchey Diverticulitis','WSES Diverticulitis','LARS Score','Wexner Incontinence Score'],
 'Trauma': ['GCS','RTS','AAST Organ Injury Grade'],
 'Postoperative': ['Clavien-Dindo','CDC SSI Classification']
}

INFO = {
 'ASA':'Preoperative anesthesia and systemic disease status.', 'RCRI':'Major cardiac complication risk before non-cardiac surgery.',
 'Caprini VTE':'Venous thromboembolism risk stratification.', 'Alvarado':'Clinical probability of acute appendicitis.',
 'BISAP':'Early severity risk in acute pancreatitis.', 'Glasgow-Blatchford':'Upper GI bleeding intervention/admission risk.',
 'MELD-Na':'Liver disease short-term mortality risk.', 'Clavien-Dindo':'Postoperative complication severity classification.'
}

def cb(label, pts=1):
    return pts if st.checkbox(f'{label} (+{pts})') else 0

def show_info(name):
    st.caption(INFO.get(name, 'Clinical score/classification for surgical decision support.'))

def calc_score(name):
    show_info(name)
    risk='Low'; interp=''; rec='Use with clinical judgment.'; result=''

    if name == 'ASA':
        asa = st.radio('ASA class', ['ASA I - Healthy','ASA II - Mild systemic disease','ASA III - Severe systemic disease','ASA IV - Constant threat to life','ASA V - Moribund'])
        result = asa.split(' - ')[0]; interp = asa; risk = 'Low' if result in ['ASA I','ASA II'] else 'High'; rec='Document ASA and optimize comorbidities before surgery.'

    elif name == 'RCRI':
        score=sum(cb(x) for x in ['High-risk surgery','Ischemic heart disease','Heart failure','Cerebrovascular disease','Insulin-dependent diabetes','Creatinine >2 mg/dL'])
        result=score; risk='Low' if score==0 else 'Medium' if score==1 else 'High'; interp=f'RCRI {score} cardiac risk category: {risk}.'; rec='Consider ECG, optimization, anesthesia/cardiology review if elevated.'

    elif name == 'Caprini VTE':
        items={'Age 41–60':1,'Age 61–74':2,'Age ≥75':3,'Minor surgery':1,'Major surgery >45 min':2,'BMI >25':1,'Varicose veins':1,'Cancer':2,'Bed rest >72h':2,'Central venous access':2,'Prior DVT/PE':3,'Thrombophilia':3,'Stroke <1 month':5,'Lower limb arthroplasty/fracture':5}
        score=sum(cb(k,v) for k,v in items.items()); result=score
        risk='Low' if score<=2 else 'Medium' if score<=4 else 'High'; interp=f'Caprini {score}: {risk} VTE risk.'; rec='Choose mechanical/pharmacologic prophylaxis according to bleeding risk.'

    elif name == 'Charlson Comorbidity Index':
        items={'MI':1,'CHF':1,'PVD':1,'CVA/TIA':1,'Dementia':1,'COPD':1,'Connective tissue disease':1,'Peptic ulcer':1,'Mild liver disease':1,'Diabetes':1,'Hemiplegia':2,'Moderate/severe renal disease':2,'Diabetes with end-organ damage':2,'Tumor':2,'Leukemia/Lymphoma':2,'Moderate/severe liver disease':3,'Metastatic tumor':6,'AIDS':6}
        score=sum(cb(k,v) for k,v in items.items()); result=score; risk='Low' if score<=2 else 'Medium' if score<=4 else 'High'; interp=f'CCI {score}: comorbidity burden {risk}.'; rec='Use for risk adjustment and shared decision-making.'

    elif name == 'Clinical Frailty Scale':
        val=st.slider('Frailty scale',1,9,3); result=val; risk='Low' if val<=3 else 'Medium' if val<=5 else 'High'; interp=f'CFS {val}: {risk} frailty risk.'; rec='High frailty needs geriatric/anesthetic optimization and realistic consent.'

    elif name == 'STOP-Bang':
        score=sum(cb(x) for x in ['Snoring','Tiredness','Observed apnea','High blood pressure','BMI >35','Age >50','Neck circumference high','Male gender'])
        result=score; risk='Low' if score<=2 else 'Medium' if score<=4 else 'High'; interp=f'STOP-Bang {score}: OSA risk {risk}.'; rec='Plan airway/postoperative monitoring if elevated.'

    elif name == 'SIRS':
        score=sum(cb(x) for x in ['Temp >38 or <36','HR >90','RR >20 or PaCO2 <32','WBC >12k, <4k, or bands >10%'])
        result=f'{score}/4'; risk='High' if score>=2 else 'Low'; interp='SIRS positive.' if score>=2 else 'SIRS negative.'; rec='Search for infection/source control if clinically suspected.'

    elif name == 'qSOFA':
        score=sum(cb(x) for x in ['RR ≥22','Altered mentation','SBP ≤100']); result=f'{score}/3'; risk='High' if score>=2 else 'Low'; interp='High risk poor outcome in suspected infection.' if score>=2 else 'Lower qSOFA risk.'; rec='Escalate sepsis management when ≥2.'

    elif name == 'NEWS2':
        rr=st.selectbox('Respiratory rate score',[0,1,2,3]); spo2=st.selectbox('SpO2 score',[0,1,2,3]); o2=st.selectbox('Supplemental O2',[0,2]); temp=st.selectbox('Temperature score',[0,1,2,3]); sbp=st.selectbox('SBP score',[0,1,2,3]); hr=st.selectbox('Heart rate score',[0,1,2,3]); avpu=st.selectbox('Consciousness score',[0,3]); score=sum([rr,spo2,o2,temp,sbp,hr,avpu])
        result=score; risk='Low' if score<=4 else 'Medium' if score<=6 else 'High'; interp=f'NEWS2 {score}: {risk} deterioration risk.'; rec='Escalate monitoring according to NEWS2 severity.'

    elif name == 'Shock Index':
        hr=st.number_input('Heart rate',20,250,90); sbp=st.number_input('Systolic BP',40,250,120); val=round(hr/sbp,2); result=val; risk='Low' if val<0.7 else 'Medium' if val<=0.9 else 'High'; interp=f'Shock Index {val}: {risk} hemodynamic risk.'; rec='Assess bleeding, sepsis, dehydration, and resuscitation needs.'

    elif name == 'SOFA Simplified':
        score=sum(st.selectbox(x,[0,1,2,3,4]) for x in ['Respiration','Coagulation','Liver','Cardiovascular','CNS','Renal'])
        result=score; risk='Low' if score<2 else 'Medium' if score<8 else 'High'; interp=f'Simplified SOFA {score}: organ dysfunction burden.'; rec='Use trend and ICU context; this is simplified.'

    elif name == 'Alvarado':
        score=cb('Migration')+cb('Anorexia')+cb('Nausea/vomiting')+cb('RIF tenderness',2)+cb('Rebound')+cb('Fever')+cb('Leukocytosis',2)+cb('Neutrophilia')
        result=f'{score}/10'; risk='Low' if score<=4 else 'Medium' if score<=6 else 'High'; interp=f'Alvarado {score}: {risk} appendicitis probability.'; rec='Use imaging/observation according to probability and patient factors.'

    elif name == 'AIR Appendicitis':
        score=cb('Vomiting')+st.selectbox('RIF tenderness',[0,1,2,3])+st.selectbox('Rebound/defense',[0,1,2,3])+cb('Temp ≥38.5')+st.selectbox('WBC score',[0,1,2])+st.selectbox('Neutrophil score',[0,1,2])+st.selectbox('CRP score',[0,1,2])
        result=f'{score}/12'; risk='Low' if score<=4 else 'Medium' if score<=8 else 'High'; interp=f'AIR {score}: {risk} probability.'; rec='Intermediate/high risk usually needs imaging or surgical review.'

    elif name == 'RIPASA':
        score=sum(st.checkbox(x)*1 for x in ['Male','Age <40','RIF pain','Migration','Anorexia','Nausea/vomiting','RIF tenderness','Guarding','Rebound','Fever','Raised WBC','Negative urine'])
        result=score; risk='Low' if score<5 else 'Medium' if score<7.5 else 'High'; interp=f'RIPASA {score}: {risk} probability.'; rec='Apply local validation; useful adjunct in suspected appendicitis.'

    elif name == 'Pediatric Appendicitis Score':
        score=cb('Migration')+cb('Anorexia')+cb('Nausea/vomiting')+cb('RIF tenderness',2)+cb('Cough/percussion/hopping pain',2)+cb('Fever')+cb('Leukocytosis')+cb('Neutrophilia')
        result=f'{score}/10'; risk='Low' if score<=3 else 'Medium' if score<=6 else 'High'; interp=f'PAS {score}: {risk} probability.'; rec='Pediatric surgical assessment/imaging as appropriate.'

    elif name == 'Tokyo Cholecystitis Grade':
        organ=st.checkbox('Organ dysfunction'); moderate=any([st.checkbox('WBC abnormal'),st.checkbox('Palpable RUQ mass'),st.checkbox('Duration >72h'),st.checkbox('Marked local inflammation')])
        result='Grade III' if organ else 'Grade II' if moderate else 'Grade I'; risk='High' if organ else 'Medium' if moderate else 'Low'; interp=f'Tokyo acute cholecystitis {result}.'; rec='Select early surgery/drainage/antibiotics based on grade and fitness.'

    elif name == 'Tokyo Cholangitis Grade':
        organ=st.checkbox('Organ dysfunction'); moderate=sum(st.checkbox(x) for x in ['WBC abnormal','Fever ≥39','Age ≥75','Bilirubin ≥5','Hypoalbuminemia'])>=2
        result='Grade III' if organ else 'Grade II' if moderate else 'Grade I'; risk='High' if organ else 'Medium' if moderate else 'Low'; interp=f'Tokyo acute cholangitis {result}.'; rec='Antibiotics and biliary drainage urgency depend on grade.'

    elif name == 'ASGE CBD Stone Risk':
        high=st.checkbox('CBD stone on imaging') or st.checkbox('Ascending cholangitis') or st.checkbox('Bilirubin >4 + dilated CBD'); inter=st.checkbox('Abnormal LFTs / age >55 / dilated CBD')
        result='High' if high else 'Intermediate' if inter else 'Low'; risk='High' if high else 'Medium' if inter else 'Low'; interp=f'ASGE CBD stone risk: {result}.'; rec='High: consider ERCP. Intermediate: MRCP/EUS/IOC. Low: cholecystectomy as indicated.'

    elif name in ['Nassar Difficulty Grade','Parkland Grade','Csendes Mirizzi','AAST Organ Injury Grade']:
        grade=st.selectbox('Grade',[1,2,3,4,5]); result=f'Grade {grade}'; risk='Low' if grade<=2 else 'Medium' if grade==3 else 'High'; interp=f'{name}: Grade {grade}.'; rec='Higher grade suggests more complex operative strategy and senior support.'

    elif name == 'BISAP':
        score=sum(cb(x) for x in ['BUN >25','Impaired mental status','SIRS','Age >60','Pleural effusion']); result=f'{score}/5'; risk='High' if score>=3 else 'Low'; interp=f'BISAP {score}: {risk} severity risk.'; rec='High risk needs close monitoring/ICU consideration.'

    elif name == 'Ranson Admission':
        score=sum(cb(x) for x in ['Age >55','WBC >16k','Glucose >200','LDH >350','AST >250']); result=f'{score}/5'; risk='Low' if score<=2 else 'High'; interp=f'Ranson admission {score}: {risk} severity risk.'; rec='Complete 48h criteria for full Ranson assessment.'

    elif name == 'Glasgow-Imrie':
        score=sum(cb(x) for x in ['Age >55','WBC >15k','Glucose >180','Urea >45','PaO2 <60','Calcium <8','Albumin <3.2','LDH >600','AST/ALT >200']); result=f'{score}/9'; risk='High' if score>=3 else 'Low'; interp=f'Glasgow-Imrie {score}: pancreatitis severity {risk}.'; rec='Score ≥3 suggests severe pancreatitis risk.'

    elif name == 'Modified CTSI':
        infl=st.selectbox('Pancreatic inflammation',[0,2,4]); nec=st.selectbox('Necrosis',[0,2,4]); extra=st.selectbox('Extrapancreatic complications',[0,2]); score=infl+nec+extra; result=f'{score}/10'; risk='Low' if score<=2 else 'Medium' if score<=6 else 'High'; interp=f'Modified CTSI {score}: {risk} radiologic severity.'; rec='Use with clinical course, organ failure, and collections.'

    elif name == 'Atlanta Classification':
        cls=st.selectbox('Atlanta severity',['Mild','Moderately severe','Severe']); result=cls; risk='Low' if cls=='Mild' else 'Medium' if cls=='Moderately severe' else 'High'; interp=f'Acute pancreatitis: {cls}.'; rec='Severe = persistent organ failure >48h; manage in high-acuity setting.'

    elif name == 'Glasgow-Blatchford':
        score=0; score+=st.selectbox('BUN score',[0,2,3,4,6]); score+=st.selectbox('Hemoglobin score',[0,1,3,6]); score+=st.selectbox('SBP score',[0,1,2,3]); score+=cb('Pulse ≥100'); score+=cb('Melena'); score+=cb('Syncope',2); score+=cb('Liver disease',2); score+=cb('Cardiac failure',2)
        result=score; risk='Low' if score==0 else 'Medium' if score<=5 else 'High'; interp=f'GBS {score}: {risk} UGIB risk.'; rec='GBS 0 may be outpatient; higher scores usually need admission/endoscopy.'

    elif name == 'AIMS65':
        score=sum(cb(x) for x in ['Albumin <3.0','INR >1.5','Altered mental status','SBP ≤90','Age >65']); result=f'{score}/5'; risk='Low' if score<=1 else 'Medium' if score==2 else 'High'; interp=f'AIMS65 {score}: mortality risk {risk}.'; rec='Escalate resuscitation and endoscopy planning if elevated.'

    elif name == 'Rockall Pre-Endoscopy':
        score=st.selectbox('Age score',[0,1,2])+st.selectbox('Shock score',[0,1,2])+st.selectbox('Comorbidity score',[0,2,3]); result=score; risk='Low' if score<=2 else 'Medium' if score<=4 else 'High'; interp=f'Pre-endoscopy Rockall {score}: {risk} risk.'; rec='Use final Rockall after endoscopic diagnosis/stigmata.'

    elif name == 'Oakland Lower GI Bleeding':
        score=st.number_input('Oakland total score if calculated manually',0,40,8); result=score; risk='Low' if score<=8 else 'High'; status = 'possible safe discharge' if score <= 8 else 'admission/assessment usually needed'; interp=f'Oakland {score}: {status}.'; rec='Use local protocol and clinical judgment.'

    elif name == 'Mannheim Peritonitis Index':
        items={'Age >50':5,'Female':5,'Organ failure':7,'Malignancy':4,'Duration >24h':4,'Non-colonic origin':4,'Diffuse peritonitis':6,'Cloudy/purulent exudate':6,'Fecal exudate':12}
        score=sum(cb(k,v) for k,v in items.items()); result=score; risk='Low' if score<21 else 'Medium' if score<=29 else 'High'; interp=f'MPI {score}: {risk} mortality risk.'; rec='High score supports aggressive resuscitation/source control/ICU planning.'

    elif name == 'Boey Score':
        score=sum(cb(x) for x in ['Major medical illness','Preoperative shock','Perforation >24h']); result=f'{score}/3'; risk='Low' if score<=1 else 'High'; interp=f'Boey {score}: perforated peptic ulcer risk {risk}.'; rec='Optimize resuscitation and counsel risk.'

    elif name == 'Child-Pugh':
        score=sum([st.selectbox('Ascites',[1,2,3]),st.selectbox('Encephalopathy',[1,2,3]),st.selectbox('Bilirubin',[1,2,3]),st.selectbox('Albumin',[1,2,3]),st.selectbox('INR/PT',[1,2,3])]); cls='A' if score<=6 else 'B' if score<=9 else 'C'; result=f'{score} Class {cls}'; risk='Low' if cls=='A' else 'Medium' if cls=='B' else 'High'; interp=f'Child-Pugh {result}.'; rec='Higher class increases operative risk; optimize liver status.'

    elif name == 'MELD-Na':
        bili=max(st.number_input('Bilirubin',0.1,50.0,1.0),1.0); inr=max(st.number_input('INR',0.8,10.0,1.0),1.0); cr=max(st.number_input('Creatinine',0.1,15.0,1.0),1.0); na=st.number_input('Sodium',120,150,137); meld=round(3.78*math.log(bili)+11.2*math.log(inr)+9.57*math.log(cr)+6.43); nac=min(max(na,125),137); val=round(meld+1.32*(137-nac)-0.033*meld*(137-nac)); result=val; risk='Low' if val<10 else 'Medium' if val<20 else 'High'; interp=f'MELD-Na {val}: {risk} liver mortality risk.'; rec='Use validated transplant/hepatology context.'

    elif name == 'ALBI Grade':
        alb=st.number_input('Albumin g/L',10.0,60.0,35.0); bili=st.number_input('Bilirubin µmol/L',1.0,600.0,20.0); val=round((math.log10(bili)*0.66)+(alb*-0.085),2); grade='1' if val<=-2.60 else '2' if val<=-1.39 else '3'; result=f'{val} Grade {grade}'; risk='Low' if grade=='1' else 'Medium' if grade=='2' else 'High'; interp=f'ALBI {result}.'; rec='Useful in HCC/liver reserve assessment.'

    elif name in ['Hinchey Diverticulitis','WSES Diverticulitis']:
        stage=st.selectbox('Stage/Grade',['Ia','Ib','II','III','IV']); result=stage; risk='Low' if stage in ['Ia','Ib'] else 'Medium' if stage=='II' else 'High'; interp=f'{name}: {stage}.'; rec='Higher stage suggests drainage/surgery depending on stability and contamination.'

    elif name == 'LARS Score':
        score=st.number_input('LARS score',0,42,0); result=score; risk='Low' if score<=20 else 'Medium' if score<=29 else 'High'; interp='No/minor LARS' if score<=20 else 'Minor LARS' if score<=29 else 'Major LARS'; rec='Consider bowel rehabilitation and colorectal follow-up if high.'

    elif name == 'Wexner Incontinence Score':
        score=sum(st.selectbox(x,[0,1,2,3,4]) for x in ['Solid','Liquid','Gas','Pad use','Lifestyle alteration']); result=f'{score}/20'; risk='Low' if score<=4 else 'Medium' if score<=12 else 'High'; interp=f'Wexner {score}: {risk} incontinence severity.'; rec='Guide pelvic floor workup and treatment.'

    elif name == 'GCS':
        e=st.selectbox('Eye',[1,2,3,4],index=3); v=st.selectbox('Verbal',[1,2,3,4,5],index=4); m=st.selectbox('Motor',[1,2,3,4,5,6],index=5); score=e+v+m; result=f'{score}/15'; risk='Low' if score>=13 else 'Medium' if score>=9 else 'High'; interp=f'GCS {score}: {risk} head injury severity.'; rec='Protect airway and image/escalate according to trauma protocol.'

    elif name == 'RTS':
        gcs=st.selectbox('GCS coded',[0,1,2,3,4]); sbp=st.selectbox('SBP coded',[0,1,2,3,4]); rr=st.selectbox('RR coded',[0,1,2,3,4]); val=round(0.9368*gcs+0.7326*sbp+0.2908*rr,2); result=val; risk='High' if val<4 else 'Medium' if val<6 else 'Low'; interp=f'RTS {val}: trauma physiologic risk.'; rec='Use for triage, not isolated disposition.'

    elif name == 'Clavien-Dindo':
        grade=st.selectbox('Grade',['I','II','IIIa','IIIb','IV','V']); result=f'Grade {grade}'; risk='Low' if grade in ['I','II'] else 'Medium' if grade=='IIIa' else 'High'; interp=f'Clavien-Dindo Grade {grade}.'; rec='Document postoperative complication severity consistently.'

    elif name == 'CDC SSI Classification':
        cls=st.selectbox('SSI type',['Superficial incisional','Deep incisional','Organ/space']); result=cls; risk='Medium' if cls!='Organ/space' else 'High'; interp=f'CDC SSI classification: {cls}.'; rec='Treat according to depth/source control and culture when needed.'

    else:
        st.warning('Score not implemented yet.'); result='N/A'; interp='Pending implementation.'; rec=''; risk='Low'

    return result, interp, rec, risk
