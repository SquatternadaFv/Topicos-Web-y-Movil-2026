# Análisis de patrones web y móvil

Eduardo Osvaldo Rodríguez Gutiérrez · 22121280

ANÁLISIS DE PATRONES / 1 DE 2

Patrones del backend

Contexto. El Proyecto 1 integra un recomendador de paquetes de óptica en Django y SQLite. Los patrones se identifican en archivos propios; cada separación responde a una variación o inconveniente real.

Strategy o políticas intercambiables

Archivo: backend/optica/reglas.py. El protocolo Regla define evaluar(paquete, entradas); ReglaPresupuesto, ReglaDisponibilidad y ReglaPreferencia implementan esa operación. REGLAS permite componer políticas sin modificar el adaptador del modelo. Evita mezclar restricciones actuales con la inferencia. Se aplica una composición de políticas; no se afirma que cada regla sea un algoritmo de clasificación independiente.

Adapter

Archivo: backend/optica/recomendador.py. RecomendadorArbol carga el Pipeline, prepara el DataFrame y traduce classes_ / predict_proba a pares (código, probabilidad). El servicio consume el protocolo Predictor. Evita que vistas y cliente conozcan estructuras internas de scikit-learn.

Repository

Archivo: backend/optica/repositories.py. CatalogoRepository y OrdenRepository concentran consultas ORM y persistencia. OpticaService solicita datos por estos objetos. Evita consultas repartidas por vistas o pantallas. El ORM no convierte automáticamente toda la aplicación en Repository: aquí existe un borde explícito.

Front Controller

Archivos: backend/config/urls.py, backend/optica/urls.py y views.py. Django recibe la petición y el enrutador la despacha a una vista. La vista adapta HTTP, verifica JSON y delega. Evita una entrada distinta y lógica duplicada para cada cliente. Es infraestructura del framework, no una clase GoF inventada.

Service Layer / Facade y transacción

Archivo: backend/optica/services.py. OpticaService coordina validación, ranking, reglas y registro. Registrar vuelve a calcular la decisión en servidor y usa transaction.atomic. El servicio ofrece una puerta al caso de uso; la transacción es el equivalente operativo de una unidad de trabajo con ORM. Evita que Flutter coordine la base o imponga el precio.

Idempotencia: una clave UUID única en Orden permite que un reintento con el mismo perfil recupere el folio previo. Es una propiedad del protocolo, no un patrón GoF. La base conserva el resultado y el precio históricos.

ANÁLISIS DE PATRONES / 2 DE 2

Diseño del cliente Flutter

Separación comparable a MVC

Archivos: flutter_app/lib/screens/, models/models.dart y data/api_client.dart. Las pantallas presentan datos y manejan eventos; los modelos Dart representan el contrato JSON; ApiClient adapta la comunicación. Se separan presentación, datos y acceso HTTP. Es una analogía arquitectónica: Flutter no impone MVC estricto y un modelo Dart no es el modelo de IA.

Composición de interfaz

Archivos: widgets/common.dart y screens/result_screen.dart. PageBody, ErrorPanel, EyewearArt y RecommendationView componen pantallas reutilizables. El resultado se muestra tanto antes de confirmar como dentro de la orden. Evita duplicar el ranking y que dos pantallas interpreten distinto la misma respuesta. Composición de widgets no se etiqueta automáticamente como Composite GoF.

Estado local y navegación

Archivos: main.dart y screens/*.dart. StatefulWidget mantiene carga, errores y formulario; IndexedStack conserva las pestañas. FutureBuilder resuelve la carga del catálogo. Navigator abre detalle y resultado; pushReplacement lleva a la orden tras confirmar. Los controladores se liberan en dispose y se verifica mounted después de esperas. Evita actualizar una pantalla ya cerrada o perder el formulario por cambiar de pestaña.

Una frontera HTTP comprobable

Archivo: data/api_client.dart. Centraliza URL configurable, UTF-8, timeout, encabezados y errores. Admite http.Client inyectado para pruebas con MockClient. Evita direcciones repetidas y mensajes inconsistentes. La app solo interpreta JSON: no contiene joblib, precios autoritativos ni reglas del recomendador.

Patrones que no se justifican en esta entrega

Gateway/BFF y microservicios: el requisito sitúa la IA dentro del monolito; no existen equipos o despliegues independientes que exijan ese costo. Observer de dominio: no se envían correos ni eventos posteriores. Factory Method, Abstract Factory, Builder y Prototype: no hay una familia de creación variable que los requiera. La caché lru_cache del modelo es reutilización por proceso, no una implementación propia de Singleton GoF.

Por qué esta separación importa

El cambio de precio se atiende en catálogo; el de política, en reglas; el de modelo, en el adaptador; y el de presentación, en Flutter. El caso de $700 demuestra la relación: el árbol propone Claridad, presupuesto la descarta, el servicio elige Esencial y la UI muestra tanto la sugerencia como la corrección. Los nombres de patrones describen responsabilidades que se pueden localizar en el código.

Fuente principal: apuntes de Eduardo Alcaraz, apartados de patrones web/móvil y Proyecto 1; https://ealcaraz85.github.io/topicoswebmobil/ (consulta: 11/11/2026). Elaboración asistida con ChatGPT/Codex; debe revisarse y explicarse por el estudiante.
