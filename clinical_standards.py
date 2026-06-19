"""Clinical workflow definitions derived from internationally used perioperative standards.

Local policy must review and approve every checklist before clinical use.
"""

PREOP_TASKS = [
    {"phase": "Pre-op", "code": "id_two", "label_ar": "تأكيد هوية المريض باستخدام معرفين مستقلين", "label_en": "Confirm patient identity using two identifiers"},
    {"phase": "Pre-op", "code": "procedure_site", "label_ar": "مطابقة الإجراء والموقع والجهة مع السجل والموافقة", "label_en": "Verify procedure, site and laterality against record and consent"},
    {"phase": "Pre-op", "code": "consent", "label_ar": "وجود informed consent موثق", "label_en": "Documented informed consent available"},
    {"phase": "Pre-op", "code": "site_mark", "label_ar": "تعليم موقع العملية عند الحاجة", "label_en": "Surgical site marked when applicable"},
    {"phase": "Pre-op", "code": "allergies", "label_ar": "مراجعة allergies وردود الفعل السابقة", "label_en": "Review allergies and previous reactions"},
    {"phase": "Pre-op", "code": "med_recon", "label_ar": "Medication reconciliation ومراجعة anticoagulants/antiplatelets", "label_en": "Medication reconciliation including anticoagulants/antiplatelets"},
    {"phase": "Pre-op", "code": "fasting", "label_ar": "تأكيد fasting status حسب خطة anesthesia", "label_en": "Confirm fasting status according to anesthesia plan"},
    {"phase": "Pre-op", "code": "anesthesia", "label_ar": "اكتمال anesthesia assessment وخطة airway", "label_en": "Anesthesia assessment and airway plan completed"},
    {"phase": "Pre-op", "code": "labs", "label_ar": "مراجعة التحاليل المطلوبة والقيم الحرجة", "label_en": "Required laboratory results and critical values reviewed"},
    {"phase": "Pre-op", "code": "imaging", "label_ar": "مراجعة imaging وإتاحته داخل العمليات", "label_en": "Relevant imaging reviewed and available in theatre"},
    {"phase": "Pre-op", "code": "blood", "label_ar": "تقييم الحاجة إلى crossmatch/blood products", "label_en": "Crossmatch and blood-product needs assessed"},
    {"phase": "Pre-op", "code": "vte", "label_ar": "تقييم VTE وbleeding risk ووضع خطة prophylaxis", "label_en": "VTE and bleeding risk assessed; prophylaxis plan documented"},
    {"phase": "Pre-op", "code": "antibiotic", "label_ar": "تحديد antibiotic prophylaxis ووقت إعطائه", "label_en": "Antibiotic prophylaxis agent and timing planned"},
    {"phase": "Pre-op", "code": "pregnancy", "label_ar": "تقييم pregnancy status عند الانطباق", "label_en": "Pregnancy status assessed when applicable"},
    {"phase": "Pre-op", "code": "nutrition", "label_ar": "تقييم nutrition/frailty واحتياجات optimization", "label_en": "Nutrition/frailty and optimization needs assessed"},
    {"phase": "Pre-op", "code": "equipment", "label_ar": "تأكيد توفر implants/equipment والمواد الخاصة", "label_en": "Required implants, equipment and special supplies confirmed"},
    {"phase": "Pre-op", "code": "destination", "label_ar": "تحديد post-op destination: Ward/HDU/ICU", "label_en": "Postoperative destination planned: ward/HDU/ICU"},
]

