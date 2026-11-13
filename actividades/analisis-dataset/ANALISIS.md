# Análisis de las ocho actividades del dataset

Predicciones previas: [PREDICCIONES.md](PREDICCIONES.md). Código propio: `../../laboratorio/analisis.py`. Datos sintéticos y generador originales del profesor. Resultados calculados en esta computadora; no se copian los de otro alumno. Las proporciones se expresan de 0 a 1 salvo donde se indica %. Semilla 42, prueba estratificada 20 %.


## Actividad 1 — El retrato del dataset

**Resultado: porcentajes por clima.**

| clima | bicicleta | camioneta | dron | moto |
| --- | --- | --- | --- | --- |
| despejado | 32.8390 | 16.5692 | 13.5178 | 37.0740 |
| lluvia | 8.4910 | 16.6752 | 0.0000 | 74.8338 |
| viento_fuerte | 31.6860 | 18.4109 | 0.0000 | 49.9031 |

**Porcentajes por zona.**

| zona_destino | bicicleta | camioneta | dron | moto |
| --- | --- | --- | --- | --- |
| centro | 58.4486 | 13.5245 | 0.0000 | 28.0270 |
| periferia | 0.8798 | 13.9785 | 12.6100 | 72.5318 |
| residencial | 26.1970 | 14.6152 | 17.2976 | 41.8902 |
| rural | 0.0000 | 40.8000 | 0.0000 | 59.2000 |

| medio_recomendado | distancia_km_min | distancia_km_median | distancia_km_max | peso_kg_min | peso_kg_median | peso_kg_max | volumen_l_min | volumen_l_median | volumen_l_max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bicicleta | 0.3700 | 3.4200 | 7.0000 | 0.1000 | 1.7600 | 7.9900 | 0.3000 | 7.7800 | 39.7000 |
| camioneta | 0.4300 | 8.9900 | 59.1200 | 0.1000 | 6.7250 | 80.0000 | 0.3000 | 31.3650 | 400.5700 |
| dron | 2.0700 | 9.5350 | 14.9900 | 0.1000 | 1.0450 | 2.5000 | 0.3000 | 4.2900 | 11.9800 |
| moto | 0.3400 | 10.6300 | 39.9000 | 0.1000 | 2.5800 | 24.9300 | 0.3000 | 11.2750 | 89.9900 |

**Comparación y preguntas.** Hay 0 etiquetas imposibles de 10000. En periferia aparecen 18 bicicletas; las distancias de esas filas están entre 5.38 y 6.93 km. La distancia explica la asociación sin inventar una prohibición por zona. Hay 107 camionetas a menos de 2 km y 95 no tienen otra alternativa factible. Las restantes pueden deberse a refrigeración, riesgos, costo/tiempo o ruido: se examinan las filas, no se atribuye todo al azar. Dron está prohibido con lluvia, viento fuerte y en el centro; en rural la distancia puede excluirlo aunque no haya prohibición por zona. Los máximos sugieren límites, pero observar un máximo menor no prueba una restricción contractual. **Decisión:** reconstruir reglas solo del CSV confunde ausencia de ejemplos con imposibilidad. Conservar restricciones explícitas y verificarlas antes de operar.
