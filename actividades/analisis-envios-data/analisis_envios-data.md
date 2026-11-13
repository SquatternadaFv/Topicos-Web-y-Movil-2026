# Análisis de seis variantes de envíos

Los seis CSV se descargaron del repositorio original `ealcaraz85/topicoswebmobil`, ruta proyectos/dataset-medios/envios1.csv a envios6.csv. Código fuente: https://github.com/ealcaraz85/topicoswebmobil/tree/main/proyectos/dataset-medios . Este programa y los cálculos son nuevos. envios1 es balanceado; envios2 incluye eskuter; los demás muestran distribuciones diferentes. **Predicción previa:** el modelo base no podrá emitir eskuter; una exactitud alta no garantiza recall alto de dron. Los identificadores ENV se repiten entre CSV y no prueban identidad de características; para comprobar fuga se deben comparar las filas completas.

| archivo | modelo | exactitud | recall_dron | recall_bicicleta | ms_por_fila | clase_nueva |
| --- | --- | --- | --- | --- | --- | --- |
| envios1 | arbol | 0.9537 | 0.8188 | 1.0000 | 0.0064 |  |
| envios1 | bosque | 0.9837 | 0.9428 | 0.9940 | 0.0247 |  |
| envios1 | red | 0.9752 | 0.9216 | 0.9836 | 0.0093 |  |
| envios2 | arbol | 0.7766 | 0.8515 | 0.9664 | 0.0102 | eskuter |
| envios2 | bosque | 0.7851 | 0.9310 | 0.9388 | 0.0214 | eskuter |
| envios2 | red | 0.7477 | 0.8000 | 0.8926 | 0.0092 | eskuter |
| envios3 | arbol | 0.9449 | 0.9211 | 0.9219 | 0.0104 |  |
| envios3 | bosque | 0.9372 | 0.7957 | 0.8958 | 0.0219 |  |
| envios3 | red | 0.9305 | 0.6918 | 0.8242 | 0.0102 |  |
| envios4 | arbol | 0.9269 | 0.8745 | 0.9285 | 0.0097 |  |
| envios4 | bosque | 0.9098 | 0.8999 | 0.8949 | 0.0210 |  |
| envios4 | red | 0.9011 | 0.7715 | 0.8571 | 0.0093 |  |
| envios5 | arbol | 0.9210 | 0.9053 | 0.9642 | 0.0148 |  |
| envios5 | bosque | 0.9315 | 0.9526 | 0.9338 | 0.0644 |  |
| envios5 | red | 0.8875 | 0.8474 | 0.8855 | 0.0136 |  |
| envios6 | arbol | 0.9615 | 0.8356 | 0.8514 | 0.0094 |  |
| envios6 | bosque | 0.9614 | 0.9452 | 0.8160 | 0.0213 |  |
| envios6 | red | 0.9503 | 0.8493 | 0.7925 | 0.0091 |  |

La presencia de eskuter limita el modelo base: ninguna cantidad de confianza genera una clase ausente de classes_. Las clases nuevas requieren ampliar contrato, estrategias, reglas, datos y entrenamiento.
