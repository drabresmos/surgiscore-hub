import math
import streamlit as st
from styles import risk_label
from data import SCORE_DESCRIPTIONS

def _cb(label, pts=1): return pts if st.checkbox(f"{label} (+{pts})") else 0

def render_score(score_name):
    st.caption(SCORE_DESCRIPTIONS.get(score_name, "Clinical score."))
    result, interp, risk = None, "", "Low"
    if score_name == "ASA":
        v=st.selectbox("ASA Physical Status", ["ASA I","ASA II","ASA III","ASA IV","ASA V"]); result=v; interp=f"{v} selected"; risk="Low" if v in ["ASA I","ASA II"] else "High"
    elif score_name == "Caprini VTE":
        s=sum([_cb("Age 41–60",1),_cb("Age 61–74",2),_cb("Age ≥75",3),_cb("Minor surgery",1),_cb("Major surgery >45 min",2),_cb("BMI >25",1),_cb("Cancer",2),_cb("Bed rest >72h",2),_cb("Prior DVT/PE",3),_cb("Known thrombophilia",3),_cb("Stroke <1 month",5),_cb("Hip/pelvis/leg fracture",5)])
        result=s; interp="Very low/low VTE risk" if s<=2 else "Moderate VTE risk" if s<=4 else "High VTE risk"; risk="Low" if s<=2 else "Medium" if s<=4 else "High"
    elif score_name == "RCRI":
        s=sum([_cb("High-risk surgery"),_cb("Ischemic heart disease"),_cb("Heart failure"),_cb("Cerebrovascular disease"),_cb("Insulin-dependent diabetes"),_cb("Creatinine >2 mg/dL")]); result=s; interp="Low cardiac risk" if s==0 else "Intermediate cardiac risk" if s==1 else "High cardiac risk"; risk="Low" if s==0 else "Medium" if s==1 else "High"
    elif score_name == "Charlson Comorbidity Index":
        items=[("MI",1),("CHF",1),("Peripheral vascular disease",1),("CVA/TIA",1),("Dementia",1),("COPD",1),("Connective tissue disease",1),("Peptic ulcer",1),("Mild liver disease",1),("Diabetes",1),("Hemiplegia",2),("Moderate/severe renal disease",2),("Diabetes with end-organ damage",2),("Tumor",2),("Leukemia/Lymphoma",2),("Moderate/severe liver disease",3),("Metastatic tumor",6)]
        s=sum(_cb(a,b) for a,b in items); result=s; interp="Comorbidity burden score"; risk="Low" if s<=2 else "Medium" if s<=5 else "High"
    elif score_name == "Clinical Frailty Scale":
        s=st.slider("CFS",1,9,3); result=s; interp="Fit/vulnerable" if s<=4 else "Frail" if s<=6 else "Severely frail"; risk="Low" if s<=4 else "Medium" if s<=6 else "High"
    elif score_name == "STOP-Bang":
        s=sum([_cb("Snoring"),_cb("Tiredness"),_cb("Observed apnea"),_cb("High BP"),_cb("BMI >35"),_cb("Age >50"),_cb("Neck circumference large"),_cb("Male")]); result=s; interp="Low OSA risk" if s<=2 else "Intermediate OSA risk" if s<=4 else "High OSA risk"; risk="Low" if s<=2 else "Medium" if s<=4 else "High"
    elif score_name == "qSOFA":
        s=sum([_cb("RR ≥22/min"),_cb("Altered mentation"),_cb("SBP ≤100 mmHg")]); result=f"{s}/3"; interp="High risk in suspected sepsis" if s>=2 else "Lower risk"; risk="High" if s>=2 else "Low"
    elif score_name == "SIRS":
        s=sum([_cb("Temp >38 or <36"),_cb("HR >90"),_cb("RR >20 or PaCO2 <32"),_cb("WBC >12 or <4 or bands >10%")]); result=f"{s}/4"; interp="SIRS present" if s>=2 else "SIRS not met"; risk="Medium" if s>=2 else "Low"
    elif score_name == "NEWS2":
        rr=st.selectbox("RR",["12-20","9-11","21-24","≤8 or ≥25"]); spo2=st.selectbox("SpO2",["≥96","94-95","92-93","≤91"]); o2=st.checkbox("On oxygen"); temp=st.selectbox("Temp",["36.1-38.0","35.1-36.0 or 38.1-39.0","≤35 or ≥39.1"]); sbp=st.selectbox("SBP",["111-219","101-110","91-100","≤90 or ≥220"]); pulse=st.selectbox("Pulse",["51-90","41-50 or 91-110","111-130","≤40 or ≥131"]); conf=st.checkbox("New confusion/unresponsive")
        s={"12-20":0,"9-11":1,"21-24":2,"≤8 or ≥25":3}[rr]+{"≥96":0,"94-95":1,"92-93":2,"≤91":3}[spo2]+(2 if o2 else 0)+{"36.1-38.0":0,"35.1-36.0 or 38.1-39.0":1,"≤35 or ≥39.1":3}[temp]+{"111-219":0,"101-110":1,"91-100":2,"≤90 or ≥220":3}[sbp]+{"51-90":0,"41-50 or 91-110":1,"111-130":2,"≤40 or ≥131":3}[pulse]+(3 if conf else 0)
        result=s; interp="Low aggregate score" if s<=4 else "Medium risk: clinical review" if s<=6 else "High risk: urgent response"; risk="Low" if s<=4 else "Medium" if s<=6 else "High"
    elif score_name == "Shock Index":
        hr=st.number_input("Heart rate",20,250,90); sbp=st.number_input("SBP",40,250,120); s=round(hr/sbp,2); result=s; interp="Normal" if s<0.7 else "Borderline" if s<=0.9 else "Possible shock"; risk="Low" if s<0.7 else "Medium" if s<=0.9 else "High"
    elif score_name in ["Alvarado","AIR Appendicitis","RIPASA"]:
        if score_name=="Alvarado":
            s=sum([_cb("Migration"),_cb("Anorexia"),_cb("Nausea/vomiting"),_cb("RIF tenderness",2),_cb("Rebound"),_cb("Fever"),_cb("Leukocytosis",2),_cb("Neutrophilia")]); result=f"{s}/10"; interp="Unlikely" if s<=4 else "Possible" if s<=6 else "Probable"; risk="Low" if s<=4 else "Medium" if s<=6 else "High"
        elif score_name=="AIR Appendicitis":
            s=sum([_cb("Vomiting"),_cb("RIF pain/tenderness",2),_cb("Rebound/guarding",2),_cb("Temp ≥38.5"),_cb("WBC elevated",2),_cb("Neutrophils ≥85%",2),_cb("CRP ≥50",2)]); result=f"{s}/12"; interp="Low probability" if s<=4 else "Intermediate" if s<=8 else "High probability"; risk="Low" if s<=4 else "Medium" if s<=8 else "High"
        else:
            s=sum([_cb("Male"),_cb("Age <40"),_cb("RIF pain",0.5),_cb("Migration",0.5),_cb("Anorexia"),_cb("Nausea/vomiting"),_cb("Duration <48h"),_cb("RIF tenderness"),_cb("Guarding",2),_cb("Raised WBC"),_cb("Negative urine")]); result=s; interp="Low/intermediate" if s<7.5 else "High probability"; risk="High" if s>=7.5 else "Medium"
    elif score_name in ["Tokyo Cholecystitis Grade","Tokyo Cholangitis Grade"]:
        organ=st.checkbox("Organ dysfunction"); moderate=sum([_cb("Marked inflammatory response"),_cb("Symptoms >72h"),_cb("Local severe inflammation/abscess/gangrene")]); result="Grade III" if organ else "Grade II" if moderate else "Grade I"; interp="Severe" if organ else "Moderate" if moderate else "Mild"; risk="High" if organ else "Medium" if moderate else "Low"
    elif score_name == "ASGE CBD Stone Risk":
        high=st.checkbox("CBD stone on imaging") or st.checkbox("Ascending cholangitis") or st.checkbox("Bilirubin >4 + dilated CBD"); inter=st.checkbox("Abnormal LFT/age>55/dilated CBD alone"); result="High" if high else "Intermediate" if inter else "Low"; interp="ERCP usually considered" if high else "MRCP/EUS/IOC usually considered" if inter else "Low probability"; risk=result if result!="Intermediate" else "Medium"
    elif score_name in ["Nassar Difficulty Grade","Parkland Cholecystitis Grade"]:
        s=st.slider("Grade",1,5,2); result=f"Grade {s}"; interp="Easy/mild" if s<=2 else "Difficult/moderate" if s==3 else "Severe/dangerous anatomy"; risk="Low" if s<=2 else "Medium" if s==3 else "High"
    elif score_name in ["BISAP","Ranson Admission","Glasgow-Imrie Pancreatitis","Modified CT Severity Index"]:
        if score_name=="BISAP": s=sum([_cb("BUN >25"),_cb("Impaired mental status"),_cb("SIRS"),_cb("Age >60"),_cb("Pleural effusion")]); result=f"{s}/5"; interp="Higher risk" if s>=3 else "Lower risk"; risk="High" if s>=3 else "Low"
        elif score_name=="Ranson Admission": s=sum([_cb("Age >55"),_cb("WBC >16k"),_cb("Glucose >200"),_cb("LDH >350"),_cb("AST >250")]); result=f"{s}/5"; interp="Higher severity" if s>=3 else "Lower severity"; risk="High" if s>=3 else "Low"
        elif score_name=="Glasgow-Imrie Pancreatitis": s=sum([_cb("PaO2 <60"),_cb("Age >55"),_cb("Neutrophils/WBC >15k"),_cb("Calcium <2 mmol/L"),_cb("Urea >16"),_cb("LDH >600"),_cb("Albumin <32"),_cb("Glucose >10")]); result=f"{s}/8"; interp="Severe pancreatitis likely" if s>=3 else "Lower severity"; risk="High" if s>=3 else "Low"
        else: s=st.slider("CTSI score",0,10,2); result=s; interp="Mild" if s<=3 else "Moderate" if s<=6 else "Severe"; risk="Low" if s<=3 else "Medium" if s<=6 else "High"
    elif score_name in ["Glasgow-Blatchford","AIMS65","Rockall Pre-Endoscopy"]:
        if score_name=="AIMS65": s=sum([_cb("Albumin <3.0"),_cb("INR >1.5"),_cb("Altered mental status"),_cb("SBP ≤90"),_cb("Age >65")]); result=f"{s}/5"; interp="High mortality risk" if s>=2 else "Lower risk"; risk="High" if s>=2 else "Low"
        elif score_name=="Rockall Pre-Endoscopy": s=sum([_cb("Age 60-79",1),_cb("Age ≥80",2),_cb("Shock/tachycardia",1),_cb("Hypotension",2),_cb("Major comorbidity",2)]); result=s; interp="Higher pre-endoscopy risk" if s>=3 else "Lower risk"; risk="High" if s>=3 else "Low"
        else: s=sum([_cb("BUN high",2),_cb("Hb low",2),_cb("SBP <100",2),_cb("Pulse ≥100"),_cb("Melena"),_cb("Syncope",2),_cb("Liver disease",2),_cb("Heart failure",2)]); result=s; interp="Very low" if s==0 else "Moderate" if s<=5 else "High risk"; risk="Low" if s==0 else "Medium" if s<=5 else "High"
    elif score_name in ["Mannheim Peritonitis Index","Boey Score"]:
        if score_name=="Boey Score": s=sum([_cb("Major medical illness"),_cb("Preop shock"),_cb("Perforation >24h")]); result=f"{s}/3"; interp="High risk" if s>=2 else "Lower risk"; risk="High" if s>=2 else "Low"
        else: s=sum([_cb("Age >50",5),_cb("Female",5),_cb("Organ failure",7),_cb("Malignancy",4),_cb("Duration >24h",4),_cb("Origin not colonic",4),_cb("Diffuse peritonitis",6),_cb("Purulent exudate",6),_cb("Fecal exudate",12)]); result=s; interp="Low" if s<21 else "Intermediate" if s<=29 else "High mortality risk"; risk="Low" if s<21 else "Medium" if s<=29 else "High"
    elif score_name in ["Child-Pugh","MELD-Na","ALBI Grade"]:
        if score_name=="MELD-Na":
            bili=st.number_input("Bilirubin",0.1,60.0,1.0); inr=st.number_input("INR",0.8,10.0,1.0); cr=st.number_input("Creatinine",0.1,15.0,1.0); na=st.number_input("Sodium",120,150,137); meld=round(3.78*math.log(max(bili,1))+11.2*math.log(max(inr,1))+9.57*math.log(max(cr,1))+6.43); nac=min(max(na,125),137); s=round(meld+1.32*(137-nac)-0.033*meld*(137-nac)); result=s; interp="Lower" if s<10 else "Moderate" if s<20 else "High"; risk="Low" if s<10 else "Medium" if s<20 else "High"
        elif score_name=="ALBI Grade": alb=st.number_input("Albumin g/L",10.0,60.0,35.0); bili=st.number_input("Bilirubin µmol/L",1.0,800.0,20.0); s=round((math.log10(bili)*0.66)+(alb*-0.085),2); result=s; interp="Grade 1" if s<=-2.60 else "Grade 2" if s<=-1.39 else "Grade 3"; risk="Low" if s<=-2.60 else "Medium" if s<=-1.39 else "High"
        else: s=st.slider("Child-Pugh points",5,15,6); result=s; interp="Class A" if s<=6 else "Class B" if s<=9 else "Class C"; risk="Low" if s<=6 else "Medium" if s<=9 else "High"
    elif score_name in ["Hinchey Diverticulitis","GCS","RTS","Clavien-Dindo","CDC SSI Classification"]:
        if score_name=="GCS": e=st.slider("Eye",1,4,4); v=st.slider("Verbal",1,5,5); m=st.slider("Motor",1,6,6); s=e+v+m; result=s; interp="Mild" if s>=13 else "Moderate" if s>=9 else "Severe"; risk="Low" if s>=13 else "Medium" if s>=9 else "High"
        elif score_name=="RTS": g=st.selectbox("GCS category",["13-15","9-12","6-8","4-5","3"]); sbp=st.selectbox("SBP category",[">89","76-89","50-75","1-49","0"]); rr=st.selectbox("RR category",["10-29",">29","6-9","1-5","0"]); s={"13-15":4,"9-12":3,"6-8":2,"4-5":1,"3":0}[g]+{">89":4,"76-89":3,"50-75":2,"1-49":1,"0":0}[sbp]+{"10-29":4,">29":3,"6-9":2,"1-5":1,"0":0}[rr]; result=f"{s}/12"; interp="Lower trauma physiologic risk" if s>=10 else "High risk"; risk="Low" if s>=10 else "High"
        elif score_name=="Clavien-Dindo": result=st.selectbox("Grade",["Grade I","Grade II","Grade IIIa","Grade IIIb","Grade IV","Grade V"]); interp="Postoperative complication grade"; risk="High" if result in ["Grade IIIb","Grade IV","Grade V"] else "Medium"
        elif score_name=="CDC SSI Classification": result=st.selectbox("SSI type",["No SSI","Superficial incisional SSI","Deep incisional SSI","Organ/space SSI"]); interp="CDC SSI surveillance classification"; risk="Low" if result=="No SSI" else "Medium" if "Superficial" in result else "High"
        else: result=st.selectbox("Hinchey",["Ia","Ib","II","III","IV"]); interp="Diverticulitis classification"; risk="Low" if result in ["Ia","Ib"] else "Medium" if result=="II" else "High"
    else:
        result=st.text_input("Result / Grade"); interp=st.text_area("Interpretation"); risk=st.selectbox("Risk",["Low","Medium","High"])
    st.metric("Result", result)
    st.write(interp); risk_label(risk)
    return result, interp, risk
