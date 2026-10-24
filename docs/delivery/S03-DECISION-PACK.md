# Sprint 1–3 decisions — approved product directions and open reviews

Prepared 2026-10-24 after the instruction to continue Sprint 3 through completion.
The user decisions recorded below supersede the corresponding draft proposals.
All remaining candidate decisions are unapproved proposals. No decision here
has been installed as defaults or configuration in the application.
The original specifications, identifiers, scope and acceptance cases are unchanged.

## Approved recommendation package — revision 3, 2026-10-24

Approval evidence: user instruction **`apply all your recommended decisions`**,
immediately following the complete Sprint 1–3 recommendation tables in this
conversation. Approver: requesting user, Product owner. This approves that
package's product directions and proposed operating targets, preserving prior
explicit approvals. It does not supply specialist signoffs, approve production
infrastructure/payments, pass UAT or authorize a new push/deployment. Nothing
below is installed as operational configuration by this documentation change.

This section supersedes older pending-question/proposal descriptions only for
the choices explicitly addressed below. Original DEC/GATE identifiers, owners,
feature prerequisites, source cases and baseline specification text are retained.
Specific supplier choices, field mappings, detailed permission matrices and
specialist evidence not supplied in the package remain implementation inputs.

### Sprint 1 — foundations

| Topic | Approved product direction / operating target | Remaining review or input |
| --- | --- | --- |
| Consent withdrawal | Guardians may withdraw media permission at any time. Immediately block new publication and remove existing content from nursery-controlled channels. Track external-platform removal requests separately; do not promise removal of downloaded copies. | Legal/Privacy/Safeguarding review; authenticate guardian authority. |
| Separate consent purposes | Separate private parent updates, classroom/group sharing and public promotion. Default optional sharing off. Record guardian authority, wording/version, date and withdrawal. | Approved collection/processing basis and guardian verification rules; DEC-01/GATE-01. |
| Privacy requests | Offer access, correction, export and deletion requests. Verify identity/authority before disclosure. Respect approved retention duties and legal holds when handling deletion. | Legal/Privacy process and retention approval. |
| Retention targets | Unsuccessful inquiries: 12 months after closure. Routine care media: 90 days. Security logs: 90 days. Backup rotation: 30 days. | Operating targets only, not statutory periods. Child, medical, safeguarding and financial record periods require specialist approval before production use; holds, start events and deletion/backup procedures need specification. |
| Enrollment fields | Require child name/date of birth, branch/classroom/start date, verified guardian relationship/contact, emergency contact and essential care instructions. Medical information only as necessary for care. Avoid routine national-ID scans, religion and unrelated family information. | Legal/Privacy/Operations review and exact field validation/carry-over mapping. DEC-07; inquiry age bands remain distinct from enrollment date of birth. |
| Permissions | Organization admins: their organization. Branch managers: assigned branches. Teachers: assigned classrooms/children. Guardians: children with verified relationships. Restrict medical, safeguarding and financial fields by task. Provider support: approved, time-limited, audited access. | Detailed field/action/relationship matrix and GATE-02 review; these scopes do not override the stricter approved no-teacher/no-parent admissions access. |
| Identity lifecycle | Individual accounts; privileged-user MFA; immediate revocation on staff departure or guardian-authority change; no shared teacher accounts. | Identity provider, verification/revocation implementation and denial tests. |
| Hosting | Prefer an Egypt-hosted environment if security/recovery requirements are met. Review residency of database, backups, media, logs and support access. | Actual provider/region and GATE-07 approval before production provisioning; preference is not final selection. |
| Devices/accessibility | Windows 11 Chrome/Edge, physical iPhone Safari and native iPhone. Test current and previous supported major versions. Target WCAG 2.2 AA, Arabic RTL, keyboard operation, VoiceOver and readable scaling. | Product/Engineering GATE-05 approval and dated device/version matrix; no conformance/UAT claim yet. |
| Service targets | 99.5% monthly availability; ordinary read p95 ≤2 seconds and write p95 ≤3 seconds; disaster recovery within 4 hours; ≤15 minutes of lost committed data. | Engineering validation against load/cost, measurement definitions and recovery testing; not a contractual SLA or achieved result. |
| Plans/suspension | Configurable branch/active-child/staff limits; 30-day trial; 14-day payment grace. No automatic deletion on downgrade. Preserve emergency information and essential child-safety workflows during commercial suspension; restrict new commercial activity instead. | Actual tier quantities/prices and safety/permissions behaviour under suspension need specification/review; no access after identity revocation is implied. |

