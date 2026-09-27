"""Page Controller — delgado. Ni SQL, ni switch de medios aquí."""

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from entregas.models import Pedido
from entregas.repository import contexto_pedido, listar_pedidos_recientes
from entregas.services import registrar_pedido


def crear_pedido(request: HttpRequest) -> HttpResponse:
    """POST /pedidos/nuevo — alta. Redirige (PRG) al seguimiento tras crear."""
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


def ver_pedido(request: HttpRequest, folio) -> HttpResponse:
    """GET /pedidos/<folio> — seguimiento en HTML. Sin SQL en la plantilla.

    No depende de la IA ni del mapa externo: un pedido ya guardado
    debe seguir viéndose aunque esos colaboradores estén caídos.
    """
    pedido = get_object_or_404(Pedido, folio=folio)
    return render(request, "entregas/seguimiento.html", contexto_pedido(pedido))


def ver_pedido_json(request: HttpRequest, folio) -> JsonResponse:
    """GET /api/pedidos/<folio> — el mismo pedido, JSON mínimo para la app."""
    pedido = get_object_or_404(Pedido, folio=folio)
    ctx = contexto_pedido(pedido)
    return JsonResponse(
        {"folio": str(ctx["folio"]), "estado": pedido.estado, "eta": ctx["eta"]}
    )


def reporte_pedidos(request: HttpRequest) -> HttpResponse:
    """Reporte de gerencia — reutiliza contexto_pedido, no duplica el SELECT."""
    pedidos = [contexto_pedido(p) for p in listar_pedidos_recientes()]
    return render(request, "entregas/reporte.html", {"pedidos": pedidos})
