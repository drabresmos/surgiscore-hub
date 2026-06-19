# Validation and Clinical Governance Plan

## 1. Intended use

The system supports scheduling, documentation, checklist completion, observation trending, surgical scores, ward rounds, discharge and quality review for general-surgery patients. It is not intended to autonomously diagnose, prescribe, triage, or replace clinical judgement.

## 2. Safety case

Create and maintain:

- Intended-use statement
- User and environment assumptions
- Hazard log
- Risk controls and verification evidence
- Clinical-content approval log
- Requirements-to-test traceability matrix
- Known limitations and residual-risk statement
- Release and rollback plan

## 3. Priority hazards

| Hazard | Example cause | Required controls |
|---|---|---|
| Wrong patient/procedure/site | Duplicate MRN, incorrect selection, incomplete time-out | Two identifiers, visible MRN/name, laterality, site marking, documented time-out, active team confirmation |
| Missed deterioration | Incomplete observations, wrong unit, delayed review | Required fields, ranges, NEWS2, single-red trigger, escalation text, overdue-observation dashboard and local response policy |
| Incorrect score | Formula defect, wrong threshold, wrong units | Versioned formulas, unit labels, automated test cases, independent clinical verification and change control |
| Lost or unavailable data | SQLite/public demo use, outage, failed backup | Managed database, encrypted backups, restore tests, downtime process and monitoring |
| Unauthorized disclosure | Shared account, public link, excessive role | OIDC/MFA, least privilege, audit logs, access reviews, secure hosting and incident response |
| Incomplete handoff | Missing blood loss, drains or escalation plan | Structured OR-to-PACU handoff and signer/timestamp |
| SSI missed after discharge | No surveillance window or follow-up | Procedure-category mapping, 30/90-day surveillance tasks and infection-control workflow |
| Alert fatigue | Excessive/non-actionable alerts | Tiered alerts, local thresholds, role-specific queues, governance review and alert-performance monitoring |

## 4. Clinical verification

For every score and decision rule:

1. Record the source/version.
2. Create normal, boundary and abnormal test cases.
3. Have two independent clinicians calculate expected results.
4. Run automated tests.
5. Record discrepancies and resolution.
6. Lock the approved version and repeat validation after changes.

## 5. User acceptance scenarios

Minimum scenarios:

- Elective laparoscopic cholecystectomy
- Emergency appendectomy
- Emergency laparotomy with sepsis and high NEWS2
- Major colorectal resection with ERAS pathway
- Patient transferred from OR to PACU then ward
- Return to theatre
- Cancelled case
- Discharge with pathology pending
- Readmission with suspected SSI
- Wrong-patient selection caught before saving
- Network outage and recovery
- User role revoked while active

## 6. Quality indicators

Track at minimum:

- WHO checklist phase completion
- Time-out documented before incision
- Prophylactic antibiotic timing completeness
- VTE assessment and prophylaxis documentation
- NEWS2 escalation compliance
- Unplanned ICU transfer
- Return to theatre
- 30-day readmission
- SSI surveillance completion and events
- Mortality and major complications
- Missing-data rate
- User-reported safety incidents
- System uptime and failed backups

## 7. Change governance

Any change to formulas, thresholds, required fields, clinical pathways, terminology, permissions or interoperability mappings requires:

- Change request
- Clinical impact assessment
- Risk assessment
- Test evidence
- Version release note
- Named approver
- Rollback plan
