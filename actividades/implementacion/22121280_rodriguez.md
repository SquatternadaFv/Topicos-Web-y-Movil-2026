# Actividad individual — Lo que hay detrás de la implementación

Nombre: Eduardo Osvaldo Rodríguez Gutiérrez
Matrícula: 22121280
Equipo: Eduardo Osvaldo Rodríguez Gutiérrez; Diego Soria Magos; Gonzalo García Chavez; Diego Rivera Cisneros; Rodrigo Vega Espinoza.

## A1

Los dos tienen una parte de razón y una parte equivocada.

**Ana.** Es cierto que Docker puede ejecutar todo el proyecto sin instalar Python ni las dependencias en la computadora. Es falso que el entorno virtual sobre: sirve para desarrollar en local (editar, probar, correr `runserver`, instalar paquetes) sin ensuciar el Python del sistema ni mezclar versiones con otros proyectos. Y dentro de la imagen las dependencias se instalan desde el mismo `requirements.txt` que mantenemos en el entorno virtual.

**Luis.** Es cierto que para desarrollar un entorno virtual basta. Es falso que abrir más terminales con `runserver` sirva para atender más gente: `runserver` es un servidor de desarrollo, no está hecho para carga ni seguridad. Cada terminal sería una copia en otro puerto, con su propia memoria, y nadie reparte las peticiones entre ellas (no hay balanceador). Además, no es reproducible ni automatizable.

**Qué aísla cada uno.** El entorno virtual aísla solo los paquetes de Python de un proyecto (su propia carpeta de librerías); comparte con el resto el sistema operativo, las librerías del sistema y el Python base. El contenedor aísla un entorno completo: sistema de archivos, procesos, red, Python, librerías del sistema y dependencias. Por eso corre igual en cualquier máquina.

**Uso en el curso.** El entorno virtual lo usamos para desarrollar en nuestra computadora. El contenedor lo usamos para empaquetar la plataforma, ejecutarla como en producción (Gunicorn + nginx + PostgreSQL) y poder tener varias copias.

## A2

a) **No perdió su código.** El código (`.py`, plantillas, etc.) está en la carpeta del proyecto, fuera de `.venv`. La carpeta `.venv` solo contiene el intérprete y los paquetes instalados, es desechable y por eso ni siquiera se sube a Git.

b) Necesita recrear el entorno (`python -m venv .venv`), activarlo e instalar las dependencias con `pip install -r requirements.txt`. El archivo `requirements.txt` es la receta: lista los paquetes y sus versiones, de modo que se reconstruye exactamente el mismo entorno. Sin ese archivo tendría que acordarse de qué instaló y en qué versión.

c) **Activar no instala nada.** Solo modifica las variables de la terminal actual (sobre todo `PATH`) para que los comandos `python` y `pip` apunten a los del `.venv` y no a los del sistema. Como el cambio solo vive en esa sesión de terminal, al abrir otra terminal `PATH` vuelve a ser el original y hay que activar de nuevo.

## A3

a) `/app` existe **dentro de la imagen y del contenedor**, no en la computadora. `WORKDIR /app` lo crea en la imagen y lo deja como directorio de trabajo. `COPY . .` copia el contenido de la carpeta del proyecto (el contexto de construcción, menos lo que excluye `.dockerignore`) al directorio actual del contenedor, o sea `/app`. Primero se copia solo `requirements.txt` para aprovechar la caché de capas: si el código cambia pero las dependencias no, no se reinstalan.

b) `.venv/` se excluye porque es un entorno armado para *mi* máquina (rutas y binarios de mi sistema operativo, distinto del Linux del contenedor), es pesado y es innecesario: en la imagen las dependencias ya se instalaron con `pip install`. Copiarlo inflaría la imagen y podría estorbar. `db.sqlite3` se excluye porque contiene datos locales de desarrollo; si se copiara, esos datos quedarían dentro de la imagen y cada copia arrancaría con su propia base, además de filtrar información de prueba. La base de datos no debe vivir dentro de la imagen.

## B1

a) La regla estaría duplicada: habría que reescribirla en la app móvil (otro lenguaje), y las dos versiones acabarían diferentes. Cambiar una regla obligaría a actualizar la web y también todas las apps ya instaladas, que mucha gente no actualiza. Además, el código del navegador lo puede ver y manipular cualquiera, así que la regla se puede saltar, y no hay un solo lugar donde probarla.

