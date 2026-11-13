# Comparación de árbol, bosque y red

Experimento A: entrenar/probar 80/20 en cada archivo público, estratificando por etiqueta. Experimento B: modelos base de envios5 frente a variantes; ver ../analisis-envios-data/analisis_envios-data.md para procedencia y fugas posibles. Las mismas particiones se usan para los tres tipos. No se exige que gane la red; comparar costo, tamaño, recall y facilidad de explicación.

| archivo | modelo | exactitud | recall_dron | bytes_comprimidos | segundos_entrenamiento |
| --- | --- | --- | --- | --- | --- |
| envios1 | arbol | 0.9915 | 0.9840 | 3860 | 0.0668 |
| envios1 | bosque | 0.9975 | 0.9940 | 1881035 | 1.3209 |
| envios1 | red | 0.9915 | 0.9940 | 93469 | 1.4810 |
| envios2 | arbol | 0.7605 | 0.8421 | 6813 | 0.1200 |
| envios2 | bosque | 0.8105 | 0.8889 | 14523325 | 2.9096 |
| envios2 | red | 0.7660 | 0.8713 | 94136 | 1.0642 |
| envios3 | arbol | 0.9440 | 0.9821 | 4951 | 0.1207 |
| envios3 | bosque | 0.9515 | 0.8036 | 7525843 | 2.1010 |
| envios3 | red | 0.9330 | 0.6607 | 93420 | 1.4716 |
| envios4 | arbol | 0.9190 | 0.7394 | 5800 | 0.1155 |
| envios4 | bosque | 0.9265 | 0.7958 | 9268602 | 2.2347 |
| envios4 | red | 0.8840 | 0.7958 | 93418 | 1.0617 |
| envios5 | arbol | 0.9210 | 0.9053 | 5462 | 0.1234 |
| envios5 | bosque | 0.9315 | 0.9526 | 9540456 | 2.1387 |
| envios5 | red | 0.8875 | 0.8474 | 93480 | 1.2700 |
| envios6 | arbol | 0.9535 | 0.8000 | 5125 | 0.1150 |
| envios6 | bosque | 0.9510 | 0.5333 | 6067982 | 1.7673 |
| envios6 | red | 0.9430 | 0.4000 | 93425 | 1.3648 |

**Experimento B.**

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

- modelo_arbol.joblib: 5464 bytes comprimidos.
- modelo_bosque.joblib: 9534798 bytes comprimidos.
- modelo_red.joblib: 93463 bytes comprimidos.

No seleccionaría automáticamente el de mayor accuracy: decidiría con restricciones duras, error por clase, costo, latencia y capacidad de mantenerlo.
