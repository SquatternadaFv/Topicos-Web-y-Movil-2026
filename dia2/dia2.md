# Día 2 — Pensar el primer corte y arrancar Django

Objetivo: que exista el proyecto y **una** petición completa, todavía
sin los cuatro medios ni la IA (eso llega el día 3).

## El camino de `POST /pedidos/nuevo` con nombres de Django

1. **Front Controller** — el resolver de Django (todo `urls.py`), no algo escrito por nosotros.
   *No es GoF que escribamos: el marco ya lo instancia.*
2. **Middleware** — `CommonMiddleware` (y sesión/CSRF si se activan). Aquí iría autenticación si el proyecto la necesitara.
   *No es GoF que escribamos: es Chain of Responsibility que Django ya trae.*
3. **Page Controller (vista delgada)** — `entregas.views.crear_pedido`. Solo lee el POST, llama a `registrar_pedido(...)` y redirige. No conoce medios ni IA.
4. **Service Layer / trámite con nombre** — `entregas.services.registrar_pedido`. Hoy es honesto y simple: siempre motocicleta, ETA de mentira. El día 3 le mete Strategy y Adapter *sin tocar la vista*.
5. **Persistencia** — el ORM de Django (`Pedido.objects.create`) hace de Repository; no escribimos SQL a mano.
6. **PRG** — `crear_pedido` termina con `redirect("ver_pedido", folio=...)`. Recargar la página de seguimiento (un `GET`) nunca vuelve a dar de alta.
7. **Template View** — `seguimiento.html` recibe `estado`, `medio`, `eta` ya calculados; no ejecuta `SELECT`.

## Al final del día

- ¿`urls.py` es Front Controller, Page Controller, o el camino hacia los dos?
  Es el camino hacia los dos: el resolver completo de Django es el Front Controller; cada vista a la que despacha es el Page Controller.
- ¿La plantilla Jinja/Django puede hacer `SELECT`? Técnicamente sí, pero no se debe: mezclaría persistencia con presentación.
- ¿Por qué? Porque cualquier cambio de "cómo se guarda" obligaría a tocar el HTML.

Con `python manage.py migrate` y `python manage.py runserver`, `POST /pedidos/nuevo` da de alta (hoy siempre motocicleta) y redirige a `GET /pedidos/<folio>`. Feo vale; mezclar sesión, SQL y medios en la vista no.
