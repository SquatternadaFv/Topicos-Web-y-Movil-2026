"""Entrena y evalúa fuera de HTTP; guarda Pipeline, prueba y versiones."""
import hashlib
import json
from pathlib import Path
import sys
import joblib
import pandas as pd
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report,confusion_matrix,accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
from optica.clasificador_asistente import normalizar_texto


def entrenar():
    ruta=ROOT/'ml/datos/intenciones_optica.csv'
    datos=pd.read_csv(ruta)
    textos=datos.texto.map(normalizar_texto)
    if textos.duplicated().any():raise ValueError('Hay textos duplicados; corregir antes de separar.')
    train,test=train_test_split(datos.index,test_size=.2,stratify=datos.intencion,random_state=42)
    modelo=Pipeline([
        ('texto',TfidfVectorizer(ngram_range=(1,2),strip_accents='unicode',sublinear_tf=True)),
        ('clasificador',LogisticRegression(C=6,max_iter=1000,random_state=42)),
    ]).fit(textos.loc[train],datos.intencion.loc[train])
    pred=modelo.predict(textos.loc[test])
    version='asistente-v1-'+hashlib.sha256(ruta.read_bytes()).hexdigest()[:12]
    metricas={'version':version,'sklearn':sklearn.__version__,'filas':len(datos),'entrenamiento':len(train),'prueba':len(test),
              'semilla_split':42,'umbral_inferencia':.30,'accuracy':accuracy_score(datos.intencion.loc[test],pred),
              'clases':list(modelo.classes_),'vocabulario':len(modelo.named_steps['texto'].vocabulary_),
              'reporte':classification_report(datos.intencion.loc[test],pred,output_dict=True,zero_division=0),
              'matriz_confusion':confusion_matrix(datos.intencion.loc[test],pred,labels=modelo.classes_).tolist(),
              'limitacion':'Prueba pequeña de frases redactadas, sin validación con clientes reales; accuracy del clasificador, no de respuestas completas.'}
    salida=ROOT/'backend/optica/modelo';salida.mkdir(parents=True,exist_ok=True)
    joblib.dump({'pipeline':modelo,'version':version,'umbral':.30,'sklearn':sklearn.__version__},salida/'modelo_asistente.joblib')
    (ROOT/'ml/metricas_asistente.json').write_text(json.dumps(metricas,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    particiones=datos.copy();particiones['particion']=['entrenamiento' if i in train else 'prueba' for i in datos.index]
    particiones.to_csv(ROOT/'ml/datos/particiones_asistente.csv',index=False)
    prueba=datos.loc[test].copy();prueba['predicho']=pred;prueba['confianza_maxima']=modelo.predict_proba(textos.loc[test]).max(axis=1)
    prueba.to_csv(ROOT/'ml/prueba_asistente.csv',index=False)
    print(json.dumps({k:metricas[k] for k in ['version','filas','entrenamiento','prueba','accuracy','vocabulario']},ensure_ascii=False,indent=2))


if __name__=='__main__':entrenar()
