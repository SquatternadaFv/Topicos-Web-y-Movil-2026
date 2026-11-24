# Lúmina Óptica · Proyectos 1 y 2 individuales

**Eduardo Osvaldo Rodríguez Gutiérrez · 22121280**  
Ingeniería en Sistemas Computacionales · Instituto Tecnológico de Morelia  
Tópicos Selectos de Tecnologías Web y Móvil · Entrega de análisis: 12 de noviembre de 2026

Sistema académico que recomienda un **paquete de lentes y tratamientos comerciales**, muestra cómo intervienen el modelo y las reglas, y registra una solicitud con folio. Está construido con Django + SQLite y Flutter. La asignación corresponde a la fila 23 de [Proyectos Flutter (progresivos)](https://ealcaraz85.github.io/topicoswebmobil/#orgcb3827a), consultada el 10/11/2026.

**Revisión conjunta del 17/11/2026:** P1 se conserva y P2 añade un asistente entrenado dentro de la misma aplicación. Para estudiar y exponer utiliza la [guía detallada de ambos proyectos](docs/DEFENSA_PROYECTOS_1_Y_2.md), disponible también en [PDF](docs/DEFENSA_PROYECTOS_1_Y_2.pdf), con arquitectura, datos, entrenamiento, contratos y 50 preguntas de defensa. Consulta la [matriz conjunta](docs/MATRIZ_PROYECTOS_1_Y_2.md), el [análisis de patrones actualizado de dos páginas](docs/ANALISIS_PATRONES_P1_P2.pdf) y la [validación actual](evidencias/VALIDACION_P1_P2_2026-11-17.md). Los informes `Avance_Analisis_22121280.pdf`, `Analisis_Patrones_22121280.pdf` y `GUIA_CONSTRUCCION.md` ya existían y explican P1.

## Configuración móvil y Git: apuntes actualizados el 24/11/2026

Se revisaron los apartados nuevos [De Flutter web al celular](https://ealcaraz85.github.io/topicoswebmobil/#org6a74d56), [Actualizar la app con Git](https://ealcaraz85.github.io/topicoswebmobil/#org0999286) y las indicaciones de [desarrollo con IA](https://ealcaraz85.github.io/topicoswebmobil/#orgb12d96e). La revisión cubre configuración, reproducción y documentación de Lúmina P1/P2; la auditoría con IA local se trabajará posteriormente. No se presenta como implementación del proyecto de equipo P3.

| Indicación de los apuntes | Estado de Lúmina |
|---|---|
| Mismo cliente para web y Android | `flutter_app/lib/` compartido; Django, modelos y corpus permanecen en el servidor |
| Flutter estable, SDK Android, licencias y dispositivo | Flutter 3.47.9 stable / Dart 3.13.7; SDK 36, JDK de Android Studio y realme RMX3760 detectados. Se instalaron las Command-line Tools 23; `flutter doctor -v` ya marca Android en verde y licencias aceptadas |
| Dirección de API configurable | `ApiClient.defaultUrl` usa `String.fromEnvironment('API_BASE_URL')`; equivale al nombre ilustrativo `API_BASE` de los apuntes |
| Permiso de Internet y HTTP de laboratorio | INTERNET en el manifest principal; cleartext únicamente en `src/debug/AndroidManifest.xml`. Release requiere una API HTTPS |
| APK instalable que habla con la API | APK debug con firma verificada, catálogo, recomendación, folio y chat comprobados en esta PC y teléfono. Los apuntes permiten explícitamente debug para demostrar en el salón |
| Código, lockfile, Android y assets en Git | Incluidos; fuentes y fotografías locales también. Se excluyen compilaciones, `.dart_tool`, configuración de SDK, `.env`, claves y keystores |
| Versión identificable del avance | `pubspec.yaml`: **1.1.0+2**; Android usa esos valores como versionName/versionCode |
| Mismo historial para web y móvil | Avance publicado en `main` y en `revision-movil-2026-11-24`. Se conserva el historial anterior |

La advertencia restante de doctor corresponde a Visual Studio para aplicaciones **Windows de escritorio**; no es requisito para web o Android. El paquete de herramientas se obtuvo del índice oficial de Google y se verificó contra su checksum. La descarga actual de los apuntes devolvió HTTP 200, `Last-Modified: 24/11/2026 04:44:58 GMT` y SHA-256 `6a170f78801f94c4219577584fbbaeec7243b1a6d2a95187b5e827fbad29ca7d`.

### URL por destino

| Destino | `--dart-define=API_BASE_URL=...` | Backend |
|---|---|---|
| Chrome en esta PC | `http://127.0.0.1:8000/api` | Django local |
| Emulador sin túnel | `http://10.0.2.2:8000/api` | Django accesible desde el emulador |
| Teléfono por USB, método usado aquí | `http://127.0.0.1:8000/api` más `adb reverse tcp:8000 tcp:8000` | Django local; mantener USB y backend activos |
| Teléfono por Wi-Fi | `http://IP_DE_LA_PC:8000/api` | `runserver 0.0.0.0:8000`, `DJANGO_ALLOWED_HOSTS` con esa IP y acceso de red permitido |
| Release | `https://TU_API/api` | API HTTPS accesible; no usar el backend HTTP local con este artefacto |

El túnel ADB es la razón por la que localhost funciona en la APK instalada; sin túnel debe cambiarse la URL. El nombre de la constante puede diferir del ejemplo del profesor; deben coincidir `--dart-define` y `String.fromEnvironment`.

### Actualizar desde Git y reconstruir

Ejecuta Git desde la raíz **Topicos-Web-y-Movil-2026**, donde está el remoto `origin`. Esta copia antigua también contiene un `.git` interno sin remoto, con un historial del 11/11. Windows impidió moverlo; se conserva intacto. Dentro de la carpeta de Lúmina usa `GIT_LUMINA.cmd status`, `GIT_LUMINA.cmd log` o `git -C RUTA_DEL_REPOSITORIO_PRINCIPAL ...` para evitar consultar ese historial antiguo. El `.git` interno no se distribuye al clonar el repositorio principal.

```powershell
# Desde Topicos-Web-y-Movil-2026, con el trabajo local previamente guardado:
git status
git fetch origin
git switch main
git pull --ff-only
cd Proyecto_1_Optica_22121280/optica_22121280/flutter_app
flutter pub get
flutter analyze
flutter test

# Demostración local por USB; permite HTTP solo en debug:
flutter build apk --debug --dart-define=API_BASE_URL=http://127.0.0.1:8000/api
adb install -r build/app/outputs/flutter-apk/app-debug.apk
adb reverse tcp:8000 tcp:8000

# Empaquetado release, cuando exista una API HTTPS:
flutter build apk --release --dart-define=API_BASE_URL=https://TU_API/api
```

`flutter clean` es opcional y se reserva para problemas de caché. `pubspec.lock` se conserva en Git. El avance está [publicado en main](https://github.com/SquatternadaFv/Topicos-Web-y-Movil-2026/tree/main) y también en `revision-movil-2026-11-24`; `git pull --ff-only` permite traerlo al repositorio actualizado. La [entrega Android 1.1.0+2](https://github.com/SquatternadaFv/Topicos-Web-y-Movil-2026/releases/tag/lumina-p1-p2-v1.1.0-2026-11-24) adjunta APK, SHA-256 y manifiesto. La entrega del 17/11 se conserva como antecedente.

Se comprobó un clon nuevo del commit **`0bdbeba`**: dependencias resueltas con `flutter pub get --offline`, `flutter analyze` sin avisos, once pruebas aprobadas y APK debug 1.1.0+2 compilada. Esa APK, no una copia de la build anterior, se instaló con `adb install -r` en el realme; Android confirmó versionName 1.1.0, versionCode 2 y el túnel al puerto 8000. Los comandos y resultados están en [validacion_clon.json](evidencias/2026-11-24/configuracion/validacion_clon.json) y [telefono_1_1_0.json](evidencias/2026-11-24/configuracion/telefono_1_1_0.json). El JSON de entrega incluye commit de origen, versión y SHA-256 para identificar el binario.

También terminó correctamente `flutter build apk --release` desde ese clon (50.8 MB). Esta fue una comprobación de empaquetado con la dirección HTTPS reservada `https://example.invalid/api`; no es un servidor de Lúmina ni una release conectada a una API desplegada. No se instaló ese binario. La demostración funcional permanece en la APK debug con backend local, admitida por los apuntes. El clon terminó sin cambios en los archivos versionados.

### Uso de IA en este avance

Se utilizó **OpenAI Codex** para implementar y revisar código, documentación, pruebas, rediseño y configuración bajo las indicaciones del estudiante. No se declara que esta asistencia haya usado Ollama ni una IA local. El apartado del profesor permite herramientas ya disponibles, incluido un plan de pago; no exige comprar uno.

Los generadores de perfiles e intenciones, el entrenamiento scikit-learn y sus artefactos están en `ml/` y `backend/optica/modelo/`; los datos son sintéticos y específicos del dominio, no registros reales de clientes. Se ejecutaron entrenamiento y pruebas documentados en las evidencias; no se atribuyen a una revisión personal del estudiante las verificaciones que hizo el agente. Para la defensa, el estudiante debe revisar y poder explicar perfil → API → modelo/reglas → JSON → pantalla, así como los datos y las métricas. **No se ha realizado la auditoría con IA local de los apartados finales.**

## Rediseño web y Android · 24/11/2026

La interfaz comparte una paleta marfil, ciruela y lavanda, portada editorial con fotografías reales de lentes, catálogo adaptable, navegación superior en escritorio e inferior en móvil. Se retiró la referencia P1/P2 del encabezado visible. Formulario, folio y asistente conservan la API existente. Las fuentes Roboto y su licencia se incluyen en `flutter_app/assets/fonts/`; la compilación web usa `--no-web-resources-cdn` para servir también CanvasKit localmente.

Se mantienen los cuatro paquetes: la consigna pide catálogo coherente, listado, detalle y búsqueda, sin establecer un mínimo de productos. Las cinco fotos se incluyen como assets locales en `flutter_app/assets/images/` y funcionan sin descargar imágenes durante el uso. Son referencias visuales de armazones; no acreditan tratamientos ópticos ni equivalen a inventario real.

Fotos utilizadas bajo la [licencia de Pexels](https://www.pexels.com/license/): [Esencial, Pixabay](https://www.pexels.com/photo/gold-framed-eye-glasses-53177/), [Claridad, Saliem Moeslan](https://www.pexels.com/photo/close-up-shot-of-a-pair-of-eyeglasses-13430489/), [Transición, Evgeniy Alekseyev](https://www.pexels.com/photo/a-close-up-shot-of-an-eyeglasses-on-white-surface-7357976/), [Integral, Curtis Adams](https://www.pexels.com/photo/close-up-of-eyeglasses-17246017/) y [portada, Evgeniy Alekseyev](https://www.pexels.com/photo/eyeglasses-in-close-up-shot-7357970/). `assets/images/sources.json` conserva fuentes, autores, fecha y enlaces de descarga.

Para verlo, ejecuta `INICIAR_DEMO.cmd`. El APK actualizado se genera localmente en `entrega_android/Lumina-Optica-P1-P2.apk` y está adjunto a la entrega 1.1.0+2 del 24/11. Las capturas del rediseño y el recorrido real se guardan en `evidencias/2026-11-24/`. Se ejecutaron 11 pruebas Flutter, incluida navegación a 320, 390, 900 y 1440 px, y el recorrido Chrome con catálogo, recomendación, registro, consulta de folio y asistente.

**Cuentas y pagos según la consigna:** en la copia de los apuntes consultada el 17/11, los apartados [P1](https://ealcaraz85.github.io/topicoswebmobil/#orgd85c21d) y [P2](https://ealcaraz85.github.io/topicoswebmobil/#orga05f98b) no enumeran registro/inicio de sesión de usuarios. P1 pide registrar la operación con folio y añade la consulta GET por folio; P2 conserva esa búsqueda y la integra con el asistente. «Registrar la operación» significa guardar una solicitud, no crear una cuenta. La [consideración final de P3](https://ealcaraz85.github.io/topicoswebmobil/#org6560959) aclara expresamente: «No se pide publicar en tiendas ni pagos reales». El seguimiento por folio no necesita una pasarela de pagos. Esto describe el texto disponible, sin asumir instrucciones verbales posteriores.

## En tu computadora, después de esta revisión

La revisión del 11/11/2026 parte del código y los documentos que ya estaban en esta carpeta. Se contrastaron con el apartado original del curso y se preparó un entorno Python 3.12 separado: `optica_22121280/.venv` (el entorno de la carpeta superior sigue usando Python 3.15). Flutter está en `C:\dev\flutter`; puedes usar su ruta completa si `flutter` no aparece en PATH.

Abre **INICIAR_DEMO.cmd** para iniciar la API y la versión web compilada en `http://127.0.0.1:5173`. Mantén abierta su terminal y usa Ctrl+C para detener ambos procesos. Este acceso requiere `.venv` y `flutter_app/build/web`, preparados en este equipo; un ZIP de código no lleva entornos de Python ni SDK. En otro equipo sigue la instalación completa de abajo y compila Flutter antes de usarlo.

El informe tiene también fuente editable en [docs/AVANCE_ANALISIS.md](docs/AVANCE_ANALISIS.md). La relación detallada con los apartados originales está en [docs/RELACION_APUNTES.md](docs/RELACION_APUNTES.md). El registro de esta revisión está en [evidencias/VALIDACION_LOCAL_2026-11-11.md](evidencias/VALIDACION_LOCAL_2026-11-11.md); `VALIDACION.md` documenta la construcción anterior.

## Qué recomienda frente al ejemplo de clase

El ejemplo del curso recomienda medios de transporte a partir de distancia, peso y contexto de envío. Esta adaptación utiliza horas de pantalla, horas en exteriores, presupuesto, uso principal y preferencia de fotocromático para sugerir **Esencial, Claridad, Transición o Integral**. Conserva la tubería aprendida: CSV → partición entrenamiento/prueba → preprocesamiento → árbol → `.joblib` → `predict_proba` → reglas → JSON → Flutter → orden con folio. El objetivo es una elección comercial académica: no se determina graduación, diagnóstico ni eficacia clínica.

## Alcance

- Catálogo con cuatro paquetes, búsqueda por nombre y detalle desde la API.
- Formulario Flutter con validación local y validación independiente en Django.
- Recomendación real de un árbol entrenado: original, final, confianza de ambas opciones, ranking, corrección y motivos de descarte.
- Reglas de presupuesto, disponibilidad y preferencia fotocromática obligatoria.
- Confirmación con recálculo en el servidor, precio y resultado históricos, folio UUID y consulta por folio.
- Carga, reintentos, mensajes de error, URL base configurable e idempotencia de confirmación.
- Admin Django para catálogo y consulta de órdenes. No hay credenciales predefinidas.

P2 incorpora chat, clasificador TF-IDF + regresión logística entrenado con 160 frases propias, consultas a catálogo/órdenes, explicación histórica por folio y recuperación de seis documentos públicos con fuentes. No hay LLM ni servicio comercial de chat. El asistente dirige al recomendador P1 para decisiones nuevas. Se mantiene el monolito; microservicios/gateway de P3 están fuera de este alcance. Los precios, paquetes, etiquetas y reglas son supuestos de una óptica ficticia, no requisitos clínicos dictados por el docente.

## Estructura

| Carpeta | Responsabilidad |
|---|---|
| `backend/config/` | Configuración y entrada de rutas Django |
| `backend/optica/` | Modelos, API, repositorios, reglas y casos de uso |
| `backend/optica/modelo/` | Artefacto entrenado incluido |
| `ml/` | CSV sintético, generación, entrenamiento y métricas |
| `flutter_app/lib/` | Cliente web/Android: modelos, HTTP, pantallas y widgets |
| `docs/` | Análisis, guía, trazabilidad y diagramas PNG/SVG/DOT |
| `evidencias/` | Capturas de flutter_tester con HTTP real y JSON del recorrido |
| `scripts/` | Prueba HTTP reproducible |

## Requisitos de desarrollo

- Python **3.12** recomendado, con `pip` y `venv`.
- Flutter estable con Dart 3.8 o superior. Se verificó con Flutter 3.47.9 / Dart 3.13.7.
- Chrome o Edge para la ejecución web. Android Studio + SDK/emulador solo si ejecutarás Android.
- Acceso a Internet en la primera instalación de dependencias.

Comprueba en PowerShell:

```powershell
python --version
python -m pip --version
flutter --version
flutter doctor
```

Si `python` o `py` no se reconocen, instala Python desde [python.org](https://www.python.org/downloads/windows/), habilita **Add python.exe to PATH** y abre una terminal nueva. En una PC con instalación restringida usa tu equipo personal o solicita la instalación al responsable. Flutter se instala siguiendo [la guía oficial](https://docs.flutter.dev/install); añade `flutter\bin` a PATH. No basta con instalar las extensiones de VS Code.

## Inicio rápido en Windows: backend

Descomprime el ZIP en una ruta corta como `C:\Proyectos\optica_22121280`. Abre esa carpeta en VS Code. Los comandos siguientes parten de la raíz que contiene `backend`, `ml` y `flutter_app`.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
.\.venv\Scripts\python.exe backend\manage.py migrate
.\.venv\Scripts\python.exe backend\manage.py sembrar_demo
.\.venv\Scripts\python.exe backend\manage.py runserver 127.0.0.1:8000
```

Se usa el ejecutable del entorno directamente; no es necesario cambiar la política de ejecución de PowerShell. Mantén abierta esta terminal. Visita `http://127.0.0.1:8000/api/catalogo/` y comprueba que aparecen cuatro paquetes. El ZIP incluye `backend/db.sqlite3` con datos de demostración; migraciones y semilla también permiten reconstruirla desde cero. La semilla crea/actualiza el catálogo, restablece disponibilidad y no borra órdenes.

En Linux/macOS:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.txt
.venv/bin/python backend/manage.py migrate
.venv/bin/python backend/manage.py sembrar_demo
.venv/bin/python backend/manage.py runserver 127.0.0.1:8000
```

## Inicio rápido: Flutter web

Abre una **segunda terminal** desde la raíz:

```powershell
cd flutter_app
flutter pub get
flutter run -d chrome --web-port=5173 --dart-define=API_BASE_URL=http://127.0.0.1:8000/api
```

Si usas Edge: sustituye `-d chrome` por `-d edge`. El backend permite CORS para `http://localhost:5173` y `http://127.0.0.1:5173`. Si cambias el puerto, cambia también la variable de entorno del backend y reinícialo:

```powershell
$env:CORS_ALLOWED_ORIGINS="http://localhost:5300,http://127.0.0.1:5300"
```

Las variables de `backend/.env.example` son ejemplos: el proyecto **no carga `.env` automáticamente**. Se exportan en la terminal. `API_BASE_URL` se define al compilar; después de cambiarla detén la app y ejecútala de nuevo. La URL termina en `/api`, sin duplicar `/api/api`.

## Android

**APK actual de P1 + P2: 1.1.0+2, del 24/11/2026:** [descargar Lumina-Optica-P1-P2.apk](https://github.com/SquatternadaFv/Topicos-Web-y-Movil-2026/releases/download/lumina-p1-p2-v1.1.0-2026-11-24/Lumina-Optica-P1-P2.apk). Guarda la descarga en `entrega_android/`. Para abrirlo en el emulador de esta PC ejecuta **`ABRIR_ANDROID.cmd`** desde la raíz de la aplicación. Inicia el AVD, instala la app y conecta su puerto 8000 al mismo Django mediante `adb reverse`. Consulta [las instrucciones Android](entrega_android/LEEME.md) y [la verificación actual del teléfono](evidencias/2026-11-24/configuracion/telefono_1_1_0.json). El APK es debug para demostración, con firma verificada; el código fuente y comandos permiten regenerarlo.

Con el emulador activo:

```powershell
cd flutter_app
flutter devices
flutter run -d ID_DEL_EMULADOR --dart-define=API_BASE_URL=http://10.0.2.2:8000/api
```

El manifest principal incluye el permiso INTERNET; el manifest de **debug** habilita HTTP local. La versión release debe usar HTTPS. Para un teléfono físico, conecta ambos equipos a la misma red, utiliza la IP de tu PC en `API_BASE_URL` y arranca Django así (ejemplo: IP 192.168.1.50):

```powershell
$env:DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1,10.0.2.2,192.168.1.50"
.\.venv\Scripts\python.exe backend\manage.py runserver 0.0.0.0:8000
```

Revisa la regla de firewall para el puerto 8000 en la red privada si eliges conexión por Wi-Fi. `localhost` en Android apunta al dispositivo; el acceso `ABRIR_ANDROID.cmd` usa un túnel ADB que redirige ese puerto a la PC. El código compartido cubre P1 y P2; la revisión Android posterior a la web se documenta por separado y no implica implementar microservicios ni gateway de P3.

## Demostración de cinco minutos

1. En **Catálogo**, busca `Claridad`, abre su detalle y vuelve. Limpia la búsqueda para ver las cuatro opciones.
2. Abre **Mi recomendación**. El formulario inicia con pantalla `8`, exterior `1`, presupuesto `700`, uso `Oficina`, preferencia fotocromática desactivada.
3. Pulsa **Obtener recomendación**. El árbol propone `antirreflejante` (Claridad, $1,100) con 85%; la regla de presupuesto lo descarta y elige `esencial` (Esencial, $650). La confianza para la alternativa final es **0%**, un resultado real que la UI muestra sin inflarlo.
4. Explica que 0% significa que el árbol no asignó masa a esa clase en esa hoja; la política comercial garantiza restricciones, no confianza estadística. Ante empates se ordena por código; no hay una promesa de que la alternativa sea la óptima. En una versión real se podría pedir revisión humana bajo un umbral justificado.
5. Revisa el ranking y los motivos. Pulsa **Registrar solicitud y obtener folio**; confirma en el diálogo.
6. Copia el folio. Vuelve al inicio, abre **Consultar folio**, pégalo y comprueba el paquete, precio y perfil históricos.
7. Repite con presupuesto `3000`: el modelo y las reglas coinciden en Claridad. Repite con `500`: aparece error de negocio y no se guarda orden.
8. Activa fotocromático con presupuesto `700`: no hay opción válida. Con presupuesto `2000`, sí se puede recomendar Transición.

## Regenerar los datos y el modelo

Desde la raíz y sin el servidor en ejecución:

```powershell
.\.venv\Scripts\python.exe ml\generar_datos.py
.\.venv\Scripts\python.exe ml\entrenar.py
```

La primera orden regenera 1,200 filas con semilla 22121280. La segunda separa 960 para entrenamiento y 240 para prueba (estratificado, semilla 42), entrena un Pipeline con OneHotEncoder y árbol (profundidad 6, hoja mínima 12), y escribe `.joblib`, `ml/metricas.json` y `ml/arbol.txt`. Reinicia Django: el modelo se mantiene en caché por proceso.

Se fijan las versiones en `requirements.txt` para que entrenamiento y carga usen el mismo scikit-learn. El artefacto se genera con código propio y no debe reemplazarse por un `.joblib` de origen desconocido. La accuracy de 93.75% mide reproducción de etiquetas sintéticas en la partición de prueba. No demuestra desempeño clínico, generalización a clientes reales ni cumplimiento de las reglas: esas restricciones se verifican aparte.

## API

### P2: entrenar y demostrar el asistente

Desde la raíz, usando el mismo entorno que el backend:

```powershell
.\.venv\Scripts\python.exe ml\generar_intenciones.py
.\.venv\Scripts\python.exe ml\entrenar_asistente.py
.\.venv\Scripts\python.exe ml\indexar_corpus.py
```

El dataset tiene 160 frases y ocho intenciones. La partición estratificada reserva 32 para prueba y usa 128 para entrenamiento; la accuracy medida es **75 %** (24/32), antes del umbral de aclaración. Los errores se entregan en `ml/prueba_asistente.csv`. Reinicia Django al cambiar los artefactos: los modelos y el índice permanecen en caché por proceso.

En **Asistente**, escribe `hola`, `qué paquetes ofrecen`, `quiero rastrear mi orden`, `explica mi orden`, `cuál es el horario de atención` y `quién ganó el partido de fútbol`. Para seguimiento/explicación pega un folio creado desde P1 en el campo de referencia. `qué paquete me recomiendas` abre el formulario P1: el chat no inventa una clase. Consulta la guía conjunta para distinguir entrenamiento de intenciones, corpus público y datos actuales de SQLite.

Para repetir las capturas conjuntas con la demo activa y Playwright instalado:

```powershell
.\.venv\Scripts\python.exe scripts\capturar_navegador.py --con-asistente --salida evidencias\2026-11-17
```

Usa `--chrome RUTA_AL_EJECUTABLE` si tu navegador no está en la ruta predeterminada. El comando registra una solicitud demo y verifica que el chat use el mismo folio. El viewport móvil es una comprobación de diseño adaptable en navegador, no una prueba Android.

Para regenerar los documentos conjuntos sin sobrescribir los informes históricos:

```powershell
.\.venv\Scripts\python.exe -m pip install -r docs\requirements-documentos.txt
.\.venv\Scripts\python.exe scripts\exportar_guias.py
```

### Endpoints

Todos los endpoints terminan con `/`. Los POST de recomendación y orden reciben el perfil completo, **sin precio, clase final ni confianza enviados por Flutter**. El POST del asistente recibe `mensaje` y, opcionalmente, `folio` o un `perfil` completo para delegar en el recomendador.

| Método | Ruta | Resultado |
|---|---|---|
| GET | `/api/salud/` | Estado de la API |
| GET | `/api/catalogo/?q=Claridad` | Lista y búsqueda por nombre |
| GET | `/api/catalogo/esencial/` | Detalle de un paquete |
| POST | `/api/asistente/` | Mensaje y folio opcional → intención, respuesta, fuentes, acción y datos |
| POST | `/api/recomendaciones/` | Vista previa con modelo + reglas; no guarda |
| POST | `/api/ordenes/` | Recalcula, guarda y devuelve folio; requiere `Idempotency-Key` UUID |
| GET | `/api/ordenes/<folio>/` | Resultado histórico de la orden |

```json
{
  "horas_pantalla": 8,
  "horas_exterior": 1,
  "presupuesto": 700,
  "uso_principal": "oficina",
  "prefiere_fotocromatico": false
}
```

En `evidencias/02_recomendacion.json` hay una respuesta real completa. Los códigos son 200 (consulta o reintento de confirmación), 201 (orden creada), 400 (entrada/clave inválida), 404 (recurso inexistente), 405 (método), 409 (clave reutilizada con otro perfil), 413 (cuerpo grande), 415 (Content-Type), 422 (sin alternativa elegible), 503 (modelo ausente). La ruta de consulta exige un UUID válido; una ruta mal formada responde 404 del enrutador Django.

## Verificación

Backend desde raíz:

```powershell
.\.venv\Scripts\python.exe backend\manage.py check
.\.venv\Scripts\python.exe backend\manage.py test optica
.\.venv\Scripts\python.exe scripts\verificar_api.py
```

El tercer comando requiere Django activo y registra una orden demo. Comprueba original/final, POST, reintento idempotente y GET por folio. Con una base modificada debes restaurar el catálogo mediante `sembrar_demo` para reproducir los importes de la prueba.

Flutter, desde `flutter_app`:

```powershell
flutter analyze
flutter test
flutter build web --no-web-resources-cdn --dart-define=API_BASE_URL=http://127.0.0.1:8000/api
```

El registro de validación, versiones y límites de lo comprobado está en `evidencias/VALIDACION.md`.

## Administrar los datos

```powershell
.\.venv\Scripts\python.exe backend\manage.py createsuperuser
```

Define tus propias credenciales y entra a `http://127.0.0.1:8000/admin/`. Puedes marcar un paquete como no disponible para probar la regla. No borres ni renombres códigos usados como clases del modelo; si añades una nueva clase, necesitas datos, entrenamiento y una revisión del contrato. El precio confirmado y el snapshot de cada orden permanecen históricos aunque edites el catálogo.

## Decisiones y límites

- Monolito Django con API: una app cliente separada no constituye microservicios.
- SQLite: apropiado para una demostración individual local; no se promete concurrencia de producción.
- API pública sin datos personales ni autenticación del comprador. El folio UUID dificulta adivinar solicitudes, pero no sustituye autorización. Antes de manejar clientes reales harían falta identidad, permisos, límites de consumo y HTTPS.
- El admin conserva sus mecanismos de sesión y CSRF. Solo los endpoints públicos JSON están exentos de CSRF; no aceptan sesión como autorización.
- Orden equivale a solicitud académica. No hay pago real, graduación médica, envío ni descuento de existencias físicas. `disponible` representa disponibilidad del paquete, no inventario por unidad.
- El sistema revalida al confirmar: una recomendación preliminar puede cambiar si cambian catálogo, disponibilidad o modelo. La pantalla de orden presenta el resultado final efectivamente guardado.
- Los PDF, README y guía aportados se usaron como referencias y se contrastaron con los apuntes y el código local. Las afirmaciones de validación anteriores se distinguen de las comprobaciones de esta revisión en Windows.

## Historial y entrega manual en GitHub

Se incluye un repositorio local con commits de construcción asistida por IA y un registro legible en `docs/HISTORIAL.txt`. No se ha creado ni publicado un repositorio remoto.

Si tienes Git, desde la raíz puedes usar `git log --oneline` y conectar tu remoto propio. Si en el trabajo no puedes instalarlo, crea un repositorio en GitHub desde el navegador y usa **Add file → Upload files** para subir las carpetas. No subas `.venv`, `.dart_tool`, `build`, credenciales ni `.git` mediante el navegador. Conserva `pubspec.lock`, migraciones, CSV y `.joblib`. Puedes incluir la base demo para la revisión; `.gitignore` la excluye por defecto y siempre se reconstruye con las migraciones y la semilla.

La subida manual crea el historial de GitHub a partir de esos commits web; no transporta automáticamente el historial local. Haz cambios y commits reales posteriores conforme comprendas y ajustes el proyecto.

## Uso de IA y responsabilidad académica

Se utilizó ChatGPT/Codex para interpretar los requisitos, proponer la separación de responsabilidades, generar el código y datos sintéticos, preparar pruebas, diagramas y documentación. El informe distingue resultados ejecutados de instrucciones pendientes en el equipo del estudiante. Antes de exponer o entregar, Eduardo debe ejecutar el flujo, revisar las decisiones, adaptar lo necesario y explicar con sus palabras las limitaciones del dataset. Esta nota no afirma una revisión personal ni una ejecución en su computadora que todavía no ha ocurrido.

## Cómo se produjeron las capturas originales (00–09)

Las imágenes PNG muestran los widgets reales de la aplicación ejecutados con `LiveTestWidgetsFlutterBinding` y `flutter_tester`. El cliente hizo peticiones HTTP al backend Django con el árbol entrenado y la base SQLite; no se usó `MockClient` para estas capturas. La tipografía Roboto y los iconos se cargaron del SDK. La build web se comprobó por compilación; la captura automatizada en Chromium no pudo ejecutarse por las restricciones de sockets de este entorno. No se presentan estas imágenes como capturas de navegador o emulador.

Para regenerarlas, mantén Django activo en el puerto 8000. En otra terminal, desde `flutter_app`:

```powershell
$env:FLUTTER_ROOT="C:\src\flutter" # ajusta a donde instalaste el SDK
flutter test tool\capturar_evidencias.dart --update-goldens
```

Este comando registra una solicitud de prueba y actualiza las evidencias. No forma parte de `flutter test` normal, que usa dobles HTTP y no requiere el backend. La versión móvil del formulario en las capturas es un viewport de 390 × 844; no implica ejecución en un teléfono.

## Capturas de Chrome de esta revisión (10–17)

La revisión del 11/11/2026 también ejecutó la build web en Chrome con la API real. Se comprobó recomendación → reglas → registro → folio → consulta y ausencia de opciones; no hubo errores JavaScript. Los anexos del PDF actualizado utilizan estas capturas. Para regenerarlas con la demo activa:

```powershell
.\.venv\Scripts\python.exe -m pip install -r scripts\requirements-evidencias.txt
.\.venv\Scripts\python.exe scripts\capturar_navegador.py
```

Requiere Chrome instalado; no descarga otro navegador. El comando crea una solicitud de demostración y guarda ocho PNG y `evidencias/recorrido_chrome.json`. Consulta [la validación local](evidencias/VALIDACION_LOCAL_2026-11-11.md) para distinguir las comprobaciones de Windows de las evidencias previas.

## Regenerar los informes de entrega

Desde la raíz del proyecto, con Python 3.12:

```powershell
.\.venv\Scripts\python.exe -m pip install -r docs\requirements-documentos.txt
.\.venv\Scripts\python.exe scripts\generar_informes.py
```

El generador usa Arial en Windows y DejaVu Sans en Linux. Regenera ambos PDF y las fuentes Markdown del avance y de patrones. La fecha de entrega predeterminada es 12/11/2026; puedes cambiarla con `$env:FECHA_ENTREGA="2026-11-12"` antes de ejecutarlo. Requiere conservar `docs/diagramas/`, `ml/metricas.json` y las evidencias JSON/PNG del proyecto.

## Preparar el ZIP de entrega

Detén la demo con Ctrl+C y ejecuta:

```powershell
.\.venv\Scripts\python.exe scripts\empaquetar_entrega.py
```

El ZIP se escribe en la carpeta superior. Incluye código backend y Flutter, CSV, modelo entrenado, SQLite demo, informes, diagramas y evidencias. Excluye entornos, SDK, build web, cachés, `.git` y configuración local. En otro equipo se instala y compila siguiendo este README. El historial local previo está exportado en `docs/HISTORIAL.txt`; la revisión actual está descrita en `docs/REVISION_2026-11-11.md` y no se ha publicado en un remoto.
