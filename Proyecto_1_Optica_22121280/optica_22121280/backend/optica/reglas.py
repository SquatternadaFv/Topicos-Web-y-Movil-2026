"""Políticas comerciales explícitas, independientes del modelo estadístico."""
from decimal import Decimal
from typing import Protocol

class Regla(Protocol):
    def evaluar(self, paquete, entradas: dict) -> str | None: ...

class ReglaPresupuesto:
    def evaluar(self, paquete, entradas):
        if paquete.precio > Decimal(str(entradas['presupuesto'])):
            return f'Precio ${paquete.precio} superior al presupuesto ${entradas["presupuesto"]:.2f}.'
        return None

class ReglaDisponibilidad:
    def evaluar(self, paquete, entradas):
        return None if paquete.disponible else 'Paquete temporalmente no disponible.'

class ReglaPreferencia:
    def evaluar(self, paquete, entradas):
        if entradas['prefiere_fotocromatico'] and not paquete.fotocromatico:
            return 'No satisface la preferencia explícita de fotocromático.'
        return None

REGLAS: tuple[Regla, ...] = (ReglaPresupuesto(), ReglaDisponibilidad(), ReglaPreferencia())

def motivos_descarte(paquete, entradas, reglas=REGLAS):
    return [motivo for regla in reglas if (motivo := regla.evaluar(paquete, entradas))]
