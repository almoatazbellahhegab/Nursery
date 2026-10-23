# Administration application

TW-011 scaffold only. Next.js/TypeScript strict mode. Dependencies are pinned candidates; install resolution and the lockfile remain blocked by ENV-001. No reproducible build is claimed until `npm install` completes, the resulting lockfile is reviewed and `npm ci` reproduces it.

After restoring access: `npm install`, `npm run typecheck`, `npm run lint`, `npm run format:check`, `npm run build`, `npm run dev`. Run from this directory. This is separate from the root offline review portal.

The shell contains no business rules or authorization. Future protected data must come from the reviewed API contract and server-owned identity. Complete bilingual strings are added on FEAT-036's branch.
