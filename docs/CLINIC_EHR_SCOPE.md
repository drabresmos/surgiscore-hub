# v9 Clinic and Surgical EHR Scope

## End-to-end workflow

1. Register patient and document allergy status.
2. Schedule clinic appointment and track check-in/queue status.
3. Complete structured encounter, examination, diagnosis and plan.
4. Add problem-list entries, requests, tasks, prescriptions and follow-up.
5. Convert a surgical decision to an operation record with pre-op tasks and recommended scores.
6. Continue through theatre safety workflow, ward monitoring and discharge.
7. Track wound, pathology, medication adherence, complications and post-operative follow-up.

## Production backlog

- Formal immutable signing and amendment workflow.
- Dedicated MAR/eMAR for inpatient administrations and omitted-dose reasons.
- Licensed drug interaction, renal/hepatic dose and pregnancy checking.
- Patient portal and approved communication channel.
- LIS, PACS/DICOMweb, pharmacy and billing integrations.
- FHIR profiles for Appointment, Encounter, Condition, AllergyIntolerance, ServiceRequest, DiagnosticReport and MedicationRequest.
- Terminology service for ICD-11, SNOMED CT, LOINC and local formulary codes.
- Multi-site tenancy, downtime mode, retention policy and disaster-recovery testing.
