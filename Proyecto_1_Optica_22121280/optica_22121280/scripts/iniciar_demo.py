"""Sirve la build Flutter y Django localmente. Detener con Ctrl+C.

No instala dependencias, no altera el catálogo y no usa servicios externos.
"""
from functools import partial
import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen
import webbrowser

ROOT = Path(__file__).resolve().parents[1]


def api_disponible():
    try:
        with urlopen('http://127.0.0.1:8000/api/salud/', timeout=1) as response:
            return json.load(response).get('proyecto') == 'Optica 22121280'
    except (URLError, ValueError, OSError):
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sin-navegador', action='store_true', help='Iniciar sin abrir una ventana del navegador.')
    args = parser.parse_args()
    web = ROOT / 'flutter_app/build/web'
    if not (web / 'index.html').exists():
        print('Falta compilar Flutter web. Consulta README.md: Inicio rápido.')
        return 1
    try:
        server = ThreadingHTTPServer(
            ('127.0.0.1', 5173), partial(SimpleHTTPRequestHandler, directory=str(web))
        )
    except OSError:
        print('El puerto 5173 está ocupado. Cierra la demo anterior antes de reiniciarla.')
        return 1
    backend = None
    log = None
    try:
        if not api_disponible():
            log_dir = ROOT / '.logs'
            log_dir.mkdir(exist_ok=True)
            log = (log_dir / 'django.log').open('a', encoding='utf-8')
            backend = subprocess.Popen(
                [sys.executable, str(ROOT / 'backend/manage.py'), 'runserver', '127.0.0.1:8000', '--noreload'],
                cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
            )
            for _ in range(60):
                if api_disponible():
                    break
                if backend.poll() is not None:
                    raise RuntimeError('Django no inició. Revisa .logs/django.log y la instalación del README.')
                time.sleep(.25)
            else:
                raise RuntimeError('Django no respondió. Revisa .logs/django.log y el puerto 8000.')
        print('Lúmina Óptica: http://127.0.0.1:5173')
        print('API: http://127.0.0.1:8000/api/catalogo/')
        print('Mantén esta terminal abierta. Ctrl+C detiene la demo.')
        if not args.sin_navegador:
            webbrowser.open('http://127.0.0.1:5173')
        server.serve_forever(poll_interval=.25)
    except KeyboardInterrupt:
        print('\nDemo detenida.')
    except (OSError, RuntimeError) as exc:
        print(str(exc))
        return 1
    finally:
        server.server_close()
        if backend is not None:
            backend.terminate()
            try:
                backend.wait(timeout=5)
            except subprocess.TimeoutExpired:
                backend.kill()
                backend.wait()
        if log is not None:
            log.close()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
