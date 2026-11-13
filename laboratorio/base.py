from contextlib import contextmanager
from copy import deepcopy
import importlib.util
from pathlib import Path
import random

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

RAIZ = Path(__file__).resolve().parents[1]
DATOS = RAIZ / 'proyectos' / 'dataset-medios'
MODELOS = DATOS / 'modelos'
NUMERICAS = ['distancia_km', 'peso_kg', 'largo_cm', 'ancho_cm', 'alto_cm',
             'volumen_l', 'fragil', 'refrigerado', 'valor_declarado_mxn', 'hora_salida']
CATEGORICAS = ['prioridad', 'zona_destino', 'clima', 'trafico']
CAMPOS = NUMERICAS + CATEGORICAS
OBJETIVO = 'medio_recomendado'
spec = importlib.util.spec_from_file_location('generador_profesor', DATOS / 'originales_profesor' / 'generar_dataset.py')
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)
LIMITES = deepcopy(g.LIMITES)
MEDIOS = tuple(g.MEDIOS)


@contextmanager
def escenario(lluvias=False, drones=False):
    anteriores, climas = deepcopy(g.LIMITES), g.CLIMAS
    if lluvias:
        g.CLIMAS = (('despejado', .30), ('lluvia', .55), ('viento_fuerte', .15))
    if drones:
        g.LIMITES['dron'].update(peso_kg=5, volumen_l=25, distancia_km=25)
    try:
        yield
    finally:
        g.LIMITES.clear()
        g.LIMITES.update(anteriores)
        g.CLIMAS = climas


def generar(filas=10000, semilla=42, faltantes=0., lluvias=False, drones=False):
    rng, registros = random.Random(semilla), []
    with escenario(lluvias, drones):
        for i in range(filas):
            p = g.generar_paquete(rng)
            etiqueta = g.recomendar(p, rng, .03)
            fila = {'id_envio': f'ENV-{i+1:06d}', **p, OBJETIVO: etiqueta}
            # Misma secuencia RNG que el script proporcionado, incluso con faltantes=0.
            for campo in g.COLUMNAS_CON_FALTANTES:
                if rng.random() < faltantes:
                    fila[campo] = np.nan
            registros.append(fila)
    return pd.DataFrame(registros)


def es_posible(medio, p, limites=None):
    lim = (limites or LIMITES)[medio]
    if any(p[k] > lim[k] for k in ('peso_kg', 'volumen_l', 'distancia_km')):
        return False
    if p['refrigerado'] and medio != 'camioneta':
        return False
    if medio == 'bicicleta' and p['zona_destino'] == 'rural':
        return False
    if medio == 'dron' and (p['clima'] != 'despejado' or not 6 <= p['hora_salida'] < 21 or p['zona_destino'] == 'centro'):
        return False
    return True


class SinRuido:
    def gauss(self, media, desviacion):
        return media


def costo(medio, paquete):
    return g.puntaje(medio, paquete, SinRuido())


def optimo(paquete, limites=None):
    return min((m for m in MEDIOS if es_posible(m, paquete, limites)), key=lambda m: costo(m, paquete))


def pipeline(tipo='arbol', profundidad=8, balance=None, numericas=None, categoricas=None, imputar=True, min_hoja=5):
    nums = NUMERICAS if numericas is None else numericas
    pasos_n = [('imputar', SimpleImputer(strategy='median'))] if imputar else []
    if tipo == 'red':
        pasos_n.append(('escala', StandardScaler()))
    preparacion = ColumnTransformer([
        ('numericas', Pipeline(pasos_n) if pasos_n else 'passthrough', nums),
        ('categoricas', Pipeline([
            ('imputar', SimpleImputer(strategy='most_frequent')),
            ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False)),
        ]), CATEGORICAS if categoricas is None else categoricas),
    ])
    if tipo == 'bosque':
        estimador = RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1)
    elif tipo == 'red':
        estimador = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=400, early_stopping=True, random_state=42)
    else:
        estimador = DecisionTreeClassifier(max_depth=profundidad, min_samples_leaf=min_hoja, class_weight=balance, random_state=42)
    return Pipeline([('preparacion', preparacion), ('modelo', estimador)])


def separar(datos, semilla=42):
    return train_test_split(datos[CAMPOS], datos[OBJETIVO], test_size=.2, stratify=datos[OBJETIVO], random_state=semilla)


def recomendar(modelo, x, limites=None):
    probabilidades = modelo.predict_proba(x)
    clases = modelo.classes_
    elegidos = []
    for p, probs in zip(x.to_dict('records'), probabilidades):
        ranking = np.argsort(-probs, kind='stable')
        elegidos.append(next((clases[i] for i in ranking if es_posible(clases[i], p, limites)), 'camioneta'))
    return np.asarray(elegidos)


def medir(modelo, x, y):
    pred = modelo.predict(x)
    precision, recall, _, _ = precision_recall_fscore_support(y, pred, labels=['dron'], zero_division=0)
    imposibles = sum(not es_posible(m, p) for m, p in zip(pred, x.to_dict('records')))
    return {'exactitud': float(accuracy_score(y, pred)), 'precision_dron': float(precision[0]),
            'recall_dron': float(recall[0]), 'predice_dron': int((pred == 'dron').sum()), 'imposibles': int(imposibles)}


def preparar():
    DATOS.mkdir(parents=True, exist_ok=True)
    MODELOS.mkdir(exist_ok=True)
    ruta = DATOS / 'envios_medios.csv'
    if not ruta.exists():
        generar().to_csv(ruta, index=False)
    return pd.read_csv(ruta)


def entrenar_todos():
    import sklearn, sys, json
    datos = preparar()
    xe, xp, ye, yp = separar(datos)
    metricas = {}
    for tipo in ('arbol', 'bosque', 'red'):
        print(f'Entrenando {tipo}...', flush=True)
        modelo = pipeline(tipo).fit(xe, ye)
        joblib.dump(modelo, MODELOS / f'modelo_{tipo}.joblib', compress=3)
        metricas[tipo] = medir(modelo, xp, yp)
    metadata = {'python': sys.version, 'sklearn': sklearn.__version__, 'semilla': 42, 'filas': len(datos), 'metricas': metricas}
    (MODELOS / 'metadata.json').write_text(json.dumps(metadata, indent=2), encoding='utf8')
    return metadata
