import math


def leer_numero(parametros, nombre):
    texto = parametros.get(nombre)
    if texto is None or not texto.strip():
        raise ValueError(f'Falta el parámetro {nombre}.')
    try:
        valor = float(texto)
    except (ValueError, OverflowError):
        raise ValueError(f'{nombre} debe ser un número válido.') from None
    if not math.isfinite(valor):
        raise ValueError(f'{nombre} debe ser un número finito.')
    if valor < 0:
        raise ValueError(f'{nombre} no puede ser negativo.')
    return valor
