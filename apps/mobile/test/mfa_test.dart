import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:nursery_mobile/runtime/api.dart';
import 'package:nursery_mobile/runtime/mfa.dart';
import 'package:nursery_mobile/runtime/workspace.dart';

Map<String, dynamic> account({bool pending = false}) => {
  'role': 'administrator',
  'csrf_token': 'synthetic-csrf',
  'access_token': 'synthetic-session',
  'organization': {'name': 'Fictional security test'},
  'mfa_required': pending,
  'mfa_enrolled': true,
  'branches': pending
      ? <Map<String, dynamic>>[]
      : [
          {'id': 'synthetic-branch', 'name': 'Maadi', 'active': true},
        ],
};

void main() {
  testWidgets(
    'privileged login waits for MFA before loading operational records',
    (tester) async {
      var verified = false;
      final api = NurseryApi(
        base: Uri.parse('https://fixture.invalid/api/v1/'),
        client: MockClient((request) async {
          if (request.url.path.endsWith('/auth/me')) {
            return http.Response('{"code":"authentication_required"}', 401);
          }
          if (request.url.path.endsWith('/auth/login')) {
            return http.Response(jsonEncode(account(pending: true)), 200);
          }
          if (request.url.path.endsWith('/mfa/verify')) {
            final body = jsonDecode(request.body) as JsonMap;
            expect(body['code'], '123456');
            verified = true;
            return http.Response(jsonEncode({'profile': account()}), 200);
          }
          expect(verified, true);
          return http.Response('{"items":[],"next_cursor":null}', 200);
        }),
      );
      await tester.pumpWidget(ConnectedApp(api: api));
      await tester.pumpAndSettle();
      await tester.enterText(
        find.widgetWithText(TextField, 'Email'),
        'fictional@example.test',
      );
      await tester.enterText(
        find.widgetWithText(TextField, 'Password'),
        'noncredential fixture',
      );
      await tester.tap(find.text('Sign in'));
      await tester.pumpAndSettle();
      expect(find.text('Protect your account'), findsOneWidget);
      expect(find.text('Manage branches'), findsNothing);
      await tester.enterText(
        find.widgetWithText(TextField, 'Verification code'),
        '123456',
      );
      await tester.ensureVisible(find.text('Verify code'));
      await tester.tap(find.text('Verify code'));
      await tester.pumpAndSettle();
      expect(find.text('Manage branches'), findsOneWidget);
      expect(find.text('Verification code'), findsNothing);
    },
  );

  testWidgets(
    'enrollment retains recovery codes until the user acknowledges saving them',
    (tester) async {
      JsonMap? accepted;
      final api = NurseryApi(
        base: Uri.parse('https://fixture.invalid/api/v1/'),
        client: MockClient((request) async {
          if (request.url.path.endsWith('/mfa/begin')) {
            return http.Response('{"secret":"SYNTHETIC-SETUP-KEY"}', 200);
          }
          return http.Response(
            jsonEncode({
              'profile': account(),
              'recovery_codes': List.generate(
                10,
                (i) => 'synthetic-recovery-$i',
              ),
            }),
            200,
          );
        }),
      );
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: MfaForm(
                api: api,
                ar: false,
                profile: {'mfa_required': true, 'mfa_enrolled': false},
                onReady: (value) async {
                  accepted = value;
                },
              ),
            ),
          ),
        ),
      );
      await tester.tap(find.text('Set up authenticator'));
      await tester.pumpAndSettle();
      expect(find.text('SYNTHETIC-SETUP-KEY'), findsOneWidget);
      await tester.enterText(
        find.widgetWithText(TextField, 'Verification code'),
        '123456',
      );
      await tester.ensureVisible(find.text('Verify code'));
      await tester.tap(find.text('Verify code'));
      await tester.pumpAndSettle();
      expect(accepted, isNull);
      expect(find.text('synthetic-recovery-0'), findsOneWidget);
      await tester.ensureVisible(find.text('Continue to workspace'));
      expect(
        tester
            .widget<FilledButton>(
              find.widgetWithText(FilledButton, 'Continue to workspace'),
            )
            .onPressed,
        isNull,
      );
      await tester.tap(find.text('I saved these codes securely'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Continue to workspace'));
      await tester.pumpAndSettle();
      expect(accepted?['role'], 'administrator');
      await tester.pumpWidget(const SizedBox());
      api.close();
    },
  );
}
