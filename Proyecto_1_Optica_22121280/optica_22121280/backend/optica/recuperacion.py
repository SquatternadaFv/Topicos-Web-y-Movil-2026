"""Recuperación de contexto público: citas verificables, sin generación libre."""
from functools import lru_cache
from pathlib import Path
import joblib
from .validation import ErrorDominio


class RecuperadorCorpus:
    def __init__(self,ruta=None):
        ruta=ruta or Path(__file__).parent/'modelo/indice_corpus.joblib'
        try:
            artefacto=joblib.load(ruta)
            self.vectorizador=artefacto['vectorizador']
            self.matriz=artefacto['matriz']
            self.documentos=artefacto['documentos']
        except (OSError,ValueError,KeyError) as error:
            raise ErrorDominio('Corpus no disponible. Ejecuta ml/indexar_corpus.py.',503) from error

    def buscar(self,mensaje):
        vector=self.vectorizador.transform([mensaje])
        puntuaciones=(vector@self.matriz.T).toarray()[0]
        i=int(puntuaciones.argmax())
        if puntuaciones[i]<.10:return None
        return {**self.documentos[i],'similitud':float(puntuaciones[i])}


@lru_cache(maxsize=1)
def obtener_recuperador():return RecuperadorCorpus()