b) Porque en un buen diseño el frontend solo muestra y captura datos, y toda la lógica está en el backend. Lo único que el backend le entrega al frontend son **datos** (JSON) con un formato acordado, no decisiones ni pantallas. Mientras se respete ese formato, se puede cambiar la web por una app móvil u otra interfaz sin tocar el backend.

## B2

La app móvil ya instalada sigue esperando la clave `medios_disponibles`. Al recibir `medios` no la encuentra: mostraría una lista vacía o fallaría, y no se puede corregir en el mismo día porque está en miles de teléfonos. Solo se actualizó la página web, que sí controlamos.

El **contrato** es el acuerdo entre backend y frontend sobre las direcciones, los métodos, los nombres de los campos, sus tipos y su significado. Todo cliente se construye confiando en él, así que cambiarlo rompe a los clientes.

El campo `version` permite hacer cambios incompatibles sin romper a los clientes viejos: la versión 1 sigue respondiendo como siempre y se publica una versión 2 con el nombre nuevo. Cada cliente sabe qué formato recibe y se migra poco a poco. Agregar un campo nuevo es compatible; renombrar o quitar uno no lo es.

## B3

**No estamos de acuerdo.** La validación del frontend es una comodidad para el usuario: avisa rápido y evita viajes innecesarios al servidor. Pero no es una barrera, porque cualquiera puede mandar peticiones directas al backend (con otra aplicación, `curl`, una versión vieja de la app o un navegador manipulado) y saltarse la validación del cliente. La validación del backend es la que protege los datos y las reglas: sin ella entrarían paquetes sin peso o con números inválidos que provocarían errores 500, datos corruptos en la base o recomendaciones absurdas. El backend nunca debe confiar en el cliente. Se necesitan las dos: la del frontend por experiencia de uso y la del backend por seguridad y consistencia (respondiendo, por ejemplo, un 400 con un mensaje claro).

## C1

a) Escalar **verticalmente** es darle más recursos (CPU, memoria) a una sola máquina o contenedor. Escalar **horizontalmente** es tener más copias del mismo servicio funcionando en paralelo.

b) Tiene un límite físico y económico (hay una máquina máxima y el costo sube más rápido que el rendimiento), sigue habiendo un solo punto de falla (si cae esa máquina cae todo) y suele requerir reiniciar.

c) nginx es el único punto de entrada: recibe todas las peticiones y las reparte entre las tres copias de Django (por defecto, por turnos). Para el cliente existe una sola dirección. También puede dejar de mandar peticiones a una copia que no responda.

## C2

a) Cada copia es un contenedor distinto, con su propio proceso y su propia memoria. `pedidos_en_memoria` es un diccionario que vive en la RAM de un proceso, así que solo el proceso que registró el pedido lo tiene. Las otras copias no comparten esa memoria, y nginx reparte las peticiones sin saber dónde quedó el pedido.

b) Porque cada copia arranca Gunicorn con `--workers 2`, o sea **dos procesos independientes**, cada uno con su propio diccionario. El registro cayó en uno de los dos workers de `e6c28e82ce8f`, y la consulta posterior llegó al otro worker de esa misma copia, que tiene un diccionario vacío. Con tres copias hay en realidad seis diccionarios separados.

c) **No tiene razón.** El defecto estaba en el código: guardar datos importantes en la memoria del proceso. Con `runserver` (un solo proceso) el problema no se veía; Docker con varias copias solo lo dejó al descubierto. La solución es guardar los pedidos en un lugar compartido, como PostgreSQL.

## C3

Con una variable global, el destino queda en la memoria de un proceso concreto. Entre el primer paso y la confirmación, la segunda petición puede caer en otra copia o en otro worker que no lo tiene. Además, esa variable la comparten todos los usuarios que caigan en ese proceso, así que dos personas registrando pedidos al mismo tiempo se pisarían el destino.

