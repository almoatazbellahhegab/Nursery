/// Connected branch administration. All authorization/version checks are server-owned.
library;

import 'package:flutter/material.dart';
import 'api.dart';

class BranchManagement extends StatefulWidget {
  final NurseryApi api;
  final bool ar;
  const BranchManagement({super.key, required this.api, required this.ar});
  @override
  State<BranchManagement> createState() => _BranchManagementState();
}

class _BranchManagementState extends State<BranchManagement> {
  List<JsonMap> _branches = [];
  List<JsonMap> _members = [];
  String? _cursor;
  String? _memberCursor;
  bool _busy = true;
  String _message = '';
  String t(String en, String ar) => widget.ar ? ar : en;
  @override
  void initState() {
    super.initState();
    _run(() async {
      await _load();
      await _loadMembers();
    });
  }

  Future<void> _run(Future<void> Function() action) async {
    setState(() {
      _busy = true;
      _message = '';
    });
    try {
      await action();
    } on ApiException catch (error) {
      if (mounted) {
        setState(
          () => _message = error.code == 'branch_version_conflict'
              ? t(
                  'Branch changed. Close and reopen it before saving.',
                  'تغير الفرع. أغلقه وأعد فتحه قبل الحفظ.',
                )
              : t(
                  'Unable to save. Check fields and refresh before retrying.',
                  'تعذر الحفظ. تحقق من الحقول وحدّث البيانات قبل المحاولة.',
                ),
        );
      }
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _load({String? cursor}) async {
    final data = await widget.api.request(
      'branches${cursor == null ? '' : '?cursor=$cursor'}',
    );
    if (mounted) {
      setState(() {
        final rows = (data['items'] as List).cast<JsonMap>();
        _branches = cursor == null ? rows : [..._branches, ...rows];
        _cursor = data['next_cursor'] as String?;
      });
    }
  }

  Future<void> _loadMembers({String? cursor}) async {
    final data = await widget.api.request(
      'branches/members${cursor == null ? '' : '?cursor=$cursor'}',
    );
    if (mounted) {
      setState(() {
        final rows = (data['items'] as List).cast<JsonMap>();
        _members = cursor == null ? rows : [..._members, ...rows];
        _memberCursor = data['next_cursor'] as String?;
      });
    }
  }

  Future<void> _edit(JsonMap? item) async {
    final name = TextEditingController(text: item?['name'] as String? ?? '');
    final timezone = TextEditingController(
      text: item?['timezone'] as String? ?? 'Africa/Cairo',
    );
    final email = TextEditingController(
      text: item?['contact_email'] as String? ?? '',
    );
    final phone = TextEditingController(
      text: item?['contact_phone'] as String? ?? '',
    );
    final address = TextEditingController(
      text: item?['address'] as String? ?? '',
    );
    final capacity = TextEditingController(
      text: item?['capacity']?.toString() ?? '',
    );
    var active = item?['active'] as bool? ?? true;
    var status = item?['operating_status'] as String? ?? 'open';
    var saving = false;
    var message = '';
    final formKey = GlobalKey<FormState>();
    if (!mounted) return;
    await showDialog<void>(
      context: context,
      builder: (dialogContext) => StatefulBuilder(
        builder: (context, update) => AlertDialog(
          title: Text(
            item == null
                ? t('Create branch', 'إنشاء فرع')
                : t('Edit branch', 'تعديل الفرع'),
          ),
          content: SizedBox(
            width: 480,
            child: SingleChildScrollView(
              child: Form(
                key: formKey,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    if (message.isNotEmpty) Text(message),
                    TextFormField(
                      controller: name,
                      maxLength: 160,
                      decoration: InputDecoration(
                        labelText: t('Branch name', 'اسم الفرع'),
                      ),
                      validator: (value) =>
                          value == null || value.trim().isEmpty
                          ? t('Name required', 'الاسم مطلوب')
                          : null,
                    ),
                    TextFormField(
                      controller: timezone,
                      decoration: InputDecoration(
                        labelText: t('Timezone', 'المنطقة الزمنية'),
                      ),
                    ),
                    TextFormField(
                      controller: email,
                      maxLength: 254,
                      keyboardType: TextInputType.emailAddress,
                      decoration: InputDecoration(
                        labelText: t('Branch email', 'بريد الفرع'),
                      ),
                    ),
                    TextFormField(
                      controller: phone,
                      maxLength: 40,
                      keyboardType: TextInputType.phone,
                      decoration: InputDecoration(
                        labelText: t('Branch phone', 'هاتف الفرع'),
                      ),
                    ),
                    TextFormField(
                      controller: address,
                      maxLength: 500,
                      decoration: InputDecoration(
                        labelText: t('Address', 'العنوان'),
                      ),
                    ),
                    TextFormField(
                      controller: capacity,
                      keyboardType: TextInputType.number,
                      decoration: InputDecoration(
                        labelText: t('Capacity context', 'السعة الاسترشادية'),
                      ),
                      validator: (value) =>
                          value != null &&
                              value.isNotEmpty &&
                              (int.tryParse(value) == null ||
                                  int.parse(value) < 1 ||
                                  int.parse(value) > 10000)
                          ? t('Enter 1–10000', 'أدخل رقماً من ١ إلى ١٠٠٠٠')
                          : null,
                    ),
                    Padding(
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      child: Text(
                        t(
                          'Branch capacity is planning context. Classroom capacity is enforced during enrollment.',
                          'سعة الفرع استرشادية للتخطيط. يتم التحقق من سعة الفصل عند التسجيل.',
                        ),
                      ),
                    ),
                    DropdownButtonFormField<String>(
                      initialValue: status,
                      decoration: InputDecoration(
                        labelText: t('Operating status', 'حالة التشغيل'),
                      ),
                      items: [
                        DropdownMenuItem(
                          value: 'open',
                          child: Text(t('Open', 'مفتوح')),
                        ),
                        DropdownMenuItem(
                          value: 'planned',
                          child: Text(t('Planned', 'مخطط')),
                        ),
                        DropdownMenuItem(
                          value: 'temporarily_closed',
                          child: Text(t('Temporarily closed', 'مغلق مؤقتاً')),
                        ),
                      ],
                      onChanged: saving
                          ? null
                          : (value) => update(() => status = value!),
                    ),
                    SwitchListTile(
                      contentPadding: EdgeInsets.zero,
                      title: Text(
                        t('Active for new records', 'نشط للسجلات الجديدة'),
                      ),
                      value: active,
                      onChanged: saving
                          ? null
                          : (value) => update(() => active = value),
                    ),
                  ],
                ),
              ),
            ),
          ),
          actions: [
            TextButton(
              onPressed: saving ? null : () => Navigator.pop(dialogContext),
              child: Text(t('Cancel', 'إلغاء')),
            ),
            FilledButton(
              onPressed: saving
                  ? null
                  : () async {
                      if (!formKey.currentState!.validate()) return;
                      update(() => saving = true);
                      try {
                        await widget.api.request(
                          item == null ? 'branches' : 'branches/${item['id']}',
                          body: {
                            'name': name.text.trim(),
                            'timezone': timezone.text.trim(),
                            'contact_email': email.text.trim(),
                            'contact_phone': phone.text.trim(),
                            'address': address.text.trim(),
                            'capacity': capacity.text.isEmpty
                                ? null
                                : int.parse(capacity.text),
                            'operating_status': status,
                            'active': active,
                            if (item != null)
                              'expected_version': item['version'],
                          },
                        );
                        if (dialogContext.mounted) Navigator.pop(dialogContext);
                        await _run(_load);
                      } on ApiException catch (error) {
                        if (context.mounted) {
                          update(() {
                            saving = false;
                            message = error.code == 'branch_version_conflict'
                                ? t(
                                    'Branch changed. Close and reopen it.',
                                    'تغير الفرع. أغلقه وأعد فتحه.',
                                  )
                                : t(
                                    'Unable to save. Check the fields.',
                                    'تعذر الحفظ. تحقق من الحقول.',
                                  );
                          });
                        }
                      }
                    },
              child: Text(t('Save branch', 'حفظ الفرع')),
            ),
          ],
        ),
      ),
    );
    // Controllers are disposed after the closing route animation finishes.
    await Future<void>.delayed(const Duration(milliseconds: 300));
    for (final controller in [
      name,
      timezone,
      email,
      phone,
      address,
      capacity,
    ]) {
      controller.dispose();
    }
  }

