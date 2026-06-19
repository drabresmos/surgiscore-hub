import math
import streamlit as st

CATEGORIES = {
    'Preoperative': ['ASA','RCRI','Caprini VTE','STOP-Bang','Clinical Frailty Scale'],
    'Emergency / ICU': ['SIRS','qSOFA','NEWS2','Shock Index'],
    'Appendix': ['Alvarado','AIR Appendicitis','RIPASA'],
    'Gallbladder / CBD': ['Tokyo Cholecystitis Grade','ASGE CBD Stone Risk','Parkland Grade'],
    'Pancreas': ['BISAP','Ranson Admission','Glasgow-Imrie'],
    'GI Bleeding': ['Glasgow-Blatchford','AIMS65','Rockall Pre-Endoscopy'],
    'Peritonitis': ['Mannheim Peritonitis Index','Boey Score'],
    'Liver / HPB': ['Child-Pugh','MELD-Na','ALBI Grade'],
    'Postoperative': ['Clavien-Dindo','CDC SSI Classification'],
}

def cb(label, pts):
    return pts if st.checkbox(f'{label} (+{pts})') else 0

def run_score(score):
    result, interp, risk = None, '', 'Low'
    if score=='ASA':
        v=st.radio('ASA Physical Status', ['ASA I - Normal healthy patient','ASA II - Mild systemic disease','ASA III - Severe systemic disease','ASA IV - Severe disease constant threat to life','ASA V - Moribund patient'])
        result=v.split(' - ')[0]; interp=v; risk='Low' if result in ['ASA I','ASA II'] else 'High'
    elif score=='RCRI':
        s=sum(cb(x,1) for x in ['High-risk surgery','Ischemic heart disease','Heart failure','Cerebrovascular disease','Insulin-dependent diabetes','Creatinine >2 mg/dL'])
        result=s; interp='Low cardiac risk' if s==0 else 'Intermediate cardiac risk' if s==1 else 'High cardiac risk'; risk='Low' if s==0 else 'Medium' if s==1 else 'High'
    elif score=='Caprini VTE':
        items={'Age 41–60':1,'Age 61–74':2,'Age ≥75':3,'Minor surgery':1,'Major surgery >45 min':2,'BMI >25':1,'Varicose veins':1,'Malignancy':2,'Bed rest >72h':2,'Central venous access':2,'Prior DVT/PE':3,'Known thrombophilia':3,'Stroke <1 month':5,'Hip/pelvis/leg fracture':5}
        s=sum(cb(k,v) for k,v in items.items()); result=s
        interp='Very low/low VTE risk' if s<=2 else 'Moderate VTE risk' if s<=4 else 'High VTE risk'; risk='Low' if s<=2 else 'Medium' if s<=4 else 'High'
    elif score=='STOP-Bang':
        s=sum(cb(x,1) for x in ['Snoring','Tiredness','Observed apnea','Pressure: hypertension','BMI >35','Age >50','Neck circumference high','Male gender'])
        result=s; interp='Low OSA risk' if s<=2 else 'Intermediate OSA risk' if s<=4 else 'High OSA risk'; risk='Low' if s<=2 else 'Medium' if s<=4 else 'High'
    elif score=='Clinical Frailty Scale':
        v=st.slider('CFS 1 Very Fit → 9 Terminally ill',1,9,3); result=v
        interp='Fit/mild frailty' if v<=4 else 'Moderate frailty' if v<=6 else 'Severe frailty'; risk='Low' if v<=4 else 'Medium' if v<=6 else 'High'
    elif score=='SIRS':
        s=sum(cb(x,1) for x in ['Temp >38 or <36','HR >90','RR >20 or PaCO2 <32','WBC >12k or <4k or bands >10%'])
        result=f'{s}/4'; interp='SIRS positive' if s>=2 else 'SIRS negative'; risk='Medium' if s>=2 else 'Low'
    elif score=='qSOFA':
        s=sum(cb(x,1) for x in ['RR ≥22/min','Altered mentation','SBP ≤100 mmHg'])
        result=f'{s}/3'; interp='High risk in suspected sepsis' if s>=2 else 'Lower risk'; risk='High' if s>=2 else 'Low'
    elif score=='NEWS2':
        s=sum(st.number_input(x,0,3,0) for x in ['Respiratory rate points','SpO2 points','Oxygen use points','Temperature points','Systolic BP points','Heart rate points','Consciousness points'])
        result=s; interp='Low NEWS2' if s<=4 else 'Medium NEWS2' if s<=6 else 'High NEWS2'; risk='Low' if s<=4 else 'Medium' if s<=6 else 'High'
    elif score=='Shock Index':
        hr=st.number_input('Heart rate',20,250,90); sbp=st.number_input('Systolic BP',40,250,120); v=round(hr/sbp,2); result=v
        interp='Normal' if v<0.7 else 'Borderline' if v<=0.9 else 'Possible shock/physiologic stress'; risk='Low' if v<0.7 else 'Medium' if v<=0.9 else 'High'
    elif score=='Alvarado':
        s=0
        for label, pts in [('Migration pain',1),('Anorexia',1),('Nausea/vomiting',1),('RIF tenderness',2),('Rebound tenderness',1),('Fever',1),('Leukocytosis',2),('Neutrophilia',1)]: s+=cb(label,pts)
        result=f'{s}/10'; interp='Unlikely' if s<=4 else 'Possible' if s<=6 else 'Probable/very probable appendicitis'; risk='Low' if s<=4 else 'Medium' if s<=6 else 'High'
    elif score=='AIR Appendicitis':
        s=cb('Vomiting',1)+st.selectbox('RIF pain/tenderness points',[0,1,2,3])+st.selectbox('Rebound/defense points',[0,1,2,3])+cb('Temp ≥38.5',1)+st.selectbox('WBC points',[0,1,2])+st.selectbox('Neutrophils points',[0,1,2])+st.selectbox('CRP points',[0,1,2])
        result=f'{s}/12'; interp='Low probability' if s<=4 else 'Intermediate probability' if s<=8 else 'High probability'; risk='Low' if s<=4 else 'Medium' if s<=8 else 'High'
    elif score=='RIPASA':
        s=sum(st.number_input(x,0.0,5.0,0.0,0.5) for x in ['Demographic points','Symptoms points','Signs points','Labs points'])
        result=s; interp='Unlikely/low' if s<7.5 else 'High probability appendicitis'; risk='Low' if s<7.5 else 'High'
    elif score=='Tokyo Cholecystitis Grade':
        organ=st.checkbox('Organ dysfunction'); moderate=any([st.checkbox('WBC >18k'),st.checkbox('Palpable tender RUQ mass'),st.checkbox('Duration >72h'),st.checkbox('Marked local inflammation')])
        result='Grade III' if organ else 'Grade II' if moderate else 'Grade I'; interp='Severe' if organ else 'Moderate' if moderate else 'Mild'; risk='High' if organ else 'Medium' if moderate else 'Low'
    elif score=='ASGE CBD Stone Risk':
        high=any([st.checkbox('CBD stone on imaging'),st.checkbox('Ascending cholangitis'),st.checkbox('Bilirubin >4 AND dilated CBD')]); inter=st.checkbox('Abnormal LFTs OR age>55 OR dilated CBD')
        result='High' if high else 'Intermediate' if inter else 'Low'; interp='ERCP usually considered' if high else 'MRCP/EUS/IOC usually considered' if inter else 'Low probability'; risk=result if result!='Intermediate' else 'Medium'
    elif score=='Parkland Grade':
        v=st.slider('Parkland cholecystitis grade 1–5',1,5,2); result=f'Grade {v}'; interp='Mild/moderate difficulty' if v<=3 else 'Severe inflammation/difficult LC'; risk='Low' if v<=2 else 'Medium' if v==3 else 'High'
    elif score=='BISAP':
        s=sum(cb(x,1) for x in ['BUN >25','Impaired mental status','SIRS','Age >60','Pleural effusion'])
        result=f'{s}/5'; interp='Lower risk' if s<3 else 'High severe pancreatitis/mortality risk'; risk='Low' if s<3 else 'High'
    elif score=='Ranson Admission':
        s=sum(cb(x,1) for x in ['Age >55','WBC >16k','Glucose >200','LDH >350','AST >250'])
        result=f'{s}/5'; interp='Mild admission criteria' if s<=2 else 'Higher severity risk'; risk='Low' if s<=2 else 'High'
    elif score=='Glasgow-Imrie':
        s=sum(cb(x,1) for x in ['PaO2 <60','Age >55','Neutrophils/WBC >15k','Calcium <8','Urea >45','LDH >600','Albumin <3.2','Glucose >180'])
        result=f'{s}/8'; interp='Severe pancreatitis likely' if s>=3 else 'Lower severity'; risk='High' if s>=3 else 'Low'
    elif score=='Glasgow-Blatchford':
        s=0; bun=st.number_input('BUN mg/dL',0.0,200.0,20.0); hb=st.number_input('Hemoglobin g/dL',0.0,25.0,12.0); sbp=st.number_input('SBP',40,250,120); pulse=st.number_input('Pulse',30,220,80)
        if bun>=28: s+=2
        if hb<12: s+=2
        if sbp<100: s+=2
        if pulse>=100: s+=1
        s+=sum(cb(x,p) for x,p in [('Melena',1),('Syncope',2),('Liver disease',2),('Cardiac failure',2)])
        result=s; interp='Very low risk' if s==0 else 'Moderate risk' if s<=5 else 'High risk'; risk='Low' if s==0 else 'Medium' if s<=5 else 'High'
    elif score=='AIMS65':
        s=sum(cb(x,1) for x in ['Albumin <3','INR >1.5','Altered mental status','SBP ≤90','Age >65'])
        result=f'{s}/5'; interp='Higher mortality risk' if s>=2 else 'Lower mortality risk'; risk='High' if s>=2 else 'Low'
    elif score=='Rockall Pre-Endoscopy':
        s=st.selectbox('Age points',[0,1,2])+st.selectbox('Shock points',[0,1,2])+st.selectbox('Comorbidity points',[0,2,3])
        result=s; interp='Low' if s<=2 else 'Moderate/high'; risk='Low' if s<=2 else 'High'
    elif score=='Mannheim Peritonitis Index':
        items={'Age >50':5,'Female sex':5,'Organ failure':7,'Malignancy':4,'Duration >24h':4,'Origin not colonic':4,'Diffuse peritonitis':6,'Purulent exudate':6,'Fecal exudate':12}
        s=sum(cb(k,v) for k,v in items.items()); result=s; interp='Lower mortality risk' if s<21 else 'Intermediate' if s<=29 else 'High mortality risk'; risk='Low' if s<21 else 'Medium' if s<=29 else 'High'
    elif score=='Boey Score':
        s=sum(cb(x,1) for x in ['Major medical illness','Preoperative shock','Perforation >24h'])
        result=f'{s}/3'; interp='Lower risk' if s<=1 else 'High risk perforated peptic ulcer'; risk='Low' if s<=1 else 'High'
    elif score=='Child-Pugh':
        s=st.selectbox('Ascites',[1,2,3])+st.selectbox('Encephalopathy',[1,2,3])+st.selectbox('Bilirubin',[1,2,3])+st.selectbox('Albumin',[1,2,3])+st.selectbox('INR',[1,2,3])
        cls='A' if s<=6 else 'B' if s<=9 else 'C'; result=f'{s} Class {cls}'; interp='Compensated' if cls=='A' else 'Significant compromise' if cls=='B' else 'Decompensated'; risk='Low' if cls=='A' else 'Medium' if cls=='B' else 'High'
    elif score=='MELD-Na':
        bili=max(st.number_input('Bilirubin',0.1,50.0,1.0),1.0); inr=max(st.number_input('INR',0.8,10.0,1.0),1.0); cr=max(st.number_input('Creatinine',0.1,15.0,1.0),1.0); na=st.number_input('Sodium',120,150,137)
        meld=round(3.78*math.log(bili)+11.2*math.log(inr)+9.57*math.log(cr)+6.43); nac=min(max(na,125),137); val=round(meld+1.32*(137-nac)-(0.033*meld*(137-nac)))
        result=val; interp='Lower' if val<10 else 'Moderate' if val<20 else 'High liver mortality risk'; risk='Low' if val<10 else 'Medium' if val<20 else 'High'
    elif score=='ALBI Grade':
        alb=st.number_input('Albumin g/L',10.0,60.0,35.0); bili=st.number_input('Bilirubin µmol/L',1.0,600.0,20.0); albi=round((math.log10(bili)*0.66)+(alb*-0.085),2)
        grade='1' if albi<=-2.60 else '2' if albi<=-1.39 else '3'; result=f'{albi} Grade {grade}'; interp='Better liver reserve' if grade=='1' else 'Intermediate' if grade=='2' else 'Poor liver reserve'; risk='Low' if grade=='1' else 'Medium' if grade=='2' else 'High'
    elif score=='Clavien-Dindo':
        v=st.selectbox('Grade',['Grade I - Minor deviation','Grade II - Pharmacological treatment','Grade IIIa - Intervention without GA','Grade IIIb - Intervention under GA','Grade IV - ICU/life-threatening','Grade V - Death'])
        result=v.split(' - ')[0]; interp=v; risk='High' if result in ['Grade IIIb','Grade IV','Grade V'] else 'Medium'
    elif score=='CDC SSI Classification':
        v=st.selectbox('SSI type',['No SSI','Superficial incisional SSI','Deep incisional SSI','Organ/space SSI'])
        result=v; interp=v; risk='Low' if v=='No SSI' else 'Medium' if 'Superficial' in v else 'High'
    else:
        st.info('This score is listed for board reference. Calculator form will be added in the next update.'); result='Reference only'; interp='Not calculated in this build'; risk='Low'
    return result, interp, risk
