"""El trámite tiene nombre: registrar_pedido.

Día 2: todavía SIN los cuatro medios (Strategy) ni la IA (Adapter).
Siempre asigna motocicleta y un ETA de mentira, solo para que exista
UNA petición completa de punta a punta. El día 3 reemplaza el interior
de esta función; la vista no cambia.
"""

from entregas.models import Pedido


def registrar_pedido(origen: str, destino: str, peso_kg: float, distancia_km: float) -> Pedido:
    medio = "motocicleta"
    eta_minutos = distancia_km / 35.0 * 60  # ETA de mentira, vale por hoy

    pedido = Pedido.objects.create(
        origen=origen,
        destino=destino,
        peso_kg=peso_kg,
        medio=medio,
        eta_minutos=eta_minutos,
        estado="CREADO",
    )
    return pedido