  Future<void> _assign(JsonMap branch) => _run(() async {
    final data = await widget.api.request('branches/${branch['id']}/members');
    var assigned = (data['items'] as List).cast<JsonMap>();
    String? cursor = data['next_cursor'] as String?;
    String? selected;
    var version = branch['version'] as int;
    var saving = false;
    var message = '';
    if (!mounted) return;
    await showDialog<void>(
      context: context,
      builder: (dialogContext) => StatefulBuilder(
        builder: (context, update) => AlertDialog(
          title: Text(t('Branch access', 'صلاحيات الفرع')),
          content: SizedBox(
            width: 480,
            child: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    t(
                      'Branch access does not replace classroom, child or employee assignments.',
                      'صلاحية الفرع لا تستبدل تكليفات الفصل أو الطفل أو الموظف.',
                    ),
                  ),
                  if (message.isNotEmpty) Text(message),
                  ...assigned.map(
                    (row) => ListTile(
                      title: Text(
                        _members
                                    .where(
                                      (m) => m['user_id'] == row['user_id'],
                                    )
                                    .firstOrNull?['email']
                                as String? ??
                            row['user_id'] as String,
                      ),
                    ),
                  ),
                  if (cursor != null)
                    TextButton(
                      onPressed: saving
                          ? null
                          : () async {
                              final next = await widget.api.request(
                                'branches/${branch['id']}/members?cursor=$cursor',
                              );
                              if (context.mounted) {
                                update(() {
                                  assigned = [
                                    ...assigned,
                                    ...(next['items'] as List).cast<JsonMap>(),
                                  ];
                                  cursor = next['next_cursor'] as String?;
                                });
                              }
                            },
                      child: Text(t('More assignments', 'المزيد من التكليفات')),
                    ),
                  DropdownButtonFormField<String>(
                    initialValue: selected,
                    isExpanded: true,
                    decoration: InputDecoration(
                      labelText: t('Organization member', 'عضو المؤسسة'),
                    ),
                    items: _members
                        .map(
                          (m) => DropdownMenuItem(
                            value: m['user_id'] as String,
                            child: Text(
                              m['email'] as String,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        )
                        .toList(),
                    onChanged: saving
                        ? null
                        : (value) => update(() => selected = value),
                  ),
                  if (_memberCursor != null)
                    TextButton(
                      onPressed: saving
                          ? null
                          : () async {
                              await _loadMembers(cursor: _memberCursor);
                              if (context.mounted) update(() {});
                            },
                      child: Text(t('More members', 'المزيد من الأعضاء')),
                    ),
                  for (final value in [true, false])
                    Padding(
                      padding: const EdgeInsets.only(top: 12),
                      child: OutlinedButton(
                        onPressed:
                            saving ||
                                selected == null ||
                                (value && branch['active'] != true)
                            ? null
                            : () async {
                                update(() => saving = true);
                                try {
                                  final result = await widget.api.request(
                                    'branches/${branch['id']}/members',
                                    body: {
                                      'user_id': selected,
                                      'assigned': value,
                                      'expected_version': version,
                                    },
                                  );
                                  final current = await widget.api.request(
                                    'branches/${branch['id']}/members',
                                  );
                                  if (context.mounted) {
                                    update(() {
                                      version = result['version'] as int;
                                      assigned = (current['items'] as List)
                                          .cast<JsonMap>();
                                      cursor =
                                          current['next_cursor'] as String?;
                                      message = t(
                                        'Assignment saved.',
                                        'تم حفظ التكليف.',
                                      );
                                      saving = false;
                                    });
                                  }
                                } on ApiException catch (_) {
                                  if (context.mounted) {
                                    update(() {
                                      saving = false;
                                      message = t(
                                        'Unable to save. Close and refresh.',
                                        'تعذر الحفظ. أغلق وحدّث البيانات.',
                                      );
                                    });
                                  }
                                }
                              },
                        child: Text(
                          value
                              ? t('Assign branch', 'إضافة للفرع')
                              : t('Remove branch access', 'إزالة صلاحية الفرع'),
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ),
          actions: [
            TextButton(
              onPressed: saving ? null : () => Navigator.pop(dialogContext),
              child: Text(t('Close', 'إغلاق')),
            ),
          ],
        ),
      ),
    );
    await _load();
  });

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: Text(t('Branches', 'الفروع'))),
    body: SafeArea(
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 900),
          child: ListView(
            padding: const EdgeInsets.all(24),
            children: [
              if (_busy) const LinearProgressIndicator(),
              if (_message.isNotEmpty)
                Semantics(liveRegion: true, child: Text(_message)),
              Wrap(
                spacing: 12,
                children: [
                  FilledButton.icon(
                    onPressed: _busy ? null : () => _edit(null),
                    icon: const Icon(Icons.add),
                    label: Text(t('New branch', 'فرع جديد')),
                  ),
                  OutlinedButton(
                    onPressed: _busy ? null : () => _run(_load),
                    child: Text(t('Refresh', 'تحديث')),
                  ),
                ],
              ),
              ..._branches.map(
                (branch) => Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          branch['name'] as String,
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                        Text(
                          '${branch['timezone']} · ${branch['active'] == true ? t('Active', 'نشط') : t('Inactive', 'غير نشط')}',
                        ),
                        Wrap(
                          spacing: 12,
                          children: [
                            TextButton(
                              onPressed: _busy ? null : () => _edit(branch),
                              child: Text(t('Edit branch', 'تعديل الفرع')),
                            ),
                            TextButton(
                              onPressed: _busy ? null : () => _assign(branch),
                              child: Text(t('Branch access', 'صلاحيات الفرع')),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              ),
              if (_cursor != null)
                TextButton(
                  onPressed: _busy
                      ? null
                      : () => _run(() => _load(cursor: _cursor)),
                  child: Text(t('More branches', 'المزيد من الفروع')),
                ),
            ],
          ),
        ),
      ),
    ),
  );
}
