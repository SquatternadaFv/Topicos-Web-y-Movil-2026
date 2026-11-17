# Lúmina Óptica: guía de construcción, funcionamiento y defensa de P1 y P2

Eduardo Osvaldo Rodríguez Gutiérrez · 22121280 · Revisión del 17 de noviembre de 2026.

Este documento describe **el código que existe**, no una propuesta de funciones futuras. Es la guía principal para estudiar los dos proyectos. Los informes anteriores de análisis y diseño se conservan como antecedentes; algunos describen únicamente P1. El estado de pruebas y capturas de esta revisión se consulta en `evidencias/VALIDACION_P1_P2_2026-11-17.md`.

## 1. Qué pidió el profesor y qué se construyó

La fuente de los requisitos es [Apuntes de Tópicos Web y Móvil](https://ealcaraz85.github.io/topicoswebmobil/), en particular:

- [Proyectos Flutter progresivos](https://ealcaraz85.github.io/topicoswebmobil/#orgcb3827a): al control 22121280 le corresponde óptica, con recomendación de paquete de lentes/tratamiento.
- [Proyecto 1](https://ealcaraz85.github.io/topicoswebmobil/#orgd85c21d): adaptar el recomendador del curso, integrarlo en un monolito Django con SQLite, consumirlo desde Flutter, registrar una orden con folio y analizar patrones reales de ambos lados.
- [Proyecto 2](https://ealcaraz85.github.io/topicoswebmobil/#orga05f98b): extender el mismo producto con un asistente entrenado, dataset propio, métrica de prueba, endpoint y chat Flutter. El asistente consulta datos y remite al recomendador cuando necesita una decisión de dominio.
- [Entrenar un modelo chico para el asistente](https://ealcaraz85.github.io/topicoswebmobil/#orgf9397a0): referencia para clasificación de intenciones, vectorización y artefacto entrenado.
- [Actividad de corpus RAG](https://ealcaraz85.github.io/topicoswebmobil/#actividad-rag-corpus): separación entre frases para aprender intenciones, documentos recuperables y datos vivos de la API.

La matriz detallada requisito → archivo → evidencia está en `MATRIZ_PROYECTOS_1_Y_2.md`. El análisis breve de patrones actualizado está en `ANALISIS_PATRONES_P1_P2.md` y su PDF.

Los apuntes definen **la integración y los entregables**. Los nombres Lúmina, sus cuatro paquetes, precios, cinco variables, reglas comerciales, frases y corpus son decisiones de esta adaptación académica. No son precios ni prescripciones proporcionados por el profesor. Tampoco se afirma conocer indicaciones verbales que no estén publicadas en los apuntes.

### Qué representa cada proyecto

**P1:** un usuario ve paquetes, llena un perfil, recibe una propuesta comercial calculada en el servidor, revisa restricciones y confirma una solicitud. El sistema guarda un folio y permite volver a consultar exactamente el resultado registrado.

**P2:** ese mismo usuario puede escribir preguntas. Un segundo modelo identifica la intención. Según ella, el servidor consulta catálogo, orden, explicación histórica o documento público, o dirige al formulario del recomendador. El chat se agregó como cuarta pestaña; permanecen catálogo, recomendación y consulta de folio.

El sistema no calcula graduación, no diagnostica, no verifica eficacia clínica, no cobra y no programa fabricación. Una orden `registrada` es una solicitud de demostración, no prueba de que existan lentes listos para recoger.

### Diferencia con el ejemplo de mensajería de clase

La tubería del ejemplo se conserva: datos etiquetados → separación de entrenamiento y prueba → preprocesamiento → modelo → `.joblib` → probabilidades → reglas → JSON → Flutter → registro con folio. Lo adaptado es la semántica: las clases ya no son transportes y las entradas ya no son distancia/peso de un envío. Aquí las clases son paquetes de óptica y las entradas describen rutina, presupuesto y preferencia. El asistente también usa frases y documentos de esta óptica, no el corpus defectuoso de otro ejercicio.

## 2. Arquitectura general: cómo se conecta todo

```text
NAVEGADOR / DISPOSITIVO
  Flutter: catálogo | perfil | resultado | folio | chat
      modelos Dart + ApiClient (HTTP/JSON)
                         |
                         v
DJANGO, UN SOLO MONOLITO EN EL PUERTO 8000
  config/urls -> optica/urls -> views: contrato HTTP y JSON
                         |
              +----------+----------------+
              |                           |
         OpticaService               AsistenteService
       validación del perfil         clasificación del texto
       adaptador del árbol           adaptador TF-IDF/logística
       reglas comerciales            selección de operación
       confirmación y snapshot       consulta real o contexto
              |                           |
              +--------- repositorios ----+
                         |
                       ORM
                         |
                    db.sqlite3

FUERA DE LAS PETICIONES HTTP
  ml/generar_datos.py -> CSV perfiles -> ml/entrenar.py
      -> modelo_optica.joblib
  ml/generar_intenciones.py -> CSV frases -> ml/entrenar_asistente.py
      -> modelo_asistente.joblib
  ml/corpus_optica.json -> ml/indexar_corpus.py
      -> indice_corpus.joblib
```

La compilación de Flutter web se sirve en `127.0.0.1:5173`. Ese servidor entrega archivos estáticos; **no** ejecuta los modelos. El navegador llama por HTTP a Django en `127.0.0.1:8000/api`. Son dos procesos locales, pero el backend sigue siendo un monolito: recomendador, asistente y acceso a datos viven en la misma aplicación Django. No hay gateway ni microservicios del Proyecto 3.

No existe una llamada del navegador a scikit-learn, ni un `.joblib` dentro de los assets de Flutter. Esto evita repartir artefactos y reglas a cada cliente y permite que cualquier cliente reciba decisiones consistentes del servidor.

### Mapa de archivos para una explicación frente al profesor

| Archivo o carpeta | Qué mostrar y explicar |
|---|---|
| `backend/config/settings.py` | SQLite, aplicaciones Django, hosts y CORS local |
| `backend/config/urls.py` | Entrada de rutas del framework y prefijo `/api/` |
| `backend/optica/urls.py` | Rutas públicas de ambos proyectos |
| `backend/optica/views.py` | Métodos permitidos, lectura JSON, traducción de errores y delegación |
| `backend/optica/models.py` | Esquema de Paquete y Orden |
| `backend/optica/migrations/` | Evolución reproducible del esquema |
| `backend/optica/repositories.py` | Consultas y creación mediante ORM |
| `backend/optica/validation.py` | Validación independiente de Flutter |
| `backend/optica/recomendador.py` | Adapter del árbol: entrada DataFrame y salida ranking |
| `backend/optica/reglas.py` | Restricciones comerciales composables |
| `backend/optica/services.py` | Recomendación y registro transaccional/idempotente |
| `backend/optica/clasificador_asistente.py` | Normalización y Adapter del modelo de intenciones |
| `backend/optica/asistente.py` | Orquestación de respuestas de P2 |
| `backend/optica/recuperacion.py` | Recuperación léxica de documentos públicos |
| `backend/optica/modelo/` | Dos modelos aprendidos y un índice de documentos |
| `ml/` | Procedencia de datos, entrenamiento, corpus, métricas y particiones |
| `flutter_app/lib/main.dart` | Tema, cuatro pestañas y estado de navegación |
| `flutter_app/lib/data/api_client.dart` | Contrato HTTP centralizado, timeout y errores |
| `flutter_app/lib/models/models.dart` | Representación tipada de JSON, no modelos de IA |
| `flutter_app/lib/screens/` | Catálogo, perfil, resultado, orden y chat |
| `backend/optica/tests*.py`, `flutter_app/test/` | Comportamientos comprobados y regresiones |
| `scripts/iniciar_demo.py` | Inicio de API y servidor estático de la demo |

## 3. Base de datos: qué se conserva y por qué

### Paquete: el catálogo actual

| Campo | Tipo / función |
|---|---|
| `codigo` | Slug único que enlaza clase del modelo y producto |
| `nombre`, `descripcion` | Información comercial mostrada |
| `precio` | Decimal con dos posiciones; restricción de precio positivo |
| `tratamientos` | Lista JSON de componentes del paquete |
| `fotocromatico` | Permite comprobar la preferencia obligatoria |
| `disponible` | Disponibilidad comercial del paquete |
| `activo` | Permite retirarlo del catálogo consultable |

La semilla `python backend/manage.py sembrar_demo` crea o actualiza:

| Clase / código | Nombre UI | Precio demo | Fotocromático |
|---|---|---:|---|
| `esencial` | Esencial | $650.00 | No |
| `antirreflejante` | Claridad | $1,100.00 | No |
| `fotocromatico` | Transición | $1,800.00 | Sí |
| `premium` | Integral | $2,400.00 | Sí |

Todos incluyen lente monofocal base y capa endurecida; Claridad añade antirreflejante, Transición añade fotocromático e Integral combina ambos. Son componentes del catálogo ficticio, no afirmaciones médicas.

`disponible` es un booleano, no un inventario por piezas. `activo=False` lo excluye de las consultas públicas y de opciones elegibles. La semilla no borra órdenes, pero sí restablece precios y disponibilidad del catálogo demo; no se debe ejecutar en medio de una demostración de cambios de catálogo esperando conservar esos cambios.

### Orden: la decisión que se confirmó

| Campo | Función |
|---|---|
| `folio` | UUID generado por el servidor, único y consultable |
| `clave_idempotencia` | UUID único suministrado para identificar un intento lógico de confirmación |
| `paquete` | Clave foránea protegida a Paquete |
| `entradas` | Perfil validado que originó el registro |
| `resultado` | Snapshot JSON de recomendación, probabilidades, ranking, motivos y versión |
| `precio_confirmado` | Precio decimal vigente al registrar |
| `creada` | Fecha/hora de alta |
| `estado` | Inicialmente `registrada` |

La relación es **un paquete a muchas órdenes**. `PROTECT` evita borrar un paquete que tiene órdenes. El snapshot es necesario porque el catálogo puede cambiar: si mañana Esencial cuesta $690, un folio registrado por $650 debe seguir mostrando $650 y el razonamiento que tuvo al confirmarse.

El catálogo y la orden responden preguntas distintas: «¿cuánto cuesta hoy?» consulta Paquete; «¿cuánto confirmé en mi folio?» consulta Orden. El asistente respeta esta diferencia. No actualiza resultados históricos cuando cambia el modelo.

No se guarda cada previsualización de recomendación como orden. Tampoco existe una tabla de conversaciones; el chat conserva su historial en el estado Flutter mientras vive la pantalla. Recargar el navegador elimina ese historial, pero no las órdenes persistidas en SQLite.

## 4. P1: entradas y validación

El perfil contiene exactamente cinco campos:

| Campo JSON | Tipo permitido | Intervalo / valores |
|---|---|---|
| `horas_pantalla` | Número, no booleano | 0 a 16 |
| `horas_exterior` | Número, no booleano | 0 a 12 |
| `presupuesto` | Número finito, máximo dos decimales | 300 a 10000 |
| `uso_principal` | Texto categórico | `general`, `estudio`, `oficina`, `exterior` |
| `prefiere_fotocromatico` | Booleano real | `true` o `false` |

No se aceptan campos adicionales. Por ejemplo, agregar `precio: 1` o `paquete: premium` a la confirmación provoca un error en lugar de permitir al cliente imponer una decisión. Las cadenas `"false"`, booleanos usados como cantidades, NaN e infinitos se rechazan. Python considera `bool` una subclase de `int`, por eso se debe excluir explícitamente para números.

Flutter valida para ayudar a corregir rápido. Django vuelve a validar porque una llamada puede venir de PowerShell o de un cliente modificado. La validación del navegador nunca es una frontera de confianza para guardar datos.

En HTTP, `cuerpo()` comprueba el tipo `application/json`, limita el cuerpo a 8 KB, decodifica UTF-8 y rechaza JSON inválido. Un JSON sintácticamente correcto aún puede ser semánticamente inválido: son comprobaciones diferentes.

## 5. P1: cómo se alimentó y entrenó el recomendador

### Procedencia y significado del dataset

`ml/generar_datos.py` genera `ml/datos/perfiles_optica.csv` con **1,200 filas sintéticas**, semilla `22121280`. No provienen de pacientes, ventas ni encuestas. Cada fila tiene las cinco características y una etiqueta `paquete`.

El generador selecciona horas de pantalla enteras de 0 a 16, exterior de 0 a 12 y uno de los cuatro usos. La preferencia fotocromática tiene probabilidad de 25 %. El presupuesto se toma de 500, 700, 1000, 1500, 2000, 3000 y 4000.

La política de etiquetado simulada es:

```text
si exterior >= 4 o uso == exterior:
    si pantalla >= 7: premium
    si no: fotocromatico
si no:
    si pantalla >= 5: antirreflejante
    si no: esencial

en 10 % de las filas:
    reemplazar la etiqueta por una clase elegida al azar
```

Ese último sorteo puede elegir la misma etiqueta: 10 % de reemplazos no significa exactamente 10 % de etiquetas diferentes. En expectativa cambia aproximadamente 7.5 % de todas las etiquetas. Simula decisiones históricas imperfectas.

Presupuesto y preferencia no determinan obligatoriamente la etiqueta histórica. Es deliberado para distinguir aprendizaje de datos y restricciones actuales. El árbol puede aprender patrones de horas/uso, pero eso no garantiza cumplir un presupuesto. Por ello las reglas se aplican después y consultan el catálogo vigente.

### Separación y preprocesamiento

`ml/entrenar.py` toma las cinco columnas como X y `paquete` como y. Separa **960 filas de entrenamiento y 240 de prueba**, `test_size=0.2`, `stratify=y`, `random_state=42`.

Estratificar mantiene aproximadamente la proporción de clases en ambas particiones. La semilla permite reproducir la separación. La prueba no se utiliza para ajustar el árbol: sirve para medir sus predicciones después de `fit`.

El CSV completo contiene 516 etiquetas premium, 354 fotocromático, 214 antirreflejante y 116 esencial. No está balanceado: por eso no basta mirar la accuracy total y conviene consultar las métricas por clase. Predecir siempre premium lograría 43 % en el conjunto completo, pero no distinguiría perfiles. En el asistente, en cambio, las ocho clases tienen 20 frases cada una.

El `Pipeline` combina un `ColumnTransformer` y un `DecisionTreeClassifier`:

- Las cuatro columnas numéricas/lógicas pasan sin escalar: horas, exterior, presupuesto y preferencia codificada 0/1.
- `uso_principal` pasa por `OneHotEncoder(handle_unknown='ignore')`. Cada categoría se representa con una columna binaria; no se asigna un orden numérico ficticio a general/estudio/oficina/exterior.
- El árbol utiliza `max_depth=6`, `min_samples_leaf=12`, `random_state=42`.

Los árboles dividen por umbrales y no necesitan estandarización para comparar escalas. La profundidad limita complejidad; el mínimo de muestras por hoja impide hojas con un solo caso. Estos controles reducen sobreajuste, pero no validan que un dataset sintético represente clientes reales.

### Qué aprende un árbol y de dónde sale la confianza

En cada nodo, el entrenamiento elige una división que reduce la impureza Gini de las etiquetas. Gini es `1 - suma(p_clase²)`. El resultado es una sucesión de preguntas sobre características; una hoja agrupa perfiles de entrenamiento.

`predict_proba` devuelve la distribución de clases de la hoja alcanzada. Un valor 0.85 para antirreflejante significa que esa hoja asigna 85 % de su masa a esa etiqueta. **No significa 85 % de eficacia del tratamiento ni 85 % de certeza clínica.** Tampoco es una estimación calibrada de satisfacción de clientes.

El árbol legible se conserva en `ml/arbol.txt`. Se puede recorrer para explicar qué condiciones llevan al perfil de ejemplo a una hoja. No se entrenó una red neuronal ni un modelo de lenguaje para P1.

### Evaluación y artefacto

La métrica registrada en `ml/metricas.json` es **accuracy = 0.9375 = 225 aciertos / 240 perfiles**, o 93.75 %. También se guarda matriz de confusión y precision, recall y F1 por clase.

- Accuracy: fracción total de etiquetas acertadas.
- Precision de una clase: cuántas de las predicciones de esa clase fueron correctas.
- Recall: cuántos de los ejemplos reales de esa clase se recuperaron.
- F1: media armónica de precision y recall.
- En la matriz de confusión las filas son clases reales y las columnas predichas, en el orden de `clases` del JSON.

Esta evaluación mide reproducción de una política sintética con ruido, antes de reglas. No mide la calidad de toda la aplicación ni la validez clínica. Que las reglas se cumplan se comprueba aparte con pruebas de negocio.

El entrenamiento guarda un diccionario con `pipeline`, `version` y `sklearn` en `backend/optica/modelo/modelo_optica.joblib`. La versión es `optica-v1-` más los primeros 12 caracteres del SHA-256 del CSV; el dataset entregado corresponde a **`optica-v1-f68e75c47161`**. El hash identifica los bytes de datos; no contiene por sí mismo todo el código o los hiperparámetros, por lo que estos se conservan también en el script.

Se usan las dependencias fijadas, especialmente scikit-learn **1.8.0**. El entorno compartido de otras actividades puede tener otra versión y no debe sustituir al `.venv` de esta aplicación. Un `.joblib` se carga como objeto Python confiable, no como un documento inocuo: aquí se genera con los scripts propios.

### Entrenamiento e inferencia son momentos distintos

`fit` se ejecuta con `ml/entrenar.py`, fuera de HTTP. Durante una recomendación, `RecomendadorArbol` solo prepara el DataFrame y llama `predict_proba`. `obtener_recomendador()` tiene caché de un objeto por proceso para no cargar el archivo en cada petición. Reentrenar no recarga mágicamente el proceso Django: después de regenerar hay que reiniciarlo.

La aplicación **no aprende automáticamente** de cada orden nueva. Registrar una orden guarda información; no incorpora esa información al CSV ni vuelve a entrenar. Para un aprendizaje con casos reales harían falta nuevas etiquetas verificadas y un proceso separado de evaluación y versionado.

## 6. P1: del ranking a la decisión válida

`RecomendadorArbol.ranking()` asocia `classes_` con `predict_proba` y ordena por probabilidad descendente. Los empates se resuelven por código. Es importante usar `classes_`: suponer un orden manual de clases puede unir una probabilidad al paquete equivocado.

`OpticaService.recomendar()` valida, obtiene el ranking y consulta el catálogo actual. Para cada candidato reúne motivos de descarte:

1. **Presupuesto:** el precio debe ser menor o igual al presupuesto.
2. **Disponibilidad:** el paquete debe estar disponible.
3. **Preferencia:** si el perfil exige fotocromático, un paquete sin él no es elegible.
4. Una clase que no existe en el catálogo activo se descarta.

Las primeras tres políticas son objetos en `reglas.py` con la misma operación `evaluar`. No modifican las probabilidades ni vuelven a entrenar el árbol. El servicio selecciona el **primer candidato elegible del ranking**. No hace optimización global ni promete encontrar la mejor alternativa clínica.

Devuelve `original`, `paquete`, `confianza_original`, `confianza`, `corregido`, `motivo`, `ranking`, `version_modelo`, `entradas` y `aviso`. El ranking incluye probabilidad, precio, elegibilidad y motivos por opción.

Si ninguna opción cumple, devuelve HTTP **422** y no registra una orden. Es una situación válida de negocio, distinta de un fallo de red. El usuario debe modificar restricciones; el sistema no inventa un paquete más barato.

### Ejemplo que debes dominar: pantalla 8, exterior 1, presupuesto 700

```json
{
  "horas_pantalla": 8,
  "horas_exterior": 1,
  "presupuesto": 700,
  "uso_principal": "oficina",
  "prefiere_fotocromatico": false
}
```

El árbol propone `antirreflejante` (Claridad) con **85 %**. Claridad cuesta $1,100 y viola el presupuesto de $700. El servicio recorre alternativas y termina en `esencial`, de $650. Devuelve `corregido=true` y el motivo.

Para ese perfil, la probabilidad del modelo para Esencial es **0 %**. Se muestra así, sin reemplazarla por 85 %. Esencial se eligió por ser elegible al aplicar reglas; las reglas no convierten ese resultado en una predicción estadísticamente confiable. La implementación permite esa corrección y la explica. Una política de revisión por baja confianza sería una mejora futura, no una función presente ni un requisito explícito de P1.

Con presupuesto $3,000, Claridad sí cumple y `corregido=false`. Con $500, no alcanza ni Esencial y se responde 422. Si se exige fotocromático con $700, también se responde 422; con $2,000 aparece una alternativa fotocromática elegible.

## 7. P1: confirmación, transacción, folio e idempotencia

La previsualización y la confirmación son operaciones distintas:

```text
POST recomendaciones(perfil)
  -> calcula y muestra; no guarda Orden

usuario revisa y confirma

POST ordenes(perfil), Idempotency-Key: UUID
  -> valida otra vez
  -> busca si la clave ya existe
  -> recalcula modelo + reglas con el catálogo vigente
  -> crea Orden + snapshot + precio + folio en una transacción
  -> devuelve 201 si creó, 200 si es reintento equivalente
```

No se registra ciegamente el JSON que mostró Flutter. Si cambió disponibilidad o precio entre previsualizar y confirmar, Django vuelve a comprobar. El cliente envía las cinco entradas, no su precio ni decisión. El folio consultable representa lo que efectivamente confirmó el servidor.

`transaction.atomic()` agrupa la escritura; ante un error se revierte. La clave única en base de datos respalda la idempotencia. Si el cliente reintenta la misma clave y perfil, obtiene la misma orden. Si intenta reutilizarla con otro perfil, recibe **409**. Flutter conserva la clave durante la pantalla de resultado para un reintento de red.

El folio identifica el resultado; la clave de idempotencia identifica un intento lógico de creación. No son intercambiables. UUID reduce colisiones y hace el identificador difícil de adivinar, pero **no constituye autenticación**. El prototipo local no implementa cuentas de compradores ni autorización de acceso por dueño de orden.

La clave se conserva durante la pantalla de resultado, pero no en una cola persistente. Si se recarga o cierra antes de conocer el folio, se puede perder esa referencia de reintento. Una aplicación de cobros reales necesitaría recuperación persistente de operaciones; este prototipo registra solicitudes académicas.

La transacción y la restricción única no equivalen a un sistema distribuido ni a una garantía absoluta ante toda concurrencia. SQLite es apropiado para esta demostración; el código no implementa bloqueo distribuido de existencias ni cobros. Los cambios concurrentes de catálogo a gran escala necesitarían una estrategia adicional.

## 8. P2: qué modelo se entrenó y cómo se alimentó

El asistente usa un **clasificador supervisado de intenciones**, no un LLM generativo ni una llamada a ChatGPT. Después de clasificar, el servicio construye respuestas con datos verificables y plantillas. Usar plantillas para presentar resultados no elimina el modelo: la selección de intención procede de un artefacto entrenado y la respuesta incluye información real de la aplicación.

### Dataset propio

`ml/generar_intenciones.py` contiene **160 frases redactadas para Lúmina**, 20 por cada una de 8 intenciones. Genera `ml/datos/intenciones_optica.csv` con `id`, `texto`, `intencion`, `origen`.

El origen declara «redacción académica propia asistida; sin conversaciones reales». No se afirma que sean transcripciones de clientes ni que el modelo haya leído los apuntes como conocimiento general. Los apuntes orientaron la técnica y la separación de responsabilidades; el dataset describe consultas de este producto.

| Intención aprendida | Ejemplo | Operación posterior |
|---|---|---|
| `saludo` | «hola» | Presentación de capacidades |
| `catalogo` | «qué paquetes ofrecen» | Consulta Paquete vigente |
| `detalle_producto` | «cuánto cuesta claridad» | Busca paquete por nombre/código y consulta datos actuales |
| `seguimiento` | «quiero rastrear mi orden» | Consulta Orden por UUID |
| `explicar_recomendacion` | «explica mi orden» | Lee el snapshot histórico del folio |
| `recomendar` | «qué paquete me recomiendas» | Abre formulario o delega al servicio P1 si viene perfil completo |
| `politicas` | «cuál es el horario de atención» | Recupera contexto público con fuente |
| `fuera_dominio` | «quién ganó el partido de fútbol» | Respuesta que delimita el alcance |

El script comprueba que no existan textos normalizados idénticos antes de separar. Usa **128 frases de entrenamiento y 32 de prueba**, estratificación por intención y semilla 42: 16 y 4 ejemplos de cada clase, respectivamente. El vectorizador se ajusta solo con las 128 de entrenamiento.

### Normalización y representación de texto

Antes de entrenar y de inferir se aplica la misma función `normalizar_texto`: minúsculas, espacios normalizados y UUID reemplazados por `<folio>`. Un folio no debería crear miles de palabras diferentes en el vocabulario; la identidad se extrae aparte y se usa para consultar la base.

El vectorizador es `TfidfVectorizer(ngram_range=(1,2), strip_accents='unicode', sublinear_tf=True)`. Usa palabras y pares de palabras. Por ejemplo, «consultar mi folio» puede generar términos y combinaciones que distinguen seguimiento de catálogo.

TF representa presencia/frecuencia de un término en una frase; IDF aumenta el peso relativo de términos menos comunes en el conjunto de entrenamiento. La variante sublineal aplica logaritmo a frecuencias positivas. El vector resultante es disperso: la mayoría de sus posiciones son cero. El vocabulario de esta versión tiene **638 características**.

No son embeddings semánticos neuronales. El modelo no comprende sinónimos nuevos por conocimiento universal; necesita que las características aprendidas sean útiles. Palabras o expresiones no representadas pueden causar confusión o abstención.

### Regresión logística multiclase

El clasificador es `LogisticRegression(C=6, max_iter=1000, random_state=42)`. A pesar del nombre, aquí hace clasificación, no una predicción de una cantidad continua.

Para cada clase aprende pesos que combinan los valores TF-IDF y un sesgo. La salida se transforma en probabilidades entre clases. `C` controla la regularización de forma inversa: valores mayores penalizan menos los pesos. `max_iter` limita los pasos de optimización; no significa entrenar una red de 1,000 capas.

`fit` aprende el vocabulario, los pesos y sesgos a partir de frases etiquetadas. El sistema no guarda una lista de respuestas como si fueran memoria de un modelo generativo. La intención es la clase; las respuestas útiles se construyen después.

### Métricas y límites del resultado

`ml/metricas_asistente.json` registra **accuracy de 75 %: 24 de 32 frases de prueba**, ocho errores. Incluye métricas por intención y matriz de confusión. `ml/prueba_asistente.csv` muestra frase, etiqueta real, predicción y confianza máxima, por lo que se pueden revisar también los errores. `ml/datos/particiones_asistente.csv` identifica las filas de cada partición.

La métrica se calcula con `pipeline.predict`, antes del umbral de abstención de la API. No debe presentarse como precisión de todas las respuestas del chat, como resultado de pruebas con usuarios reales ni como garantía de detectar cualquier pregunta ajena al dominio. Solo hay cuatro ejemplos de prueba por clase; un acierto adicional cambia mucho la métrica de esa clase. Las expresiones parecidas redactadas por la misma fuente también limitan la independencia y generalización de esta evaluación.

La clase fuera de dominio no es un detector universal: en este pequeño test su recall es 25 %. Esto significa que algunas preguntas ajenas se clasifican en otras intenciones. La abstención y el uso de datos/fuentes limitan las consecuencias, pero no eliminan esos errores. Una mejora defendible sería ampliar variedad, errores ortográficos y ejemplos negativos, reservar una prueba independiente y calibrar umbrales con validación separada. No se cambiaron etiquetas ni se ajustaron resultados para fingir 100 %.

### Artefacto e inferencia

`ml/entrenar_asistente.py` guarda `pipeline`, `version`, `umbral` y `sklearn` en `backend/optica/modelo/modelo_asistente.joblib`. Su versión actual es **`asistente-v1-cb544a468f18`**.

El Adapter `ClasificadorIntenciones` transforma el mensaje y obtiene probabilidades. Si no hay términos conocidos, devuelve `fuera_dominio` con confianza 0. Si hay vocabulario pero la máxima probabilidad es menor que **0.30**, devuelve `aclaracion`. En otro caso devuelve la intención ganadora. Aclaración es una política de inferencia, **no una novena clase entrenada**. El umbral es una decisión del prototipo, no una confianza calibrada ni un requisito numérico del profesor.

El clasificador está en caché por proceso. Entrenar un archivo nuevo no cambia el que ya cargó un proceso; hay que reiniciar Django. Las conversaciones tampoco actualizan el dataset automáticamente.

## 9. P2: pregunta → intención → datos → respuesta

La pantalla envía `POST /api/asistente/` con `mensaje` y opcionalmente `folio`. El endpoint acepta también `perfil` como operación programática para delegar a P1. Se limita el mensaje a 1–1000 caracteres y se rechazan campos desconocidos.

`AsistenteService` extrae UUID del texto o del campo separado. Si aparecen dos folios distintos, responde error 400 para evitar una consulta ambigua. Un UUID malformado en el campo `folio` también se rechaza. No hay seguimiento implícito de «el pedido anterior» entre peticiones: el servidor es independiente de la conversación y necesita referencia explícita.

Respuesta mínima y metadatos:

```json
{
  "intencion": "saludo",
  "respuesta": "Hola. Soy el asistente de Lúmina...",
  "confianza_intencion": 0.940955,
  "version_asistente": "asistente-v1-cb544a468f18",
  "fuentes": [],
  "accion": null,
  "datos": {}
}
```

La confianza de intención no es la confianza del paquete de P1 ni el score de similitud de un documento. Son tres cantidades diferentes que deben explicarse por separado.

### Casos importantes

**Catálogo y detalle.** Consulta `CatalogoRepository`, no precios memorizados en el CSV. Si cambia el precio en SQLite, el siguiente mensaje usa el valor actual sin reentrenar. El clasificador identifica la tarea; el código de entidad reconoce nombre o código del paquete, normalizando acentos para los nombres. Si no identifica un paquete, pregunta cuál desea consultar.

**Seguimiento.** Con intención `seguimiento` y un folio válido, consulta `OrdenRepository`. Sin folio lo solicita. Si no existe lo informa; no genera una orden ficticia. El estado se lee de `Orden.estado` y el precio es `precio_confirmado`, no el precio actual del paquete.

**Por qué me salió X.** Con intención `explicar_recomendacion`, recupera `Orden.resultado`: clase original, confianza, paquete confirmado y motivo de reglas. No llama otra vez a `predict_proba`; una explicación histórica debe explicar esa operación, no una posible predicción nueva.

**Recomiéndame.** El chat no interpreta libremente «trabajo mucho frente a pantalla» como cinco entradas completas. Devuelve `accion=abrir_recomendador`, y Flutter ofrece «Completar mi perfil». Si un cliente proporciona un `perfil` estructurado completo, el servicio delega en **el mismo** `OpticaService.recomendar`; no reproduce reglas ni inventa una clase. Esa llamada no registra una orden: sigue faltando confirmación explícita.

**Políticas.** Recupera un fragmento del corpus público y muestra su fuente. Una pregunta sobre horario no permite inventar horas: el documento dice que no existe un horario confirmado para esta óptica ficticia.

**Fuera de dominio y baja confianza.** Delimita capacidades o pide aclarar. No intenta responder fútbol, noticias, inversiones o matemáticas. Esto expresa la intención del diseño; la métrica publicada reconoce que el clasificador pequeño puede equivocarse.

### Por qué no inventa la decisión del recomendador

La única ruta que decide un paquete nuevo es `OpticaService.recomendar`, con cinco características validadas, árbol y reglas actuales. El asistente puede solicitar ese flujo, delegar en él o explicar una decisión guardada. El dataset de intenciones no es una tabla «pregunta → paquete» y el corpus no contiene predicciones particulares. Que la clasificación de intención sea imperfecta no autoriza a fabricar precios, estados ni paquetes.

## 10. Corpus y recuperación: lo que sí hay y lo que no

Se distinguen tres fuentes:

| Fuente | Ejemplos | Cuándo cambia | Cómo se usa |
|---|---|---|---|
| CSV de intenciones | «quiero rastrear mi orden» → seguimiento | Al mejorar entrenamiento | Clasifica la tarea |
| Corpus documental | Alcance, registro, cuidados, garantía, privacidad, horario | Al editar documentos y reindexar | Recupera contexto público |
| Datos vivos de SQLite | Precios, disponibilidad, folio, estado, snapshot | Al modificar/registrar datos | Responde consultas operativas |

`ml/corpus_optica.json` contiene **seis fragmentos** alineados al prototipo, cada uno con `id`, `titulo`, `version`, `audiencia`, `activo` y `contenido`. No se cargó el material defectuoso de la actividad de corpus. No contiene conversaciones, claves privadas ni datos particulares de órdenes.

`ml/indexar_corpus.py` selecciona documentos activos de audiencia pública, ajusta otro vectorizador TF-IDF y guarda vectorizador, matriz, documentos y hash del corpus en `indice_corpus.joblib`.

`RecuperadorCorpus.buscar` vectoriza la pregunta con ese vocabulario y calcula el producto con la matriz documental. Como los vectores TF-IDF están normalizados, el producto corresponde a similitud coseno. Elige **un** documento de mayor score. Si el score es menor que **0.10**, no hay fuente suficiente y se pide aclaración. El score indica coincidencia léxica, no probabilidad de verdad.

La respuesta entrega el contenido del fragmento recuperado y una cita con id, título, versión, origen y similitud. El umbral y `top-1` son decisiones simples de este prototipo, no un sistema avanzado de búsqueda semántica ni una validación de pertinencia infalible.

En términos precisos hay **recuperación documental con respuesta extractiva**. Está inspirada en la separación de corpus de la actividad RAG, pero no utiliza generación aumentada por recuperación mediante un LLM. No hay prompt, fine-tuning generativo, servicio de embeddings, base vectorial externa ni acceso a Internet en el chat. Para el objetivo de P2 basta el clasificador entrenado propio; la recuperación es un apoyo opcional.

El corpus expresa límites reales: no hay horario, instrucciones del fabricante ni políticas comerciales de una tienda en operación. Responder esas limitaciones es más fiel al sistema que inventarlas para una demo. Si se agregaran documentos de una óptica real, habría que verificar responsable, vigencia y permisos de lectura antes de indexar.

Editar JSON sin reindexar deja el índice viejo. Reindexar sin reiniciar Django deja el objeto viejo en caché. El procedimiento correcto es editar → `ml/indexar_corpus.py` → reiniciar backend.

## 11. Flutter: navegación, estado y comunicación

`main.dart` crea `OpticaApp` y un `HomeScreen` con cuatro destinos. `IndexedStack` mantiene sus pantallas montadas: cambiar de pestaña no destruye inmediatamente el formulario ni los mensajes del chat. `setState` actualiza el índice seleccionado; no se incorporó un gestor de estado externo porque el alcance es pequeño.

El cliente tiene tres responsabilidades separadas:

1. **Pantallas:** presentar datos, capturar eventos y mostrar carga/errores.
2. **Modelos Dart:** representar Paquete, Recomendacion y Orden recibidos en JSON.
3. **ApiClient:** construir URLs, codificar/decodificar UTF-8 y JSON, hacer HTTP, timeout y traducir fallos a `ApiException`.

`CatalogScreen` consulta lista y búsqueda; abre detalle. `ProfileScreen` valida y solicita la recomendación. `ResultScreen` muestra probabilidades, ranking y reglas, pide confirmación y registra. `OrderLookupScreen` pide UUID y abre el detalle; `OrderDetailScreen` presenta el snapshot y permite copiar folio.

`ChatScreen` incorpora campo de folio opcional, mensajes, respuestas, botones de ejemplo, indicador de espera y fuentes. Desactiva envío mientras hay una petición pendiente; así se evita entrelazar respuestas por envíos simultáneos desde esa pantalla. Si falla la red conserva el mensaje para reintentar y no agrega una respuesta ficticia. El botón «Completar mi perfil» cambia a la pestaña de P1.

La UI mantiene su historial local, pero no ofrece memoria semántica conversacional. «¿Y por qué?» sin contexto explícito puede no identificarse. El folio se conserva en el campo mientras la pantalla esté montada; no se autentica al comprador ni se persiste el chat en disco.

### URL base y CORS

`ApiClient.defaultUrl` usa `String.fromEnvironment('API_BASE_URL')`, con valor local por defecto `http://127.0.0.1:8000/api`. Se cambia con `--dart-define` al ejecutar o compilar. No basta editar una variable del navegador después de compilar.

En web, 5173 y 8000 son orígenes distintos. `CorsLocalMiddleware` permite explícitamente los orígenes locales configurados y los encabezados JSON/Idempotency-Key. CORS es una política del navegador; no sustituye autorización. La API de demostración no usa cookies de sesión para el comprador y sus vistas JSON están exentas de CSRF; el admin Django conserva su protección normal.

El timeout HTTP es 15 segundos. Los errores de red, JSON inesperado, timeout y errores de dominio se muestran como mensajes legibles. En un emulador Android, `127.0.0.1` sería el propio emulador: la máquina anfitriona se alcanza con `10.0.2.2`. Android incluye INTERNET y HTTP local en debug; una instalación release real debe usar HTTPS.

## 12. Contrato HTTP de los dos proyectos

| Método | Ruta | Uso |
|---|---|---|
| GET | `/api/salud/` | Disponibilidad e identificación de la API |
| GET | `/api/catalogo/?q=Claridad` | Lista activa y búsqueda por nombre |
| GET | `/api/catalogo/esencial/` | Detalle actual |
| POST | `/api/recomendaciones/` | Perfil → modelo + reglas, sin registrar |
| POST | `/api/ordenes/` | Perfil + Idempotency-Key → orden y folio |
| GET | `/api/ordenes/{UUID}/` | Snapshot histórico por folio |
| POST | `/api/asistente/` | Mensaje + folio/perfil opcional → intención y respuesta |

Todos terminan con `/`. Enviar una petición POST a una URL incorrecta puede tener consecuencias distintas de un GET redirigible; usar las rutas documentadas evita depender de redirecciones.

| Estado | Interpretación en este sistema |
|---|---|
| 200 | Consulta, recomendación o asistente correctos; también confirmación repetida equivalente |
| 201 | Orden creada |
| 400 | JSON o entradas inválidas, UUID de referencia inválido o ambigüedad |
| 404 | Recurso de catálogo/orden de su endpoint directo no encontrado |
| 405 | Método no permitido, por ejemplo GET al asistente |
| 409 | Clave de confirmación usada con otro perfil o conflicto de registro |
| 413 | Cuerpo demasiado grande |
| 415 | Tipo de contenido distinto de JSON |
| 422 | Perfil válido pero ningún paquete satisface restricciones |
| 503 | Artefacto requerido no disponible para cargar |

En el chat, «no encontré ese folio» puede venir con HTTP 200: la operación conversacional se procesó y comunica un resultado negativo en `datos.encontrada=false`. El endpoint GET directo sí usa 404 para un folio inexistente. No confundir éxito de transporte con existencia de la entidad.

## 13. Patrones y decisiones que sí se pueden defender

| Patrón / decisión | Archivo propio | Problema que evita |
|---|---|---|
| Strategy / composición de políticas | `reglas.py`, protocolo `Regla` | Mezclar cada restricción con el árbol |
| Adapter de dominio | `recomendador.py`, `Predictor` | Acoplar servicio y UI a DataFrame/classes_/sklearn |
| Adapter del asistente | `clasificador_asistente.py` | Exponer vectores, etiquetas numpy y probabilidades internas a HTTP |
| Repository | `repositories.py` | Repetir consultas ORM en vistas y casos de uso |
| Service Layer | `services.py`, `asistente.py` | Hacer que la vista HTTP coordine validación, modelo, reglas y persistencia |
| Front Controller del framework | `config/urls.py`, `optica/urls.py`, `views.py` | Múltiples entradas independientes sin enrutamiento común |
| Separación comparable a MVC | `screens/`, `models/`, `data/api_client.dart` | Mezclar presentación, representación de datos y transporte |
| Composición de UI | `widgets/common.dart`, pantallas | Duplicar bloques de presentación y mezclar casos de uso |
| Navegación y estado local explícito | `main.dart`, `chat_screen.dart`, `setState` | Perder estado al cambiar de pestaña o enviar durante carga |
| Inyección para pruebas | Constructores de servicios y ApiClient | Necesitar red/base/modelo real para toda prueba aislada |

No hay que llamar MVC estricto a Flutter ni afirmar que un modelo Dart es la IA. Django organiza MVT (modelo, vista y plantillas), pero aquí sus vistas sirven JSON y Flutter hace la presentación. Tampoco es correcto llamar Singleton global distribuido a `lru_cache`: solo mantiene una instancia por proceso Python.

El registro usa transacción e idempotencia; son propiedades de la operación, no nombres GoF que haya que forzar. Las reglas son políticas con una interfaz común; no son diferentes algoritmos de aprendizaje. El despachador de intenciones usa ramas de código porque hay ocho casos; no se inventó un patrón complejo para ocultarlo.

### Qué cambió de P1 a P2

En backend se añadieron dataset, entrenamiento, clasificador, recuperación documental, servicio y endpoint. Los repositorios, modelos de negocio y recomendador P1 se reutilizan. No fue necesaria una nueva tabla para el chat.

En Flutter se añadió `conversar`, `ChatScreen` y un destino de navegación. Los modelos y pantallas del flujo comercial siguen disponibles. El cliente recibe texto, datos y acciones; no interpreta matrices TF-IDF ni decide paquetes.

**Diferencia central de responsabilidad:** el árbol de P1 contesta «qué paquete sugiere este perfil, dadas las reglas»; el modelo de P2 contesta «qué tarea intenta pedir este mensaje». La intención dirige una operación, no sustituye su lógica.

## 14. Cómo instalar, regenerar, probar y ejecutar

Los comandos parten de la carpeta `optica_22121280`, que contiene `backend`, `ml`, `flutter_app` y `scripts`. En este equipo el entorno correcto es `.venv` **dentro de esa carpeta**, Python 3.12. El `.venv` de la carpeta superior y el entorno de otras actividades son distintos.

### Preparar en otro equipo

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
.\.venv\Scripts\python.exe backend\manage.py migrate
.\.venv\Scripts\python.exe backend\manage.py sembrar_demo

.\.venv\Scripts\python.exe ml\generar_datos.py
.\.venv\Scripts\python.exe ml\entrenar.py
.\.venv\Scripts\python.exe ml\generar_intenciones.py
.\.venv\Scripts\python.exe ml\entrenar_asistente.py
.\.venv\Scripts\python.exe ml\indexar_corpus.py

cd flutter_app
flutter pub get
flutter analyze
flutter test
flutter build web --release --dart-define=API_BASE_URL=http://127.0.0.1:8000/api
cd ..
.\.venv\Scripts\python.exe backend\manage.py test optica
.\.venv\Scripts\python.exe scripts\iniciar_demo.py
```

Se recomienda Python 3.12 para las versiones fijadas de estas bibliotecas. En este equipo Flutter está en `C:\dev\flutter\bin\flutter.bat`; puede usarse su ruta completa si no está en PATH. Los entornos virtuales y los SDK no son parte del código que se entrega; se reconstruyen con instrucciones y dependencias.

Ya compilada la versión web, abrir `INICIAR_DEMO.cmd` inicia backend y sitio local. Mantener su terminal abierta; Ctrl+C detiene los procesos que inició. La demo abre `http://127.0.0.1:5173`. También puede iniciarse con `--sin-navegador` para automatización.

**Versión Android.** Se generó `entrega_android/Lumina-Optica-P1-P2.apk`, versión 1.0.0, debug con firma comprobada, para ARM32, ARM64 y x86_64, desde API 24. `ABRIR_ANDROID.cmd` abre el emulador, instala la app y conecta Android al mismo Django mediante `adb reverse tcp:8000 tcp:8000`. Esa redirección permite que el APK use `http://127.0.0.1:8000/api` dentro del dispositivo para alcanzar la PC; sin el túnel, localhost sería Android. El backend y los modelos siguen en la computadora. Las instrucciones están en `entrega_android/LEEME.md` y las comprobaciones nativas en `evidencias/VALIDACION_ANDROID_2026-11-17.md`. La firma de depuración sirve para revisión académica; no es una publicación en una tienda.

Para desarrollo con recarga, ejecutar Django en una terminal y `flutter run -d chrome --web-port=5173 --dart-define=API_BASE_URL=http://127.0.0.1:8000/api` desde `flutter_app` en otra. La compilación web estática no cambia al guardar Dart: hay que reconstruirla.

`backend/.env.example` documenta variables; no se carga automáticamente un archivo `.env`. Para cambiar configuración se exportan variables al proceso. La URL de Flutter se define al compilar y la lista CORS se define en backend; son configuraciones diferentes.

### Qué regenerar según el cambio

| Cambio | Acción necesaria |
|---|---|
| Precio/disponibilidad en SQLite | La próxima consulta usa los datos nuevos; no reentrenar |
| Frases/intenciones | Actualizar dataset, entrenar asistente, evaluar, reiniciar Django |
| Etiquetas de perfiles | Actualizar CSV, entrenar árbol, evaluar, reiniciar Django |
| Texto documental | Editar corpus, reindexar y reiniciar Django |
| Código Dart o URL API | Pruebas y nueva compilación Flutter |
| Esquema Django | Crear/revisar migración y aplicar `migrate` |

## 15. Demostración recomendada de diez minutos

1. **Presentación (30 s):** «Es una óptica ficticia. P1 recomienda un paquete mediante árbol y reglas; P2 entiende preguntas mediante otro modelo y consulta el mismo sistema». Abrir los enlaces a las consignas y la matriz de cumplimiento.
2. **Catálogo (45 s):** mostrar cuatro paquetes, buscar Claridad y abrir detalle. Explicar que vienen de SQLite por JSON.
3. **Perfil (45 s):** mostrar las cinco entradas. Usar pantalla 8, exterior 1, presupuesto 700, oficina, fotocromático desactivado.
4. **Recomendación y reglas (90 s):** mostrar original Claridad 85 %, corrección a Esencial y su confianza real 0 %. Explicar precio, motivo y ranking; distinguir predicción de restricción.
5. **Orden (45 s):** confirmar, copiar folio y mostrar precio/fecha/snapshot. Consultarlo en la pestaña de folio. Explicar que registrar recalcula en servidor e identifica reintentos.
6. **Chat, saludo y catálogo (45 s):** «hola» y «qué paquetes ofrecen». Mostrar que el chat convive con P1 y lee precios actuales.
7. **Chat con folio (60 s):** pegar el folio en referencia y escribir «quiero rastrear mi orden»; después «explica mi orden». Señalar estado real y explicación histórica, sin nuevo cálculo.
8. **Pregunta documental y fuera de dominio (60 s):** «cuál es el horario de atención» muestra una fuente y reconoce que no hay horario confirmado. «quién ganó el partido de fútbol» delimita el dominio.
9. **Enlace al recomendador (30 s):** «qué paquete me recomiendas» y botón «Completar mi perfil». No escribir una clase inventada en el chat.
10. **Construcción y evaluación (90 s):** abrir scripts y métricas: 1,200 perfiles/93.75 %, 160 frases/75 %, particiones separadas y tres artefactos. Mostrar patrones con archivos reales y el registro de pruebas.

Si hay poco tiempo, conserva el caso corregido, el folio y la explicación por chat. Esas tres acciones muestran la integración entre modelo, reglas, datos, backend y cliente.

## 16. Preguntas de defensa y respuestas preparadas

### Sobre propósito y arquitectura

**1. ¿Qué problema resuelve?** Ayuda a elegir un paquete comercial entre cuatro opciones dadas unas características y restricciones; registra una solicitud trazable y permite consultar/explicar el resultado mediante pantallas y chat.

**2. ¿Qué parte es web y cuál móvil?** Django expone una API web JSON. Flutter es el cliente compartido, ejecutado aquí como web compilada; el proyecto incluye soporte Android. El modelo solo corre en Django. No presentar como probada una instalación Android si solo se ejecutó navegador.

**3. ¿Por qué SQLite?** Está requerido para esta etapa y permite persistencia relacional local con migraciones y ORM, suficiente para la demo. No se está afirmando que sea la base ideal para todas las cargas de producción.

**4. ¿Es una arquitectura de microservicios?** No. Ambos modelos y los casos de uso están en el monolito Django. Servir Flutter estático aparte no convierte la lógica de negocio en microservicios. Esa evolución corresponde a P3.

**5. ¿Por qué JSON y no acceso directo a la base desde Flutter?** Para separar responsabilidades y mantener validación, reglas y persistencia bajo control del servidor. Flutter no necesita credenciales ni detalles de tablas.

**6. ¿Qué se tomó de los apuntes?** La tubería de entrenamiento y artefacto, integración modelo + reglas, API con SQLite, cliente Flutter, folio, clasificación de intenciones, separación de fuentes y análisis de patrones. El dominio, datos y decisiones comerciales se adaptaron a óptica.

### Sobre el recomendador

**7. ¿De dónde salieron los datos?** De un generador sintético determinista de 1,200 perfiles, no de pacientes ni compradores. La política de etiquetas y el ruido están en `generar_datos.py`.

**8. ¿Qué significa entrenar?** Ajustar un algoritmo con ejemplos etiquetados para que encuentre divisiones que predigan la clase. En P1 se aprende un árbol; cargar el `.joblib` no es entrenarlo.

**9. ¿Por qué separar prueba?** Para medir sobre ejemplos no usados en `fit`. Si se evaluara solo entrenamiento se podría ocultar sobreajuste. La prueba sintética sigue siendo una estimación limitada del mismo generador.

**10. ¿Por qué OneHotEncoder?** Porque uso principal no tiene orden numérico. Una columna por categoría evita sugerir que oficina es «mayor» que estudio.

**11. ¿Por qué no escalar?** El árbol aprende comparaciones con umbrales de cada característica. No usa distancias entre todas las dimensiones como lo haría un vecino más cercano.

**12. ¿Por qué árbol y no una red neuronal?** Es suficiente para relaciones simples, se integra con el ejemplo de clase, permite `predict_proba` y se puede inspeccionar en texto. La complejidad adicional no está justificada por el tamaño ni la naturaleza sintética de los datos.

**13. ¿Qué significa 93.75 %?** Que acertó 225 etiquetas de 240 perfiles sintéticos separados para prueba. No es eficacia de lentes ni precisión global de todas las pantallas.

**14. ¿Si hay reglas, para qué el modelo?** El modelo ordena preferencias aprendidas de etiquetas; las reglas imponen restricciones actuales que no deben incumplirse. Son capas con objetivos distintos. La política sintética es deliberadamente simple y se reconoce que se podría resolver directamente con reglas en este ejercicio; el objetivo académico es integrar un modelo real y explicar sus límites.

**15. ¿Por qué el presupuesto está en X si una regla lo verifica?** Se conserva como variable de perfil, aunque la etiqueta simulada no garantiza respetarlo. Que sea una entrada no significa que el árbol le asigne importancia. La regla independiente es la garantía operacional de presupuesto.

**16. ¿El 0 % de Esencial es un error de interfaz?** No. Es la probabilidad real del árbol para esa clase en ese perfil. La regla puede llegar a una alternativa elegible sin masa en esa hoja; se informa sin inflarla.

**17. ¿Qué ocurre si todas las clases se descartan?** HTTP 422, sin crear Orden. La UI presenta el motivo y permite cambiar el perfil.

**18. ¿Qué pasa si el catálogo añade una quinta clase?** El modelo de cuatro clases no la propondrá automáticamente. Habría que definir etiquetas/datos, reentrenar, evaluar y revisar UI/reglas. Cambiar el precio de una clase existente sí se refleja sin reentrenar.

**19. ¿Cómo sabes qué archivo de modelo produjo una orden?** El snapshot incluye `version_modelo`. Su versión usa hash del CSV y se conserva junto con scripts y métricas para trazabilidad.

**20. ¿Qué harías para usarlo con clientes reales?** Definir objetivo comercial verificable, reunir datos consentidos y etiquetas adecuadas, evaluar con una prueba representativa y revisar reglas/abstención. Ninguna exactitud del generador sintético reemplaza esa validación.

### Sobre órdenes y consistencia

**21. ¿Por qué recalcular al confirmar?** Porque el cliente es manipulable y el catálogo puede cambiar desde la previsualización. El servidor decide lo que registra.

**22. ¿Qué evita dos órdenes por doble clic?** UI en espera, clave idempotente y unicidad en base. Un reintento equivalente recupera la misma orden. La propiedad no depende únicamente de deshabilitar un botón.

**23. ¿Por qué guardar JSON si ya existe una FK?** La FK conserva relación; el snapshot conserva lo que se vio y decidió en ese momento. El producto actual puede cambiar de nombre/precio y no debe reescribir el pasado.

**24. ¿Por qué Decimal para precios?** Para almacenar cantidades monetarias con precisión decimal y dos posiciones, evitando errores de representación binaria en el precio persistido.

**25. ¿El folio funciona como contraseña?** No. Es un identificador. La consulta pública local es suficiente para la demostración; una solución real necesita identidad y permisos sobre la orden.

### Sobre el asistente

**26. ¿Es ChatGPT o tiene una API comercial?** No. Es un Pipeline local TF-IDF + regresión logística entrenado con frases del dominio. No usa token de proveedor ni Internet para responder.

**27. ¿Qué aprendió exactamente?** A asociar patrones de términos y pares de términos con ocho intenciones. No aprendió precios, estados de órdenes ni una graduación.

**28. ¿Cómo se alimentó?** Se redactaron 160 consultas etiquetadas, se normalizaron y se separaron 128/32 estratificadas. El script ajustó vocabulario y clasificador solo con entrenamiento y guardó el Pipeline.

**29. ¿Qué significa TF-IDF?** Una representación numérica de términos que combina su frecuencia en el texto y su rareza en el corpus de entrenamiento. Permite que un algoritmo de clasificación procese texto.

**30. ¿Por qué regresión logística si no predices números?** Es un algoritmo de clasificación probabilística; en multiclase aprende una puntuación por intención y produce una distribución entre ellas.

**31. ¿Qué significa el 75 %?** Veinticuatro intenciones correctas de 32 frases reservadas. No demuestra que el 75 % de cualquier conversación real quede resuelta ni que todos los errores se detecten por umbral.

**32. ¿Por qué no respondes siempre la clase ganadora?** Porque puede haber señal insuficiente. Cero vocabulario conocido se trata como fuera de dominio y confianza máxima menor de 0.30 provoca aclaración. Ese umbral debe mejorarse con validación si crece el sistema.

**33. ¿Puede equivocarse con preguntas ajenas?** Sí. La prueba muestra ese límite, especialmente en recall fuera de dominio. Por eso se restringe a operaciones con datos reales, se piden folios/perfiles y se explicitan fuentes y ausencias.

**34. ¿No son respuestas fijas?** El saludo y textos de control usan plantillas, pero la intención la selecciona un modelo entrenado y el contenido de precios/folios viene de consultas. El requisito no pide generar lenguaje libre; sí pide entrenamiento propio y conexión con datos.

**35. ¿Por qué no decide el asistente qué paquete darme?** Su objetivo es reconocer la solicitud, no resolver la clasificación del perfil. Para una decisión nueva usa el formulario o el mismo servicio P1; para una explicación usa el snapshot.

**36. ¿Qué pasa si digo «por qué me salió Esencial» sin folio?** Aunque identifique explicación, no sabe cuál operación histórica consultar. Solicita el UUID. No inventa un perfil ni asume una orden global previa.

**37. ¿Qué sucede si la orden no existe?** El chat informa que no encontró la solicitud. No fabrica estado, entrega o precio y no crea una orden para satisfacer la pregunta.

**38. ¿El bot recuerda conversaciones anteriores?** La UI conserva mensajes mientras vive la pantalla, pero el servidor no tiene memoria conversacional persistente. Cada petición debe incluir las referencias necesarias.

**39. ¿Reentrena cuando converso?** No. Los mensajes no se añaden automáticamente al dataset. La mejora del modelo se hace fuera de HTTP, con nuevas etiquetas y evaluación.

### Sobre corpus y patrones

**40. ¿Dataset y corpus son lo mismo?** No. Las frases etiquetadas entrenan qué tarea reconocer. Los documentos públicos apoyan respuestas de contenido. Los datos vivos responden precios/folios y no deben congelarse como texto entrenado.

**41. ¿Tienes RAG generativo?** No hay LLM. Hay recuperación TF-IDF y respuesta extractiva con fuentes; se aprovechó la separación documental de la actividad de corpus. Es más exacto describirlo así que afirmar que se afinó un modelo generativo.

**42. ¿La similitud 0.6 significa 60 % de verdad?** No. Es cercanía léxica normalizada entre pregunta y documento. La verdad depende de la fuente y su vigencia.

**43. ¿Qué pasa si pregunta un horario que no existe?** El documento vigente dice que no hay horario confirmado de una tienda real. El asistente muestra ese límite con fuente, sin inventar apertura/citas.

**44. ¿Dónde está Adapter?** En `recomendador.py` y `clasificador_asistente.py`, que traducen entradas/salidas de scikit-learn al contrato del dominio. En el primero DataFrame/probabilidades → ranking, en el segundo texto/probabilidades → intención/confianza/versión.

**45. ¿Dónde está Repository?** En dos objetos explícitos que encapsulan ORM: catálogo y órdenes. El nombre no se adjudica al ORM entero; se puede mostrar dónde los servicios los consumen.

**46. ¿Dónde está Strategy?** En las políticas `ReglaPresupuesto`, `ReglaDisponibilidad` y `ReglaPreferencia` con la misma operación. Se componen para evaluar elegibilidad, separadas de inferencia.

**47. ¿Dónde está MVC?** Existe separación de presentación, representaciones y transporte comparable a MVC, sin declarar que Flutter imponga un MVC estricto. Las pantallas coordinan eventos locales; la lógica de dominio está en Django.

**48. ¿Por qué mantener estado local?** Porque formularios y chat son pequeños y pertenecen a pantallas concretas. `IndexedStack` conserva pantallas y `setState` actualiza carga/mensajes. Si creciera el estado compartido, se evaluaría otra solución.

**49. ¿Cómo pruebas que no son pantallas desconectadas?** Mediante tests del backend con modelos reales, tests Flutter de contratos/estados, build y recorrido en navegador compilado contra API real. Las capturas y JSON contienen el mismo folio usado en el chat.

**50. ¿Qué no debes afirmar en la presentación?** Que hubo clientes reales, diagnósticos, LLM entrenado desde cero, precisión universal, prueba Android inexistente, autorización por usuario, pagos o microservicios. Describir con claridad el alcance implementado demuestra comprensión.

## 17. Fallos comunes y diagnóstico

| Síntoma | Comprobación / corrección |
|---|---|
| No abre 5173 | Verificar que la demo siga activa y exista `flutter_app/build/web/index.html` |
| Abre la UI pero no carga catálogo | Visitar `http://127.0.0.1:8000/api/salud/`; revisar URL compilada, puerto y CORS |
| Error de `.joblib` | Usar `.venv` de la aplicación y dependencias fijadas; regenerar con su Python y reiniciar Django |
| No hay paquetes | Aplicar migraciones y ejecutar `sembrar_demo` antes de la presentación |
| 422 al recomendar | Leer restricciones: es posible que presupuesto/preferencia no permitan ninguna opción |
| 409 al confirmar | Una clave ya se usó con otro perfil; no reutilizar claves arbitrarias entre operaciones nuevas |
| El chat pide aclaración | Reformular con una tarea específica; revisar predicción y métricas, no atribuir comprensión universal |
| No encuentra folio | Copiar UUID completo y usar la misma base de datos/servidor donde se creó |
| Cambié corpus pero responde igual | Reindexar y reiniciar backend; el índice y la caché son independientes del JSON editable |
| Cambié Dart pero veo interfaz vieja | Recompilar y recargar navegador; el servidor estático no compila Dart |
| Puerto ocupado | Identificar la demo anterior y detener su propia terminal; no terminar procesos ajenos a ciegas |
| Android no llega a localhost | Usar `10.0.2.2` en emulador y revisar hosts; no es la misma dirección que en web |

## 18. Qué evidencia estudiar antes de exponer

Leer primero la matriz, ejecutar el caso de $700, copiar un folio y pedir su explicación en el chat. Después abrir `ml/generar_datos.py`, `ml/entrenar.py`, `ml/metricas.json`, `ml/generar_intenciones.py`, `ml/entrenar_asistente.py` y `ml/metricas_asistente.json`. Revisar al menos dos errores de `ml/prueba_asistente.csv`, no solo frases que funcionaron.

Luego seguir una petición desde `ApiClient` a `urls`, `views`, servicio, Adapter/repositorio y respuesta. Explicar esa ruta con archivos abiertos da más sustento que memorizar nombres de patrones. Practicar la diferencia entre predicción, regla, consulta de datos y presentación: son las cuatro distinciones que atraviesan ambos proyectos.

Los PDFs `Avance_Analisis_22121280.pdf` y `Analisis_Patrones_22121280.pdf`, la guía `GUIA_CONSTRUCCION.md` y `RELACION_APUNTES.md` ya existían y documentaban P1. Esta guía, la matriz conjunta y el análisis P1/P2 actualizados explican la extensión efectivamente construida. La verificación corresponde a los requisitos publicados, no sustituye la evaluación del profesor.
