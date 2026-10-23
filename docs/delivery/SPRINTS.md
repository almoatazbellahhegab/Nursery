# Sprint milestones and itemized work

Source: all four unchanged files in Document. Two-week planning envelopes are provisional; no dates are committed. Preserve dependencies inside each sprint. Enabling localization and UI experiments in S01 do not complete FEAT-036, TW-034 or TW-035. TW-006 and TW-010 remain open decisions.

## S01 Review foundations

Review portal, bilingual interface prototypes, stack skeletons and traceability. Production builds are blocked by dependency access.

Exit: Windows and iPhone review flows visible; prototype checks pass; physical device UAT remains pending.

Approval: pending. Planning envelope: 2 weeks; re-estimate after refinement; no committed dates.



- [ ] TW-006 Approve supported devices, browsers, accessibility target and response-time objectives — depends on None; owner Product and Engineering
- [ ] TW-010 Name UAT owners for operations, safeguarding, finance, privacy and Arabic quality — depends on None; owner Product and Delivery
- [ ] TW-011 Create the repository structure for web, Flutter, API, worker, contracts, infrastructure and system tests — depends on TW-006; owner Technical Lead
- [ ] TW-012 Define OpenAPI governance and generate Dart and TypeScript clients in CI — depends on TW-011; owner Backend Lead
- [ ] TW-013 Configure Ruff, mypy, pytest, Dart analysis, ESLint, Prettier and commit checks — depends on TW-011; owner Engineering Enablement
- [ ] TW-014 Configure secret, dependency, static-analysis, container and Terraform scans — depends on TW-011; owner Security and DevOps
- [ ] TW-020 Create deterministic synthetic organization fixtures and reset tooling — depends on TW-011; owner QA and Backend
- [ ] TW-030 Establish Arabic and English ICU catalogues, RTL foundations and locale formatting — depends on TW-006,TW-011; owner Web, Mobile and Design
- [ ] TW-034 Build the administration shell, navigation, role-aware routes and bilingual layout — depends on TW-012,TW-023,TW-030; owner Web
- [ ] TW-035 Build the Flutter shell, authentication, role-aware navigation and secure storage — depends on TW-012,TW-025,TW-030; owner Mobile



## S02 Tenant and access foundations

Organization, branches, identity, server authorization and append-only audit.

Exit: Allowed and denied API journeys, real PostgreSQL RLS and suspension tests pass.

Approval: pending. Planning envelope: 2 weeks; re-estimate after refinement; no committed dates.

- [ ] FEAT-001 Organization Lifecycle and Tenant Configuration — depends on None; branch `feat/FEAT-001-organization-lifecycle-and-tenant-configuration`
- [ ] FEAT-034 Audit History — depends on FEAT-001, FEAT-005; branch `feat/FEAT-034-audit-history`
- [ ] FEAT-002 Branch Management — depends on FEAT-001; branch `feat/FEAT-002-branch-management`
- [ ] FEAT-003 Authentication and Account Recovery — depends on FEAT-001; branch `feat/FEAT-003-authentication-and-account-recovery`
- [ ] FEAT-005 Roles Permissions and Access Boundaries — depends on FEAT-001, FEAT-002; branch `feat/FEAT-005-roles-permissions-and-access-boundaries`

- [ ] TW-001 Approve Egypt privacy, controller, processor and cross-border data model — depends on None; owner Legal and Product
- [ ] TW-002 Approve retention, deletion, archival, legal-hold and breach-response policies — depends on TW-001; owner Privacy and Security
- [ ] TW-003 Approve the field-level permission matrix for all roles and relationships — depends on None; owner Product and Safeguarding
- [ ] TW-004 Approve pickup identity evidence, verification and retention rules — depends on TW-001; owner Safeguarding and Legal
- [ ] TW-005 Approve incident severity, escalation, acknowledgement and response rules — depends on TW-001; owner Safeguarding and Operations
- [ ] TW-007 Approve the production AWS region and data-residency position — depends on TW-001; owner Legal and Security
- [ ] TW-008 Approve payment markets, methods, tax, receipt, refund, dispute and reconciliation rules — depends on TW-001; owner Finance and Legal
- [ ] TW-009 Approve Phase 1 reports and metric definitions — depends on None; owner Product and Finance
- [ ] TW-015 Create Terraform modules for network, ECS, RDS, S3, SQS, Cognito, KMS and monitoring — depends on TW-007,TW-011; owner DevOps
- [ ] TW-016 Create immutable Docker builds for API and worker services — depends on TW-011; owner Backend and DevOps
- [ ] TW-017 Implement development, staging and production deployment workflows with approvals — depends on TW-015,TW-016; owner DevOps
- [ ] TW-018 Establish OpenTelemetry context, structured logging, metrics and correlation identifiers — depends on TW-011,TW-015; owner Platform Engineering
- [ ] TW-019 Create service ownership, incident severity and operational runbook templates — depends on TW-018; owner DevOps and Support
- [ ] TW-021 Define tenant-aware base tables, identifiers, foreign keys and indexes — depends on TW-003; owner Backend and Database
- [ ] TW-022 Implement PostgreSQL row-level security and a non-owner runtime role — depends on TW-021; owner Database and Security
- [ ] TW-023 Implement authoritative membership, role, branch, classroom and relationship policy evaluation — depends on TW-003,TW-021; owner Backend and Security
- [ ] TW-024 Implement field-level response filtering for sensitive categories — depends on TW-003,TW-023; owner Backend and Security
- [ ] TW-025 Configure Cognito clients, OIDC flows, MFA, recovery and token validation — depends on TW-015; owner Backend and DevOps
- [ ] TW-028 Implement append-only audit event creation, review and protected retention — depends on TW-021,TW-023; owner Backend and Security
- [ ] TW-031 Implement standard errors, cursor pagination, idempotency and concurrency controls — depends on TW-012,TW-023; owner Backend
- [ ] TW-032 Implement transactional outbox, relay, SQS consumers and dead-letter handling — depends on TW-015,TW-021; owner Backend and DevOps
- [ ] TW-036 Implement organization, branch and lifecycle administration — depends on TW-021,TW-023,TW-028; owner Backend and Web

