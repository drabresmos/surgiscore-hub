# Clinical Deployment Checklist

Every item should have an owner, evidence, date and approval signature.

## Governance

- [ ] Executive sponsor and clinical product owner appointed
- [ ] Surgical, anesthesia, nursing, infection-control and IT representatives appointed
- [ ] Intended use and excluded uses documented
- [ ] Local legal/privacy review completed
- [ ] Data-retention and record-amendment policies approved
- [ ] Clinical downtime and paper fallback process approved
- [ ] Change-control and release approval process established

## Clinical content

- [ ] Local WHO checklist adaptation approved by the multidisciplinary theatre team
- [ ] NEWS2 calculation verified against official test cases
- [ ] Local NEWS2 escalation pathway configured and approved
- [ ] All score calculators independently verified by two clinicians
- [ ] Procedure-to-score suggestions reviewed and classified as required/recommended/optional
- [ ] ERAS elements converted into procedure-specific protocols where applicable
- [ ] SSI surveillance fields and follow-up windows reviewed by infection control
- [ ] Discharge red flags and follow-up instructions approved

## Identity and access

- [ ] Clinical mode enabled
- [ ] Institutional OIDC configured
- [ ] MFA enforced at the identity provider
- [ ] Role matrix approved
- [ ] Joiner/mover/leaver account process tested
- [ ] Emergency/break-glass access policy defined
- [ ] Session timeout and device-lock expectations approved

## Infrastructure and security

- [ ] Hospital-controlled or contractually approved hosting selected
- [ ] Managed PostgreSQL configured with TLS
- [ ] Encryption at rest verified
- [ ] Object storage configured for attachments; public access disabled
- [ ] Secrets stored outside the repository
- [ ] Network segmentation/WAF/reverse proxy configured
- [ ] Central logs and security monitoring enabled
- [ ] Dependency and container vulnerability scans passing
- [ ] OWASP ASVS-based review completed
- [ ] Independent penetration test completed and findings closed
- [ ] Backup schedule configured
- [ ] Restore test completed and documented
- [ ] Recovery time and recovery point objectives approved

## Interoperability

- [ ] MRN source and duplicate-patient handling agreed
- [ ] Terminology mappings reviewed
- [ ] FHIR profiles and implementation guide selected
- [ ] FHIR export validated using an approved validator
- [ ] Receiving EHR/PACS integration tested end-to-end
- [ ] Failed-message reconciliation process tested

## Validation and rollout

- [ ] Unit and integration tests pass
- [ ] Clinical scenario tests pass
- [ ] Mobile, tablet and desktop usability tests pass
- [ ] Accessibility review completed
- [ ] Performance/load test completed
- [ ] Pilot ward and pilot dates approved
- [ ] Training completed and competency recorded
- [ ] Super-user and help-desk coverage arranged
- [ ] Safety incident reporting route published
- [ ] Go-live readiness review signed
- [ ] Post-go-live monitoring and review dates scheduled
