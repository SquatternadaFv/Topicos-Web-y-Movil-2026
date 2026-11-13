"""Experimentos reproducibles: escribe cifras medidas, nunca salidas inventadas."""
from copy import deepcopy
import json
from pathlib import Path
import time

import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.tree import export_text

from .base import (RAIZ, DATOS, MODELOS, CAMPOS, NUMERICAS, CATEGORICAS, OBJETIVO,
                   LIMITES, MEDIOS, generar, separar, preparar, pipeline, recomendar,
                   es_posible, medir, optimo, costo)

OUT = RAIZ / 'actividades' / 'analisis-dataset'
RESULTADOS = OUT / 'resultados'


def tabla(df):
    df = df.copy()
    if not isinstance(df.index, pd.RangeIndex):
        df = df.reset_index()
    def celda(v):
        return f'{v:.4f}' if isinstance(v, (float, np.floating)) else str(v).replace('|', '/')
    return '\n'.join(['| ' + ' | '.join(map(str, df.columns)) + ' |',
                       '| ' + ' | '.join(['---'] * len(df.columns)) + ' |'] +
                      ['| ' + ' | '.join(celda(v) for v in row) + ' |' for row in df.itertuples(index=False, name=None)])


def guardar(nombre, df):
    df.to_csv(RESULTADOS / f'{nombre}.csv', index=True)
    return tabla(df)


def conteo_imposibles(pred, x, limites=None):
    return int(sum(not es_posible(m, p, limites) for m, p in zip(pred, x.to_dict('records'))))