- [ ] DEV-FEAT-001-01 Create and maintain an organization profile.
- [ ] DEV-FEAT-001-02 Support active, suspended, and closed lifecycle states.
- [ ] DEV-FEAT-001-03 Apply organization-level settings consistently to all permitted users.
- [ ] DEV-FEAT-001-04 Prevent any organization user from discovering or accessing another organization’s records.
- [ ] DEV-FEAT-001-05 Record lifecycle and configuration changes in the audit history.
- [ ] DEV-FEAT-002-01 Create, edit, activate, and deactivate branches.
- [ ] DEV-FEAT-002-02 Maintain branch contact details, timezone, capacity context, and operating status.
- [ ] DEV-FEAT-002-03 Assign users to one or more branches.
- [ ] DEV-FEAT-002-04 Apply branch restrictions to dashboards, workflows, reports, and search.
- [ ] DEV-FEAT-003-01 Support email and password, phone, Google, and Apple sign-in where available.
- [ ] DEV-FEAT-003-02 Provide secure password or account recovery.
- [ ] DEV-FEAT-003-03 Prevent disabled, suspended, or unlinked accounts from accessing protected product data.
- [ ] DEV-FEAT-003-04 Display actionable but non-revealing authentication errors.
- [ ] DEV-FEAT-005-01 Define role capabilities and permitted scope.
- [ ] DEV-FEAT-005-02 Support organization, branch, classroom, child, and relationship-based access.
- [ ] DEV-FEAT-005-03 Prevent role or permission elevation by client-side changes.
- [ ] DEV-FEAT-005-04 Separate financial, care, medical, transportation, and platform-support access.
- [ ] DEV-FEAT-005-05 Cover access rules with positive and negative role tests.
- [ ] DEV-FEAT-034-01 Define auditable actions and minimum event fields.
- [ ] DEV-FEAT-034-02 Create records independently of normal user edit permissions.
- [ ] DEV-FEAT-034-03 Prevent normal users from changing or deleting audit history.
- [ ] DEV-FEAT-034-04 Provide authorized filtering and review.
- [ ] DEV-FEAT-034-05 Minimize sensitive values stored in change summaries.
- [ ] DEV-FEAT-034-06 Define retention and export handling.

## S03 People and classroom setup

Invitations, children, guardian relationships, staff and classrooms.

Exit: Administrator sets up a synthetic center; staff and parents see only permitted records.

Approval: pending. Planning envelope: 2 weeks; re-estimate after refinement; no committed dates.

- [ ] FEAT-004 User Invitations and Account Provisioning — depends on FEAT-001, FEAT-003, FEAT-005; branch `feat/FEAT-004-user-invitations-and-account-provisioning`
- [ ] FEAT-007 Child Profiles and Enrollment — depends on FEAT-002, FEAT-005; branch `feat/FEAT-007-child-profiles-and-enrollment`
- [ ] FEAT-008 Guardian and Child Relationships — depends on FEAT-004, FEAT-007; branch `feat/FEAT-008-guardian-and-child-relationships`
- [ ] FEAT-009 Classroom Management and Daily Dashboard — depends on FEAT-002, FEAT-007, FEAT-010; branch `feat/FEAT-009-classroom-management-and-daily-dashboard`
- [ ] FEAT-010 Staff Profiles and Assignments — depends on FEAT-002, FEAT-004, FEAT-005; branch `feat/FEAT-010-staff-profiles-and-assignments`

- [ ] TW-026 Implement secure invitation, existing-account linking and single-use acceptance — depends on TW-023,TW-025; owner Backend
- [ ] TW-037 Implement child, guardian, relationship, classroom and staff modules — depends on TW-024,TW-029,TW-036; owner Backend, Web and Mobile

