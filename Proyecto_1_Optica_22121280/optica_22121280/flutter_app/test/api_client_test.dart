import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:optica_app/data/api_client.dart';

void main() {
  test('Codifica búsqueda y mapea catálogo real a modelos', () async {
    final api = ApiClient(
      client: MockClient((request) async {
        expect(request.url.queryParameters['q'], 'Óptica & lentes');
        return http.Response.bytes(
          utf8.encode(
            jsonEncode({
              'resultados': [
                {
                  'codigo': 'esencial',
                  'nombre': 'Esencial',
                  'descripcion': 'Base',
                  'precio': '650.00',
                  'tratamientos': ['Base'],
                  'disponible': true,
                },
              ],
            }),
          ),
          200,
        );
      }),
    );
    expect((await api.catalogo('Óptica & lentes')).first.precio, '650.00');
    api.dispose();
  });
  test('Confirmación envía entradas y clave; nunca precio calculado', () async {
    final api = ApiClient(
      client: MockClient((request) async {
        expect(request.method, 'POST');
        expect(request.headers['Idempotency-Key'], 'clave-demo');
        expect(jsonDecode(request.body), {'presupuesto': 700});
        return http.Response('{"folio":"folio-demo"}', 201);
      }),
    );
    expect(
      (await api.registrar({'presupuesto': 700}, 'clave-demo')).folio,
      'folio-demo',
    );
    api.dispose();
  });
  test('Error de negocio y error de red son legibles', () async {
    final api = ApiClient(
      client: MockClient(
        (_) async => http.Response('{"error":"Sin opciones","campos":{}}', 422),
      ),
    );
    await expectLater(
      api.recomendar({}),
      throwsA(
        isA<ApiException>().having(
          (e) => e.message,
          'message',
          contains('Sin opciones'),
        ),
      ),
    );
    final offline = ApiClient(
      client: MockClient((_) async => throw http.ClientException('offline')),
    );
    await expectLater(offline.catalogo(''), throwsA(isA<ApiException>()));
    api.dispose();
    offline.dispose();
  });
}
