"""Empaqueta código, datos y documentación; excluye entornos y archivos locales."""
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DESTINO = ROOT.parent / 'Entrega_Proyectos_1_y_2_Optica_22121280.zip'
EXCLUIR = {'.git', '.venv', '.dart_tool', 'build', '__pycache__', '.logs', '.idea', '.gradle', 'node_modules'}
ARCHIVOS_LOCALES = {'.env', 'local.properties', '.flutter-plugins-dependencies'}


def main():
    # Detén la demo antes de empaquetar para no copiar una base en escritura.
    archivos = sorted(p for p in ROOT.rglob('*') if p.is_file()
                      and not EXCLUIR.intersection(p.relative_to(ROOT).parts)
                      and p.name not in ARCHIVOS_LOCALES
                      and p.suffix not in {'.pyc', '.pyo'}
                      and not p.name.endswith(('.sqlite3-journal', '.sqlite3-wal', '.sqlite3-shm')))
    with zipfile.ZipFile(DESTINO, 'w', compression=zipfile.ZIP_DEFLATED) as entrega:
        for path in archivos:
            entrega.write(path, Path(ROOT.name) / path.relative_to(ROOT))
    with zipfile.ZipFile(DESTINO) as entrega:
        assert entrega.testzip() is None, 'Error de integridad del ZIP.'
        assert f'{ROOT.name}/backend/db.sqlite3' in entrega.namelist()
        assert f'{ROOT.name}/backend/optica/modelo/modelo_optica.joblib' in entrega.namelist()
        assert f'{ROOT.name}/backend/optica/modelo/modelo_asistente.joblib' in entrega.namelist()
        assert f'{ROOT.name}/backend/optica/modelo/indice_corpus.joblib' in entrega.namelist()
        assert f'{ROOT.name}/ml/datos/intenciones_optica.csv' in entrega.namelist()
        assert f'{ROOT.name}/docs/DEFENSA_PROYECTOS_1_Y_2.pdf' in entrega.namelist()
    print(f'{DESTINO.name}: {len(archivos)} archivos, {DESTINO.stat().st_size / 1024 / 1024:.2f} MB. Integridad correcta.')
    print('El ZIP lleva fuentes; en otro equipo sigue el README para instalar y compilar.')


if __name__ == '__main__':
    main()
