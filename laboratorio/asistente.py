"""Tutorial: clasificador de intenciones, no LLM generativo ni proyecto de óptica."""
from functools import lru_cache
import json
import re

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from .base import RAIZ

CARPETA=RAIZ/'actividades'/'asistente-tutorial'
RUTA=CARPETA/'modelo_asistente.joblib'
EJEMPLOS={
 'saludo':['hola','buenos días','buenas tardes','qué tal','buenas noches','hola asistente','saludos','buen día amigo','hey hola','hola quiero ayuda'],
 'seguimiento':['dónde está mi pedido','quiero rastrear el folio','consultar estado de entrega','cómo va mi envío','buscar mi pedido','seguimiento de paquete','cuál es el estado del folio','mi pedido ya llegó','rastrear entrega por folio','ver situación de mi envío'],
 'catalogo':['qué servicios ofrecen','cuáles medios tienen','ver opciones de transporte','qué vehículos hay','lista de servicios','qué tipos de entrega manejan','tienen motocicleta','hay servicio de bicicleta','muéstrame sus medios','cuentan con camioneta'],
 'recomendacion':['recomienda un medio','qué vehículo me conviene','calcular recomendación del paquete','quiero elegir transporte','sugiere cómo enviar','necesito un medio para mi envío','cuál transporte recomiendas','recomendar entrega con peso y distancia','elegir vehículo adecuado','consulta al recomendador'],
 'explicacion':['por qué eligió moto','explica la recomendación','por qué no se usó dron','qué significa corregido por reglas','por qué fue camioneta','explicar el medio asignado','cuál fue el motivo del pedido','razón de la recomendación','por qué cambiaron mi medio','qué reglas descartaron el dron'],
 'fuera':['quién ganó el partido','cuál es la receta del pastel','resuelve mi tarea de historia','dime el clima en Marte','comprar acciones de una empresa','recomienda una película','qué significa esta canción','cuéntame política internacional','quiero un diagnóstico médico','qué celular debería comprar'],
}


def entrenar():
    CARPETA.mkdir(parents=True,exist_ok=True)
    datos=pd.DataFrame([{'texto':t,'intencion':i} for i,frases in EJEMPLOS.items() for t in frases])
    datos.to_csv(CARPETA/'intenciones.csv',index=False)
    xe,xp,ye,yp=train_test_split(datos.texto,datos.intencion,test_size=.2,stratify=datos.intencion,random_state=42)
    vacias=['el','la','de','del','en','un','una','mi','por','que','cual','es','los','las','a','con','para']
    modelo=Pipeline([('texto',TfidfVectorizer(ngram_range=(1,2),strip_accents='unicode',stop_words=vacias)),('clasificador',LogisticRegression(C=6,max_iter=1000,random_state=42))]).fit(xe,ye)
    reporte=classification_report(yp,modelo.predict(xp),zero_division=0)
    joblib.dump(modelo,RUTA,compress=3)
    (CARPETA/'metricas.txt').write_text('Prueba separada 20 %, semilla 42. Solo 12 ejemplos: incertidumbre alta.\n'+reporte,encoding='utf8')
    pd.DataFrame({'texto':xp,'real':yp,'predicho':modelo.predict(xp)}).to_csv(CARPETA/'prueba.csv',index=False)
    return reporte


@lru_cache(maxsize=1)
def cargar():
    return joblib.load(RUTA)


def clasificar(texto):
    modelo=cargar()
    if modelo.named_steps['texto'].transform([texto]).nnz==0:
        return 'fuera',0.
    ps=modelo.predict_proba([texto])[0];j=ps.argmax()
    return str(modelo.classes_[j]),float(ps[j])


def extraer_folio(texto):
    match=re.search(r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b',texto)
    return match.group(0) if match else None