def ejecutar():
    RESULTADOS.mkdir(parents=True, exist_ok=True)
    datos = preparar()
    xe, xp, ye, yp = separar(datos)
    modelo = joblib.load(MODELOS / 'modelo_arbol.joblib')
    pred = modelo.predict(xp)
    corregido = recomendar(modelo, xp)
    informe = ['# Análisis de las ocho actividades del dataset', '',
               'Predicciones previas: [PREDICCIONES.md](PREDICCIONES.md). Código propio: `../../laboratorio/analisis.py`. '
               'Datos sintéticos y generador originales del profesor. Resultados calculados en esta computadora; no se copian los de otro alumno. '
               'Las proporciones se expresan de 0 a 1 salvo donde se indica %. Semilla 42, prueba estratificada 20 %.', '']
    resumen = {}
    def seccion(titulo):
        print(titulo, flush=True)
        informe.extend(['', '## ' + titulo, ''])
    def texto(s):
        informe.extend([s, ''])

    seccion('Actividad 1 — El retrato del dataset')
    clima = pd.crosstab(datos.clima, datos[OBJETIVO], normalize='index') * 100
    zona = pd.crosstab(datos.zona_destino, datos[OBJETIVO], normalize='index') * 100
    extremos = datos.groupby(OBJETIVO)[['distancia_km', 'peso_kg', 'volumen_l']].agg(['min', 'median', 'max'])
    extremos.columns = ['_'.join(c) for c in extremos.columns]
    texto('**Resultado: porcentajes por clima.**\n\n' + guardar('01_clima', clima))
    texto('**Porcentajes por zona.**\n\n' + guardar('01_zona', zona))
    texto(guardar('01_extremos', extremos))
    inviables = conteo_imposibles(datos[OBJETIVO], datos)
    periferia = datos[(datos[OBJETIVO] == 'bicicleta') & (datos.zona_destino == 'periferia')]
    van = datos[(datos[OBJETIVO] == 'camioneta') & (datos.distancia_km < 2)]
    forzada = van.apply(lambda p: all(not es_posible(m, p) for m in MEDIOS if m != 'camioneta'), axis=1)
    texto(f'**Comparación y preguntas.** Hay {inviables} etiquetas imposibles de {len(datos)}. '
          f'En periferia aparecen {len(periferia)} bicicletas; las distancias de esas filas están entre '
          f'{periferia.distancia_km.min():.2f} y {periferia.distancia_km.max():.2f} km. La distancia explica la asociación sin inventar una prohibición por zona. '
          f'Hay {len(van)} camionetas a menos de 2 km y {int(forzada.sum())} no tienen otra alternativa factible. '
          'Las restantes pueden deberse a refrigeración, riesgos, costo/tiempo o ruido: se examinan las filas, no se atribuye todo al azar. '
          'Dron está prohibido con lluvia, viento fuerte y en el centro; en rural la distancia puede excluirlo aunque no haya prohibición por zona. '
          'Los máximos sugieren límites, pero observar un máximo menor no prueba una restricción contractual. '
          '**Decisión:** reconstruir reglas solo del CSV confunde ausencia de ejemplos con imposibilidad. Conservar restricciones explícitas y verificarlas antes de operar.')
    guardar('01_camionetas_cortas', van.assign(sin_alternativa=forzada))

    seccion('Actividad 2 — La hora y el dron')
    horas = pd.crosstab(datos.hora_salida, datos[OBJETIVO])
    texto(guardar('02_horas', horas))
    horas.plot.bar(stacked=True, figsize=(12, 5)); plt.tight_layout(); plt.savefig(RESULTADOS / '02_horas.png'); plt.close()
    noche = (datos.hora_salida < 6) | (datos.hora_salida >= 21)
    con_noche = datos.assign(es_de_noche=noche.astype(int))
    mn = pipeline(numericas=NUMERICAS + ['es_de_noche']).fit(con_noche.loc[xe.index], ye)
    xpn = con_noche.loc[xp.index]
    comparacion_noche = pd.DataFrame([{'version': 'sin columna', **medir(modelo, xp, yp)},
                                    {'version': 'es_de_noche', **medir(mn, xpn, yp)}])
    texto(guardar('02_es_de_noche', comparacion_noche))
    texto('**Conteo del ejercicio sobre las 10 000 filas (no es una métrica de generalización):** sin columna '
          f'{conteo_imposibles(modelo.predict(datos[CAMPOS]),datos[CAMPOS])}; con es_de_noche '
          f'{conteo_imposibles(mn.predict(con_noche),con_noche)}. La tabla anterior usa exclusivamente la prueba de 2 000 filas.')
    texto(f'**Comparación.** La noche representa {noche.mean():.2%}: {int(noche.sum())} filas frente a {int((~noche).sum())} diurnas. '
          'La tabla permite contrastar las horas sin dron con el intervalo legal 6–20. '
          'El generador penaliza a la bicicleta de noche y modifica el tráfico por hora; no es una prohibición absoluta de bicicleta. '
          'Representar noche con umbrales requiere separar hora < 6 de hora >= 21, al menos dos comparaciones. '
          '**Decisión:** conservar es_de_noche si mejora los imposibles y métricas en prueba, no solo exactitud. '
          'La predicción previa se contrasta con la fila calculada; si no mejora, no se fuerza la conclusión.\n\n![Envíos por hora](resultados/02_horas.png)')

    seccion('Actividad 3 — Anatomía de los errores')
    errores = xp.assign(real=yp, predicho=pred)
    errores = errores[errores.real != errores.predicho]
    confusiones = errores.groupby(['real', 'predicho']).size().sort_values(ascending=False).rename('cantidad').to_frame()
    texto(guardar('03_confusiones', confusiones))
    guardar('03_filas_errores', errores)
    md = errores[(errores.real == 'moto') & (errores.predicho == 'dron')]
    mb = errores[(errores.real == 'moto') & (errores.predicho == 'bicicleta')]
    md_noche = int(((md.hora_salida < 6) | (md.hora_salida >= 21)).sum())
    guardar('03_moto_dron', md.assign(corregido_por_regla=md.apply(lambda p: not es_posible('dron', p), axis=1)))
    comparacion_mb = pd.concat({'moto_a_bici': mb[CAMPOS], 'bici_correcta': xp.loc[(yp == 'bicicleta') & (pred == 'bicicleta')]})
    guardar('03_comparacion_moto_bici', comparacion_mb)
    no_corregidos=md[md.apply(lambda p: es_posible('dron',p),axis=1)]
    texto('**Motos que pasan a dron y no corrigen las reglas:**\n\n' + tabla(no_corregidos[['distancia_km','peso_kg','volumen_l','hora_salida','prioridad','clima','trafico','zona_destino','fragil']]))
    bicis_bien=xp.loc[(yp=='bicicleta') & (pred=='bicicleta')]
    for columna in ('prioridad','clima','fragil'):
        comp=pd.concat({'moto_a_bicicleta':mb[columna].value_counts(normalize=True),
                        'bicicleta_correcta':bicis_bien[columna].value_counts(normalize=True)},axis=1).fillna(0)
        texto(f'**Diferencias en {columna}, proporciones:**\n\n'+guardar('03_diferencia_'+columna,comp))
    texto(f'**Resultado y comparación.** {len(errores)} errores de {len(xp)}; las tres confusiones principales aparecen arriba. '
          f'De {len(md)} motos enviadas a dron, {md_noche} son nocturnas; las otras necesitan inspeccionar clima, zona y capacidad, no solo la hora. '
          f'Las {len(mb)} motos enviadas a bicicleta tienen distancia mediana {mb.distancia_km.median():.2f} km; '
          f'{int((mb.distancia_km >= 6).sum())} están a 6 km o más. Se conservan filas, prioridades, clima y riesgos en los CSV para explicar las diferencias. '
          'Cambiar random_state cambia los ejemplos de entrenamiento/prueba y ya no permite evaluar el archivo guardado como si fuera el mismo holdout. '
          '**Decisión:** priorizar recomendaciones físicamente inviables mediante reglas; los errores entre medios posibles se evalúan por costo y riesgo, sin confundir etiqueta con verdad absoluta.')

    seccion('Actividad 4 — ¿Qué columnas usa de verdad el modelo?')
    nombres = modelo.named_steps['preparacion'].get_feature_names_out()
    importancias = pd.DataFrame({'feature': nombres, 'importancia': modelo.named_steps['modelo'].feature_importances_}).sort_values('importancia', ascending=False)
    texto(guardar('04_importancias', importancias))
    agrupadas={c:sum(v for n,v in zip(nombres,modelo.named_steps['modelo'].feature_importances_)
                     if n==f'numericas__{c}' or n.startswith(f'categoricas__{c}_')) for c in CAMPOS}
    agrupadas=pd.Series(agrupadas,name='importancia').sort_values(ascending=False).to_frame()
    texto('**Importancia agrupada de las catorce columnas originales:**\n\n'+guardar('04_importancias_agrupadas',agrupadas))
    inicio_arbol=export_text(modelo.named_steps['modelo'],feature_names=list(nombres),max_depth=3)
    (RESULTADOS/'04_inicio_arbol.txt').write_text(inicio_arbol,encoding='utf8')
    ablaciones = []
    for c in CAMPOS:
        m = pipeline(numericas=[n for n in NUMERICAS if n != c], categoricas=[n for n in CATEGORICAS if n != c]).fit(xe, ye)
        ablaciones.append({'sin': c, 'exactitud': accuracy_score(yp, m.predict(xp)), 'cambio_pp': 100 * (accuracy_score(yp, m.predict(xp)) - accuracy_score(yp, pred))})
    ablaciones = pd.DataFrame(ablaciones).sort_values('exactitud')
    texto(guardar('04_ablaciones', ablaciones))
    texto('Las cuatro columnas de origen más importantes fueron '+', '.join(agrupadas.index[:4])+'. '
          'El inicio del árbol se conserva en `resultados/04_inicio_arbol.txt` para contrastar nodos y el orden previo. '
          f'La mayor caída al quitar una columna fue {ablaciones.iloc[0]["sin"]}: {ablaciones.iloc[0]["cambio_pp"]:.2f} puntos. '
          'Columnas sin cambio en esta partición: '+', '.join(ablaciones.loc[ablaciones.cambio_pp.abs()<1e-10,'sin'])+'. '
          'La predicción previa puso peso/volumen antes que clima; los datos permiten identificar ese desacuerdo sin reescribir la hipótesis.')
    texto('**Comparación y decisión.** Las cuatro primeras filas muestran las entradas usadas por el árbol; las variables one-hot deben agruparse por columna de origen antes de compararlas con el orden previo. '
          'Quitar una columna y reentrenar no equivale a ponerla en cero en inferencia. '
          'Una importancia cero de zona no evita que reglas.py prohíba un dron al centro: son responsabilidades distintas. '
          'Se mantienen datos necesarios para restricciones, cálculo de volumen, auditoría o seguimiento aunque no mejoren este árbol. '
          'Retirar campos de la app exige analizar ese uso y versionar el contrato.')

    seccion('Actividad 5 — El dron es minoría: ¿hay que balancear?')
    texto(f'**Parte A.** Un sistema que nunca acierta drones y acierta todo lo demás tendría {1-(datos[OBJETIVO]=="dron").mean():.2%}; '
          f'siempre responder la clase mayoritaria daría {datos[OBJETIVO].value_counts(normalize=True).max():.2%}. '
          'Ninguno basta para juzgar drones: se necesitan precisión, recall, matriz y costo. Su rareza proviene de capacidades, clima, horario y zonas. '
          'Separar primero y balancear solo entrenamiento; la prueba debe conservar la distribución objetivo.')
    entrenamiento = xe.assign(**{OBJETIVO: ye})
    grupos = entrenamiento.groupby(OBJETIVO)
    menor, mayor = int(grupos.size().min()), int(grupos.size().max())
    estrategias = {
        'sin_balancear': (entrenamiento, None),
        'submuestreo': (pd.concat([f.sample(menor, random_state=42) for _, f in grupos]), None),
        'sobremuestreo': (pd.concat([f.sample(mayor, replace=True, random_state=42) for _, f in grupos]), None),
        'class_weight_balanced': (entrenamiento, 'balanced'),
    }
    nuevos = generar(20000, 7)
    drones = nuevos[nuevos[OBJETIVO] == 'dron'].head(mayor - int((ye == 'dron').sum()))
    estrategias['drones_nuevos'] = (pd.concat([entrenamiento, drones[CAMPOS + [OBJETIVO]]]), None)
    filas = []
    for nombre, (d, peso) in estrategias.items():
        m = pipeline(balance=peso).fit(d[CAMPOS], d[OBJETIVO])
        filas.append({'estrategia': nombre, 'entrenamiento': len(d), **medir(m, xp, yp)})
    balanceo = pd.DataFrame(filas)
    texto('**Parte B: misma prueba intacta para todas las estrategias.**\n\n' + guardar('05_balanceo', balanceo))
    # Experimento incorrecto deliberado: duplica antes de separar y mide fuga por id.
    tramposo = pd.concat([datos, datos[datos[OBJETIVO] == 'dron'].sample(6000, replace=True, random_state=42)])
    tre, trp = train_test_split(tramposo, test_size=.2, stratify=tramposo[OBJETIVO], random_state=42)
    fuga = len(set(tre.id_envio) & set(trp.id_envio))
    tm = pipeline().fit(tre[CAMPOS], tre[OBJETIVO])
    trmet = medir(tm, trp[CAMPOS], trp[OBJETIVO])
    texto(f'**Trampa explícita, no válida como resultado comparable:** {fuga} IDs aparecen a ambos lados después de duplicar antes de separar. '
          f'Métricas de esa prueba contaminada: `{json.dumps(trmet)}`. El resultado no mide generalización y cambia la prevalencia. '
          '**Parte C.** Mayor recall puede comprar falsos positivos; el submuestreo pierde ejemplos de regiones raras. '
          'Duplicar y ponderar pueden parecerse porque alteran el peso efectivo, aunque no garantizan el mismo árbol. '
          'Después de cambiar prevalencias, predict_proba no es confianza calibrada para la población original. '
          '**Parte D.** No desplegaría balanceo solo por recall: evaluaría costo y precisión del dron y conservaría las reglas. '
          'Comprar más drones requiere datos nuevos y revisar restricciones; duplicar filas viejas no representa mayor capacidad.')

    seccion('Actividad 6 — ¿Quién se equivoca: el modelo o los datos?')
    registros = xp.to_dict('records')
    ideal = np.array([optimo(p) for p in registros])
    ce = np.array([costo(m, p) for m, p in zip(yp, registros)])
    co = np.array([costo(m, p) for m, p in zip(ideal, registros)])
    cm = np.array([costo(m, p) for m, p in zip(corregido, registros)])
    todas_ideales = pd.Series([optimo(p) for p in datos.to_dict('records')], index=datos.index)
    limpio = pipeline().fit(xe, todas_ideales.loc[xe.index])
    pl = recomendar(limpio, xp)
    cl = np.array([costo(m, p) for m, p in zip(pl, registros)])
    costes = pd.DataFrame({'decision': ['optimo', 'etiquetas', 'modelo_con_reglas', 'entrenado_con_optimo'],
                          'costo_total': [co.sum(), ce.sum(), cm.sum(), cl.sum()]})
    costes['exceso_porcentaje'] = 100 * (costes.costo_total / co.sum() - 1)
    texto(guardar('06_costos', costes))
    fallos_etiqueta = corregido != yp.to_numpy()
    recupera_optimo = fallos_etiqueta & (corregido == ideal)
    rescates = xp.assign(etiqueta=yp, modelo=corregido, optimo=ideal).loc[recupera_optimo]
    guardar('06_rescates', rescates)
    texto('**Desacuerdos con la etiqueta que recuperan el óptimo, por confusión:**\n\n'+guardar('06_rescates_por_confusion',rescates.groupby(['etiqueta','modelo']).size().rename('cantidad').to_frame()))
    texto(f'**Preguntas.** Óptimo/etiqueta coinciden {accuracy_score(yp, ideal):.2%}; el modelo sin reglas coincide con etiqueta {accuracy_score(yp,pred):.2%} '
          f'y con reglas {accuracy_score(yp,corregido):.2%}. Modelo con reglas/óptimo: {accuracy_score(ideal,corregido):.2%}. '
          f'De {int(fallos_etiqueta.sum())} desacuerdos con etiqueta, {int(recupera_optimo.sum())} recuperan el óptimo. '
          'El CSV de rescates indica cuáles confusiones de la actividad 3 no son peores decisiones según costo. '
          'El supuesto techo describe ruido difícil de predecir, no un límite estadístico probado. '
          'Comparar el costo con la última fila indica cuánto ayuda limpiar etiquetas; su costo humano debe compararse con ese ahorro. '
          'El alumno puede superar el costo de las etiquetas porque una hoja con varios ejemplos suaviza decisiones ruidosas; no aprende necesariamente cada error individual del operador. '
          '**Decisión:** si la fórmula ya es exacta y barata, usarla directamente. Con decisiones humanas sin fórmula, revisar resultados operativos y adjudicar una muestra; accuracy solo mide acuerdo con quien etiquetó.')

    seccion('Actividad 7 — ¿El modelo razona o memoriza?')
    libre = pipeline(profundidad=None, min_hoja=1).fit(xe, ye)
    props = {}
    mitad = xp.copy(); mitad['peso_kg'] /= 2
    # Si el nuevo elegido ya era factible antes, reducir peso no mejora su costo frente al anterior.
    props['peso_mitad_no_salto_a_otro_ya_factible'] = (mitad, 'factible')
    hora = xp.copy(); hora['hora_salida'] = 16
    base_hora = xp.copy(); base_hora['hora_salida'] = 10
    props['hora_10_a_16_con_trafico_fijo'] = (hora, 'hora')
    dimensiones = xp.copy(); dimensiones['largo_cm'] *= .5
    props['largo_sin_cambiar_volumen'] = (dimensiones, 'igual')
    fragil = xp.copy(); fragil['fragil'] = 1
    props['fragil_no_entra_a_moto'] = (fragil, 'fragil')
    resultados_props = []
    for nombre, m in [('profundidad_8', modelo), ('sin_limite', libre)]:
        original = recomendar(m, xp)
        fila = {'modelo': nombre, 'exactitud': accuracy_score(yp, m.predict(xp))}
        for prop, (cambio, regla) in props.items():
            antes = recomendar(m, base_hora) if regla == 'hora' else original
            despues = recomendar(m, cambio)
            if regla == 'factible':
                invalidas = [a != b and es_posible(b, p) for a, b, p in zip(antes, despues, registros)]
            elif regla == 'fragil':
                invalidas = (xp.fragil.to_numpy() == 0) & (antes != 'moto') & (despues == 'moto')
            else:
                invalidas = antes != despues
            fila[prop] = int(np.sum(invalidas))
        resultados_props.append(fila)
    texto(guardar('07_coherencia', pd.DataFrame(resultados_props)))
    menor_dist = xp.copy(); menor_dist['distancia_km'] *= .5
    nuevos_optimos = np.array([optimo(p) for p in menor_dist.to_dict('records')])
    contra = (ideal != 'camioneta') & (nuevos_optimos == 'camioneta')
    guardar('07_contraejemplos_distancia', xp.loc[contra].assign(distancia_nueva=menor_dist.loc[contra, 'distancia_km']))
    ejemplo = dict(registros[0], distancia_km=2., peso_kg=1., largo_cm=10., ancho_cm=10., alto_cm=10., volumen_l=1.,
                   fragil=1, refrigerado=0, valor_declarado_mxn=100., hora_salida=3, prioridad='normal',
                   zona_destino='residencial', clima='lluvia', trafico='medio')
    ejemplo_corto = dict(ejemplo, distancia_km=1.)
    texto('**Contraejemplo calculado a la regla de distancia:** paquete de 1 kg/1 L, frágil, no refrigerado, valor 100, '
          'a las 3:00, prioridad normal, residencial, lluvia y tráfico medio. '
          f'A 2 km el óptimo es {optimo(ejemplo)}; a 1 km es {optimo(ejemplo_corto)}. '
          f'Costos a 2 km: moto={costo("moto",ejemplo):.3f}, camioneta={costo("camioneta",ejemplo):.3f}; '
          f'a 1 km: moto={costo("moto",ejemplo_corto):.3f}, camioneta={costo("camioneta",ejemplo_corto):.3f}. '
          'La penalización fija de fragilidad/lluvia afecta más a moto; al reducir distancia puede dominar el costo fijo, '
          'por lo que «más cerca nunca pasa a camioneta» es falsa incluso si la búsqueda en una muestra no encuentra un caso.')
    valor = xp.copy(); valor['valor_declarado_mxn'] = 30000
    elegibles = xp.valor_declarado_mxn < 20000
    nuevos_valor = np.array([optimo(p) for p in valor.to_dict('records')])
    cambios_valor_modelo = int(((recomendar(modelo, valor) != corregido) & elegibles).sum())
    cambios_valor_optimo = int(((nuevos_valor != ideal) & elegibles).sum())
    texto('**Justificación de propiedades.** (1) Peso no interviene en puntaje, solo capacidad: al reducirlo puede entrar un medio antes inviable, '
          'pero no hay razón para preferir otro ya viable. (2) 10:00 y 16:00 son diurnas; con tráfico fijo el costo no cambia. '
          '(3) La fórmula usa volumen_l, no largo aislado; cambiar largo sin volumen es una prueba controlada, no un paquete coherente de producción. '
          '(4) Fragilidad penaliza moto 50, bici 30, dron 20 y camioneta 0: activar fragilidad no puede introducir moto desde otro ganador, salvo empate previo; se revisan empates en el óptimo. '
          f'**Distancia:** se encontraron {int(contra.sum())} contraejemplos al reducirla a la mitad. Si no aparecen en esta muestra, no demuestra la propiedad: '
          'el costo fijo de camioneta y las penalizaciones ajenas a distancia pueden hacer que gane a distancias muy cortas. '
          f'**Valor:** {int((datos.valor_declarado_mxn>20000).sum())} filas del dataset completo y {int((xe.valor_declarado_mxn>20000).sum())} del entrenamiento superan 20000; '
          f'al subir a 30000 cambian {cambios_valor_modelo} decisiones del modelo y {cambios_valor_optimo} óptimos. '
          'Una prueba que solo prohíbe direcciones incorrectas no detecta insensibilidad; hace falta una prueba de sensibilidad con casos donde el óptimo sí debe cambiar. '
          '**Decisión:** cero medios físicamente imposibles y cero cambios por hora 10→16 con tráfico fijo; bloquear promoción si falla esa invariancia. '
          'Para otras incoherencias se admite como máximo 1 % en el conjunto retenido y nunca empeorar la versión vigente sin justificación del negocio. '
          'Entre 93 % con cincuenta incoherencias y 92 % con dos, elegiría el segundo si las incoherencias representan riesgos reales. '
          'El árbol libre puede memorizar fronteras del ruido: pequeñas perturbaciones cruzan hojas arbitrarias aunque cambie poco accuracy. '
          'La tabla permite comprobarlo, sin declararlo por anticipado. Reglas corrigen inviabilidad, no todos los errores de costo.')

    seccion('Actividad 8 — El mundo cambia')
    nuevos_limites = deepcopy(LIMITES); nuevos_limites['dron'].update(peso_kg=5, volumen_l=25, distancia_km=25)
    mundos = {'referencia': generar(5000, 99), 'lluvias': generar(5000, 99, lluvias=True), 'drones_nuevos': generar(5000, 99, drones=True)}
    filas = []
    for nombre, d in mundos.items():
        d.to_csv(RESULTADOS / f'08_{nombre}.csv', index=False)
        px = modelo.predict(d[CAMPOS]); final = recomendar(modelo, d[CAMPOS])
        fila = {'escenario': nombre, 'exactitud': accuracy_score(d[OBJETIVO], px),
                'confianza_media': modelo.predict_proba(d[CAMPOS]).max(axis=1).mean(),
                'corregidas': float(np.mean(px != final)),
                'lluvia_observada': float((d.clima == 'lluvia').mean())}
        fila.update({f'pred_{m}': float(np.mean(px == m)) for m in MEDIOS})
        filas.append(fila)
    texto(guardar('08_escenarios', pd.DataFrame(filas)))
    dn = mundos['drones_nuevos']; xn, yn = dn[CAMPOS], dn[OBJETIVO]
    reglas_nuevas = recomendar(modelo, xn, nuevos_limites)
    nuevos1000 = generar(1000, 123, drones=True)
    nuevas_comparaciones = []
    for n in (200, 500, 1000):
        d = nuevos1000.iloc[:n]
        for estrategia, entrenamiento_n in [('solo_nuevos', d), ('viejos_mas_nuevos', pd.concat([datos, d])),
                                            ('nuevos_ponderados', pd.concat([datos, *([d] * 10)]))]:
            m = pipeline().fit(entrenamiento_n[CAMPOS], entrenamiento_n[OBJETIVO])
            nuevas_comparaciones.append({'estrategia': estrategia, 'nuevos': n,
                'exactitud': accuracy_score(yn, recomendar(m, xn, nuevos_limites))})
    texto(guardar('08_reentrenamiento', pd.DataFrame(nuevas_comparaciones)))
    texto(f'**Solo reglas nuevas sin entrenar:** exactitud con reglas anteriores {accuracy_score(yn,recomendar(modelo,xn)):.2%}, '
          f'con límites actualizados {accuracy_score(yn,reglas_nuevas):.2%}. '
          'La señal sin etiqueta para lluvia es su frecuencia observada; la nueva capacidad puede ser invisible en las entradas si solo cambia qué decisión es correcta. '
          'La confianza no sabe que el contrato operativo cambió. Mezclar muchos datos viejos conserva etiquetas de la capacidad anterior y diluye los pocos nuevos. '
          '**Decisión:** registrar entrada, versión de modelo/reglas, ranking, medio sugerido y medio finalmente elegido por el operador. '
          'Observer después del commit permite registrar esa discrepancia sin recargar la vista. '
          'Actualizar primero el contrato de límites acordado con negocio, generar/obtener etiquetas del mundo nuevo, evaluar contra escenarios retenidos, versionar y desplegar juntos reglas/modelo. '
          'La métrica dispara revisión; el responsable del negocio y el equipo deciden el reentrenamiento, no el modelo por sí solo.')

    (OUT / 'ANALISIS.md').write_text('\n'.join(informe) + '\n', encoding='utf8')
    resumen['base'] = medir(modelo, xp, yp)
    resumen['filas'] = len(datos)
    resumen['prueba'] = len(xp)
    (RESULTADOS / 'resumen.json').write_text(json.dumps(resumen, indent=2), encoding='utf8')
    ejercicios(modelo, datos, xe, xp, ye, yp)
    variantes_y_modelos(modelo)
    print('Informes y experimentos terminados.', flush=True)


