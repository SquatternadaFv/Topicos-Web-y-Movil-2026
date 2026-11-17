# Validación del proyecto

Fecha: 10 de noviembre de 2026. Entorno de construcción Linux, Python 3.12, Django 5.2.19, scikit-learn 1.8.0, Flutter 3.47.9, Dart 3.13.7. Las versiones Python exactas están fijadas en `backend/requirements.txt` y las dependencias Dart resueltas en `flutter_app/pubspec.lock`.

| Comprobación ejecutada | Resultado |
|---|---|
| Entrenamiento y evaluación del Pipeline | 1,200 filas sintéticas; 960 train / 240 test; accuracy 0.9375 |
| Django check | Sin problemas identificados |
| Migraciones | Aplicadas; comprobación de cambios pendientes sin diferencias |
| Pruebas Django | 10 pruebas aprobadas |
| Prueba HTTP real con servidor Django | Recomendación corregida, registro 201, reintento 200 y GET del mismo folio |
| Flutter analyze | Sin incidencias |
| Flutter test | 5 pruebas aprobadas: 3 de HTTP/modelos y 2 de widgets |
| Flutter build web | Compilación correcta |
| Flujo visual con Flutter y API real | 1 prueba de integración de capturas aprobada, sin MockClient |
| Revisión de PDF | Patrones: 2 páginas. Avance: 10 páginas de contenido y 4 de capturas. Renderizado y revisión de paginación |

## Qué verifican las pruebas

Backend: catálogo/búsqueda/detalle, corrección con modelo real, caso sin corrección, dinero y snapshot histórico, idempotencia y conflicto, rechazo de resultado/precio del cliente, falta de opciones, disponibilidad, tipos/rangos/JSON inválidos, métodos HTTP, CORS, folio inexistente y obligatoriedad de clave.

Cliente: codificación de búsqueda, conversión del catálogo, envío de entradas y clave, mensajes de negocio/red, recorrido perfil → recomendación → confirmación → folio y bloqueo local de presupuesto inválido en viewport móvil.

El recorrido visual adicional ejecuta los widgets de la app contra Django y SQLite mediante HTTP real: catálogo, detalle, formulario, recomendación corregida, ranking, confirmación, consulta por folio, búsqueda y ausencia de opciones. Las imágenes se obtienen con `LiveTestWidgetsFlutterBinding`, `flutter_tester` y el mecanismo de captura golden de Flutter. El modelo `.joblib` se carga y se ejecuta en Django. Las respuestas no se simulan en esta prueba.

## Evidencias incluidas

- `00_inicio.png`: catálogo de la app.
- `01_detalle.png`: respuesta de detalle de Claridad.
- `02_formulario.png`: entradas del perfil reproducible.
- `03_recomendacion.png`: opción original/final, confianzas y corrección.
- `04_reglas.png`: ranking y motivos de descarte.
- `05_folio.png`: registro efectivo y folio.
- `06_consulta.png`: recuperación independiente del mismo folio.
- `07_busqueda.png`: búsqueda del catálogo.
- `08_formulario_movil.png`: formulario en viewport de 390 × 844.
- `09_sin_opciones.png`: error 422 mostrado en la interfaz.
- `01_entradas.json`, `02_recomendacion.json`, `03_orden_registrada.json`, `04_consulta_folio.json`: prueba HTTP independiente.
- `folio_capturas.json`: folio correspondiente a las capturas. Puede diferir del JSON de la otra prueba porque son órdenes distintas.
- Logs `flutter_analyze.log`, `flutter_test.log`, `flutter_build_web.log` y `capturas_http.log`.

## Límites de la comprobación

La versión web se compiló. Las capturas no son de Chrome ni de un emulador: Chromium no pudo iniciarse en este entorno por una restricción de sockets locales. Se usó el motor real de Flutter para obtener imágenes y comprobar el flujo HTTP. No se declara ejecución de la build web dentro de un navegador, prueba Android, generación de APK, despliegue público ni publicación en GitHub.

La compilación emite un aviso sobre una familia CupertinoIcons no incluida; las pantallas utilizan MaterialIcons y esas fuentes sí se empaquetan. El aviso no impide el build. No se ha realizado prueba de carga concurrente de SQLite ni evaluación con clientes reales. Los datos son sintéticos y no hay validación clínica.

Para repetir el proceso, consulta los comandos del README. La prueba visual se ejecuta por separado con `flutter test tool/capturar_evidencias.dart --update-goldens` y requiere Django activo. Los tests habituales no requieren un servidor externo.
