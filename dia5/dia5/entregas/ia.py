"""Adapter — la IA habla otro idioma.

El dominio solo entiende Sugerencia(medio, motivo). El proveedor
(real o falso) responde route_hint/score, XML, o lo que sea: el JSON
ajeno muere aquí, en un solo archivo.

Día 4: el colaborador se puede "apagar" (flag) o tardar más de la
cuenta (timeout simulado). registrar_pedido decide qué hacer si esto
falla; este archivo solo levanta la excepción, no la esconde.
"""

from dataclasses import dataclass
from typing import Protocol

# Flag para simular la caída del proveedor en pruebas/demos, sin
# apagar nada de verdad. En un proveedor real esto sería un timeout
# de red (requests, timeout=...).
IA_DISPONIBLE = True


class IANoDisponible(Exception):
    """Se levanta cuando el colaborador de IA no responde a tiempo."""


@dataclass
class Sugerencia:
    medio: str
    motivo: str


class RecomendadorIA(Protocol):
    def sugerir(self, peso_kg: float, distancia_km: float) -> Sugerencia: ...


class AdaptadorIAFalsa:
    """Simula un proveedor real sin pagar ninguna API.

    Responde con el JSON crudo que 'llegaría' de un proveedor
    (route_hint/reason_code) y lo traduce aquí mismo.
    """

    _MAPA_HINT = {
        "van": "camioneta",
        "bike": "motocicleta",
        "pedal": "bicicleta",
        "air": "dron",
    }

    def _llamar_proveedor_falso(self, peso_kg: float, distancia_km: float) -> dict:
        if not IA_DISPONIBLE:
            # Aquí, con un proveedor real, sería un timeout de red.
            raise IANoDisponible("El proveedor de IA no respondió a tiempo")

        if peso_kg <= 2 and distancia_km <= 30:
            return {"route_hint": "air", "reason_code": "FASTEST"}
        if peso_kg <= 8 and distancia_km <= 12:
            return {"route_hint": "pedal", "reason_code": "SHORT_RANGE"}
        if peso_kg <= 20:
            return {"route_hint": "bike", "reason_code": "URBAN_TRAFFIC"}
        return {"route_hint": "van", "reason_code": "HEAVY_LOAD"}

    def sugerir(self, peso_kg: float, distancia_km: float) -> Sugerencia:
        crudo = self._llamar_proveedor_falso(peso_kg, distancia_km)
        medio = self._MAPA_HINT.get(crudo["route_hint"], "camioneta")
        return Sugerencia(medio=medio, motivo=crudo["reason_code"])
