# Connected session consistency and staff-history hardening

Older session responses are discarded when a sign-in or sign-out has started.
Flutter preserves the newer bearer/CSRF credentials even if an older restore
returns 401; both clients discard an older successful restore. Web restore also
checks its effect lifetime after JSON parsing. UI authority remains server-owned.
Staff history applies branch filtering before its bounded query and returns the
newest 1,000 events in chronological order, with an explicit truncation flag.

Automated evidence: 233 backend scenarios and all coding checks pass in
`runs/2026-10-24T13-31-40-815Z-runtime.json`; ten Flutter tests, analysis and
formatting pass in `runs/2026-10-24T13-31-40-480Z-clients.json`.
Flutter web compilation succeeded after these production changes. Next.js
types/lint/format/build pass in `runs/2026-10-24T14-31-35-917Z-clients.json`.
All five connected browser groups, including the new delayed-web-restore test,
pass in `runs/2026-10-24T14-37-44-976Z-connected-browsers.json`.
These are Windows Chrome/emulated browser checks; physical iPhone Safari,
native iPhone and human UAT remain unperformed/pending.
