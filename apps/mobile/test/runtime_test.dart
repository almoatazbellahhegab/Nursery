import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:nursery_mobile/runtime/api.dart';
import 'package:nursery_mobile/runtime/workspace.dart';

Map<String, dynamic> profile() => {
  'role': 'teacher',
  'csrf_token': 'synthetic-csrf',
  'access_token': 'synthetic-session',
  'organization': {'name': 'Fictional Nursery'},
  'branches': [
    {'id': 'branch-fixture', 'name': 'Maadi'},
  ],
};

void main() {
  testWidgets('administrator branch entry keeps its Arabic accessible label', (
    tester,
  ) async {
    final api = NurseryApi(
      base: Uri.parse('https://fixture.invalid/api/v1/'),
      client: MockClient((request) async {
        if (request.url.path.endsWith('/auth/me')) {
          return http.Response('{"code":"authentication_required"}', 401);
        }
        if (request.url.path.endsWith('/auth/login')) {
          return http.Response(
            jsonEncode({...profile(), 'role': 'administrator'}),
            200,
          );
        }
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
    expect(find.text('Manage branches'), findsOneWidget);
    await tester.tap(find.text('العربية'));
    await tester.pumpAndSettle();
    expect(find.text('إدارة الفروع'), findsOneWidget);
    expect(find.textContaining('???'), findsNothing);
  });

  for (final status in [200, 401]) {
    test(
      'late restore $status cannot replace or clear a newer login',
      () async {
        final pending = Completer<http.Response>();
        final api = NurseryApi(
          client: MockClient((request) async {
            if (request.url.path.endsWith('/auth/me')) return pending.future;
            if (request.url.path.endsWith('/auth/login')) {
              return http.Response(jsonEncode(profile()), 200);
            }
            expect(
              request.headers['Authorization'],
              'Bearer synthetic-session',
            );
            expect(request.headers['X-CSRF-Token'], 'synthetic-csrf');
            return http.Response('{}', 200);
          }),
          base: Uri.parse('https://fixture.invalid/api/v1/'),
        );
        final restoring = api.restore();
        await api.login('fictional@example.test', 'noncredential fixture');
        final assertion = expectLater(
          restoring,
          throwsA(
            isA<ApiException>().having(
              (e) => e.code,
              'code',
              'session_changed',
            ),
          ),
        );
        pending.complete(
          http.Response(
            status == 200
                ? jsonEncode({...profile(), 'csrf_token': 'older-session'})
                : '{"code":"authentication_required"}',
            status,
          ),
        );
        await assertion;
        await api.request('staff-attendance/transitions', body: {});
        api.close();
      },
    );
  }

  test(
    'network retry retains operation key and current native session',
    () async {
      final operations = <String>[];
      var failed = false;
      final api = NurseryApi(
        client: MockClient((request) async {
          if (request.url.path.endsWith('login')) {
            return http.Response(jsonEncode(profile()), 200);
          }
          operations.add(request.headers['Idempotency-Key']!);
          expect(request.headers['Authorization'], 'Bearer synthetic-session');
          if (!failed) {
            failed = true;
            throw http.ClientException('Synthetic connection loss');
          }
          return http.Response('{"version":1}', 200);
        }),
        base: Uri.parse('https://fixture.invalid/api/v1/'),
      );
      await api.login('fictional@example.test', 'noncredential fixture');
      final response = await api.request(
        'staff-attendance/transitions',
        body: {'expected_version': 0},
      );
      expect(response['version'], 1);
      expect(operations.length, 2);
      expect(operations.first, operations.last);
      expect(operations.first, matches(RegExp(r'^[a-f0-9-]{36}$')));
      api.close();
    },
  );

  test(
    'invalid login exposes a safe code, not submitted credentials',
    () async {
      final api = NurseryApi(
        client: MockClient(
          (request) async =>
              http.Response('{"code":"invalid_credentials"}', 401),
        ),
        base: Uri.parse('https://fixture.invalid/api/v1/'),
      );
      await expectLater(
        api.login('fictional@example.test', 'noncredential fixture'),
        throwsA(
          isA<ApiException>().having(
            (e) => e.code,
            'code',
            'invalid_credentials',
          ),
        ),
      );
      api.close();
    },
  );

  testWidgets(
    'connected teacher signs in, checks in and sees persisted state',
    (tester) async {
      var signedIn = false;
      var present = false;
      final api = NurseryApi(
        client: MockClient((request) async {
          if (request.url.path.endsWith('/auth/me')) {
            return http.Response('{"code":"authentication_required"}', 401);
          }
          if (request.url.path.endsWith('/auth/login')) {
            signedIn = true;
            return http.Response(jsonEncode(profile()), 200);
          }
          expect(signedIn, true);
          if (request.url.path.endsWith('/transitions')) {
            final body = jsonDecode(request.body) as Map<String, dynamic>;
            expect(body['action'], 'check_in');
            expect(body['expected_version'], 0);
            present = true;
            return http.Response('{"version":1}', 200);
          }
          return http.Response(
            jsonEncode({
              'items': [
                {
                  'id': 'employee-fixture',
                  'display_name': 'Teacher Demo',
                  'active': true,
                  'version': present ? 1 : 0,
                  'open_session_id': present ? 'session-fixture' : null,
                  'open_branch_id': present ? 'branch-fixture' : null,
                },
              ],
            }),
            200,
          );
        }),
        base: Uri.parse('https://fixture.invalid/api/v1/'),
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
      expect(find.text('Teacher Demo'), findsOneWidget);
      await tester.ensureVisible(find.text('Check in'));
      await tester.tap(find.text('Check in'));
      await tester.pumpAndSettle();
      expect(find.text('Check out'), findsOneWidget);
      expect(find.text('Attendance saved.'), findsOneWidget);
    },
  );
}
