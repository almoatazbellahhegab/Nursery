# Flutter mobile application

TW-011 scaffold only. Flutter SDK, generated platform runners and package resolution are unavailable here (ENV-001). This source has not passed formatter, analyzer, widget tests or build. The review portal's mobile screen is an HTML experiment, not this app.

Once Flutter stable is available, run in this directory:

1. `flutter create --platforms=web,ios --project-name nursery_mobile .` to create platform runners. Review generated changes and preserve application source.
2. `flutter pub get`; commit the resolved `pubspec.lock` and record the exact Flutter SDK version in CI.
3. `dart format --output=none --set-exit-if-changed .`, `flutter analyze`, `flutter test`, `flutter build web`.
4. Serve the web build through staging for iPhone Safari review. Browser checks do not validate native plugins or offline storage.
5. On macOS with Xcode and signing configured, run `flutter build ipa` and deliver through an approved device/TestFlight workflow. Physical iPhone UAT remains required.

Future features use presentation/application/data boundaries, generated API clients, secure storage and encrypted offline data. None is stubbed as a working permission or storage boundary.
