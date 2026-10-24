/// Fictional presentation demo. No identity, storage or operational APIs.
library;

import 'dart:convert';
import 'package:flutter/material.dart';
import 'demo_data.dart';
import 'l10n/app_localizations.dart';

void main() => runApp(
  NurseryApp(initialTeacher: Uri.base.queryParameters['view'] == 'teacher'),
);

class NurseryApp extends StatefulWidget {
  const NurseryApp({this.initialTeacher = false, super.key});
  final bool initialTeacher;
  @override
  State<NurseryApp> createState() => _NurseryAppState();
}

class _NurseryAppState extends State<NurseryApp> {
  Locale _locale = const Locale('en');
  @override
  Widget build(BuildContext context) => MaterialApp(
    onGenerateTitle: (context) => AppLocalizations.of(context)!.appTitle,
    locale: _locale,
    localizationsDelegates: AppLocalizations.localizationsDelegates,
    supportedLocales: AppLocalizations.supportedLocales,
    theme: ThemeData(
      fontFamilyFallback: const ['NotoNaskhArabic'],
      colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xff285947)),
      scaffoldBackgroundColor: const Color(0xfff6f8f2),
      useMaterial3: true,
      cardTheme: const CardThemeData(
        elevation: 0,
        margin: EdgeInsets.only(bottom: 16),
      ),
    ),
    home: FoundationShell(
      initialTeacher: widget.initialTeacher,
      onLanguageChanged: () => setState(() {
        _locale = Locale(_locale.languageCode == 'en' ? 'ar' : 'en');
      }),
    ),
  );
}

typedef DemoRow = Map<String, dynamic>;

class FoundationShell extends StatefulWidget {
  const FoundationShell({
    required this.onLanguageChanged,
    this.initialTeacher = false,
    super.key,
  });
  final VoidCallback onLanguageChanged;
  final bool initialTeacher;
  @override
  State<FoundationShell> createState() => _FoundationShellState();
}

class _FoundationShellState extends State<FoundationShell> {
  DemoRow _data = jsonDecode(demoSeedJson) as DemoRow;
  String _branch = 'B001';
  String _childId = 'C001';
  late bool _staff;
  @override
  void initState() {
    super.initState();
    _staff = widget.initialTeacher;
  }

  int _tab = 0;
  int _generation = 0;
  bool get _ar => Localizations.localeOf(context).languageCode == 'ar';
  String t(String en, String ar) => _ar ? ar : en;
  String text(dynamic label) => (label as DemoRow)[_ar ? 'ar' : 'en'] as String;
  List<DemoRow> rows(String key) => (_data[key] as List).cast<DemoRow>();
  List<DemoRow> get children =>
      rows('children').where((c) => c['branchId'] == _branch).toList();
  DemoRow get child => children.firstWhere((c) => c['id'] == _childId);
  List<DemoRow> get events =>
      rows('events').where((e) => e['childId'] == _childId).toList();
  DemoRow get invoice =>
      rows('invoices').firstWhere((i) => i['childId'] == _childId);
  String money(int minor) => '${minor ~/ 100} ${t('EGP', 'ج.م')}';
  String status(dynamic value) => switch (value) {
    'present' => t('Here now', 'حاضر الآن'),
    'expected' => t('Expected', 'متوقع وصوله'),
    'home' => t('Went home', 'غادر'),
    _ => t('Absent', 'غائب'),
  };
  void feedback(String message) {
    ScaffoldMessenger.of(context)
      ..clearSnackBars()
      ..showSnackBar(SnackBar(content: Text(message)));
  }

  void reset() {
    setState(() {
      _data = jsonDecode(demoSeedJson) as DemoRow;
      _branch = 'B001';
      _childId = 'C001';
      _tab = 0;
      _staff = widget.initialTeacher;
      _generation++;
    });
    feedback(
      t(
        'Demo restored to its starting story.',
        'أعيد العرض إلى القصة الأولية.',
      ),
    );
  }

  void addEvent(String childId, String kind, String en, String ar) {
    final selected = children.firstWhere((c) => c['id'] == childId);
    final educator = rows(
      'staff',
    ).firstWhere((s) => s['classroomId'] == selected['classroomId']);
    (_data['events'] as List).add({
      'id': 'demo-${rows('events').length}',
      'childId': childId,
      'branchId': _branch,
      'time': '11:35',
      'kind': kind,
      'detail': {'en': en, 'ar': ar},
      'staffId': educator['id'],
    });
  }

