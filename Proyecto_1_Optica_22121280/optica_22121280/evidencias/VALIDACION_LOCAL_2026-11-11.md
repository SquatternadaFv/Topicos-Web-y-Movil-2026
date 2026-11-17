# Verificación de esta revisión en Windows

Fecha: **11 de noviembre de 2026**. Entrega prevista: 12/11/2026.

Esta revisión aprovecha el código y los documentos existentes, contrasta la consigna con la página del curso y ejecuta las siguientes comprobaciones en este equipo. `VALIDACION.md` y los logs originales describen una construcción previa en Linux; no se presentan como resultados nuevos de Windows.

## Entorno utilizado

- Python **3.12.16**, instalado para este proyecto; entorno de la app: `optica_22121280/.venv`.
- Django **5.2.19**, scikit-learn **1.8.0**, pandas **2.2.3** y demás dependencias de `backend/requirements.txt`.
- Flutter **3.47.9**, Dart **3.13.7**, SDK existente en `C:\dev\flutter`.
- Google Chrome instalado en `C:\Program Files\Google\Chrome\Application\chrome.exe`; automatización con Playwright **1.65.0**.
- El entorno `.venv` de la carpeta superior usa Python 3.15.2 para herramientas documentales y de captura; no ejecuta el backend.

## Comprobaciones efectivamente realizadas

| Comprobación | Resultado |
|---|---|
| Consigna y asignación | Página original descargada y leída; fila 23: 22121280 → óptica → paquete de lentes/tratamiento |
| Lectura de las referencias | Dos PDF, README y guía proporcionados; contrastados con el código local |
| `manage.py test optica --verbosity 2` | **10 pruebas aprobadas**, incluyendo ejecución del modelo real |
| `manage.py check` | Sin incidencias |
| `makemigrations --check --dry-run` | Sin cambios pendientes |
| `migrate --noinput` | Base actualizada; sin migraciones pendientes |
| Reentrenamiento en carpeta temporal | Reprodujo exactamente `ml/metricas.json`: accuracy **0.9375**, 960 train / 240 test; no reemplazó el artefacto entregado |
| `flutter pub get` | Dependencias resueltas con el lock existente |
| `flutter analyze` | Sin incidencias |
| `flutter test --reporter expanded` | **5 pruebas aprobadas** |
| `flutter build web --no-web-resources-cdn --dart-define=API_BASE_URL=http://127.0.0.1:8000/api` | Compilación correcta; recursos del motor incluidos localmente |
| `scripts/iniciar_demo.py --sin-navegador` | Inició Django en 8000 y Flutter web estático en 5173 |
| `scripts/verificar_api.py` por HTTP real | Original antirreflejante → final esencial; registro 201, reintento 200 con el mismo folio y GET correcto |
| `scripts/capturar_navegador.py` | **Recorrido completo aprobado en Chrome:** formulario, recomendación, reglas, registro, consulta por folio, error de negocio 422 y viewport móvil |
| Errores JavaScript en el recorrido | **Ninguno**, registrados en `recorrido_chrome.json` |
| PDF regenerados | Avance: **14 páginas**; patrones: **2 páginas**; fecha de entrega actualizada al 12/11/2026 |
| Revisión de PDF | Renderizado de todas las páginas, revisión visual y comprobación de texto dentro de los márgenes de página |

## Evidencia nueva de navegador

Las ocho capturas nuevas muestran **Flutter web compilado ejecutándose en Chrome headless**, con peticiones HTTP a Django, SQLite y el `.joblib` reales. El script no usa MockClient ni respuestas prefabricadas.

| Archivo | Qué muestra |
|---|---|
| `10_chrome_inicio.png` | Catálogo servido por Django |
| `11_chrome_formulario.png` | Perfil 8 h, 1 h, presupuesto 700, oficina |
| `12_chrome_recomendacion.png` | Original/final, probabilidades y explicación |
| `13_chrome_reglas.png` | Ranking y motivos de descarte |
| `14_chrome_folio.png` | Solicitud guardada y folio devuelto por el servidor |
| `15_chrome_consulta.png` | Consulta independiente del mismo folio |
| `16_chrome_sin_opciones.png` | Error 422 con presupuesto 500 |
| `17_chrome_movil.png` | Formulario en navegador con viewport 390 × 844 |

`recorrido_chrome.json` contiene el folio, versión del navegador, recomendación, orden y resultado de las comprobaciones. El folio de la captura sigue en la base de demostración. Las comprobaciones crean solicitudes de prueba: no son ventas reales. Las capturas 00–09 y sus JSON se conservan como evidencias históricas de flutter_tester, no se confunden con las ocho nuevas.

## Cómo repetir la comprobación

Desde `optica_22121280`, inicia `INICIAR_DEMO.cmd`. En otra terminal:

```powershell
.\.venv\Scripts\python.exe scripts\verificar_api.py
.\.venv\Scripts\python.exe -m pip install -r scripts\requirements-evidencias.txt
.\.venv\Scripts\python.exe scripts\capturar_navegador.py
```

La ruta de Chrome se puede cambiar con `--chrome RUTA_AL_EJECUTABLE`; la URL, con `--url`. La herramienta usa la capa semántica de accesibilidad de Flutter para pulsar y rellenar los controles de la app.

## Límites reales

No se ha probado Android en emulador ni generado APK, publicado un sitio o un repositorio remoto, medido concurrencia de producción ni evaluado el modelo con clientes reales. El viewport móvil es una comprobación de diseño adaptable en Chrome. El build emite un aviso sobre CupertinoIcons; la app utiliza MaterialIcons, incluidos correctamente, y el recorrido visual no presentó iconos faltantes ni errores JavaScript.

La accuracy reproduce etiquetas sintéticas y la confianza no está calibrada. El caso corregido devuelve 0% para la clase final; ese valor se conserva en la UI. El servidor respeta las restricciones comerciales y no promete una elección clínica ni una alternativa estadísticamente óptima.
