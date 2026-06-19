"""Curated general-surgery procedure catalog.

The catalog intentionally uses local stable IDs. Production deployments can map these
IDs to SNOMED CT / ICD-11 / national procedure codes according to local licensing and policy.
"""

COMMON_OPERATIONS = [
    # Most common first
    ("APP-LAP", "Laparoscopic appendectomy", "Appendix"),
    ("APP-OPEN", "Open appendectomy", "Appendix"),
    ("GB-LC", "Laparoscopic cholecystectomy", "Gallbladder & Biliary"),
    ("GB-OPEN", "Open cholecystectomy", "Gallbladder & Biliary"),
    ("HERN-ING-LAP", "Laparoscopic inguinal hernia repair (TEP/TAPP)", "Hernia"),
    ("HERN-ING-OPEN", "Open inguinal hernia repair", "Hernia"),
    ("HERN-UMB", "Umbilical hernia repair", "Hernia"),
    ("HERN-VENT", "Ventral/incisional hernia repair", "Hernia"),
    ("ANOREC-HEM", "Hemorrhoidectomy", "Anorectal"),
    ("ANOREC-FISS", "Lateral internal sphincterotomy", "Anorectal"),
    ("ANOREC-FIST", "Fistulotomy / seton procedure", "Anorectal"),
    ("ABSC-I&D", "Incision and drainage of abscess", "Minor & Soft Tissue"),
    ("SOFT-LIP", "Excision of lipoma / soft-tissue lesion", "Minor & Soft Tissue"),
    ("PILO", "Pilonidal sinus excision", "Minor & Soft Tissue"),
    ("THY-HEMI", "Hemithyroidectomy", "Endocrine"),
    ("THY-TOTAL", "Total thyroidectomy", "Endocrine"),
    ("PARA", "Parathyroidectomy", "Endocrine"),
    ("BR-LUMP", "Breast lumpectomy / wide local excision", "Breast"),
    ("BR-MAST", "Mastectomy", "Breast"),
    ("BR-AX", "Axillary surgery / sentinel lymph-node biopsy", "Breast"),
    ("LAP-DIAG", "Diagnostic laparoscopy", "Abdominal"),
    ("LAPAR-EM", "Emergency laparotomy", "Emergency Abdominal"),
    ("LAPAR-EL", "Elective laparotomy", "Abdominal"),
    ("PERF-PPU", "Repair of perforated peptic ulcer", "Upper GI"),
    ("BOWEL-OBST", "Surgery for intestinal obstruction", "Small Bowel"),
    ("SB-RESECT", "Small-bowel resection and anastomosis", "Small Bowel"),
    ("ADH-LYSIS", "Adhesiolysis", "Small Bowel"),
    ("COL-RHC", "Right hemicolectomy", "Colorectal"),
    ("COL-LHC", "Left hemicolectomy", "Colorectal"),
    ("COL-SIG", "Sigmoid colectomy", "Colorectal"),
    ("COL-AR", "Anterior resection", "Colorectal"),
    ("COL-APR", "Abdominoperineal resection", "Colorectal"),
    ("COL-TOTAL", "Total/subtotal colectomy", "Colorectal"),
    ("STOMA-C", "Colostomy formation", "Colorectal"),
    ("STOMA-I", "Ileostomy formation", "Colorectal"),
    ("STOMA-REV", "Stoma reversal", "Colorectal"),
    ("DIV-PERF", "Surgery for perforated diverticulitis", "Colorectal"),
    ("GAST-DIST", "Distal gastrectomy", "Upper GI"),
    ("GAST-TOTAL", "Total gastrectomy", "Upper GI"),
    ("SPLEN", "Splenectomy", "HPB"),
    ("LIVER-RESECT", "Liver resection", "HPB"),
    ("LIVER-CYST", "Hydatid liver surgery", "HPB"),
    ("CBD-EXP", "Common bile duct exploration", "Gallbladder & Biliary"),
    ("BILIARY-BYPASS", "Biliary bypass", "Gallbladder & Biliary"),
    ("WHIPPLE", "Pancreaticoduodenectomy (Whipple)", "Pancreas"),
    ("PAN-DIST", "Distal pancreatectomy", "Pancreas"),
    ("PAN-NEC", "Pancreatic necrosectomy", "Pancreas"),
    ("TRACH", "Tracheostomy", "Emergency / Airway"),
    ("TRAUMA-LAP", "Trauma laparotomy", "Trauma"),
    ("DAMAGE-CTRL", "Damage-control laparotomy", "Trauma"),
    ("WOUND-DEBR", "Wound debridement", "Minor & Soft Tissue"),
    ("OTHER", "Other general-surgery procedure", "Other"),
]

OPERATION_BY_CODE = {code: {"name": name, "category": category} for code, name, category in COMMON_OPERATIONS}
OPERATION_LABELS = [f"{name} — {category}" for _, name, category in COMMON_OPERATIONS]
LABEL_TO_CODE = {f"{name} — {category}": code for code, name, category in COMMON_OPERATIONS}

