# La empresa de entregas — Día 5

Continuación del día 4: el panel y el contrato móvil consultan el mismo pedido. Python 3.10+ y Django 5.2; SQLite, IA falsa, mapa de ejemplo y cobro simulado.

## Cómo correrlo

Abrir una terminal dentro de `dia5`:

```bash
python -m venv .venv
```

Activar: Windows CMD, `.venv\Scripts\activate`; PowerShell, `.venv\Scripts\Activate.ps1`; Linux/macOS, `source .venv/bin/activate`. Luego:

```bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Abrir `http://127.0.0.1:8000/pedidos/nuevo`, registrar y copiar el folio. El seguimiento ofrece un enlace al JSON del mismo pedido. Las migraciones están incluidas; no se necesita ejecutar `makemigrations`.

| Método y ruta | Resultado |
|---|---|
| `GET /entregas/hola/` | Comprobación de arranque |
| `GET/POST /pedidos` o `/pedidos/nuevo` | Formulario/alta y redirección PRG |
| `GET /pedidos/<folio>` | Seguimiento HTML con mapa y ETA |
| `GET /api/pedidos/<folio>` | JSON: `folio`, `estado`, `eta` en minutos |
| `GET /reporte` | Últimos 20 pedidos, una consulta |

## Conflictos y archivos

| Punto | Fuerza del relato y solución |
|---|---|
| 1 | Evitar portería copiada: Django aporta manejador/resolver HTTP y middleware; `urls.py` configura el despacho. No reescribimos Front Controller ni la cadena. CSRF activo; autenticación y sesiones no configuradas en este corte. |
| 2 | Crecen los medios y cambian los proveedores: Strategy en `entregas/medios.py`, Adapter en `ia.py`, fábrica simple en `fabrica.py`; el trámite `services.registrar_pedido` coordina. No hay familias que justifiquen Factory Method. |
| 3 | HTML sin SQL: Template View de Django; `repository.py` prepara valores y `services.py` los reutiliza en seguimiento/reporte. |
| 4 | Alta y cobro juntos: ORM y `transaction.atomic`; aviso con `on_commit(robust=True)`. PRG evita reenvío por recarga; idempotencia ante dos POST reales sigue pendiente, como se anotó el día 4. |
| 5 | Panel y móvil necesitan formatos distintos: ambos llaman `services.consultar_pedido`; cada vista devuelve HTML o JSON. Una consulta por seguimiento. |
| 6 | IA caída: fallback en el alta; las consultas leen datos persistidos y no dependen del proveedor. |
| 7 | Rechazamos Event Sourcing, CQRS y Redux global para una guía PDF: autenticar, consultar y generar no exige historial de eventos ni dos modelos. Este día no genera PDF ni app nativa. |

## Verificación y defensa

```bash
python manage.py check
python manage.py test entregas
```

Notas: `dia5.md`; contrato: `contrato_api.md`; ensayo de tres minutos: `defensa.md`; resultados reproducibles: `verificacion.md`. La configuración es local (`DEBUG=True`); no hay pagos reales ni validación completa de datos. La base del ZIP previo conserva el proveedor JSON; el segundo Adapter XML del día 3 sigue pendiente. El equipo debe revisar el guion y defender las decisiones del diseño que ya traía.