### Sprint 2 — daily operations

| Topic | Approved product direction / operating target | Remaining review or input |
| --- | --- | --- |
| Attendance corrections | Teachers record attendance; branch managers/organization admins approve corrections. Require reason; retain original/corrected values, actor and time. Never silently overwrite history. | Operations policy approval and authoritative scope/storage prerequisites. |
| Lateness/early departure | Compare against child branch-local booked schedule. Configurable 15-minute lateness threshold. Departure before booked checkout requires a reason. No automatic penalties. | Schedule/exception semantics and Operations review. |
| Absence | Separate parent-reported absence. Create staff follow-up at 30 minutes after expected arrival for a missing booked child. Review before marking absent. | Operations follow-up/escalation procedure and working schedules. |
| Checkout exceptions | Manager approval alone cannot bypass authorized-person checks. Require documented exception, manager approval and identity verification. Stop unsafe/disputed checkout. | Safeguarding-approved exception and dispute process; GATE-03. |
| Offline conflicts | Mark attendance/care entries pending; retry without duplication. Route contradictions to manager review rather than selecting latest timestamp. Pickup checkout requires authoritative online check. | Conflict UI, secure device storage and transaction/replay design/test evidence. |
| Notifications | Required delivery attempts for safeguarding incidents, pickup-security changes and account-security events. Routine care/announcements/reminders may be muted or digested. Routine quiet hours 20:00–07:00 branch time; urgent alerts bypass. Delivery is not acknowledgement. | Approved channels/recipient authority, escalation and fallback; required categories do not guarantee receipt or bypass legal contact restrictions. |
| Go-live reports | Daily attendance/exceptions, child timeline, missing care entries, pickup history, outstanding invoices and admissions pipeline. Advanced trend dashboards retain planned later scope. | Real feature dependencies and report acceptance remain required; no sprint scope/identifier is removed or rescheduled by this list. |

### Sprint 3 — safety, finance and growth

