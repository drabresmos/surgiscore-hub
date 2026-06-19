from datetime import date

COMMON_OPERATIONS = [
    "Laparoscopic appendectomy", "Open appendectomy", "Laparoscopic cholecystectomy", "Open cholecystectomy",
    "Hernia repair - inguinal", "Hernia repair - ventral/incisional", "Perianal abscess drainage", "Hemorrhoidectomy",
    "Anal fistula surgery", "Pilonidal sinus surgery", "Diagnostic laparoscopy", "Exploratory laparotomy",
    "Small bowel resection/anastomosis", "Right hemicolectomy", "Left hemicolectomy", "Sigmoid colectomy",
    "Anterior resection", "Abdominoperineal resection", "Hartmann procedure", "Stoma formation", "Stoma reversal",
    "Perforated peptic ulcer repair", "Adhesiolysis for bowel obstruction", "Bowel obstruction surgery",
    "Thyroidectomy - hemi", "Thyroidectomy - total", "Breast lumpectomy", "Mastectomy", "Axillary surgery",
    "Liver abscess drainage", "Hydatid cyst surgery", "Splenectomy", "Pancreatic necrosectomy", "Whipple procedure",
    "CBD exploration", "ERCP-related surgical backup", "Trauma laparotomy", "Wound debridement", "Skin/soft tissue excision", "Other"
]

STATUS_OPTIONS = ["Scheduled", "Pre-op", "Intra-op", "Post-op", "Discharged", "Cancelled"]
URGENCY_OPTIONS = ["Elective", "Urgent", "Emergency"]
WOUND_OPTIONS = ["Clean", "Clean-contaminated", "Contaminated", "Dirty/Infected"]
ASA_OPTIONS = ["ASA I", "ASA II", "ASA III", "ASA IV", "ASA V"]

SCORE_DESCRIPTIONS = {
    "ASA": "Preoperative anaesthetic risk classification.",
    "Caprini VTE": "Risk stratification for postoperative DVT/PE and thromboprophylaxis planning.",
    "RCRI": "Estimates major cardiac risk for non-cardiac surgery.",
    "Charlson Comorbidity Index": "Summarizes comorbidity burden and long-term prognosis.",
    "Clinical Frailty Scale": "Frailty assessment, important in elderly surgical patients.",
    "STOP-Bang": "Screening tool for obstructive sleep apnea before anaesthesia.",
    "qSOFA": "Quick bedside screen for poor outcome in suspected sepsis.",
    "SIRS": "Systemic inflammatory response criteria.",
    "NEWS2": "Track-and-trigger system for acute clinical deterioration.",
    "Shock Index": "HR/SBP; quick marker of shock or physiological stress.",
    "Alvarado": "Classic appendicitis probability score.",
    "AIR Appendicitis": "Appendicitis score using symptoms, signs, WBC, neutrophils, and CRP.",
    "RIPASA": "Appendicitis score often used in Asian/Middle Eastern populations.",
    "Tokyo Cholecystitis Grade": "Severity grading for acute cholecystitis.",
    "Tokyo Cholangitis Grade": "Severity grading for acute cholangitis.",
    "ASGE CBD Stone Risk": "Stratifies probability of choledocholithiasis and need for MRCP/EUS/ERCP.",
    "Nassar Difficulty Grade": "Intraoperative difficulty grading for laparoscopic cholecystectomy.",
    "Parkland Cholecystitis Grade": "Visual grading of gallbladder inflammation/difficulty.",
    "BISAP": "Early pancreatitis severity score in first 24 hours.",
    "Ranson Admission": "Admission criteria for acute pancreatitis severity.",
    "Glasgow-Imrie Pancreatitis": "Acute pancreatitis severity score.",
    "Modified CT Severity Index": "Radiologic severity of acute pancreatitis.",
    "Glasgow-Blatchford": "Risk score for upper GI bleeding before endoscopy.",
    "AIMS65": "Mortality risk tool in upper GI bleeding.",
    "Rockall Pre-Endoscopy": "Pre-endoscopy risk in upper GI bleeding.",
    "Mannheim Peritonitis Index": "Mortality risk in peritonitis.",
    "Boey Score": "Risk score for perforated peptic ulcer.",
    "Child-Pugh": "Cirrhosis severity and operative risk context.",
    "MELD-Na": "Short-term liver disease mortality risk.",
    "ALBI Grade": "Albumin-bilirubin liver function grade.",
    "Hinchey Diverticulitis": "Classification of complicated diverticulitis.",
    "GCS": "Consciousness assessment in trauma and critical illness.",
    "RTS": "Physiologic trauma severity score.",
    "Clavien-Dindo": "Standard classification of postoperative complications.",
    "CDC SSI Classification": "Classifies surgical site infection as superficial, deep, or organ-space."
}

BASE_RECOMMENDED = ["ASA", "Caprini VTE", "RCRI"]

def recommended_scores(operation: str, urgency: str = "Elective"):
    op = (operation or "").lower()
    scores = list(BASE_RECOMMENDED)
    if urgency in ["Urgent", "Emergency"]:
        scores += ["NEWS2", "Shock Index", "qSOFA"]
    if "append" in op:
        scores += ["Alvarado", "AIR Appendicitis", "RIPASA"]
    if "chole" in op or "cbd" in op or "ercp" in op:
        scores += ["Tokyo Cholecystitis Grade", "ASGE CBD Stone Risk", "Nassar Difficulty Grade", "Parkland Cholecystitis Grade"]
    if "pancre" in op or "whipple" in op:
        scores += ["BISAP", "Ranson Admission", "Glasgow-Imrie Pancreatitis", "Modified CT Severity Index"]
    if "perforated" in op or "laparotomy" in op or "periton" in op:
        scores += ["Mannheim Peritonitis Index", "Boey Score", "SIRS"]
    if "bowel" in op or "colect" in op or "rect" in op or "hartmann" in op or "stoma" in op:
        scores += ["NEWS2", "Clinical Frailty Scale", "Charlson Comorbidity Index"]
    if "thyroid" in op or "breast" in op:
        scores += ["STOP-Bang"]
    if "trauma" in op:
        scores += ["GCS", "RTS", "Shock Index"]
    if "liver" in op or "hydatid" in op:
        scores += ["Child-Pugh", "MELD-Na", "ALBI Grade"]
    # preserve order unique
    out=[]
    for s in scores:
        if s not in out: out.append(s)
    return out
