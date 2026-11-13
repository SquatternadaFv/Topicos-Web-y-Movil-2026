"""Comprobación Docker auténtica; escribe el fallo si no existe el motor."""
import json
from pathlib import Path
import shutil
import subprocess

RAIZ=Path(__file__).resolve().parents[1]


def main():
    out=RAIZ/'evidencias/verificacion';out.mkdir(parents=True,exist_ok=True)
    resultado={'ejecutable':shutil.which('docker'),'docker_ejecutado':False}
    if resultado['ejecutable']:
        p=subprocess.run(['docker','version'],capture_output=True,text=True,encoding='utf8',errors='replace')
        resultado.update(codigo=p.returncode,salida=p.stdout+p.stderr,docker_ejecutado=p.returncode==0)
    else:
        resultado['motivo']='Docker no está instalado o no está en PATH. No se ejecutaron contenedores ni compose ps.'
    (out/'docker.json').write_text(json.dumps(resultado,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(resultado,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
