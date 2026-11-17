# Validación Android de Lúmina Óptica: P1 + P2

Fecha: **17/11/2026**. Extiende la [validación web conjunta](VALIDACION_P1_P2_2026-11-17.md).

## Resultado

**APK compilado, firma verificada, instalado y abierto en el emulador de esta PC.** La actividad `mx.edu.itm.optica_app/.MainActivity` quedó en primer plano. Android completó el arranque y el proceso de la aplicación estaba activo; esos datos y los textos de interfaz se conservaron en [android-2026-11-17/ejecucion.json](android-2026-11-17/ejecucion.json).

| Elemento | Resultado comprobado |
|---|---|
| APK | `entrega_android/Lumina-Optica-P1-P2.apk` |
| Tipo | Debug para revisión académica |
| Paquete / versión | `mx.edu.itm.optica_app`, 1.0.0, código 1 |
| Tamaño | 150,925,026 bytes, aproximadamente 144 MiB |
| SDK mínimo / objetivo | API 24 / API 36 |
| Arquitecturas | ARM32 (`armeabi-v7a`), ARM64 (`arm64-v8a`) y x86_64 |
| Firma | `apksigner verify --verbose`: **Verifies**, APK Signature Scheme v2 válida |
| Emulador | `Medium_Phone_API_37.0`, dispositivo `emulator-5554` |
| Android ejecutado | API 37; `sys.boot_completed=1` |
| Aceleración | AEHD 2.2 instalado y utilizable; comprobación con código 0 |
| Instalación | `adb install -r`: **Success** |
| Inicio | `am start`: actividad de Lúmina abierta |
| Conexión con Django | `adb reverse tcp:8000 tcp:8000` activo |

SHA-256 del APK:

```text
1e1f8f83574a6514593a4c75e6e27d6253ade520522357088482c8103cfd7ecb
```

El tamaño, hash, versión, arquitecturas y comando están también en `entrega_android/apk_info.json` y `SHA256SUMS.txt`. El APK es un artefacto local regenerable y se excluye de Git; el código y las instrucciones se conservan.

## Preparación del entorno

La carpeta del NDK existente solo contenía un marcador de instalación incompleta. Se completó la descarga oficial de NDK r28c y se verificaron sus 748,118,221 bytes y SHA-1 `086bba43ff2f5eb0e387b15c8278bb4e0d89ba1d`, publicados en la [versión oficial de Android NDK](https://github.com/android/ndk/releases/tag/r28c). Después de extraerlo, `source.properties` confirmó `28.2.13676358`, versión requerida por este Flutter.

Gradle instaló Android SDK Platform 36, que faltaba. La compilación posterior terminó correctamente en 129.2 segundos. El log completo se conserva en `android_build_2026-11-17.log`.

La CPU ya tenía la virtualización habilitada, pero no había hipervisor utilizable. La prueba sin aceleración no consiguió arrancar Android. Se preparó AEHD 2.2 desde el repositorio oficial de Google, se comprobó la firma válida de `Google LLC` y el usuario aceptó el aviso de administrador de Windows. El servicio `aehd` quedó `RUNNING` y `emulator -accel-check` confirmó que era utilizable. Es una dependencia del entorno de desarrollo; no forma parte del backend ni del APK. Referencia: [aceleración del emulador Android](https://developer.android.com/studio/run/emulator-acceleration).

## Comandos principales

Desde `flutter_app`, con Flutter/SDK/JDK configurados:

```powershell
flutter build apk --debug --dart-define=API_BASE_URL=http://127.0.0.1:8000/api
Copy-Item build\app\outputs\flutter-apk\app-debug.apk ..\entrega_android\Lumina-Optica-P1-P2.apk
```

Desde la raíz `optica_22121280`:

```powershell
.\.venv\Scripts\python.exe scripts\android_demo.py --iniciar-emulador
```

Salida final del acceso:

```text
Performing Streamed Install
Success
Starting: Intent { cmp=mx.edu.itm.optica_app/.MainActivity }
Lúmina P1 + P2 instalada y abierta en emulator-5554
Django ya estaba activo. Conserva abierto el acceso que lo inició.
```

El script comprueba el SDK, la aceleración y los AVD, espera el arranque completo, conecta el puerto, instala y abre la app. Inicia Django si todavía no está activo. Para repetirlo mediante doble clic se añadió **`ABRIR_ANDROID.cmd`**. Las instrucciones están en [entrega_android/LEEME.md](../entrega_android/LEEME.md).

## Qué se observó en ejecución nativa

La interfaz Android mostró Lúmina y sus cuatro pestañas. Se guardó una captura del formulario y su árbol UI nativo en `android-2026-11-17/01_perfil.png` y `.xml`. Durante la revisión interactiva se observaron peticiones correctas al catálogo/detalle y al recomendador, además del registro de una orden.

La segunda captura y árbol UI, `02_estado_actual.png` y `.xml`, muestran **Solicitud registrada**, el ranking y el resultado premium al 100 % que cumplía las reglas para el perfil introducido durante esa interacción. La orden `2740f288-0360-4109-a3b8-f83156729a8c` quedó almacenada con precio confirmado $2,400.00. `ordenes_observadas.json` conserva la consulta de las órdenes recientes, incluida la anterior de la revisión web; no se borraron registros.

Estas capturas corresponden al **APK en Android**, no a un viewport móvil del navegador. El acceso automatizó arranque, instalación y conexión; las capturas posteriores observaron la interacción sin modificar los controles que el usuario estaba usando. No se presentan como una repetición automatizada completa de todos los escenarios nativos del chat. Esos contratos y flujos se probaron en las pruebas Flutter/backend y en el recorrido web previo; ambos clientes se construyen desde el mismo código Flutter.

## Conexión y uso posterior

### Ampliación: teléfono físico realme C53

Posteriormente se conectó y autorizó por USB un **realme C53 (RMX3760), Android 15 / API 35**. Se instaló el mismo APK con resultado `Success` y se abrió `mx.edu.itm.optica_app/.MainActivity`; `dumpsys activity` confirmó que era la actividad en primer plano y el proceso de Lúmina estaba activo.

El catálogo respondió HTTP 200 desde el backend compartido. Se restableció la redirección USB después de instalar y se comprobó `UsbFfs tcp:8000 tcp:8000`. El acceso `scripts/android_demo.py` ahora configura esa redirección después de la instalación para evitar perderla en teléfonos que reinician la conexión USB durante ese paso. El dispositivo se eligió explícitamente al ejecutar el acceso; no se guarda aquí su identificador USB.

Para volver a conectar el teléfono se utiliza `INSTALAR_ANDROID.cmd`, con depuración USB autorizada y el cable conectado. La app física usa los mismos modelos, catálogo y órdenes del backend de la PC. Esta comprobación añade instalación, apertura y carga de catálogo en hardware real; no se presenta como una repetición de todos los escenarios automatizados de negocio en el teléfono.

El APK incluye las pantallas de P1 y P2. El recomendador, el clasificador del asistente, el corpus y SQLite continúan ejecutándose en Django. El puerto 8000 de Android se redirige a la PC; por eso un folio registrado desde la app pertenece al mismo sistema que consulta la web.

Se dejó el emulador con la aplicación abierta y el backend existente activo. Para volver a abrirla utiliza `ABRIR_ANDROID.cmd`; conserva el emulador y la terminal de Django abiertos durante la revisión. El APK de depuración sirve para instalar y presentar localmente; una publicación comercial requeriría su configuración de distribución correspondiente.
