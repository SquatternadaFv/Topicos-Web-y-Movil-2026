"""Reglas de cotización independientes de HTTP y de los clientes."""
LIMITE_BICICLETA_KM = 6.0
LIMITE_BICICLETA_KG = 5.0
LIMITE_MOTO_KM = 15.0
LIMITE_MOTO_KG = 20.0


def elegir_medio(km: float, kg: float) -> tuple[str, str]:
    if kg > LIMITE_MOTO_KG:
        return 'camioneta', 'paquete de más de 20 kg'
    if km > LIMITE_MOTO_KM:
        return 'camioneta', 'distancia de más de 15 km'
    if km <= LIMITE_BICICLETA_KM and kg <= LIMITE_BICICLETA_KG:
        return 'bicicleta', 'distancia corta y paquete de hasta 5 kg'
    return 'moto', 'distancia media y paquete ligero'
