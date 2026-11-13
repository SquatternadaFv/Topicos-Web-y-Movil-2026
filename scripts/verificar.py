"""Pruebas significativas y registro de comandos/resultados reales."""
import json
from pathlib import Path
import subprocess
import sys
import yaml

RAIZ=Path(__file__).resolve().parents[1]


def main():
    out=RAIZ/'evidencias/verificacion';out.mkdir(parents=True,exist_ok=True)
    resultados=[]
    comandos=[
      ['-m','unittest','discover','-s','tests','-v'],
      ['Actividad_Extra_Django/retos_django/manage.py','test','entregas','--verbosity','2'],
      ['dia5/dia5/manage.py','test','entregas','--verbosity','2'],
      ['Actividad_Extra_Django/retos_django/manage.py','check'],
      ['Actividad_Extra_Django/retos_django/manage.py','makemigrations','--check','--dry-run'],
    ]
    for i,args in enumerate(comandos,1):
        r=subprocess.run([sys.executable,*args],cwd=RAIZ,capture_output=True,text=True,encoding='utf8',errors='replace')
        texto='$ python '+' '.join(args)+'\n'+r.stdout+r.stderr
        (out/f'prueba_{i}.txt').write_text(texto,encoding='utf8')
        resultados.append({'comando':'python '+' '.join(args),'codigo':r.returncode,'salida':f'prueba_{i}.txt'})
        print('OK' if r.returncode==0 else 'ERROR',' '.join(args),flush=True)
    for ruta in (RAIZ/'microservicios-entregas/docker-compose.yml',RAIZ/'Actividad_Extra_Django/retos_django/docker-compose.yml'):
        doc=yaml.safe_load(ruta.read_text(encoding='utf8'))
        for servicio,config in doc['services'].items():
            build=config.get('build')
            if build:
                contexto=ruta.parent/(build if isinstance(build,str) else build.get('context','.'))
                dockerfile=contexto/('Dockerfile' if isinstance(build,str) else build.get('dockerfile','Dockerfile'))
                assert dockerfile.is_file(),dockerfile
        resultados.append({'compose':str(ruta.relative_to(RAIZ)),'yaml_y_rutas_validos':True,'docker_ejecutado':False})
    (out/'pruebas.json').write_text(json.dumps(resultados,ensure_ascii=False,indent=2),encoding='utf8')
    if any(r.get('codigo',0) for r in resultados):raise SystemExit(1)


if __name__=='__main__':main()
