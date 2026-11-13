"""Ejecuta el reto 4 real en una computadora con Docker Compose v2.

Desde la raíz: python scripts/reto4_docker.py
Requiere puerto 8000 libre. Deja cinco copias con la versión corregida.
"""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import urllib.request
import uuid

RAIZ = Path(__file__).resolve().parents[1]
EVIDENCIAS = RAIZ / 'evidencias'


def main():
    if not shutil.which('docker'):
        raise SystemExit('Docker no está instalado. Instale/inicie Docker Desktop o Docker Engine + Compose v2.')
    env = os.environ.copy()
    EVIDENCIAS.mkdir(exist_ok=True)
    def ejecutar(argumentos, nombre):
        print('Ejecutando:', ' '.join(argumentos), flush=True)
        resultado = subprocess.run(argumentos, cwd=RAIZ, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace')
        texto = '$ ' + ' '.join(argumentos) + '\n' + resultado.stdout + resultado.stderr
        (EVIDENCIAS / nombre).write_text(texto, encoding='utf-8')
        if resultado.returncode:
            raise SystemExit(f'Falló el comando. Revise evidencias/{nombre}; se conservó la salida real.')
    def esperar():
        cliente = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        limite = time.monotonic() + 30
        while time.monotonic() < limite:
            try:
                with cliente.open('http://127.0.0.1:8000/entregas/estado/', timeout=2):
                    return
            except OSError:
                time.sleep(.5)
        raise SystemExit('El backend no respondió en 30 s. Revise docker compose ps y docker compose logs.')
    ejecutar(['docker', 'compose', 'version'], 'docker_version.txt')
    # Etapas 4 y 5: imagen, PostgreSQL, migración única, nginx y tres copias.
    env['DEMO_ULTIMO_GLOBAL'] = '1'
    ejecutar(['docker', 'build', '-f', 'Dockerfile', '-t', 'plataforma-entregas-extra', '../..'], 'docker_build.txt')
    # Paso 12: comprobar primero una imagen ejecutándose sola.
    contenedor = 'entregas-extra-etapa4-' + uuid.uuid4().hex[:8]
    ejecutar(['docker', 'run', '-d', '--rm', '--name', contenedor, '-p', '8000:8000', 'plataforma-entregas-extra', 'sh', '-c', 'python manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2'], 'docker_copia_unica.txt')
    try:
        esperar()
        cliente = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with cliente.open('http://127.0.0.1:8000/entregas/estado/', timeout=5) as respuesta:
            texto = f'GET /entregas/estado/ -> HTTP {respuesta.status}\n' + respuesta.read().decode('utf-8') + '\n'
            (EVIDENCIAS / 'docker_estado_unico.txt').write_text(texto, encoding='utf-8')
    finally:
        ejecutar(['docker', 'stop', contenedor], 'docker_detener_copia_unica.txt')
    ejecutar(['docker', 'compose', 'up', '-d', '--build', '--scale', 'web=3'], 'docker_arranque_3.txt')
    ejecutar(['docker', 'compose', 'exec', '-T', 'balanceador', 'nginx', '-s', 'reload'], 'docker_reload_global.txt')
    esperar()
    ejecutar(['docker', 'compose', 'ps'], 'docker_ps_global_3.txt')
    ejecutar([sys.executable, 'scripts/capturar_http.py', '--modo', 'contador'], 'docker_contadores_3.txt')
    ejecutar([sys.executable, 'scripts/capturar_http.py', '--modo', 'global', '--numero', '30', '--min-copias', '3'], 'docker_global_3.txt')
    # Mismas rutas, ahora con sesión en PostgreSQL. El default del código es 0.
    env['DEMO_ULTIMO_GLOBAL'] = '0'
    ejecutar(['docker', 'compose', 'up', '-d', '--no-deps', '--force-recreate', '--scale', 'web=3', 'web'], 'docker_arreglo_3.txt')
    ejecutar(['docker', 'compose', 'exec', '-T', 'balanceador', 'nginx', '-s', 'reload'], 'docker_reload_sesion_3.txt')
    esperar()
    ejecutar(['docker', 'compose', 'ps'], 'docker_ps_sesion_3.txt')
    ejecutar([sys.executable, 'scripts/capturar_http.py', '--modo', 'sesion', '--numero', '30', '--min-copias', '3'], 'docker_sesion_3.txt')
    ejecutar(['docker', 'compose', 'up', '-d', '--scale', 'web=5'], 'docker_escalado_5.txt')
    ejecutar(['docker', 'compose', 'exec', '-T', 'balanceador', 'nginx', '-s', 'reload'], 'docker_reload_sesion_5.txt')
    esperar()
    ejecutar(['docker', 'compose', 'ps'], 'docker_ps_sesion_5.txt')
    ejecutar([sys.executable, 'scripts/capturar_http.py', '--modo', 'sesion', '--numero', '60', '--min-copias', '5'], 'docker_sesion_5.txt')
    nombres = ['docker_version.txt', 'docker_build.txt', 'docker_copia_unica.txt', 'docker_estado_unico.txt', 'docker_ps_global_3.txt', 'docker_contadores_3.txt', 'docker_global_3.txt', 'docker_ps_sesion_3.txt', 'docker_sesion_3.txt', 'docker_escalado_5.txt', 'docker_ps_sesion_5.txt', 'docker_sesion_5.txt']
    bloque = 'Ejecución Docker completada en esta computadora. Salidas capturadas sin modificar:\n\n'
    for nombre in nombres:
        bloque += f'### {nombre}\n\n```text\n{(EVIDENCIAS / nombre).read_text(encoding="utf-8").rstrip()}\n```\n\n'
    extra = RAIZ / 'EXTRA.md'
    texto = extra.read_text(encoding='utf-8')
    inicio, fin = '<!-- DOCKER_EVIDENCIAS_INICIO -->', '<!-- DOCKER_EVIDENCIAS_FIN -->'
    antes, resto = texto.split(inicio, 1)
    _, despues = resto.split(fin, 1)
    actualizado = antes + inicio + '\n\n' + bloque + fin + despues
    actualizado = actualizado.replace(
        '| 4 | Código y configuración Docker preparados; fallo/arreglo probados con procesos locales | Ejecutar Docker con tres y cinco contenedores y guardar las salidas |',
        '| 4 | Ejecutado con Docker: fallo global y arreglo con tres y cinco copias; salidas incorporadas abajo | Revisar las salidas y poder repetir la demostración |',
    )
    actualizado = actualizado.replace('### Evidencias Docker obligatorias — pendientes', '### Evidencias Docker obligatorias — ejecución completada')
    extra.write_text(actualizado, encoding='utf-8')
    print('Reto 4 ejecutado; evidencia Docker incorporada en EXTRA.md. Revise las salidas antes de entregar.')


if __name__ == '__main__':
    main()
