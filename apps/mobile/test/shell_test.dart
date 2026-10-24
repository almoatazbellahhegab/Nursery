/// FEAT-036 shell scenarios; these do not exercise operational care records.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nursery_mobile/main.dart';

void main() {
  testWidgets('switching experience changes the staff heading', (tester) async {
    await tester.pumpWidget(const NurseryApp());
    await tester.tap(find.text('Parent'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Staff').last);
    await tester.pumpAndSettle();
    expect(find.text('More time for little moments.'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
  testWidgets('switching to Arabic changes the shell direction', (
    tester,
  ) async {
    await tester.pumpWidget(const NurseryApp());
    await tester.tap(find.text('العربية'));
    await tester.pumpAndSettle();
    expect(find.text('أقرب إلى طفلك، طوال اليوم.'), findsOneWidget);
    final context = tester.element(find.byType(Scaffold));
    expect(Directionality.of(context), TextDirection.rtl);
  });

  testWidgets('timeline navigation retains the explicit empty foundation state', (
    tester,
  ) async {
    await tester.pumpWidget(const NurseryApp());
    await tester.tap(find.text('Timeline'));
    await tester.pumpAndSettle();
    expect(
      find.text(
        'No operational records. Authentication and storage are not connected.',
      ),
      findsOneWidget,
    );
  });
}
