"""Evidencia complementaria: procesos reales, SIN Docker ni nginx.

Cada proceso ejecuta Django y comparte SQLite. Peticiones secuenciales
dirigidas por turno a puertos distintos; no sustituye el reto Docker.
"""
import http.cookiejar
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import urllib.request

RAIZ = Path(__file__).resolve().parents[1]


def ejecutar():
    salida = []
    def anotar(texto):
        print(texto, flush=True)
        salida.append(texto)
    with tempfile.TemporaryDirectory() as temporal:
        env = os.environ.copy()
        env['SQLITE_PATH'] = str(Path(temporal) / 'compartida.sqlite3')
        env['DJANGO_DEBUG'] = '0'
        subprocess.run([sys.executable, 'manage.py', 'migrate', '--noinput'], cwd=RAIZ, env=env, check=True, capture_output=True)
        anotar('PRUEBA LOCAL COMPLEMENTARIA: procesos independientes, SQLite compartido, sin Docker/nginx/PostgreSQL.')
        for numero, global_malo in [(3, True), (3, False), (5, False)]:
            env['DEMO_ULTIMO_GLOBAL'] = '1' if global_malo else '0'
            procesos = []
            logs = []
            puertos = list(range(8101, 8101 + numero))
            cliente = urllib.request.build_opener(urllib.request.ProxyHandler({}), urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
            try:
                for puerto in puertos:
                    log = open(Path(temporal) / f'{puerto}.log', 'w+')
                    logs.append(log)
                    proceso = subprocess.Popen([sys.executable, 'manage.py', 'runserver', f'127.0.0.1:{puerto}', '--noreload', '--nothreading'], cwd=RAIZ, env=env, stdout=log, stderr=log)
                    procesos.append(proceso)
                for puerto in puertos:
                    limite = time.monotonic() + 15
                    while True:
                        try:
                            with cliente.open(f'http://127.0.0.1:{puerto}/entregas/estado/', timeout=1):
                                break
                        except OSError:
                            if time.monotonic() > limite:
                                for log in logs:
                                    log.seek(0); print(log.read())
                                raise RuntimeError('El servidor no arrancó.')
                            time.sleep(.1)
                anotar(f'\nETAPA: {numero} procesos; almacenamiento={"global" if global_malo else "sesion-db"}')
                def pedir(indice, ruta):
                    puerto = puertos[indice % numero]
                    with cliente.open(f'http://127.0.0.1:{puerto}' + ruta, timeout=5) as r:
                        datos = json.load(r)
                        anotar(f'puerto={puerto} GET {ruta} -> HTTP {r.status} ' + json.dumps(datos, ensure_ascii=False))
                        return datos
                if global_malo:
                    for ruta in ['/entregas/visitas/', '/entregas/visitas-mal/']:
                        for i in range(6):
                            datos = pedir(i, ruta)
                            if ruta == '/entregas/visitas/':
                                assert datos['visitas'] == i + 1
                pedir(0, '/entregas/ultimo/?folio=ABC123')
                resultados = [pedir(i, '/entregas/ultimo/ver/') for i in range(numero * 2)]
                if global_malo:
                    assert any(d['folio'] is None for d in resultados)
                    anotar('FALLO OBSERVADO: solo el proceso que escribió recuerda ABC123.')
                else:
                    assert all(d['folio'] == 'ABC123' for d in resultados)
                    assert len({d['proceso'] for d in resultados}) == numero
                    anotar(f'OK: {numero} procesos devolvieron ABC123 con la misma cookie.')
            finally:
                for proceso in procesos:
                    proceso.terminate()
                for proceso in procesos:
                    try:
                        proceso.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        proceso.kill(); proceso.wait()
                for log in logs:
                    log.close()
    (RAIZ / 'evidencias/replicas_locales.txt').write_text('\n'.join(salida) + '\n', encoding='utf-8')


if __name__ == '__main__':
    ejecutar()
