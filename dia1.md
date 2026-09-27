# Día 1 — Estudiar el caso web (sin código de dominio)

## Tabla de los siete inconvenientes atada a Django

| # | Inconveniente del enunciado | Qué ya trae Django | Qué tendremos que escribir nosotros | Qué no vamos a copiar del libro |
|---|---|---|---|---|
| 1 | Sesión, bitácora y encabezado copiados en cada trámite | `MIDDLEWARE` en `settings.py` (sesión, CSRF, auth) ya es la cadena de responsabilidad | Middleware propio solo si hace falta bitácora específica del dominio | Un Front Controller casero: `urls.py` + el resolver de Django ya lo son |
| 2a | El `switch` de 200 líneas para elegir medio | Nada (es dominio puro) | Contrato `MedioDeEntrega` + una clase/función por medio (Strategy) | No meter Abstract Factory: solo cambia el medio, no un kit completo |
| 2b | Cada proveedor de IA habla un JSON/XML distinto | Nada | Un `RecomendadorIA` (contrato) + un adaptador que traduce a `Sugerencia(medio, motivo)` | No meter el `route_hint` dentro de la vista ni del `planear()` |
| 3 | La plantilla ejecuta SQL para pintar mapa y ETA | El motor de plantillas (Jinja/Django templates) solo rellena huecos | La vista/servicio arma el contexto ya listo (`estado`, `eta`) antes de renderizar | No repetir el mismo `SELECT` en el reporte de gerencia: reusar el servicio |
| 4 | Cobro y alta se mezclan; doble clic duplica el cargo | `django.db.transaction.atomic()` ya es la Unit of Work | El aviso (correo/señal) disparado **después** del commit, no dentro | No usar Observer para decidir si el envío se confirma |
| 5 | App y panel piden distinto formato del mismo pedido | El mismo modelo/servicio puede alimentar dos vistas | Una vista JSON mínima (`JsonResponse`) además de la vista HTML | No hacer doce *fetch*; un recurso de agregación basta |
| 6 | Si la IA o el mapa se caen, no se puede ni consultar lo ya guardado | Nada especial | Un timeout/flag para apagar la IA sin tumbar `GET /pedidos/<id>` | No inventar Circuit Breaker de librería si un `try/except` con timeout alcanza |
| 7 | Proponen Event Sourcing/CQRS/Redux para un PDF de guía | El ORM y una vista bastan para leer un pedido y generar un archivo | Nada de aparato extra | **Ninguno** de esos patrones: es autenticar + consultar + generar |

## Tres renglones finales

- **¿`urls.py` es Front Controller, Page Controller, o el camino hacia los dos?**
  Es el camino hacia los dos: el `resolver` de Django (todo el árbol de `urls.py`) hace de Front Controller — una sola entrada HTTP para todo el proyecto. Cada función/vista a la que despacha (`registrar_pedido`, `ver_pedido`) es el Page Controller: delgada, un trámite.

- **¿La plantilla Jinja/Django puede hacer `SELECT`?**
  Técnicamente sí (se puede llamar al ORM desde un template tag), pero no se debe: eso mezcla persistencia con presentación (Template View roto). La plantilla debe recibir el contexto ya armado por la vista o el servicio.

- **¿Por qué sí o por qué no?**
  Porque si la plantilla consulta, cualquier cambio de "cómo se guarda" (SQL, memoria, otro motor) obliga a tocar el HTML, y el reporte de gerencia acaba duplicando la misma consulta con otro formato — exactamente el inconveniente 3 del enunciado.
