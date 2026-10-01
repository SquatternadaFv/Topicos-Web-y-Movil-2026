# Día 5 — El mismo pedido en JSON y la defensa

Objetivo: inconveniente 5 del enunciado. El panel necesita HTML con mapa; la futura app necesita un JSON mínimo del **mismo folio**. La solución continúa la separación de responsabilidades de los días 2, 3 y 4.

## Qué se agregó o consolidó

1. **`entregas/views.py` + `urls.py`** — el día 4 ya contenía `ver_pedido_json` y su ruta. En el día 5 se consolida su contrato y se restringen las consultas a GET. La API entrega exactamente `folio`, `estado`, `eta`; el seguimiento HTML conserva mapa, medio y etiqueta legible del estado. Un pedido inexistente devuelve 404; la API devuelve un objeto de error.
2. **`entregas/services.py`** — `consultar_pedido(folio)` es el trámite compartido por HTML y JSON. Pide el pedido a `repository.buscar_pedido`, que ejecuta una sola consulta, y reutiliza `contexto_pedido`. `consultar_reporte` prepara la lista con una consulta para hasta 20 pedidos. Los resultados llegan materializados a las plantillas; no se les pasa un QuerySet pendiente ni relaciones que disparen consultas.
3. **`entregas/repository.py`** — se conserva `contexto_pedido` del día 4 y se añade `estado_codigo`. El panel muestra `Creado` o `En camino`; la API usa `CREADO` o `EN_CAMINO`, códigos estables para la app. Son dos representaciones del mismo estado guardado, no dos pedidos ni dos fuentes de verdad.
4. **`seguimiento.html`** — un enlace abre el JSON del folio actual. El mapa sigue siendo un recuadro: no se inventa una integración ni se consulta SQL desde HTML.
5. **Arranque y continuidad** — se incluyen `requirements.txt` y `migrations/0001_initial.py`. Se conserva `/pedidos/nuevo` y se añade `/pedidos`, la ruta del enunciado. Se recupera `/entregas/hola/`. Django proporciona la protección CSRF del formulario; no escribimos una portería propia. `on_commit(robust=True)` conserva el pedido y permite responder aunque falle el aviso posterior.
6. **Entregables escritos** — README breve, contrato con ejemplos, guion de defensa y verificación con pruebas de integración. El diseño de medios, la fábrica simple y el Adapter JSON proceden del proyecto entregado en el ZIP.

## Camino de la consulta con nombres de Django

1. El manejador HTTP de Django y los middleware reciben la petición. **Esto ya lo instancia el marco**: no es un Front Controller GoF que escribimos al lado.
2. `config.urls` incluye `entregas.urls`; el resolver despacha a `ver_pedido` o `ver_pedido_json`. `urls.py` configura el camino, no es por sí solo el manejador HTTP completo.
3. El Page Controller llama a `services.consultar_pedido(folio)`.
4. El servicio obtiene el modelo mediante `repository.buscar_pedido` y prepara valores con `contexto_pedido`.
5. El Page Controller selecciona la representación: `render(..., seguimiento.html, contexto)` o `JsonResponse(...)`.

Los GET no llaman `registrar_pedido`, al Adapter ni a `planear`: ETA y medio se leen del pedido ya guardado. Así, un folio previo sigue disponible aunque se apague `IA_DISPONIBLE`.

## Una frase por decisión

- **Service Layer:** comparte el trámite de consultar entre clientes porque el panel y la app tienen distinta presentación del mismo pedido; no es un segundo modelo de lectura ni CQRS.
- **Template View:** el HTML pinta datos preparados porque consultar desde la plantilla acoplaría el seguimiento a la persistencia; no se reimplementa el motor de Django.
- **Recurso agregado JSON:** una petición obtiene los tres datos que necesita este seguimiento móvil; no se fuerza un patrón GoF ni doce endpoints separados.
- **Strategy y Adapter, heredados:** el algoritmo del medio y la traducción del proveedor cambian por razones distintas. La consulta del día 5 no necesita conocer ninguna clase concreta.
- **Fábrica simple, heredada:** un string identifica el medio; no existen familias de trámites que redefinan un gancho de creación, así que no se añadió Factory Method.

## Qué se rechazó y por qué

El punto 7 propone Event Sourcing, CQRS y Redux global para una guía PDF. En ese trámite bastarían autenticación, una consulta del pedido y generación del archivo. Un historial de eventos, proyecciones, sincronización de modelos o un almacén global no resuelven una necesidad demostrada de este corte. El JSON agregado tampoco exige microservicios ni Django REST Framework para tres campos de solo lectura.

## Alcance y pendientes honestos

Se completa el día 5 con panel HTML, JSON del mismo folio, README y apuntes del ensayo. No se programa la app nativa ni un PDF. Se conserva la idempotencia como pendiente del día 4: PRG evita crear al recargar el resultado, pero **no** evita dos altas cuando llegan dos POST reales. La base recibida tampoco contenía el segundo proveedor XML ni `score` en su JSON; esa parte del día 3 no se presenta como terminada. Dimensiones, urgencia, fechas límite, validación completa y autenticación corresponden al desarrollo posterior del caso.

El guion es material para revisar y ensayar con los cinco integrantes; no acredita una reunión, grabación o consenso que no se realizó aquí. Cada integrante debe poder justificar las decisiones con las fuerzas del relato y el código existente.

## Fuentes

- [Apuntes del curso: La empresa de entregas y actividad de cinco días](https://ealcaraz85.github.io/topicoswebmobil/#org106249d).
- [Django 5.2: JsonResponse](https://docs.djangoproject.com/en/5.2/ref/request-response/#jsonresponse-objects).
- [Django 5.2: transacciones y on_commit](https://docs.djangoproject.com/en/5.2/topics/db/transactions/#performing-actions-after-commit).
- Carpetas `dia1` a `dia4` del ZIP proporcionado, especialmente `dia4.md`, `views.py`, `repository.py` y `services.py`.
