"""Demuestra el cambio 3 -> 6 km y deja el código con el límite final de 6.

Requiere instalar playwright y Chromium solo para generar las capturas;
la aplicación y el cliente móvil no los necesitan.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.error
import urllib.request

RAIZ = Path(__file__).resolve().parents[1]


def main():
    from playwright.sync_api import sync_playwright
    parser = argparse.ArgumentParser()
    parser.add_argument('--chromium', default=None)
    args = parser.parse_args()
    reglas = RAIZ / 'entregas/reglas.py'
    clientes = [RAIZ / 'cliente_movil.py', RAIZ / 'entregas/templates/entregas/cotizador.html']
    hashes = {str(p.relative_to(RAIZ)): hashlib.sha256(p.read_bytes()).hexdigest() for p in clientes}
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=args.chromium, headless=True, args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu'])
        try:
            for etiqueta, limite, esperado in [('antes', 3.0, 'moto'), ('despues', 6.0, 'bicicleta')]:
                lineas = reglas.read_text(encoding='utf-8').splitlines()
                reglas.write_text('\n'.join(f'LIMITE_BICICLETA_KM = {limite}' if l.startswith('LIMITE_BICICLETA_KM =') else l for l in lineas) + '\n', encoding='utf-8')
                # Evitar reutilizar bytecode al cambiar dos constantes del mismo tamaño.
                for cache in (RAIZ / 'entregas/__pycache__').glob('reglas*.pyc'):
                    cache.unlink()
                log = open(RAIZ / f'evidencias/servidor_{etiqueta}.txt', 'w', encoding='utf-8')
                servidor = subprocess.Popen([sys.executable, '-u', 'manage.py', 'runserver', '127.0.0.1:8000', '--noreload'], cwd=RAIZ, stdout=log, stderr=log)
                try:
                    limite_tiempo = time.monotonic() + 15
                    while True:
                        try:
                            with opener.open('http://127.0.0.1:8000/entregas/estado/', timeout=1):
                                break
                        except OSError:
                            if time.monotonic() > limite_tiempo:
                                raise RuntimeError('El servidor no arrancó. Revise evidencias/servidor_' + etiqueta + '.txt')
                            time.sleep(.1)
                    pagina = browser.new_page(viewport={'width': 1100, 'height': 760}, device_scale_factor=1)
                    pagina.goto('http://127.0.0.1:8000/entregas/cotizador/')
                    navegaciones = []
                    pagina.on('framenavigated', lambda frame: navegaciones.append(frame.url))
                    with pagina.expect_response(lambda r: '/entregas/cotizar/' in r.url) as respuesta:
                        pagina.locator('#boton').click()
                    datos = respuesta.value.json()
                    pagina.locator('#resultado').wait_for(state='visible')
                    assert pagina.locator('#medio').inner_text() == esperado
                    assert respuesta.value.status == 200
                    assert not navegaciones, 'El formulario recargó la página.'
                    pagina.screenshot(path=str(RAIZ / f'evidencias/web_{etiqueta}.png'), full_page=True)
                    salida_movil = subprocess.run([sys.executable, 'cliente_movil.py'], cwd=RAIZ, capture_output=True, text=True, check=True).stdout
                    texto = f'LIMITE_BICICLETA_KM = {limite}\nWEB fetch -> HTTP 200 ' + json.dumps(datos, ensure_ascii=False) + '\nNavegaciones al consultar: 0\n\n' + salida_movil
                    (RAIZ / f'evidencias/reto3_{etiqueta}.txt').write_text(texto, encoding='utf-8')
                    print(texto, flush=True)
                    # Error devuelto por el backend visible incluso al omitir validación HTML.
                    pagina.locator('#km').evaluate("e => {e.type = 'text'; e.value = 'abc';}")
                    with pagina.expect_response(lambda r: '/entregas/cotizar/' in r.url) as error:
                        pagina.locator('#boton').click()
                    assert error.value.status == 400
                    assert pagina.locator('#error').inner_text()
                    assert pagina.locator('#resultado').is_hidden()
                    pagina.close()
                    if etiqueta == 'despues':
                        evidencias = []
                        for consulta in ['?km=5&kg=2', '?kg=2', '?km=abc&kg=2', '?km=-1&kg=2', '?km=NaN&kg=2', '?km=5&kg=-2']:
                            url = 'http://127.0.0.1:8000/entregas/cotizar/' + consulta
                            try:
                                respuesta_http = opener.open(url, timeout=5)
                            except urllib.error.HTTPError as e:
                                respuesta_http = e
                            with respuesta_http as r:
                                evidencias.append(f'GET {url}\nHTTP {r.status}\n' + json.dumps(json.load(r), ensure_ascii=False))
                        (RAIZ / 'evidencias/reto2_http.txt').write_text('\n\n'.join(evidencias) + '\n', encoding='utf-8')
                finally:
                    servidor.terminate()
                    servidor.wait(timeout=5)
                    log.close()
            hashes_despues = {str(p.relative_to(RAIZ)): hashlib.sha256(p.read_bytes()).hexdigest() for p in clientes}
            assert hashes == hashes_despues, 'Se modificó un cliente.'
            (RAIZ / 'evidencias/clientes_sin_cambios.txt').write_text('SHA-256 antes = después.\n' + json.dumps(hashes, indent=2) + '\n', encoding='utf-8')
        finally:
            browser.close()


if __name__ == '__main__':
    main()