URGENCY_OPTIONS = ["Elective", "Expedited", "Urgent", "Emergency"]
STATUS_OPTIONS = [
    "Scheduled",
    "Pre-op assessment",
    "Ready for theatre",
    "In theatre",
    "PACU/Recovery",
    "Post-op ward",
    "Discharged",
    "Cancelled",
]
WOUND_CLASSES = ["I Clean", "II Clean-contaminated", "III Contaminated", "IV Dirty/Infected", "Not assigned"]
ANESTHESIA_OPTIONS = ["General anesthesia", "Spinal anesthesia", "Regional block", "Local anesthesia", "Sedation", "Not decided"]
LATERALITY_OPTIONS = ["Not applicable", "Right", "Left", "Bilateral", "Midline"]

SCORE_DESCRIPTIONS = {
    "ASA Physical Status": "تصنيف الحالة العامة قبل التخدير ASA Physical Status؛ يوثق شدة المرض الجهازي ولا يُعد توقعاً منفرداً للمضاعفات.",
    "Caprini VTE": "تقدير خطر venous thromboembolism للمريض الجراحي لتوجيه خطة الوقاية وفق سياسة المؤسسة.",
    "RCRI": "Revised Cardiac Risk Index لتقدير خطر المضاعفات القلبية الكبرى في الجراحات غير القلبية.",
    "Clinical Frailty Scale": "تقييم frailty لدى كبار السن وربطه بخطة perioperative optimization والمتابعة.",
    "STOP-Bang": "تحرّي obstructive sleep apnea قبل التخدير.",
    "NEWS2": "National Early Warning Score 2 لمراقبة التدهور السريري وتحديد سرعة التصعيد وتواتر القياسات.",
    "qSOFA": "أداة سريعة لتحديد مرضى العدوى المعرضين لنتائج سيئة؛ لا تستبدل تقييم sepsis الكامل.",
    "SIRS": "معايير الاستجابة الالتهابية الجهازية؛ مفيدة كسياق سريري ولا تكفي وحدها لتشخيص sepsis.",
    "Alvarado": "سكور سريري لاحتمال acute appendicitis لدى البالغين.",
    "AIR Appendicitis": "Appendicitis Inflammatory Response score ويجمع العلامات السريرية والالتهابية.",
    "Tokyo Cholecystitis Grade": "تصنيف شدة acute cholecystitis إلى Grade I–III.",
    "ASGE CBD Stone Risk": "تصنيف احتمال choledocholithiasis إلى low/intermediate/high لتوجيه MRCP/EUS/IOC/ERCP حسب السياق.",
    "BISAP": "تقدير مبكر لشدة acute pancreatitis خلال أول 24 ساعة.",
    "Ranson": "معايير شدة pancreatitis عند القبول وبعد 48 ساعة؛ لا يُعتمد على جزء واحد باعتباره السكور الكامل.",
    "Glasgow-Blatchford": "تقدير الحاجة إلى تدخل/قبول في upper GI bleeding قبل endoscopy.",
    "AIMS65": "تقدير خطر الوفاة والنتائج السلبية في upper GI bleeding.",
    "Rockall Pre-Endoscopy": "تقدير خطر rebleeding/وفاة قبل endoscopy باستخدام العمر والصدمة والأمراض المصاحبة.",
    "Mannheim Peritonitis Index": "تقدير شدة ومآل peritonitis باستخدام عوامل سريرية ومصدر التلوث.",
    "Boey": "تقدير خطورة perforated peptic ulcer اعتماداً على shock/comorbidity/delay.",
    "Child-Pugh": "تقييم شدة chronic liver disease باستخدام bilirubin, albumin, INR, ascites, encephalopathy.",
    "MELD-Na": "تقدير شدة مرض الكبد وخطر الوفاة قصير الأمد؛ يتطلب وحدات صحيحة وحدوداً معيارية.",
    "GCS": "Glasgow Coma Scale لتقييم الوعي.",
    "Shock Index": "Heart rate ÷ systolic BP؛ مؤشر سريع للاضطراب الدوراني ولا يستبدل الإنعاش والتقييم الكامل.",
    "Clavien-Dindo": "تصنيف شدة postoperative complications وفق التدخل المطلوب.",
    "CDC SSI Classification": "تصنيف surgical-site infection إلى superficial, deep, organ/space وفق تعريفات surveillance.",
}


def suggested_scores(operation_code: str, urgency: str, age: int | None = None) -> list[str]:
    """Return a conservative list of recommended scores.

    Local governance can mark these as mandatory, optional, or not applicable.
    """
    category = OPERATION_BY_CODE.get(operation_code, {}).get("category", "Other")
    scores = ["ASA Physical Status", "Caprini VTE", "RCRI"]
    if age and age >= 65:
        scores.append("Clinical Frailty Scale")
    if urgency in {"Urgent", "Emergency"}:
        scores.extend(["NEWS2", "Shock Index"])
    if category == "Appendix":
        scores.extend(["Alvarado", "AIR Appendicitis"])
    elif category == "Gallbladder & Biliary":
        scores.extend(["Tokyo Cholecystitis Grade", "ASGE CBD Stone Risk"])
    elif category == "Pancreas":
        scores.append("BISAP")
    elif category == "Emergency Abdominal":
        scores.extend(["Mannheim Peritonitis Index", "qSOFA"])
    elif category == "Upper GI":
        scores.append("Boey")
    elif category == "Trauma":
        scores.extend(["GCS", "Shock Index"])
    elif category in {"HPB", "Colorectal"}:
        scores.append("Clinical Frailty Scale") if age and age >= 60 else None
    # preserve order, remove duplicates
    return list(dict.fromkeys(scores))
