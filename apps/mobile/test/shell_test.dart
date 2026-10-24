/// Presentation scenarios only; these do not accept operational APIs or roles.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nursery_mobile/main.dart';

void main() {
  testWidgets(
    'teacher link starts in teacher view and reset retains that view',
    (tester) async {
      await tester.pumpWidget(const NurseryApp(initialTeacher: true));
      expect(find.text('Teacher'), findsOneWidget);
      final action = find.byKey(const Key('add-care'));
      await tester.ensureVisible(action);
      expect(action, findsOneWidget);
      await tester.tap(find.byTooltip('Reset demo'));
      await tester.pumpAndSettle();
      expect(find.text('Teacher'), findsOneWidget);
      expect(find.text('Parent'), findsNothing);
      expect(tester.takeException(), isNull);
    },
  );
  Future<void> chooseStaff(WidgetTester tester) async {
    final role = find.byType(DropdownButtonFormField<bool>);
    await tester.ensureVisible(role);
    await tester.tap(role);
    await tester.pumpAndSettle();
    await tester.tap(find.text('Teacher').last);
    await tester.pumpAndSettle();
  }

  testWidgets('parent has a seeded child, invoice and daily events', (
    tester,
  ) async {
    await tester.pumpWidget(const NurseryApp());
    expect(find.text('Adam Demo'), findsWidgets);
    await tester.tap(find.text('Timeline'));
    await tester.pumpAndSettle();
    expect(
      find.text('Arrived and settled in with the classroom team.'),
      findsOneWidget,
    );
    expect(tester.takeException(), isNull);
  });
  testWidgets(
    'staff update reaches parent timeline and reset restores baseline',
    (tester) async {
      await tester.pumpWidget(const NurseryApp());
      await chooseStaff(tester);
      final action = find.byKey(const Key('add-care'));
      await tester.ensureVisible(action);
      await tester.tap(action);
      await tester.pumpAndSettle();
      final update = find.text(
        'Garden play · explored leaves and colours with friends.',
      );
      await tester.ensureVisible(update);
      expect(update, findsOneWidget);
      final role = find.byType(DropdownButtonFormField<bool>);
      await tester.scrollUntilVisible(role, -300);
      await Scrollable.ensureVisible(tester.element(role), alignment: 0.5);
      await tester.pumpAndSettle();
      await tester.tap(role);
      await tester.pumpAndSettle();
      await tester.tap(find.text('Parent').last);
      await tester.pumpAndSettle();
      await tester.scrollUntilVisible(update, 300);
      expect(update, findsOneWidget);
      await tester.tap(find.byTooltip('Reset demo'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Timeline'));
      await tester.pumpAndSettle();
      expect(update, findsNothing);
      expect(tester.takeException(), isNull);
    },
  );
  testWidgets('branch switch selects that branch family', (tester) async {
    await tester.pumpWidget(const NurseryApp());
    await tester.tap(find.text('Maadi Garden'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('New Cairo Grove').last);
    await tester.pumpAndSettle();
    expect(find.text('Layla Demo'), findsWidgets);
    expect(find.text('Adam Demo'), findsNothing);
    expect(tester.takeException(), isNull);
  });
  testWidgets('Arabic demo keeps readable labels and RTL direction', (
    tester,
  ) async {
    await tester.pumpWidget(const NurseryApp());
    await tester.tap(find.text('العربية'));
    await tester.pumpAndSettle();
    final context = tester.element(find.byType(Scaffold));
    expect(Directionality.of(context), TextDirection.rtl);
    expect(find.text('آدم التجريبي'), findsWidgets);
    expect(tester.takeException(), isNull);
  });
}
