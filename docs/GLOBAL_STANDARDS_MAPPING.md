# Global Standards Mapping

This document separates what is **implemented**, **partially implemented**, and **not yet implemented**. It is intended for governance review, not as a certification claim.

| Reference | Intended control/workflow | v8 implementation | Status / remaining gap |
|---|---|---|---|
| WHO Surgical Safety Checklist | Sign-in, time-out, sign-out; designated completion and team communication | Structured three-phase checklist with signer, timestamp, comment and audit events | Implemented as a local adaptation. Requires local multidisciplinary approval, simulation, training and compliance audit. |
| Joint Commission Universal Protocol concepts | Patient/procedure/site verification, site marking, final time-out immediately before incision, documentation | Two identifiers, procedure/site/laterality, site marking, team confirmation and documented time-out | Partially implemented. Local policy must define who leads the time-out and prevent incision until unresolved concerns are closed. |
| ERAS Society pathways | Multimodal care throughout pre-, intra- and post-operative journey | Practical ERAS-oriented elements, optimization, analgesia, nutrition, mobilization and discharge readiness | Framework implemented; procedure-specific pathways and order sets still require local specialty approval. |
| RCP NEWS2 | Standardized observation scoring, monitoring frequency, escalation, single-parameter red trigger | Complete core score with Scale 1/2, oxygen, ACVPU, monitoring text and single-red rule | Implemented in software; clinical validation against official charts and local escalation policy required. |
| CDC/NHSN SSI | Standardized SSI surveillance and 30/90-day follow-up based on procedure category | SSI classification selector, wound/round fields, discharge red flags | Partial. Needs NHSN category mapping, event criteria logic, denominator data, surveillance window engine and infection-control review. |
| HL7 FHIR R4 | Interoperable Patient, Encounter, Procedure, Observation and DocumentReference resources | FHIR R4-style collection Bundle with LOINC-coded vital signs | Partial. Requires official profiles, terminology bindings, validation server tests and receiving-EHR conformance testing. |
| SMART App Launch | OAuth2/OIDC launch and identity context | Streamlit OIDC login and local role mapping | Partial. Not a full SMART-on-FHIR launch; requires EHR authorization server and scoped FHIR API integration. |
| SNOMED CT | Standard clinical terminology | Local stable procedure identifiers with a documented mapping point | Not implemented. Requires licensed/local terminology service and validated mappings. |
| ICD-11 | Diagnosis and procedure classification | Free-text diagnosis fields | Not implemented. Add coded diagnosis search and national reporting rules after local approval. |
| LOINC | Standard lab/vital observation identifiers | Core vital signs use LOINC codes in FHIR export | Partial. Laboratory catalogue and unit validation are not implemented. |
| DICOM/DICOMweb | Imaging storage and exchange | Upload of exported PDF/JPG reports only | Not implemented. Use PACS/DICOMweb references rather than duplicating diagnostic images in the app. |
| ISO 27799:2025 | Health-information security controls | RBAC, OIDC-ready authentication, audit trail, remote database support | Partial governance alignment only. Requires institutional ISMS, risk assessment, policies, incident response and independent audit. |
| IEC 82304-1 | Health-software product lifecycle, safety and security | Versioned code, risk/validation documents, tests | Partial. Requires formal product requirements, hazard analysis, traceability, release controls, maintenance and post-market process. |
| NIST CSF 2.0 | Govern, Identify, Protect, Detect, Respond and Recover | Deployment checklist, audit log and backup requirements | Partial. Organization must establish target profile, incident response, recovery and supplier-risk controls. |
| OWASP ASVS | Web application security verification | OIDC, role checks, server-side database access, secrets guidance | Partial. Requires ASVS test plan, penetration test, dependency scanning, secure headers and remediation evidence. |

## Design decisions

1. **FHIR R4-style export** was selected for broad compatibility. R5 is the current published base specification, while R4 remains a permanent, widely implemented release.
2. **PostgreSQL is the production database target.** SQLite is retained only for local/demo use.
3. **Attachments are metadata-separated from binary retrieval** to avoid exposing file payloads in lists, exports and audit views.
4. **Soft archive** is used for cases rather than destructive deletion.
5. **Audit entries** are created for patient, operation, checklist, score, observation, attachment and administration changes.
6. **Clinical scores remain decision support.** No result is allowed to replace responsible clinician assessment or local policy.
