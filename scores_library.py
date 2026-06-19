import math
import streamlit as st

CATEGORIES = {
    'Perioperative': ['ASA','Clinical Frailty Scale','Charlson Comorbidity Index','STOP-Bang','Caprini VTE','RCRI'],
    'Emergency / Sepsis': ['SIRS','qSOFA','NEWS2','Shock Index','SOFA Simplified'],
    'Appendicitis': ['Alvarado','AIR Appendicitis','RIPASA','Pediatric Appendicitis Score'],
    'Gallbladder / CBD': ['Tokyo Cholecystitis Grade','Tokyo Cholangitis Grade','ASGE CBD Stone Risk','Nassar Difficulty Grade','Parkland Cholecystitis Grade','Csendes Mirizzi Classification'],
    'Pancreas': ['BISAP','Ranson Admission','Glasgow-Imrie Pancreatitis','Modified CT Severity Index','Atlanta Pancreatitis Classification'],
    'GI Bleeding': ['Glasgow-Blatchford','AIMS65','Rockall Pre-Endoscopy','Oakland Lower GI Bleeding'],
    'Peritonitis / Perforation': ['Mannheim Peritonitis Index','Boey Score'],
    'Liver / HPB': ['Child-Pugh','MELD-Na','ALBI Grade'],
    'Colorectal': ['Hinchey Diverticulitis','WSES Diverticulitis Classification','LARS Score','Wexner Incontinence Score'],
    'Trauma': ['GCS','RTS','AAST Organ Injury Grade'],
    'Postoperative': ['Clavien-Dindo','CDC SSI Classification']
}

SCORE_INFO = {
    'ASA':'Baseline anesthetic fitness. Use for every operative patient.',
    'Caprini VTE':'VTE risk stratification and thromboprophylaxis planning.',
    'RCRI':'Major cardiac event risk in non-cardiac surgery.',
    'Alvarado':'Clinical probability of acute appendicitis.',
    'BISAP':'Early acute pancreatitis severity.',
    'Glasgow-Blatchford':'Need for intervention/admission in upper GI bleeding.',
}

def cb(label, points=1):
    return points if st.checkbox(f'{label} (+{points})') else 0