`request.session` sí funciona porque el dato no vive en la memoria del proceso: Django lo guarda en un almacén y le da al navegador una cookie con un identificador de sesión propio de cada usuario. Cualquier copia que reciba la petición lee esa cookie y recupera la sesión de ese usuario en el almacén compartido. La clave es que lo que se recuerda entre peticiones esté en un lugar al que todas las copias accedan.

En nuestro proyecto, Django guarda la sesión en la base de datos (tabla `django_session`, en PostgreSQL), que es el comportamiento por defecto. <!-- AJUSTA: revisa en tu settings.py si SESSION_ENGINE es otro (cache, etc.) y corrige esta frase -->

## C4

a) Con cinco copias el aviso de las 8:00 se enviaría **cinco veces** a cada cliente, porque cada copia ejecuta su propio programa de tareas. Esa tarea debe vivir en un único lugar que corra una sola vez: un servicio aparte de tareas programadas (un contenedor con una sola instancia, `cron` o un planificador como Celery beat), no dentro de las copias que atienden peticiones web.

b) Las migraciones cambian el esquema de la base de datos y deben ejecutarse una sola vez. Si cada copia las ejecutara al arrancar, varias intentarían modificar la base al mismo tiempo (bloqueos, errores, estados a medias). Con un servicio `migrar` aparte, se ejecutan una vez, terminan, y las copias web arrancan después, cuando el esquema ya está listo.

c) 20 copias × 4 procesos = **80 conexiones** a PostgreSQL (suponiendo una conexión por proceso). Con un máximo de 100 solo quedan 20 de margen: con 26 copias ya se pasaría de 100 y PostgreSQL rechazaría conexiones. La conclusión es que no se pueden agregar copias «sin límite»: la base de datos compartida se vuelve el nuevo cuello de botella, y habría que limitar copias y workers, aumentar el máximo de conexiones o usar un agrupador de conexiones. SQLite deja de servir porque es un archivo local pensado para un proceso: cada contenedor tendría su propio archivo (cada copia vería datos distintos) y no soporta bien muchas escrituras concurrentes ni acceso por red. Con varias copias se necesita una base de datos que sea un servicio compartido, como PostgreSQL.

## D1

a) Porque se evaluó con los mismos datos con los que se entrenó. El árbol ya los vio y puede memorizarlos (un árbol sin límite puede acertar casi todo el entrenamiento). Ese número mide memoria, no si el modelo funcionará con envíos nuevos, que es lo que importa.

b) `train_test_split` aparta un 20 % que el modelo nunca ve al entrenar. Al evaluar con esos datos se estima cómo se comportará con casos nuevos y se detecta el sobreajuste.

c) `stratify=y` hace que entrenamiento y prueba conserven la misma proporción de cada clase. En este dataset el dron es una clase minoritaria (pocos envíos). Sin estratificar, por azar la prueba podría tener muy pocos drones (o ninguno) y las métricas del dron serían poco confiables, o el entrenamiento vería muy pocos ejemplos de esa clase. <!-- AJUSTA: pon el porcentaje o número real de envíos de dron que viste en tu dataset -->

## D2

Con despejado = 0, lluvia = 1 y viento_fuerte = 2 se le da al árbol la idea falsa de que hay un **orden y una distancia** entre los climas: que viento_fuerte «es más» que lluvia, que lluvia está «entre» los otros dos y que despejado y viento_fuerte están lejos. Sin embargo, esas categorías no tienen orden. El árbol corta con preguntas del tipo «clima ≤ 1.5», que agrupan categorías sin relación real.

El **one-hot encoding** crea una columna 0/1 por categoría (`clima_lluvia`, `clima_despejado`…), cada una independiente, sin orden ni distancia entre ellas.

Se guardan la preparación y el árbol juntos en un **Pipeline** para que el modelo aplique, al predecir, exactamente la misma transformación aprendida al entrenar (mismas columnas, mismo orden, mismas categorías). Así se evita que, con un paquete nuevo, se haga el one-hot por separado o distinto y el árbol reciba columnas desalineadas, lo que daría predicciones equivocadas sin avisar.

## D3

a) Porque el árbol sin límite crece hasta ajustarse a casos raros y ruido del entrenamiento (346 hojas, casi una por caso particular) y deja de generalizar bien. Ese fenómeno se llama **sobreajuste** (*overfitting*). Un árbol más pequeño aprende las reglas generales y acierta más con datos nuevos.

