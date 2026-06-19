# SurgiScore Clinical EHR v9

Responsive bilingual **clinic + theatre + ward + follow-up** pilot for a general-surgery service.

## What is new in v9

- Longitudinal patient chart and timeline.
- Clinic appointments, monthly calendar, daily queue and status workflow.
- Structured surgical clinic encounter with templates, vital signs and electronic signing.
- One-click conversion of a clinic decision into a scheduled surgical case.
- Structured problem list and allergy/intolerance register.
- Structured prescriptions with multiple medication items, printable bilingual HTML and audit trail.
- Medication safety checks for documented allergies, duplicate active therapy and selected high-risk medicines.
- Medication reconciliation across clinic, admission, pre-op, transfer, discharge and follow-up.
- Investigation ordering, result entry, abnormal/critical flags and result acknowledgement inbox.
- Post-operative follow-up scheduler and structured wound/pain/intake/mobility/medication review.
- Patient-linked clinical tasks and due-date dashboard.
- Existing v8 theatre calendar, WHO checklist workflow, pre-op tasks, NEWS2, ward rounds, scoring library, FHIR-style export and quality dashboards retained.
- Improved Apple-inspired responsive UI for mobile and iPad.

## Important status

This is a **clinical pilot**, not a certified production EHR. Do not use real patient data on public Streamlit Community Cloud.

Before clinical deployment use:

- Institutional OIDC/SSO and MFA.
- Managed PostgreSQL.
- Private encrypted attachment storage.
- Tested encrypted backup and restore.
- Formulary-approved medication catalogue and interaction knowledge base.
- Local governance approval for clinical templates, escalation rules, scores and prescribing.
- Privacy, security, penetration and user-acceptance testing.

## Files

- `app.py` — application entry point.
- `clinic_pages.py` — clinic, patient record, prescribing, investigations, follow-up and task UI.
- `app_pages.py` — theatre, ward, scoring, governance and quality UI from v8.
- `database.py` — SQLAlchemy data model and audited persistence.
- `clinic_catalog.py` — appointment, investigation, medication and template catalogues.
- `medication_safety.py` — pilot safety alerts; not a complete interaction engine.
- `reports.py` — printable prescription output.
- `operations_catalog.py`, `scores.py`, `clinical_logic.py`, `clinical_standards.py` — surgical workflow and score logic.
- `auth.py` — demo/OIDC-aware roles.
- `styles.py` — responsive UI.

## Streamlit Community Cloud deployment

1. Upload all project files to the GitHub repository root.
2. Open Streamlit Community Cloud and create/redeploy the app.
3. Main file path:

```text
app.py
```

4. For demonstration only, add secrets:

```toml
APP_MODE = "demo"
HOSPITAL_NAME = "Your Surgical Department"
TIMEZONE = "Asia/Baghdad"
```

SQLite is used automatically when `DATABASE_URL` is absent. Community Cloud storage may reset, so SQLite is not suitable for production persistence.

## PostgreSQL

Set a SQLAlchemy-compatible database URL:

```toml
DATABASE_URL = "postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE?sslmode=require"
APP_MODE = "clinical"
```

Configure Streamlit OIDC under `[auth]` according to the deployment identity provider.

## Local run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Automated checks

```bash
pip install -r requirements-dev.txt
pytest -q
```

Current package: **11 automated tests passing**.

## Clinical limitations

- Medication dosing is entered by the authorized clinician; the system does not generate treatment doses.
- The safety checker is deliberately limited and must not replace a licensed drug interaction and dose-checking knowledge base.
- Clinical scores and recommendations are decision support only.
- Signed records should become immutable with formal amendment workflow before production rollout.