| Topic | Approved product direction / operating target | Remaining review or input |
| --- | --- | --- |
| Pickup identity | Guardian-authorized collectors with effective dates/revocation; verify identity at collection. QR alone is insufficient. Record verification outcome rather than routine ID images. Refer disputed authority for safeguarding review. | Exact acceptable evidence, access, retention and authority/dispute rules; DEC-03/GATE-03. |
| Temporary pickup | One child, named collector, explicit expiry, single checkout use, immediate revocation and audit. | Authoritative identity, atomic checkout, concurrent revoke/use and exception policies. |
| Media sharing | Default private access for authorized guardians. Check each identifiable child's applicable consent before group sharing; block if missing. Restrict downloads where practical without promising screenshot prevention. | Guardian/consent verification, secure media delivery and privacy review. |
| Messaging | Authorized staff and verified guardians of the relevant child only. No parent directory or parent-to-parent messaging. Preserve conversation history and membership changes. Emergency messages direct users to phone/emergency procedures. | Exact participant permissions, retention, channels and safeguarding procedure. |
| Incidents | Minor/significant/critical with safeguarding-approved definitions. Critical events trigger immediate human action and calls; app records/tracks response. Acknowledgement targets: critical 5 minutes; significant 30 minutes during operating hours; minor by end of day. Escalate unacknowledged cases to deputy. | Category definitions, actual recipients/deputy, availability/fallback and GATE-04 signoff. App targets do not replace emergency procedures. |
| Fees/discounts | EGP integer minor-unit calculations. Effective-dated fee versions. Fixed/percentage discounts with explicit dates and approver. No stacking initially; no retroactive mutation of issued invoices. | Actual fees/discount authority, proration/rounding specifics and Finance review. |
| Invoices | Unique numbers; drafts editable. Correct issued invoices through approved credit/debit adjustments. Show opening balance, charges, payments, adjustments and remaining balance. | Numbering/tax/adjustment details and Finance approval. |
| Payments | Record cash/bank-transfer payments and use one hosted gateway supporting approved Egyptian methods. Never store card numbers/security codes. Verified callbacks, duplicate protection and daily reconciliation. | Actual gateway/methods and Finance/Security approval; payment claims require verified settlement/evidence. |
| Refunds/disputes | Finance approval/reason; distinguish initiated from confirmed refund. Preserve original payments and use linked reversals/adjustments. | Local accountant approval of tax/receipt rules, dispute timelines and provider process. |
| Reminders | 3 days before, 1 day after and 7 days after due date; respect preferences/quiet hours. Stop when paid, disputed or under agreed arrangement. Authorized billing contacts only. | Contact authority, channels, scheduler/delivery ledger and Financial/Privacy review. |
| Waiting list | Branch, approved age band, intended start and capacity eligibility. Eligible applicants ordered by application timestamp; manager overrides documented. Offers expire after 3 business days; no automatic enrollment. | Capacity/age policies, business-day calendar, override authority and atomic reservation design. |
| Admissions reopening | Lost → Contacted with reason/audit; preserve loss history. Branch managers within scope and organization admins may authorize. | Field/action matrix and authoritative authorization prerequisites. |
| Appointments | Reject host double-booking and times outside configured branch hours. Managers/admins may reschedule/cancel with reasons/history. Record only; no invitations. | Branch hours, host assignment and exact appointment status/time rules. |
| Conversion | Copy approved mapped fields after verification; retain source lead link; convert atomically. Flag possible duplicates using matching signals, never auto-merge. Managers resolve within-branch matches; organization admins resolve organization-wide cross-branch matches. | Actual mapping, matching criteria and resolution procedure; authority does not itself approve destructive merging or cross-organization access. |

### Approved metric definitions

| Metric | Product definition |
| --- | --- |
| Occupancy | Booked child places ÷ approved available places for selected branch/date/session; show actual attendance separately. |
| Active parent | Verified guardian who signed in during preceding 30 days. |
| Engagement | Active guardians who viewed at least one child update during period ÷ active guardians. |
| Collection rate | Payments allocated to invoices due in selected period ÷ net amount due on those invoices, at displayed cutoff. |
| Withdrawal | Enrollment ending with approved withdrawal reason; distinguish graduation and branch transfer. |
| Customer churn | Nursery organizations ending paid subscriptions during month ÷ paying organizations at month start. |
| MRR | Recurring monthly subscription revenue excluding tax/one-time charges; annual contracts divided by 12. Keep nursery fee collections separate. |
| ARR | MRR × 12. |
| Admissions conversion | Distinct leads created in selected period that converted by displayed cutoff ÷ distinct eligible leads created in that period. |
| Shared rules | Africa/Cairo branch-local dates; UTC stored instants. Exclude demo/test records; avoid double counting merged records. Zero denominator displays N/A. Display refresh/cutoff times. |

Metric definitions are product-approved, not verified financial/reporting
results. Finance/Product must settle any unaddressed eligibility, refund,
archive or attribution edge cases before affected report acceptance.

### Release ownership and review status

Retain revision 2's owner/reviewer assignments. Add an Arabic-language reviewer
and Engineering release owner, individual names pending. Obtain separate
Operations, Safeguarding, Finance, Privacy, Arabic and technical acceptance,
then final Product acceptance from the user. Record Windows 11 human browser,
physical iPhone Safari and native iPhone UAT separately from automated/emulated
checks. No such review is marked passed by this approval.

