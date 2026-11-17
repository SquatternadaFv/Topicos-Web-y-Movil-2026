"""Genera los dos informes entregables. Dependencia documental: reportlab."""
from pathlib import Path
import json
import os
from datetime import date
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT
from xml.sax.saxutils import escape
from PIL import Image as PILImage

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs'
FECHA_ENTREGA = date.fromisoformat(os.getenv('FECHA_ENTREGA', '2026-11-12'))
MESES = ('enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre')
FECHA_TEXTO = f'{FECHA_ENTREGA.day} de {MESES[FECHA_ENTREGA.month-1]} de {FECHA_ENTREGA.year}'
# Fuentes Unicode disponibles en Windows y Linux, sin modificar el script.
if os.name == 'nt':
    FONT = Path(os.getenv('WINDIR', 'C:/Windows')) / 'Fonts'
    normal, bold = FONT / 'arial.ttf', FONT / 'arialbd.ttf'
else:
    FONT = Path('/usr/share/fonts/truetype/dejavu')
    normal, bold = FONT / 'DejaVuSans.ttf', FONT / 'DejaVuSans-Bold.ttf'
pdfmetrics.registerFont(TTFont('DV', str(normal)))
pdfmetrics.registerFont(TTFont('DVB', str(bold)))
pdfmetrics.registerFontFamily('DV',normal='DV',bold='DVB',italic='DV',boldItalic='DVB')
INK=colors.HexColor('#163B38'); ACCENT=colors.HexColor('#CEEB87'); LIGHT=colors.HexColor('#EAF1E8')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyDV',fontName='DV',fontSize=9.4,leading=14,spaceAfter=9,textColor=colors.HexColor('#263B37')))
styles.add(ParagraphStyle(name='SmallDV',parent=styles['BodyDV'],fontSize=8,leading=11,spaceAfter=6))
styles.add(ParagraphStyle(name='H1DV',fontName='DVB',fontSize=24,leading=29,spaceAfter=16,textColor=INK))
styles.add(ParagraphStyle(name='H2DV',fontName='DVB',fontSize=13,leading=18,spaceBefore=10,spaceAfter=8,textColor=INK))
styles.add(ParagraphStyle(name='Kicker',fontName='DVB',fontSize=8.5,leading=12,spaceAfter=12,textColor=INK))
W=499

def P(text,small=False):return Paragraph(text,styles['SmallDV' if small else 'BodyDV'])
def H(t):return Paragraph(t,styles['H2DV'])
def T(headers,rows,widths=None):
    vals=[[P(escape(str(x)),True) for x in headers]]+[[P(escape(str(x)),True) for x in row] for row in rows]
    t=Table(vals,colWidths=widths or [W/len(headers)]*len(headers),repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),LIGHT),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),('LINEBELOW',(0,0),(-1,0),1,INK),('LINEBELOW',(0,1),(-1,-1),.35,colors.HexColor('#DDE5DE'))]))
    return t

def IMG(name,maxh=350,maxw=W):
    path=ROOT/name
    im=PILImage.open(path);w,h=im.size;scale=min(maxw/w,maxh/h)
    return Image(str(path),width=w*scale,height=h*scale,hAlign='CENTER')

def page(kicker,title,items):
    return [Paragraph(kicker.upper(),styles['Kicker']),Paragraph(title,styles['H1DV'])]+items

def footer(c,doc):
    c.setStrokeColor(INK);c.setLineWidth(.7);c.line(48,799,547,799)
    c.setFont('DVB',8);c.setFillColor(INK);c.drawString(48,810,'LÚMINA / ÓPTICA');c.setFont('DV',7.5);c.drawRightString(547,810,'PROYECTO 1 · 22121280')
    c.setFillColor(colors.HexColor('#65766E'));c.drawString(48,30,f'Eduardo O. Rodríguez Gutiérrez · {FECHA_TEXTO}');c.drawRightString(547,30,str(doc.page))

