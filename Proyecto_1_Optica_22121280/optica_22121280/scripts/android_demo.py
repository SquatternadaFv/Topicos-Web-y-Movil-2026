"""Instala el APK local y conecta Android al mismo Django mediante adb reverse.

Requiere Android autorizado por USB o emulador encendido. No modifica redes,
firewall, BIOS ni configuración del hipervisor.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = 'mx.edu.itm.optica_app'


def adb_executable():
    sdk = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
    if not sdk:
        local = os.environ.get('LOCALAPPDATA')
        if local:
            sdk = str(Path(local) / 'Android/Sdk')
    if sdk:
        archivo = Path(sdk) / 'platform-tools' / ('adb.exe' if os.name == 'nt' else 'adb')
        if archivo.is_file():
            return str(archivo)
    import shutil
    return shutil.which('adb')


def api_disponible():
    try:
        with urlopen('http://127.0.0.1:8000/api/salud/', timeout=2) as r:
            return json.load(r).get('proyecto') == 'Optica 22121280'
    except (URLError, OSError, ValueError):
        return False


def dispositivos(adb):
    salida = subprocess.run([adb, 'devices'], check=True, capture_output=True, text=True, timeout=10).stdout
    estados = [line.split()[:2] for line in salida.splitlines()[1:] if len(line.split()) >= 2]
    return salida, [serial for serial, estado in estados if estado == 'device']


def iniciar_emulador(adb, nombre=None):
    emulator = Path(adb).parent.parent / 'emulator' / ('emulator.exe' if os.name == 'nt' else 'emulator')
    if not emulator.is_file():
        raise RuntimeError('Falta Android Emulator en el SDK. Instálalo desde Android Studio.')
    aceleracion = subprocess.run([str(emulator), '-accel-check'], capture_output=True, text=True, timeout=15)
    if aceleracion.returncode:
        raise RuntimeError('El emulador necesita aceleración de virtualización.\n' + aceleracion.stdout + aceleracion.stderr)
    avds = subprocess.run([str(emulator), '-list-avds'], check=True, capture_output=True, text=True, timeout=15).stdout.splitlines()
    avds = [x.strip() for x in avds if x.strip()]
    if nombre and nombre not in avds:
        raise RuntimeError(f'No existe el emulador {nombre}. Disponibles: {avds}')
    if not nombre:
        if len(avds) != 1:
            raise RuntimeError(f'Elige uno con --emulador NOMBRE. Disponibles: {avds}')
        nombre = avds[0]
    logs = ROOT / '.logs'
    logs.mkdir(exist_ok=True)
    print(f'Iniciando {nombre}; el primer arranque puede tardar unos minutos.', flush=True)
    with (logs / 'emulador-android.log').open('a', encoding='utf8') as log:
        proceso = subprocess.Popen(
            [str(emulator), '-avd', nombre, '-no-snapshot-load', '-no-snapshot-save', '-gpu', 'host'],
            stdout=log, stderr=subprocess.STDOUT,
        )
        for intento in range(90):
            _, conectados = dispositivos(adb)
            emulados = [s for s in conectados if s.startswith('emulator-')]
            for serial in emulados:
                boot = subprocess.run([adb, '-s', serial, 'shell', 'getprop', 'sys.boot_completed'], capture_output=True, text=True, timeout=10)
                if boot.returncode == 0 and boot.stdout.strip() == '1':
                    return serial
            if proceso.poll() not in (None, 0):
                raise RuntimeError('El emulador terminó con error. Revisa .logs/emulador-android.log.')
            if intento % 10 == 0:
                print('Esperando a que Android termine de arrancar...', flush=True)
            time.sleep(2)
    raise RuntimeError('Android no terminó de arrancar. Revisa el emulador y .logs/emulador-android.log.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--serial', help='Identificador mostrado por adb devices si hay varios dispositivos.')
    parser.add_argument('--iniciar-emulador', action='store_true', help='Abrir un AVD si no hay un Android conectado.')
    parser.add_argument('--emulador', help='Nombre del AVD para --iniciar-emulador.')
    parser.add_argument('--apk', type=Path, default=ROOT / 'entrega_android/Lumina-Optica-P1-P2.apk')
    args = parser.parse_args()
    adb = adb_executable()
    if not adb:
        print('Falta adb. Instala Android SDK Platform-Tools o configura ANDROID_HOME.')
        return 1
    apk = args.apk.resolve()
    if not apk.is_file():
        print(f'No se encontró el APK: {apk}. Consulta entrega_android/LEEME.md para compilarlo.')
        return 1
    output, conectados = dispositivos(adb)
    if not conectados and args.iniciar_emulador:
        try:
            serial_emulado = iniciar_emulador(adb, args.emulador)
            output, conectados = dispositivos(adb)
            if not args.serial:
                args.serial = serial_emulado
        except (OSError, RuntimeError, subprocess.SubprocessError) as error:
            print(str(error))
            return 1
    serial = args.serial
    if serial and serial not in conectados:
        print(f'El dispositivo {serial} no está conectado y autorizado.\n{output}')
        return 1
    if not serial:
        if not conectados:
            print('Conecta un Android por USB, activa depuración USB y acepta la huella de esta computadora.')
            print('También puedes abrir un emulador Android. Después vuelve a ejecutar este acceso.')
            print(output)
            return 1
        if len(conectados) > 1:
            print('Hay varios Android. Ejecuta con --serial IDENTIFICADOR para elegir.\n' + output)
            return 1
        serial = conectados[0]
    backend = None
    log = None
    try:
        if not api_disponible():
            carpeta_log = ROOT / '.logs'
            carpeta_log.mkdir(exist_ok=True)
            log = (carpeta_log / 'django-android.log').open('a', encoding='utf8')
            backend = subprocess.Popen(
                [sys.executable, str(ROOT / 'backend/manage.py'), 'runserver', '127.0.0.1:8000', '--noreload'],
                cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
            )
            for _ in range(60):
                if api_disponible():
                    break
                if backend.poll() is not None:
                    raise RuntimeError('Django no inició. Revisa .logs/django-android.log y el puerto 8000.')
                time.sleep(.25)
            else:
                raise RuntimeError('Django no respondió. Revisa su entorno y base de datos en el README.')
        base = [adb, '-s', serial]
        subprocess.run(base + ['install', '-r', str(apk)], check=True)
        # Algunos teléfonos reinician la conexión USB al instalar el APK.
        # Configurar el túnel después evita perderlo durante esa instalación.
        subprocess.run(base + ['reverse', 'tcp:8000', 'tcp:8000'], check=True)
        subprocess.run(base + ['shell', 'am', 'start', '-n', PACKAGE + '/.MainActivity'], check=True)
        print('\nLúmina P1 + P2 instalada y abierta en ' + serial)
        print('La app usa el mismo Django y SQLite que la web. Mantén activo el emulador o la conexión USB.')
        if backend is not None:
            print('Esta terminal inició Django. Manténla abierta; Ctrl+C detiene ese backend.')
            while backend.poll() is None:
                time.sleep(1)
        else:
            print('Django ya estaba activo. Conserva abierto el acceso que lo inició.')
    except KeyboardInterrupt:
        print('\nAcceso Android terminado.')
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(str(error))
        return 1
    finally:
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
