GENERAL_SURGERY_OPERATIONS = [
    "Laparoscopic Cholecystectomy", "Open Cholecystectomy", "Appendectomy - Laparoscopic", "Appendectomy - Open",
    "Inguinal Hernia Repair - Open", "Inguinal Hernia Repair - Laparoscopic TEP/TAPP", "Umbilical Hernia Repair",
    "Incisional/Ventral Hernia Repair", "Exploratory Laparotomy", "Adhesiolysis", "Small Bowel Resection",
    "Right Hemicolectomy", "Left Hemicolectomy", "Sigmoid Colectomy", "Anterior Resection", "Abdominoperineal Resection",
    "Hartmann Procedure", "Stoma Formation", "Stoma Reversal", "Perforated DU Repair / Graham Patch",
    "Gastrectomy - Partial/Subtotal", "Gastrectomy - Total", "Splenectomy", "Thyroidectomy - Hemi", "Thyroidectomy - Total",
    "Parathyroidectomy", "Breast Lumpectomy", "Modified Radical Mastectomy", "Axillary Clearance", "Pilonidal Sinus Surgery",
    "Hemorrhoidectomy", "Anal Fistula Surgery", "Fissure Surgery / LIS", "Abscess Drainage", "Debridement",
    "Diabetic Foot Debridement", "Skin/Soft Tissue Tumor Excision", "Liver Cyst / Hydatid Surgery", "CBD Exploration",
    "ERCP Referral/Perioperative Plan", "Pancreatic Necrosectomy", "Whipple Procedure", "Distal Pancreatectomy",
    "Emergency Trauma Laparotomy", "Other General Surgery Procedure"
]

SCORE_CATEGORIES = {
    "Pre-operative / عام قبل العملية": ["ASA", "RCRI", "Caprini VTE", "Charlson Comorbidity Index", "Clinical Frailty Scale", "STOP-Bang", "Shock Index"],
    "Emergency / Sepsis": ["SIRS", "qSOFA", "NEWS2", "SOFA Simplified", "Mannheim Peritonitis Index", "Boey Score"],
    "Appendix": ["Alvarado", "AIR Appendicitis", "RIPASA", "Pediatric Appendicitis Score"],
    "Gallbladder / CBD": ["Tokyo Cholecystitis Grade", "Tokyo Cholangitis Grade", "ASGE CBD Stone Risk", "Nassar Difficulty Grade", "Parkland Cholecystitis Grade", "Csendes Mirizzi Classification"],
    "Pancreas": ["BISAP", "Ranson Admission", "Glasgow-Imrie Pancreatitis", "Modified CT Severity Index", "Atlanta Pancreatitis Classification"],
    "GI Bleeding": ["Glasgow-Blatchford", "AIMS65", "Rockall Pre-Endoscopy", "Oakland Lower GI Bleeding"],
    "Liver / HPB": ["Child-Pugh", "MELD-Na", "ALBI Grade"],
    "Colorectal / Functional": ["Hinchey Diverticulitis", "WSES Diverticulitis Classification", "LARS Score", "Wexner Incontinence Score"],
    "Trauma": ["GCS", "RTS", "AAST Organ Injury Grade"],
    "Post-operative": ["Clavien-Dindo", "CDC SSI Classification"]
}

