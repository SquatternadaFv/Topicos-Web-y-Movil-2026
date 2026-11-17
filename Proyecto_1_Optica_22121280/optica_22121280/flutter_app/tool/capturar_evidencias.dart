// Capturas de widgets Flutter reales, renderizados por flutter_tester.
// Requiere Django activo en 127.0.0.1:8000. No usa MockClient.
// flutter test tool/capturar_evidencias.dart --update-goldens
import 'dart:io';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:optica_app/main.dart';
import 'package:optica_app/data/api_client.dart';
import 'package:http/io_client.dart';

void main() {
  LiveTestWidgetsFlutterBinding.ensureInitialized();
  HttpOverrides.global = null;
  final liveApi = ApiClient(client: IOClient(HttpClient()));
  testWidgets('Evidencias visuales con Django y SQLite reales', (tester) async {
    HttpOverrides.global = null;
    tester.view.physicalSize = const Size(1100, 1050);
    tester.view.devicePixelRatio = 1;
    await tester.binding.setSurfaceSize(const Size(1100, 1050));
    final sdk = Platform.environment['FLUTTER_ROOT']!;
    final fonts = FontLoader('Roboto');
    fonts.addFont(
      Future.value(
        ByteData.sublistView(
          File(
            '$sdk/bin/cache/artifacts/material_fonts/Roboto-Regular.ttf',
          ).readAsBytesSync(),
        ),
      ),
    );
    fonts.addFont(
      Future.value(
        ByteData.sublistView(
          File(
            '$sdk/bin/cache/artifacts/material_fonts/Roboto-Bold.ttf',
          ).readAsBytesSync(),
        ),
      ),
    );
    await fonts.load();
    final icons = FontLoader('MaterialIcons')
      ..addFont(
        Future.value(
          ByteData.sublistView(
            File(
              '$sdk/bin/cache/artifacts/material_fonts/MaterialIcons-Regular.otf',
            ).readAsBytesSync(),
          ),
        ),
      );
    await icons.load();
    const root = Key('capture');
    Future<void> settleNetwork() async {
      await tester.runAsync(
        () => Future<void>.delayed(const Duration(milliseconds: 1000)),
      );
      await tester.pumpAndSettle();
    }

    Future<void> snap(String name) async {
      await tester.pumpAndSettle();
      await expectLater(
        find.byKey(root),
        matchesGoldenFile('../../evidencias/$name.png'),
      );
    }

    await tester.pumpWidget(
      RepaintBoundary(
        key: root,
        child: OpticaApp(api: liveApi),
      ),
    );
    await settleNetwork();
    expect(find.text('Colección de paquetes'), findsOneWidget);
    expect(find.text('Claridad'), findsOneWidget);
    await snap('00_inicio');
    await tester.ensureVisible(find.text('Claridad'));
    await tester.tap(find.text('Claridad'));
    await settleNetwork();
    expect(find.text('Detalle del paquete'), findsOneWidget);
    await snap('01_detalle');
    await tester.pageBack();
    await tester.pumpAndSettle();
    await tester.tap(find.text('Mi recomendación'));
    await tester.pumpAndSettle();
    await snap('02_formulario');
    await tester.tap(find.byKey(const Key('recommend')));
    await settleNetwork();
    expect(find.text('Ajustado por reglas comerciales'), findsOneWidget);
    await snap('03_recomendacion');
    await tester.ensureVisible(
      find.text('Registrar solicitud y obtener folio'),
    );
    await tester.pumpAndSettle();
    await snap('04_reglas');
    await tester.tap(find.text('Registrar solicitud y obtener folio'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Confirmar registro'));
    await settleNetwork();
    expect(find.text('Solicitud registrada'), findsOneWidget);
    final folio = tester
        .widgetList<SelectableText>(find.byType(SelectableText))
        .first
        .data!;
    expect(folio, matches(RegExp(r'^[0-9a-f-]{36}$')));
    await snap('05_folio');
    await tester.runAsync(() async {
      File('../evidencias/folio_capturas.json').writeAsStringSync(
        jsonEncode({
          'folio': folio,
          'origen': 'flutter_tester con HTTP real; no navegador ni emulador',
        }),
      );
    });
    await tester.pageBack();
    await tester.pumpAndSettle();
    await tester.tap(find.text('Consultar folio'));
    await tester.pumpAndSettle();
    await tester.enterText(find.byType(TextFormField).last, folio);
    await tester.tap(find.text('Consultar solicitud'));
    await settleNetwork();
    expect(find.text('Detalle de la solicitud'), findsOneWidget);
    expect(find.text(folio), findsOneWidget);
    await snap('06_consulta');
    await tester.pageBack();
    await tester.pumpAndSettle();
    await tester.tap(find.text('Catálogo'));
    await tester.pumpAndSettle();
    await tester.enterText(find.byType(TextField).first, 'Claridad');
    await tester.testTextInput.receiveAction(TextInputAction.done);
    await settleNetwork();
    await snap('07_busqueda');
    await tester.tap(find.text('Mi recomendación'));
    await tester.pumpAndSettle();
    await tester.enterText(find.byKey(const Key('presupuesto')), '500');
    await tester.tap(find.byKey(const Key('recommend')));
    await settleNetwork();
    expect(find.textContaining('No hay un paquete disponible'), findsOneWidget);
    await snap('09_sin_opciones');
    await tester.enterText(find.byKey(const Key('presupuesto')), '700');
    await tester.tap(find.byKey(const Key('recommend')));
    await settleNetwork();
    await tester.pageBack();
    await tester.pumpAndSettle();
    tester.view.physicalSize = const Size(390, 844);
    await tester.binding.setSurfaceSize(const Size(390, 844));
    await tester.pumpAndSettle();
    await snap('08_formulario_movil');
    expect(tester.takeException(), isNull);
    await tester.binding.setSurfaceSize(null);
    tester.view.resetPhysicalSize();
    tester.view.resetDevicePixelRatio();
  });
}
