# Sprint 3 completion decisions — draft for review

Prepared 2026-10-24 after the instruction to continue Sprint 3 through completion.
**Nothing in this packet is approved policy.** Candidate decisions below are
reviewable proposals; they are not defaults or configuration in the application.
The original specifications, identifiers, scope and acceptance cases are unchanged.

## Current boundary

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
