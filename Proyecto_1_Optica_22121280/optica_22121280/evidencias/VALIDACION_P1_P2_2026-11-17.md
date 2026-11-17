# Validación conjunta de proyectos 1 y 2

Fecha: **17/11/2026**. Proyecto: Lúmina Óptica, control 22121280.

> Este registro corresponde a la primera validación web. La ampliación posterior incluye APK Android compilado y su comprobación específica en [VALIDACION_ANDROID_2026-11-17.md](VALIDACION_ANDROID_2026-11-17.md).

## Resultado y alcance

Se revisó P1 y se implementó la extensión P2 contra los apartados publicados de [Proyecto 1](https://ealcaraz85.github.io/topicoswebmobil/#orgd85c21d) y [Proyecto 2](https://ealcaraz85.github.io/topicoswebmobil/#orga05f98b). P1 ya contaba con recomendador, reglas, catálogo, registro y folio; faltaba la implementación de P2 que la guía anterior describía como propuesta.

P2 ahora incluye dataset propio, entrenamiento fuera de HTTP, Pipeline guardado, métrica, endpoint, Adapter, consultas a datos reales, explicación histórica, corpus público extractivo y chat dentro de la misma aplicación. Se actualizaron documentación, patrones y matriz de requisitos.

El resultado verificado es **Flutter web compilado + Django + SQLite + modelos locales**. La revisión no incluye ejecución Android/APK ni P3. Los viewports de 390 × 844 verifican presentación adaptable en navegador. La conformidad con la consigna publicada no equivale a una calificación o presentación del estudiante.

## Entorno ejecutado

| Componente | Entorno utilizado |
|---|---|
| Backend y modelos | `.venv/Scripts/python.exe` dentro de `optica_22121280`; Python 3.12.16 |
| Dependencias de inferencia | scikit-learn 1.8.0, Django 5.2.19, pandas 2.2.3; versiones fijadas en backend |
| Cliente | Flutter 3.47.9 / Dart 3.13.7, SDK `C:/dev/flutter` |
| Navegador automatizado | Chromium headless instalado en `ms-playwright/chromium_headless_shell-1234` |
| Control del navegador | Python del entorno compartido `.venv-actividades` con Playwright; las predicciones se ejecutan en el entorno propio del backend |
| API y sitio | `http://127.0.0.1:8000/api` y `http://127.0.0.1:5173` |

## Comprobaciones ejecutadas

| Comprobación | Resultado |
|---|---|
| `python backend/manage.py migrate --noinput` | Sin migraciones pendientes |
| `python backend/manage.py sembrar_demo` | Cuatro paquetes listos; no se borraron órdenes |
| `python backend/manage.py test optica` | **18 pruebas aprobadas**, sin problemas de system check |
| `flutter analyze` | **Sin incidencias** |
| `flutter test` | **7 pruebas aprobadas** |
| `flutter build web --release --no-wasm-dry-run --dart-define=API_BASE_URL=http://127.0.0.1:8000/api` | **Build web generada** |
| Artefactos guardados frente a sus métricas | Accuracy recalculada coincide: árbol 0.9375 y asistente 0.75 |
| `python scripts/exportar_guias.py` | Guía: 16 páginas; patrones: 2; matriz: 2 |
| Recorrido en navegador contra API real | **Correcto, 16 PNG, cero errores JavaScript** |
| Comprobación HTTP de sitio, salud y catálogo | Los tres respondieron **200** |

Los logs están en `django_test_2026-11-17.log`, `flutter_analyze_2026-11-17.log`, `flutter_test_2026-11-17.log` y `flutter_build_2026-11-17.log`. El compilador emitió una advertencia sobre la familia opcional CupertinoIcons; produjo la build correctamente. Los iconos Material, las vistas y el chat fueron revisados en las capturas.

### Qué cubren las pruebas

Las 10 pruebas originales de backend comprueban catálogo/detalle/búsqueda, inferencia real, corrección de presupuesto, resultado sin corrección, snapshot, precio histórico, idempotencia y 409, validación estricta, ausencia de opciones, disponibilidad, métodos/CORS y folios inexistentes.

Las 8 nuevas comprueban saludo y fuera de dominio con el clasificador real; precios actuales y disponibilidad del catálogo; seguimiento y explicación del mismo snapshot sin nueva inferencia; folio ausente/desconocido/inválido/ambiguo; derivación al formulario y delegación al servicio P1 sin registrar; recuperación con fuente; falta de fuente/aclaración y validación del contrato.

Las 5 pruebas Flutter originales verifican contratos HTTP, errores, flujo perfil → recomendación → confirmación → folio y bloqueo local de presupuesto inválido. Las 2 nuevas verifican mensaje/folio, estado de espera, desactivación de envío, respuesta/fuente, acción de abrir perfil y conservación del texto al fallar la red. Los tests aislados utilizan dobles HTTP; el recorrido siguiente usa API, base y modelos reales.

## Modelos comprobados

| Artefacto | Datos | Partición | Métrica comprobada |
|---|---|---|---|
| `modelo_optica.joblib` | 1,200 perfiles sintéticos | 960 entrenamiento / 240 prueba | 225/240 = **93.75 %** |
| `modelo_asistente.joblib` | 160 frases, ocho clases de 20 | 128 entrenamiento / 32 prueba | 24/32 = **75 %**, antes de abstención |
| `indice_corpus.joblib` | Seis documentos públicos activos | Índice, no clasificador supervisado | Similitud léxica para recuperación; no se presenta como accuracy |

Versiones: `optica-v1-f68e75c47161` y `asistente-v1-cb544a468f18`. El manifiesto [modelos_2026-11-17.json](modelos_2026-11-17.json) registra SHA-256 de datos, clases y métricas recalculadas con los artefactos guardados. El test del asistente es pequeño y presenta errores; la guía documenta especialmente la limitación para detectar preguntas fuera de dominio.

## Recorrido de integración con evidencia real

Comando usado desde la raíz de la aplicación, con la demo activa:

```powershell
C:\TopicosMovilWeb\.venv-actividades\Scripts\python.exe scripts\capturar_navegador.py --chrome C:\Users\Eduardo\AppData\Local\ms-playwright\chromium_headless_shell-1234\chrome-headless-shell-win64\chrome-headless-shell.exe --salida evidencias\2026-11-17 --con-asistente
```

Resultado final:

```json
{
  "estado": "correcto",
  "folio": "b9befbeb-3bc7-4165-97e5-38dd80a0d8f1",
  "capturas": 16,
  "errores_javascript": []
}
```

Las capturas y el JSON completo están en [2026-11-17](2026-11-17/):

| Captura | Evidencia |
|---|---|
| `10_chrome_inicio.png` | Catálogo en Flutter compilado |
| `11_chrome_formulario.png` | Cinco entradas del perfil |
| `12_chrome_recomendacion.png` | Claridad original, Esencial final y corrección |
| `13_chrome_reglas.png` | Ranking y restricciones |
| `14_chrome_folio.png` | Registro real con folio |
| `15_chrome_consulta.png` | Consulta del mismo snapshot |
| `16_chrome_sin_opciones.png` | Presupuesto $500, respuesta HTTP 422 |
| `17_chrome_movil.png` | Catálogo en viewport móvil |
| `20_chat_saludo.png` | Intención saludo |
| `21_chat_catalogo.png` | Precios actuales desde SQLite |
| `22_chat_folio_real.png` | Estado del mismo folio creado en P1 |
| `23_chat_explicacion.png` | Snapshot, confianza y regla histórica |
| `24_chat_dominio_fuente.png` | Pregunta de horario y documento público citado |
| `25_chat_fuera_dominio.png` | Pregunta de fútbol fuera de alcance |
| `26_chat_abrir_recomendador.png` | Derivación al formulario en vez de inventar paquete |
| `27_chat_movil.png` | Chat adaptable en viewport móvil |

`recorrido_chrome.json` conserva el perfil, recomendación y orden reales, la igualdad de la consulta histórica y los siete intercambios del chat. El script verifica que el cuerpo HTTP contiene el mensaje escrito, que el folio y precio coinciden y que el botón del asistente abre el formulario de P1.

Para la automatización se sincronizó el foco de los campos accesibles de Flutter antes de escribir y se utilizaron nombres de grupos accesibles para verificar las burbujas. Los intentos de ajustar el recorrido generaron solicitudes demo adicionales; no se borraron las órdenes que ya existían. Las 16 capturas y el JSON indicados corresponden al recorrido final completo.

## Documentación entregada y ejecución para revisión

- [Guía detallada P1/P2](../docs/DEFENSA_PROYECTOS_1_Y_2.md) y su PDF de 16 páginas: arquitectura, esquema, datasets, algoritmos, reglas, API, Flutter, corpus, entrenamiento/inferencia, instalación, demostración y 50 preguntas de defensa.
- [Análisis actualizado de patrones](../docs/ANALISIS_PATRONES_P1_P2.md) y PDF de dos páginas.
- [Matriz de requisitos de los apuntes](../docs/MATRIZ_PROYECTOS_1_Y_2.md) y PDF.
- README e índices actualizados; se conservan los informes y guías originales de P1.

La demo se dejó iniciada en `http://127.0.0.1:5173` para revisión. Para iniciarla de nuevo se usa `INICIAR_DEMO.cmd` desde la carpeta de la aplicación, con el entorno y la build preparados. Ctrl+C en la terminal de la demo detiene los procesos que inició. No se incorporaron microservicios/gateway de P3.
