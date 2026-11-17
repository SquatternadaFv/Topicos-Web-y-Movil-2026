# Matriz de cumplimiento del Proyecto 1

Estudiante: Eduardo Osvaldo Rodríguez Gutiérrez · 22121280  
Fuente: [apuntes del curso, Proyecto 1](https://ealcaraz85.github.io/topicoswebmobil/#orgd85c21d), consulta original del 10/11/2026, contrastada de nuevo el 11/11/2026. Entrega prevista: 12/11/2026.

| Solicitud del apartado | Implementación propia | Evidencia / cómo comprobar |
|---|---|---|
| Dominio asignado | Óptica, paquetes y tratamientos | README, catálogo Esencial/Claridad/Transición/Integral |
| Adaptar features y clases | Cinco entradas y cuatro clases propias | ml/datos/perfiles_optica.csv, ml/entrenar.py |
| Modelo .joblib + reglas en Django | Pipeline entrenado, adaptador, tres políticas | backend/optica/modelo/, recomendador.py, reglas.py |
| Decisión, confianza y corrección | Original/final, dos confianzas y `corregido` | 02_recomendacion.json; pantalla de resultado |
| Ranking útil | Probabilidad, elegibilidad y motivos por alternativa | 04_reglas.png |
| Modelos y db.sqlite3 | Paquete y Orden; migración y base demo | backend/optica/models.py, migrations/, backend/db.sqlite3 |
| Datos coherentes | Cuatro paquetes ópticos y 1,200 perfiles sintéticos | sembrar_demo.py y generador con semilla fija |
| JSON listado y detalle | GET catalogo/ y catalogo/<codigo>/ | Prueba backend y pantalla detalle |
| POST de recomendación | POST recomendaciones/ | Adapter real con predict_proba; no consulta simulada |
| Registro con resultado del servidor y folio | POST ordenes/, recálculo y UUID | 03_orden_registrada.json, 05_folio.png |
| GET por folio adicional | GET ordenes/<uuid>/ | 04_consulta_folio.json, 06_consulta.png |
| Flutter lista, detalle y búsqueda | CatalogScreen y DetailScreen | 00_inicio.png, 01_detalle.png, 07_busqueda.png |
| Formulario propio del modelo | ProfileScreen | 02_formulario.png |
| Confirmación y folio | Diálogo y OrderDetailScreen | 05_folio.png |
| Carga, errores y URL configurable | ApiClient, FutureBuilder y estado local | Pruebas Dart/widgets; README; 09_sin_opciones.png |
| Backend y cliente | Código fuente completo | backend/ y flutter_app/ |
| Instalación y ejecución | Windows, Linux, web y URL de Android | README y GUIA_CONSTRUCCION.md |
| Regenerar .joblib | Generador + entrenador + versiones fijadas | ml/generar_datos.py, entrenar.py, backend/requirements.txt |
| Capturas de todo el recorrido | Widgets Flutter renderizados por flutter_tester con HTTP real | evidencias/*.png |
| Caso corregido explicado | Presupuesto $700: Claridad → Esencial | Guía, informe y respuestas HTTP guardadas |
| Párrafo de adaptación frente a clase | Comparación explícita con medios de transporte | README, primera sección |
| Análisis web y móvil de 1-2 páginas | Dos páginas con patrón, archivo y problema | Analisis_Patrones_22121280.pdf |
| Historial claro | Commits locales y exportación legible | Repositorio local y docs/HISTORIAL.txt |

Las evidencias originales documentan widgets reales renderizados por flutter_tester y conectados a Django por HTTP. La revisión del 11/11 añade ocho capturas de Chrome ejecutando Flutter web compilado contra la API y el modelo reales: `10_chrome_inicio.png` a `17_chrome_movil.png`. Consulta `evidencias/VALIDACION_LOCAL_2026-11-11.md` para los resultados actuales de Windows; `VALIDACION.md` conserva la validación anterior. La prueba de Android en emulador y la publicación remota no se declaran realizadas.
