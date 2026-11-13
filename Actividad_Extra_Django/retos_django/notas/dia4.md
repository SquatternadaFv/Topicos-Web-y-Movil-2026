# Día 4 — Plantilla limpia, transacción e IA caída

Objetivo: inconvenientes 3, 4 y 6 del enunciado.

## Qué se agregó

1. **`entregas/repository.py`** — `contexto_pedido(pedido)` es la única función que arma los datos de un pedido. La vista de seguimiento (`ver_pedido`) y el nuevo **reporte de gerencia** (`reporte_pedidos`) la reutilizan; ninguna de las dos vuelve a escribir el `SELECT`. La plantilla `seguimiento.html` solo pinta un recuadro ("mapa") y el ETA que ya le llegaron en el contexto — no consulta la base (Template View limpio).

2. **`entregas/models.py` + `services.py`** — se agregó `Cobro` (cobro simulado). `registrar_pedido` mete `Pedido.objects.create` y `Cobro.objects.create` **dentro del mismo `transaction.atomic()`**: nacen juntos o ninguno de los dos (Unit of Work). El aviso (`_avisar`, hoy un `print`) se dispara con `transaction.on_commit(...)`, es decir, **después** de que la transacción confirmó. Si el aviso fallara, el pedido y el cobro ya habrían quedado guardados — Observer no sustituye la atomicidad.

3. **`entregas/ia.py` + `services._sugerir_medio`** — se agregó un flag `IA_DISPONIBLE` que simula la caída del colaborador (`IANoDisponible`). `_sugerir_medio` atrapa esa excepción y cae a un medio por defecto (`camioneta`, motivo `IA_NO_DISPONIBLE_FALLBACK`) en vez de tumbar el alta. Y algo más importante: `ver_pedido` (`GET /pedidos/<folio>`) **nunca llama a la IA** — solo lee de la base — así que un folio ya guardado se sigue consultando aunque el colaborador de IA esté completamente apagado. Eso es lo que pide el inconveniente 6: la rueda infinita mientras la IA no habla no es diseño.

## Por escrito: doble clic en "crear"

- **PRG (ya cubierto desde el día 2)** resuelve el caso más común: si el usuario recarga la página de *resultado* (un `GET`) después de crear, el navegador no reenvía el formulario, así que no hay un segundo `POST` por esa vía.
- **Pero PRG no basta si el doble clic dispara dos peticiones `POST` reales** (dedo lento, doble tap, o un reintento automático del navegador/red antes de que llegue la redirección). Como hay "dinero de mentira" (el `Cobro` simulado), ahí sí hace falta **idempotencia**: el cliente debería mandar una `Idempotency-Key` única por intento de compra (p. ej. un UUID generado al cargar el formulario) y el servidor debe rechazar o devolver el mismo resultado si ya vio esa clave, en vez de crear un segundo `Pedido`+`Cobro`.
- **Lo que no vamos a hacer**: no se implementa Event Sourcing ni un log de eventos completo para esto — un campo único (`Idempotency-Key`) con una restricción `unique` en la base alcanza para el alcance de esta semana. Se deja anotado como *pendiente*, no como parte obligatoria del día 4.

## Vecino que no es

Un compañero podría decir "esto ya lo resuelve Observer, avisando dos veces no importa". No: Observer resuelve *quién se entera*, no *si el cobro se duplicó*. El problema del doble clic es de **Unit of Work + idempotencia**, no de aviso.