def render_score(name):
    st.caption(SCORE_INFO.get(name, 'Educational scoring aid. Interpret with clinical judgment.'))

    if name=='ASA':
        val=st.radio('ASA class', ['ASA I - Healthy','ASA II - Mild systemic disease','ASA III - Severe systemic disease','ASA IV - Constant threat to life','ASA V - Moribund'])
        result=val.split(' - ')[0]; risk='Low' if result in ['ASA I','ASA II'] else ('Medium' if result=='ASA III' else 'High')
        return result,val,risk

    if name=='Clinical Frailty Scale':
        result=st.selectbox('CFS', ['1 Very fit','2 Well','3 Managing well','4 Vulnerable','5 Mildly frail','6 Moderately frail','7 Severely frail','8 Very severely frail','9 Terminally ill'])
        n=int(result[0]); risk='Low' if n<=3 else ('Medium' if n<=5 else 'High')
        return n,result,risk

    if name=='Charlson Comorbidity Index':
        score=0
        for item,pts in [('MI',1),('CHF',1),('Peripheral vascular disease',1),('CVA/TIA',1),('Dementia',1),('COPD',1),('Connective tissue disease',1),('Peptic ulcer disease',1),('Mild liver disease',1),('Diabetes',1),('Diabetes with end-organ damage',2),('Hemiplegia',2),('Moderate/severe renal disease',2),('Any tumor',2),('Leukemia',2),('Lymphoma',2),('Moderate/severe liver disease',3),('Metastatic solid tumor',6),('AIDS',6)]:
            score += cb(item,pts)
        risk='Low' if score<=2 else ('Medium' if score<=5 else 'High')
        return score, 'Higher score indicates higher comorbidity burden.', risk

    if name=='STOP-Bang':
        score=0
        for item in ['Snoring','Tiredness','Observed apnea','High blood pressure','BMI >35','Age >50','Neck circumference >40 cm','Male sex']:
            score += cb(item,1)
        risk='Low' if score<=2 else ('Medium' if score<=4 else 'High')
        return f'{score}/8', 'OSA risk screening.', risk

    if name=='Caprini VTE':
        score=0
        for item,pts in [('Age 41-60',1),('Age 61-74',2),('Age ≥75',3),('Minor surgery',1),('Major surgery >45 min',2),('BMI >25',1),('Swollen legs',1),('Varicose veins',1),('Pregnancy/postpartum',1),('History of malignancy',2),('Bed rest >72h',2),('Central venous access',2),('Prior DVT/PE',3),('Known thrombophilia',3),('Stroke <1 month',5),('Hip/pelvis/leg fracture',5),('Elective lower limb arthroplasty',5)]:
            score += cb(item,pts)
        risk='Low' if score<=2 else ('Medium' if score<=4 else 'High')
        return score, 'VTE risk: 0-2 low, 3-4 moderate, ≥5 high.', risk

    if name=='RCRI':
        score=sum(cb(x,1) for x in ['High-risk surgery','Ischemic heart disease','Heart failure','Cerebrovascular disease','Insulin-dependent diabetes','Creatinine >2 mg/dL'])
        risk='Low' if score==0 else ('Medium' if score==1 else 'High')
        return score, 'Cardiac risk increases with score.', risk

    if name=='SIRS':
        score=sum(cb(x,1) for x in ['Temp >38 or <36','HR >90','RR >20 or PaCO2 <32','WBC >12k, <4k, or bands >10%'])
        risk='High' if score>=2 else 'Low'
        return f'{score}/4', 'SIRS positive if ≥2.', risk

    if name=='qSOFA':
        score=sum(cb(x,1) for x in ['RR ≥22/min','Altered mentation','SBP ≤100 mmHg'])
        risk='High' if score>=2 else 'Low'
        return f'{score}/3', 'High risk in suspected infection if ≥2.', risk

    if name=='NEWS2':
        rr=st.selectbox('Respiratory rate', ['12-20','9-11','21-24','≤8 or ≥25'])
        spo2=st.selectbox('SpO2', ['≥96','94-95','92-93','≤91'])
        sbp=st.selectbox('Systolic BP', ['111-219','101-110','91-100','≤90 or ≥220'])
        pulse=st.selectbox('Pulse', ['51-90','41-50 or 91-110','111-130','≤40 or ≥131'])
        consciousness=st.checkbox('New confusion / AVPU not alert')
        temp=st.selectbox('Temperature', ['36.1-38.0','35.1-36.0 or 38.1-39.0','≤35.0 or ≥39.1'])
        score={'12-20':0,'9-11':1,'21-24':2,'≤8 or ≥25':3}[rr]+{'≥96':0,'94-95':1,'92-93':2,'≤91':3}[spo2]+{'111-219':0,'101-110':1,'91-100':2,'≤90 or ≥220':3}[sbp]+{'51-90':0,'41-50 or 91-110':1,'111-130':2,'≤40 or ≥131':3}[pulse]+(3 if consciousness else 0)+{'36.1-38.0':0,'35.1-36.0 or 38.1-39.0':1,'≤35.0 or ≥39.1':3}[temp]
        risk='Low' if score<=4 else ('Medium' if score<=6 else 'High')
        return score, 'Early warning score for acute deterioration.', risk

    if name=='Shock Index':
        hr=st.number_input('Heart rate',20,250,90); sbp=st.number_input('Systolic BP',40,250,120)
        val=round(hr/sbp,2); risk='Low' if val<0.7 else ('Medium' if val<=0.9 else 'High')
        return val, 'HR/SBP. >0.9 suggests shock/physiologic stress.', risk

    if name=='SOFA Simplified':
        score=0
        score += st.selectbox('Respiration points', [0,1,2,3,4])
        score += st.selectbox('Coagulation points', [0,1,2,3,4])
        score += st.selectbox('Liver points', [0,1,2,3,4])
        score += st.selectbox('Cardiovascular points', [0,1,2,3,4])
        score += st.selectbox('CNS points', [0,1,2,3,4])
        score += st.selectbox('Renal points', [0,1,2,3,4])
        risk='Low' if score<=5 else ('Medium' if score<=10 else 'High')
        return score, 'Simplified organ dysfunction sum. Use full SOFA in ICU.', risk

    if name=='Alvarado':
        score=0
        for item,pts in [('Migration pain',1),('Anorexia',1),('Nausea/vomiting',1),('RIF tenderness',2),('Rebound tenderness',1),('Fever',1),('Leukocytosis',2),('Neutrophilia',1)]: score+=cb(item,pts)
        risk='Low' if score<=4 else ('Medium' if score<=6 else 'High')
        return f'{score}/10', 'Appendicitis unlikely ≤4, possible 5-6, probable ≥7.', risk

    if name=='AIR Appendicitis':
        score=0
        score+=cb('Vomiting',1)
        score+=st.selectbox('RIF tenderness points',[0,1,2,3])
        score+=st.selectbox('Rebound/defense points',[0,1,2,3])
        score+=cb('Temp ≥38.5',1)
        score+=st.selectbox('WBC points',[0,1,2])
        score+=st.selectbox('Neutrophils points',[0,1,2])
        score+=st.selectbox('CRP points',[0,1,2])
        risk='Low' if score<=4 else ('Medium' if score<=8 else 'High')
        return f'{score}/12', 'AIR appendicitis probability.', risk

    if name=='RIPASA':
        score=0.0
        for item,pts in [('Male',1),('Female',0.5),('Age <40',1),('RIF pain',0.5),('Migration to RIF',0.5),('Anorexia',1),('Nausea/vomiting',1),('Duration <48h',1),('RIF tenderness',1),('Guarding',2),('Rebound',1),('Rovsing sign',2),('Fever',1),('Raised WBC',1),('Negative urine analysis',1)]:
            if st.checkbox(f'{item} (+{pts})'): score+=pts
        risk='Low' if score<7.5 else 'High'
        return score, 'RIPASA ≥7.5 supports appendicitis.', risk

    if name=='Pediatric Appendicitis Score':
        score=0
        for item,pts in [('Anorexia',1),('Nausea/vomiting',1),('Migration pain',1),('Fever',1),('RIF tenderness',2),('Cough/percussion/hopping tenderness',2),('Leukocytosis',1),('Neutrophilia',1)]: score+=cb(item,pts)
        risk='Low' if score<=3 else ('Medium' if score<=6 else 'High')
        return f'{score}/10', 'Pediatric appendicitis probability.', risk

    if name=='Tokyo Cholecystitis Grade':
        organ=st.checkbox('Organ dysfunction')
        moderate=any([st.checkbox('WBC >18,000'),st.checkbox('Palpable tender RUQ mass'),st.checkbox('Duration >72h'),st.checkbox('Marked local inflammation/gangrene/abscess/peritonitis')])
        if organ: return 'Grade III','Severe acute cholecystitis.','High'
        if moderate: return 'Grade II','Moderate acute cholecystitis.','Medium'
        return 'Grade I','Mild acute cholecystitis.','Low'

    if name=='Tokyo Cholangitis Grade':
        organ=st.checkbox('Organ dysfunction')
        moderate=sum(cb(x,1) for x in ['Age ≥75','High fever','WBC abnormal','Bilirubin ≥5 mg/dL','Hypoalbuminemia'])
        if organ: return 'Grade III','Severe cholangitis.','High'
        if moderate>=2: return 'Grade II','Moderate cholangitis.','Medium'
        return 'Grade I','Mild cholangitis.','Low'

    if name=='ASGE CBD Stone Risk':
        high=any([st.checkbox('CBD stone on imaging'),st.checkbox('Ascending cholangitis'),st.checkbox('Bilirubin >4 mg/dL AND dilated CBD')])
        inter=any([st.checkbox('Abnormal LFT'),st.checkbox('Age >55'),st.checkbox('Dilated CBD alone')])
        if high: return 'High','High probability CBD stone; ERCP usually considered.','High'
        if inter: return 'Intermediate','MRCP/EUS/IOC usually considered.','Medium'
        return 'Low','Low probability CBD stone.','Low'

    if name in ['Nassar Difficulty Grade','Parkland Cholecystitis Grade','Csendes Mirizzi Classification','Hinchey Diverticulitis','WSES Diverticulitis Classification','Modified CT Severity Index','Atlanta Pancreatitis Classification','AAST Organ Injury Grade','CDC SSI Classification','Clavien-Dindo']:
        options={
        'Nassar Difficulty Grade':['Grade 1 Easy','Grade 2 Mild difficulty','Grade 3 Moderate difficulty','Grade 4 Severe difficulty','Grade 5 Extreme difficulty'],
        'Parkland Cholecystitis Grade':['Grade 1 Normal','Grade 2 Minor adhesions','Grade 3 Hyperemia/fluid','Grade 4 Extensive adhesions/obscured','Grade 5 Perforation/necrosis/unable to visualize'],
        'Csendes Mirizzi Classification':['Type I External compression','Type II fistula <1/3 CBD','Type III fistula 1/3-2/3 CBD','Type IV complete CBD destruction','Type V cholecystoenteric fistula'],
        'Hinchey Diverticulitis':['Ia Phlegmon','Ib Pericolic abscess','II Pelvic/distant abscess','III Purulent peritonitis','IV Fecal peritonitis'],
        'WSES Diverticulitis Classification':['0 Uncomplicated','1A Pericolic air/fluid','1B Abscess ≤4 cm','2A Abscess >4 cm','2B Distant air','3 Diffuse fluid no distant free air','4 Diffuse fluid with distant free air'],
        'Modified CT Severity Index':['0-2 Mild','4-6 Moderate','8-10 Severe'],
        'Atlanta Pancreatitis Classification':['Mild','Moderately severe','Severe persistent organ failure'],
        'AAST Organ Injury Grade':['Grade I','Grade II','Grade III','Grade IV','Grade V'],
        'CDC SSI Classification':['Superficial incisional SSI','Deep incisional SSI','Organ/space SSI'],
        'Clavien-Dindo':['Grade I','Grade II','Grade IIIa','Grade IIIb','Grade IVa/b','Grade V']}
        val=st.selectbox('Classification', options[name])
        risk='Low' if any(x in val for x in ['1','I','Mild','Superficial','0']) else ('High' if any(x in val for x in ['4','5','IV','V','Severe','Organ']) else 'Medium')
        return val, 'Classification selected.', risk

    if name=='BISAP':
        score=sum(cb(x,1) for x in ['BUN >25 mg/dL','Impaired mental status','SIRS present','Age >60','Pleural effusion'])
        risk='High' if score>=3 else 'Low'
        return f'{score}/5','Acute pancreatitis severity.',risk

    if name=='Ranson Admission':
        score=sum(cb(x,1) for x in ['Age >55','WBC >16,000','Glucose >200','LDH >350','AST >250'])
        risk='Low' if score<=2 else 'High'
        return f'{score}/5','Admission criteria only.',risk

    if name=='Glasgow-Imrie Pancreatitis':
        score=sum(cb(x,1) for x in ['PaO2 <60','Age >55','Neutrophils/WBC >15k','Calcium <8 mg/dL','Urea >45 mg/dL','LDH >600','Albumin <3.2 g/dL','Glucose >180 mg/dL'])
        risk='High' if score>=3 else 'Low'
        return score,'Severe pancreatitis if ≥3.',risk

    if name=='Glasgow-Blatchford':
        score=0
        bun=st.number_input('BUN mg/dL',0.0,200.0,20.0); hb=st.number_input('Hemoglobin g/dL',0.0,25.0,12.0); sbp=st.number_input('SBP',40,250,120); pulse=st.number_input('Pulse',30,220,80)
        if bun>=28: score+=2
        if hb<12: score+=2
        if sbp<100: score+=2
        if pulse>=100: score+=1
        score+=sum(cb(x,p) for x,p in [('Melena',1),('Syncope',2),('Liver disease',2),('Cardiac failure',2)])
        risk='Low' if score==0 else ('Medium' if score<=5 else 'High')
        return score,'Simplified GBS.',risk

    if name=='AIMS65':
        score=sum(cb(x,1) for x in ['Albumin <3.0','INR >1.5','Altered mental status','SBP ≤90','Age >65'])
        risk='Low' if score<=1 else ('Medium' if score==2 else 'High')
        return f'{score}/5','Upper GI bleeding mortality risk.',risk

    if name=='Rockall Pre-Endoscopy':
        score=0
        score+=st.selectbox('Age points',[0,1,2])
        score+=st.selectbox('Shock points',[0,1,2])
        score+=st.selectbox('Comorbidity points',[0,2,3])
        risk='Low' if score<=2 else ('Medium' if score<=4 else 'High')
        return score,'Pre-endoscopy Rockall.',risk

    if name=='Oakland Lower GI Bleeding':
        age=st.number_input('Age',0,120,50); sex=st.selectbox('Sex',['Male','Female']); prev=st.checkbox('Previous LGIB admission'); pr=st.checkbox('PR blood'); hr=st.number_input('HR',30,220,80); sbp=st.number_input('SBP',40,250,120); hb=st.number_input('Hb g/dL',0.0,25.0,12.0)
        score=(age//10)+(1 if sex=='Male' else 0)+(1 if prev else 0)+(1 if pr else 0)+(2 if hr>=100 else 0)+(2 if sbp<100 else 0)+(3 if hb<10 else 0)
        risk='Low' if score<=8 else ('Medium' if score<=12 else 'High')
        return score,'Simplified Oakland score; low score suggests safer discharge pathway.',risk

    if name=='Mannheim Peritonitis Index':
        score=0
        for item,pts in [('Age >50',5),('Female sex',5),('Organ failure',7),('Malignancy',4),('Duration >24h',4),('Non-colonic origin',4),('Diffuse peritonitis',6),('Cloudy/purulent exudate',6),('Fecal exudate',12)]: score+=cb(item,pts)
        risk='Low' if score<21 else ('Medium' if score<=29 else 'High')
        return score,'Peritonitis mortality risk.',risk

    if name=='Boey Score':
        score=sum(cb(x,1) for x in ['Major medical illness','Preoperative shock','Perforation >24h'])
        risk='Low' if score<=1 else 'High'
        return f'{score}/3','Perforated peptic ulcer risk.',risk

    if name=='Child-Pugh':
        score={'None':1,'Mild':2,'Moderate/Severe':3}[st.selectbox('Ascites',['None','Mild','Moderate/Severe'])]+{'None':1,'Grade I-II':2,'Grade III-IV':3}[st.selectbox('Encephalopathy',['None','Grade I-II','Grade III-IV'])]+{'<2':1,'2-3':2,'>3':3}[st.selectbox('Bilirubin',['<2','2-3','>3'])]+{'>3.5':1,'2.8-3.5':2,'<2.8':3}[st.selectbox('Albumin',['>3.5','2.8-3.5','<2.8'])]+{'<1.7':1,'1.7-2.3':2,'>2.3':3}[st.selectbox('INR',['<1.7','1.7-2.3','>2.3'])]
        cls='A' if score<=6 else ('B' if score<=9 else 'C'); risk='Low' if cls=='A' else ('Medium' if cls=='B' else 'High')
        return f'{score} Class {cls}','Cirrhosis surgical risk aid.',risk

    if name=='MELD-Na':
        bili=max(st.number_input('Bilirubin',0.1,50.0,1.0),1.0); inr=max(st.number_input('INR',0.8,10.0,1.0),1.0); cr=max(st.number_input('Creatinine',0.1,15.0,1.0),1.0); na=st.number_input('Sodium',120,150,137)
        meld=round(3.78*math.log(bili)+11.2*math.log(inr)+9.57*math.log(cr)+6.43); nac=min(max(na,125),137); meldna=round(meld+1.32*(137-nac)-0.033*meld*(137-nac))
        risk='Low' if meldna<10 else ('Medium' if meldna<20 else 'High')
        return meldna,'MELD-Na estimate.',risk

    if name=='ALBI Grade':
        alb=st.number_input('Albumin g/L',10.0,60.0,35.0); bili=st.number_input('Bilirubin µmol/L',1.0,700.0,20.0)
        val=round((math.log10(bili)*0.66)+(alb*-0.085),2)
        grade='Grade 1' if val<=-2.60 else ('Grade 2' if val<=-1.39 else 'Grade 3'); risk='Low' if grade=='Grade 1' else ('Medium' if grade=='Grade 2' else 'High')
        return f'{val} / {grade}','Liver function score.',risk

    if name=='LARS Score':
        score=0
        score+=st.selectbox('Incontinence for flatus',[0,4,7])
        score+=st.selectbox('Incontinence for liquid stool',[0,3,3])
        score+=st.selectbox('Frequency',[0,4,5])
        score+=st.selectbox('Clustering',[0,9,11])
        score+=st.selectbox('Urgency',[0,11,16])
        risk='Low' if score<=20 else ('Medium' if score<=29 else 'High')
        return score,'Low anterior resection syndrome severity.',risk

    if name=='Wexner Incontinence Score':
        score=sum(st.selectbox(x,[0,1,2,3,4]) for x in ['Solid stool','Liquid stool','Gas','Pad use','Lifestyle alteration'])
        risk='Low' if score<=7 else ('Medium' if score<=14 else 'High')
        return f'{score}/20','Fecal incontinence severity.',risk

    if name=='GCS':
        e=st.selectbox('Eye',[4,3,2,1]); v=st.selectbox('Verbal',[5,4,3,2,1]); m=st.selectbox('Motor',[6,5,4,3,2,1]); score=e+v+m
        risk='Low' if score>=13 else ('Medium' if score>=9 else 'High')
        return f'{score}/15','Consciousness level.',risk

    if name=='RTS':
        gcs=st.selectbox('GCS coded',[4,3,2,1,0]); sbp=st.selectbox('SBP coded',[4,3,2,1,0]); rr=st.selectbox('RR coded',[4,3,2,1,0]); val=round(0.9368*gcs+0.7326*sbp+0.2908*rr,2)
        risk='Low' if val>6 else ('Medium' if val>4 else 'High')
        return val,'Revised Trauma Score.',risk

    return 'N/A','Score renderer not implemented yet.','Medium'
