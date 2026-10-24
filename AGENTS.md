# Delivery rules

- On session reopen, read RESUME.md and TODO.md before continuing; preserve the recorded checkpoint and pending verification scope.

- Preserve the specification files in Document and their identifiers.
- Show progress as itemized updates. Each sprint ends with a reviewable web and mobile result, test evidence, UAT checklist and known limitations.
- Use feat/FEAT-NNN-description for one product feature. Use chore/ or test/ branches for enabling work. Integrate locally into sprint/NN-review without deleting feature branches.
- Commit each coherent tested increment. Never push a sprint or its feature branches until the user explicitly confirms that sprint. Record the confirmation and exact approved scope first.
- Never mark UAT accepted based on automated results. Record Windows 11 browser, physical iPhone Safari, native iPhone and emulated browser checks separately.
- Follow the supplied engineering standards. Production stack: Next.js/TypeScript, Flutter/Dart, FastAPI/Python, PostgreSQL. The offline review portal is a disposable prototype, not the production app or a permission boundary.
- Do not begin policy-dependent implementation before the specified gates close. No real child data or secrets in fixtures.

## User override — 2026-10-24

The user explicitly instructed: `please skip this review and complete implementation
and testing of the final product`. This overrides the outstanding review-gate
prerequisite for implementation and automated testing in this session. Continue
using the approved Product decisions and document additional implementation
defaults. Preserve the original gate identifiers as waived for implementation,
not as specialist-approved or passed. Do not claim specialist signoff, physical
device UAT, production deployment or additional push authorization. Continue to
use fictional fixtures and retain all original specification identifiers.
