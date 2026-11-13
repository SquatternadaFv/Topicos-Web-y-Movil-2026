"""Reto actual: pedidos DB/memoria y borrador por sesión con 3/5 contenedores."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import requests

ROOT=Path(__file__).resolve().parents[1]
PROYECTO=ROOT/'Actividad_Extra_Django/retos_django'
OUT=ROOT/'evidencias/verificacion/reto4_docker'


def main():
    if not shutil.which('docker'):
        raise SystemExit('Docker no está instalado. Se conserva evidencia local separada; este script requiere Docker real.')
    OUT.mkdir(parents=True,exist_ok=True)
    env=os.environ.copy()
    comandos=['docker','compose','-p','topicos-extra-22121280']
    contador=0
    def cmd(args):
        nonlocal contador
        contador+=1
        r=subprocess.run(comandos+args,cwd=PROYECTO,env=env,capture_output=True,text=True,encoding='utf8',errors='replace')
        (OUT/f'{contador:02d}_comando.txt').write_text('$ '+' '.join(comandos+args)+'\n'+r.stdout+r.stderr,encoding='utf8')
        if r.returncode:raise RuntimeError('Falló Docker. Ver salida real en '+str(OUT))
        return r.stdout
    def esperar():
        limite=time.monotonic()+60
        while time.monotonic()<limite:
            try:
                if requests.get('http://127.0.0.1:8000/entregas/estado/',timeout=2).status_code==200:return
            except requests.RequestException:pass
            time.sleep(.5)
        raise RuntimeError('La plataforma no está disponible; revisar compose logs')
    def pedir(cliente,ruta,**params):
        r=cliente.get('http://127.0.0.1:8000'+ruta,params=params,timeout=10)
        return {'ruta':ruta,'parametros':params,'status':r.status_code,'json':r.json()}
    resultados=[]
    env['DEMO_BORRADOR_GLOBAL']='1'
    cmd(['up','-d','--build','--scale','web=3']);esperar()
    cmd(['exec','-T','balanceador','nginx','-s','reload'])
    cmd(['ps'])
    c=requests.Session();c.trust_env=False
    for mala in (False,True):
        ruta='/entregas/pedidos-mal/' if mala else '/entregas/pedidos/'
        alta=pedir(c,ruta,destino='Paso 18');resultados.append(alta)
        resultados.extend(pedir(c,ruta,folio=alta['json']['folio']) for _ in range(12))
    fallos=0
    for i in range(30):
        destino=f'Destino global {i}'
        resultados.append(pedir(c,'/entregas/borrador/destino/',destino=destino))
        r=pedir(c,'/entregas/borrador/confirmar/');resultados.append(r)
        fallos+=r['status']!=201 or r['json'].get('destino')!=destino
    if not fallos:raise RuntimeError('No se observó el fallo global. Repetir y revisar balanceo; no inventar la evidencia.')
    for numero in (3,5):
        env['DEMO_BORRADOR_GLOBAL']='0'
        cmd(['up','-d','--force-recreate','--scale',f'web={numero}','web'])
        cmd(['exec','-T','balanceador','nginx','-s','reload']);esperar();cmd(['ps'])
        clientes=[requests.Session(),requests.Session()]
        vistos=set()
        for i in range(30):
            for k,cli in enumerate(clientes):
                cli.trust_env=False
                resultados.append(pedir(cli,'/entregas/borrador/destino/',destino=f'Cliente {k}, intento {i}'))
            for k,cli in enumerate(clientes):
                r=pedir(cli,'/entregas/borrador/confirmar/');resultados.append(r)
                assert r['status']==201 and r['json']['destino']==f'Cliente {k}, intento {i}'
                vistos.add(r['json']['atendido_por'])
        if len(vistos)<numero:raise RuntimeError(f'Solo se observaron {len(vistos)} copias; se requerían {numero}.')
        resultados.append({'etapa':f'{numero} copias corregidas','copias_observadas':sorted(vistos)})
    (OUT/'http.json').write_text(json.dumps(resultados,ensure_ascii=False,indent=2),encoding='utf8')
    print('Prueba Docker real completada; evidencia en',OUT)
    print('Los servicios de demostración siguen activos. Detener con docker compose -p topicos-extra-22121280 down desde',PROYECTO)


if __name__=='__main__':main()
