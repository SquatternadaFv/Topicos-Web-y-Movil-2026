# Ensayo de tres minutos — apuntes para los cinco integrantes

Guion base para adaptar y ensayar. Abrir el formulario, un seguimiento con su JSON y el código indicado. Cada integrante debe revisar su explicación; los tiempos son orientativos, no constancia de una grabación.

## 0:00–0:35 — Integrante 1: conflicto y demostración

«La empresa necesita que panel y app muestren el mismo pedido. El panel necesita HTML con mapa; la app, folio, estado y ETA. Creamos desde `/pedidos/nuevo`: el POST redirige al seguimiento, así recargar el resultado no repite el alta. Este enlace abre `/api/pedidos/<folio>`. El UUID coincide y el ETA procede del pedido guardado. No programamos aún la app nativa; dejamos su contrato disponible.»

Mostrar: registro, URL de seguimiento y enlace al JSON.

## 0:35–1:10 — Integrante 2: Django y trámite compartido

«Django ya proporciona el manejo HTTP, el resolver, middleware, ORM y motor de plantillas. `urls.py` configura el despacho; las funciones de `views.py` son Page Controllers. No escribimos otro Front Controller ni otro motor de plantillas. HTML y JSON llaman a `consultar_pedido`, en `services.py`. El repositorio obtiene el pedido una vez y prepara los valores. El panel muestra una etiqueta y la API un código del mismo estado. Es una consulta por petición de seguimiento, no doce llamadas.»

Mostrar: `urls.py`, ambas vistas y `consultar_pedido`.

## 1:10–1:45 — Integrante 3: Strategy, Adapter y triciclo

«Conservamos las estrategias de `medios.py`: cada medio sabe planear. `ia.py` traduce el idioma del proveedor a `Sugerencia`; `fabrica.py` hace la creación. Para incorporar el algoritmo de un triciclo y poder construirlo, abrimos **dos archivos de producción**: agregamos `EntregaTriciclo` en `medios.py` y la entrada en el catálogo de `fabrica.py`. El trámite y las vistas siguen usando el contrato. Añadiríamos también una prueba de sus restricciones.»

«Si además el proveedor empieza a emitir un **nuevo código externo**, actualizamos su traducción en `ia.py`: sería un tercer archivo por un cambio de integración. No hace falta alterar el formato XML ni meter el triciclo en `registrar_pedido`. La fábrica construye; Strategy planea; Adapter traduce.»

Mostrar: contrato `MedioDeEntrega`, `_CATALOGO` y `_MAPA_HINT`.

## 1:45–2:20 — Integrante 4: fallos y consistencia

«El día 4 separó alta/cobro y aviso. `transaction.atomic` hace que pedido y cobro se guarden juntos o ninguno. `on_commit` ejecuta el aviso después; `robust=True` permite que su fallo no convierta el alta confirmada en un error HTTP. Las consultas no llaman a la IA: un folio existente sigue disponible si falla el proveedor. PRG evita repetir el alta al recargar, pero dos POST reales todavía podrían duplicar el cobro; la idempotencia quedó pendiente y necesita una clave única, no Observer.»

Mostrar: bloque transaccional y prueba de consulta con IA apagada.

## 2:20–3:00 — Integrante 5: lo que se rechazó y evidencia

«Rechazamos Event Sourcing, CQRS y Redux global para la guía PDF porque autenticar, consultar y generar un archivo no exige eventos ni dos modelos sincronizados. Este día entrega el mismo folio en HTML y JSON, un README y estas notas. Las pruebas comprueban coincidencia de datos, una consulta por GET, reporte sin consultas por fila, PRG, IA caída, rollback del cobro y aviso posterior fallido. El proyecto arranca con las migraciones incluidas. El proveedor XML del día 3 y la idempotencia siguen pendientes; no los declaramos implementados.»

Mostrar: README y resultado de `python manage.py test entregas`.

## Preguntas para practicar

| Pregunta | Respuesta ligada al código |
|---|---|
| ¿Por qué el JSON no trae el mapa y el cobro? | La app pidió tres campos; el mismo trámite prepara datos y cada representación selecciona los suyos. |
| ¿El endpoint ya existía? | Sí, en día 4; día 5 consolida su contrato, trámite compartido, pruebas y defensa. |
| ¿Factory Method? | No hay familias de trámites que redefinan la creación; basta el catálogo de la fábrica simple. |
| ¿Adapter es Facade? | Aquí traduce `route_hint` a un medio del dominio; no solo simplifica una interfaz propia. |
| ¿El mapa consulta la base? | No; es un recuadro que recibe el medio en el contexto. |
| ¿Cuántas consultas al abrir HTML y después JSON? | Una por petición: dos en total al abrir las dos representaciones. |
| ¿Qué cambia si la IA cae? | Alta usa el fallback; la consulta no utiliza IA y conserva los datos guardados. |
