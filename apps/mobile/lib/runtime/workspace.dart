/// Staff workspace backed by the same authenticated PostgreSQL API as the web app.
library;

import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import 'api.dart';

class ConnectedApp extends StatefulWidget {
  final NurseryApi? api;
  const ConnectedApp({super.key, this.api});
  @override
  State<ConnectedApp> createState() => _ConnectedAppState();
}

class _ConnectedAppState extends State<ConnectedApp> {
  bool _ar = false;
  late final NurseryApi _api = widget.api ?? NurseryApi();
  @override
  void dispose() {
    _api.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => MaterialApp(
    debugShowCheckedModeBanner: false,
    locale: Locale(_ar ? 'ar' : 'en'),
    localizationsDelegates: AppLocalizations.localizationsDelegates,
    supportedLocales: AppLocalizations.supportedLocales,
    theme: ThemeData(
      colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xff275c45)),
      useMaterial3: true,
      fontFamily: _ar ? 'NotoNaskhArabic' : null,
    ),
    home: StaffWorkspace(
      api: _api,
      ar: _ar,
      onLanguage: () => setState(() => _ar = !_ar),
    ),
  );
}

class StaffWorkspace extends StatefulWidget {
  final NurseryApi api;
  final bool ar;
  final VoidCallback onLanguage;
  const StaffWorkspace({
    super.key,
    required this.api,
    required this.ar,
    required this.onLanguage,
  });
  @override
  State<StaffWorkspace> createState() => _StaffWorkspaceState();
}

class _StaffWorkspaceState extends State<StaffWorkspace> {
  final _email = TextEditingController();
  final _password = TextEditingController();
  JsonMap? _profile;
  String _branch = '';
  List<JsonMap> _employees = [];
  bool _busy = false;
  String _message = '';
  String t(String en, String ar) => widget.ar ? ar : en;
  bool get _staffAccess => [
    'administrator',
    'branch_manager',
    'teacher',
  ].contains(_profile?['role']);
  bool get _correctionAccess =>
      ['administrator', 'branch_manager'].contains(_profile?['role']);
  @override
  void initState() {
    super.initState();
    _restore();
  }

  @override
  void dispose() {
    _email.dispose();
    _password.dispose();
    super.dispose();
  }

  Future<void> _restore() async {
    try {
      final profile = await widget.api.restore();
      if (mounted) await _accept(profile);
    } on ApiException {
      /* A missing/expired session opens the sign-in form. */
    }
  }

  Future<void> _accept(JsonMap profile) async {
    final branches = (profile['branches'] as List).cast<JsonMap>();
    setState(() {
      _profile = profile;
      _branch = branches.isEmpty ? '' : branches.first['id'] as String;
    });
    if (_staffAccess && _branch.isNotEmpty) await _load();
  }

  Future<void> _load() async {
    final data = await widget.api.request(
      'staff-attendance/employees?branch_id=$_branch',
    );
    if (mounted) {
      setState(() => _employees = (data['items'] as List).cast<JsonMap>());
    }
  }

  Future<void> _run(Future<void> Function() action) async {
    if (_busy) return;
    setState(() {
      _busy = true;
      _message = '';
    });
    try {
      await action();
    } on ApiException catch (error) {
      if (mounted) {
        setState(() {
          if (error.status == 401) _profile = null;
          _message = error.code == 'invalid_credentials'
              ? t(
                  'Check your email and password.',
                  'تحقق من البريد وكلمة المرور.',
                )
              : t(
                  'Unable to complete the action. Refresh and try again.',
                  'تعذر إتمام الإجراء. حدّث وحاول مجدداً.',
                );
        });
      }
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  String _time(String value) {
    final date = DateTime.parse(value).toLocal();
    return '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')} ${date.hour.toString().padLeft(2, '0')}:${date.minute.toString().padLeft(2, '0')}';
  }

