"""Contraste real entre procesos; evidencia complementaria, NO Docker."""
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import requests

RAIZ=Path(__file__).resolve().parents[1]
DJANGO=RAIZ/'Actividad_Extra_Django/retos_django'


def main():
    salidas=['Prueba local: procesos Python independientes y SQLite compartido. NO Docker, nginx ni PostgreSQL.']
    with tempfile.TemporaryDirectory(prefix='topicos-borrador-') as temp:
        env=os.environ.copy();env['SQLITE_PATH']=str(Path(temp)/'compartida.sqlite3')
        subprocess.run([sys.executable,'manage.py','migrate','--noinput'],cwd=DJANGO,env=env,capture_output=True,check=True)
        for numero,global_malo in ((3,True),(3,False),(5,False)):
            env['DEMO_BORRADOR_GLOBAL']='1' if global_malo else '0'
            procesos=[];logs=[]
            clientes=[requests.Session(),requests.Session()]
            for c in clientes:c.trust_env=False
            puertos=[]
            while len(puertos)<numero:
                with socket.socket() as libre:
                    libre.bind(('127.0.0.1',0));puerto=libre.getsockname()[1]
                if puerto not in puertos:puertos.append(puerto)
            try:
                for puerto in puertos:
                    with socket.socket() as s:s.bind(('127.0.0.1',puerto))
                    log=open(Path(temp)/f'{puerto}.log','w',encoding='utf8');logs.append(log)
                    procesos.append(subprocess.Popen([sys.executable,'manage.py','runserver',f'127.0.0.1:{puerto}','--noreload','--nothreading'],cwd=DJANGO,env=env,stdout=log,stderr=log,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0)))
                for puerto in puertos:
                    limite=time.monotonic()+30
                    while True:
                        try:
                            if clientes[0].get(f'http://127.0.0.1:{puerto}/entregas/estado/',timeout=1).status_code==200:break
                        except requests.RequestException:pass
                        if time.monotonic()>limite:raise RuntimeError('Servidor no disponible')
                        time.sleep(.2)
                salidas.append(f'\n{numero} procesos; destino en '+('global' if global_malo else 'sesión DB'))
                c=clientes[0]
                r=c.get(f'http://127.0.0.1:{puertos[0]}/entregas/borrador/destino/',params={'destino':'Primer destino'})
                salidas.append('GUARDAR '+str(r.status_code)+' '+r.text)
                r=c.get(f'http://127.0.0.1:{puertos[1]}/entregas/borrador/confirmar/')
                salidas.append('CONFIRMAR EN OTRA COPIA '+str(r.status_code)+' '+r.text)
                assert r.status_code==(400 if global_malo else 201)
                if not global_malo:
                    for i in range(numero):
                        for k,cliente in enumerate(clientes):
                            cliente.get(f'http://127.0.0.1:{puertos[i]}/entregas/borrador/destino/',params={'destino':f'Cliente {k} vuelta {i}'})
                        for k,cliente in enumerate(clientes):
                            r=cliente.get(f'http://127.0.0.1:{puertos[(i+1)%numero]}/entregas/borrador/confirmar/')
                            assert r.status_code==201 and r.json()['destino']==f'Cliente {k} vuelta {i}'
                            salidas.append('CONFIRMAR AISLADO '+str(r.status_code)+' '+r.text)
            finally:
                for p in procesos:p.terminate()
                for p in procesos:
                    try:p.wait(timeout=5)
                    except subprocess.TimeoutExpired:p.kill();p.wait()
                for log in logs:log.close()
    out=RAIZ/'evidencias/verificacion/borrador_local.txt';out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text('\n'.join(salidas)+'\n',encoding='utf8')
    print('\n'.join(salidas))


if __name__=='__main__':main()
