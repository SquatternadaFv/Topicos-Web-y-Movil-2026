"""El trámite tiene nombre: registrar_pedido.

Día 3: ahora orquesta Adapter (IA) → Factory simple → Strategy
(planear) → persistencia. La vista sigue sin conocer EntregaDron ni
route_hint.
"""

from entregas.fabrica import crear_medio
from entregas.ia import AdaptadorIAFalsa, RecomendadorIA
from entregas.medios import ContextoViaje
from entregas.models import Pedido


def registrar_pedido(
    origen: str,
    destino: str,
    peso_kg: float,
    distancia_km: float,
    recomendador: RecomendadorIA | None = None,
) -> Pedido:
    recomendador = recomendador or AdaptadorIAFalsa()

    # Adapter: el dominio recibe Sugerencia(medio, motivo), nunca JSON crudo.
    sugerencia = recomendador.sugerir(peso_kg=peso_kg, distancia_km=distancia_km)

    # Factory simple: quién hace el new.
    medio = crear_medio(sugerencia.medio)

    # Strategy: el medio ya elegido sabe planear su propia entrega.
    ctx = ContextoViaje(distancia_km=distancia_km)
    plan = medio.planear(peso_kg=peso_kg, ctx=ctx)
    if not plan.aplica:
        # Si el medio sugerido no aplica de verdad, se cae a camioneta.
        medio = crear_medio("camioneta")
        plan = medio.planear(peso_kg=peso_kg, ctx=ctx)

    pedido = Pedido.objects.create(
        origen=origen,
        destino=destino,
        peso_kg=peso_kg,
        medio=plan.medio,
        motivo_medio=sugerencia.motivo,
        eta_minutos=plan.minutos,
        estado="CREADO",
    )
    return pedido
