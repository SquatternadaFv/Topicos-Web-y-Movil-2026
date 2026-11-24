import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:optica_app/data/api_client.dart';
import 'package:optica_app/main.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  setUpAll(() async {
    final fonts = FontLoader('LuminaSans');
    for (final weight in ['Regular', 'Medium', 'Bold']) {
      fonts.addFont(
        Future.value(
          ByteData.sublistView(
            File('assets/fonts/Roboto-$weight.ttf').readAsBytesSync(),
          ),
        ),
      );
    }
    await fonts.load();
  });
  for (final width in [320.0, 390.0, 900.0, 1440.0]) {
    testWidgets('Catálogo y navegación a ${width.toInt()} px', (tester) async {
      tester.view.physicalSize = Size(width, 1000);
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      final fixture = jsonDecode(
        File('test/fixtures/recomendacion.json').readAsStringSync(),
      );
      final api = ApiClient(
        client: MockClient(
          (_) async => http.Response.bytes(
            utf8.encode(
              jsonEncode({
                'resultados': [fixture['paquete']],
              }),
            ),
            200,
          ),
        ),
      );
      await tester.pumpWidget(OpticaApp(api: api));
      await tester.pumpAndSettle();
      expect(find.text('ÓPTICA'), findsOneWidget);
      expect(find.textContaining('P1'), findsNothing);
      expect(
        find.byType(NavigationBar),
        width < 1000 ? findsOneWidget : findsNothing,
      );
      expect(
        find.byType(TabBar),
        width >= 1000 ? findsOneWidget : findsNothing,
      );
      await tester.ensureVisible(find.text('Esencial'));
      await tester.pumpAndSettle();
      expect(tester.takeException(), isNull);
      await tester.tap(find.text('Consultar folio'));
      await tester.pumpAndSettle();
      expect(find.text('Consulta tu folio.'), findsOneWidget);
      await tester.tap(find.text('Asistente'));
      await tester.pumpAndSettle();
      expect(find.text('Tu asistente de óptica'), findsOneWidget);
      expect(tester.takeException(), isNull);
    });
  }
}
