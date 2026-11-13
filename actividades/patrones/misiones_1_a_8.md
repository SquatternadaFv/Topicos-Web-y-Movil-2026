# Misiones 1–8 — Empresa de entregas

Complemento del caso universitario anterior. Las respuestas se aplican al enunciado vigente de mensajería. Se prepararon con asistencia y deben poder defenderse usando el código del repositorio.

## Misión 1 — La plataforma no es un patrón

| Problema | Capa | Patrón o mecanismo | Por qué | Vecino descartado | Cuándo no |
|---|---|---|---|---|---|
| Sesión copiada | Entrada HTTP | Front Controller + middleware | Centraliza acceso antes del trámite | Page Controller aislado conserva copias | Una función local sin entrada HTTP |
| Cuatro medios en un switch | Aplicación | Strategy + fábrica simple | Cada medio varía sin cambiar registro | State trata fases del mismo objeto | Un solo algoritmo estable |
| Protocolos incompatibles de IA | Integración | Adapter | El dominio conserva Sugerencia | Facade no traduce necesariamente un contrato ajeno | Ambos lados comparten contrato propio |
| SQL en plantilla | Datos/presentación | Repository + Template View | Una consulta compartida entrega datos resueltos | Una etiqueta MVC no corrige SQL en HTML | Envoltura CRUD redundante del ORM |
| Pedido y cobro separados | Persistencia | Unit of Work | Confirma o revierte escrituras relacionadas | Observer no aporta atomicidad | Una única escritura independiente |
| IA caída bloquea lectura | Integración | Timeout y Circuit Breaker | Limita esperas y permite consultar datos propios | Retry ciego agrava la caída | Operación local sin red |

**Stack justificado.** Django/Python permite reutilizar ORM, middleware y plantillas y cargar los modelos entrenados con scikit-learn. REST/JSON conserva el contrato del móvil. SQLite basta para la práctica de una copia; PostgreSQL comparte estado con varias. Sesión y CSRF sirven al panel; una futura app usaría credenciales/tokens gestionados por el servidor, no una bandera de cliente. IA entra por Adapter, mapas son presentación externa con timeout; no hace falta tiempo real para consultar un folio. Separamos vistas, servicios, repositorio y estrategias. Pruebas verifican persistencia, fallos y contrato; Compose empaqueta servicios distintos solo donde existe esa separación.

## Misión 2 — Una petición, varios patrones

`POST /pedidos → Django WSGI/ASGI + urls → middleware de acceso/bitácora → vista delgada → registrar_pedido → Adapter IA → fábrica → Strategy.planear → Repository + transaction.atomic → COMMIT → aviso → redirección GET o JSON`.

La entrada recibe HTTP; las políticas no eligen vehículo. El servicio nombra el caso de uso. Adapter traduce el idioma externo. La fábrica crea la implementación que corresponde al medio sugerido. La estrategia planea. La transacción garantiza el par pedido/cobro simulado. Los avisos se registran con on_commit. PRG evita repetir el POST al recargar; una clave única de idempotencia resuelve solicitudes duplicadas del mismo intento.

Código: `dia5/dia5/entregas/{views,services,ia,fabrica,medios,repository}.py`. No reimplementamos el controlador frontal de Django.

## Misión 3 — Políticas transversales

Front Controller corresponde cuando varias rutas comparten despacho, errores y políticas. No significa meter todos los trámites en una clase gigante. Spring ya tiene DispatcherServlet/filtros; Laravel kernel y middleware; Express router/app y app.use. El orden es autenticar, autorizar lo necesario para acceder, registrar intento según política y ejecutar caso de uso. La bitácora de intentos fallidos puede envolver autenticación; nunca se cobra antes de comprobar identidad. Ni middleware ni filtros deciden el medio: eso cambia por reglas del negocio y pertenece al servicio.

## Misión 4 — Entrega e IA

Strategy representa los algoritmos de dron, moto, bicicleta y camioneta. Adapter transforma JSON/XML en Sugerencia. La fábrica concentra la creación, fuera de la vista.

Java permite un contrato `interface Medio { Plan planear(Pedido p, Contexto c); }` y una implementación por alternativa. En JavaScript puede ser una función:

```javascript
const estrategias = { bici: p => ({medio:'bici', minutos:p.km/15*60}),
                      moto: p => ({medio:'moto', minutos:p.km/35*60}) };
const crearMedio = nombre => {
  if (!estrategias[nombre]) throw new Error('medio desconocido');
  return estrategias[nombre];
};
const plan = crearMedio('bici')({km:3});
```

