# Contrato móvil — consulta del mismo pedido

## Recurso

`GET /api/pedidos/<folio>` sin barra final. `folio` es el UUID que devuelve el alta mediante la redirección al seguimiento HTML. No es el entero interno `Pedido.id`. Base local: `http://127.0.0.1:8000`.

No crea pedidos, no cobra y no vuelve a planear la ruta. Ejecuta **una consulta** del pedido guardado y responde `Content-Type: application/json`.

| Campo | Tipo JSON | Significado |
|---|---|---|
| `folio` | string UUID | Identificador compartido con `/pedidos/<folio>` |
| `estado` | string | Código `CREADO`, `EN_CAMINO` o `ENTREGADO` |
| `eta` | number o null | Minutos estimados persistidos; `null` si todavía no hay estimación |

ETA es duración estimada del plan guardado, no hora absoluta ni cuenta regresiva. El GET no la recalcula. El panel traduce el código de estado a una etiqueta legible y agrega el mapa de ejemplo; la API conserva los tres campos mínimos.

## Ejemplo ilustrativo de éxito, HTTP 200

Para peso 1.5 kg y distancia 8 km, el proveedor falso elige dron y el plan calcula 12 minutos. El folio siguiente es solo un ejemplo; cada alta genera el suyo:

```json
{
  "folio": "7d4637e1-4c17-4a90-a075-8c7536210b42",
  "estado": "CREADO",
  "eta": 12.0
}
```

Tras crear un pedido, abrir su enlace JSON o sustituir `FOLIO_REAL` en:

```bash
curl http://127.0.0.1:8000/api/pedidos/FOLIO_REAL
```

En PowerShell también se puede usar:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/pedidos/FOLIO_REAL
```

## Errores y métodos

| Situación | Respuesta |
|---|---|
| UUID válido sin pedido guardado | 404, JSON `{"error": "Pedido no encontrado"}` |
| Identificador que no es UUID | 404 del resolver de Django; no se garantiza cuerpo JSON |
| POST, PUT, PATCH o DELETE a un folio, con CSRF válido cuando corresponda | 405, encabezado `Allow: GET`; no modifica el pedido |
| Petición insegura sin token CSRF válido | 403 del middleware de Django, antes de la vista |
| IA apagada al consultar un folio existente | 200 con los valores guardados |

Las respuestas 404 del resolver, 403 y 405 de Django pueden tener otro tipo de cuerpo. Este contrato mínimo no es una API autenticada de producción. El alta sigue siendo un formulario web con CSRF y PRG, no un endpoint de creación JSON.
