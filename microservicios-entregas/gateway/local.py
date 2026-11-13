"""Proxy alternativo para comprobar HTTP local sin afirmar ejecución Docker/nginx."""
from pathlib import Path
import os
from flask import Flask, Response, send_from_directory, request
import requests

app=Flask(__name__)
HTML=Path(__file__).parent/'html'
PEDIDOS=os.environ.get('PEDIDOS_URL','http://127.0.0.1:18081')
RECOMENDAR=os.environ.get('RECOMENDAR_URL','http://127.0.0.1:18082')


@app.get('/')
def index():
    return send_from_directory(HTML,'index.html')


@app.route('/pedidos',methods=['GET','POST'])
@app.get('/pedidos/<folio>')
@app.get('/salud/pedidos')
@app.get('/salud/recomendar')
def proxy(folio=None):
    destino=(RECOMENDAR if request.path.endswith('/recomendar') else PEDIDOS)
    ruta='/salud' if request.path.startswith('/salud/') else request.path
    try:
        r=requests.request(request.method,destino+ruta,data=request.get_data(),headers={'Content-Type':request.content_type or 'application/json'},timeout=8)
        return Response(r.content,status=r.status_code,content_type=r.headers.get('Content-Type','application/json'))
    except requests.RequestException:
        return {'error':'Servicio no disponible'},503


if __name__=='__main__':
    app.run(host='127.0.0.1',port=int(os.environ.get('PORT','18080')),debug=False)
