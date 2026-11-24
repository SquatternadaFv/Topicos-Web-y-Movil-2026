# Actividades y proyectos de Tópicos Web y Móvil

Eduardo Osvaldo Rodríguez Gutiérrez · 22121280. Actividades de los apuntes revisadas al 13/11/2026 y **proyectos 1 y 2 de Lúmina Óptica actualizados el 24/11/2026**, con rediseño web/Android, fotos reales de referencia y configuración móvil/Git revisada. Proyecto 3 y la auditoría con IA local quedan fuera de este avance.

**Lúmina P1 + P2:** [empieza aquí](Proyecto_1_Optica_22121280/EMPIEZA_AQUI.md), [guía de defensa de 16 páginas](Proyecto_1_Optica_22121280/optica_22121280/docs/DEFENSA_PROYECTOS_1_Y_2.pdf), [instrucciones Android](Proyecto_1_Optica_22121280/optica_22121280/entrega_android/LEEME.md) y [descarga del APK 1.1.0+2](https://github.com/SquatternadaFv/Topicos-Web-y-Movil-2026/releases/download/lumina-p1-p2-v1.1.0-2026-11-24/Lumina-Optica-P1-P2.apk).

El trabajo anterior se conserva. Las entregas de implementación individual y examen teórico de microservicios que ya estaban en GitHub se recuperaron también en esta copia local. Las ampliaciones escritas se elaboraron con asistencia y requieren revisión personal para poder defenderlas; las métricas, capturas y pruebas indicadas como ejecutadas se obtuvieron realmente aquí.

## Índice de entregas

| Actividad | Archivo/carpeta |
|---|---|
| Estado y límites de verificación | [ESTADO_ACTIVIDADES.md](ESTADO_ACTIVIDADES.md) |
| Actividad de clase, pasos 1–3 | [actividad_en_clase.md](actividades/patrones/actividad_en_clase.md) |
| Misiones 1–8, caso actual de entregas | [misiones_1_a_8.md](actividades/patrones/misiones_1_a_8.md) |
| Acertijos, ejercicios y autoevaluación | [ejercicios_y_autoevaluacion.md](actividades/patrones/ejercicios_y_autoevaluacion.md) |
| Preguntas de discusión web/móvil/Flutter | [discusion_web_movil.md](actividades/discusion_web_movil.md) |
| Diagnóstico: respuestas faltantes y precisiones | [diagnostico_complemento.md](actividades/diagnostico_complemento.md) |
| Veinte lenguajes: paradigmas y problemas | [lenguajes_paradigmas_complemento.md](actividades/lenguajes_paradigmas_complemento.md) |
| Cinco días y contrato HTML/JSON | [dia5/dia5/README.md](dia5/dia5/README.md); [día 1](dia1.md), [día 2](dia2/dia2.md), [día 3](dia3/dia3.md), [día 4](dia4/dia4.md) |
| Retos Django | [EXTRA.md](EXTRA.md) y [complemento](actividades/retos_django_complemento.md) |
| Árbol, bosque y red entrenados | [dataset-medios](proyectos/dataset-medios/README.md) |
| Ocho actividades de análisis | [ANALISIS.md](actividades/analisis-dataset/ANALISIS.md), [predicciones](actividades/analisis-dataset/PREDICCIONES.md) |
| Seis ejercicios del modelo | [EJERCICIOS.md](actividades/ejercicios-modelo/EJERCICIOS.md) |
| Seis datasets envios-data | [análisis](actividades/analisis-envios-data/analisis_envios-data.md) |
| Comparación árbol/bosque/red | [comparación](actividades/comparacion-modelos/comparacion_modelos.md) |
| Evaluación individual A1–F1 | [implementación](actividades/implementacion/22121280_rodriguez.md) |
| Monolito con API frente a microservicios | [arquitectura](actividades/arquitectura/22121280_rodriguez.md) |
| Microservicios: código y ejecución | [README](microservicios-entregas/README.md), [informe individual](actividades/microservicios-docker/22121280_rodriguez.md) |
| Examen teórico de microservicios | [Actividad Microservicios](Actividad%20Microservicios) |
| Widgets, HTTP y empaquetado Flutter | [README_ACTIVIDAD.md](practicas_flutter/README_ACTIVIDAD.md) |
| Corpus RAG del dominio Óptica, A1–A6 | [RAG](actividades/rag_corpus/22121280_rodriguez.md) |
| Asistente entrenado del tutorial de entregas | [asistente-tutorial](actividades/asistente-tutorial/README.md) |

## Ejecutar y reproducir

En esta computadora ya está preparado el entorno `C:\TopicosMovilWeb\.venv-actividades`. Desde esta carpeta, en PowerShell:

```powershell
$pythonLab = '..\.venv-actividades\Scripts\python.exe'
& $pythonLab scripts/verificar.py
& $pythonLab ejecutar_actividades.py
& $pythonLab Actividad_Extra_Django/retos_django/manage.py migrate
& $pythonLab Actividad_Extra_Django/retos_django/manage.py runserver
```

En otra computadora se requiere Python 3.12: crear un entorno e instalar `requirements.txt`, que fija las versiones de esta ejecución. Entrenar no ocurre dentro de una petición HTTP. Las predicciones previas no se sobrescriben al regenerar resultados.

Abrir `/entregas/modelo/` para el árbol real; `/entregas/cotizador/` para los retos; `/pedidos/nuevo` para el flujo de pedido persistido. El servidor del laboratorio se usa localmente con datos de prueba. Los endpoints JSON para Flutter no son una API de producción autenticada.

Para Flutter: seguir su README y usar `C:\dev\flutter\bin\flutter.bat` si flutter no está en PATH. Para Docker: seguir cada README cuando haya un motor instalado; un archivo Compose no demuestra que se haya ejecutado.

## Evidencia

La limpieza conserva fuentes, datos, modelos y evidencias de las actividades. Los archivos compilados de Flutter, cachés, logs de servidor y configuración local del IDE no se versionan. Para repetir capturas de Flutter es necesario regenerar primero el build web, como indica su README.

[Pruebas](evidencias/verificacion/pruebas.json), [HTTP y entorno](evidencias/verificacion/http.json), [borradores entre procesos](evidencias/verificacion/borrador_local.txt), [disponibilidad Docker](evidencias/verificacion/docker.json), [métricas de los modelos](proyectos/dataset-medios/modelos/metadata.json).

Las capturas `evidencias/verificacion/01-*` a `06-*` corresponden a esta ejecución. Quedan identificadas por separado las pruebas locales y las que necesitan Docker u otras computadoras.
