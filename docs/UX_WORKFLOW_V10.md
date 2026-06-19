# v10 UX and workflow design

## Design principle

The user starts with work requiring action, not a list of software modules. Patient context remains available while moving between clinic, investigations, medication, surgery, ward and follow-up.

## Primary workflow

```text
Login
  → My Worklist
  → Open task/result/patient
  → Longitudinal Patient Chart
  → Clinic / Orders / Medication / Surgery / Ward / Follow-up
```

## Patient context

The Patient Chart banner shows identity, MRN, age, sex, phone, blood group, allergies, active surgical pathway, active problems, medicines, new results and open tasks.

## Surgical pathway

```text
Decision
→ Pre-op assessment
→ Scheduled
→ Ready for theatre
→ In theatre
→ PACU/Recovery
→ Post-op ward
→ Discharged
→ Follow-up
→ Closed
```

## Mobile and iPad

- Compact top application bar
- Quick navigation buttons
- Single-column clinical cards on phones
- Horizontally scrollable workflow stepper
- Reduced calendar density
- Touch targets of approximately 38 px or larger

## Remaining limitations

Streamlit is appropriate for workflow validation and a controlled pilot, but does not provide the same level of client-side routing, offline support, real-time multi-user interaction or fine-grained UI control as a dedicated React/Next.js PWA. A later production migration should preserve these validated workflows.
