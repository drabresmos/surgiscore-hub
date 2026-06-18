import math
import streamlit as st

CATEGORIES = {
    'Perioperative': ['ASA','Clinical Frailty Scale','Charlson Comorbidity Index','STOP-Bang','Caprini VTE','RCRI'],
    'Emergency / Sepsis': ['SIRS','qSOFA','NEWS2','Shock Index','SOFA Simplified'],
    'Appendicitis': ['Alvarado','AIR Appendicitis','RIPASA','Pediatric Appendicitis Score'],
    'Gallbladder / CBD': ['Tokyo Cholecystitis Grade','Tokyo Cholangitis Grade','ASGE CBD Stone Risk','Nassar Difficulty Grade','Parkland Grade','Csendes Mirizzi'],
    'Pancreas': ['BISAP','Ranson Admission','Glasgow-Imrie','Modified CT Severity Index','Atlanta Classification'],
    'GI Bleeding': ['Glasgow-Blatchford','AIMS65','Rockall Pre-Endoscopy','Oakland Lower GI Bleeding'],
    'Peritonitis / Perforation': ['Mannheim Peritonitis Index','Boey Score'],
    'Liver / HPB': ['Child-Pugh','MELD-Na','ALBI Grade'],
    'Colorectal': ['Hinchey Diverticulitis','WSES Diverticulitis','LARS Score','Wexner Incontinence Score'],
    'Trauma': ['GCS','RTS','AAST Organ Injury Grade'],
    'Postoperative': ['Clavien-Dindo','CDC SSI Classification']
}

INFO = {
 'ASA':'Global pre-anesthesia physical status. Use for every operation.',
 'Caprini VTE':'VTE risk stratification to guide thromboprophylaxis planning.',
 'RCRI':'Major perioperative cardiac event risk in non-cardiac surgery.',
 'Alvarado':'Classic appendicitis probability score.',
 'AIR Appendicitis':'Inflammatory response appendicitis score; useful with CRP/WBC.',
 'BISAP':'Early acute pancreatitis severity score within 24 hours.',
 'Glasgow-Blatchford':'Upper GI bleeding risk and need for intervention/admission.',
 'Mannheim Peritonitis Index':'Mortality risk in secondary peritonitis.',
 'Child-Pugh':'Cirrhosis severity and operative risk context.',
 'MELD-Na':'Liver disease short-term mortality estimate.',
 'Clavien-Dindo':'Postoperative complication severity classification.'
}

def cb(label, pts=1):
    return pts if st.checkbox(f'{label} (+{pts})') else 0

def risk_label(score, low=None, high=None):
    if high is not None and score >= high: return 'High'
    if low is not None and score <= low: return 'Low'
    return 'Medium'