| Original decision | Current resolution overlay; baseline remains unchanged |
| --- | --- |
| DEC-01 | Product operating model, consent/request/retention directions approved; Egyptian legal/privacy, statutory periods, breach-response duties, contracts and any required authorizations still open. |
| DEC-02 | Role/scope principles approved; detailed sensitive-field matrix and Product/Safeguarding signoff pending. |
| DEC-03 | Pickup principles approved; exact evidence/retention and Operations/Legal/Safeguarding signoff pending. |
| DEC-04 | Incident categories/acknowledgement targets approved as product directions; severity definitions, recipients and Safeguarding/Operations signoff pending. |
| DEC-05 | Categories, opt-out/digest and quiet-hour directions approved; contact/channel/escalation details pending. |
| DEC-06 | Correction, lateness, early-departure, absence and override directions approved; Operations/Safeguarding review and exact exception procedure pending. |
| DEC-07 | Enrollment field direction approved; exact schema and Privacy review pending. |
| DEC-08 | Device/accessibility/service targets approved as proposed operating targets; Engineering feasibility, release-plan GATE-05 review and actual tests pending. |
| DEC-09 | Metric definitions above product-approved; unresolved boundary details and Finance validation pending. |
| DEC-10 | Go-live report list product-approved; dependent implementations and acceptance pending. |
| DEC-11 | Trial/grace/downgrade/suspension directions approved; actual plan quantities/prices and detailed entitlements pending. |
| DEC-12 | Egypt/EGP/payment/refund/reconciliation directions approved; gateway/method selection, taxes/receipts and Finance/Legal/Security review pending. |
| DEC-13 | Optional parent community remains outside S01–S03 and unapproved; no parent-to-parent messaging is enabled by this package. |
| DEC-14 | Owner/reviewer roles approved, including Arabic/Engineering; individual assignments and actual UAT/release signoffs pending. |

All original GATE-01–07 remain open until their required owners provide the
specific evidence; user Product approval satisfies only its recorded scope.
S03/FEAT-030 remains active; S01/S02 incomplete/unaccepted; S04 not started.
No source acceptance case is passed by approving this package.

Documentation validation on 2026-10-24: plan regeneration retained 41 features,
204 feature tasks, 69 technical tasks and 216 source cases. All four RV-001–004
checks passed via `node --test tests/system/review.test.mjs`; `git diff --check`
passed. Existing baseline decisions/specifications are unchanged. No runtime
code changed, so earlier backend/client results are retained rather than claimed
as rerun. Physical/native/human UAT remains pending.

