"""Entrena y reproduce las actividades de análisis, sin Docker ni Flutter."""
import argparse
import json
from laboratorio.base import entrenar_todos

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--solo-entrenar', action='store_true')
    args = parser.parse_args()
    print(json.dumps(entrenar_todos(), indent=2))
    if not args.solo_entrenar:
        from laboratorio.analisis import ejecutar
        ejecutar()
    from laboratorio.asistente import entrenar
    print(entrenar())