def render_score(name):
    inputs={}
    st.markdown(f'**Use:** {INFO.get(name, "Clinical surgical score / classification.")}')

    if name=='ASA':
        v=st.radio('ASA class',['ASA I - Healthy','ASA II - Mild systemic disease','ASA III - Severe systemic disease','ASA IV - Constant threat to life','ASA V - Moribund'])
        result=v.split(' - ')[0]; risk='Low' if result in ['ASA I','ASA II'] else 'High'; return result,risk,v,{'asa':v}
    if name=='Clinical Frailty Scale':
        n=st.slider('CFS grade',1,9,3); risk='Low' if n<=3 else 'Medium' if n<=5 else 'High'; interp=f'CFS {n}: frailty increases perioperative vulnerability.'; return n,risk,interp,{'cfs':n}
    if name=='Charlson Comorbidity Index':
        score=0
        for label,pts in [('MI',1),('CHF',1),('Peripheral vascular disease',1),('CVA/TIA',1),('Dementia',1),('COPD',1),('Connective tissue disease',1),('Peptic ulcer',1),('Diabetes',1),('Diabetes with complications',2),('Renal disease',2),('Any tumor',2),('Leukemia/Lymphoma',2),('Moderate/severe liver disease',3),('Metastatic solid tumor',6)]: score+=cb(label,pts)
        age=st.number_input('Age',0,120,50); score += max(0,(age-40)//10); risk=risk_label(score,2,5); return score,risk,'Higher score reflects greater comorbidity burden.',{'score':score,'age':age}
    if name=='STOP-Bang':
        score=sum([st.checkbox(x) for x in ['Snoring','Tiredness','Observed apnea','High BP','BMI >35','Age >50','Neck circumference high','Male']]); risk='Low' if score<=2 else 'Medium' if score<=4 else 'High'; return score,risk,'Obstructive sleep apnea screening.',{'score':score}
    if name=='Caprini VTE':
        score=0
        items=[('Age 41–60',1),('Age 61–74',2),('Age ≥75',3),('Minor surgery',1),('Major surgery >45 min',2),('BMI >25',1),('Swollen legs',1),('Varicose veins',1),('Malignancy',2),('Bed rest >72h',2),('Central venous access',2),('Prior DVT/PE',3),('Known thrombophilia',3),('Stroke <1 month',5),('Hip/pelvis/leg fracture',5)]
        for l,p in items: score+=cb(l,p)
        risk='Low' if score<=2 else 'Medium' if score<=4 else 'High'; return score,risk,'VTE risk category for prophylaxis planning.',{'score':score}
    if name=='RCRI':
        score=sum([st.checkbox(x) for x in ['High-risk surgery','Ischemic heart disease','Heart failure','Cerebrovascular disease','Insulin-dependent diabetes','Creatinine >2 mg/dL']]); risk='Low' if score==0 else 'Medium' if score==1 else 'High'; return score,risk,'Perioperative cardiac risk.',{'score':score}
    if name=='SIRS':
        score=sum([st.checkbox(x) for x in ['Temp >38 or <36','HR >90','RR >20 or PaCO2 <32','WBC >12k or <4k or bands >10%']]); risk='High' if score>=2 else 'Low'; return f'{score}/4',risk,'SIRS positive if ≥2 criteria.',{'score':score}
    if name=='qSOFA':
        score=sum([st.checkbox(x) for x in ['RR ≥22','Altered mentation','SBP ≤100']]); risk='High' if score>=2 else 'Low'; return f'{score}/3',risk,'High risk in suspected infection if ≥2.',{'score':score}
    if name=='NEWS2':
        rr=st.selectbox('Respiratory rate score',[0,1,2,3]); spo2=st.selectbox('SpO2 score',[0,1,2,3]); o2=2 if st.checkbox('Supplemental oxygen') else 0; temp=st.selectbox('Temperature score',[0,1,2,3]); sbp=st.selectbox('SBP score',[0,1,2,3]); hr=st.selectbox('HR score',[0,1,2,3]); avpu=3 if st.checkbox('New confusion / VPU') else 0; score=rr+spo2+o2+temp+sbp+hr+avpu; risk='Low' if score<=4 else 'Medium' if score<=6 else 'High'; return score,risk,'Early warning score for clinical deterioration.',{'score':score}
    if name=='Shock Index':
        hr=st.number_input('HR',20,250,90); sbp=st.number_input('SBP',40,250,120); val=round(hr/sbp,2); risk='Low' if val<0.7 else 'Medium' if val<=0.9 else 'High'; return val,risk,'HR/SBP; elevated suggests shock/physiological stress.',{'hr':hr,'sbp':sbp}
    if name=='SOFA Simplified':
        score=0
        for organ in ['Respiratory','Coagulation','Liver','Cardiovascular','CNS','Renal']: score+=st.selectbox(f'{organ} SOFA subscore',[0,1,2,3,4],key=organ)
        risk='Low' if score<=5 else 'Medium' if score<=10 else 'High'; return score,risk,'Organ dysfunction burden.',{'score':score}
    if name in ['Alvarado','Pediatric Appendicitis Score']:
        score=0
        pts=[('Migration of pain',1),('Anorexia',1),('Nausea/vomiting',1),('RIF tenderness',2),('Rebound/percussion pain',1),('Fever',1),('Leukocytosis',2),('Neutrophilia',1)]
        for l,p in pts: score+=cb(l,p)
        risk='Low' if score<=4 else 'Medium' if score<=6 else 'High'; return f'{score}/10',risk,'Appendicitis probability.',{'score':score}
    if name=='AIR Appendicitis':
        score=0; score+=cb('Vomiting',1); score+=st.selectbox('RIF tenderness',[0,1,2,3]); score+=st.selectbox('Rebound/defense',[0,1,2,3]); score+=cb('Temp ≥38.5',1); score+=st.selectbox('WBC points',[0,1,2]); score+=st.selectbox('Neutrophils points',[0,1,2]); score+=st.selectbox('CRP points',[0,1,2]); risk='Low' if score<=4 else 'Medium' if score<=8 else 'High'; return f'{score}/12',risk,'AIR appendicitis probability.',{'score':score}
    if name=='RIPASA':
        score=0.0
        for l,p in [('Male',1),('Female',0.5),('Age <40',1),('RIF pain',0.5),('Migration to RIF',0.5),('Anorexia',1),('Nausea/vomiting',1),('Duration <48h',1),('RIF tenderness',1),('Guarding',2),('Rebound',1),('Rovsing',2),('Fever',1),('Raised WBC',1),('Negative urinalysis',1)]:
            if st.checkbox(f'{l} (+{p})'): score+=p
        risk='Low' if score<5 else 'Medium' if score<7.5 else 'High'; return score,risk,'RIPASA appendicitis probability.',{'score':score}
    if name=='Tokyo Cholecystitis Grade':
        organ=st.checkbox('Organ dysfunction'); moderate=sum([st.checkbox(x) for x in ['WBC >18k','Palpable tender RUQ mass','Symptoms >72h','Marked local inflammation']]);
        result='Grade III' if organ else 'Grade II' if moderate else 'Grade I'; risk='High' if result=='Grade III' else 'Medium' if result=='Grade II' else 'Low'; return result,risk,'Acute cholecystitis severity.',{'result':result}
    if name=='Tokyo Cholangitis Grade':
        organ=st.checkbox('Organ dysfunction'); mod=sum([st.checkbox(x) for x in ['Abnormal WBC','High fever','Age ≥75','Bilirubin ≥5','Hypoalbuminemia']]); result='Grade III' if organ else 'Grade II' if mod>=2 else 'Grade I'; risk='High' if result=='Grade III' else 'Medium' if result=='Grade II' else 'Low'; return result,risk,'Acute cholangitis severity.',{'result':result}
    if name=='ASGE CBD Stone Risk':
        high=st.checkbox('CBD stone on imaging') or st.checkbox('Ascending cholangitis') or st.checkbox('Bilirubin >4 + dilated CBD'); inter=st.checkbox('Abnormal LFTs / age >55 / dilated CBD alone'); result='High' if high else 'Intermediate' if inter else 'Low'; risk={'High':'High','Intermediate':'Medium','Low':'Low'}[result]; return result,risk,'CBD stone probability category.',{'result':result}
    if name=='Nassar Difficulty Grade':
        g=st.selectbox('Nassar grade',['Grade 1 Easy','Grade 2 Mild difficulty','Grade 3 Moderate difficulty','Grade 4 Severe difficulty','Grade 5 Extreme difficulty']); risk='Low' if '1' in g or '2' in g else 'Medium' if '3' in g else 'High'; return g,risk,'Laparoscopic cholecystectomy difficulty.',{'grade':g}
    if name=='Parkland Grade':
        g=st.slider('Parkland cholecystitis grade',1,5,2); risk='Low' if g<=2 else 'Medium' if g==3 else 'High'; return g,risk,'Operative inflammation severity.',{'grade':g}
    if name=='Csendes Mirizzi':
        t=st.selectbox('Type',['Type I external compression','Type II fistula <1/3 CBD','Type III fistula 1/3–2/3 CBD','Type IV complete CBD destruction','Type V cholecystoenteric fistula']); risk='Low' if t.startswith('Type I') else 'Medium' if t.startswith('Type II') else 'High'; return t,risk,'Mirizzi classification.',{'type':t}
    if name=='BISAP':
        score=sum([st.checkbox(x) for x in ['BUN >25','Impaired mental status','SIRS','Age >60','Pleural effusion']]); risk='High' if score>=3 else 'Low'; return f'{score}/5',risk,'Early pancreatitis severity.',{'score':score}
    if name=='Ranson Admission':
        score=sum([st.checkbox(x) for x in ['Age >55','WBC >16k','Glucose >200','LDH >350','AST >250']]); risk='High' if score>=3 else 'Low'; return f'{score}/5',risk,'Admission Ranson criteria.',{'score':score}
    if name=='Glasgow-Imrie':
        score=sum([st.checkbox(x) for x in ['PaO2 <60','Age >55','Neutrophils/WBC >15k','Calcium <8','Urea >45 mg/dL','LDH >600','Albumin <3.2','Glucose >180']]); risk='High' if score>=3 else 'Low'; return score,risk,'Severe pancreatitis if ≥3.',{'score':score}
    if name=='Modified CT Severity Index':
        infl=st.selectbox('Pancreatic inflammation',[0,2,4]); nec=st.selectbox('Necrosis',[0,2,4]); extra=st.selectbox('Extrapancreatic complications',[0,2]); score=infl+nec+extra; risk='Low' if score<=2 else 'Medium' if score<=6 else 'High'; return f'{score}/10',risk,'CT pancreatitis severity.',{'score':score}
    if name=='Atlanta Classification':
        g=st.selectbox('Atlanta class',['Mild','Moderately severe','Severe']); risk='Low' if g=='Mild' else 'Medium' if g.startswith('Moderately') else 'High'; return g,risk,'Acute pancreatitis clinical severity.',{'class':g}
    if name=='Glasgow-Blatchford':
        score=0; score+=st.selectbox('BUN points',[0,2,3,4,6]); score+=st.selectbox('Hb points',[0,1,3,6]); score+=st.selectbox('SBP points',[0,1,2,3]); score+=cb('Pulse ≥100',1); score+=cb('Melena',1); score+=cb('Syncope',2); score+=cb('Liver disease',2); score+=cb('Heart failure',2); risk='Low' if score==0 else 'Medium' if score<=5 else 'High'; return score,risk,'Upper GI bleeding intervention/admission risk.',{'score':score}
    if name=='AIMS65':
        score=sum([st.checkbox(x) for x in ['Albumin <3.0','INR >1.5','Altered mental status','SBP ≤90','Age >65']]); risk='High' if score>=2 else 'Low'; return f'{score}/5',risk,'UGIB mortality risk.',{'score':score}
    if name=='Rockall Pre-Endoscopy':
        score=st.selectbox('Age points',[0,1,2])+st.selectbox('Shock points',[0,1,2])+st.selectbox('Comorbidity points',[0,2,3]); risk='Low' if score<=2 else 'Medium' if score<=4 else 'High'; return score,risk,'Pre-endoscopy UGIB risk.',{'score':score}
    if name=='Oakland Lower GI Bleeding':
        score=st.number_input('Oakland total score',0,50,8); risk='Low' if score<=8 else 'Medium' if score<=15 else 'High'; return score,risk,'LGIB safe discharge probability context.',{'score':score}
    if name=='Mannheim Peritonitis Index':
        score=0
        for l,p in [('Age >50',5),('Female',5),('Organ failure',7),('Malignancy',4),('Duration >24h',4),('Non-colonic origin',4),('Diffuse peritonitis',6),('Cloudy/purulent exudate',6),('Fecal exudate',12)]: score+=cb(l,p)
        risk='Low' if score<21 else 'Medium' if score<=29 else 'High'; return score,risk,'Peritonitis mortality risk.',{'score':score}
    if name=='Boey Score':
        score=sum([st.checkbox(x) for x in ['Major medical illness','Preoperative shock','Perforation >24h']]); risk='High' if score>=2 else 'Low'; return f'{score}/3',risk,'Perforated peptic ulcer risk.',{'score':score}
    if name=='Child-Pugh':
        score=st.selectbox('Ascites',[1,2,3])+st.selectbox('Encephalopathy',[1,2,3])+st.selectbox('Bilirubin',[1,2,3])+st.selectbox('Albumin',[1,2,3])+st.selectbox('INR/PT',[1,2,3]); cls='A' if score<=6 else 'B' if score<=9 else 'C'; risk='Low' if cls=='A' else 'Medium' if cls=='B' else 'High'; return f'{score} Class {cls}',risk,'Cirrhosis severity.',{'score':score,'class':cls}
    if name=='MELD-Na':
        bili=st.number_input('Bilirubin',0.1,60.0,1.0); inr=st.number_input('INR',0.8,10.0,1.0); cr=st.number_input('Creatinine',0.1,15.0,1.0); na=st.number_input('Sodium',120,150,137); meld=round(3.78*math.log(max(bili,1))+11.2*math.log(max(inr,1))+9.57*math.log(max(cr,1))+6.43); nac=min(max(na,125),137); meldna=round(meld+1.32*(137-nac)-0.033*meld*(137-nac)); risk='Low' if meldna<10 else 'Medium' if meldna<20 else 'High'; return meldna,risk,'Liver disease mortality estimate.',{'meldna':meldna}
    if name=='ALBI Grade':
        alb=st.number_input('Albumin g/L',10.0,60.0,35.0); bili=st.number_input('Bilirubin µmol/L',1.0,800.0,20.0); val=round((math.log10(bili)*0.66)+(alb*-0.085),2); grade='Grade 1' if val<=-2.60 else 'Grade 2' if val<=-1.39 else 'Grade 3'; risk='Low' if grade=='Grade 1' else 'Medium' if grade=='Grade 2' else 'High'; return f'{val} / {grade}',risk,'Albumin-bilirubin liver function grade.',{'albi':val,'grade':grade}
    if name=='Hinchey Diverticulitis':
        h=st.selectbox('Hinchey',['Ia phlegmon','Ib pericolic abscess','II pelvic/distant abscess','III purulent peritonitis','IV fecal peritonitis']); risk='Low' if h.startswith('Ia') else 'Medium' if h.startswith('Ib') or h.startswith('II') else 'High'; return h,risk,'Complicated diverticulitis stage.',{'stage':h}
    if name=='WSES Diverticulitis':
        g=st.selectbox('WSES grade',['0 uncomplicated','1A pericolic air/fluid','1B abscess ≤4cm','2A abscess >4cm','2B distant gas','3 diffuse fluid no distant gas','4 diffuse fluid with distant gas']); risk='Low' if g[0]=='0' else 'Medium' if g[0] in ['1','2'] else 'High'; return g,risk,'WSES diverticulitis severity.',{'grade':g}
    if name=='LARS Score':
        score=0
        for l,p in [('Incontinence for flatus',7),('Incontinence for liquid stool',3),('Frequency >7/day',4),('Clustering',11),('Urgency',16)]: score+=cb(l,p)
        risk='Low' if score<=20 else 'Medium' if score<=29 else 'High'; return score,risk,'Low anterior resection syndrome severity.',{'score':score}
    if name=='Wexner Incontinence Score':
        score=sum([st.slider(x,0,4,0) for x in ['Solid','Liquid','Gas','Wears pad','Lifestyle alteration']]); risk='Low' if score<=5 else 'Medium' if score<=12 else 'High'; return f'{score}/20',risk,'Fecal incontinence severity.',{'score':score}
    if name=='GCS':
        e=st.selectbox('Eye',[4,3,2,1]); v=st.selectbox('Verbal',[5,4,3,2,1]); m=st.selectbox('Motor',[6,5,4,3,2,1]); score=e+v+m; risk='Low' if score>=13 else 'Medium' if score>=9 else 'High'; return score,risk,'Glasgow Coma Scale.',{'score':score}
    if name=='RTS':
        g=st.selectbox('GCS coded',[4,3,2,1,0]); sbp=st.selectbox('SBP coded',[4,3,2,1,0]); rr=st.selectbox('RR coded',[4,3,2,1,0]); val=round(0.9368*g+0.7326*sbp+0.2908*rr,2); risk='Low' if val>7 else 'Medium' if val>5 else 'High'; return val,risk,'Revised Trauma Score.',{'rts':val}
    if name=='AAST Organ Injury Grade':
        organ=st.selectbox('Organ',['Spleen','Liver','Kidney','Pancreas','Duodenum','Colon']); grade=st.slider('AAST grade',1,5,2); risk='Low' if grade<=2 else 'Medium' if grade==3 else 'High'; return f'{organ} Grade {grade}',risk,'AAST anatomical injury grade.',{'organ':organ,'grade':grade}
    if name=='Clavien-Dindo':
        g=st.selectbox('Grade',['Grade I','Grade II','Grade IIIa','Grade IIIb','Grade IVa/IVb','Grade V']); risk='Low' if g in ['Grade I','Grade II'] else 'Medium' if g=='Grade IIIa' else 'High'; return g,risk,'Postoperative complication severity.',{'grade':g}
    if name=='CDC SSI Classification':
        g=st.selectbox('SSI type',['No SSI','Superficial incisional','Deep incisional','Organ/space']); risk='Low' if g=='No SSI' else 'Medium' if g=='Superficial incisional' else 'High'; return g,risk,'Surgical site infection classification.',{'type':g}
    return 'N/A','Low','Score not implemented.',{}
