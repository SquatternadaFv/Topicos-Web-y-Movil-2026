"""Captura JSON real con una cookie común. Sin dependencias externas."""
import argparse
import http.cookiejar
import json
import urllib.parse
import urllib.request


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url', default='http://127.0.0.1:8000')
    parser.add_argument('--modo', choices=['contador', 'global', 'sesion'], required=True)
    parser.add_argument('--folio', default='ABC123')
    parser.add_argument('--numero', type=int, default=12)
    parser.add_argument('--min-copias', type=int, default=1)
    args = parser.parse_args()
    cliente = urllib.request.build_opener(urllib.request.ProxyHandler({}), urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    def pedir(ruta):
        url = args.base_url.rstrip('/') + ruta
        with cliente.open(url, timeout=15) as respuesta:
            datos = json.load(respuesta)
            print(f'GET {ruta} -> HTTP {respuesta.status} ' + json.dumps(datos, ensure_ascii=False))
            return datos
    if args.modo == 'contador':
        for ruta in ['/entregas/visitas/', '/entregas/visitas-mal/']:
            for _ in range(6):
                pedir(ruta)
        return
    escritura = pedir('/entregas/ultimo/?' + urllib.parse.urlencode({'folio': args.folio}))
    lecturas = [pedir('/entregas/ultimo/ver/') for _ in range(args.numero)]
    copias = {d['atendido_por'] for d in [escritura] + lecturas}
    procesos = {(d['atendido_por'], d['proceso']) for d in [escritura] + lecturas}
    print('Copias observadas:', len(copias), 'Workers observados:', len(procesos))
    if len(copias) < args.min_copias:
        raise SystemExit('Faltan copias en la evidencia: repita con --numero 60 y revise docker compose ps / nginx.')
    if args.modo == 'sesion':
        if any(d['folio'] != args.folio or d['almacenamiento'] != 'sesion-db' for d in lecturas):
            raise SystemExit('ERROR: el folio no se conservó en todas las lecturas.')
        print('OK: el folio se conserva con la misma cookie en todas las lecturas.')
    else:
        if all(d['folio'] == args.folio for d in lecturas):
            raise SystemExit('El fallo global aún no se observa: repita con --numero 60.')
        print('FALLO OBSERVADO: algunos workers no conocen el folio guardado.')


if __name__ == '__main__':
    main()