WHO_CHECKLIST = [
    # Sign-in: before induction
    {"phase": "Sign-in", "code": "si_identity", "text_ar": "أكد المريض هويته والإجراء والموقع والموافقة", "text_en": "Patient confirms identity, procedure, site and consent"},
    {"phase": "Sign-in", "code": "si_marked", "text_ar": "الموقع معلّم أو غير منطبق", "text_en": "Site marked or not applicable"},
    {"phase": "Sign-in", "code": "si_machine", "text_ar": "إكمال فحص جهاز التخدير والأدوية", "text_en": "Anesthesia machine and medication check completed"},
    {"phase": "Sign-in", "code": "si_oximeter", "text_ar": "Pulse oximeter يعمل ومثبت", "text_en": "Pulse oximeter functioning and on patient"},
    {"phase": "Sign-in", "code": "si_allergy", "text_ar": "مراجعة الحساسية", "text_en": "Known allergy reviewed"},
    {"phase": "Sign-in", "code": "si_airway", "text_ar": "تقييم difficult airway/aspiration risk وخطة المساعدة", "text_en": "Difficult airway/aspiration risk assessed with assistance plan"},
    {"phase": "Sign-in", "code": "si_bloodloss", "text_ar": "تقييم خطر فقدان الدم وخطة الوصول الوريدي/السوائل", "text_en": "Blood-loss risk assessed with access and fluid plan"},
    # Time-out: before incision
    {"phase": "Time-out", "code": "to_team", "text_ar": "تعريف جميع أعضاء الفريق بأسمائهم وأدوارهم", "text_en": "All team members introduced by name and role"},
    {"phase": "Time-out", "code": "to_identity", "text_ar": "تأكيد جماعي: المريض، الإجراء، الموقع، موضع الشق", "text_en": "Team confirms patient, procedure, site and incision location"},
    {"phase": "Time-out", "code": "to_critical", "text_ar": "الجراح يراجع الخطوات الحرجة والمدة وفقدان الدم المتوقع", "text_en": "Surgeon reviews critical steps, duration and anticipated blood loss"},
    {"phase": "Time-out", "code": "to_anesthesia", "text_ar": "التخدير يراجع المخاوف الخاصة بالمريض", "text_en": "Anesthesia reviews patient-specific concerns"},
    {"phase": "Time-out", "code": "to_nursing", "text_ar": "التمريض يؤكد sterility ومشكلات المعدات", "text_en": "Nursing confirms sterility and equipment concerns"},
    {"phase": "Time-out", "code": "to_antibiotic", "text_ar": "إعطاء antibiotic prophylaxis في الوقت المناسب أو غير منطبق", "text_en": "Antibiotic prophylaxis given in the appropriate window or not applicable"},
    {"phase": "Time-out", "code": "to_imaging", "text_ar": "عرض imaging الضروري أو غير منطبق", "text_en": "Essential imaging displayed or not applicable"},
    # Sign-out: before leaving OR
    {"phase": "Sign-out", "code": "so_procedure", "text_ar": "تأكيد اسم الإجراء المنفذ", "text_en": "Confirm name of procedure performed"},
    {"phase": "Sign-out", "code": "so_counts", "text_ar": "اكتمال instrument/sponge/needle counts", "text_en": "Instrument, sponge and needle counts completed"},
    {"phase": "Sign-out", "code": "so_specimen", "text_ar": "تأكيد specimen labels بصوت مسموع", "text_en": "Specimen labels confirmed aloud"},
    {"phase": "Sign-out", "code": "so_equipment", "text_ar": "تسجيل مشكلات المعدات التي تحتاج متابعة", "text_en": "Equipment problems requiring follow-up documented"},
    {"phase": "Sign-out", "code": "so_recovery", "text_ar": "الفريق يراجع المخاوف الأساسية للتعافي والمتابعة", "text_en": "Team reviews key recovery and management concerns"},
]

PRACTICAL_ERAS_ELEMENTS = [
    "Patient education and shared expectations",
    "Optimization of anemia, nutrition, smoking and comorbidity",
    "Minimize unnecessary fasting according to anesthesia policy",
    "Multimodal opioid-sparing analgesia",
    "Appropriate antibiotic and VTE prophylaxis",
    "Goal-directed fluid and temperature management where indicated",
    "Avoid unnecessary tubes and drains",
    "Early oral intake when clinically appropriate",
    "Early mobilization",
    "Daily discharge-readiness assessment",
]

POSTOP_HANDOFF_FIELDS = [
    "Patient and procedure",
    "Relevant history and allergies",
    "Airway/respiratory status",
    "Hemodynamic status and blood loss",
    "Fluids, transfusion and urine output",
    "Analgesia, antiemetics and antibiotics",
    "Lines, tubes, drains and catheters",
    "Specimens and pending tests",
    "Complications or special concerns",
    "Immediate plan and escalation criteria",
]

DISCHARGE_RED_FLAGS = [
    "Fever or rigors",
    "Increasing wound redness, swelling or discharge",
    "Persistent vomiting or inability to tolerate fluids",
    "Worsening abdominal/chest pain or breathlessness",
    "Bleeding",
    "Reduced urine output",
    "New calf swelling/pain",
    "Confusion or marked weakness",
]
