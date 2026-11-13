# Guía para completar y demostrar la actividad

## 1. Cada integrante, en su computadora

Suban el contenido de esta carpeta al repositorio del equipo (mantengan `EXTRA.md` en la raíz). Cada persona debe clonar ese repositorio; descargar el mismo ZIP en una sola computadora no cumple el reto 1.

```bash
git clone URL_DEL_REPOSITORIO_DEL_EQUIPO
cd NOMBRE_DEL_REPOSITORIO
python -m venv .venv
```

En Windows pueden crear el entorno con `py -3 -m venv .venv`. Activación en PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Si la política de PowerShell impide activar, pueden usar CMD con `.venv\Scripts\activate.bat`. No cambien la política del sistema si no hace falta. En Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Con el entorno activo, todos ejecutan:

```bash
python -m pip install -r requirements.txt
python -c "import sys; print(sys.prefix)"
python manage.py migrate
python manage.py runserver
```

Copien la salida real de `sys.prefix` en su sección de `EXTRA.md`. Abran `http://127.0.0.1:8000/entregas/estado/` y guarden una captura donde se vea la dirección. Pónganla en `evidencias/reto1/` con el nombre indicado en `EXTRA.md` y enlácenla allí. Nadie puede sustituir las capturas de sus compañeros. Si usan distintos sistemas, confirmen el párrafo de diferencias de comandos con lo que realmente hicieron.

## 2. Demostrar la cotización y sus errores

Con el servidor activo, prueben estas direcciones en navegador o terminal:

```bash
curl -i "http://127.0.0.1:8000/entregas/cotizar/?km=5&kg=2"
curl -i "http://127.0.0.1:8000/entregas/cotizar/?kg=2"
curl -i "http://127.0.0.1:8000/entregas/cotizar/?km=abc&kg=2"
```

En PowerShell usen `curl.exe`. Con la regla final (6 km), el primer resultado es bicicleta. Un paquete de 21 kg recibe camioneta incluso si la distancia es 1 km. Lean `reglas.py`, `validacion.py` y `cotizar` en `retos_views.py`: conversión/validación y decisión son responsabilidades distintas.

## 3. Dos clientes, misma regla

La carpeta `evidencias/` ya contiene capturas y salidas reales de antes/después. Para repetir manualmente: cambien solo `LIMITE_BICICLETA_KM` en `reglas.py` a `3.0`, reinicien el servidor, consulten 5 km y 2 kg en `/entregas/cotizador/` y en `python cliente_movil.py`. Guarden los resultados. Cambien la constante a `6.0`, reinicien y repitan las mismas consultas. Los dos clientes deben pasar de moto a bicicleta. No editen el HTML ni el cliente Python.

El servidor se reinicia para cargar el código Python actualizado; no se requiere cambiar los clientes. La versión final del paquete conserva `6.0`. La cotización es una política didáctica independiente del planificador del alta de pedidos del proyecto anterior.

Para regenerar automáticamente las capturas (opcional): `python -m pip install playwright`, `python -m playwright install chromium` y `python scripts/capturar_reto3.py`. Estas dependencias no se necesitan para correr la aplicación.

## 4. Docker: ejecución automática

Instalen/inicien Docker Desktop (Windows/macOS) o Docker Engine con Compose v2 (Linux). Detengan `runserver` para liberar el puerto 8000. Activen el entorno Python y ejecuten:

```bash
python scripts/reto4_docker.py
```

El script construye la imagen, inicia tres copias con el modo global, captura seis visitas buenas y seis malas, reproduce el folio inconsistente en las rutas exigidas, recrea las copias con sesiones en PostgreSQL y verifica el folio con tres y cinco contenedores distintos. Usa cookies; sin reenviarlas se estaría abriendo una sesión nueva. Solo incorpora la evidencia Docker a `EXTRA.md` si todas las etapas terminan correctamente. Si falla, deja la salida en `evidencias/docker_*.txt`; describan el intento y el error. No borra el volumen de la base.

## 4.1. Comandos manuales equivalentes

**Etapa 4 (pasos 9–12):** `.dockerignore` excluye el entorno local; `Dockerfile` instala dependencias y configura Gunicorn. Construyan y ejecuten una copia:

```bash
docker build -t plataforma-entregas-extra .
docker run --rm -p 8000:8000 plataforma-entregas-extra sh -c "python manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2"
```

Prueben `/entregas/estado/` y detengan con Ctrl+C antes de Compose. Esta copia usa SQLite efímero; en la siguiente etapa todas comparten PostgreSQL con volumen persistente.

**Etapa 5 y fallo global:** primero activen `DEMO_ULTIMO_GLOBAL=1`. En PowerShell: `$env:DEMO_ULTIMO_GLOBAL="1"`; en Linux/macOS: `export DEMO_ULTIMO_GLOBAL=1`.

```bash
docker compose up -d --build --scale web=3
docker compose exec -T balanceador nginx -s reload
docker compose ps
python scripts/capturar_http.py --modo contador
python scripts/capturar_http.py --modo global --numero 30 --min-copias 3
```

Guarden las salidas. `migrar` se ejecuta una vez antes de `web`; las tres copias no compiten por crear tablas. Cada contenedor usa dos workers: el PID permite identificar cada proceso.

**Arreglo:** cambien la variable a 0. En PowerShell: `$env:DEMO_ULTIMO_GLOBAL="0"`; en Linux/macOS: `export DEMO_ULTIMO_GLOBAL=0`.

```bash
docker compose up -d --no-deps --force-recreate --scale web=3 web
docker compose exec -T balanceador nginx -s reload
docker compose ps
python scripts/capturar_http.py --modo sesion --numero 30 --min-copias 3
docker compose up -d --scale web=5
docker compose exec -T balanceador nginx -s reload
docker compose ps
python scripts/capturar_http.py --modo sesion --numero 60 --min-copias 5
```

nginx debe resolver otra vez los destinos al cambiar las réplicas. Si aún no observa suficientes copias, espere a que arranquen, recargue nginx y repita la captura. Un HTTP 200 de una sola copia no demuestra el escalado.

Para detener: `docker compose down`. No agreguen `-v` si quieren conservar los datos. Las credenciales por defecto son solo para esta práctica local.

## 5. Para explicar cuando pase el docente

Cada integrante debe poder ubicar la regla y la validación, explicar por qué ambos clientes reflejan el cambio, distinguir memoria por proceso de sesión compartida, señalar la cookie y justificar por qué una transacción no evita por sí sola cobrar dos veces. Lean las cinco respuestas del reto 5 en `EXTRA.md` y exprésenlas con sus palabras.
