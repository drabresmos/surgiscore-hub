# Architecture

## Current pilot architecture

```text
Mobile / iPad / Desktop browser
          |
      HTTPS host
          |
   Streamlit application
      |           |
SQLAlchemy      OIDC identity
      |
PostgreSQL (clinical pilot) or SQLite (demo only)
```

Attachments are stored in the database in this pilot. Before production, move binary files to private object storage and store only metadata plus object identifiers in PostgreSQL.

## Target production architecture

```text
PWA / responsive web client
          |
 API gateway / WAF / TLS
          |
 Clinical API + authorization service
   |        |          |
PostgreSQL  Private    Audit/SIEM
            object
            storage
   |
FHIR/SMART integration layer -> EHR/PACS/LIS
```

## Trust boundaries

- End-user device
- Identity provider
- Application runtime
- Database
- Object storage
- EHR/PACS/LIS integration
- Backup and disaster-recovery environment

Each boundary requires authenticated, encrypted, logged and least-privilege access.

## Data lifecycle

1. Patient/case creation
2. Pre-op preparation and safety checks
3. Intra-op documentation and handoff
4. Ward monitoring, scoring and escalation
5. Discharge and post-discharge follow-up
6. Quality/audit analysis
7. Retention, archive and approved disposal

## Known technical limitations

- Streamlit is suitable for a pilot but not the final multi-hospital architecture.
- `create_all()` is used for initial schema creation; production requires versioned database migrations.
- File payloads are stored in the database; production requires private object storage.
- FHIR output is unprofiled and not validated against a specific national or hospital implementation guide.
- No offline mode is implemented.
- No real-time EHR/PACS/LIS interface is implemented.
