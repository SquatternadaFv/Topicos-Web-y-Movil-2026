"""Page Controller — delgado. Ni SQL, ni switch de medios aquí."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from entregas.models import Pedido
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
    """GET /pedidos/<folio> — seguimiento en HTML. Sin SQL en la plantilla."""
    pedido = get_object_or_404(Pedido, folio=folio)
    contexto = {
        "folio": pedido.folio,
        "estado": pedido.get_estado_display(),
        "medio": pedido.medio,
        "eta": pedido.eta_minutos,
    }
    return render(request, "entregas/seguimiento.html", contexto)
