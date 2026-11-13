# Complemento de los cinco retos Django

## Reto 1 — Evidencia individual

Se ejecutó el proyecto en esta computadora. Entorno real: `C:\TopicosMovilWeb\.venv-actividades`, Python 3.12.16. Salida y versión: [http.json](../evidencias/verificacion/http.json), campo entorno. [Captura real de /entregas/estado/](../evidencias/verificacion/01-estado-esta-computadora.png).

No se afirma que esta ejecución pertenezca al entorno habitual de Eduardo ni que demuestre cinco computadoras. Faltan salidas/capturas propias de los cinco integrantes que pide el profesor. La guía existente explica cómo obtenerlas. Windows activa `.venv\Scripts\Activate.ps1`; Linux/macOS usa `source .venv/bin/activate`. Esa diferencia no prueba que todos las hayan ejecutado.

## Reto 2 — Cotización

Se conserva la función `entregas/reglas.py`, la validación backend y las salidas 200/400 ya guardadas en la entrega anterior. Las pruebas nuevas preservan su comportamiento. El cliente puede saltarse JavaScript, por eso el servidor valida números finitos, presencia y rango. Cuando las políticas por medio crezcan, Strategy separa algoritmos y la fábrica concentra creación; no se exige para cada if estable.

## Reto 3 — Dos clientes

Se conservan HTML con fetch, cliente_movil.py, capturas y salidas antes/después del cambio de regla de la entrega anterior. La decisión cambia en el backend; ningún cliente reimplementa el umbral. Si estuviera solo en JavaScript, el cliente Python seguiría usando otra regla o no tendría ninguna.

## Reto 4 — Enunciado actual

Implementado en `entregas/retos_views.py`:

- `/entregas/pedidos/?destino=Demo` crea en DB y con `?folio=...` consulta; `pedidos-mal/` conserva solo el contraejemplo en memoria.
- `/entregas/borrador/destino/?destino=...` guarda en request.session.
- `/entregas/borrador/confirmar/` consume el borrador y registra Pedido/Cobro en transacción; sin destino devuelve 400.
- `DEMO_BORRADOR_GLOBAL=1` reproduce el error con variable global.

Ejecución real **local**: [borrador_local.txt](../evidencias/verificacion/borrador_local.txt). El destino guardado por un proceso no aparece en otro en modo global; con sesión compartida se confirma correctamente entre tres y cinco procesos y dos clientes conservan destinos distintos. Se usa SQLite para esta comprobación secuencial; no se recomienda para réplicas de producción.

Pendiente **Docker**: [docker.json](../evidencias/verificacion/docker.json) registra que el ejecutable no está disponible. `python scripts/reto4_docker.py`, desde la raíz, prepara la demostración con PostgreSQL/nginx, verifica tres y cinco contenedores y guarda salidas reales. La evidencia local no sustituye ese requisito.

Con un proceso la variable global parece funcionar porque las peticiones suelen llegar a la misma memoria; dos clientes pueden sobrescribirse incluso allí. La sesión usa una identidad de cliente y almacenamiento compartido, por lo que dos usuarios no comparten la misma clave de datos. Para concurrencia de pagos se necesita además idempotencia; consumir una sesión no demuestra exclusión atómica entre POST simultáneos.

## Reto 5 — Casos

Las cinco respuestas se conservan en el EXTRA original: contrato compatible/versionado, tarea única fuera de las réplicas, archivos compartidos, entorno virtual frente a contenedor e idempotencia en pagos. Docker no vuelve persistentes las variables globales ni los archivos privados de cada contenedor.
