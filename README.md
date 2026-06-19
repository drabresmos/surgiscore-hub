# SurgiScore Clinical EHR v10

A bilingual Arabic/English **workflow-centred surgical clinical pilot** for clinic, theatre, ward, results, prescribing and post-operative follow-up.

> **Safety status:** This is a pilot and decision-support application. It is not a certified medical device or an accredited hospital EHR. Do not use identifiable patient data on a public Streamlit Community Cloud deployment. Clinical adoption requires hospital-controlled hosting, governance, validation, security testing, training, backup/restore testing and approval by surgery, anesthesia, nursing, pharmacy, infection control, IT and privacy teams.

## What changed in v10

The interface was redesigned around the way hospital teams work rather than around isolated software modules.

- Role-aware **My Worklist** for due tasks, results, clinic, theatre and ward work
- Compact hospital-style application header instead of a large landing banner
- Global search across patients, MRN, phone, appointments, operations and results
- Quick-add dialog for patients, appointments, tasks and surgical cases
- Persistent selected-patient context between modules
- Unified **Longitudinal Patient Chart** with:
  - Overview and timeline
  - Visits and encounters
  - Problems and structured allergies
  - Medications and reconciliation
  - Orders and results
  - Surgical episodes
  - Follow-up
  - Documents and images
- Surgical pathway stepper from decision to closure
- Theatre **Calendar/List** views with direct pathway access
- Action-oriented Results Inbox with acknowledge, task creation and patient navigation
- Operational Ward Board with NEWS2, observation due status, POD, pain, filters and quick observations
- Mobile/iPad quick navigation and smaller touch-friendly responsive components
- Role-aware page visibility while retaining server-side permission checks
- Search-safe output escaping and existing audit trail preservation
- No new database tables: v10 remains compatible with the v9 schema

## Main files

```text
app.py                 Application entry point and role-aware routing
app_shell.py           Global toolbar, search, quick add and navigation
workflow_pages.py      My Worklist, Patient Chart and Results Workspace
ui_components.py       Patient banner, workflow stepper and shared UI components
clinic_pages.py        Clinic, prescribing, follow-up and tasks
app_pages.py           Theatre, ward, surgical journey, scores and governance
database.py            SQLAlchemy models, persistence, audit and global search
styles.py              Responsive hospital-style UI
```

## Streamlit Community Cloud deployment

Use only with synthetic/test data.

1. Unzip the project.
2. Upload the **contents** of the folder to the root of the GitHub repository.
3. In Streamlit Community Cloud set the main file to `app.py`.
4. Keep `APP_MODE = "demo"`.
5. Reboot the app after replacing files.

## Clinical pilot deployment

A controlled pilot should use:

- `APP_MODE = "clinical"`
- OIDC/SSO with MFA
- Managed PostgreSQL over TLS
- Private encrypted object storage for attachments
- Role-based access and named accounts
- Encrypted automated backups with tested restoration
- Separate development, validation and production environments
- Central audit and security logs
- Formal medication-safety content and local formulary governance
- Approved downtime and incident-response procedures

## Local run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Testing

```bash
pip install -r requirements-dev.txt
pytest -q
```

## Upgrade from v9

v10 uses the existing v9 database schema and does not require a destructive migration. Back up the production database before every upgrade. Replace the application files, retain the configured `DATABASE_URL`, and run validation in a non-production environment before release.

## Adoption gate

Do not move to real clinical use until `docs/DEPLOYMENT_CHECKLIST.md` and `docs/VALIDATION_AND_GOVERNANCE.md` are completed and formally approved.
