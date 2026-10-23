/// FEAT-036 shell scenarios. Execution remains blocked until SDK setup.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nursery_mobile/main.dart';

void main() {
  testWidgets('switching to Arabic changes the shell direction', (tester) async {
    await tester.pumpWidget(const NurseryApp());
    await tester.tap(find.text('العربية'));
    await tester.pumpAndSettle();
    expect(find.text('أقرب إلى طفلك، طوال اليوم.'), findsOneWidget);
    final context = tester.element(find.byType(Scaffold));
    expect(Directionality.of(context), TextDirection.rtl);
  });

  testWidgets('timeline navigation retains the explicit empty foundation state', (tester) async {
    await tester.pumpWidget(const NurseryApp());
    await tester.tap(find.text('Timeline'));
    await tester.pumpAndSettle();
    expect(find.text('No operational records. Authentication and storage are not connected.'), findsOneWidget);
  });
}
