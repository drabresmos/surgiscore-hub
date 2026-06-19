# Security Policy for the Pilot

- Never commit passwords, database URLs, OIDC secrets or patient data.
- Use the hosting platform's encrypted secret manager.
- Use demo mode and synthetic data on public Streamlit Community Cloud.
- Production requires institutional OIDC with MFA, managed PostgreSQL, TLS, encryption at rest, centralized logging, encrypted backups, restore testing and least-privilege roles.
- Attachments should move to private object storage with short-lived signed URLs before production.
- Report suspected vulnerabilities privately to the designated hospital security owner; do not enter real patient data while a critical issue is open.
- Run dependency scanning, secret scanning, static analysis and an OWASP ASVS-based security test before each clinical release.
