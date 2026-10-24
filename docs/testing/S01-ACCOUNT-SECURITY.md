# FEAT-003 connected account-security increment

The original source feature remains in S01. This tested increment adds application
MFA and a response/commit boundary; it does not complete provider login, all account
recovery methods, or the final product. Reviews are waived for implementation under
the recorded user instruction. Source acceptance and UAT are separate.

## Delivered behavior

- Web and Flutter enroll a time-based authenticator, confirm it, retain recovery
  codes until an explicit save acknowledgement, and verify authenticator/recovery
  codes at later sign-in. Arabic controls and RTL are included.
- Enrolled users require MFA at each new application sign-in. In enforced mode,
  administrator, branch-manager and finance roles require MFA before product
  routes; primary authentication alone exposes no branch list or product routes.
- Branch administration requires second-factor proof within 15 minutes. Promotion
  to a privileged role does not upgrade a pre-existing weak session.
- Enrollment is bound to the initiating session, expires after ten minutes and
  revokes other sessions when confirmed. Active/pending seeds and successful retry
  receipts are encrypted; recovery codes are hashed and consumed once.
- Consumed authenticator counters cannot authorize another operation. Exact
  retries are session-bound and return current role/branch scope. Five failed
  verifications per five-minute user window persist across new logins.
- Changes, proof, receipt and minimal audit commit together. A database failure
  deferred until commit produces failure before HTTP success. Request activity is
  updated after business locks, preventing a session/MFA-lock ordering cycle.

## Evidence

Full backend: **259 pass**, including the new deferred-commit regression, plus
Ruff, format, strict typing and dependency checks:
`runs/2026-10-24T15-58-32-780Z-runtime.json`.

Next.js types/lint/format/build and Flutter build pass in
`runs/2026-10-24T15-51-03-240Z-clients.json`. That run failed on a test-only Dart
collection annotation, subsequently fixed. Flutter format, analyzer and all
**14 widget tests** pass in `runs/2026-10-24T15-58-44-421Z-clients.json`; production
mobile source is unchanged from that successful build.

All four real connected browser groups pass in
`runs/2026-10-24T16-06-26-782Z-security-browsers.json`: web enrollment/recovery-save
acknowledgement, Flutter authenticator verification, recovery-code use/reuse denial,
and Arabic controls in both clients. Arabic desktop/mobile screenshots inspected;
screenshots omit seeds, entered codes and recovery material. All 12 targeted
security checks (11 MFA cases including cross-user RLS, plus deferred commit failure)
and coding checks pass in `runs/2026-10-24T16-11-21-404Z-account-security.json`.

## UAT checklist and remaining scope

- [ ] Windows 11 human Chrome/Edge: enrollment, key entry, valid/invalid/fresh code,
      recovery-code acknowledgement, expired/limited sessions and keyboard access.
- [ ] Physical iPhone Safari: authenticator app switching, autofill, keyboard,
      screen reader, recovery storage and Arabic dialogs.
- [ ] Native iPhone: build/sign/install, MFA, app switching, session expiry and RTL.
- [ ] Human Arabic/security operating review and explicit user acceptance.

No automated pass accepts those UAT items. Cognito/OIDC email/phone/Google/Apple
login, provider recovery and provisioning remain unfinished. Non-secret provider
settings were requested asynchronously; implementation can continue with templates
and provider fixtures while pending. No production resource or real message was
created. MFA session-ID rotation, provider expiry bounds, key rotation/backup
operations and generated transport contracts remain final-product hardening work.

Local review mode preserves the ordinary fictional accounts without forced first
enrollment; enrolling any account activates its factor requirement. The dedicated
security-browser fixture resets only its fictional account's security state in
owned nursery_dev, retaining audit. It never resets ordinary accounts or nursery_test.
