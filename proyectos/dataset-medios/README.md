# Dataset y modelos del laboratorio

Se conserva sin modificar `originales_profesor/generar_dataset.py`, descargado de https://ealcaraz85.github.io/topicoswebmobil/proyectos/dataset-medios/generar_dataset.py. Los datos son sintéticos. El CSV enlazado en los apuntes devolvió 404 al preparar esta entrega, por lo que se regeneró con el algoritmo, semilla 42 y 10 000 filas. La secuencia RNG se conserva, incluidos los sorteos de faltantes con probabilidad cero.

Desde la raíz del repositorio:

```powershell
python -m pip install -r requirements.txt
python ejecutar_actividades.py
python proyectos/dataset-medios/entrenar_arbol.py --profundidad 4
```

El primer comando de ejecución guarda los tres modelos comprimidos, versiones y métricas en `modelos/metadata.json`, ejecuta ocho análisis, seis ejercicios y las comparaciones de modelos. Los scripts son propios salvo los archivos identificados como originales del profesor. Los seis CSV históricos de envios-data se descargaron directamente de `ealcaraz85/topicoswebmobil/proyectos/dataset-medios/`; su origen se documenta en el informe.

La partición es 80/20, estratificada, semilla 42. El preprocesamiento se entrena solo con entrenamiento. Las restricciones de negocio se aplican después del ranking. Las cifras de otro scikit-learn pueden variar: instalar las versiones exactas de requirements.txt para reproducir esta ejecución.