def build(name,pages):
    story=[]
    for i,parts in enumerate(pages):
        if i:story.append(PageBreak())
        story+=parts
    doc=SimpleDocTemplate(str(OUT/name),pagesize=(595.28,841.89),leftMargin=48,rightMargin=48,topMargin=58,bottomMargin=49,title=name.replace('_',' '),author='Eduardo Osvaldo Rodríguez Gutiérrez · elaboración asistida con IA')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)

backend_patterns=page('Análisis de patrones / 1 de 2','Patrones del backend',[
 P('<b>Contexto.</b> El Proyecto 1 integra un recomendador de paquetes de óptica en Django y SQLite. Los patrones se identifican en archivos propios; cada separación responde a una variación o inconveniente real.'),
 H('Strategy o políticas intercambiables'),P('<b>Archivo:</b> backend/optica/reglas.py. El protocolo Regla define evaluar(paquete, entradas); ReglaPresupuesto, ReglaDisponibilidad y ReglaPreferencia implementan esa operación. REGLAS permite componer políticas sin modificar el adaptador del modelo. Evita mezclar restricciones actuales con la inferencia. Se aplica una composición de políticas; no se afirma que cada regla sea un algoritmo de clasificación independiente.'),
 H('Adapter'),P('<b>Archivo:</b> backend/optica/recomendador.py. RecomendadorArbol carga el Pipeline, prepara el DataFrame y traduce classes_ / predict_proba a pares (código, probabilidad). El servicio consume el protocolo Predictor. Evita que vistas y cliente conozcan estructuras internas de scikit-learn.'),
 H('Repository'),P('<b>Archivo:</b> backend/optica/repositories.py. CatalogoRepository y OrdenRepository concentran consultas ORM y persistencia. OpticaService solicita datos por estos objetos. Evita consultas repartidas por vistas o pantallas. El ORM no convierte automáticamente toda la aplicación en Repository: aquí existe un borde explícito.'),
 H('Front Controller'),P('<b>Archivos:</b> backend/config/urls.py, backend/optica/urls.py y views.py. Django recibe la petición y el enrutador la despacha a una vista. La vista adapta HTTP, verifica JSON y delega. Evita una entrada distinta y lógica duplicada para cada cliente. Es infraestructura del framework, no una clase GoF inventada.'),
 H('Service Layer / Facade y transacción'),P('<b>Archivo:</b> backend/optica/services.py. OpticaService coordina validación, ranking, reglas y registro. Registrar vuelve a calcular la decisión en servidor y usa transaction.atomic. El servicio ofrece una puerta al caso de uso; la transacción es el equivalente operativo de una unidad de trabajo con ORM. Evita que Flutter coordine la base o imponga el precio.'),
 P('<b>Idempotencia:</b> una clave UUID única en Orden permite que un reintento con el mismo perfil recupere el folio previo. Es una propiedad del protocolo, no un patrón GoF. La base conserva el resultado y el precio históricos.',True),
])
client_patterns=page('Análisis de patrones / 2 de 2','Diseño del cliente Flutter',[
 H('Separación comparable a MVC'),P('<b>Archivos:</b> flutter_app/lib/screens/, models/models.dart y data/api_client.dart. Las pantallas presentan datos y manejan eventos; los modelos Dart representan el contrato JSON; ApiClient adapta la comunicación. Se separan presentación, datos y acceso HTTP. Es una analogía arquitectónica: Flutter no impone MVC estricto y un modelo Dart no es el modelo de IA.'),
 H('Composición de interfaz'),P('<b>Archivos:</b> widgets/common.dart y screens/result_screen.dart. PageBody, ErrorPanel, EyewearArt y RecommendationView componen pantallas reutilizables. El resultado se muestra tanto antes de confirmar como dentro de la orden. Evita duplicar el ranking y que dos pantallas interpreten distinto la misma respuesta. Composición de widgets no se etiqueta automáticamente como Composite GoF.'),
 H('Estado local y navegación'),P('<b>Archivos:</b> main.dart y screens/*.dart. StatefulWidget mantiene carga, errores y formulario; IndexedStack conserva las pestañas. FutureBuilder resuelve la carga del catálogo. Navigator abre detalle y resultado; pushReplacement lleva a la orden tras confirmar. Los controladores se liberan en dispose y se verifica mounted después de esperas. Evita actualizar una pantalla ya cerrada o perder el formulario por cambiar de pestaña.'),
 H('Una frontera HTTP comprobable'),P('<b>Archivo:</b> data/api_client.dart. Centraliza URL configurable, UTF-8, timeout, encabezados y errores. Admite http.Client inyectado para pruebas con MockClient. Evita direcciones repetidas y mensajes inconsistentes. La app solo interpreta JSON: no contiene joblib, precios autoritativos ni reglas del recomendador.'),
 H('Patrones que no se justifican en esta entrega'),P('<b>Gateway/BFF y microservicios:</b> el requisito sitúa la IA dentro del monolito; no existen equipos o despliegues independientes que exijan ese costo. <b>Observer de dominio:</b> no se envían correos ni eventos posteriores. <b>Factory Method, Abstract Factory, Builder y Prototype:</b> no hay una familia de creación variable que los requiera. La caché lru_cache del modelo es reutilización por proceso, no una implementación propia de Singleton GoF.'),
 H('Por qué esta separación importa'),P('El cambio de precio se atiende en catálogo; el de política, en reglas; el de modelo, en el adaptador; y el de presentación, en Flutter. El caso de $700 demuestra la relación: el árbol propone Claridad, presupuesto la descarta, el servicio elige Esencial y la UI muestra tanto la sugerencia como la corrección. Los nombres de patrones describen responsabilidades que se pueden localizar en el código.'),
 P('Fuente principal: apuntes de Eduardo Alcaraz, apartados de patrones web/móvil y Proyecto 1; https://ealcaraz85.github.io/topicoswebmobil/ (consulta: 11/11/2026). Elaboración asistida con ChatGPT/Codex; debe revisarse y explicarse por el estudiante.',True),
])