- [ ] DEV-FEAT-004-01 Create, resend, revoke, and expire invitations.
- [ ] DEV-FEAT-004-02 Show invitation status to authorized administrators.
- [ ] DEV-FEAT-004-03 Validate the intended assignment independently of information supplied by the invitee.
- [ ] DEV-FEAT-004-04 Handle existing accounts and new accounts without duplicate membership.
- [ ] DEV-FEAT-007-01 Create, view, edit, transfer, enroll, withdraw, and archive child profiles.
- [ ] DEV-FEAT-007-02 Capture all supplied child profile fields, allowing optional fields to remain blank.
- [ ] DEV-FEAT-007-03 Highlight allergies and urgent care information to authorized care staff.
- [ ] DEV-FEAT-007-04 Restrict medical, insurance, and medication details by role.
- [ ] DEV-FEAT-007-05 Retain history for sensitive changes.
- [ ] DEV-FEAT-008-01 Create and revoke relationships for mother, father, guardian, grandparent, authorized caregiver, emergency contact, and pickup-only contact.
- [ ] DEV-FEAT-008-02 Configure permissions per relationship.
- [ ] DEV-FEAT-008-03 Support one guardian with multiple children and one child with multiple guardians.
- [ ] DEV-FEAT-008-04 Prevent revoked relationships from retaining access.
- [ ] DEV-FEAT-009-01 Create, edit, deactivate, and search classrooms.
- [ ] DEV-FEAT-009-02 Assign and remove children and staff with effective dates.
- [ ] DEV-FEAT-009-03 Warn authorized users when configured capacity would be exceeded.
- [ ] DEV-FEAT-009-04 Show real-time operational classroom status to permitted users.
- [ ] DEV-FEAT-010-01 Create, edit, activate, suspend, and archive employee profiles.
- [ ] DEV-FEAT-010-02 Assign roles, branches, classrooms, and schedules.
- [ ] DEV-FEAT-010-03 Remove access when employment ends or a user is suspended.
- [ ] DEV-FEAT-010-04 Keep future shift, leave, attendance, and payroll extension points as product considerations without implementing full payroll.

## S04 Privacy and platform controls

Consent and lifecycle, audited support, full localization and plan/module controls.

Exit: Privacy review, support expiry, disabled-module denial and bilingual journeys pass.

Approval: pending. Planning envelope: 2 weeks; re-estimate after refinement; no committed dates.

- [ ] FEAT-006 Platform Administration and Audited Support Access — depends on FEAT-001, FEAT-005, FEAT-034; branch `feat/FEAT-006-platform-administration-and-audited-support-access`
- [ ] FEAT-035 Privacy Consent Retention Export and Deletion — depends on FEAT-001, FEAT-005, FEAT-034; branch `feat/FEAT-035-privacy-consent-retention-export-and-deletion`
- [ ] FEAT-036 Arabic English Localization and Regional Settings — depends on FEAT-001; branch `feat/FEAT-036-arabic-english-localization-and-regional-settings`
- [ ] FEAT-037 Configurable Branding Modules and Plans — depends on FEAT-001, FEAT-006; branch `feat/FEAT-037-configurable-branding-modules-and-plans`

- [ ] TW-027 Implement reason-bound, expiring and audited platform support sessions — depends on TW-023; owner Backend and Security
- [ ] TW-029 Implement consent versions, retention state and privacy workflow skeleton — depends on TW-002,TW-028; owner Backend and Privacy
- [ ] TW-033 Implement private upload authorization, quarantine, scanning, transformation and signed delivery — depends on TW-015,TW-023,TW-029,TW-032; owner Backend and Media

- [ ] DEV-FEAT-006-01 Manage organizations, plans, subscriptions, feature availability, and platform metrics.
- [ ] DEV-FEAT-006-02 Expose operational health without showing unnecessary child data.
- [ ] DEV-FEAT-006-03 Require a support reason for exceptional sensitive-data access.
- [ ] DEV-FEAT-006-04 Record who accessed what, why, and when.
- [ ] DEV-FEAT-006-05 Allow authorized review of support-access history.
- [ ] DEV-FEAT-035-01 Capture consent purpose, status, subject, grantor, effective dates, and withdrawal.
- [ ] DEV-FEAT-035-02 Apply consent to media, communications, and authorized uses.
- [ ] DEV-FEAT-035-03 Provide reviewed account-deletion and organization-export workflows.
- [ ] DEV-FEAT-035-04 Apply configurable retention rules with legal-hold or exception handling where approved.
- [ ] DEV-FEAT-035-05 Prevent public exposure of child data.
- [ ] DEV-FEAT-035-06 Require explicit marketing consent for child data or images.
- [ ] DEV-FEAT-036-01 Allow organization and user language preferences.
- [ ] DEV-FEAT-036-02 Provide complete Arabic and English product text for released features.
- [ ] DEV-FEAT-036-03 Support right-to-left layout and mixed-direction content.
- [ ] DEV-FEAT-036-04 Localize dates, numbers, currency, and times using organization settings.
- [ ] DEV-FEAT-036-05 Localize notification content and dynamic placeholders.
- [ ] DEV-FEAT-036-06 Identify untranslated content before release.
- [ ] DEV-FEAT-037-01 Apply tenant branding within approved accessibility constraints.
- [ ] DEV-FEAT-037-02 Enable and disable modules by plan and organization entitlement.
- [ ] DEV-FEAT-037-03 Represent Starter, Growth, and Pro packaging as configurable commercial concepts pending validation.
- [ ] DEV-FEAT-037-04 Handle plan downgrade, suspension, and expired subscription states.
- [ ] DEV-FEAT-037-05 Keep historical data when a module is disabled unless approved lifecycle policy says otherwise.
- [ ] DEV-FEAT-037-06 Prepare for custom domain and dedicated build decisions without implementing them in MVP.

