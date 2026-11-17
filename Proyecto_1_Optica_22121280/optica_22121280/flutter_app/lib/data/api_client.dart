import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/models.dart';

class ApiException implements Exception {
  final String message;
  ApiException(this.message);
  @override
  String toString() => message;
}

class ApiClient {
  static const defaultUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://127.0.0.1:8000/api',
  );
  final String baseUrl;
  final http.Client _client;
  ApiClient({String? baseUrl, http.Client? client})
    : baseUrl = (baseUrl ?? defaultUrl).replaceFirst(RegExp(r'/+$'), ''),
      _client = client ?? http.Client();

  Future<Json> _request(String path, {Json? body, String? key}) async {
    try {
      final uri = Uri.parse('$baseUrl/$path');
      final response =
          await (body == null
                  ? _client.get(uri)
                  : _client.post(
                      uri,
                      headers: {
                        'Content-Type': 'application/json',
                        'Idempotency-Key': ?key,
                      },
                      body: jsonEncode(body),
                    ))
              .timeout(const Duration(seconds: 15));
      Json j;
      try {
        j = jsonDecode(utf8.decode(response.bodyBytes)) as Json;
      } catch (_) {
        throw ApiException(
          'El servidor respondió en un formato inesperado (${response.statusCode}).',
        );
      }
      if (response.statusCode < 200 || response.statusCode >= 300) {
        final fields = j['campos'] as Json?;
        final details =
            fields?.entries
                .where((e) => e.value is String)
                .map((e) => '${e.key}: ${e.value}')
                .join('\n') ??
            '';
        throw ApiException(
          '${j['error'] ?? 'Error del servidor.'}${details.isEmpty ? '' : '\n$details'}',
        );
      }
      return j;
    } on TimeoutException {
      throw ApiException(
        'La conexión tardó demasiado. Reintenta; la confirmación conserva su clave para evitar duplicados.',
      );
    } on http.ClientException {
      throw ApiException(
        'No se pudo conectar. Revisa que Django esté activo y la URL base sea correcta.',
      );
    }
  }

  Future<List<Paquete>> catalogo(String q) async {
    final j = await _request('catalogo/?q=${Uri.encodeQueryComponent(q)}');
    return (j['resultados'] as List)
        .map((e) => Paquete.fromJson(e as Json))
        .toList();
  }

  Future<Paquete> detalle(String codigo) async =>
      Paquete.fromJson(await _request('catalogo/$codigo/'));
  Future<Recomendacion> recomendar(Json body) async =>
      Recomendacion(await _request('recomendaciones/', body: body));
  Future<Orden> registrar(Json body, String key) async =>
      Orden(await _request('ordenes/', body: body, key: key));
  Future<Orden> consultar(String folio) async =>
      Orden(await _request('ordenes/${Uri.encodeComponent(folio.trim())}/'));
  Future<Json> conversar(String mensaje, {String? folio}) => _request(
    'asistente/',
    body: {
      'mensaje': mensaje.trim(),
      if (folio != null && folio.trim().isNotEmpty) 'folio': folio.trim(),
    },
  );
  void dispose() => _client.close();
}
