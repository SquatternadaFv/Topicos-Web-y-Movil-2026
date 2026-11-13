# Veinte lenguajes y frameworks: paradigma, estructura y límites

Complementa `../LenguajesYPatrones.md`. Un lenguaje no tiene un patrón obligatorio: se distinguen paradigma, mecanismo del framework y patrones que pueden implementarse. Los decoradores de sintaxis no equivalen automáticamente al patrón GoF Decorator.

| # | Lenguaje/framework | Paradigma o enfoque | Patrones/mecanismos frecuentes | Problema al llevarlo al extremo |
|---|---|---|---|---|
| 1 | Java | OO y programación genérica | Strategy, Factory, DI | Jerarquías profundas e interfaces sin variación ocultan el caso de uso |
| 2 | C++ | Multiparadigma y control de recursos | RAII, Strategy, Pimpl | Propiedad ambigua y punteros sin control causan fugas/doble liberación; RAII no es GoF |
| 3 | C# | OO, genéricos, eventos | Observer/eventos, DI | Suscripciones que no se liberan conservan objetos y crean efectos inesperados |
| 4 | Python | Imperativo, OO y funcional | Protocolos, Adapter, Iterator | Tipos y contratos implícitos pueden fallar tarde; se necesitan validación y pruebas |
| 5 | JavaScript | Prototipos y eventos asíncronos | Módulos, Observer, Strategy con funciones | Trabajo CPU bloqueante impide atender otros eventos; asincronía no lo paraleliza sola |
| 6 | TypeScript | Tipado estático sobre JavaScript | Adapter, puertos, funciones genéricas | Los tipos no validan JSON externo en ejecución; abusar de any elimina garantías |
| 7 | Ruby/Rails | OO dinámico, convención | Active Record, MVC | Callback y modelo gigante mezclan persistencia, reglas y efectos |
| 8 | PHP/Laravel | OO y aplicación web por peticiones | Container/DI, middleware, Active Record | Dependencias obtenidas globalmente pueden quedar ocultas; Facade del framework no implica diseño desacoplado |
| 9 | Go | Imperativo y concurrencia con goroutines | Worker Pool, composición | Goroutines bloqueadas y canales sin cancelación filtran recursos |
| 10 | Rust | Propiedad, enums, traits | RAII, Builder, Typestate | Forzar grafos con referencias cruzadas complica préstamos; abusar de unsafe elimina protección |
| 11 | Haskell | Funcional puro, evaluación perezosa | Functor, composición, mónadas | Acumular expresiones diferidas puede consumir memoria; mónada es abstracción funcional, no ficha GoF |
| 12 | Scala | OO y funcional | Composición de traits, typeclasses | Mezclas y abstracciones profundas dificultan inferir dependencias y errores de tipos |
| 13 | C | Procedural | Puntero opaco, tabla de funciones | Gestión manual de memoria y límites insuficientes exponen errores de vida útil y buffers |
| 14 | Prolog | Lógico/declarativo | Unificación, búsqueda | El orden de reglas y búsqueda puede provocar no terminación o explosión combinatoria |
| 15 | React | UI declarativa por componentes | Composición, estado y flujo de datos | Estado global excesivo o efectos mal sincronizados producen renders y datos obsoletos |
| 16 | Angular | Componentes, DI y reactividad | DI, Observer | Suscripciones y servicios con responsabilidades excesivas dificultan vida útil y pruebas |
| 17 | Vue | UI declarativa y estado reactivo | Composición, MVVM como aproximación | Mutaciones dispersas y estado compartido implícito hacen difícil explicar cambios |
| 18 | Django | MTV, ORM y middleware | Front Controller, Template View, Unit of Work | Consultas N+1 y reglas en plantillas/vistas gigantes degradan separación aunque haya carpetas |
| 19 | Spring Boot | OO, contenedor IoC y proxies | DI, transacciones declarativas | Suponer que toda llamada pasa por el proxy rompe expectativas de @Transactional, por ejemplo auto-invocación |
| 20 | Flutter/Dart | UI declarativa, composición y async | Estado observable, Repository, Adapter HTTP | Guardar todo en widgets efímeros pierde estado; copiar BLoC sin necesidad añade ceremonia |

**Decisión aplicada:** en los cinco días usamos lo que Django ya proporciona y añadimos estrategias donde sí varía el medio. En Flutter los widgets muestran estado; no cargan joblib ni contienen restricciones del transporte. Tipado, paradigma y framework ayudan, pero no sustituyen límites de responsabilidad ni datos de entrada validados.