SCORE_DESCRIPTIONS = {
    "ASA": "ASA Physical Status: تصنيف عام لتحمل anesthesia والعملية.",
    "RCRI": "Revised Cardiac Risk Index: تقدير خطر major cardiac events قبل non-cardiac surgery.",
    "Caprini VTE": "Caprini Score: يحدد خطر DVT/PE واختيار thromboprophylaxis.",
    "Charlson Comorbidity Index": "Charlson Index: يقيّم عبء comorbidities وتأثيرها على prognosis.",
    "Clinical Frailty Scale": "Clinical Frailty Scale: مهم جداً لكبار السن قبل الجراحة.",
    "STOP-Bang": "STOP-Bang: screening لاحتمال obstructive sleep apnea قبل anesthesia.",
    "Shock Index": "Shock Index = HR/SBP: مؤشر سريع للـ shock أو physiological stress.",
    "SIRS": "SIRS Criteria: screening للاستجابة الالتهابية وقد يساعد في sepsis context.",
    "qSOFA": "qSOFA: تقييم سريع لخطر poor outcome في suspected sepsis.",
    "NEWS2": "NEWS2: early warning score لمراقبة deterioration في المرضى الحادين.",
    "SOFA Simplified": "SOFA: يقيس organ dysfunction؛ هنا نسخة تعليمية مبسطة.",
    "Alvarado": "Alvarado Score: تقدير احتمال acute appendicitis.",
    "AIR Appendicitis": "AIR Score: Appendicitis Inflammatory Response؛ يستفيد من CRP/WBC/neutrophils.",
    "RIPASA": "RIPASA: score شائع في آسيا/الشرق الأوسط لتشخيص appendicitis.",
    "Pediatric Appendicitis Score": "PAS: تقييم appendicitis عند الأطفال.",
    "Tokyo Cholecystitis Grade": "Tokyo Grade: تصنيف شدة acute cholecystitis.",
    "Tokyo Cholangitis Grade": "Tokyo Grade: تصنيف شدة acute cholangitis.",
    "ASGE CBD Stone Risk": "ASGE risk: stratification لاحتمال choledocholithiasis واختيار MRCP/EUS/ERCP.",
    "Nassar Difficulty Grade": "Nassar Grade: تقدير صعوبة laparoscopic cholecystectomy intra-op.",
    "Parkland Cholecystitis Grade": "Parkland Grade: تصنيف شدة gallbladder inflammation أثناء العملية.",
    "Csendes Mirizzi Classification": "Csendes: تصنيف Mirizzi syndrome حسب fistula/erosion.",
    "BISAP": "BISAP: quick severity score للـ acute pancreatitis خلال أول 24h.",
    "Ranson Admission": "Ranson admission criteria: مؤشرات شدة pancreatitis عند الدخول.",
    "Glasgow-Imrie Pancreatitis": "Glasgow-Imrie: severity score للـ acute pancreatitis.",
    "Modified CT Severity Index": "Modified CTSI: شدة pancreatitis بالـ CT مع necrosis/complications.",
    "Atlanta Pancreatitis Classification": "Revised Atlanta: mild/moderately severe/severe acute pancreatitis.",
    "Glasgow-Blatchford": "GBS: risk stratification للـ upper GI bleeding قبل endoscopy.",
    "AIMS65": "AIMS65: mortality risk in upper GI bleeding.",
    "Rockall Pre-Endoscopy": "Rockall pre-endoscopy: تقدير risk في UGIB قبل المنظار.",
    "Oakland Lower GI Bleeding": "Oakland Score: يساعد في تحديد safe discharge في LGIB.",
    "Mannheim Peritonitis Index": "MPI: mortality risk في peritonitis.",
    "Boey Score": "Boey: risk score للـ perforated peptic ulcer.",
    "Child-Pugh": "Child-Pugh: liver reserve وتصنيف cirrhosis perioperative risk.",
    "MELD-Na": "MELD-Na: تقدير short-term mortality في liver disease.",
    "ALBI Grade": "ALBI: liver function based on albumin and bilirubin.",
    "Hinchey Diverticulitis": "Hinchey: تصنيف complicated diverticulitis.",
    "WSES Diverticulitis Classification": "WSES: staging حديث للـ acute diverticulitis.",
    "LARS Score": "LARS: bowel dysfunction بعد low anterior resection.",
    "Wexner Incontinence Score": "Wexner: شدة fecal incontinence.",
    "GCS": "Glasgow Coma Scale: مستوى الوعي في trauma/critical care.",
    "RTS": "Revised Trauma Score: physiologic trauma severity.",
    "AAST Organ Injury Grade": "AAST: grading لإصابات الأعضاء مثل spleen/liver/kidney.",
    "Clavien-Dindo": "Clavien-Dindo: تصنيف postoperative complications.",
    "CDC SSI Classification": "CDC SSI: superficial/deep/organ-space surgical site infection."
}

def suggested_scores_for_operation(op):
    s = ["ASA", "RCRI", "Caprini VTE"]
    low = op.lower()
    if "append" in low: s += ["Alvarado", "AIR Appendicitis", "RIPASA"]
    if "chole" in low or "cbd" in low or "ercp" in low: s += ["Tokyo Cholecystitis Grade", "ASGE CBD Stone Risk", "Nassar Difficulty Grade", "Parkland Cholecystitis Grade"]
    if "laparotomy" in low or "perforated" in low or "bowel" in low: s += ["qSOFA", "Shock Index", "Mannheim Peritonitis Index", "Boey Score"]
    if "pancrea" in low or "whipple" in low: s += ["BISAP", "Ranson Admission", "Modified CT Severity Index"]
    if "liver" in low or "hydatid" in low: s += ["Child-Pugh", "MELD-Na", "ALBI Grade"]
    if "trauma" in low: s += ["GCS", "RTS", "Shock Index", "AAST Organ Injury Grade"]
    if "colon" in low or "rect" in low or "hartmann" in low: s += ["Caprini VTE", "Clavien-Dindo", "Hinchey Diverticulitis"]
    return list(dict.fromkeys(s))
