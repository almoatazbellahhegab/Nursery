# Localization groundwork scope

Owner: Technical Lead. Status: implementation experiment; full FEAT-036 acceptance pending consolidated S01 (original S04).

The dedicated FEAT-036 branch adds typed Next.js catalogues and Flutter ARB files with framework-generated localization. Only public shell strings and direction switching are included. No organization preferences, notification templates, currency/date policy or authorization is implemented. These require FEAT-001 and approved requirements.

TW-030 groundwork is intentionally started as an isolated presentation experiment before the dependent operational shell is ready. This does not close TW-006, TW-034, TW-035 or FEAT-036. Type checking, Flutter generation, analyzer, widget tests, builds and Arabic owner review remain blocked or pending. User review of the HTML prototype does not approve this code's runtime behavior.
