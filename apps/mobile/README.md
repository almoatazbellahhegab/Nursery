# Flutter mobile application

Public Flutter foundation shell. Flutter 3.47.8 / Dart 3.13.7 is now available in the ignored workspace tooling directory. Web/iOS runners and localization source have been generated, and pubspec.lock records the resolved packages. Formatter, analyzer, three widget tests and the Flutter web build have passed locally. Native iOS compilation and physical iPhone UAT have not run. The old HTML mobile preview remains separate from this compiled Dart application.

With the pinned Flutter SDK available, run in this directory:

1. Platform runners already exist; preserve them and the application source.
2. `flutter pub get`; retain `pubspec.lock`. CI and local verification must use Flutter 3.47.8.
3. `dart format --output=none --set-exit-if-changed lib test`, `flutter analyze --no-pub`, `flutter test --no-pub`, `flutter build web --no-pub --no-web-resources-cdn`.
4. The root `Start-Applications.cmd` serves the compiled Flutter web build on port 3200 for same-Wi-Fi iPhone Safari review. Browser checks do not validate native plugins or offline storage. `Test-Applications.cmd` records build/quality evidence for both clients.
5. On macOS with Xcode and signing configured, run `flutter build ipa` and deliver through an approved device/TestFlight workflow. Physical iPhone UAT remains required.

Future features use presentation/application/data boundaries, generated API clients, secure storage and encrypted offline data. None is stubbed as a working permission or storage boundary.
