# Matriz conjunta de requisitos y evidencias: P1 y P2

Revisión: 17/11/2026. Fuente: [apuntes del profesor](https://ealcaraz85.github.io/topicoswebmobil/), [P1](https://ealcaraz85.github.io/topicoswebmobil/#orgd85c21d) y [P2](https://ealcaraz85.github.io/topicoswebmobil/#orga05f98b). Dominio asignado: óptica, control 22121280. Esta matriz distingue cumplimiento implementado de una calificación o presentación que corresponde al profesor.

## Proyecto 1

| Requisito publicado | Implementación / documento | Verificación |
|---|---|---|
| Entradas, datos y decisión adaptados al tema | `ml/generar_datos.py`, `ml/datos/perfiles_optica.csv`; cinco entradas, cuatro paquetes | Generador reproducible de 1,200 perfiles; guía secciones 4–6 |
| `.joblib` integrado al flujo del monolito | `recomendador.py`, `services.py`, `modelo/modelo_optica.joblib` | Tests de recomendación con el modelo real y recorrido de navegador |
| Clase, confianza y corrección por reglas | `services.py`, `reglas.py`, `result_screen.dart` | Caso $700: Claridad → Esencial; captura `12_chrome_recomendacion.png` |
| Ranking de alternativas útil | Probabilidad, precio, elegibilidad y motivos en JSON/UI | `13_chrome_reglas.png`; suma de probabilidades comprobada en tests |
| SQLite con catálogo y órdenes | `models.py`, migraciones, `sembrar_demo` | Migraciones aplicadas; tests sobre base temporal |
| Datos de prueba coherentes | Cuatro paquetes y perfiles sintéticos | Semilla y CSV incluidos; procedencia explícita |
| JSON de lista y detalle | GET `/api/catalogo/` y `/api/catalogo/{codigo}/` | Tests de búsqueda, detalle y 404 |
| POST características → modelo + reglas | POST `/api/recomendaciones/` | Tests con y sin corrección y sin alternativas |
| Registro con resultado del servidor y folio | POST `/api/ordenes/`; recalcula y conserva snapshot | Tests de 201/200, idempotencia, 409 y entradas manipuladas |
| GET adicional por folio | GET `/api/ordenes/{UUID}/` | Snapshot conserva precio anterior tras cambiar catálogo |
| Flutter lista, detalle, búsqueda | `catalog_screen.dart`, `ApiClient` | Catálogo real en navegador; tests del contrato de búsqueda |
| Formulario de características | `profile_screen.dart`, validación local/servidor | `11_chrome_formulario.png`; test Flutter bloquea presupuesto inválido |
| Confirmación y folio | `result_screen.dart`, `order_screen.dart` | `14_chrome_folio.png`, `15_chrome_consulta.png` |
| Carga, errores, URL configurable | `api_client.dart`, estados de pantallas, `--dart-define` | Pruebas de errores HTTP/red y carga; 422 real en navegador |
| Modelo y reglas solo servidor | Ningún `.joblib` en Flutter; API JSON | Estructura de fuentes y análisis de patrones |
| Instalación, ejecución y regeneración | `README.md`, guía de defensa sección 14 | Comandos reproducibles; `INICIAR_DEMO.cmd` |
| Capturas entradas → resultado → reglas → orden → folio | `evidencias/2026-11-17/10` a `17` | Recorrido sobre Flutter compilado y Django real |
| Caso corregido y diferencia con ejemplo de clase | Guía secciones 1 y 6 | $700, 85 % original y 0 % final explicados sin inflar probabilidades |
| Análisis de patrones backend y Flutter | `ANALISIS_PATRONES_P1_P2.md` y PDF de dos páginas | Archivo, inconveniente y justificación de cada patrón |

## Proyecto 2

| Requisito publicado | Implementación / documento | Verificación |
|---|---|---|
| Extender P1 con el mismo tema | Cuarta pestaña en la misma app y servicios compartidos | Catálogo, perfil y folio siguen disponibles |
| Dataset propio de preguntas/intenciones | `ml/generar_intenciones.py`, `ml/datos/intenciones_optica.csv` | 160 frases, ocho intenciones, origen declarado |
| Si hay recuperación, corpus propio alineado | `ml/corpus_optica.json`, `ml/indexar_corpus.py` | Seis fuentes públicas; no se usa corpus defectuoso del ejercicio |
| Entrenar fuera de HTTP | `ml/entrenar_asistente.py` | Separación estratificada 128/32; no hay `fit` en endpoint |
| Guardar artefacto | `modelo/modelo_asistente.joblib` | Pipeline, versión, umbral y sklearn incluidos; regeneración documentada |
| Métrica sencilla de prueba | `ml/metricas_asistente.json`, `ml/prueba_asistente.csv` | 75 % = 24/32, errores y métricas por clase visibles |
| POST con mensaje de comprador | POST `/api/asistente/` | Tests de métodos, JSON, longitud, campos y folios inválidos |
| Cargar modelo y obtener intención | `clasificador_asistente.py` | Pruebas con artefacto real; caché y umbral explícitos |
| Consultar productos / folio / recomendador | `asistente.py`, repositorios y `OpticaService` | Pruebas de precio actual, orden real, ausencia y delegación |
| Respuesta JSON con intención y respuesta | `views.asistente`, `AsistenteService.responder` | `intencion`, `respuesta`, confianza, versión, fuentes, acción y datos |
| Adapter del formato del modelo | `ClasificadorIntenciones` | Traduce salida sklearn y política de aclaración al dominio |
| Chat Flutter, envío y respuestas | `chat_screen.dart`, `ApiClient.conversar` | Tests de carga, cuerpo JSON, referencia, fuente, acción y error de red |
| P1 sigue disponible como un solo producto | `main.dart`, cuatro destinos con IndexedStack | Chat abre el formulario; navegación probada en navegador |
| Capturas saludo, folio, dominio y fuera de dominio | `20_chat_saludo.png`, `22_chat_folio_real.png`, `24_chat_dominio_fuente.png`, `25_chat_fuera_dominio.png` | `recorrido_chrome.json` enlaza respuestas con el mismo folio creado |
| Explicación del resultado y no inventar decisión | Snapshot en `asistente.py`; derivación al recomendador | Test impide llamar al predictor al explicar; capturas 23 y 26 |
| Patrones actualizados de cliente y servidor | `ANALISIS_PATRONES_P1_P2.md` y PDF | Adapter, separación, cambios de ambos lados y responsabilidades |

## Lectura de evidencias y límites

Todas las capturas de esta revisión están bajo `evidencias/2026-11-17/`. El registro `evidencias/VALIDACION_P1_P2_2026-11-17.md` contiene comandos, resultados, folio del recorrido y límites de la validación. Los resultados anteriores del 11/11 son antecedentes; no se sustituyeron por capturas con la misma fecha.

La validación inicial cubrió Flutter web compilado, Django, SQLite y los modelos locales. Después se generó el APK Android debug de P1/P2, con firma verificada y acceso `ABRIR_ANDROID.cmd`; la comprobación específica se documenta en `evidencias/VALIDACION_ANDROID_2026-11-17.md`. Los apartados P1/P2 no exigen gateway, microservicios ni demostración simultánea de P3. Tampoco se incorporan informes de Cinerex, Hotel Luna, PasoFit, Sabores o TallerPro, que no pertenecen a la consigna de estos proyectos.

La guía `DEFENSA_PROYECTOS_1_Y_2.md` diferencia los requisitos del profesor de supuestos comerciales del prototipo, documenta las limitaciones de los datasets y prepara 50 preguntas de exposición.