Traducir route_hint:"bike" al vocabulario interno es Adapter; la correspondencia exacta debe fijarla el contrato del proveedor, no adivinarse por la palabra. `MedioFactory.crear("dron")` con switch es fábrica simple. Factory Method se justifica si variantes de un trámite heredan el esqueleto y redefinen el gancho que crea el medio; no basta llamar factory a un switch. En esta práctica la fábrica simple alcanza. La segunda vía XML está en los archivos ia.py y usa el mismo contrato interno.

## Misión 5 — Atomicidad frente a aviso

Unit of Work cubre pedido + cobro simulado dentro de la misma base. Observer cubre correo, repartidor y estadísticas después del commit. Si el banco fuera externo, una transacción del ORM no lo incluye: se necesitan clave de idempotencia en el proveedor, estados y conciliación/compensación. El doble clic se deduplica en `POST /pagos` con clave de intento persistida y restricción única; dos transacciones independientes no se deduplican solas. Se conserva el resultado de la primera solicitud para responder a la repetida. Error 400 de validación se corrige, no se reintenta sin cambiar datos.

## Misión 6 — Clientes y fallo externo

Un GET agregado puede dar JSON mínimo a la app y HTML con mapa al panel. BFF solo si las necesidades difieren lo suficiente para justificarlo; Gateway proporciona una entrada cuando hay varios servicios. Pueden coexistir, pero no son obligatorios por tener dos clientes. `/pedidos/{folio}` identifica el recurso. `/asignar` expresa un verbo y oculta qué pedido/asignación cambia; es preferible crear o actualizar un recurso de asignación, con semántica y permisos explícitos.

La consulta de un pedido guardado no llama al modelo ni al mapa. Una creación que requiere IA usa timeout; Circuit Breaker deja de insistir durante una caída; Retry se limita a fallos transitorios y operaciones seguras o idempotentes. No se reintenta un cobro ambiguo sin la misma clave ni errores 400. Para un PDF se rechazan Event Sourcing y Redux global: autenticar, leer y renderizar una vista bastan.

## Misión 7 — El marco ya lo trae

| Intención | Spring | Express | No reescribir |
|---|---|---|---|
| Punto único de entrada | DispatcherServlet | app/router del framework | Un segundo despachador del libro |
| Cadena de políticas | Servlet Filter, Spring Security | app.use y middleware ordenado | Autenticación copiada en cada handler |
| Unidad de trabajo | @Transactional con gestor y conexión | Transacción del driver/ORM, p. ej. sequelize.transaction | Un commit simulado en JavaScript; Express no trae ORM por sí mismo |
| Observer de la SPA | En el navegador: estado/eventos del framework cliente | Lo mismo: no depende de que el servidor sea Express | Un segundo bus global solo por uniformidad |

El marco servidor no implementa por sí solo la reactividad del navegador. Tampoco una anotación cubre automáticamente una llamada bancaria externa.

## Misión 8 — El mismo pedido en Flutter

Elijo Flutter. `{estado, eta, posicion}` vive en un controlador de estado/ViewModel o BLoC fuera del widget que dibuja; el repositorio ofrece datos locales/remotos. El controlador no contiene sockets, SQL ni formato del proveedor: depende de interfaces. Rotar o reconstruir un widget no debe reiniciar el estado del pedido. Un repositorio con caché local permite consultar un pedido visto sin red; Circuit Breaker limita intentos hacia la API, pero no reemplaza datos persistidos. Se muestra fecha de actualización y estado offline.

Un pago pendiente es un Command con identidad de intento. Se conserva en almacenamiento local y el servidor usa la misma clave de idempotencia. Un worker/scheduler del sistema reenvía cuando haya condiciones, no un hilo ligado a una Activity que puede destruirse. En Android nativo, WorkManager es la opción del sistema para trabajo diferible; en Flutter se integra una solución de background compatible con las restricciones de cada plataforma. No se promete cobro completado hasta confirmación del backend. No se copia BLoC a Android ni ViewModel Android a Flutter para uniformar nombres: se conservan responsabilidades usando mecanismos del marco. Doce fetch para iniciar la app apuntan a agregación/BFF, no a Factory.

Fuente: https://ealcaraz85.github.io/topicoswebmobil/#misiones-web
