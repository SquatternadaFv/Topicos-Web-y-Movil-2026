from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from flask import Flask, jsonify, request
from laboratorio.recomendadores import validar, RecomendadorArbol

app = Flask(__name__)


@app.get('/salud')
def salud():
    return jsonify(servicio='recomendar', estado='ok')


@app.post('/sugerir')
def sugerir():
    try:
        cuerpo = request.get_json(silent=True)
        paquete = validar(cuerpo)
        nombre = cuerpo.get('modelo','arbol')
        recomendador = RecomendadorArbol(nombre)
    except (ValueError, TypeError) as error:
        return jsonify(error=str(error),servicio='recomendar'),400
    try:
        return jsonify(servicio='recomendar', **recomendador.sugerir(paquete))
    except (OSError, RuntimeError) as error:
        return jsonify(error=f'Modelo no disponible: {type(error).__name__}',servicio='recomendar'),503


if __name__=='__main__':
    import os
    app.run(host='0.0.0.0',port=int(os.environ.get('PORT','8002')),debug=False)