metricas=json.loads((ROOT/'ml/metricas.json').read_text())
rec=json.loads((ROOT/'evidencias/02_recomendacion.json').read_text())
orden=json.loads((ROOT/'evidencias/03_orden_registrada.json').read_text())
pages=[]
pages.append(page('Avance de análisis y diseño / entrega individual','Lúmina Óptica',[
 P(f'<b>Eduardo Osvaldo Rodríguez Gutiérrez</b><br/>Número de control: <b>22121280</b><br/>Ingeniería en Sistemas Computacionales · Instituto Tecnológico de Morelia<br/>Materia: Tópicos Selectos de Tecnologías Web y Móvil<br/>Entrega de análisis: <b>{FECHA_TEXTO}</b>'),
 H('Problema, objetivo y alcance'),P('Un usuario necesita comparar paquetes comerciales de una óptica según su rutina y presupuesto. La propuesta es integrar un recomendador entrenado con reglas explícitas, mostrar su decisión en Flutter y registrar una solicitud consultable por folio. La asignación del dominio corresponde a la fila 23 de los proyectos progresivos de los apuntes.'),
 P('Se desarrolla el Proyecto 1: Django, SQLite, catálogo, recomendador .joblib + reglas y cliente Flutter. El asistente entrenado corresponde al Proyecto 2; la integración de equipo y demostración web/móvil, al Proyecto 3. Los paquetes y precios se definen como supuestos propios de una óptica ficticia.'),
 H('Requisitos verificables'),
 T(['ID','Requisito / evidencia'],[
 ('RF01','Listar, buscar y consultar detalle de los paquetes mediante JSON.'),('RF02','Recibir cinco características, ejecutar modelo + reglas y mostrar confianza, corrección y ranking.'),('RF03','Confirmar una solicitud con resultado calculado en servidor y folio único.'),('RF04','Consultar por folio el resultado, perfil y precio registrados.'),('RNF01','URL configurable, estados de carga, errores y validación independiente en servidor.'),('RNF02','Instalación reproducible, datos de prueba, caso corregido y análisis de patrones web/móvil.')],[55,444]),
 H('Usuarios y casos de uso'),P('El comprador explora catálogo, solicita recomendación, confirma y consulta folio. El administrador mantiene paquetes en Django Admin. El comprador no captura información personal en este prototipo. No hay pagos, prescripción ni inventario por unidad.'),
]))
pages.append(page('Especificación del dominio','Entradas, catálogo y reglas',[
 T(['Variable','Tipo / rango','Interpretación'],[('horas_pantalla','Número 0-16','Contexto de uso diario'),('horas_exterior','Número 0-12','Contexto exterior diario'),('presupuesto','Número 300-10000','MXN; máximo 2 decimales'),('uso_principal','Categoría','general / estudio / oficina / exterior'),('prefiere_fotocromatico','Booleano','Preferencia obligatoria si es true')],[142,126,231]),
 H('Clases objetivo y catálogo ficticio'),
 T(['Código / nombre','Precio MXN','Tratamientos'],[('esencial / Esencial','$650','Monofocal base, capa endurecida'),('antirreflejante / Claridad','$1,100','Base, antirreflejante, capa endurecida'),('fotocromatico / Transición','$1,800','Base, fotocromático, capa endurecida'),('premium / Integral','$2,400','Base, antirreflejante, fotocromático, capa endurecida')],[177,80,242]),
 H('Reglas posteriores al modelo'),P('<b>R1 Presupuesto:</b> descarta cualquier paquete cuyo precio actual supere el máximo indicado. <b>R2 Disponibilidad:</b> descarta paquetes no disponibles; clases no activas en catálogo tampoco son elegibles. <b>R3 Preferencia:</b> cuando el usuario exige fotocromático, descarta los paquetes que no lo incluyen.'),
 P('Se conserva el ranking estadístico y se elige la primera alternativa elegible; los empates se resuelven por código. Si no existe una opción válida, la API devuelve 422 y no registra una orden. Las reglas no modifican ni renormalizan las probabilidades.'),
 H('Límite de interpretación'),P('Son reglas comerciales académicas. Las horas de pantalla no determinan una enfermedad; el sistema no calcula graduación ni eficacia de tratamientos. El presupuesto y los precios son supuestos del proyecto, no información clínica ni precios de un establecimiento real.'),
]))
pages.append(page('Diseño de solución','Arquitectura y responsabilidades',[
 IMG('docs/diagramas/01_arquitectura.png',330),
 H('Un monolito con un cliente separado'),P('Flutter consume HTTP/JSON; Django concentra reglas, inferencia y persistencia. Hay un solo backend desplegable y una base SQLite. Separar interfaz y servidor no equivale a microservicios. Esta elección coincide con el alcance explícito del Proyecto 1 y reduce infraestructura para una entrega individual.'),
 T(['Capa','Responsabilidad estable'],[('Flutter','Capturar datos, navegar, mostrar estados y resultados.'),('Vistas y rutas','Traducir HTTP, comprobar formato, responder JSON.'),('Servicio','Orquestar recomendación y confirmación.'),('Adaptador / reglas','Inferencia estadística / políticas comerciales separadas.'),('Repositorios / ORM','Leer catálogo y guardar o recuperar órdenes.')],[130,369]),
 P('La URL base varía entre navegador, emulador y dispositivo; el contrato JSON permanece igual. El artefacto del modelo nunca se envía al cliente.',True),
]))
pages.append(page('Componente de inteligencia artificial','Datos, entrenamiento y evaluación',[
 P('Se adapta la tubería de los apuntes: CSV propio → X/y → partición estratificada → ColumnTransformer + OneHotEncoder → árbol → evaluación → joblib → carga en Django. No se entrena dentro de una petición.'),
 T(['Elemento','Definición'],[('Datos','1,200 perfiles sintéticos; semilla de generación 22121280.'),('Partición','960 entrenamiento / 240 prueba; estratificación por clase; semilla 42.'),('Modelo','DecisionTreeClassifier: profundidad 6, hoja mínima 12.'),('Entradas','4 numéricas/booleanas y 1 categórica; sin folio ni clase objetivo como feature.'),('Artefactos','modelo_optica.joblib, metricas.json y arbol.txt.'),('Resultado','Accuracy 0.9375 = 225/240 etiquetas sintéticas acertadas.')],[128,371]),
 H('Matriz de confusión de prueba'),P('Filas = etiqueta real; columnas = predicción. Orden: antirreflejante (A), esencial (E), fotocromático (F), premium (P).',True),
 T(['Real / pred.','A','E','F','P'],[[c]+row for c,row in zip(['A','E','F','P'],metricas['matriz_confusion'])],[139,90,90,90,90]),
 H('Supuestos y limitaciones del conjunto'),P('Las etiquetas simulan elecciones históricas por rutina, con variación aleatoria. No siempre respetan presupuesto o preferencia; esas condiciones actuales se imponen con reglas. La alta accuracy solo indica reproducción de la política sintética de etiquetado. No se afirma validación con clientes reales ni desempeño clínico.'),
 P('La confianza es la proporción de clases en la hoja del árbol, no una garantía de satisfacción. Se conserva la confianza original y la de la alternativa seleccionada. No se ha calibrado el modelo. Las versiones de dependencias quedan fijadas para regenerar y cargar el mismo Pipeline.'),
]))
pages.append(page('Comportamiento del sistema','De la entrada al folio',[
 IMG('docs/diagramas/02_flujo.png',450),
 P('<b>Vista previa:</b> POST /api/recomendaciones/ valida, infiere y evalúa reglas sin guardar. <b>Confirmación:</b> POST /api/ordenes/ vuelve a calcular y guarda el resultado vigente en una transacción. El cliente envía las entradas y una clave UUID; no envía una decisión o precio autoritativo.'),
 P('<b>Recuperación:</b> GET /api/ordenes/&lt;folio&gt;/ obtiene el snapshot histórico. Un reintento de confirmación con la misma clave y perfil devuelve el mismo folio; la misma clave con otro perfil produce 409. No hay opciones válidas: 422 y cero órdenes nuevas.',True),
]))
pages.append(page('Persistencia y contrato','Modelo de datos e integridad',[
 IMG('docs/diagramas/03_datos.png',275),
 P('La relación es 1:N: cada orden utiliza un paquete; un paquete puede tener muchas órdenes. La FK usa PROTECT. El folio y la clave de idempotencia tienen restricciones de unicidad. La base valida precio positivo y utiliza Decimal para dinero.'),
 H('Por qué conservar un snapshot'),P('Orden guarda entradas, resultado JSON, versión del modelo y precio confirmado. La consulta no vuelve a predecir ni utiliza el precio actual del catálogo para reinterpretar una orden anterior. Esto permite explicar y auditar la decisión que se tomó en ese momento.'),
 H('Contrato API'),T(['Método / ruta bajo /api/','Propósito'],[('GET catalogo/ y catalogo/<codigo>/','Listado, búsqueda q= y detalle.'),('POST recomendaciones/','Ranking, original, final, confianza y reglas.'),('POST ordenes/','Confirmación con Idempotency-Key; 201 o 200.'),('GET ordenes/<folio>/','Recuperación histórica; 404 si no existe.')],[230,269]),
 P('Validación: cuerpo JSON de hasta 8 KB; números finitos, límites y categorías explícitas; rechazo de campos extra. La API demo es pública y no guarda datos personales. Antes de uso real se necesitarían autenticación, autorización, HTTPS y límites de consumo.',True),
]))
pages += [backend_patterns,client_patterns]
pages.append(page('Demostración y aceptación','Caso corregido y pruebas',[
 P('<b>Entrada:</b> pantalla 8 h, exterior 1 h, presupuesto $700, uso oficina, fotocromático obligatorio desactivado.'),
 T(['Paso','Resultado observado'],[('Modelo','antirreflejante / Claridad: 85% de confianza original.'),('Regla','Claridad cuesta $1,100, supera el presupuesto de $700.'),('Final','esencial / Esencial: $650; confianza estadística final 0%.'),('Explicación','corregido=true; el ranking conserva descartes y motivos.'),('Registro','Se guarda una orden con resultado y precio del servidor.'),('Consulta','El folio recupera la misma operación histórica.')],[100,399]),
 P('<b>Interpretación del 0%:</b> el árbol no asignó masa a Esencial en esa hoja, pero era la única alternativa comercial elegible. Se muestra sin inflar la confianza. El proyecto demuestra restricciones correctas; no garantiza que la alternativa seleccionada sea óptima.'),
 H('Criterios de aceptación y comprobación'),T(['Criterio','Verificación'],[('Búsqueda y detalle','Catálogo completo, coincidencia y recurso inexistente.'),('Reglas','Presupuesto, preferencia, disponibilidad y ausencia de opciones.'),('Registro confiable','Rechazo de precio/clase enviados por cliente; folio y snapshot.'),('Reintentos','Misma clave y perfil → mismo folio; cambio de perfil → 409.'),('Entradas y red','Tipos/rangos/JSON inválidos, CORS y mensajes de error.'),('Cliente','Pruebas HTTP simuladas; flujo completo de widgets y validación móvil.')],[154,345]),
 P('En la revisión del 11/11/2026 se aprobaron 10 pruebas Django, 5 Flutter, flutter analyze y build web. Se comprobó además el recorrido en Chrome con Django y el modelo reales: recomendación, reglas, registro, consulta y error 422. Evidencias y límites: evidencias/VALIDACION_LOCAL_2026-11-11.md. Las capturas anteriores de flutter_tester se conservan como material histórico. No se afirma prueba en emulador ni APK.',True),
]))
pages.append(page('Ejecución, trazabilidad y reflexión','Preparar la entrega y explicarla',[
 H('Ruta de instalación resumida'),P('1. Instalar Python 3.12 y Flutter estable, comprobar PATH y flutter doctor. 2. Crear .venv e instalar backend/requirements.txt. 3. Ejecutar migrate y sembrar_demo. 4. Arrancar Django en 127.0.0.1:8000. 5. En flutter_app, ejecutar flutter pub get y flutter run -d chrome --web-port=5173 --dart-define=API_BASE_URL=http://127.0.0.1:8000/api. El README contiene comandos completos para Windows y Android.'),
 H('Relación con el curso'),P('<b>Patrones:</b> se parte del problema de responsabilidades, no de llenar una lista de nombres. <b>Django:</b> apps, ORM, migraciones, SQLite, JSON, admin y transacciones. <b>IA:</b> adaptación del árbol de medios a clases del dominio, ranking y reglas. <b>Flutter:</b> composición, estado local, formularios, navegación y HTTP. <b>Arquitectura:</b> monolito modular con API; gateway y servicios independientes se reservan para una necesidad posterior. La guía de construcción incluye la matriz completa de relación con los apuntes.'),
 H('Riesgos conocidos y siguientes mejoras'),P('Datos sintéticos y confianza sin calibrar; ausencia de autenticación de comprador; idempotencia conservada durante la pantalla, sin cola persistente tras recargar; SQLite sin prueba de carga concurrente; disponibilidad por bandera, sin inventario físico. Para un uso real se requerirían datos comerciales autorizados, evaluación externa, recuperación de operaciones, seguridad y validación de reglas con responsables del negocio.'),
 H('Uso de IA'),P('Se utilizó ChatGPT/Codex para interpretar requisitos, proponer diseño, generar código y datos sintéticos, construir pruebas, diagramas y documentación. Se revisó la implementación existente y se comprobó en Windows el 11/11/2026. La ejecución por el agente no implica una revisión personal del estudiante: debe recorrer la app y explicar sus decisiones antes de presentarla. La justificación exige comprender límites, responsabilidades y evidencias.'),
 H('Fuentes'),P('Eduardo Alcaraz. Apuntes de Tópicos Selectos de Tecnologías Web y Móvil, secciones de Proyecto 1, patrones, Django, Flutter y modelo entrenado. Consulta: 11/11/2026.<br/><link href="https://ealcaraz85.github.io/topicoswebmobil/" color="#163B38">https://ealcaraz85.github.io/topicoswebmobil/</link>',True),
 P('Documentación primaria: docs.djangoproject.com/en/5.2/topics/db/transactions/; docs.flutter.dev/cookbook/networking/send-data; scikit-learn.org/stable/model_persistence.html. README aportado por el estudiante: referencia de organización documental; no se reutilizan sus afirmaciones de validación ni su tecnología.',True),
]))
# Capturas opcionales de ejecución real; la generación final se hace después de verificarlas.
shots=ROOT/'evidencias'
chrome = (shots/'recorrido_chrome.json').exists()
if (shots/'02_formulario.png').exists():
 for title,filename,caption in [
  ('Perfil de entrada','11_chrome_formulario.png' if chrome else '02_formulario.png','Formulario con el perfil de prueba: 8 h, 1 h, $700, oficina y preferencia desactivada.'),
  ('Recomendación explicada','12_chrome_recomendacion.png' if chrome else '03_recomendacion.png','Original: Claridad, 85%. Final: Esencial, $650, 0%. Se conserva la baja confianza sin inflarla.'),
  ('Reglas y alternativas','13_chrome_reglas.png' if chrome else '04_reglas.png','El ranking muestra motivos de descarte por paquete; solo Esencial cumple el presupuesto.'),
  ('Solicitud registrada','14_chrome_folio.png' if chrome else '05_folio.png','Folio real y datos históricos. La captura de consulta incluida en evidencias documenta la recuperación independiente por folio.'),
 ]:
  pages.append(page('Anexo / evidencia de ejecución',title,[
   P('Captura de Chrome sin interfaz gráfica, ejecutando Flutter web compilado contra Django, SQLite y el modelo reales. Recorrido reproducible: scripts/capturar_navegador.py. Un viewport móvil no equivale a una prueba en Android.' if chrome else 'Captura de widgets Flutter reales renderizados por flutter_tester, conectados por HTTP a Django y SQLite. No es una captura de navegador ni de emulador.',True),
   IMG('evidencias/'+filename,510),Spacer(1,12),P(caption),
  ]))
