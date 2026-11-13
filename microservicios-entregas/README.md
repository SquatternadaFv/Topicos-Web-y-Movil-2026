# Microservicios de la práctica

Tres responsabilidades: gateway sirve HTML y enruta, Pedidos asigna folio y conserva el registro, Recomendar carga los modelos y aplica reglas. Pedidos no instala scikit-learn. Es distinto de replicar el monolito.

Primero entrenar desde la raíz con `python ejecutar_actividades.py --solo-entrenar`. Después:

```powershell
cd microservicios-entregas
docker compose up --build
```

Abrir http://127.0.0.1:8080/ y crear un pedido. La única entrada publicada es el gateway. El selector envía arbol/bosque/red; Pedidos reenvía ese campo sin cargar los artefactos.

```powershell
curl.exe -H "Content-Type: application/json" --data-binary "@paquete.json" http://127.0.0.1:8080/pedidos
docker compose ps
docker compose stop recomendar
```

La siguiente creación muestra plan B/HTTP 503 y un folio de demostración. Ese 503 no autoriza reintentar a ciegas: aquí se conserva el pedido en memoria. En un sistema real se definiría semántica idempotente y estado pendiente antes de usarlo para operaciones comerciales. `docker compose start recomendar` recupera el servicio. `docker compose down` detiene estos servicios.

**Estado verificado:** se ejecutaron tres procesos HTTP locales y el proxy `gateway/local.py`, con capturas y fallo parcial. No se ejecutó Docker/nginx en esta computadora porque no están instalados. La configuración Compose se validó estructuralmente, no se presenta como una ejecución de contenedores. Evidencia: `../evidencias/verificacion/http.json` y capturas `03-*`, `04-*`.

**Límites de práctica:** memoria de Pedidos se pierde al reiniciar; no hay autenticación; plan B no representa aprobación comercial; Flask/Gunicorn y configuración de recursos requieren preparación de producción. La URL interna se configura con RECOMENDAR_URL y nunca se incrusta en Flutter ni en el HTML.
