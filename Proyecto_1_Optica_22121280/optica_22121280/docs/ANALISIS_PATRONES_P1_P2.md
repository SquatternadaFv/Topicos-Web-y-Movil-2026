# Análisis de patrones web y móvil: proyectos 1 y 2

Eduardo Osvaldo Rodríguez Gutiérrez · 22121280 · 17/11/2026

## Página 1: backend y límites de responsabilidad

**Contexto.** Lúmina integra un recomendador de paquetes comerciales y un asistente de comprador en el mismo monolito Django/SQLite. Flutter consume JSON. El análisis corresponde a archivos propios y distingue patrones de propiedades operativas.

**Strategy / políticas composables.** En `backend/optica/reglas.py`, el protocolo `Regla` define `evaluar(paquete, entradas)`. `ReglaPresupuesto`, `ReglaDisponibilidad` y `ReglaPreferencia` comparten esa interfaz. La colección de reglas permite combinar restricciones sin modificar el árbol. Evita confundir una preferencia estadística aprendida con una condición comercial obligatoria; las reglas no son algoritmos de entrenamiento independientes.

**Adapter del recomendador.** `backend/optica/recomendador.py` convierte el perfil en DataFrame y `classes_`/`predict_proba` en pares de código y probabilidad ordenados. `OpticaService` consume el protocolo `Predictor`. Evita que vistas o Flutter conozcan detalles de scikit-learn.

**Adapter del asistente, añadido en P2.** `backend/optica/clasificador_asistente.py` normaliza texto/UUID y traduce probabilidades multiclase a intención, confianza y versión. Aplica abstención ante vocabulario desconocido o confianza insuficiente. `AsistenteService` recibe una representación del dominio, no vectores ni valores numpy. Así no se filtra el formato del modelo al contrato HTTP.

**Repository.** `backend/optica/repositories.py` concentra lectura del catálogo, búsqueda de órdenes y creación mediante ORM. Ambos servicios reutilizan `CatalogoRepository` y `OrdenRepository`. Evita repetir consultas en cada vista o respuesta del chat. Se trata de un borde explícito sobre Django ORM, no de llamar Repository a cualquier modelo.

**Service Layer / fachada de casos de uso.** `backend/optica/services.py` coordina validación, inferencia, reglas y registro. `backend/optica/asistente.py` coordina clasificación, datos vivos, snapshot y contexto recuperable. Evita que HTTP o el cliente implementen lógica comercial. Explicar una orden lee su resultado histórico; una decisión nueva delega al mismo recomendador P1.

**Front Controller del framework.** `backend/config/urls.py`, `backend/optica/urls.py` y `views.py` reciben y despachan peticiones, adaptan métodos/cuerpos JSON y traducen errores. La entrada común evita rutas con reglas y validaciones duplicadas. Es infraestructura Django, no una clase adicional inventada.

**Transacción, idempotencia y caché.** El registro usa `transaction.atomic`, clave UUID única y snapshot en `Orden`; evita duplicar un reintento equivalente y perder la decisión histórica. Son propiedades operativas, no patrones GoF. `lru_cache` carga cada artefacto una vez por proceso: no es un Singleton distribuido. Cambiar artefactos requiere reiniciar Django.

<!-- SALTO_PAGINA -->

## Página 2: Flutter y evolución de P1 a P2

**Separación comparable a MVC.** `flutter_app/lib/screens/` presenta datos y maneja eventos; `models/models.dart` representa el contrato JSON; `data/api_client.dart` concentra transporte y errores. Evita mezclar widgets, HTTP y persistencia. Es una analogía arquitectónica, no un MVC estricto impuesto por Flutter. Los modelos Dart no son los modelos de IA; Django sirve JSON y no usa plantillas para esta interfaz.

**Composición de UI.** Pantallas y `widgets/common.dart` ensamblan controles reutilizables para catálogo, recomendación y orden. `ChatScreen` compone entrada, conversación, fuentes y acciones. Evita duplicar presentación y conserva un producto visual común. La composición de widgets es una decisión de diseño, sin forzar un nombre GoF.

**Navegación y estado local explícitos.** En `main.dart`, `NavigationBar` y `IndexedStack` mantienen disponibles catálogo, recomendación, consulta y asistente. `setState` actualiza selección y estados de cada pantalla. El chat conserva mensajes al cambiar de pestaña, deshabilita envío durante carga y conserva el texto ante error. Evita perder contexto inmediato y entrelazar envíos simultáneos; no implementa memoria conversacional en el servidor.

**Adapter HTTP e inyección para pruebas.** `ApiClient` codifica solicitudes, decodifica UTF-8/JSON y convierte errores de red/dominio en `ApiException`. Acepta un cliente HTTP inyectado; pantallas y servicios aceptan colaboradores en sus constructores. Esto permite comprobar contratos, carga y fallos sin una red real en cada prueba aislada. El recorrido de navegador complementa esas pruebas con HTTP y modelos reales.

**Separación cliente/servidor.** En P2, Flutter añadió `conversar`, `chat_screen.dart` y la cuarta pestaña; muestra `respuesta`, fuentes y la acción de abrir el perfil. En backend se añadieron entrenamiento, artefacto, Adapter, servicio y POST `/api/asistente/`. Los `.joblib`, reglas, corpus y SQLite permanecen en el servidor. El cliente solicita operaciones, no impone precio ni decisión.

**Dos modelos, responsabilidades diferentes.** El árbol de P1 estima clases de paquete a partir de cinco características; el servicio aplica restricciones y puede registrar. El clasificador de P2 identifica una intención a partir del texto. Para precios consulta catálogo actual; para explicar un folio lee snapshot; para recomendar dirige al formulario o delega a `OpticaService.recomendar`. Evita que el chat invente una decisión que pertenece al modelo de dominio.

**Recuperación documental y fuentes.** `recuperacion.py` usa un índice TF-IDF público para devolver un fragmento con cita. Los precios y estados no se congelan en documentos. Es recuperación extractiva sin LLM generativo; no se afirma una arquitectura de microservicios ni un patrón de generación que no existe.

**Trazabilidad.** Estas decisiones cubren el análisis exigido en [Proyecto 1](https://ealcaraz85.github.io/topicoswebmobil/#orgd85c21d) y su actualización en [Proyecto 2](https://ealcaraz85.github.io/topicoswebmobil/#orga05f98b). La matriz conjunta relaciona archivos, pruebas y capturas; la guía de defensa amplía los flujos y límites.