build('Avance_Analisis_22121280.pdf',pages)
build('Analisis_Patrones_22121280.pdf',[backend_patterns,client_patterns])
# Fuente editable completa del avance: conserva tablas y diagramas del PDF.
from html import unescape
import re

def texto_plano(item):
    if isinstance(item, Paragraph):
        return unescape(re.sub('<[^>]+>', '', item.text.replace('<br/>', ' · ')))
    return str(item)

editable = ['# Avance de análisis y diseño · Lúmina Óptica',
            f'Entrega: {FECHA_TEXTO} · Control 22121280',
            'Fuente editable del informe PDF. Generada con scripts/generar_informes.py.']
for parts in pages:
    for item in parts:
        if isinstance(item, Paragraph):
            prefix = '## ' if item.style.name == 'H1DV' else '### ' if item.style.name == 'H2DV' else ''
            editable.append(prefix + texto_plano(item))
        elif isinstance(item, Image):
            relative = Path(item.filename).relative_to(OUT).as_posix() if Path(item.filename).is_relative_to(OUT) else '../' + Path(item.filename).relative_to(ROOT).as_posix()
            editable.append(f'![Diagrama o evidencia]({relative})')
        elif isinstance(item, Table):
            rows = [[texto_plano(cell).replace('|', '\\|') for cell in row] for row in item._cellvalues]
            editable.append('\n'.join(['| ' + ' | '.join(rows[0]) + ' |',
                                      '| ' + ' | '.join(['---'] * len(rows[0])) + ' |'] +
                                     ['| ' + ' | '.join(row) + ' |' for row in rows[1:]]))
(OUT/'AVANCE_ANALISIS.md').write_text('\n\n'.join(editable) + '\n', encoding='utf-8')
print('Informes PDF generados:',len(pages),'páginas previstas del avance; 2 de patrones.')
# Fuente editable resumida de las dos páginas de patrones.
lines=['# Análisis de patrones web y móvil\n','Eduardo Osvaldo Rodríguez Gutiérrez · 22121280\n']
for parts in [backend_patterns,client_patterns]:
 for item in parts:
  if isinstance(item,Paragraph):lines.append(re.sub('<[^>]+>','',item.text)+'\n')
(OUT/'ANALISIS_PATRONES.md').write_text('\n'.join(lines),encoding='utf-8')
