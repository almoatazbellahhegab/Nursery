/// MFA secrets and recovery codes stay in this form's memory until the user continues.
library;

import 'package:flutter/material.dart';
import 'api.dart';

class MfaForm extends StatefulWidget {
  final NurseryApi api;
  final bool ar;
  final JsonMap profile;
  final Future<void> Function(JsonMap) onReady;
  const MfaForm({
    super.key,
    required this.api,
    required this.ar,
    required this.profile,
    required this.onReady,
  });
  @override
  State<MfaForm> createState() => _MfaFormState();
}

class _MfaFormState extends State<MfaForm> {
  final _code = TextEditingController();
  String _secret = '';
  String _kind = 'totp';
  String _message = '';
  bool _busy = false;
  bool _saved = false;
  JsonMap? _completed;
  String t(String en, String ar) => widget.ar ? ar : en;
  @override
  void dispose() {
    _code.dispose();
    super.dispose();
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
        setState(
          () => _message = error.code == 'verification_rate_limited'
              ? t(
                  'Too many attempts. Wait five minutes before retrying.',
                  'محاولات كثيرة. انتظر خمس دقائق قبل المحاولة مجدداً.',
                )
              : error.code == 'invalid_mfa_verification'
              ? t(
                  'Check the code. Each authenticator code works once; wait for the next code if needed.',
                  'تحقق من الرمز. يُستخدم كل رمز مرة واحدة؛ انتظر الرمز التالي عند الحاجة.',
                )
              : error.code == 'reauthentication_required'
              ? t(
                  'Verify a fresh authenticator or recovery code before changing your setup.',
                  'تحقق برمز حديث من التطبيق أو رمز استرداد قبل تغيير الإعداد.',
                )
              : t(
                  'Unable to verify. Sign in again if the session expired.',
                  'تعذر التحقق. سجّل الدخول مجدداً إذا انتهت الجلسة.',
                ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _busy = false);
      }
    }
  }

  Future<void> _begin() => _run(() async {
    final data = await widget.api.request('auth/mfa/begin', body: {});
    if (mounted) {
      setState(() {
        _secret = data['secret'] as String;
        _kind = 'totp';
        _code.clear();
      });
    }
  });

  Future<void> _verify() => _run(() async {
    final result = await widget.api.request(
      _secret.isEmpty ? 'auth/mfa/verify' : 'auth/mfa/confirm',
      body: {
        'code': _code.text.trim(),
        'kind': _secret.isEmpty ? _kind : 'totp',
      },
    );
    _code.clear();
    if (!mounted) return;
    setState(() => _secret = '');
    if (result['recovery_codes'] != null) {
      setState(() => _completed = result);
    } else {
      await widget.onReady(result['profile'] as JsonMap);
    }
  });

  @override
  Widget build(BuildContext context) => Card(
    child: Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            t('Protect your account', 'حماية حسابك'),
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 12),
          Text(
            t(
              'Privileged access requires a second factor. Keep recovery codes somewhere only you can access.',
              'تتطلب الصلاحيات الحساسة عاملاً ثانياً. احتفظ برموز الاسترداد في مكان آمن خاص بك.',
            ),
          ),
          if (_busy) const LinearProgressIndicator(),
          if (_message.isNotEmpty)
            Semantics(liveRegion: true, child: Text(_message)),
          if (_completed != null) ...[
            const SizedBox(height: 20),
            Text(
              t('Save your recovery codes', 'احفظ رموز الاسترداد'),
              style: Theme.of(context).textTheme.titleLarge,
            ),
            Text(
              t(
                'Each code works once. Codes stay here until you continue.',
                'يعمل كل رمز مرة واحدة. تبقى الرموز هنا حتى تختار المتابعة.',
              ),
            ),
            ...(_completed!['recovery_codes'] as List).cast<String>().map(
              (value) => Padding(
                padding: const EdgeInsets.symmetric(vertical: 5),
                child: SelectableText(value, textDirection: TextDirection.ltr),
              ),
            ),
            CheckboxListTile(
              contentPadding: EdgeInsets.zero,
              title: Text(
                t('I saved these codes securely', 'حفظت هذه الرموز بأمان'),
              ),
              value: _saved,
              onChanged: (value) => setState(() => _saved = value ?? false),
            ),
            FilledButton(
              onPressed: !_saved || _busy
                  ? null
                  : () => _run(
                      () => widget.onReady(_completed!['profile'] as JsonMap),
                    ),
              child: Text(t('Continue to workspace', 'متابعة إلى مساحة العمل')),
            ),
          ] else ...[
            if (_secret.isNotEmpty) ...[
              const SizedBox(height: 20),
              Text(
                t(
                  'Add Nursery to your authenticator',
                  'أضف الحضانة إلى تطبيق المصادقة',
                ),
                style: Theme.of(context).textTheme.titleMedium,
              ),
              Text(
                t(
                  'Choose a time-based account and enter this setup key. Then enter its six-digit code.',
                  'اختر حساباً يعتمد على الوقت وأدخل مفتاح الإعداد هذا، ثم أدخل الرمز المكون من ستة أرقام.',
                ),
              ),
              const SizedBox(height: 12),
              Semantics(
                label: t('Setup key', 'مفتاح الإعداد'),
                child: SelectableText(
                  _secret,
                  textDirection: TextDirection.ltr,
                ),
              ),
            ],
            if (widget.profile['mfa_enrolled'] == true ||
                _secret.isNotEmpty) ...[
              if (_secret.isEmpty)
                DropdownButtonFormField<String>(
                  initialValue: _kind,
                  decoration: InputDecoration(
                    labelText: t('Verification method', 'طريقة التحقق'),
                  ),
                  items: [
                    DropdownMenuItem(
                      value: 'totp',
                      child: Text(
                        t('Authenticator code', 'رمز تطبيق المصادقة'),
                      ),
                    ),
                    DropdownMenuItem(
                      value: 'recovery',
                      child: Text(t('Recovery code', 'رمز استرداد')),
                    ),
                  ],
                  onChanged: _busy
                      ? null
                      : (value) => setState(() => _kind = value!),
                ),
              TextField(
                controller: _code,
                decoration: InputDecoration(
                  labelText: t('Verification code', 'رمز التحقق'),
                ),
                autofillHints: const [AutofillHints.oneTimeCode],
                keyboardType: _kind == 'totp'
                    ? TextInputType.number
                    : TextInputType.text,
                maxLength: 80,
                textDirection: TextDirection.ltr,
              ),
              const SizedBox(height: 12),
              FilledButton(
                onPressed: _busy ? null : _verify,
                child: Text(t('Verify code', 'تحقق من الرمز')),
              ),
            ],
            if (_secret.isEmpty &&
                (widget.profile['mfa_enrolled'] != true ||
                    widget.profile['mfa_required'] != true))
              OutlinedButton(
                onPressed: _busy ? null : _begin,
                child: Text(
                  widget.profile['mfa_enrolled'] == true
                      ? t('Replace authenticator', 'استبدال تطبيق المصادقة')
                      : t('Set up authenticator', 'إعداد تطبيق المصادقة'),
                ),
              ),
          ],
        ],
      ),
    ),
  );
}
