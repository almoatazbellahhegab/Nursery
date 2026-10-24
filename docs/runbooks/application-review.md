# Compiled application shell review

This launcher is separate from the temporary HTML review portal. It runs the actual Next.js administration shell and a compiled Flutter web build. Neither shell has operational data, identity or connected attendance/admissions APIs.

After builds are ready, double-click `Start-Applications.cmd`. It uses Node 24+ (or the available bundled Node 24 runtime), starts Next.js on port 3000 and serves the Flutter web build on port 3200. The console prints a current Wi-Fi URL for iPhone Safari. Both devices must share the network. Private-network firewall access may need to be allowed by the computer owner; the launcher does not alter firewall rules.

Keep the console open; Ctrl+C stops the child services. `NURSERY_APP_NODE` can select the Node 24+ executable. Build files and dependency directories are not committed; lockfiles and source are. See each application's README for reproduction commands.

Flutter web review runs the actual mobile application's Dart code compiled for a browser. It does not verify native plugins, native storage or a signed iPhone installation. Native iOS still requires macOS/Xcode/signing and physical device UAT.