## S05 Attendance and daily care

Attendance, timeline, batch entry and encrypted offline command recovery.

Exit: Staff completes a classroom day; retry and conflict tests show no silent loss or duplication.

Approval: pending. Planning envelope: 2 weeks; re-estimate after refinement; no committed dates.

- [ ] FEAT-011 Child Attendance — depends on FEAT-007, FEAT-009; branch `feat/FEAT-011-child-attendance`
- [ ] FEAT-013 Daily Child Timeline — depends on FEAT-007, FEAT-011; branch `feat/FEAT-013-daily-child-timeline`
- [ ] FEAT-014 Quick and Batch Care Entry — depends on FEAT-009, FEAT-013; branch `feat/FEAT-014-quick-and-batch-care-entry`

- [ ] TW-038 Implement child attendance commands, corrections, QR entry and reporting views — depends on TW-031,TW-037; owner Backend and Mobile
- [ ] TW-039 Implement typed child timeline events and visibility projections — depends on TW-024,TW-037,TW-038; owner Backend and Mobile
- [ ] TW-040 Implement authorized batch care commands with per-child exceptions — depends on TW-031,TW-039; owner Backend and Mobile
- [ ] TW-041 Implement encrypted SQLite working set, local outbox and resumable sync — depends on TW-031,TW-035,TW-038,TW-039; owner Mobile and Backend
- [ ] TW-042 Implement idempotent command receipt and user-visible conflict handling — depends on TW-041; owner Backend, Mobile and QA

- [ ] DEV-FEAT-011-01 Record and correct attendance with controlled permissions.
- [ ] DEV-FEAT-011-02 Support optional parent QR and center-managed QR processes.
- [ ] DEV-FEAT-011-03 Prevent impossible or duplicate attendance transitions.
- [ ] DEV-FEAT-011-04 Show daily, classroom, absenteeism, and trend reports.
- [ ] DEV-FEAT-011-05 Operate through short connectivity interruptions and reconcile safely afterward.
- [ ] DEV-FEAT-013-01 Create event types with appropriate required fields.
- [ ] DEV-FEAT-013-02 Display events chronologically with actor and time where appropriate.
- [ ] DEV-FEAT-013-03 Restrict sensitive event types and fields by role and relationship.
- [ ] DEV-FEAT-013-04 Allow controlled correction while preserving audit history.
- [ ] DEV-FEAT-013-05 Generate a parent-facing daily summary from authorized events.
- [ ] DEV-FEAT-014-01 Provide quick actions for meal outcome, mood, nap, toilet, diaper, and medication administration where permitted.
- [ ] DEV-FEAT-014-02 Allow multi-child selection within authorized scope.
- [ ] DEV-FEAT-014-03 Preview recipients and values before committing a batch.
- [ ] DEV-FEAT-014-04 Edit or exclude exceptions without re-entering the whole batch.
- [ ] DEV-FEAT-014-05 Prevent duplicate submission and preserve child-level records.

## S06 Parent engagement and Phase 1 acceptance

Announcements, notification ledger, calendar, search, parent home and complete demo.

Exit: A representative center completes a full day in English and Arabic.

Approval: pending. Planning envelope: 2 weeks; re-estimate after refinement; no committed dates.

- [ ] FEAT-015 Parent Home and Daily Summary — depends on FEAT-008, FEAT-013, FEAT-017, FEAT-019; branch `feat/FEAT-015-parent-home-and-daily-summary`
- [ ] FEAT-016 Announcements — depends on FEAT-002, FEAT-005, FEAT-009; branch `feat/FEAT-016-announcements`
- [ ] FEAT-017 Notifications and Preference Management — depends on FEAT-013, FEAT-016; branch `feat/FEAT-017-notifications-and-preference-management`
- [ ] FEAT-018 Calendar and Relevant Events — depends on FEAT-002, FEAT-009; branch `feat/FEAT-018-calendar-and-relevant-events`
- [ ] FEAT-019 Administrative Search — depends on FEAT-005, FEAT-007, FEAT-009, FEAT-010; branch `feat/FEAT-019-administrative-search`
- [ ] FEAT-041 Demo Organization and Scenario Data — depends on FEAT-001 through FEAT-019 as applicable; branch `feat/FEAT-041-demo-organization-and-scenario-data`

