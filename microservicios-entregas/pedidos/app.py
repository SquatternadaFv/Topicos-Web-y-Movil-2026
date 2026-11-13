"""Pedidos no importa sklearn ni carga modelos; delega por HTTP."""
import os
import uuid
from flask import Flask, jsonify, request
import requests

app=Flask(__name__)
RECOMENDAR_URL=os.environ.get('RECOMENDAR_URL','http://127.0.0.1:8002').rstrip('/')
PEDIDOS={}


@app.get('/salud')
def salud():
    return jsonify(servicio='pedidos',estado='ok',pedidos=len(PEDIDOS))


@app.post('/pedidos')
def crear():
    paquete=request.get_json(silent=True)
    if not isinstance(paquete,dict):
        return jsonify(error='El cuerpo debe ser objeto JSON'),400
    plan_b=False
    try:
        r=requests.post(RECOMENDAR_URL+'/sugerir',json=paquete,timeout=(2,3))
        if r.status_code>=500:
            raise requests.ConnectionError('Recomendar respondió con fallo')
        if r.status_code!=200:
            return jsonify(r.json()),r.status_code
        sugerencia=r.json()
    except (requests.RequestException, ValueError):
        plan_b=True
        sugerencia={'medio':'camioneta','motivo':'Recomendar no disponible; plan B de demostración, requiere revisión operativa',
                    'modelo':None,'confianza':None,'corregido_por_reglas':False,'ranking':[]}
    pedido={'folio':uuid.uuid4().hex[:8].upper(), **sugerencia, 'servicio':'pedidos', 'plan_b':plan_b,
            'recorrido':['gateway','pedidos','recomendar' if not plan_b else 'recomendar no disponible']}
    PEDIDOS[pedido['folio']]=pedido
    return jsonify(pedido),503 if plan_b else 201


@app.get('/pedidos/<folio>')
def detalle(folio):
    if folio not in PEDIDOS:
        return jsonify(error='Pedido no encontrado'),404
    return jsonify(PEDIDOS[folio])


if __name__=='__main__':
    app.run(host='0.0.0.0',port=int(os.environ.get('PORT','8001')),debug=False)
