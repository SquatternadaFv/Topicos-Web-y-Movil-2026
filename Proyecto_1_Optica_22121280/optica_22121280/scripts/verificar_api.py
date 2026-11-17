"""Prueba reproducible contra el servidor en ejecución; usa solo biblioteca estándar."""
import json
import sys
import urllib.request
import urllib.error
import uuid
BASE = (sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8000/api').rstrip('/')
PERFIL = dict(horas_pantalla=8, horas_exterior=1, presupuesto=700, uso_principal='oficina', prefiere_fotocromatico=False)
def llamar(ruta, datos=None, clave=None):
    headers = {'Content-Type': 'application/json'}
    if clave:
        headers['Idempotency-Key'] = clave
    request = urllib.request.Request(BASE + ruta, data=json.dumps(datos).encode() if datos is not None else None, headers=headers)
    with urllib.request.urlopen(request) as r:
        return r.status, json.load(r)
_, resultado = llamar('/recomendaciones/', PERFIL)
assert resultado['corregido'] and resultado['paquete']['codigo'] == 'esencial'
clave = str(uuid.uuid4())
status, orden = llamar('/ordenes/', PERFIL, clave)
repetido, copia = llamar('/ordenes/', PERFIL, clave)
assert status == 201 and repetido == 200 and copia['folio'] == orden['folio']
_, consulta = llamar('/ordenes/' + orden['folio'] + '/')
assert consulta['precio_confirmado'] == '650.00'
print(json.dumps({'original': resultado['original'], 'final': resultado['paquete']['codigo'], 'corregido': resultado['corregido'], 'folio': consulta['folio'], 'idempotencia': '201 -> 200, mismo folio'}, ensure_ascii=False, indent=2))
