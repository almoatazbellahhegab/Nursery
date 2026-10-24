# Administration application

Public Next.js/TypeScript foundation shell. The resolved package lock now reproduces with npm ci. Node 24.19+ and npm 12.2.1 are the verified toolchain. Webpack and the matching SWC WebAssembly dependency provide the build path documented in ADR-0003.

From this directory run `npm ci`, `npm run typecheck`, `npm run lint`, `npm run format:check`, `npm run build` and `npm start`. Run npm using the supported Node runtime. This application is separate from the HTML review portal. The root `Start-Applications.cmd` launches the built web and Flutter web clients; `Test-Applications.cmd` rebuilds and checks both clients.

The shell contains no business rules or authorization. Future protected data must come from the reviewed API contract and server-owned identity. Complete bilingual strings are added on FEAT-036's branch.
