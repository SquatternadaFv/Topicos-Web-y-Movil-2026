"""Cliente simulado: usa exclusivamente el contrato HTTP del backend."""
import argparse
import json
import urllib.error
import urllib.parse
import urllib.request


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url', default='http://127.0.0.1:8000')
    parser.add_argument('--km', default='5')
    parser.add_argument('--kg', default='2')
    args = parser.parse_args()
    url = args.base_url.rstrip('/') + '/entregas/cotizar/?' + urllib.parse.urlencode({'km': args.km, 'kg': args.kg})
    print('GET', url)
    try:
        with urllib.request.urlopen(url, timeout=10) as respuesta:
            datos = json.load(respuesta)
    except urllib.error.HTTPError as error:
        print('HTTP', error.code, json.load(error))
        return 1
    except urllib.error.URLError as error:
        print('No se pudo conectar:', error.reason)
        return 1
    print('Medio sugerido:', datos['medio'])
    print('Motivo:', datos['motivo'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
