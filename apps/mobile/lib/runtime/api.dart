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
  int _generation = 0;

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
    if ({
      'auth/mfa/confirm',
      'auth/mfa/verify',
      'auth/oidc/native/finish',
    }.contains(path)) {
      _generation++;
    }
    final generation = _generation;
    final headers = <String, String>{'Content-Type': 'application/json'};
    if (_bearer.isNotEmpty) headers['Authorization'] = 'Bearer $_bearer';
    if (body != null) {
      headers['X-CSRF-Token'] = _csrf;
      headers['Idempotency-Key'] = operationId();
    }
    for (var attempt = 0; attempt < 2; attempt++) {
      if (generation != _generation) {
        throw const ApiException('session_changed', 409);
      }
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
        if (generation != _generation) {
          throw const ApiException('session_changed', 409);
        }
        final data = response.statusCode == 204
            ? <String, dynamic>{}
            : jsonDecode(utf8.decode(response.bodyBytes)) as JsonMap;
        if (response.statusCode < 200 || response.statusCode >= 300) {
          if (response.statusCode == 401) {
            _bearer = '';
            _csrf = '';
            _generation++;
          }
          throw ApiException(
            data['code'] as String? ?? 'service_unavailable',
            response.statusCode,
          );
        }
        if (path.startsWith('auth/')) {
          final value = data['profile'] is JsonMap
              ? data['profile'] as JsonMap
              : data;
          if (value['csrf_token'] is String) {
            final csrf = value['csrf_token'] as String;
            final bearer = value['access_token'] as String? ?? _bearer;
            if (csrf != _csrf || bearer != _bearer) _generation++;
            _csrf = csrf;
            _bearer = bearer;
          }
          if (path == 'auth/logout') {
            _bearer = '';
            _csrf = '';
            _generation++;
          }
        }
        return data;
      } on http.ClientException {
        if (attempt == 1) throw const ApiException('service_unavailable', 503);
      } on TimeoutException {
        if (attempt == 1) throw const ApiException('service_unavailable', 503);
      } on FormatException {
        throw const ApiException('service_unavailable', 503);
      }
      if (path == 'auth/login' || path == 'auth/logout') {
        throw const ApiException('service_unavailable', 503);
      }
      if (attempt == 0 && kIsWeb && body != null) {
        // A rotated HttpOnly cookie can arrive even if its response body was
        // lost. Refresh only the retry header; accept credentials atomically
        // when the original operation's durable response is recovered.
        try {
          final current = await _client
              .get(base.resolve('auth/me'))
              .timeout(const Duration(seconds: 5));
          final value = jsonDecode(utf8.decode(current.bodyBytes));
          if (current.statusCode == 200 &&
              value is JsonMap &&
              value['csrf_token'] is String) {
            headers['X-CSRF-Token'] = value['csrf_token'] as String;
          }
        } on http.ClientException {
          // The original operation can still recover through its old session.
        } on TimeoutException {
          // Keep the bounded original-operation retry.
        } on FormatException {
          // A failed refresh is not an authentication result.
        }
      }
    }
    throw const ApiException('service_unavailable', 503);
  }

  Future<JsonMap> login(String email, String password) {
    _generation++;
    return request(
      'auth/login',
      body: {'email': email, 'password': password, 'native': !kIsWeb},
    );
  }

  Future<JsonMap> restore() => request('auth/me');

  Future<void> logout() async {
    _generation++;
    await request('auth/logout', body: {});
  }

  void close() => _client.close();
}
