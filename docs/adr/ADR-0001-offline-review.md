# Offline review portal exception

Status: proposed temporary exception; user acceptance pending. Owner: Technical Lead. Tracking: ENV-001.

The specifications select Next.js/TypeScript, Flutter/Dart, FastAPI and PostgreSQL. On 23 October 2026 Flutter and a normal Python installation were absent. A bundled Python runtime exists. npm registry access failed with EACCES in the sandbox and ENOTFOUND after approved escalation. No production stack replacement is approved.

To permit concrete review without installing dependencies, tools/review-server.mjs serves synthetic, dependency-free HTML/CSS/JavaScript prototypes and the delivery plan. The prototype has no operational writes, accounts, permission enforcement, native storage, notifications or production data. A browser mock is never presented as a compiled Flutter app.

Removal condition: restore dependency access, install pinned production dependencies, build actual Next.js and Flutter shells, migrate approved visual direction, and rerun equivalent tests against those apps. S01 stays incomplete until the actual builds and agreed device checks are evidenced. Native iOS compilation and signing require macOS/Xcode and Apple credentials or a configured CI/TestFlight path.

S02 update: registry access has recovered. FastAPI and test dependencies are installed into `services/api/.venv` with resolved versions in `requirements-dev.lock`. Health and FEAT-011 domain checks execute locally. Actual client builds, identity, PostgreSQL and physical-device testing remain open, so the prototype exception is still in effect.
