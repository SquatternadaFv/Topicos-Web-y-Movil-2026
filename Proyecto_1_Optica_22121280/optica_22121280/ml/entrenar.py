"""Replica la tubería de los apuntes: preparar -> dividir -> fit -> evaluar -> joblib."""
import hashlib
import json
from pathlib import Path
import joblib
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'ml/datos/perfiles_optica.csv'
SALIDA = ROOT / 'backend/optica/modelo'
NUMERICAS = ['horas_pantalla', 'horas_exterior', 'presupuesto', 'prefiere_fotocromatico']
CATEGORICAS = ['uso_principal']

def entrenar():
    datos = pd.read_csv(DATA)
    x, y = datos[NUMERICAS + CATEGORICAS], datos['paquete']
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=.2, stratify=y, random_state=42)
    pipeline = Pipeline([
        ('preparacion', ColumnTransformer([('numericas', 'passthrough', NUMERICAS), ('categoricas', OneHotEncoder(handle_unknown='ignore'), CATEGORICAS)])),
        ('arbol', DecisionTreeClassifier(max_depth=6, min_samples_leaf=12, random_state=42)),
    ])
    pipeline.fit(x_train, y_train)
    pred = pipeline.predict(x_test)
    version = 'optica-v1-' + hashlib.sha256(DATA.read_bytes()).hexdigest()[:12]
    metricas = {'version': version, 'sklearn': sklearn.__version__, 'origen': 'sintético; no validación clínica ni evidencia de eficacia', 'filas': len(datos), 'entrenamiento': len(x_train), 'prueba': len(x_test), 'semilla_split': 42, 'accuracy': accuracy_score(y_test, pred), 'clases': pipeline.classes_.tolist(), 'matriz_confusion': confusion_matrix(y_test, pred, labels=pipeline.classes_).tolist(), 'reporte': classification_report(y_test, pred, output_dict=True, zero_division=0)}
    SALIDA.mkdir(parents=True, exist_ok=True)
    joblib.dump({'pipeline': pipeline, 'version': version, 'sklearn': sklearn.__version__}, SALIDA / 'modelo_optica.joblib')
    (ROOT / 'ml/metricas.json').write_text(json.dumps(metricas, ensure_ascii=False, indent=2), encoding='utf-8')
    nombres = pipeline.named_steps['preparacion'].get_feature_names_out().tolist()
    (ROOT / 'ml/arbol.txt').write_text(export_text(pipeline.named_steps['arbol'], feature_names=nombres), encoding='utf-8')
    print(f'Accuracy prueba sintética: {metricas["accuracy"]:.4f}; {len(x_test)} perfiles. Modelo: {version}')
    print(classification_report(y_test, pred, zero_division=0))

if __name__ == '__main__':
    entrenar()
