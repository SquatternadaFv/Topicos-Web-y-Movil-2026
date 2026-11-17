import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:optica_app/data/api_client.dart';
import 'package:optica_app/screens/chat_screen.dart';

void main() {
  testWidgets(
    'Chat envía mensaje y folio, espera, muestra fuente y abre perfil',
    (tester) async {
      final completer = Completer<http.Response>();
      final requests = <http.Request>[];
      var opened = false;
      final api = ApiClient(
        client: MockClient((request) {
          requests.add(request);
          return completer.future;
        }),
      );
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: ChatScreen(api: api, onRecommend: () => opened = true),
          ),
        ),
      );
      await tester.enterText(
        find.byType(TextField).first,
        '11111111-1111-4111-8111-111111111111',
      );
      await tester.enterText(
        find.byType(TextField).last,
        '  Explica mi orden  ',
      );
      await tester.tap(find.byTooltip('Enviar mensaje'));
      await tester.pump();
      expect(find.byType(LinearProgressIndicator), findsOneWidget);
      expect(
        tester.widget<IconButton>(find.byType(IconButton)).onPressed,
        isNull,
      );
      expect(requests.single.url.path, '/api/asistente/');
      expect(jsonDecode(requests.single.body), {
        'mensaje': 'Explica mi orden',
        'folio': '11111111-1111-4111-8111-111111111111',
      });
      completer.complete(
        http.Response.bytes(
          utf8.encode(
            jsonEncode({
              'intencion': 'recomendar',
              'respuesta': 'Completa las cinco entradas.',
              'accion': 'abrir_recomendador',
              'fuentes': [
                {'titulo': 'Alcance comercial', 'version': '1.0'},
              ],
            }),
          ),
          200,
        ),
      );
      await tester.pumpAndSettle();
      expect(find.text('Completa las cinco entradas.'), findsOneWidget);
      expect(find.text('Fuente: Alcance comercial · v1.0'), findsOneWidget);
      expect(find.byType(LinearProgressIndicator), findsNothing);
      await tester.tap(find.text('Completar mi perfil'));
      expect(opened, isTrue);
      expect(tester.takeException(), isNull);
      api.dispose();
    },
  );

  testWidgets(
    'Error de red conserva mensaje para reintentar sin respuesta ficticia',
    (tester) async {
      final api = ApiClient(
        client: MockClient((_) async => throw http.ClientException('offline')),
      );
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: ChatScreen(api: api, onRecommend: () {}),
          ),
        ),
      );
      await tester.enterText(find.byType(TextField).last, 'hola');
      await tester.tap(find.byTooltip('Enviar mensaje'));
      await tester.pumpAndSettle();
      expect(find.textContaining('No se pudo conectar.'), findsOneWidget);
      expect(
        tester.widget<TextField>(find.byType(TextField).last).controller!.text,
        'hola',
      );
      expect(find.text('Asistente Lúmina'), findsNothing);
      expect(tester.takeException(), isNull);
      api.dispose();
    },
  );
}