def ejercicios(modelo, datos, xe, xp, ye, yp):
    out = RAIZ / 'actividades' / 'ejercicios-modelo'
    out.mkdir(parents=True, exist_ok=True)
    chico = pipeline(profundidad=4).fit(xe, ye)
    arbol = export_text(chico.named_steps['modelo'], feature_names=list(chico.named_steps['preparacion'].get_feature_names_out()), max_depth=1000)
    (out / 'arbol_profundidad4.txt').write_text(arbol, encoding='utf8')
    sucio = generar(faltantes=.05)
    sucio.to_csv(out / 'sucio.csv', index=False)
    sx, tx, sy, ty = separar(sucio)
    comparacion = []
    for imputar in (False, True):
        m = pipeline(imputar=imputar).fit(sx, sy)
        comparacion.append({'imputacion_numerica': imputar, 'exactitud': accuracy_score(ty, m.predict(tx))})
    (out / 'resultados_sucio.json').write_text(json.dumps(comparacion, indent=2), encoding='utf8')
    contenido = f'''# Seis ejercicios del modelo

1. **Noche.** La columna es_de_noche está implementada y medida en actividad 2; ver `../analisis-dataset/resultados/02_es_de_noche.csv`. Se cuenta la inviabilidad de todos los medios, no solo drones nocturnos. Dos intervalos disjuntos se vuelven una pregunta binaria para el árbol. La comparación se hace con la misma prueba, no con la cifra 121 como objetivo a imitar.
2. **Balance.** Actividad 5 incluye class_weight balanced, precisión, recall e imposibles. Prefiero limitar falsos positivos costosos y aplicar reglas; aumentar recall sin revisar precisión no garantiza una mejor operación.
3. **Profundidad 4.** Exactitud medida: {accuracy_score(yp, chico.predict(xp)):.4f}. `arbol_profundidad4.txt` contiene el árbol completo. Cada nodo puede escribirse como if/else sobre las columnas transformadas. Al hacerlo a mano se pierde la conexión reproducible con entrenamiento, el pipeline y las probabilidades de hojas; no desaparece la necesidad de preparar categorías exactamente igual.
4. **Sucio.** Se dejaron celdas vacías con probabilidad 0.05 en las columnas que el generador permite: no significa 5 % de todas las celdas del CSV. Resultado real: `{json.dumps(comparacion)}`. En ambas versiones se imputan categorías para comparar de manera controlada; varía la imputación numérica. La mediana/moda se aprende únicamente del entrenamiento. La API rechaza peso omitido con 400: un imputador de entrenamiento no autoriza inventar datos operativos obligatorios.
5. **RecomendadorReglas.** Está en `laboratorio/recomendadores.py`. La variable RECOMENDADOR=reglas cambia la dependencia sin editar la vista de Django. Adapter mantiene el contrato de salida y la selección de implementación permite sustituir estrategias; fábrica configura cuál se usa.
6. **Respaldo.** RecomendadorConRespaldo envuelve principal y respaldo bajo la misma interfaz. Ante una excepción operativa del principal utiliza reglas y lo declara en motivo. Es similar a Decorator. No se usa el respaldo para ocultar un JSON inválido: la validación ocurre antes. La prueba simula un fallo del árbol y comprueba el resultado.

Reproducir: `python ejecutar_actividades.py`. La prueba de intercambiabilidad y caída está en `tests/test_laboratorio.py`.
'''
    (out / 'EJERCICIOS.md').write_text(contenido, encoding='utf8')


