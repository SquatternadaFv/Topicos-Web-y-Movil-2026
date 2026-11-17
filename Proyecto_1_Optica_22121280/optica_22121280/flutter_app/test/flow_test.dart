import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:optica_app/data/api_client.dart';
import 'package:optica_app/screens/profile_screen.dart';

void main() {
  testWidgets('Perfil -> modelo corregido -> confirmación -> folio', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(900, 1500);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    final recommendation = jsonDecode(
      File('test/fixtures/recomendacion.json').readAsStringSync(),
    );
    final calls = <String>[];
    final api = ApiClient(
      client: MockClient((request) async {
        calls.add(request.url.path);
        final body = jsonDecode(request.body);
        expect(body['presupuesto'], 700);
        if (request.url.path.endsWith('/recomendaciones/')) {
          return http.Response.bytes(
            utf8.encode(jsonEncode(recommendation)),
            200,
          );
        }
        expect(request.headers['Idempotency-Key'], isNotEmpty);
        return http.Response.bytes(
          utf8.encode(
            jsonEncode({
              'folio': '11111111-1111-4111-8111-111111111111',
              'estado': 'registrada',
              'creada': '2026-11-10T16:30:00Z',
              'precio_confirmado': '650.00',
              'entradas': recommendation['entradas'],
              'recomendacion': recommendation,
            }),
          ),
          201,
        );
      }),
    );
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(body: ProfileScreen(api: api)),
      ),
    );
    await tester.tap(find.byKey(const Key('recommend')));
    await tester.pumpAndSettle();
    expect(find.text('Ajustado por reglas comerciales'), findsOneWidget);
    expect(
      find.text('Confianza del modelo para la opción final: 0.0%'),
      findsOneWidget,
    );
    final confirm = find.text('Registrar solicitud y obtener folio');
    await tester.ensureVisible(confirm);
    await tester.tap(confirm);
    await tester.pumpAndSettle();
    await tester.tap(find.text('Confirmar registro'));
    await tester.pumpAndSettle();
    expect(find.text('Solicitud registrada'), findsOneWidget);
    expect(find.text('11111111-1111-4111-8111-111111111111'), findsOneWidget);
    expect(calls, ['/api/recomendaciones/', '/api/ordenes/']);
    expect(tester.takeException(), isNull);
    api.dispose();
  });

  testWidgets('Formulario móvil rechaza presupuesto inválido antes de HTTP', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(390, 844);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    var calls = 0;
    final api = ApiClient(
      client: MockClient((_) async {
        calls++;
        return http.Response('{}', 500);
      }),
    );
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(body: ProfileScreen(api: api)),
      ),
    );
    await tester.enterText(find.byKey(const Key('presupuesto')), '-1');
    final button = find.byKey(const Key('recommend'));
    await tester.ensureVisible(button);
    await tester.tap(button);
    await tester.pumpAndSettle();
    expect(
      find.text('Ingresa un valor entre 300.0 y 10000.0.'),
      findsOneWidget,
    );
    expect(calls, 0);
    expect(tester.takeException(), isNull);
    api.dispose();
  });
}