b) La diferencia entre 92.1 % y 92.4 % es de 0.3 puntos, tan pequeña que puede ser ruido de la muestra de prueba. A cambio, el de profundidad 10 tiene casi el doble de hojas (92 contra 47): es más complejo, más difícil de leer y explicar, y está más cerca del sobreajuste. Con un rendimiento prácticamente igual, conviene el modelo más simple.

## D4

a) **Precisión 0.839:** de todos los paquetes que el modelo mandó en dron, el 83.9 % realmente podía ir en dron (el 16.1 % restante no debía). **Recall 0.905:** de todos los paquetes que realmente podían ir en dron, el modelo reconoció el 90.5 % (se le escapó el 9.5 %).

b) Para la empresa es más grave mandar en dron un paquete que no debía ir (falso positivo), porque implica riesgo operativo y de seguridad (distancia, peso, clima), con posible pérdida del paquete o del dron. Ese error lo mide la **precisión**. No reconocer un paquete que sí podía ir en dron (falso negativo) solo hace que se mande por un medio más lento o caro, es una pérdida de eficiencia. Ese error lo mide el **recall**. Por eso, en el dron importa cuidar sobre todo la precisión.

c) Porque los datos tienen casos de frontera, ruido e información que el modelo no ve, y limitamos la profundidad para no sobreajustar. Eso no es necesariamente malo: un 100 % en la prueba sería sospechoso (sobreajuste o fuga de datos). Un modelo que generaliza bien comete algunos errores, y para eso están las reglas del negocio como segunda barrera.

## D5

**Respuesta al jefe de logística:** no conviene elegir siempre el que acierte más, porque la ventaja es de solo un punto (92.1 % contra 93.1 %) y cuesta mucho. Argumentos que no son la exactitud:

1. **Interpretabilidad:** las reglas del árbol se pueden leer, auditar y explicar a un cliente o a un auditor (por qué se mandó un paquete en dron) y sirven para depurar errores. El bosque es una caja negra.
2. **Tamaño y costo de operación:** 14 KB contra 60 MB. El bosque hace la imagen más pesada, tarda más en cargar y ocupa mucha más memoria, y como el modelo se carga en cada proceso (cada worker de cada copia), el gasto se multiplica por todos ellos. También suele ser más lento al predecir.

**En la vista de Django casi no cambia nada**, porque la vista depende de la abstracción `RecomendadorIA` y no del modelo concreto. Solo habría que cambiar la clase concreta que devuelve `obtener_recomendador()` (un recomendador de bosque en lugar de `RecomendadorArbol`) y el archivo `.joblib`. Esto es posible porque el diseño separa lo que la vista necesita (una recomendación) de cómo se obtiene. Lo único que sí habría que revisar es el texto del motivo y los recursos (memoria) de cada copia.

## E1

a) El árbol no «entiende» que de noche los drones no vuelan: solo aprende patrones de los datos de entrenamiento. Si de noche hay pocos ejemplos o la hora aparece mezclada con otras variables (distancia y peso), puede aprender que con un paquete ligero y 13 km conviene dron sin pesar la hora. Además, la hora es una variable circular (las 23:00 y las 0:00 están cerca) y el árbol la trata como un número lineal con cortes simples.

b) Un modelo más grande se sobreajusta (como en D3) y nunca llega a cero errores. Además, una restricción como «no volar de noche» es una obligación del negocio y no una probabilidad: un modelo estadístico no la garantiza. Las reglas son deterministas, se pueden auditar y cambiar sin reentrenar nada.

c) Por separación de responsabilidades. Las reglas del negocio no dependen de qué modelo recomiende (árbol, bosque, servicio externo). Si estuvieran dentro del recomendador del árbol, al cambiar de modelo habría que copiarlas (o se perderían). En `reglas.py` están en un solo lugar y se aplican igual a cualquier recomendador, y se pueden probar por separado.

## E2

**No es una contradicción.** La regla de no guardar nada importante en memoria se refiere al **estado que cambia con las peticiones y que otras copias necesitan ver** (pedidos, sesiones). Un pedido es un dato nuevo, cambia, lo escribe una copia y lo deben leer todas, y no se puede perder. El modelo en cambio es de **solo lectura**, es idéntico en todas las copias (viene en la imagen en el archivo `.joblib`) y si se pierde de la memoria se vuelve a cargar sin perder nada. Por eso no genera inconsistencias.

