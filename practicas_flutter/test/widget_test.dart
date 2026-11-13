import 'package:flutter_test/flutter_test.dart';
import 'package:practicas_flutter/main.dart';

void main() {
  testWidgets('Conserva el contador al cambiar de pantalla', (tester) async {
    await tester.pumpWidget(const LaboratorioApp());
    await tester.tap(find.text('Sumar'));
    await tester.pump();
    expect(find.text('Contador con estado: 1'), findsOneWidget);
    await tester.tap(find.text('API y chat'));
    await tester.pumpAndSettle();
    expect(find.text('Consumo real de JSON'), findsOneWidget);
    await tester.tap(find.text('Widgets'));
    await tester.pumpAndSettle();
    expect(find.text('Contador con estado: 1'), findsOneWidget);
  });
}
