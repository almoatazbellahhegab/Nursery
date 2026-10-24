# Sprint 4 completion checklist and required review evidence

## Explicit user override — later instruction takes precedence

The user subsequently instructed `please skip this review and complete
implementation and testing of the final product`. Outstanding review prerequisites
below are waived for implementation/testing as recorded in AGENTS.md. They are
not specialist-approved and no longer block development. Preserve their original
identifiers and the 41-feature scope. Connected identity/PostgreSQL and staff
web/mobile work now exists; see the latest RESUME and staff test report. Continue
remaining implementation and automated testing, not repeated review requests.
Historical pending/Not run descriptions below are superseded by actual scoped
execution evidence; UAT/deployment/push boundaries remain separate.

Updated 2026-10-24 after the user instruction `complete sprint 4 development`.
This is a concrete delivery/review checklist, not a completion or approval record.
The request authorizes work toward all original S04 scope; it does not supply the
specialist policy content or evidence required by the original gates.

## Current result

FEAT-012 now has connected PostgreSQL/API/Next.js/Flutter staff journeys. All
232 backend scenarios pass, including 14 real identity/RLS and 14 staff API
integration scenarios, plus Ruff lint/format, strict mypy and dependency checks.
TC-FEAT-012-01/02/03 have passing actual API integration coverage; the other
22 S04 source cases and all human/physical/native UAT remain pending. The
explicit waiver permits remaining implementation without the original review
handoff; it does not imply expert signoff or completion of the final product.

| Feature | Original tasks / source cases | Current status | Required predecessors / policy review |
| --- | --- | --- | --- |
| FEAT-012 Staff Attendance | DEV-FEAT-012-01–04; TC-FEAT-012-01–03 | Connected staff implementation; three API cases Pass; onboarding/MFA/large-data refinement and UAT pending | Seeded authoritative profiles/assignments and current role/session access implemented; complete remaining predecessor features |
| FEAT-025 Medication | DEV-FEAT-025-01–05; TC-FEAT-025-01–05 | Five tasks open; five cases Not run | FEAT-007/013/034; TW-065, Medical and Safeguarding |
| FEAT-033 Transport | DEV-FEAT-033-01–06; TC-FEAT-033-01–05 | Six tasks open; five cases Not run | FEAT-005/007/017; TW-066, Operations and Product |
| FEAT-038 Commercial KPIs | DEV-FEAT-038-01–05; TC-FEAT-038-01–04 | Five tasks open; four cases Not run | FEAT-006/027/032/037; TW-067, Product and Finance; approved privacy/data scope |
| FEAT-039 Parent Community | DEV-FEAT-039-01–05; TC-FEAT-039-01–05 | Five tasks open; five cases Not run; not enabled | FEAT-008/035/037; TW-068, Product and Safeguarding; DEC-13 |
| FEAT-040 Commerce Readiness | DEV-FEAT-040-01–04; TC-FEAT-040-01–03 | Four tasks open; three cases Not run; not enabled | FEAT-027/028/037; TW-069, Product and Finance |

Totals remain six features, 29 feature tasks, five technical tasks and 25 source
cases, plus affected cross-cutting checks. The exact original task/case text,
stable UAT IDs and current S04 aliases remain in `plan.json`/`SPRINTS.md`.
Earlier S01–S03 predecessors and their transitive dependencies remain incomplete;
advancing sprints does not replace them with demo state or synthetic grants.

## Original review handoff — historical after explicit waiver

Each review needs approved content/version, a named owner/reviewer, date, scope,
source reference and recorded unresolved limitations. A generic development
instruction or assignment of a reviewer role does not establish that review.
The user was asked for these documents/owners asynchronously in this turn;
none has been supplied at this checkpoint. Existing S01–S03 revision 3 Product
approvals remain valid and must not be requested again as if absent.

### Staff attendance — first active feature

- Approve which staff may view their own presence and which managers/admins may
  record/view/correct other employees, including branch/organization scope and
  fields. Identify the authoritative employee/assignment and revocation source.
- Approve correction reasons, permitted correction age/windows, approval process,
  edit/cancel semantics, inactive-worker handling and cross-branch exceptions.
  Retain original/new values, actor, time and reason in append-only audit.
