"""Strategy — varias formas de planear la entrega.

Camioneta, moto, bici y dron responden la misma pregunta (¿cabe?
¿cuánto tarda?) de formas distintas. El contrato deja que
`registrar_pedido` los use sin conocer sus nombres concretos.

Esto NO es Adapter (eso traduce el JSON de la IA) ni Factory (eso
decide QUIÉN construye el objeto, no cómo planea).
"""

from dataclasses import dataclass
from typing import Optional, Protocol


@dataclass
class ContextoViaje:
    distancia_km: float
    viento_alto: bool = False
    zona_urbana: bool = True


@dataclass
class Plan:
    aplica: bool
    medio: str = ""
    minutos: Optional[float] = None

    @staticmethod
    def no_aplica() -> "Plan":
        return Plan(aplica=False)

    @staticmethod
    def ok(medio: str, minutos: float) -> "Plan":
        return Plan(aplica=True, medio=medio, minutos=minutos)


class MedioDeEntrega(Protocol):
    def planear(self, peso_kg: float, ctx: ContextoViaje) -> Plan: ...


class EntregaCamioneta:
    def planear(self, peso_kg: float, ctx: ContextoViaje) -> Plan:
        if peso_kg > 200:
            return Plan.no_aplica()
        return Plan.ok("camioneta", ctx.distancia_km / 40.0 * 60)


class EntregaMotocicleta:
    def planear(self, peso_kg: float, ctx: ContextoViaje) -> Plan:
        if peso_kg > 20:
            return Plan.no_aplica()
        return Plan.ok("motocicleta", ctx.distancia_km / 35.0 * 60)


class EntregaBicicleta:
    def planear(self, peso_kg: float, ctx: ContextoViaje) -> Plan:
        if peso_kg > 8 or ctx.distancia_km > 12:
            return Plan.no_aplica()
        return Plan.ok("bicicleta", ctx.distancia_km / 15.0 * 60)


class EntregaDron:
    def planear(self, peso_kg: float, ctx: ContextoViaje) -> Plan:
        if peso_kg > 2 or ctx.viento_alto:
            return Plan.no_aplica()
        return Plan.ok("dron", ctx.distancia_km / 40.0 * 60)
