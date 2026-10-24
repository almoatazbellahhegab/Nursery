import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:nursery_mobile/runtime/api.dart';
import 'package:nursery_mobile/runtime/branches.dart';

void main() {
  testWidgets('administrator creates a branch and edits its current version', (
    tester,
  ) async {
    final rows = <Map<String, dynamic>>[];
    final api = NurseryApi(
      base: Uri.parse('https://fixture.invalid/api/v1/'),
      client: MockClient((request) async {
        if (request.url.path.endsWith('/members')) {
          return http.Response('{"items":[],"next_cursor":null}', 200);
        }
        if (request.method == 'POST') {
          final body = jsonDecode(request.body) as Map<String, dynamic>;
          expect(body['name'], 'Fictional Riverside');
          expect(body['timezone'], 'Africa/Cairo');
          expect(request.headers['Idempotency-Key'], isNotEmpty);
          if (rows.isEmpty) {
            rows.add({...body, 'id': 'synthetic-branch', 'version': 1});
          } else {
            expect(body['expected_version'], 1);
            rows[0] = {...body, 'id': 'synthetic-branch', 'version': 2};
          }
          return http.Response(jsonEncode(rows[0]), 200);
        }
        return http.Response(
          jsonEncode({'items': rows, 'next_cursor': null}),
          200,
        );
      }),
    );
    await tester.pumpWidget(
      MaterialApp(home: BranchManagement(api: api, ar: false)),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.text('New branch'));
    await tester.pumpAndSettle();
    await tester.enterText(
      find.widgetWithText(TextFormField, 'Branch name'),
      'Fictional Riverside',
    );
    await tester.tap(find.text('Save branch'));
    await tester.pumpAndSettle();
    expect(find.text('Fictional Riverside'), findsOneWidget);
    await tester.tap(find.text('Edit branch'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Save branch'));
    await tester.pumpAndSettle();
    expect(rows[0]['version'], 2);
    await tester.pumpWidget(const SizedBox());
    await tester.pumpAndSettle();
    api.close();
  });
}
