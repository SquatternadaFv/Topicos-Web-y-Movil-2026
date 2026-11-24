# App Android: Lúmina Óptica, proyectos 1 y 2

La misma aplicación Flutter incorpora catálogo, recomendador, órdenes/folio y asistente. El APK de demostración se llama **`Lumina-Optica-P1-P2.apk`**. Su firma y tipo son de depuración para revisión académica.

**Rediseño local del 24/11/2026:** el APK de esta carpeta incorpora la nueva paleta marfil/ciruela/lavanda, el encabezado sin P1/P2 y fotografías reales de referencia incluidas para uso sin internet. Usa este archivo con `ABRIR_ANDROID.cmd` o `INSTALAR_ANDROID.cmd`. `apk_info.json` y `SHA256SUMS.txt` identifican esta compilación; la descarga de GitHub indicada abajo es una versión anterior del 17/11 y reemplazar el archivo local con ella restaura el diseño anterior.

**[Descargar el APK desde la release del repositorio](https://github.com/SquatternadaFv/Topicos-Web-y-Movil-2026/releases/download/lumina-p1-p2-v1.0.0-2026-11-17/Lumina-Optica-P1-P2.apk).** Colócalo en esta carpeta `entrega_android/` antes de ejecutar los accesos de instalación. Se distribuye como archivo adjunto de la release; el repositorio conserva el código, el manifiesto y los comandos para reconstruirlo.

## Abrir en el emulador de esta computadora

Ejecuta **`ABRIR_ANDROID.cmd`**, en la carpeta superior `optica_22121280`. El acceso comprueba la aceleración, abre el AVD instalado, espera el arranque de Android, inicia Django si falta, instala el APK y abre Lúmina. Conserva abierto el emulador y la terminal que esté ejecutando el backend.

Si tienes varios AVD, indica uno desde PowerShell:

```powershell
.\.venv\Scripts\python.exe scripts\android_demo.py --iniciar-emulador --emulador Medium_Phone_API_37.0
```

La PC necesita virtualización habilitada y un controlador de aceleración operativo. El script diagnostica esa condición, pero no cambia BIOS ni instala controladores como administrador por sí solo.

## Alternativa: instalar en un celular Android

1. Conecta un celular Android por USB. Activa las opciones de desarrollador y la depuración USB; acepta en el teléfono la huella de la computadora. También sirve un emulador Android ya iniciado.
2. Ejecuta **`INSTALAR_ANDROID.cmd`**, en la carpeta superior `optica_22121280`.
3. El acceso comprueba el dispositivo, inicia Django si hace falta, instala el APK, configura `adb reverse tcp:8000 tcp:8000` y abre Lúmina.
4. Mantén el USB conectado y el backend activo. Si el acceso inició Django, conserva su terminal abierta; Ctrl+C lo detiene. Si ya estaba activo por la demo web, conserva esa otra terminal.

La app usa `http://127.0.0.1:8000/api` **dentro de Android**. El túnel ADB dirige ese puerto a la computadora. Así no hay que exponer Django a la red local ni modificar el firewall para la demostración por USB. El sitio web y la app consultan la misma base SQLite: un folio creado en cualquiera puede recuperarse en la otra.

Instalar el APK copiándolo al teléfono no configura el túnel por sí solo. Sin Django y conexión al servidor no habrá catálogo, predicción ni asistente: los modelos y las reglas permanecen en backend según la consigna.

Si hay varios Android conectados, abre PowerShell desde `optica_22121280` y ejecuta:

```powershell
.\.venv\Scripts\python.exe scripts\android_demo.py --serial IDENTIFICADOR
```

El identificador aparece en `adb devices`. Un estado `unauthorized` requiere aceptar el permiso en el teléfono; `offline` indica que el dispositivo no terminó de conectar/arrancar. El script no instala controladores de hipervisor ni cambia BIOS.

## Recompilar el APK

Desde `flutter_app`, con Flutter, JDK y Android SDK instalados:

```powershell
flutter pub get
flutter build apk --debug --dart-define=API_BASE_URL=http://127.0.0.1:8000/api
Copy-Item build\app\outputs\flutter-apk\app-debug.apk ..\entrega_android\Lumina-Optica-P1-P2.apk
```

En esta computadora Flutter está en `C:\dev\flutter\bin\flutter.bat`. El APK debug permite HTTP local en el manifest de depuración y contiene el código de ambos proyectos. No distribuye `.joblib`, SQLite ni el servidor Python. Para publicar una app real se requiere firma de distribución y API HTTPS; esa publicación no forma parte de esta demo.

## Recorrido de revisión

En Catálogo, buscar y abrir un paquete. En Mi recomendación, usar pantalla 8, exterior 1, presupuesto 700, oficina y sin fotocromático; revisar la corrección Claridad → Esencial. Confirmar y copiar el folio. Consultarlo en la pestaña correspondiente y en Asistente con «quiero rastrear mi orden» y «explica mi orden». Probar también «hola», «qué paquetes ofrecen», «cuál es el horario de atención» y una pregunta de fútbol.

La guía detallada está en `../docs/DEFENSA_PROYECTOS_1_Y_2.pdf`. El registro específico de esta compilación/ejecución está en `../evidencias/VALIDACION_ANDROID_2026-11-17.md`, que distingue generar el APK de comprobarlo en un dispositivo.
