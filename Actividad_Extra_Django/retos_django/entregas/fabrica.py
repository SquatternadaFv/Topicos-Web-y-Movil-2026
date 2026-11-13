"""Quién hace el `new`.

Con el string que ya vino de la Sugerencia (traducida por el Adapter),
una fábrica simple basta: no hay familias de trámite que redefinan un
gancho, así que Factory Method sería ceremonia aquí.
"""

from entregas.medios import (
    EntregaBicicleta,
    EntregaCamioneta,
    EntregaDron,
    EntregaMotocicleta,
    MedioDeEntrega,
)

_CATALOGO = {
    "camioneta": EntregaCamioneta,
    "motocicleta": EntregaMotocicleta,
    "bicicleta": EntregaBicicleta,
    "dron": EntregaDron,
}


def crear_medio(tipo: str) -> MedioDeEntrega:
    clase = _CATALOGO.get(tipo)
    if clase is None:
        raise ValueError(f"Medio desconocido: {tipo!r}")
    return clase()
