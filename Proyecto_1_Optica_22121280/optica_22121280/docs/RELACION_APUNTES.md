# Cómo se conecta el Proyecto 1 con los apuntes

> Antecedente de P1, fechado el 11/11. P2 ya está implementado desde la revisión del 17/11/2026; la trazabilidad vigente de ambos proyectos está en [MATRIZ_PROYECTOS_1_Y_2.md](MATRIZ_PROYECTOS_1_Y_2.md) y la explicación completa en [DEFENSA_PROYECTOS_1_Y_2.md](DEFENSA_PROYECTOS_1_Y_2.md).

Eduardo Osvaldo Rodríguez Gutiérrez · 22121280 · Revisión: 11/11/2026 · Entrega prevista: 12/11/2026.

Se consultó la página original completa y su apartado de [Proyecto 1](https://ealcaraz85.github.io/topicoswebmobil/#orgd85c21d). La fila 23 asigna al número 22121280 el dominio óptica y la decisión «paquete de lentes / tratamiento sugerido». Los documentos proporcionados son referencias del proyecto: las exigencias de entrega se contrastan con el curso. La elección de precios, marca, variables y paquetes es una decisión de esta implementación.

## Recorrido recomendado para estudiarlo

1. Lee el apartado de Proyecto 1 y [MATRIZ_ENTREGA.md](MATRIZ_ENTREGA.md). Localiza un archivo o evidencia por cada requisito.
2. Ejecuta `INICIAR_DEMO.cmd` y sigue la demostración del README. Primero entiende qué hace el sistema desde la perspectiva del usuario.
3. Abre [GUIA_CONSTRUCCION.md](GUIA_CONSTRUCCION.md), secciones 3 a 9, y sigue una petición desde Flutter hasta SQLite.
4. Lee `ml/generar_datos.py`, `ml/entrenar.py` y `ml/metricas.json`. Distingue entrenamiento, inferencia y reglas.
5. Lee el PDF de patrones junto con los archivos que nombra. Cada patrón debe poder señalarse en código.
6. Repite la demostración sin leer el guion: presupuesto 3000, presupuesto 700 y presupuesto 500. Explica por qué cambia el resultado.

## Cada bloque del curso tiene una relación concreta

| Apartado original | Dónde aparece aquí | Qué puedes explicar |
|---|---|---|
| [Antes de los patrones: reconocer estructuras](https://ealcaraz85.github.io/topicoswebmobil/#orgf1d69cb) | `services.py`, `reglas.py`, `recomendador.py` | Primero se identifica lo que varía: políticas, modelo y almacenamiento. La separación responde a esas variaciones. |
| [Qué es un patrón](https://ealcaraz85.github.io/topicoswebmobil/#orgd7ffc3c) y [catálogo GoF](https://ealcaraz85.github.io/topicoswebmobil/#org65fcebc) | Adaptador del árbol y políticas con interfaz común | Adapter traduce sklearn al dominio; Strategy orienta la composición de políticas. No se implementa cada patrón del catálogo por obligación. |
| [Empresa de entregas](https://ealcaraz85.github.io/topicoswebmobil/#orgf3ef74b) y [sus problemas](https://ealcaraz85.github.io/topicoswebmobil/#orgb418010) | `OpticaService.recomendar` y `registrar` | El mismo recorrido de recomendación y pedido se adapta: las etiquetas dejan de ser moto/dron y se convierten en paquetes ópticos. |
| [De dónde salen los objetos](https://ealcaraz85.github.io/topicoswebmobil/#org968cf54) | Constructor de `OpticaService`; `ApiClient(client: ...)` | Se pueden inyectar colaboradores para comprobarlos. No se necesita una fábrica de familias de productos para cuatro registros de catálogo. |
| [Patrones web y móviles](https://ealcaraz85.github.io/topicoswebmobil/#orgd761098) | Repositorios, rutas, servicio y separación Flutter | Repository concentra ORM; Front Controller dirige peticiones; Service Layer coordina; las pantallas se separan del contrato y del acceso HTTP. |
| [Cómo analizar, elegir y no usar](https://ealcaraz85.github.io/topicoswebmobil/#org137772e) | Análisis de patrones de dos páginas | La caché no se vende como un Singleton propio. No se añaden Builder, Prototype o Abstract Factory sin una necesidad de creación variable. |
| [IA y caso integrador](https://ealcaraz85.github.io/topicoswebmobil/#orged30ae5) | `ml/`, adaptador, reglas y pruebas | CSV → split → Pipeline → evaluación → joblib → inferencia → reglas → orden. La IA está dentro del flujo de la aplicación. |
| [Arrancar Django](https://ealcaraz85.github.io/topicoswebmobil/#orga5e7de1) | `backend/config/`, `optica/models.py`, migraciones, admin | Proyecto/app, settings, rutas, modelos, ORM, migraciones y JSON. Se conserva SQLite como pide el primer proyecto. |
| [Django ya incorpora patrones](https://ealcaraz85.github.io/topicoswebmobil/#org62ff1d4) | Enrutamiento, ORM y `transaction.atomic` | Se distingue infraestructura del framework de separaciones explícitas propias. No se atribuye todo a clases inventadas para el trabajo. |
| [Primer corte](https://ealcaraz85.github.io/topicoswebmobil/#org7b25f10) | Un backend Django con módulos internos | Se empieza con un despliegue y responsabilidades claras. Extraer un servicio será una decisión posterior basada en necesidades. |
| [Flutter: fundamentos, instalación y widgets](https://ealcaraz85.github.io/topicoswebmobil/#orgcb52564) | `main.dart`, `screens/`, `widgets/common.dart` | `MaterialApp`, tema, widgets Stateless/Stateful, composición, `Form`, controladores, `Navigator`, `FutureBuilder` y UI según el ancho. |
| [Django + Flutter y microservicios](https://ealcaraz85.github.io/topicoswebmobil/#orgb700eb6) | `ApiClient` → API JSON Django | API separa cliente y servidor. Backend y cliente separados no implican varios servicios de negocio. DRF es una opción explicada en clase, no una exigencia de P1: aquí basta `JsonResponse`. |
| [Front, contenedor y empaquetado](https://ealcaraz85.github.io/topicoswebmobil/#org1f33cf6) | `build/web`, Android, `API_BASE_URL`, CORS | Un código Dart puede compilar a web y móvil. `10.0.2.2` apunta a la PC desde el emulador; web usa `127.0.0.1`. Cambia el destino o URL, no las reglas del servidor. |
| [Asistente entrenado](https://ealcaraz85.github.io/topicoswebmobil/#orgf9397a0) | `ml/entrenar_asistente.py`, `clasificador_asistente.py`, `asistente.py`, `chat_screen.dart` | P2 ya añade TF-IDF + logística, artefacto y chat. El árbol recomienda una clase de paquete; el asistente interpreta una intención y consulta datos. |
| [Proyectos progresivos](https://ealcaraz85.github.io/topicoswebmobil/#orgcb3827a) | Matriz conjunta, guías, PDFs y evidencias del 17/11 | P1 individual con recomendador; P2 individual con asistente integrado. La revisión actual abarca P1 y P2; P3 queda fuera. |

Las actividades del curso sirven para ejercitar estas ideas. Este proyecto no se presenta como entrega independiente de todas esas actividades. P2 añade un asistente entrenado y recuperación documental extractiva de corpus público; no utiliza un LLM generativo. No se declaran Docker, gateway ni microservicios de P3.

## Una petición completa, con archivos abiertos

Ejemplo: pantalla 8 h, exterior 1 h, presupuesto 700, oficina y sin exigir fotocromático.

| Paso | Archivo / operación | Qué entra y qué sale |
|---|---|---|
| 1 | `flutter_app/lib/screens/profile_screen.dart` | `Form` valida campos y construye el perfil. El botón pasa a carga mientras espera. |
| 2 | `flutter_app/lib/data/api_client.dart`, `recomendar` | `jsonEncode` transforma el mapa Dart; HTTP envía POST a `/api/recomendaciones/`. |
| 3 | `backend/config/urls.py` → `optica/urls.py` → `views.recomendar` | Django resuelve la ruta. La vista comprueba método y JSON. |
| 4 | `optica/validation.py`, `validar_entradas` | Verifica de nuevo tipos, rangos y campos permitidos. La validación Flutter no sustituye a la del servidor. |
| 5 | `optica/recomendador.py`, `RecomendadorArbol.ranking` | Convierte el perfil en DataFrame; el Pipeline aplica OneHotEncoder y `predict_proba`. Devuelve clases ordenadas. |
| 6 | `optica/repositories.py`, `CatalogoRepository` | Lee los precios, tratamientos y disponibilidad actuales mediante ORM. El modelo no es la autoridad del precio. |
| 7 | `optica/reglas.py`, `motivos_descarte` | Aplica presupuesto, disponibilidad y preferencia a cada alternativa. Conserva razones de rechazo. |
| 8 | `optica/services.py`, `recomendar` | Elige la primera alternativa elegible: Esencial. Devuelve original, final, probabilidades, corrección y ranking. No guarda una orden. |
| 9 | `screens/result_screen.dart`, `RecommendationView` | Muestra el JSON: Claridad 85% original, Esencial $650 final y 0% del modelo para esa clase. No se inventa una confianza nueva. |
| 10 | `ResultScreen.confirm` → `ApiClient.registrar` | El usuario confirma. Se envía el perfil con una clave UUID a `/api/ordenes/`. |
| 11 | `OpticaService.registrar` | Comprueba clave repetida, recalcula la decisión vigente y usa `transaction.atomic` para guardar. |
| 12 | `OrdenRepository` → `Orden` → SQLite | Se guardan folio, clave, paquete, perfil, precio y snapshot JSON. Devuelve HTTP 201. Un reintento idéntico devuelve la misma orden con HTTP 200. |
| 13 | `screens/order_screen.dart` | Muestra el folio y permite copiarlo. Después GET por folio recupera lo registrado, aunque cambie el precio actual. |

## Por qué el árbol y las reglas son piezas distintas

El entrenamiento aprende relaciones de las etiquetas sintéticas. No garantiza presupuesto ni disponibilidad. Si el catálogo sube un precio, sería innecesario reentrenar para impedir una solicitud que excede el máximo del comprador: esa restricción se evalúa con el precio vigente en cada petición.

La confianza corresponde al árbol, no a las reglas. Si la clase final tiene 0%, la interfaz lo conserva. La demostración cumple la restricción comercial, pero también muestra una limitación del entrenamiento que podría exigir revisión humana en un sistema real. Si ninguna clase cumple, HTTP 422 comunica el problema y no se crea una orden.

## Decisiones que conviene defender

- **SQLite:** es lo solicitado y permite una demo individual sin configurar un servidor de base de datos.
- **Monolito modular:** hay un backend desplegable, con módulos que se pueden entender por separado. Es la arquitectura exigida en P1.
- **Árbol:** sigue la tubería de los apuntes y permite inspeccionar las decisiones en `ml/arbol.txt`.
- **Pipeline:** guarda transformación y clasificador juntos; entrenamiento y uso aplican el mismo preprocesamiento.
- **Datos sintéticos:** permiten ejecutar y evaluar el prototipo sin inventar ventas reales. La accuracy mide solo esas etiquetas simuladas.
- **Dos POST:** explorar una recomendación no significa confirmar una solicitud. Se guarda cuando hay confirmación.
- **Recálculo al confirmar:** el servidor decide con el catálogo vigente y no acepta un precio impuesto por Flutter.
- **Snapshot:** explica una decisión histórica usando sus datos originales. Un cambio de catálogo no reescribe el pasado.
- **Idempotencia:** un reintento por fallo de red no debe crear otra orden. La clave se conserva en esa pantalla.
- **Estado local Flutter:** basta para este tamaño; se usa `mounted` después de esperas y `dispose` para liberar controladores.

## Guion breve de exposición

«Mi proyecto es una óptica y recomienda paquetes comerciales. Adapté el clasificador de medios de transporte de clase a cinco variables del perfil y cuatro clases de lentes. Flutter manda el formulario por JSON a Django. El backend ejecuta un Pipeline guardado con joblib y después aplica reglas sobre el catálogo actual. Muestra la sugerencia original y la decisión final con sus probabilidades. La confirmación recalcula y guarda en SQLite una orden con folio, perfil, precio y resultado histórico. Separé HTTP, servicio, adaptador, reglas y repositorios porque cambian por razones distintas. El cliente solo presenta el resultado. El modelo usa datos sintéticos, por lo que su evaluación no demuestra desempeño con clientes reales».

Antes de entregar, comprueba que puedes recorrer este ejemplo tú mismo y explicar qué cambiarías para añadir una regla o un paquete. Una nueva clase requiere datos y reentrenamiento; cambiar solo un precio se resuelve en catálogo.
