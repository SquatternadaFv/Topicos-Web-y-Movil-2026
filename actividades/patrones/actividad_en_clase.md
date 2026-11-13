# ¿Qué está pasando aquí?

Caso: empresa de entregas; panel web y aplicación móvil. Documento de trabajo preparado con asistencia para su revisión por el equipo. No se atribuyen discusiones o decisiones a compañeros que no participaron en esta sesión.

## Paso 1 — Inconvenientes

| Punto | Inconveniente | Qué cambia | Qué conservar | Qué se mezcló |
|---|---|---|---|---|
| 1 | Sesión y bitácora copiadas en cada página | Reglas de acceso | Trámites | Política común y controlador particular |
| 2a | Un switch reúne todos los medios | Algoritmo por vehículo | Registro del pedido | Orquestación y cálculo |
| 2b | JSON, XML y objetos de IA llegan al negocio | Proveedor y vocabulario | Sugerencia interna | Protocolo externo y dominio |
| 3 | SQL dentro de seguimiento y reportes duplicados | Presentación | Consulta del pedido | Acceso a datos y plantilla |
| 4 | Cobrar, guardar y avisar son una secuencia frágil | Suscriptores y disponibilidad | Consistencia de pedido/cobro | Transacción y efectos que pueden esperar |
| 5 | La app realiza doce viajes para pintar una pantalla | Necesidades del cliente | Identidad y estado del pedido | Representación y reglas duplicadas |
| 6 | Esperar IA bloquea consultar pedidos existentes | Disponibilidad externa | Lectura local | Dependencias de creación y lectura |
| 7 | Se ofrece una arquitectura desproporcionada para un PDF | Solo formato del documento | Consulta autorizada | Necesidad real y catálogo de herramientas |

**Quinto medio.** En la estructura actual del switch habría que abrir el controlador que lo contiene y sus copias. Con el corte propuesto se agrega una estrategia y una entrada en la fábrica; vista y contratos de IA permanecen iguales.

**route_hint → vehicle.** Si el idioma externo llega a la vista, tanto panel como app pueden romperse. Con Adapter se modifica la traducción de ese proveedor y se conserva Sugerencia(medio, motivo).

**Correo que falla.** No debe deshacer pedido y cobro ya confirmados. Se registra el hecho y se reintenta la notificación por separado. El cobro real externo necesitaría además idempotencia y conciliación; transaction.atomic no revierte una transferencia bancaria.

**IA caída.** Un pedido guardado debe poder consultarse sin IA. La lectura obtiene de la base el medio y ETA persistidos; no vuelve a recomendar.

## Paso 2 — Catálogo GoF, o ninguno

| Punto | GoF o ninguno | Por qué | Vecino descartado |
|---|---|---|---|
| 1 | Ninguno como solución completa | Django ya proporciona entrada y middleware; no son una única ficha GoF | Decorator por sí solo no expresa políticas que cortan la petición |
| 2a | Strategy; Factory para crear | Alternativas de planeación bajo contrato común | Adapter traduce protocolos, no calcula planes |
| 2b | Adapter | Traduce un formato externo a Sugerencia | Facade simplifica un subsistema propio |
| 3 | Ninguno como solución completa | Repository + Template View resuelven consulta/presentación | No basta nombrar MVC |
| 4 | Observer para avisos, ninguno GoF para la atomicidad | Unit of Work protege escrituras; Observer avisa después | Observer no garantiza que el pedido se guarde |
| 5 | Ninguno | Agregación/BFF responde al hambre de cada cliente | Factory no reduce viajes HTTP |
| 6 | Ninguno | Timeout, aislamiento y Circuit Breaker protegen ante fallos de red | Retry infinito amplifica el fallo |
| 7 | Ninguno | Autenticar, consultar y renderizar bastan para el PDF | Event Sourcing no es una solución al cambio de formato |

## Paso 3 — Primer corte

Elegiría separar el registro de pedidos de la vista HTTP. Un servicio recibe entradas validadas, adapta IA, crea el medio, calcula, guarda y avisa tras commit. No tocaría de inicio el cliente instalado ni los nombres del JSON. Después separaría la lectura del pedido: el panel recibe contexto HTML y el teléfono JSON mínimo del mismo folio. Son iguales pedido, estado y medio; pueden cambiar mapa, densidad de información y componentes visuales.

Fuente: https://ealcaraz85.github.io/topicoswebmobil/#orgeff9f7e
