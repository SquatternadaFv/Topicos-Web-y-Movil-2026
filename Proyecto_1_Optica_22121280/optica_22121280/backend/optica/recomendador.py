"""Adapter: Pipeline sklearn -> ranking del dominio; modelo en caché por proceso."""
from functools import lru_cache
from pathlib import Path
from typing import Protocol
import joblib
import pandas as pd
from .validation import ErrorDominio

CAMPOS = ['horas_pantalla', 'horas_exterior', 'presupuesto', 'uso_principal', 'prefiere_fotocromatico']
RUTA_MODELO = Path(__file__).resolve().parent / 'modelo' / 'modelo_optica.joblib'

class Predictor(Protocol):
    version: str
    def ranking(self, entradas: dict) -> list[tuple[str, float]]: ...

class RecomendadorArbol:
    def __init__(self, ruta=RUTA_MODELO):
        try:
            artefacto = joblib.load(ruta)
            self.modelo, self.version = artefacto['pipeline'], artefacto['version']
        except (OSError, ValueError, KeyError) as exc:
            raise ErrorDominio('Modelo no disponible. Ejecuta ml/entrenar.py y reinicia el backend.', 503) from exc

    def ranking(self, entradas):
        probabilidades = self.modelo.predict_proba(pd.DataFrame([entradas], columns=CAMPOS))[0]
        return sorted([(str(c), float(p)) for c, p in zip(self.modelo.classes_, probabilidades)], key=lambda par: (-par[1], par[0]))

@lru_cache(maxsize=1)
def obtener_recomendador() -> Predictor:
    return RecomendadorArbol()
