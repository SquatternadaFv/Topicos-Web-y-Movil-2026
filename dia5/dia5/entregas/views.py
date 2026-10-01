"""Page Controllers: adaptan HTTP y presentación; no eligen medios."""

from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_http_methods

from entregas.models import Pedido
from entregas.services import consultar_pedido, consultar_reporte, registrar_pedido


@require_GET
def hola(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Hola, plataforma de entregas — día 5.")


@require_http_methods(["GET", "POST"])
def crear_pedido(request: HttpRequest) -> HttpResponse:
    """Conserva /pedidos/nuevo y también atiende POST /pedidos (PRG)."""
    if request.method == "POST":
        pedido = registrar_pedido(
            origen=request.POST.get("origen", "Bodega central"),
            destino=request.POST.get("destino", "Cliente"),
            peso_kg=float(request.POST.get("peso_kg", 1.0)),
            distancia_km=float(request.POST.get("distancia_km", 10.0)),
        )
        # Post-Redirect-Get: recargar la página de seguimiento no
        # vuelve a dar de alta el pedido.
        return redirect("ver_pedido", folio=pedido.folio)

    return render(request, "entregas/nuevo_pedido.html")


@require_GET
def ver_pedido(request: HttpRequest, folio) -> HttpResponse:
    """GET /pedidos/<folio> — seguimiento en HTML. Sin SQL en la plantilla.

    No depende de la IA ni del mapa externo: un pedido ya guardado
    debe seguir viéndose aunque esos colaboradores estén caídos.
    """
    try:
        contexto = consultar_pedido(folio)
    except Pedido.DoesNotExist as exc:
        raise Http404("Pedido no encontrado") from exc
    return render(request, "entregas/seguimiento.html", contexto)


@require_GET
def ver_pedido_json(request: HttpRequest, folio) -> JsonResponse:
    """GET /api/pedidos/<folio> — el mismo pedido, JSON mínimo para la app."""
    try:
        ctx = consultar_pedido(folio)
    except Pedido.DoesNotExist:
        return JsonResponse({"error": "Pedido no encontrado"}, status=404)
    return JsonResponse(
        {"folio": str(ctx["folio"]), "estado": ctx["estado_codigo"], "eta": ctx["eta"]}
    )


@require_GET
def reporte_pedidos(request: HttpRequest) -> HttpResponse:
    """Reporte de gerencia — reutiliza contexto_pedido, no duplica el SELECT."""
    return render(request, "entregas/reporte.html", {"pedidos": consultar_reporte()})
