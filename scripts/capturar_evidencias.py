"""Ejecuta servicios locales y captura HTTP/UI reales. No simula docker compose ps."""
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import time

import requests
from playwright.sync_api import sync_playwright

RAIZ=Path(__file__).resolve().parents[1]
EVID=RAIZ/'evidencias'/'verificacion'
EXTRA=RAIZ/'Actividad_Extra_Django'/'retos_django'
MICRO=RAIZ/'microservicios-entregas'
PAQUETE={'distancia_km':12.64,'peso_kg':.31,'largo_cm':11.7,'ancho_cm':7.6,'alto_cm':10.6,
 'volumen_l':.94,'fragil':0,'refrigerado':0,'valor_declarado_mxn':4603,'hora_salida':3,
 'prioridad':'mismo_dia','zona_destino':'periferia','clima':'despejado','trafico':'medio'}


def main():
    if not (RAIZ/'practicas_flutter/build/web/index.html').is_file():
        raise SystemExit('Primero compile practicas_flutter: flutter build web --release --no-web-resources-cdn --dart-define=API_BASE=http://127.0.0.1:8000 . Los archivos build no se versionan.')
    EVID.mkdir(parents=True,exist_ok=True)
    procesos=[];logs=[];capturas={}
    session=requests.Session();session.trust_env=False
    def iniciar(nombre,args,cwd=RAIZ,env=None):
        log=(EVID/f'{nombre}.log').open('w',encoding='utf8');logs.append(log)
        p=subprocess.Popen([sys.executable,*args],cwd=cwd,env=env or os.environ.copy(),stdout=log,stderr=log,
                            creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        procesos.append(p)
        return p
    def esperar(url,segundos=30):
        limite=time.monotonic()+segundos
        while time.monotonic()<limite:
            try:
                if session.get(url,timeout=1).status_code<500:return
            except requests.RequestException:pass
            time.sleep(.2)
        raise RuntimeError('No inició '+url)
    def registrar(nombre,r):
        capturas[nombre]={'status':r.status_code,'json':r.json()}
        print(nombre,r.status_code,flush=True)
    for puerto in (8000,18080,18081,18082,18090):
        with socket.socket() as s:
            try:s.bind(('127.0.0.1',puerto))
            except OSError as e:raise RuntimeError(f'Puerto {puerto} ocupado; no se detiene un proceso ajeno.') from e
    try:
      with tempfile.TemporaryDirectory(prefix='topicos-evidencias-') as temp:
        env=os.environ.copy();env['SQLITE_PATH']=str(Path(temp)/'prueba.sqlite3');env['PYTHONUTF8']='1'
        subprocess.run([sys.executable,'manage.py','migrate','--noinput'],cwd=EXTRA,env=env,capture_output=True,check=True)
        iniciar('django',['manage.py','runserver','127.0.0.1:8000','--noreload'],EXTRA,env)
        esperar('http://127.0.0.1:8000/entregas/estado/')
        registrar('estado_django',session.get('http://127.0.0.1:8000/entregas/estado/'))
        registrar('modelo_django',session.post('http://127.0.0.1:8000/entregas/recomendar/',json=PAQUETE))
        for mensaje in ('hola','quiero rastrear el folio','recomienda un medio','cuál es la receta del pastel'):
            registrar('chat_'+mensaje,session.post('http://127.0.0.1:8000/entregas/asistente/',json={'mensaje':mensaje}))
        ed=os.environ.copy();ed['PORT']='18082'
        recomendar=iniciar('recomendar',[str(MICRO/'recomendar/app.py')],env=ed)
        esperar('http://127.0.0.1:18082/salud')
        ep=os.environ.copy();ep.update(PORT='18081',RECOMENDAR_URL='http://127.0.0.1:18082')
        iniciar('pedidos',[str(MICRO/'pedidos/app.py')],env=ep)
        esperar('http://127.0.0.1:18081/salud')
        iniciar('gateway',[str(MICRO/'gateway/local.py')])
        esperar('http://127.0.0.1:18080/')
        for modelo in ('arbol','bosque','red'):
            r=session.post('http://127.0.0.1:18080/pedidos',json={**PAQUETE,'modelo':modelo},timeout=12)
            registrar('micro_'+modelo,r)
            assert r.status_code==201 and r.json()['medio']!='dron'
        invalido={**PAQUETE};invalido.pop('peso_kg')
        r=session.post('http://127.0.0.1:18080/pedidos',json=invalido,timeout=8)
        registrar('micro_invalido',r);assert r.status_code==400
        iniciar('flutter_web',['-m','http.server','18090','--bind','127.0.0.1','--directory',str(RAIZ/'practicas_flutter/build/web')])
        esperar('http://127.0.0.1:18090/')
        with sync_playwright() as play:
          disponibles=list((Path(os.environ.get('LOCALAPPDATA',''))/'ms-playwright').glob('chromium_headless_shell-*/**/chrome-headless-shell.exe'))
          browser=play.chromium.launch(headless=True,**({'executable_path':str(sorted(disponibles)[-1])} if disponibles else {}))
          page=browser.new_page(viewport={'width':1200,'height':950})
          page.goto('http://127.0.0.1:8000/entregas/estado/')
          page.screenshot(path=str(EVID/'01-estado-esta-computadora.png'),full_page=True)
          page.goto('http://127.0.0.1:8000/entregas/modelo/')
          page.get_by_role('button',name='Obtener recomendación').click()
          page.wait_for_function("document.querySelector('#resultado').textContent.includes('medio')")
          page.screenshot(path=str(EVID/'02-modelo-django.png'),full_page=True)
          page.goto('http://127.0.0.1:18080/')
          for modelo in ('arbol','bosque','red'):
            page.select_option('select[name=modelo]',modelo)
            page.get_by_role('button',name='Crear pedido').click()
            page.wait_for_function("document.querySelector('#estado').textContent.includes('201')")
            page.screenshot(path=str(EVID/f'03-micro-{modelo}.png'),full_page=True)
          recomendar.terminate();recomendar.wait(timeout=5)
          r=session.post('http://127.0.0.1:18080/pedidos',json=PAQUETE,timeout=10)
          registrar('micro_recomendar_apagado',r);assert r.status_code==503 and r.json()['plan_b']
          page.get_by_role('button',name='Crear pedido').click()
          page.wait_for_function("document.querySelector('#estado').textContent.includes('Plan B')")
          page.screenshot(path=str(EVID/'04-micro-plan-b.png'),full_page=True)
          page.goto('http://127.0.0.1:18090/')
          page.wait_for_timeout(5000)
          page.screenshot(path=str(EVID/'05-flutter-widgets.png'),full_page=True)
          # Flutter web expone semántica bajo demanda para automatización accesible.
          semantics=page.locator('flt-semantics-placeholder')
          if semantics.count():semantics.evaluate('(e)=>e.click()')
          page.wait_for_timeout(500)
          page.get_by_text('API y chat',exact=False).last.click(timeout=15000)
          page.wait_for_timeout(700)
          page.get_by_role('button',name='Consultar recomendación').click(timeout=15000)
          page.wait_for_timeout(2000)
          page.screenshot(path=str(EVID/'06-flutter-api.png'),full_page=True)
          browser.close()
        capturas['entorno']={'sys_prefix':sys.prefix,'python':sys.version,'docker_disponible':shutil.which('docker') is not None,
                             'tipo_demostracion':'procesos locales HTTP; NO Docker ni nginx'}
        (EVID/'http.json').write_text(json.dumps(capturas,ensure_ascii=False,indent=2),encoding='utf8')
    finally:
        capturas['entorno']={'sys_prefix':sys.prefix,'python':sys.version,'docker_disponible':shutil.which('docker') is not None,
                             'tipo_demostracion':'procesos locales HTTP; NO Docker ni nginx'}
        (EVID/'http.json').write_text(json.dumps(capturas,ensure_ascii=False,indent=2),encoding='utf8')
        for p in procesos:
            if p.poll() is None:p.terminate()
        for p in procesos:
            try:p.wait(timeout=8)
            except subprocess.TimeoutExpired:p.kill();p.wait()
        for log in logs:log.close()
    print('Evidencias reales guardadas en',EVID,flush=True)


if __name__=='__main__':main()