  Future<void> _change(JsonMap employee) => _run(() async {
    await widget.api.request(
      'staff-attendance/transitions',
      body: {
        'employee_id': employee['id'],
        'branch_id': _branch,
        'expected_version': employee['version'],
        'action': employee['open_session_id'] == null
            ? 'check_in'
            : 'check_out',
      },
    );
    await _load();
    if (mounted) {
      setState(() => _message = t('Attendance saved.', 'تم حفظ الحضور.'));
    }
  });
  Future<void> _history(JsonMap employee) => _run(() async {
    final data = await widget.api.request(
      'staff-attendance/history?branch_id=$_branch&employee_id=${employee['id']}',
    );
    if (!mounted) return;
    final events = (data['events'] as List).cast<JsonMap>();
    final corrections = (data['corrections'] as List).cast<JsonMap>();
    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      builder: (context) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  '${employee['display_name']} · ${t('History', 'السجل')}',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                if (events.isEmpty)
                  Text(t('No attendance recorded yet.', 'لم يسجل حضور بعد.')),
                ...events.map(
                  (event) => ListTile(
                    contentPadding: EdgeInsets.zero,
                    title: Text(
                      event['action'] == 'check_in'
                          ? t('Check in', 'حضور')
                          : t('Check out', 'انصراف'),
                    ),
                    subtitle: Text(_time(event['effective_at'] as String)),
                    trailing: _correctionAccess
                        ? IconButton(
                            tooltip: t('Correct time', 'تصحيح الوقت'),
                            icon: const Icon(Icons.edit_outlined),
                            onPressed: () {
                              Navigator.pop(context);
                              _correct(employee, event);
                            },
                          )
                        : null,
                  ),
                ),
                ...corrections.map(
                  (item) => ListTile(
                    title: Text(item['reason'] as String),
                    subtitle: Text(
                      '${_time(item['original_at'] as String)} → ${_time(item['corrected_at'] as String)}',
                    ),
                  ),
                ),
                Text(
                  t(
                    'Times shown in your device timezone.',
                    'الأوقات بتوقيت جهازك.',
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  });
  Future<void> _correct(JsonMap employee, JsonMap event) async {
    // Leave the history action before opening the correction editor.
    await Future<void>.delayed(Duration.zero);
    if (!mounted) return;
    final initial = DateTime.parse(event['effective_at'] as String).toLocal();
    final first = DateTime.now().subtract(const Duration(days: 7));
    if (initial.isBefore(first)) {
      setState(
        () => _message = t(
          'This record is outside the correction window.',
          'هذا السجل خارج فترة التصحيح.',
        ),
      );
      return;
    }
    final date = await showDatePicker(
      context: context,
      initialDate: initial,
      firstDate: DateTime.now().subtract(const Duration(days: 7)),
      lastDate: DateTime.now(),
    );
    if (date == null || !mounted) return;
    final time = await showTimePicker(
      context: context,
      initialTime: TimeOfDay.fromDateTime(initial),
    );
    if (time == null || !mounted) return;
    final reason = TextEditingController();
    final approved = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(t('Reason for correction', 'سبب التصحيح')),
        content: TextField(
          controller: reason,
          maxLength: 500,
          decoration: InputDecoration(labelText: t('Reason', 'السبب')),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: Text(t('Cancel', 'إلغاء')),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: Text(t('Save correction', 'حفظ التصحيح')),
          ),
        ],
      ),
    );
    final text = reason.text.trim();
    reason.dispose();
    if (approved != true || !mounted) return;
    if (text.length < 3) {
      setState(() => _message = t('A reason is required.', 'السبب مطلوب.'));
      return;
    }
    await _run(() async {
      await widget.api.request(
        'staff-attendance/corrections',
        body: {
          'employee_id': employee['id'],
          'branch_id': _branch,
          'event_id': event['id'],
          'expected_version': employee['version'],
          'reason': text,
          'corrected_at': DateTime(
            date.year,
            date.month,
            date.day,
            time.hour,
            time.minute,
          ).toUtc().toIso8601String(),
        },
      );
      await _load();
      if (mounted) {
        setState(
          () => _message = t(
            'Correction saved; original retained.',
            'حُفظ التصحيح مع الاحتفاظ بالأصل.',
          ),
        );
      }
    });
  }

  Future<void> _report() => _run(() async {
    final data = await widget.api.request(
      'staff-attendance/daily?branch_id=$_branch',
    );
    if (!mounted) return;
    final items = (data['items'] as List).cast<JsonMap>();
    await showDialog<void>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('${t('Daily presence', 'الحضور اليومي')} · ${data['day']}'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(data['timezone'] as String),
              ...items.map(
                (item) => ListTile(
                  title: Text(item['display_name'] as String),
                  subtitle: Text(
                    '${(item['seconds_present'] as int) ~/ 60} ${t('minutes', 'دقيقة')}',
                  ),
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(t('Close', 'إغلاق')),
          ),
        ],
      ),
    );
  });
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(
      title: Text(t('Nursery', 'الحضانة')),
      actions: [
        TextButton(
          onPressed: widget.onLanguage,
          child: Text(widget.ar ? 'English' : 'العربية'),
        ),
        if (_profile != null)
          IconButton(
            tooltip: t('Sign out', 'تسجيل الخروج'),
            onPressed: _busy
                ? null
                : () => _run(() async {
                    await widget.api.logout();
                    if (mounted) {
                      setState(() {
                        _profile = null;
                        _employees = [];
                      });
                    }
                  }),
            icon: const Icon(Icons.logout),
          ),
      ],
    ),
    body: SafeArea(
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 900),
          child: ListView(
            padding: const EdgeInsets.all(24),
            children: [
              if (_busy) const LinearProgressIndicator(),
              if (_message.isNotEmpty)
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  child: Semantics(liveRegion: true, child: Text(_message)),
                ),
              if (_profile == null) ...[
                const SizedBox(height: 40),
                Text(
                  t('Welcome back.', 'مرحباً بعودتك.'),
                  style: Theme.of(context).textTheme.headlineLarge,
                ),
                const SizedBox(height: 24),
                AutofillGroup(
                  child: Column(
                    children: [
                      TextField(
                        controller: _email,
                        autofillHints: const [AutofillHints.username],
                        keyboardType: TextInputType.emailAddress,
                        decoration: InputDecoration(
                          labelText: t('Email', 'البريد الإلكتروني'),
                        ),
                      ),
                      const SizedBox(height: 16),
                      TextField(
                        controller: _password,
                        obscureText: true,
                        autofillHints: const [AutofillHints.password],
                        decoration: InputDecoration(
                          labelText: t('Password', 'كلمة المرور'),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                FilledButton(
                  onPressed: _busy
                      ? null
                      : () => _run(() async {
                          final profile = await widget.api.login(
                            _email.text.trim(),
                            _password.text,
                          );
                          _password.clear();
                          if (mounted) await _accept(profile);
                        }),
                  child: Text(t('Sign in', 'دخول')),
                ),
              ] else ...[
                Text((_profile!['organization'] as JsonMap)['name'] as String),
                Text(
                  t('Staff attendance', 'حضور الموظفين'),
                  style: Theme.of(context).textTheme.headlineMedium,
                ),
                const SizedBox(height: 24),
                DropdownButtonFormField<String>(
                  key: ValueKey(_branch),
                  initialValue: _branch.isEmpty ? null : _branch,
                  decoration: InputDecoration(labelText: t('Branch', 'الفرع')),
                  items: (_profile!['branches'] as List)
                      .cast<JsonMap>()
                      .map(
                        (branch) => DropdownMenuItem(
                          value: branch['id'] as String,
                          child: Text(branch['name'] as String),
                        ),
                      )
                      .toList(),
                  onChanged: _busy
                      ? null
                      : (value) {
                          if (value != null) {
                            setState(() => _branch = value);
                            if (_staffAccess) _run(_load);
                          }
                        },
                ),
                const SizedBox(height: 16),
                if (!_staffAccess)
                  Text(
                    t(
                      'This account does not have staff workspace access.',
                      'لا يملك هذا الحساب صلاحية مساحة الموظفين.',
                    ),
                  ),
                if (_staffAccess) ...[
                  Wrap(
                    spacing: 12,
                    children: [
                      OutlinedButton.icon(
                        onPressed: _busy ? null : () => _run(_load),
                        icon: const Icon(Icons.refresh),
                        label: Text(t('Refresh', 'تحديث')),
                      ),
                      OutlinedButton.icon(
                        onPressed: _busy ? null : _report,
                        icon: const Icon(Icons.summarize_outlined),
                        label: Text(t('Daily report', 'التقرير اليومي')),
                      ),
                    ],
                  ),
                  if (_employees.isEmpty)
                    Text(t('No assigned employees.', 'لا يوجد موظفون مسندون.')),
                  ..._employees.map((employee) {
                    final present = employee['open_session_id'] != null;
                    final elsewhere =
                        present && employee['open_branch_id'] != _branch;
                    return Card(
                      margin: const EdgeInsets.symmetric(vertical: 8),
                      child: Padding(
                        padding: const EdgeInsets.all(20),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            Text(
                              employee['display_name'] as String,
                              style: Theme.of(context).textTheme.titleLarge,
                            ),
                            Text(
                              present
                                  ? (elsewhere
                                        ? t(
                                            'Present at another branch',
                                            'حاضر بفرع آخر',
                                          )
                                        : t('Present', 'حاضر'))
                                  : t('Not checked in', 'لم يسجل الحضور'),
                            ),
                            const SizedBox(height: 12),
                            Wrap(
                              spacing: 12,
                              children: [
                                FilledButton(
                                  onPressed:
                                      _busy ||
                                          elsewhere ||
                                          employee['active'] != true
                                      ? null
                                      : () => _change(employee),
                                  child: Text(
                                    present
                                        ? t('Check out', 'تسجيل الانصراف')
                                        : t('Check in', 'تسجيل الحضور'),
                                  ),
                                ),
                                OutlinedButton(
                                  onPressed: _busy
                                      ? null
                                      : () => _history(employee),
                                  child: Text(t('History', 'السجل')),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    );
                  }),
                ],
              ],
            ],
          ),
        ),
      ),
    ),
  );
}
