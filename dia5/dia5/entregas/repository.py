"""Un solo lugar arma el contexto de un pedido.

El seguimiento web, el contrato JSON y el reporte de gerencia reutilizan
la preparación de valores. Los servicios materializan esos datos antes
de entregarlos a las vistas; las plantillas no consultan la base.
"""

from entregas.models import Pedido


def buscar_pedido(folio) -> Pedido:
    """Una consulta por folio; no llama a proveedores ni recalcula el plan."""
    return Pedido.objects.get(folio=folio)


def contexto_pedido(pedido: Pedido) -> dict:
    return {
        "folio": pedido.folio,
        "estado": pedido.get_estado_display(),
        "estado_codigo": pedido.estado,
        "medio": pedido.medio,
        "eta": pedido.eta_minutos,
    }


def listar_pedidos_recientes(limite: int = 20):
    return Pedido.objects.order_by("-creado_en")[:limite]