- [ ] TW-043 Implement parent home, announcements, calendar and relevant search — depends on TW-037,TW-039; owner Backend, Web and Mobile
- [ ] TW-044 Implement notification intent, preference, localization and channel-delivery ledgers — depends on TW-030,TW-032,TW-043; owner Backend and Mobile
- [ ] TW-045 Populate and validate the Happy Kids Nursery demonstration scenarios — depends on TW-020,TW-036,TW-044; owner QA and Product

- [ ] DEV-FEAT-015-01 Support guardians with one or multiple children.
- [ ] DEV-FEAT-015-02 Show current state and today’s authorized summary.
- [ ] DEV-FEAT-015-03 Highlight safety-critical information without clutter.
- [ ] DEV-FEAT-015-04 Link summary items to permitted detail.
- [ ] DEV-FEAT-015-05 Keep stale or unavailable data clearly distinguished from current state.
- [ ] DEV-FEAT-016-01 Target announcements by permitted organization scope.
- [ ] DEV-FEAT-016-02 Validate that publishers cannot target unauthorized branches or classrooms.
- [ ] DEV-FEAT-016-03 Show relevant announcements to staff and guardians.
- [ ] DEV-FEAT-016-04 Track publication and read status.
- [ ] DEV-FEAT-016-05 Notify recipients according to priority and preference rules.
- [ ] DEV-FEAT-017-01 Define notification category, priority, audience, and delivery behavior.
- [ ] DEV-FEAT-017-02 Provide guardian notification preferences.
- [ ] DEV-FEAT-017-03 Identify mandatory safety categories through an approved policy.
- [ ] DEV-FEAT-017-04 Batch low-priority updates where appropriate.
- [ ] DEV-FEAT-017-05 Prevent duplicates and expose delivery status where useful.
- [ ] DEV-FEAT-018-01 Create and maintain calendar entries with dates, audience, location, and status.
- [ ] DEV-FEAT-018-02 Show users only relevant events.
- [ ] DEV-FEAT-018-03 Handle updates and cancellations.
- [ ] DEV-FEAT-018-04 Notify intended audiences according to event and notification rules.
- [ ] DEV-FEAT-019-01 Provide a unified search entry point.
- [ ] DEV-FEAT-019-02 Return only records within the user’s access scope.
- [ ] DEV-FEAT-019-03 Support common name and identifier variations approved for each record type.
- [ ] DEV-FEAT-019-04 Paginate results and handle no-result states.
- [ ] DEV-FEAT-019-05 Avoid exposing sensitive fields in result previews.
- [ ] DEV-FEAT-041-01 Create non-realistic but coherent sample identities and relationships.
- [ ] DEV-FEAT-041-02 Cover key roles and Phase 1 journeys.
- [ ] DEV-FEAT-041-03 Include safe sample activities, invoices, attendance, media placeholders, and messages.
- [ ] DEV-FEAT-041-04 Allow repeatable reset or recreation.
- [ ] DEV-FEAT-041-05 Keep demo data isolated from production customer data and metrics.

## S07 Phase 1 release hardening

Security, accessibility, performance, resilience, backup restore and operational UAT.

Exit: Blocking release controls pass with named specialist signoffs and rollback evidence.

Approval: pending. Planning envelope: 2 weeks; re-estimate after refinement; no committed dates.



- [ ] TW-046 Run tenant, role, relationship, field, media, invitation and support-access abuse suites — depends on TW-022,TW-027,TW-033,TW-045; owner Security and QA
- [ ] TW-047 Complete Arabic, English, RTL and mixed-direction test passes — depends on TW-030,TW-045; owner QA and Arabic Owner
- [ ] TW-048 Complete keyboard, screen-reader, zoom, contrast and touch-target verification — depends on TW-034,TW-035,TW-045; owner QA and Design
- [ ] TW-049 Execute realistic API, sync, notification and media performance tests — depends on TW-006,TW-045; owner Performance QA
- [ ] TW-050 Test queue replay, dead-letter recovery, retry storms, provider failure and database failover — depends on TW-032,TW-044; owner QA and DevOps
- [ ] TW-051 Restore database and protected media into an isolated environment — depends on TW-015,TW-017; owner DevOps and Security
- [ ] TW-052 Validate consent withdrawal, export, deletion, retention and log redaction — depends on TW-029,TW-033,TW-045; owner Privacy and QA
- [ ] TW-053 Finalize dashboards, alerts, runbooks, support procedures and incident response — depends on TW-018,TW-019,TW-050; owner DevOps and Support
- [ ] TW-054 Execute full-day bilingual operational UAT and close blocking defects — depends on TW-010,TW-045,TW-047,TW-052; owner Product and QA
- [ ] TW-055 Run production readiness review and verify rollback — depends on TW-046,TW-054; owner Technical Lead



## S08 Pickup and incidents

Standing/temporary pickup, atomic checkout and incident acknowledgement.

Exit: Safeguarding owner accepts identity, replay, escalation and acknowledgement scenarios.

Approval: pending. Planning envelope: 2 weeks; re-estimate after refinement; no committed dates.