Reference benchmarks used in the recommendation, not Egyptian legal signoff:
[WCAG 2.2](https://www.w3.org/TR/WCAG22/),
[consent management](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/lawful-basis/consent/how-should-we-obtain-record-and-manage-consent/),
[PCI third-party responsibility](https://www.pcisecuritystandards.org/faqs/1580/).

The earlier revision 2 tables and original proposal/gate material below are
retained for provenance. Their pending labels must be read with revision 3's
resolution overlay rather than interpreted as requests to reconfirm approval.

## User decisions recorded 2026-10-24 — revision 2

Source: the numbered decision questions and user replies in this conversation.
Decision maker and Product owner: the requesting user. Specialist owner roles
are assigned below; their individual names are pending. These are explicit product directions, not specialist
signoff, release acceptance or evidence that all implementation gates are closed.

| Question | Recorded product direction | Conversation evidence |
| --- | --- | --- |
| 1 — Inquiry fields | Require branch, adult contact name, one contact method, child age band, desired start date, inquiry source and assigned staff. | User: `1- yes`. |
| 2 — Workflow | Approve Inquiry → Contacted → Visit scheduled → Trial day → Application → Accepted or Waitlisted. Visits and trials may be skipped; Waitlisted → Accepted is allowed. | User: `2- yes`, followed by the assistant's explicit interpretation. |
| 3 — Loss reasons | Approve timing, location, capacity, fees, another provider, no longer seeking care and other. A loss reason is mandatory; lost leads may reopen. | User: `3- yes`, followed by the assistant's explicit interpretation. |
| 3 — Reopening authority | Both branch managers and organization administrators may authorize reopening. | User: `both`, answering the explicit role choice. |
| 4 — Appointment fields | Require branch, date/time and assigned host for every visit or trial appointment. | User: `yes` to the required-field question; the notification choice was clarified afterward. |
| 4 — Scheduling effects | Only record the appointment; do not send an invitation as part of scheduling. | User: `only record`. |
| 5 — Enrollment conversion | Both branch managers and organization administrators may convert accepted leads, carrying over approved inquiry details. Possible duplicate child/family records must be resolved before conversion. | User: `yes` to the explicit conversion proposal. |
| 6 — Reports | Provide current pipeline counts, leads created during a selected period and enrollment conversion rate. For conversion, use leads created in the selected period as the denominator and display the observation cutoff date. | User: `yes` to all three reports and the explicit denominator/cutoff proposal. |
| 7 — Admissions access | Branch managers manage leads only within their own branches. Organization administrators manage leads across branches within their organization. Teachers and parents have no admissions access. | User: `yes` to the explicit access proposal. |
| 8 — Decision ownership | Adopt the recommended owner/reviewer structure below, with the user as Product owner and other individual names pending. | User: `apply your recommendations`, following the explicit proposal to record the role structure. |

### Approved responsibility structure

| Area | Accountable owner | Supporting reviewer | Assignment status |
| --- | --- | --- | --- |
| Product/business rules | Requesting user, as Product owner | Nursery operations manager | Product owner assigned; supporting individual's name pending |
| Privacy and retention | Nursery owner/director | Privacy adviser or local legal counsel | Roles assigned; individual names pending |
| Safeguarding and sensitive-field permissions | Designated safeguarding lead | Operations manager and Product owner | Roles assigned; individual names pending except Product owner |
| Finance | Finance manager or accountant | Local tax/legal adviser | Roles assigned; individual names pending |
| Security and hosting/data residency | Technical/security lead | Privacy/legal adviser; nursery owner approves final hosting choice | Roles assigned; individual names pending |

One person may cover multiple roles in a small team, with appropriate specialist
review. Role assignment does not record any specialist review as completed.
The original GATE-01–07 owners and required signoffs below remain in force;
this structure supplies accountable coordination rather than replacing them.
In particular, named legal/privacy/security/executive participation for hosting
and the original Product/Safeguarding field-permission review are still required.

This does not grant branch managers cross-branch access. Exact permission scope,
reopening destination/reason/audit requirements, free-text handling, validation
details and specialist privacy/field-access approval remain to be resolved.
Appointment availability, rescheduling and cancellation rules remain open.
Conversion field mapping, duplicate matching criteria and duplicate-resolution
authority remain to be specified; conversion authority alone does not approve
record merging or cross-branch access. Report timezone/day boundaries, distinct
lead/enrollment counting, archived/merged/demo exclusions, zero-denominator
display and attribution details remain open. Question 8's role structure is
approved; individual specialist names and signoff evidence remain pending.
The access direction does not establish authentication,
authoritative branch membership or specialist GATE-02 signoff. The tables below retain their original proposals;
use this record to distinguish accepted product directions from open details.

## Current boundary

### Cross-sprint decisions — one-at-a-time review

| Decision | Approved direction | Evidence / remaining scope |
| --- | --- | --- |
| Initial production market | Egypt only for the first production release; European markets deferred to a later release. | User: `yes` to the explicit initial-market question. This scopes DEC-01 and DEC-12; it does not approve privacy rules, hosting region or payment methods. |
| Nursery/provider data-handling model | Each nursery organization controls why its child/family data is used; the software provider handles it only on that nursery's instructions. | User: `yes` to the explicit operating-model question. Product direction only; legal/privacy review, contractual duties and any provider obligations remain unresolved. |
| Provider secondary use | Prohibit provider use of identifiable child/family data for advertising, resale or AI-model training. | User: `yes` to the explicit prohibition question. No permission for anonymized/aggregate secondary use is inferred; legal/privacy and contract review remain pending. |
| Public/promotional child media | Require separate guardian opt-in for public or promotional use of a child's photos/videos. Refusal must not affect ordinary nursery services. | User: `yes` to the explicit opt-in/no-service-impact question. This does not authorize private sharing, establish guardian authority or complete specialist consent review. |

Next question: whether guardians may withdraw public/promotional media permission
at any time, immediately blocking new public/promotional publication. Existing
publication handling remains a separate decision. The approved directions are not a legal determination or
closure of DEC-01; guardian authority and consent implementation remain open.

Sprint 3 retains 12 features, 63 feature tasks, nine technical tasks and 55
assigned source cases, plus repeated applicable cross-cutting checks. FEAT-030
is the sole active product feature. Its tested stage/history/retry engine is a
domain increment, not an operational admissions journey. The client demo is a
local simulation. No complete S03 feature or sprint acceptance is recorded.

Git metadata writes were authorized through host escalation. The user explicitly
approved pushing the committed S03 scope on 2026-10-24; `sprint/03-review` through
`a9868ba` and the five retained work branches were pushed. This resolves the
earlier Git handoff blocker; product/specialist decisions remain open.

## Admissions decisions that Product must resolve

| Decision | Concrete candidate for review | Required review / remaining choice |
| --- | --- | --- |
| Inquiry fields | Branch, adult contact display name, one contact method, child age band, desired start, inquiry source and assigned staff. Notes optional; avoid unrestricted sensitive notes. | Product must mark each field required/optional/prohibited; Privacy must review the PII model under GATE-01. No production model exists yet. |
| Workflow edges | Inquiry → contacted; contacted → visit scheduled; visit scheduled → trial day or application; trial day → application; application → accepted or waitlisted; waitlisted → accepted; any non-enrolled stage → lost with an approved reason. | Product must approve each edge, required fields and whether direct application/no-visit journeys are allowed. Enumeration order does not authorize transitions. |
| Reopening | Lost → contacted only through a separately authorized action with reason and audit. | Product must approve whether reopening is allowed and who can do it. No role defaults are implemented. |
| Visits / trials | Store a UTC appointment with branch-local display, assigned host, status and cancellation/reschedule history. | Approve required details, host/branch availability rules, consent/contact rules and notification behaviour. No real invitation is sent by the demo. |
| Enrollment conversion | Conversion is a separate atomic operation, not a stage edit. Copy only approved fields, retain source lead linkage and require resolution of any possible existing family/child match. | Approve field carry-over, matching criteria and who resolves ambiguous matches. FEAT-007/FEAT-008 operational onboarding and authoritative permissions remain prerequisites. |
| Loss reasons | Candidate controlled list: timing, location, capacity, fees, chose another provider, no longer seeking care, other. | Product must approve values, access, whether optional text is permitted and the required reason rules. No production list is shipped. |
| Pipeline volume | Proposed as-of stage count by authorized branch, with explicit exclusions for deleted/demo records. | Approve timezone/day boundaries, archived/merged/lost treatment and date semantics. |
| Conversion | Candidate cohort measure: distinct leads created in the selected date window that have one authoritative enrollment conversion, divided by eligible distinct created leads; show cohort window and observation cutoff. | Product/Finance must approve the denominator, exclusions, zero-denominator display and attribution rules. This proposal is not an implemented metric. |

Approval records need the decision/version, approved content, named owner, date,
scope and evidence/reference. A generic instruction to continue or an engineering
test pass does not close these business decisions or specialist gates.

## Sprint-wide dependency and gate checklist

| Feature | Required predecessors retained from plan | Additional gate / input |
| --- | --- | --- |
| FEAT-030 Admissions | FEAT-002, FEAT-005 | Decisions above; authoritative identity/branch grants and durable PostgreSQL transactions. |
| FEAT-020 Standing Pickup | FEAT-007, FEAT-008, FEAT-034 | GATE-03 pickup identity evidence/retention; applicable field permissions. |
| FEAT-021 Temporary Pickup / Checkout | FEAT-011, FEAT-020 | GATE-03; replay-safe atomic checkout and approved exception rules. |
| FEAT-022 Consent-aware Media | FEAT-007, FEAT-008, FEAT-013, FEAT-035 | Approved consent/privacy/field access and private media delivery. |
| FEAT-023 Messaging | FEAT-005, FEAT-008, FEAT-009 | Approved participant/relationship permissions; private attachment and delivery prerequisites. |
| FEAT-024 Incidents | FEAT-007, FEAT-017, FEAT-034 | GATE-04 severity, escalation, acknowledgement and response rules; GATE-02 field permissions. |
| FEAT-026 Fees / Discounts | FEAT-001, FEAT-002, FEAT-005 | Approved financial field permissions and fee/discount calculation rules. |
| FEAT-027 Invoices / Balances | FEAT-008, FEAT-026, FEAT-034 | Approved corrections, amounts, audit and recipient rules. |
| FEAT-028 Payments | FEAT-027, FEAT-034 | GATE-06 markets/methods/tax/refund/dispute/reconciliation review. |
| FEAT-029 Payment Reminders | FEAT-017, FEAT-027 | Approved recipients, schedules/preferences and delivery ledger. |
| FEAT-031 Waiting List / Capacity | FEAT-009, FEAT-030 | Approved capacity, age/date/branch eligibility and offer rules. |
| FEAT-032 Analytics | FEAT-011, FEAT-016, FEAT-023, FEAT-027, FEAT-030, FEAT-031 | DEC-09/DEC-10 and TW-009 metric/report definitions and data scope. |

Foundational FEAT-001/002/003/005/007/008/009/034/035 and durable storage are not
completed by demo selectors or synthetic domain grants. Plan a predecessor
increment explicitly before claiming dependent operational workflows work.

## Specialist gates — original ownership and scope

| Gate | Source decision | Owner | Required by |
| --- | --- | --- | --- |
| GATE-01 | Privacy/controller/processor/retention/deletion/breach/cross-border handling | Legal, Privacy, Product | Production data model and hosting region approval. |
| GATE-02 | Sensitive field permission matrix | Product, Safeguarding | Dependent APIs. |
| GATE-03 | Pickup identity evidence and retention | Operations, Legal, Safeguarding | FEAT-020 / FEAT-021. |
| GATE-04 | Incident severity, escalation, acknowledgement, response | Safeguarding, Operations | FEAT-024. |
| GATE-05 | Devices, browsers, accessibility, availability and response targets | Product, Engineering | Release test-plan approval. |
| GATE-06 | Egypt payments, tax, refund, disputes and reconciliation | Finance, Legal, Product | FEAT-028. |
| GATE-07 | Production region and data residency | Legal, Security, Executive Sponsor | Production infrastructure approval. |

These are copied in meaning from the Technical Design's Assumptions and Decision
Gates. This packet provides no legal, medical, safeguarding or finance approval.

## Completion evidence still required

- [ ] All original feature tasks and TW-056–TW-064 complete with their prerequisites.
- [ ] Authorized Next.js and Flutter business journeys connected to real APIs.
- [ ] PostgreSQL tenant constraints/RLS, concurrent writes, atomic receipts/audit,
  failures and retries tested with authoritative identity/permissions.
- [ ] Execute all 55 assigned source cases at specified levels and applicable
  repeated XCT/TECH cases; retain failures and source/UAT links.
- [ ] Reviewable web/mobile result, test report, release notes, UAT checklist,
  open defects and known limitations.
- [ ] Human Windows 11 browser, physical iPhone Safari and native iPhone checks
  recorded separately from emulation and automated tests.
- [ ] Named specialist and user acceptance; coherent commits and local review
  integration on retained branches. Confirm exact expanded scope before push.

The latest S03 push approval covers work through `5134ba2` plus its approval
record, including the client demo and initial retry implementation. Subsequent
development remains outside that recorded scope. The push does not accept UAT,
waive open gates or authorize production deployment. S04 is not being started.
