import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import joblib
import pandas as pd
from sklearn.metrics import classification_report
from sklearn.tree import export_text
from laboratorio.base import preparar, pipeline, separar

if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--datos',type=Path)
    p.add_argument('--profundidad',type=int,default=8)
    p.add_argument('--salida',type=Path,default=Path(__file__).parent/'modelos'/'modelo_arbol.joblib')
    a=p.parse_args()
    datos=pd.read_csv(a.datos) if a.datos else preparar()
    xe,xp,ye,yp=separar(datos)
    modelo=pipeline(profundidad=a.profundidad).fit(xe,ye)
    print(classification_report(yp,modelo.predict(xp),zero_division=0))
    print(export_text(modelo.named_steps['modelo'],feature_names=list(modelo.named_steps['preparacion'].get_feature_names_out()),max_depth=1000))
    a.salida.parent.mkdir(parents=True,exist_ok=True)
    joblib.dump(modelo,a.salida,compress=3)