- [ ] FEAT-020 Pickup Persons and Standing Authorization — depends on FEAT-007, FEAT-008, FEAT-034; branch `feat/FEAT-020-pickup-persons-and-standing-authorization`
- [ ] FEAT-021 Temporary Pickup Authorization and Secure Checkout — depends on FEAT-011, FEAT-020; branch `feat/FEAT-021-temporary-pickup-authorization-and-secure-checkout`
- [ ] FEAT-024 Incident Reporting and Acknowledgement — depends on FEAT-007, FEAT-017, FEAT-034; branch `feat/FEAT-024-incident-reporting-and-acknowledgement`

- [ ] TW-056 Implement pickup persons, standing and temporary authorizations, QR or PIN and checkout — depends on TW-004,TW-037,TW-046; owner Backend, Mobile and Safeguarding
- [ ] TW-059 Implement incident capture, escalation, notification, review and acknowledgement — depends on TW-005,TW-028,TW-044; owner Backend, Mobile and Safeguarding

- [ ] DEV-FEAT-020-01 Create, edit, deactivate, and expire pickup persons.
- [ ] DEV-FEAT-020-02 Respect relationship permission to authorize pickup.
- [ ] DEV-FEAT-020-03 Show staff current authorization and identity verification information.
- [ ] DEV-FEAT-020-04 Audit all authorization changes.
- [ ] DEV-FEAT-020-05 Apply privacy minimization to identity information.
- [ ] DEV-FEAT-021-01 Create, revoke, expire, and use temporary authorizations.
- [ ] DEV-FEAT-021-02 Constrain authorization to child, date, time window, and permitted person.
- [ ] DEV-FEAT-021-03 Require staff confirmation of identity and authorization.
- [ ] DEV-FEAT-021-04 Prevent reuse after successful checkout.
- [ ] DEV-FEAT-021-05 Record failed and successful verification attempts appropriately.
- [ ] DEV-FEAT-024-01 Create incident drafts and submit complete reports.
- [ ] DEV-FEAT-024-02 Define severity and escalation rules through approved policy.
- [ ] DEV-FEAT-024-03 Notify relevant managers immediately for critical incidents.
- [ ] DEV-FEAT-024-04 Track parent notification, manager review, and acknowledgement.
- [ ] DEV-FEAT-024-05 Control post-submission amendment and preserve history.

## S09 Private media and messaging

Consent-aware media and scoped conversations with private attachments.

Exit: Revoked-consent, unrelated-child and unauthorized-participant denial tests pass.

Approval: pending. Planning envelope: 2 weeks; re-estimate after refinement; no committed dates.

- [ ] FEAT-022 Photo and Video Sharing with Consent — depends on FEAT-007, FEAT-008, FEAT-013, FEAT-035; branch `feat/FEAT-022-photo-and-video-sharing-with-consent`
- [ ] FEAT-023 Direct Messaging — depends on FEAT-005, FEAT-008, FEAT-009; branch `feat/FEAT-023-direct-messaging`

- [ ] TW-057 Implement child tagging, consent-aware media sharing and revocation behavior — depends on TW-033,TW-037,TW-052; owner Backend, Mobile and Privacy
- [ ] TW-058 Implement controlled guardian and staff conversations with private attachments — depends on TW-023,TW-033,TW-044; owner Backend and Mobile

- [ ] DEV-FEAT-022-01 Upload, process, view, and remove media within authorized scope.
- [ ] DEV-FEAT-022-02 Tag children visible in each item.
- [ ] DEV-FEAT-022-03 Enforce consent before sharing or marketing use.
- [ ] DEV-FEAT-022-04 Provide optimized previews and protected access.
- [ ] DEV-FEAT-022-05 Prevent public discovery or durable public links.
- [ ] DEV-FEAT-022-06 Audit consent changes and sensitive media actions.
- [ ] DEV-FEAT-023-01 Create conversations only among authorized participants.
- [ ] DEV-FEAT-023-02 Send and receive text, images, and approved attachments.
- [ ] DEV-FEAT-023-03 Show read and delivery states.
- [ ] DEV-FEAT-023-04 Retain conversation history according to policy.
- [ ] DEV-FEAT-023-05 Remove access when staff assignments or guardian relationships change.

## S10 Billing and payment reminders

Fee rules, invoices, immutable balances and reminder delivery.

Exit: Finance accepts minor-unit calculations, corrections, access filtering and balances.

Approval: pending. Planning envelope: 2 weeks; re-estimate after refinement; no committed dates.

- [ ] FEAT-026 Fee Plans Discounts and Charge Rules — depends on FEAT-001, FEAT-002, FEAT-005; branch `feat/FEAT-026-fee-plans-discounts-and-charge-rules`
- [ ] FEAT-027 Invoices Balances and Payment History — depends on FEAT-008, FEAT-026, FEAT-034; branch `feat/FEAT-027-invoices-balances-and-payment-history`
- [ ] FEAT-029 Automated Payment Reminders — depends on FEAT-017, FEAT-027; branch `feat/FEAT-029-automated-payment-reminders`

- [ ] TW-060 Implement fee rules, invoices, balances, payment history and reminders — depends on TW-003,TW-036,TW-044; owner Backend, Web and Finance

