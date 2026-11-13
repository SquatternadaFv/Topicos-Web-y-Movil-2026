# Prácticas de Flutter

Proyecto de laboratorio con los ejemplos de widgets y llamadas a los endpoints de entregas. **No es ninguno de los proyectos 1, 2 o 3** ni incorpora la aplicación individual de óptica.

## Ejecutar

Desde la raíz instalar requirements.txt, entrenar con `python ejecutar_actividades.py` y arrancar Django:

```powershell
python Actividad_Extra_Django/retos_django/manage.py migrate
python Actividad_Extra_Django/retos_django/manage.py runserver
```

Después, en otra terminal:

```powershell
cd practicas_flutter
flutter pub get
flutter run -d chrome --dart-define=API_BASE=http://127.0.0.1:8000
```

La API del laboratorio permite CORS de localhost/127.0.0.1 y sus endpoints JSON son de demostración, sin autenticación y excluidos de CSRF para este cliente; no se publican como aplicación comercial. El panel con formularios conserva CSRF. Para Android emulado: API_BASE=http://10.0.2.2:8000. Para un teléfono físico se usa la IP LAN de la computadora y se configura su acceso de forma explícita. En producción se necesita HTTPS y autenticación/autorización por recurso.

## Widgets cubiertos

`lib/laboratorio.dart` contiene StatelessWidget (FolioTexto), StatefulWidget (contador), Text, Scaffold, AppBar, TextField, ListView/ListTile, Row/Expanded, Switch, Dropdown, AlertDialog/SnackBar, Navigator, CircularProgressIndicator, controladores, Form/TextFormField, SingleChildScrollView, BottomNavigationBar, TabBar/TabBarView, Drawer, FloatingActionButton, Card, RefreshIndicator, FutureBuilder, POST con package:http, ThemeData, GridView, Image.network con error y SafeArea. La búsqueda muestra estado vacío si no encuentra folios. Las operaciones HTTP tienen timeout y error visible.

IndexedStack conserva las pantallas al cambiar de sección. La prueba de widgets comprueba que el contador mantiene su valor después de ir a la API y volver. Navegar al detalle no altera el pedido. Eso ilustra estado de UI, no implementa la misión de una app offline completa.

## Verificación real

Flutter 3.47.9/Dart 3.13.7. `flutter analyze`: sin problemas; `flutter test`: una prueba aprobada; `flutter build web --release --no-web-resources-cdn`: build generado. Capturas reales de galería y respuesta HTTP de Django en `../evidencias/verificacion/05-flutter-widgets.png` y `06-flutter-api.png`.

La compilación Android se intentó con `flutter build apk --debug --dart-define=API_BASE=http://10.0.2.2:8000`. El SDK comenzó a descargar el NDK 28.2.13676358, pero la descarga no avanzó y se interrumpió; no se afirma que exista un APK terminado. El manifest debug permite HTTP únicamente para el laboratorio; release requiere configurar HTTPS.

## Web en Docker y empaquetado

Las carpetas `build/`, `.dart_tool/` y `.gradle/` son generadas y se eliminan al limpiar el proyecto. Para servir la web o repetir las capturas, ejecutar primero `flutter pub get` y `flutter build web --release --no-web-resources-cdn --dart-define=API_BASE=http://127.0.0.1:8000`. Los fuentes, `pubspec.lock` y las capturas de evidencia sí se conservan.

`Dockerfile` tiene etapa de compilación y nginx. Ajustar/pinear FLUTTER_IMAGE a una imagen disponible con la versión requerida; API_BASE es la URL que ve el navegador, no un nombre interno de Compose. La imagen no se ejecutó aquí porque falta Docker. Para servir el build ya verificado sin Docker: `python -m http.server 19000 --directory build/web` desde esta carpeta.

Android: `flutter build apk --debug --dart-define=API_BASE=http://10.0.2.2:8000`, una vez instalado el NDK requerido. iOS requiere macOS/Xcode; los comandos del apunte no se hacen pasar por una ejecución en Windows. Las respuestas a las preguntas cortas y de empaquetado están en `../actividades/discusion_web_movil.md`.
