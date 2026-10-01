"""El trámite tiene nombre: registrar_pedido.

Día 4: alta + cobro simulado van juntos en una transacción (Unit of
Work). El aviso se dispara DESPUÉS del commit, nunca antes ni en
lugar de él. Si la IA no responde, el alta no se cae: se usa un medio
por defecto y se sigue de largo.
"""

from decimal import Decimal

from django.db import transaction

from entregas.fabrica import crear_medio
from entregas.ia import AdaptadorIAFalsa, IANoDisponible, RecomendadorIA
from entregas.medios import ContextoViaje
from entregas.models import Cobro, Pedido
from entregas.repository import buscar_pedido, contexto_pedido, listar_pedidos_recientes

COSTO_BASE = Decimal("35.00")
COSTO_POR_KM = Decimal("2.50")


def consultar_pedido(folio) -> dict:
    """El mismo trámite de lectura alimenta HTML y JSON con datos guardados."""
    return contexto_pedido(buscar_pedido(folio))


def consultar_reporte(limite: int = 20) -> list[dict]:
    """Materializa los contextos antes de entregarlos a la plantilla."""
    return [contexto_pedido(p) for p in listar_pedidos_recientes(limite)]


def _sugerir_medio(recomendador: RecomendadorIA, peso_kg: float, distancia_km: float):
    """Aísla el try/except del colaborador inestable.

    Si la IA se cae, no se detiene el alta: se cae a un medio por
    defecto con un motivo explícito. El pedido SIGUE quedando
    guardado y consultable, que es lo que pide el inconveniente 6.
    """
    try:
        return recomendador.sugerir(peso_kg=peso_kg, distancia_km=distancia_km)
    except IANoDisponible:
        from entregas.ia import Sugerencia

        return Sugerencia(medio="camioneta", motivo="IA_NO_DISPONIBLE_FALLBACK")


def registrar_pedido(
    origen: str,
    destino: str,
    peso_kg: float,
    distancia_km: float,
    recomendador: RecomendadorIA | None = None,
) -> Pedido:
    recomendador = recomendador or AdaptadorIAFalsa()

    # Adapter (con manejo del colaborador caído).
    sugerencia = _sugerir_medio(recomendador, peso_kg, distancia_km)

    # Factory simple: quién hace el new.
    medio = crear_medio(sugerencia.medio)

    # Strategy: el medio ya elegido sabe planear su propia entrega.
    ctx = ContextoViaje(distancia_km=distancia_km)
    plan = medio.planear(peso_kg=peso_kg, ctx=ctx)
    if not plan.aplica:
        medio = crear_medio("camioneta")
        plan = medio.planear(peso_kg=peso_kg, ctx=ctx)

    monto = COSTO_BASE + COSTO_POR_KM * Decimal(str(distancia_km))

    # Unit of Work: pedido y cobro nacen juntos, o ninguno de los dos.
    with transaction.atomic():
        pedido = Pedido.objects.create(
            origen=origen,
            destino=destino,
            peso_kg=peso_kg,
            medio=plan.medio,
            motivo_medio=sugerencia.motivo,
            eta_minutos=plan.minutos,
            estado="CREADO",
        )
        Cobro.objects.create(pedido=pedido, monto=monto, confirmado=True)

        # El aviso va DESPUÉS del commit, nunca dentro de la
        # transacción: si el aviso falla, el pedido y el cobro ya
        # quedaron. Observer no sustituye esta atomicidad.
        transaction.on_commit(lambda: _avisar(pedido), robust=True)

    return pedido


def _avisar(pedido: Pedido) -> None:
    # Aquí iría un correo, una señal de Django o una cola. Por ahora,
    # un print basta para demostrar el orden: primero COMMIT, luego
    # el aviso.
    print(f"[aviso] Pedido {pedido.folio} registrado con {pedido.medio}.")
