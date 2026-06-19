# Core Data Dictionary

| Entity | Purpose | Key fields |
|---|---|---|
| Staff | Application user and role | email, display_name, role, active |
| Patient | Patient identity and safety information | MRN, full name, DOB/age, sex, contact, blood group, allergies |
| Operation | Scheduled and performed surgical episode | procedure code/name, diagnosis, date/time, urgency, status, site/laterality, surgeon, anesthesia, ward/bed/OR |
| Task | Pre-op and score workflow item | phase, code, bilingual labels, status, override reason, completer/time |
| ChecklistItem | WHO checklist phase item | phase, code, bilingual text, answer, comment, signer/time |
| ClinicalRecord | Structured clinical note | record type, JSON payload, author, signer/time |
| VitalSign | Observation set | date/time, shift, RR, SpO2/scale/oxygen, BP, pulse, temperature, consciousness, pain, urine, NEWS2, escalation |
| WardRound | Morning/evening review | date, shift, post-op day, structured payload, author/consultant sign-off |
| ScoreResult | Saved clinical score | score name, result, interpretation, risk, inputs, completer |
| Attachment | Uploaded document | category, filename, MIME type, size, binary payload, uploader |
| AuditLog | Change history | user, action, entity, entity ID, old/new values, timestamp |

## Coding strategy

- Local stable procedure IDs are used in the pilot.
- Production should map procedures and diagnoses to locally approved SNOMED CT/ICD-11/national code systems.
- Vital signs use LOINC codes only in the FHIR export.
- Units must remain explicit and validated at entry and exchange boundaries.
