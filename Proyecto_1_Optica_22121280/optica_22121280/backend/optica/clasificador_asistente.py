"""Adapter de texto y salida sklearn; no consulta la base ni decide paquetes."""
from functools import lru_cache
from pathlib import Path
import re
import joblib
from .validation import ErrorDominio

RUTA=Path(__file__).parent/'modelo/modelo_asistente.joblib'
PATRON_FOLIO=r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b'


def normalizar_texto(texto):
    return ' '.join(re.sub(PATRON_FOLIO,' <folio> ',texto).lower().split())


class ClasificadorIntenciones:
    def __init__(self,ruta=RUTA):
        try:
            artefacto=joblib.load(ruta)
            self.pipeline=artefacto['pipeline']
            self.version=artefacto['version']
            self.umbral=artefacto['umbral']
        except (OSError,ValueError,KeyError,TypeError) as error:
            raise ErrorDominio('Asistente no disponible. Ejecuta ml/entrenar_asistente.py y reinicia el backend.',503) from error

    def clasificar(self,mensaje):
        texto=normalizar_texto(mensaje)
        vector=self.pipeline.named_steps['texto'].transform([texto])
        if vector.nnz==0:
            return {'intencion':'fuera_dominio','confianza':0.,'version':self.version,'motivo':'sin vocabulario conocido'}
        probs=self.pipeline.predict_proba([texto])[0]
        orden=sorted(zip(self.pipeline.classes_,probs),key=lambda par:(-par[1],par[0]))
        etiqueta,confianza=orden[0]
        intencion=str(etiqueta) if confianza>=self.umbral else 'aclaracion'
        return {'intencion':intencion,'confianza':float(confianza),'version':self.version,
                'ranking_intenciones':[{'intencion':str(k),'probabilidad':float(v)} for k,v in orden[:3]]}


@lru_cache(maxsize=1)
def obtener_clasificador():
    return ClasificadorIntenciones()
