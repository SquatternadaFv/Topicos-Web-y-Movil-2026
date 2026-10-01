# Verificación — día 5

Ejecutada el 1 de octubre de 2026 con Python 3.12.14 y Django 5.2.17, SQLite y las migraciones incluidas. La comprobación del servidor se hizo en el puerto 8765; el arranque habitual del README usa 8000.

## Comandos y resultados

```text
python manage.py migrate
  contenttypes.0001_initial: OK
  contenttypes.0002_remove_content_type_name: OK
  entregas.0001_initial: OK

python manage.py check
  System check identified no issues (0 silenced).

python manage.py makemigrations --check --dry-run
  No changes detected

python manage.py test entregas --verbosity 2
  Found 10 test(s).
  Ran 10 tests in 0.046s
  OK
```

Las pruebas usan una base aislada. No modifican los pedidos de la base de desarrollo y pueden repetirse con `python manage.py test entregas`.

## Qué verifican las diez pruebas

| # | Caso | Resultado |
|---|---|---|
| 1 | Mismo folio, estado y ETA en HTML/JSON, leyendo un pedido en camino | Coinciden; 1 consulta SQL por representación |
| 2 | GET con IA apagada y llamadas al proveedor/estrategia bloqueadas | HTML y JSON responden sin invocarlos |
| 3 | Folio válido inexistente | 404 en ambas representaciones; error JSON en API |
| 4 | POST a las rutas de consulta, aislando la validación CSRF | 405 y `Allow: GET`; sin nuevos pedidos |
| 5 | Pedido guardado sin ETA | JSON con `eta: null` |
| 6 | Reporte con 20 pedidos | 1 consulta, sin consultas por fila |
| 7 | Alta en `/pedidos` y `/pedidos/nuevo`, redirección y dos recargas | Un pedido y un cobro por POST, sin altas por GET |
| 8 | Alta con proveedor IA apagado | Camioneta de respaldo y cobro guardado |
| 9 | Fallo del cobro dentro de la transacción | Rollback del pedido y del cobro; sin aviso |
| 10 | Aviso que falla después de un commit real | Pedido y cobro persisten; alta responde con redirección |

La prueba 10 usa `TransactionTestCase`, observa que el aviso ocurre fuera de `atomic` y comprueba que ambos registros ya existen. No simula el commit con un mock.

## Comprobación HTTP con servidor real

Se levantó `runserver --noreload` y se hicieron peticiones HTTP con cookies y token CSRF del formulario:

1. `GET /entregas/hola/`: 200.
2. `GET /pedidos/nuevo`: formulario con token CSRF.
3. `POST /pedidos`, origen Bodega central, destino Cliente, peso 1.5 kg y distancia 8 km: el cliente siguió la redirección al seguimiento, que devolvió 200.
4. `GET /api/pedidos/<folio recién creado>`: 200, UUID idéntico al HTML, estado `CREADO`, ETA `12.0` minutos y exactamente los tres campos del contrato.
5. `GET /reporte`: 200.

Se apagó el servidor tras comprobar el flujo. La entrega excluye la base de datos usada, entornos virtuales y cachés: al ejecutar `migrate` se crea una base limpia.

## Límites de esta evidencia

Son pruebas del alcance de los cinco días: no demuestran una app móvil implementada, pagos reales, autenticación, idempotencia entre dos POST, un proveedor XML ni resistencia a concurrencia de producción. La recarga PRG sí está verificada; el doble POST sigue siendo un pendiente explícito del día 4.
