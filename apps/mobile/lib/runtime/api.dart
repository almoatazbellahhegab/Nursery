/// Connected session client. Browser cookies stay HttpOnly; native tokens stay in memory.
library;

import 'dart:async';
import 'dart:convert';
import 'dart:math';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'client_native.dart'
    if (dart.library.js_interop) 'client_browser.dart'
    as platform;

typedef JsonMap = Map<String, dynamic>;

class ApiException implements Exception {
  final String code;
  final int status;
  const ApiException(this.code, this.status);
  @override
  String toString() => code;
}

class NurseryApi {
  final http.Client _client;
  final Uri base;
  String _csrf = '';
  String _bearer = '';

  NurseryApi({http.Client? client, Uri? base})
    : _client = client ?? platform.createClient(),
      base =
          base ??
          Uri.parse(
            const String.fromEnvironment('NURSERY_API_URL').isNotEmpty
                ? const String.fromEnvironment('NURSERY_API_URL')
                : kIsWeb
                ? '${Uri.base.scheme}://${Uri.base.host}:8000/api/v1/'
                : 'http://127.0.0.1:8000/api/v1/',
          );

  String operationId() {
    final random = Random.secure();
    final bytes = List.generate(16, (_) => random.nextInt(256));
    bytes[6] = (bytes[6] & 15) | 64;
    bytes[8] = (bytes[8] & 63) | 128;
    final text = bytes.map((b) => b.toRadixString(16).padLeft(2, '0')).join();
    return '${text.substring(0, 8)}-${text.substring(8, 12)}-${text.substring(12, 16)}-${text.substring(16, 20)}-${text.substring(20)}';
  }

  Future<JsonMap> request(String path, {JsonMap? body}) async {
    final headers = <String, String>{'Content-Type': 'application/json'};
    if (_bearer.isNotEmpty) headers['Authorization'] = 'Bearer $_bearer';
    if (body != null) {
      headers['X-CSRF-Token'] = _csrf;
      headers['Idempotency-Key'] = operationId();
    }
    for (var attempt = 0; attempt < 2; attempt++) {
      try {
        final message = http.Request(
          body == null ? 'GET' : 'POST',
          base.resolve(path),
        );
        message.headers.addAll(headers);
        if (body != null) message.body = jsonEncode(body);
        final response = await http.Response.fromStream(
          await _client.send(message),
        ).timeout(const Duration(seconds: 15));
        final data = response.statusCode == 204
            ? <String, dynamic>{}
            : jsonDecode(utf8.decode(response.bodyBytes)) as JsonMap;
        if (response.statusCode < 200 || response.statusCode >= 300) {
          if (response.statusCode == 401) {
            _bearer = '';
            _csrf = '';
          }
          throw ApiException(
            data['code'] as String? ?? 'service_unavailable',
            response.statusCode,
          );
        }
        return data;
      } on http.ClientException {
        if (attempt == 1) throw const ApiException('service_unavailable', 503);
      } on TimeoutException {
        if (attempt == 1) throw const ApiException('service_unavailable', 503);
      } on FormatException {
        throw const ApiException('service_unavailable', 503);
      }
    }
    throw const ApiException('service_unavailable', 503);
  }

  Future<JsonMap> login(String email, String password) async {
    final profile = await request(
      'auth/login',
      body: {'email': email, 'password': password, 'native': !kIsWeb},
    );
    _csrf = profile['csrf_token'] as String;
    _bearer = profile['access_token'] as String? ?? '';
    return profile;
  }

  Future<JsonMap> restore() async {
    final profile = await request('auth/me');
    _csrf = profile['csrf_token'] as String;
    return profile;
  }

  Future<void> logout() async {
    await request('auth/logout', body: {});
    _bearer = '';
    _csrf = '';
  }

  void close() => _client.close();
}
