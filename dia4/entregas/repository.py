"""Un solo lugar arma el contexto de un pedido.

El seguimiento web y el futuro reporte de gerencia NO deben duplicar
la misma consulta con otro formato (inconveniente 3). Ambos llaman a
esta función.
"""

from entregas.models import Pedido


def contexto_pedido(pedido: Pedido) -> dict:
    return {
        "folio": pedido.folio,
        "estado": pedido.get_estado_display(),
        "medio": pedido.medio,
        "eta": pedido.eta_minutos,
    }


def listar_pedidos_recientes(limite: int = 20):
    return Pedido.objects.order_by("-creado_en")[:limite]