- Approve report recipients, included employee/status categories, period filters
  and branch-day rules. Reuse the already approved UTC storage/Africa-Cairo
  convention where applicable; do not infer payroll/overtime/leave policy.
- Close FEAT-010, identity/branch/action/storage prerequisites and the applicable
  privacy/field-access gates before the operational API/data model.

### TW-065 — medication, Medical and Safeguarding

- Approved instruction creation/approval roles, guardian authority, effective
  dates, revocation and the exact required instruction/administration fields.
- Approved due/missed administration definitions, discrepancy handling,
  escalation/acknowledgement, historical correction and sensitive-field access.
- Approved medication record retention and audit requirements. The product
  records authorized instructions/actions; it must not recommend treatment.
- Evidence must cover all five medication source cases, including absent,
  expired/revoked authority, dose/detail discrepancy and unauthorized access.

### TW-066 — transport, Operations and Product

- Approved route/stop/resource model, effective staff/child assignments and
  minimum information visible to assigned drivers/transport staff.
- Approved pickup/drop-off actor/identity checks, exception outcomes, missed or
  skipped stops, connectivity-loss behaviour and guardian notification rules.
- Approved event/history/audit and retry behaviour; location/tracking collection
  and retention, if any. Confirmations must remain usable without live tracking.

### TW-067 — commercial KPIs, Product and Finance

- Review the already Product-approved metric formulas from S01–S03 revision 3;
  supply authoritative sources and treatment of trial, paid, grace, suspended,
  cancelled, refunded and incomplete subscription records.
- Approve period/plan/market/organization segmentation, who may view/export
  tenant-level commercial data, and any aggregation/disclosure restrictions.
- Approve freshness/exclusion/data-quality presentation and reconciliation.
  Keep subscription recurring revenue separate from nursery fee collections.
- Close TW-009 metric inputs and TW-052 security/privacy prerequisites.

### TW-068 — parent community, Product and Safeguarding

- Approve organization enablement, explicit parent discovery/profile/messaging
  choices, permitted content and strict separation from child/care/medical/media
  records. No parent-to-parent discovery or messaging is enabled by default.
- Approve moderation ownership/staffing, reports, severity/response targets,
  blocking/removal/appeals, retention and safeguarding escalation.
- Approve opt-out/revocation behaviour and tests proving disabled modules expose
  no content or participant list. DEC-13 remains unresolved until this exists.

### TW-069 — commerce readiness, Product and Finance

- Approve the business case and boundaries for future catalog, orders, payments,
  fulfillment, returns/refunds, tax, commission and consumer-protection roles.
- Identify merchant/fulfillment responsibility, required markets/provider
  interfaces and exclusions. Review separately from existing tuition billing.
- The original feature is readiness: current MVP billing must not require a
  catalog or fulfillment workflow. Keep commerce unavailable until separately
  approved scope exists; the request does not invent that business case.

## Engineering and verification after prerequisites close

1. Complete the active feature before activating the next, retaining individual
   feature branches and integrating tested increments locally into S04.
2. Provision a disposable real PostgreSQL test environment. At this checkpoint
   no PostgreSQL/Docker commands or matching services were found by read-only
   checks; no server was installed or credentials/production data requested.
3. Build reviewed migrations, tenant constraints/RLS, authoritative membership,
   action/field checks, version/employee-resource locking and atomic receipts,
   append-only history/audit and transactional outbox as required per feature.
4. Publish reviewed OpenAPI contracts; connect generated clients to real Next.js
   and Flutter workflows with allowed, denied, empty, conflict and failure states.
5. Run all 25 source cases at specified levels plus affected cross-cutting,
   concurrency, rollback, retry, privacy, localization and accessibility checks.
6. Deliver web/mobile review, release changes, defects, test evidence and UAT
   checklist. Record human Windows 11, emulated browser, physical iPhone Safari
   and signed native iPhone checks independently; the existing demo proves none
   of the unimplemented S04 journeys.
7. Obtain named specialist/Arabic/technical/Product acceptance. Record exact
   S04 push scope and explicit user confirmation before any S04 push.

## Governing instruction

`AGENTS.md`: **"Do not begin policy-dependent implementation before the specified
gates close."** This is why governed implementations remain pending; it is not
an additional approval process invented for this task. No original specification,
baseline decision or source acceptance record is altered by this checklist.
