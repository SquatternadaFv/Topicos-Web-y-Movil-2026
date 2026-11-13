"""Adapter del modelo, implementación por reglas y Decorator de respaldo."""
from abc import ABC, abstractmethod
from functools import lru_cache
import math
import os

import joblib
import pandas as pd

from .base import CAMPOS, NUMERICAS, MODELOS, es_posible, costo, MEDIOS

OPCIONES = {'prioridad': ('normal', 'express', 'mismo_dia'),
            'zona_destino': ('centro', 'residencial', 'periferia', 'rural'),
            'clima': ('despejado', 'lluvia', 'viento_fuerte'),
            'trafico': ('bajo', 'medio', 'alto')}


def validar(cuerpo):
    if not isinstance(cuerpo, dict):
        raise ValueError('El cuerpo debe ser un objeto JSON.')
    faltantes = [c for c in CAMPOS if c not in cuerpo]
    if faltantes:
        raise ValueError('Faltan campos: ' + ', '.join(faltantes))
    p = {}
    for c in NUMERICAS:
        try:
            n = float(cuerpo[c])
        except (ValueError, TypeError, OverflowError) as error:
            raise ValueError(f'{c} debe ser numérico.') from error
        if not math.isfinite(n) or n < 0:
            raise ValueError(f'{c} debe ser finito y no negativo.')
        p[c] = n
    if p['peso_kg'] == 0 or any(p[c] == 0 for c in ('largo_cm','ancho_cm','alto_cm','volumen_l')):
        raise ValueError('Peso, dimensiones y volumen deben ser mayores que cero.')
    if p['hora_salida'] != int(p['hora_salida']) or not 0 <= p['hora_salida'] <= 23:
        raise ValueError('hora_salida debe ser un entero entre 0 y 23.')
    if p['fragil'] not in (0,1) or p['refrigerado'] not in (0,1):
        raise ValueError('fragil y refrigerado deben ser 0 o 1.')
    for c, valores in OPCIONES.items():
        if cuerpo[c] not in valores:
            raise ValueError(f'{c} debe estar en {valores}.')
        p[c] = cuerpo[c]
    volumen = p['largo_cm'] * p['ancho_cm'] * p['alto_cm'] / 1000
    if abs(volumen - p['volumen_l']) > max(.1, volumen * .05):
        raise ValueError('volumen_l no coincide con las dimensiones (tolerancia 5 % o 0.1 L).')
    if not any(es_posible(m,p) for m in MEDIOS):
        raise ValueError('El paquete excede la capacidad de todos los medios.')
    return p


class RecomendadorIA(ABC):
    @abstractmethod
    def sugerir(self, paquete):
        raise NotImplementedError


@lru_cache(maxsize=3)
def cargar_artefacto(ruta):
    return joblib.load(ruta)


class RecomendadorArbol(RecomendadorIA):
    def __init__(self, modelo='arbol'):
        if modelo not in ('arbol','bosque','red'):
            raise ValueError('Modelo desconocido.')
        self.nombre = modelo
        self.ruta = MODELOS / f'modelo_{modelo}.joblib'

    def cargar(self):
        return cargar_artefacto(self.ruta)

    def sugerir(self, paquete):
        m = self.cargar()
        probs = m.predict_proba(pd.DataFrame([paquete], columns=CAMPOS))[0]
        ranking = sorted(zip(m.classes_, probs), key=lambda par: -par[1])
        preferido = str(ranking[0][0])
        medio, confianza = next((str(m), float(c)) for m,c in ranking if es_posible(m,paquete))
        corregido = medio != preferido
        return {'modelo': self.nombre, 'medio': medio, 'confianza': confianza,
                'motivo': f'{self.nombre}; confianza {confianza:.1%}' + (f'; se descartó {preferido} por reglas' if corregido else ''),
                'preferido_por_modelo': preferido, 'corregido_por_reglas': corregido,
                'ranking': [{'medio': str(m), 'probabilidad': float(c), 'posible': es_posible(m,paquete)} for m,c in ranking],
                'plan': {'costo_estimado': round(costo(medio,paquete),2)}}


class RecomendadorReglas(RecomendadorIA):
    def sugerir(self, paquete):
        # Política simple y explícita de práctica: no pretende imitar la probabilidad del árbol.
        orden = ('camioneta',) if paquete['refrigerado'] else ('bicicleta','moto','dron','camioneta')
        medio = next(m for m in orden if es_posible(m, paquete))
        return {'modelo':'reglas', 'medio':medio, 'confianza':None,
                'motivo':'Reglas deterministas; primer medio viable por política de respaldo',
                'preferido_por_modelo':None,'corregido_por_reglas':False,'ranking':[],
                'plan':{'costo_estimado':round(costo(medio,paquete),2)}}


class RecomendadorConRespaldo(RecomendadorIA):
    def __init__(self, principal, respaldo):
        self.principal, self.respaldo = principal, respaldo

    def sugerir(self, paquete):
        try:
            return self.principal.sugerir(paquete)
        except (OSError, RuntimeError) as error:
            resultado = self.respaldo.sugerir(paquete)
            resultado['motivo'] = f'Respaldo por {type(error).__name__} del principal. ' + resultado['motivo']
            resultado['respaldo'] = True
            return resultado


@lru_cache(maxsize=6)
def obtener_recomendador(modelo='arbol'):
    if os.environ.get('RECOMENDADOR') == 'reglas':
        return RecomendadorReglas()
    return RecomendadorConRespaldo(RecomendadorArbol(modelo), RecomendadorReglas())
