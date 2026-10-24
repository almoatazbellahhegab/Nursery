# Verified client build toolchain

Owner: Technical Lead. Status: local build/quality checks passed; live browser/link verification pending at session checkpoint.

The application stack remains Next.js/TypeScript and Flutter. The application web tooling resolves dependencies requiring a newer runtime than the installed global Node 20.11.1. Client verification therefore uses the available Node 24.19.0 runtime. Application setup requires Node 24.19+ and npm 12.2.1, recorded in the web package manifest; root dependency-free review tools can still run on their existing Node baseline.

An interrupted install and the older npm CLI produced an incomplete optional-dependency lock, and the native SWC binary failed to load on Windows. The lock was regenerated with npm 12 in an empty tooling directory and successfully reproduced with npm ci. The web manifest explicitly includes the matching SWC WebAssembly package and uses Next's supported Webpack build path. No application framework or business behavior is replaced. See [Next.js compiler troubleshooting](https://nextjs.org/docs/messages/failed-loading-swc).

Flutter 3.47.8 / Dart 3.13.7 was downloaded into the ignored .tools directory; web/iOS runner files and localization output were generated from existing source. Its resolved package lock is retained. Native iOS compilation still requires macOS/Xcode and signing; the Windows-produced Flutter web build is browser review only.

The previous HTML portal stays available for delivery/test traceability. Compiled applications run separately on ports 3000 and 3200, with a launcher and runbook. These are public foundation shells; identity, PostgreSQL and operational workflow integration remain unfinished. Successful shell builds or browser tests do not accept those missing features.