Si cada petición cargara el archivo `.joblib`, habría que leerlo del disco y reconstruirlo en cada petición: más latencia, más uso de CPU y de disco, y más memoria momentánea, especialmente con un modelo grande. `lru_cache(maxsize=1)` lo carga una sola vez por proceso y lo reutiliza.

## E3

Un modelo guardado con `joblib` depende de la estructura interna de las clases de scikit-learn de la versión con la que se entrenó. Si en `requirements.txt` solo está `scikit-learn` sin versión, al construir la imagen meses después `pip` instala la versión más reciente, cuya estructura interna puede ser distinta: el modelo no carga, o peor, carga y predice mal sin avisar.

Se evita **fijando la versión exacta** (`scikit-learn==1.9.0`) en `requirements.txt`, entrenando y sirviendo el modelo con las mismas versiones (por ejemplo, reentrenando dentro del entorno del contenedor) y guardando la versión usada junto al modelo.

Esto es justo la razón de ser del entorno virtual y del contenedor de la sección A: lograr un entorno **reproducible**, con el mismo Python y las mismas versiones de paquetes en mi laptop y en producción. `requirements.txt` es la receta de esa reproducibilidad; sin ella, «funciona en mi computadora» no se puede repetir en otro lado.

## F1

a) Hay que escribir una clase nueva, por ejemplo `RecomendadorServicioExterno`, que implemente la misma interfaz que `RecomendadorIA`. Dentro llama al servicio externo y **traduce** su respuesta (`"vehiculo": "DRONE"`, `"certeza": "alta"`) al formato que usa la plataforma (el medio `dron` y una confianza en el formato interno). El patrón es **Adapter** (adapta una interfaz ajena a la nuestra), y se conecta como una estrategia más del recomendador (Strategy). No cambian: la vista, las reglas del negocio (`reglas.py`), la fábrica `crear_medio`, las estrategias de entrega (`EntregaDron`, `EntregaMotocicleta`…) y el contrato JSON con el frontend. Solo cambia qué recomendador devuelve `obtener_recomendador()`.

b) Recorrido de un paquete:

1. Llega a `/entregas/recomendar/` (nginx lo manda a una copia) y la vista valida los datos. *Diseño.*
2. El recomendador propone un medio y una confianza. **Esta es la única parte que hace la IA.**
3. Las reglas del negocio revisan y, si hace falta, descartan la propuesta (como el dron a las 3:00). *Diseño.*
4. La fábrica `crear_medio` convierte el medio elegido en el objeto de entrega correspondiente. *Diseño.*
5. La estrategia de entrega calcula el plan (tiempo, costo, etc.). *Diseño.*
6. La vista responde con el JSON del contrato. *Diseño.*

La IA decide «qué medio», pero todo lo demás (validar, aplicar restricciones, crear y ejecutar la entrega, responder y escalar) sigue necesitando diseño.

c) Argumentos contra borrar los patrones:

1. **Si el servicio se cae o tarda:** si la vista llama directo al servicio, la plataforma entera deja de recomendar. Con la abstracción `RecomendadorIA` se puede poner un respaldo (el árbol local o reglas simples), un tiempo máximo de espera y el manejo de errores en un solo lugar.
2. **Si mañana se cambia de proveedor:** cambiaría el formato y el vocabulario (`DRONE` contra `dron`). Con el adaptador se reescribe una sola clase; sin él habría que tocar la vista y todo lo que dependa de esa respuesta.
3. **La IA no sustituye las reglas, la fábrica ni las estrategias:** el servicio puede proponer algo que el negocio no permite (E1), y devuelve solo un texto (`"DRONE"`), no un objeto. Alguien tiene que convertirlo en el objeto adecuado (fábrica) y cada medio calcula su plan de forma distinta (estrategias). Además, con la abstracción se puede probar sin llamar al servicio real.

La IA cambia quién toma la decisión, pero el resto del sistema sigue necesitando una estructura que la reciba, la valide y la ejecute, y que aguante que esa decisión, o quien la toma, cambie.

