# Razonamiento, acertijos y autoevaluación

Respuestas de trabajo asistidas; se razona sobre el caso, no se atribuye una experiencia de clase inexistente.

## Tres acertijos

1. Un foco cambia una vez por cada divisor. Los divisores se emparejan salvo la raíz de un cuadrado, por lo que solo quedan encendidos los cuadrados perfectos. Para un millón: 1000 focos. Segundo mayor: 999² = **998001**. Para n general, floor(sqrt(n)). No se necesita matriz n×n.
2. El cajón es **87**. Al girar la representación 180° se observa la sucesión 86, 87, 88, 89, 90, 91. La transformación revela la estructura que una fórmula sobre los números originales oculta.
3. Los trenes cierran 240 km a 120 km/h: chocan a las 2 h. La mosca vuela 90×2 = **180 km**, sin sumar infinitos tramos. Se supone velocidad constante y giro instantáneo, como en el acertijo.

## Ejercicios de plataforma

**Switch de 200 líneas.** El problema es que varían algoritmos de envío mientras el registro debería permanecer estable. Extraer un contrato planear y una implementación por medio evita editar el trámite al añadir otro. La fábrica selecciona, Strategy ejecuta. Se descarta Adapter para calcular costo: solo traduce el idioma ajeno. Implementación: `dia3/entregas/medios.py` y `fabrica.py`; pruebas de extensión con triciclo en `tests/test_laboratorio.py` cuando aplica al contrato del ejemplo.

**«Hay if, luego Strategy».** No: un if estable de validación no implica una familia de algoritmos. Hace falta una responsabilidad que cambie de forma independiente. Con un algoritmo, interfaz + Abstract Factory + una única clase añade mantenimiento sin un cambio real que aislar.

**Facade/Adapter.** route_hint externo pide Adapter. registrar_pedido es Service Layer y puede funcionar como fachada del trámite propio. Un PedidoFacade que solo delega al servicio no agrega una responsabilidad útil.

**Observer registra envío tras pago.** No basta: puede confirmarse el pago y fallar la creación. Para escrituras de una base: `BEGIN → cobro simulado + pedido → COMMIT → PedidoActualizado → correo/app`. Para proveedor externo, estados, idempotencia y compensación/conciliación. Avisar no reemplaza garantizar consistencia.

**Dos index y Front Controller.** Cada script que recibe su propia petición es otra puerta. No basta un Page Controller por archivo: la cadena compartida debe ejecutarse por una entrada controlada, usando el marco, sin copiarla.

**Switch en middleware.** Se rechaza. Middleware trata políticas transversales; decidir el vehículo requiere el caso de uso. Dejarlo allí ata todas las rutas a una regla que no les corresponde.

**Repository basta para kardex con correo.** No: separa consulta, pero falta un servicio que aplique reglas académicas y coordine avisos. La plantilla recibe filas/resumen; no ejecuta SQL ni mail dentro del while. Evitar N+1 requiere planificar la consulta, no solo mover la conexión a otro archivo.

**Reintentar 400 de cobro.** Se rechaza: datos inválidos no se arreglan repitiendo la solicitud. Corregir entrada; para fallos transitorios aplicar política limitada e idempotencia que evite duplicar cargos.

**BFF/Gateway en CRUD de un cliente.** Si un GET ya reúne lo necesario y solo hay un backend, ninguno añade valor por sí mismo. Un endpoint agregado basta. Se justifican cuando existen diferencias de clientes o varios servidores, no para decorar el diagrama.

**IA/mapa caídos.** Timeout limita la espera; Circuit Breaker evita castigar un colaborador caído; Retry solo para causas transitorias. Consultar un pedido persistido no necesita esos colaboradores. No Event Sourcing para producir un PDF a partir de una lectura autorizada.

## Doce preguntas de autoevaluación

1. **Patrón y no patrón:** solución reutilizable a un problema recurrente con contexto y consecuencias; no una receta de código que se añade siempre.
2. **Factory/Strategy:** la primera decide/concentra creación; la segunda expresa un algoritmo intercambiable. Pueden colaborar.
3. **Adapter con IA:** traduce contrato externo; Facade ofrece una entrada simple a operaciones propias.
4. **Observer decide estado:** no debe ser la autoridad de una transición que debe confirmarse antes de avisar. Reacciona al hecho registrado.
5. **Todo switch obliga a Strategy:** no; evaluar variación, tamaño y estabilidad.
6. **Un patrón por app:** no; sesión, algoritmos, datos y presentación tienen conflictos diferentes.
7. **Quince medios en HTTP:** separar transporte HTTP de planeación y creación; no elegir arquitectura solo contando if.
8. **BFF cuándo:** agregaciones/representaciones específicas de clientes que el recurso común no resuelve bien; evitarlo si solo duplica datos.
9. **BLoC en Android nativo:** no copiarlo como ceremonia; aplicar estado y separación con mecanismos adecuados del marco.
10. **Front/Page Controller:** uno centraliza entrada/despacho; el otro maneja un recurso/página concreta. Pueden existir juntos.
11. **POST seguido de GET:** PRG permite recargar la representación sin reenviar el formulario; no garantiza idempotencia ante dos POST simultáneos.
12. **Pin perdido al rotar:** estado ligado al widget/vista efímera; conservarlo en controlador/repositorio y restaurarlo, sin recalcular arbitrariamente el pedido.

## Caso integrador POST /pedidos: defensa

Quitar Factory y concentrar new en un único punto estable puede ser suficiente; se evalúa cuánto cambia esa creación. No hace falta una jerarquía solo por el nombre. Ejecutar Observer dentro de la transacción puede mantenerla abierta por red y causar rollback por un correo fallido; confirmar antes y usar outbox si debe garantizarse el aviso. Elegir medio en middleware mezcla acceso y negocio. Se rechazan Event Sourcing, Abstract Factory preventiva y un segundo Front Controller porque los conflictos actuales se resuelven sin esas capas.

## Contraargumentación y sobreingeniería

Acepto Strategy cuando existen algoritmos que varían; la evidencia es el código y sus cambios. Rechazo que Observer deba crear el envío cuando su ausencia rompería consistencia. Rechazo «todo if es Strategy», «MVC describe toda la plataforma» y «Abstract Factory por si acaso»: cada afirmación omite contexto. Para un solo cálculo usaría una función con pruebas; extraería un contrato cuando aparezca una segunda política con variación independiente.