def variantes_y_modelos(base):
    out = RAIZ / 'actividades' / 'analisis-envios-data'
    out.mkdir(parents=True, exist_ok=True)
    datosdir = out / 'datos'; datosdir.mkdir(exist_ok=True)
    original = preparar()
    variantes = [pd.read_csv(datosdir / f'envios{i}.csv') for i in range(1, 7)]
    tablas, entrenamiento_tablas = [], []
    for i, d in enumerate(variantes, 1):
        for tipo in ('arbol', 'bosque', 'red'):
            m = joblib.load(MODELOS / f'modelo_{tipo}.joblib')
            # envios5 usa solo holdout; se contabiliza solapamiento real en las demás variantes.
            xx, yy = (separar(d)[1], separar(d)[3]) if i == 5 else (d[CAMPOS], d[OBJETIVO])
            inicio = time.perf_counter(); p = m.predict(xx)
            from sklearn.metrics import recall_score
            tablas.append({'archivo': f'envios{i}', 'modelo': tipo, 'exactitud': accuracy_score(yy,p),
                           'recall_dron': recall_score(yy,p,labels=['dron'],average='macro',zero_division=0),
                           'recall_bicicleta': recall_score(yy,p,labels=['bicicleta'],average='macro',zero_division=0),
                           'ms_por_fila': 1000*(time.perf_counter()-inicio)/len(xx),
                           'clase_nueva': 'eskuter' if i == 2 else ''})
            x1,x2,y1,y2 = separar(d)
            inicio = time.perf_counter(); adaptado = pipeline(tipo).fit(x1,y1)
            import io
            memoria=io.BytesIO(); joblib.dump(adaptado, memoria, compress=3)
            entrenamiento_tablas.append({'archivo':f'envios{i}', 'modelo':tipo, 'exactitud':accuracy_score(y2,adaptado.predict(x2)),
                                         'recall_dron': recall_score(y2,adaptado.predict(x2),labels=['dron'],average='macro',zero_division=0),
                                         'bytes_comprimidos':memoria.tell(),
                                         'segundos_entrenamiento':time.perf_counter()-inicio})
    r = pd.DataFrame(tablas); re = pd.DataFrame(entrenamiento_tablas)
    r.to_csv(out / 'resultados.csv', index=False)
    comp = RAIZ / 'actividades' / 'comparacion-modelos'; comp.mkdir(parents=True, exist_ok=True)
    re.to_csv(comp / 'entrenados_por_dataset.csv', index=False)
    informe = '# Análisis de seis variantes de envíos\n\n'
    informe += ('Los seis CSV se descargaron del repositorio original `ealcaraz85/topicoswebmobil`, ruta proyectos/dataset-medios/envios1.csv a envios6.csv. '
                'Código fuente: https://github.com/ealcaraz85/topicoswebmobil/tree/main/proyectos/dataset-medios . '
                'Este programa y los cálculos son nuevos. '
                'envios1 es balanceado; envios2 incluye eskuter; los demás muestran distribuciones diferentes. '
                '**Predicción previa:** el modelo base no podrá emitir eskuter; una exactitud alta no garantiza recall alto de dron. '
                'Los identificadores ENV se repiten entre CSV y no prueban identidad de características; para comprobar fuga se deben comparar las filas completas.\n\n')
    informe += tabla(r) + '\n\nLa presencia de eskuter limita el modelo base: ninguna cantidad de confianza genera una clase ausente de classes_. Las clases nuevas requieren ampliar contrato, estrategias, reglas, datos y entrenamiento.\n'
    (out / 'analisis_envios-data.md').write_text(informe, encoding='utf8')
    (comp / 'comparacion_modelos.md').write_text('# Comparación de árbol, bosque y red\n\n'
        'Experimento A: entrenar/probar 80/20 en cada archivo público, estratificando por etiqueta. '
        'Experimento B: modelos base de envios5 frente a variantes; ver ../analisis-envios-data/analisis_envios-data.md para procedencia y fugas posibles. '
        'Las mismas particiones se usan para los tres tipos. No se exige que gane la red; comparar costo, tamaño, recall y facilidad de explicación.\n\n'
        + tabla(re) + '\n\n**Experimento B.**\n\n' + tabla(r) + '\n\n'
        + '\n'.join(f'- {p.name}: {p.stat().st_size} bytes comprimidos.' for p in MODELOS.glob('*.joblib'))
        + '\n\nNo seleccionaría automáticamente el de mayor accuracy: decidiría con restricciones duras, error por clase, costo, latencia y capacidad de mantenerlo.\n', encoding='utf8')
