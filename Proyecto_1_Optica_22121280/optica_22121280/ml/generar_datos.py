"""Datos sintéticos educativos; etiquetas comerciales, no resultados clínicos."""
import csv
import random
from pathlib import Path
DESTINO = Path(__file__).resolve().parent / 'datos' / 'perfiles_optica.csv'
CAMPOS = ['horas_pantalla', 'horas_exterior', 'presupuesto', 'uso_principal', 'prefiere_fotocromatico', 'paquete']

def generar():
    rng = random.Random(22121280)
    filas = []
    for _ in range(1200):
        pantalla, exterior = rng.randint(0, 16), rng.randint(0, 12)
        uso = rng.choice(['general', 'estudio', 'oficina', 'exterior'])
        foto = rng.random() < .25
        # Política de etiquetado histórica simulada: preferencia y presupuesto
        # no siempre se respetaron. Las reglas actuales sí los hacen obligatorios.
        if exterior >= 4 or uso == 'exterior':
            etiqueta = 'premium' if pantalla >= 7 else 'fotocromatico'
        else:
            etiqueta = 'antirreflejante' if pantalla >= 5 else 'esencial'
        if rng.random() < .10:
            etiqueta = rng.choice(['esencial', 'antirreflejante', 'fotocromatico', 'premium'])
        filas.append([pantalla, exterior, rng.choice([500, 700, 1000, 1500, 2000, 3000, 4000]), uso, int(foto), etiqueta])
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    with DESTINO.open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(CAMPOS); w.writerows(filas)
    print(f'{DESTINO.name}: {len(filas)} perfiles; semilla 22121280; datos sintéticos.')

if __name__ == '__main__':
    generar()
