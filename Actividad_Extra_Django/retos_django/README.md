# Plataforma de entregas — Retos extra de Django

Ampliación actual: [complemento de retos](../../actividades/retos_django_complemento.md). Para el reto 4 del enunciado vigente, ejecutar `python scripts/reto4_docker.py` desde la raíz general del repositorio; ese script verifica destino → confirmar por sesión. Los scripts antiguos de esta carpeta conservan la demostración complementaria de último folio.

Ampliación del proyecto del día 4. La raíz contiene `manage.py`, `requirements.txt`, `EXTRA.md` y la configuración Docker. Requiere Python 3.12 o posterior compatible con Django 5.2. Los cinco integrantes están identificados en `EXTRA.md`.

## Arranque local

```bash
python -m venv .venv
```

Active el entorno: en PowerShell, `.\.venv\Scripts\Activate.ps1`; en Linux/macOS, `source .venv/bin/activate`. Después:

```bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Abra `http://127.0.0.1:8000/entregas/cotizador/`. En otra terminal, `python cliente_movil.py` hace la misma consulta. `python manage.py test` verifica diecisiete pruebas. En Windows se usa `runserver`; Gunicorn se ejecuta dentro del contenedor Linux. `/entregas/modelo/` y `/entregas/asistente/` usan el laboratorio compartido y sus artefactos entrenados desde la raíz.

## Rutas y responsabilidades

| Ruta | Uso |
| --- | --- |
| `/entregas/estado/` | Contrato JSON y evidencia individual |
| `/entregas/cotizar/?km=5&kg=2` | Cotización validada; errores JSON 400 |
| `/entregas/cotizador/` | Cliente HTML con `fetch` |
| `/entregas/visitas/` y `/entregas/visitas-mal/` | Sesión compartida frente a contador global |
| `/entregas/ultimo/?folio=ABC123` y `/entregas/ultimo/ver/` | Folio por sesión; versión global al activar `DEMO_ULTIMO_GLOBAL=1` |
| `/pedidos/nuevo`, `/pedidos/<folio>`, `/api/pedidos/<folio>` | Panel y JSON del proyecto anterior |

`config/urls.py` y Django cubren Front Controller; las plantillas cubren Template View. La vista `cotizar` valida HTTP y delega la decisión a `entregas/reglas.py`; ambos clientes comparten esa regla. El proyecto anterior conserva Service Layer (`services.py`), Strategy (`medios.py`), Adapter (`ia.py`), fábrica (`fabrica.py`), PRG y transacción para pedido/cobro. Las sesiones en una base común resuelven el estado al replicar.

## Réplicas y entrega

Con Docker instalado/iniciado y el puerto 8000 libre, `python scripts/reto4_docker.py` prepara tres copias, reproduce el error, aplica el arreglo, escala a cinco y agrega las salidas reales a `EXTRA.md`. `GUIA_EQUIPO.md` contiene los comandos manuales y las evidencias individuales pendientes. `docker compose down` detiene los servicios y conserva la base.

Estado inicial de esta entrega: retos 2, 3 y 5 implementados/documentados; reto 1 pendiente de las cinco computadoras; reto 4 implementado con pruebas locales complementarias, pendiente de ejecución Docker. No confundir procesos locales con contenedores. Los límites de cotización son una propuesta de práctica que el equipo debe revisar y poder justificar.