- [ ] DEV-FEAT-026-01 Create, version, activate, and retire fee plans.
- [ ] DEV-FEAT-026-02 Define recurrence, due dates, eligible branches or services, and currency.
- [ ] DEV-FEAT-026-03 Apply approved discounts with traceable rules.
- [ ] DEV-FEAT-026-04 Preview charges before issuing invoices.
- [ ] DEV-FEAT-026-05 Prevent retroactive changes to issued invoices unless handled through an approved adjustment.
- [ ] DEV-FEAT-027-01 Create, review, issue, cancel, and adjust invoices under controlled permissions.
- [ ] DEV-FEAT-027-02 Calculate invoice and account balances consistently.
- [ ] DEV-FEAT-027-03 Apply payments and preserve payment history.
- [ ] DEV-FEAT-027-04 Show guardians only invoices they are permitted to pay or view.
- [ ] DEV-FEAT-027-05 Provide printable or exportable invoice details where required.
- [ ] DEV-FEAT-029-01 Configure schedule, audience, channel, template, and enabled status.
- [ ] DEV-FEAT-029-02 Use current invoice state before sending.
- [ ] DEV-FEAT-029-03 Stop or suppress reminders for paid, cancelled, disputed, or otherwise excluded invoices.
- [ ] DEV-FEAT-029-04 Prevent duplicate delivery for the same reminder occurrence.
- [ ] DEV-FEAT-029-05 Track reminder outcome.

## S11 Payments and reconciliation

Provider adapter, signature/replay checks and settlement reconciliation.

Exit: Finance/security accept duplicate and out-of-order webhooks and reconciled settlement.

Approval: pending. Planning envelope: 2 weeks; re-estimate after refinement; no committed dates.

- [ ] FEAT-028 Online Payment Processing — depends on FEAT-027, FEAT-034; branch `feat/FEAT-028-online-payment-processing`

- [ ] TW-061 Implement provider adapter, signed webhooks, immutable events and reconciliation — depends on TW-008,TW-060; owner Backend, Finance and Security

- [ ] DEV-FEAT-028-01 Initiate payment for an eligible invoice.
- [ ] DEV-FEAT-028-02 Handle success, failure, cancellation, duplicate, delayed, and reversed outcomes.
- [ ] DEV-FEAT-028-03 Update financial records only from authoritative payment confirmation.
- [ ] DEV-FEAT-028-04 Use a consistent product contract across providers.
- [ ] DEV-FEAT-028-05 Reconcile provider and invoice records.
- [ ] DEV-FEAT-028-06 Protect payment details according to applicable specialist guidance.

## S12 Admissions and operational analytics

Admissions pipeline, waiting list and approved metric projections.

Exit: Operations accepts capacity and metric definitions; Phase 2 release tests pass.

Approval: pending. Planning envelope: 2 weeks; re-estimate after refinement; no committed dates.

- [ ] FEAT-030 Admissions Pipeline — depends on FEAT-002, FEAT-005; branch `feat/FEAT-030-admissions-pipeline`
- [ ] FEAT-031 Waiting List and Capacity Opportunity — depends on FEAT-009, FEAT-030; branch `feat/FEAT-031-waiting-list-and-capacity-opportunity`
- [ ] FEAT-032 Operational and Nursery Analytics — depends on FEAT-011, FEAT-016, FEAT-023, FEAT-027, FEAT-030, FEAT-031; branch `feat/FEAT-032-operational-and-nursery-analytics`

- [ ] TW-062 Implement admissions pipeline, waiting list and capacity opportunity — depends on TW-036,TW-037; owner Backend and Web
- [ ] TW-063 Implement approved operational projections and metric definitions — depends on TW-009,TW-060,TW-062; owner Backend, Web and Product
- [ ] TW-064 Execute safeguarding, finance, consent and end-to-end Phase 2 tests — depends on TW-056,TW-063; owner QA and Specialists

- [ ] DEV-FEAT-030-01 Create and assign leads.
- [ ] DEV-FEAT-030-02 Move leads through valid pipeline states.
- [ ] DEV-FEAT-030-03 Schedule visits and trial days.
- [ ] DEV-FEAT-030-04 Convert accepted prospects into enrollment without duplicate re-entry.
- [ ] DEV-FEAT-030-05 Record loss reasons where approved.
- [ ] DEV-FEAT-030-06 Report pipeline volume and conversion.
- [ ] DEV-FEAT-031-01 Add, rank, pause, offer, enroll, or remove waiting-list entries.
- [ ] DEV-FEAT-031-02 Record eligibility information and ordering rationale.
- [ ] DEV-FEAT-031-03 Detect relevant capacity availability.
- [ ] DEV-FEAT-031-04 Notify authorized administrators of matches.
- [ ] DEV-FEAT-031-05 Preserve history when order or status changes.
- [ ] DEV-FEAT-032-01 Define each metric, period, scope, and source of truth.
- [ ] DEV-FEAT-032-02 Provide organization, branch, classroom, and date filters where applicable.
- [ ] DEV-FEAT-032-03 Restrict financial and sensitive metrics by permission.
- [ ] DEV-FEAT-032-04 Show freshness and incomplete-data conditions.
- [ ] DEV-FEAT-032-05 Support drill-down only where the viewer may access underlying records.