  void updateCare() {
    setState(() {
      addEvent(
        _childId,
        'care',
        'Garden play · explored leaves and colours with friends.',
        'اللعب في الحديقة · استكشف الأوراق والألوان مع الأصدقاء.',
      );
      _tab = 1;
    });
    feedback(
      t(
        'Sample update added. Switch to Parent to see the same local update.',
        'أضيف تحديث تجريبي. بدّل إلى ولي الأمر لعرض نفس التحديث المحلي.',
      ),
    );
  }

  void attendance(DemoRow c) {
    final arriving = c['status'] == 'expected';
    setState(() {
      c['status'] = arriving ? 'present' : 'home';
      addEvent(
        c['id'] as String,
        arriving ? 'arrival' : 'departure',
        arriving
            ? 'Arrival recorded in the demo.'
            : 'Departure recorded in the demo.',
        arriving
            ? 'سُجل الوصول في العرض التجريبي.'
            : 'سُجلت المغادرة في العرض التجريبي.',
      );
    });
    feedback(
      t(
        'Attendance and timeline updated in this demo.',
        'حُدّث الحضور والسجل في هذا العرض.',
      ),
    );
  }

  Widget card(List<Widget> content, {Color? color}) => Card(
    color: color ?? Colors.white,
    child: Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: content,
      ),
    ),
  );
  Widget heading(String title) => Padding(
    padding: const EdgeInsets.only(bottom: 12),
    child: Text(title, style: Theme.of(context).textTheme.titleLarge),
  );
  Widget timeline() => card([
    heading(t('Today’s story', 'قصة اليوم')),
    if (events.isEmpty)
      Text(
        t(
          'No updates yet. Try a staff care update.',
          'لا توجد تحديثات بعد. جرّب تحديثاً من الفريق.',
        ),
      ),
    for (final event in events)
      Padding(
        padding: const EdgeInsets.symmetric(vertical: 12),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SizedBox(
              width: 50,
              child: Text(
                event['time'] as String,
                style: const TextStyle(color: Color(0xff61735e)),
              ),
            ),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(text(event['detail'])),
                  const SizedBox(height: 6),
                  Text(
                    text(
                      rows(
                        'staff',
                      ).firstWhere((s) => s['id'] == event['staffId'])['name'],
                    ),
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
  ]);
  Widget familySummary() => card([
    Text(
      t('YOUR CHILD’S DAY', 'يوم طفلك'),
      style: Theme.of(context).textTheme.labelMedium,
    ),
    const SizedBox(height: 12),
    heading(text(child['name'])),
    Text(
      '${text(rows('classrooms').firstWhere((r) => r['id'] == child['classroomId'])['name'])} · ${status(child['status'])}',
    ),
    const SizedBox(height: 18),
    Text(
      t('A little closer, all day.', 'أقرب إلى طفلك، طوال اليوم.'),
      style: Theme.of(context).textTheme.headlineSmall,
    ),
    const SizedBox(height: 12),
    Text(
      t(
        'Arrival, meals and little discoveries, shared by the classroom team.',
        'الوصول والوجبات والاكتشافات الصغيرة، يشاركها معك فريق الفصل.',
      ),
    ),
    const SizedBox(height: 16),
    FilledButton.icon(
      onPressed: () => setState(() => _tab = 1),
      icon: const Icon(Icons.schedule),
      label: Text(t('View daily timeline', 'عرض السجل اليومي')),
    ),
  ], color: const Color(0xffe3eddb));
  Widget fees() => card([
    heading(t('October tuition', 'رسوم أكتوبر')),
    Text(invoice['id'] as String, style: Theme.of(context).textTheme.bodySmall),
    const SizedBox(height: 12),
    Text('${t('Tuition', 'الرسوم')}: ${money(invoice['amountMinor'] as int)}'),
    Text('${t('Paid', 'المدفوع')}: ${money(invoice['paidMinor'] as int)}'),
    const Divider(height: 24),
    Text(
      '${t('Balance', 'المتبقي')}: ${money((invoice['amountMinor'] as int) - (invoice['paidMinor'] as int))}',
      style: Theme.of(context).textTheme.titleMedium,
    ),
    const SizedBox(height: 10),
    Text(
      t(
        'Fictional invoice for this family. No payment is requested or processed.',
        'فاتورة خيالية لهذه الأسرة. لا تُطلب أو تُجرى مدفوعات.',
      ),
      style: Theme.of(context).textTheme.bodySmall,
    ),
  ]);
  Widget staffSummary() => card([
    heading(t('More time for little moments.', 'وقت أطول للحظات الصغيرة.')),
    Text(
      '${children.where((c) => c['status'] == 'present').length} ${t('/ ${children.length} children here now', 'من ${children.length} طفلاً حاضراً الآن')}',
      style: Theme.of(context).textTheme.headlineSmall,
    ),
    const SizedBox(height: 12),
    Text(
      t(
        'Select a child, add a care update, then switch to Parent to show the family’s view.',
        'اختر طفلاً وأضف تحديث رعاية، ثم بدّل إلى ولي الأمر لعرض تجربة الأسرة.',
      ),
    ),
    const SizedBox(height: 16),
    FilledButton.icon(
      key: const Key('add-care'),
      onPressed: updateCare,
      icon: const Icon(Icons.add),
      label: Text(t('Add sample care update', 'إضافة تحديث رعاية تجريبي')),
    ),
  ], color: const Color(0xffe3eddb));
  Widget roster() => card([
    heading(t('Branch attendance', 'حضور الفرع')),
    Text(
      t(
        'Demo actions update attendance and the selected child’s timeline locally.',
        'تحدّث الإجراءات الحضور وسجل الطفل محلياً في العرض التجريبي.',
      ),
    ),
    const SizedBox(height: 12),
    for (final c in children)
      Padding(
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              text(c['name']),
              style: Theme.of(context).textTheme.titleSmall,
            ),
            Row(
              children: [
                Expanded(child: Text(status(c['status']))),
                if (['present', 'expected'].contains(c['status']))
                  TextButton(
                    onPressed: () => attendance(c),
                    child: Text(
                      c['status'] == 'expected'
                          ? t('Check in', 'تسجيل وصول')
                          : t('Check out', 'تسجيل مغادرة'),
                    ),
                  ),
              ],
            ),
            const Divider(),
          ],
        ),
      ),
  ]);
  Widget stories() => card([
    heading(t('Show the value', 'اعرض القيمة')),
    ExpansionTile(
      tilePadding: EdgeInsets.zero,
      title: Text(
        t(
          'A two-minute parent & staff story',
          'قصة ولي الأمر والفريق في دقيقتين',
        ),
      ),
      children: [
        Text(
          t(
            '1. Explore Adam’s summary and timeline.\n2. Switch to Staff and add a care update.\n3. Switch back to Parent: the new update is visible.\n4. Switch branch, explore another family, then Reset demo.',
            '١. استكشف ملخص آدم وسجله.\n٢. بدّل إلى الفريق وأضف تحديث رعاية.\n٣. عد إلى ولي الأمر: يظهر التحديث الجديد.\n٤. بدّل الفرع واستكشف أسرة أخرى ثم أعد الضبط.',
          ),
        ),
        const SizedBox(height: 12),
      ],
    ),
    Text(
      t(
        'The web dashboard also demonstrates fee follow-up and admissions visits.',
        'تعرض لوحة الويب أيضاً متابعة الرسوم وزيارات القبول.',
      ),
    ),
  ]);
  @override
  Widget build(BuildContext context) {
    final textL = AppLocalizations.of(context)!;
    return Scaffold(
      appBar: AppBar(
        title: Text(t('Little Garden', 'الحديقة الصغيرة')),
        actions: [
          IconButton(
            tooltip: t('Reset demo', 'إعادة ضبط العرض'),
            onPressed: reset,
            icon: const Icon(Icons.restart_alt),
          ),
          TextButton(
            onPressed: () {
              ScaffoldMessenger.of(context).clearSnackBars();
              widget.onLanguageChanged();
            },
            child: Text(textL.language),
          ),
        ],
      ),
      body: SafeArea(
        child: Align(
          alignment: Alignment.topCenter,
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 680),
            child: ListView(
              key: ValueKey('demo-$_generation'),
              padding: const EdgeInsets.all(20),
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: const Color(0xffe5edda),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    t(
                      'CLIENT DEMO · FICTIONAL DATA\n24 October 2026 · Cairo',
                      'عرض للعملاء · بيانات خيالية\n٢٤ أكتوبر ٢٠٢٦ · القاهرة',
                    ),
                    style: Theme.of(context).textTheme.labelMedium,
                  ),
                ),
                const SizedBox(height: 18),
                DropdownButtonFormField<String>(
                  key: ValueKey('branch-$_generation'),
                  initialValue: _branch,
                  isExpanded: true,
                  decoration: InputDecoration(labelText: t('Branch', 'الفرع')),
                  items: rows('branches')
                      .map(
                        (b) => DropdownMenuItem(
                          value: b['id'] as String,
                          child: Text(text(b['name'])),
                        ),
                      )
                      .toList(),
                  onChanged: (value) => setState(() {
                    _branch = value!;
                    _childId = children.first['id'] as String;
                  }),
                ),
                const SizedBox(height: 14),
                DropdownButtonFormField<bool>(
                  key: ValueKey('role-$_staff-$_generation'),
                  initialValue: _staff,
                  decoration: InputDecoration(
                    labelText: t('Demo experience', 'تجربة العرض'),
                  ),
                  items: [
                    DropdownMenuItem(value: false, child: Text(textL.parent)),
                    DropdownMenuItem(value: true, child: Text(textL.staff)),
                  ],
                  onChanged: (value) => setState(() => _staff = value ?? false),
                ),
                const SizedBox(height: 14),
                DropdownButtonFormField<String>(
                  key: ValueKey('child-$_branch-$_generation'),
                  initialValue: _childId,
                  isExpanded: true,
                  decoration: InputDecoration(
                    labelText: t(
                      'Explore a sample child',
                      'استكشف طفلاً تجريبياً',
                    ),
                  ),
                  items: children
                      .map(
                        (c) => DropdownMenuItem(
                          value: c['id'] as String,
                          child: Text(text(c['name'])),
                        ),
                      )
                      .toList(),
                  onChanged: (value) => setState(() => _childId = value!),
                ),
                const SizedBox(height: 24),
                if (_tab == 0) ...[
                  if (_staff) staffSummary() else familySummary(),
                  if (_staff) roster() else fees(),
                  stories(),
                ],
                if (_tab == 1) ...[
                  heading(
                    '${t('Daily timeline', 'السجل اليومي')} · ${text(child['name'])}',
                  ),
                  if (_staff)
                    FilledButton.icon(
                      key: const Key('add-care'),
                      onPressed: updateCare,
                      icon: const Icon(Icons.add),
                      label: Text(
                        t('Add sample care update', 'إضافة تحديث رعاية تجريبي'),
                      ),
                    ),
                  const SizedBox(height: 16),
                  timeline(),
                ],
                if (_tab == 2) ...[
                  heading(t('Notices for your branch', 'إعلانات فرعك')),
                  for (final notice in rows(
                    'notices',
                  ).where((n) => n['branchId'] == _branch))
                    card([
                      heading(text(notice['title'])),
                      Text(text(notice['body'])),
                    ]),
                ],
                const SizedBox(height: 12),
                Text(
                  t(
                    'All people and figures are fictional. Branch and role selectors explore demo stories, not access controls. Changes stay in this app session and reset on reload; they do not sync with the web dashboard. No live messages or payments.',
                    'كل الأشخاص والأرقام خيالية. اختيار الفرع والدور لاستكشاف القصص التجريبية. التغييرات محلية في هذه الجلسة وتُعاد عند التحميل ولا تتزامن مع لوحة الويب. لا رسائل أو مدفوعات حقيقية.',
                  ),
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
          ),
        ),
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _tab,
        onDestinationSelected: (value) => setState(() => _tab = value),
        destinations: [
          NavigationDestination(
            icon: const Icon(Icons.home_outlined),
            label: textL.home,
          ),
          NavigationDestination(
            icon: const Icon(Icons.schedule),
            label: textL.timeline,
          ),
          NavigationDestination(
            icon: const Icon(Icons.notifications_outlined),
            label: textL.notices,
          ),
        ],
      ),
    );
  }
}