## S13 Later approved modules

Medication, transportation and platform KPIs; scope requires separate approval.

Exit: Medical, transport, privacy and metric owners approve before implementation.

Approval: pending. Planning envelope: 2 weeks; re-estimate after refinement; no committed dates.

- [ ] FEAT-025 Medication Instructions and Administration Record — depends on FEAT-007, FEAT-013, FEAT-034; branch `feat/FEAT-025-medication-instructions-and-administration-record`
- [ ] FEAT-033 Transportation Operations — depends on FEAT-005, FEAT-007, FEAT-017; branch `feat/FEAT-033-transportation-operations`
- [ ] FEAT-038 Platform Commercial KPI Dashboard — depends on FEAT-006, FEAT-027, FEAT-032, FEAT-037; branch `feat/FEAT-038-platform-commercial-kpi-dashboard`

- [ ] TW-065 Complete medical policy review before medication record implementation — depends on TW-001,TW-003; owner Medical and Safeguarding
- [ ] TW-066 Complete transport operating model before route and confirmation implementation — depends on TW-003; owner Operations and Product
- [ ] TW-067 Implement platform commercial KPIs after metric and privacy approval — depends on TW-009,TW-052; owner Product and Finance

- [ ] DEV-FEAT-025-01 Create and approve medication instructions.
- [ ] DEV-FEAT-025-02 Require active authorization before administration recording.
- [ ] DEV-FEAT-025-03 Record medication, dosage, time, staff member, and notes for every administration.
- [ ] DEV-FEAT-025-04 Prevent unauthorized changes to historical administrations.
- [ ] DEV-FEAT-025-05 Display due or missed administrations only to authorized care roles.
- [ ] DEV-FEAT-033-01 Create and maintain transportation resources and routes.
- [ ] DEV-FEAT-033-02 Assign staff and children with effective dates.
- [ ] DEV-FEAT-033-03 Show transportation staff only assigned route and minimum required child information.
- [ ] DEV-FEAT-033-04 Confirm pickup and drop-off.
- [ ] DEV-FEAT-033-05 Notify authorized guardians.
- [ ] DEV-FEAT-033-06 Handle missed, skipped, or exceptional transport outcomes.
- [ ] DEV-FEAT-038-01 Define commercial metrics and authoritative inputs.
- [ ] DEV-FEAT-038-02 Provide period, plan, market, and organization segmentation where appropriate.
- [ ] DEV-FEAT-038-03 Separate operational usage from billed revenue.
- [ ] DEV-FEAT-038-04 Protect tenant-sensitive details in platform views.
- [ ] DEV-FEAT-038-05 Show freshness, exclusions, and data-quality limitations.

## S14 Optional future modules

Staff attendance, community and commerce; scope requires separate approval.

Exit: Separate product case, safeguards and feature acceptance are approved.

Approval: pending. Planning envelope: 2 weeks; re-estimate after refinement; no committed dates.

- [ ] FEAT-012 Staff Attendance — depends on FEAT-010; branch `feat/FEAT-012-staff-attendance`
- [ ] FEAT-039 Optional Parent Community — depends on FEAT-008, FEAT-035, FEAT-037; branch `feat/FEAT-039-optional-parent-community`
- [ ] FEAT-040 Commerce Extension Readiness — depends on FEAT-027, FEAT-028, FEAT-037; branch `feat/FEAT-040-commerce-extension-readiness`

- [ ] TW-068 Complete moderation and safeguarding design before enabling the parent community — depends on TW-001,TW-003; owner Product and Safeguarding
- [ ] TW-069 Approve commerce business case and boundaries before implementation — depends on TW-008; owner Product and Finance

- [ ] DEV-FEAT-012-01 Record staff attendance with timestamp and branch.
- [ ] DEV-FEAT-012-02 Permit authorized corrections with reason and audit history.
- [ ] DEV-FEAT-012-03 Restrict employee attendance details to approved roles.
- [ ] DEV-FEAT-012-04 Provide basic daily staff-presence reporting.
- [ ] DEV-FEAT-039-01 Require organization enablement before the module is available.
- [ ] DEV-FEAT-039-02 Collect explicit parent privacy choices.
- [ ] DEV-FEAT-039-03 Keep community identity and content separate from child records.
- [ ] DEV-FEAT-039-04 Provide moderation, reporting, and access-removal rules before launch.
- [ ] DEV-FEAT-039-05 Prevent default parent-to-parent discovery and messaging.
- [ ] DEV-FEAT-040-01 Document future catalog, order, payment, fulfillment, refund, and commission concepts.
- [ ] DEV-FEAT-040-02 Avoid coupling current billing assumptions to tuition only.
- [ ] DEV-FEAT-040-03 Identify regulatory, tax, refund, and fulfillment decisions before build.
- [ ] DEV-FEAT-040-04 Keep commerce disabled until a separately approved scope exists.
