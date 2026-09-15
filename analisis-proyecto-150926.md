# Análisis comparativo: `implementacion1` vs `implementacion2`

**Proyecto:** Plataforma de entregas (registrar pedido → consultar IA de ruteo → planear medio de entrega)
**Lenguajes evaluados:** Python y Java (ambas implementaciones existen en ambos lenguajes, con paridad estructural total)

---

## 1. Contexto rápido

- **`implementacion1`**: separa el trámite en módulos/clases con **Strategy**, **Adapter** y **Factory Method**. En Python vive en el paquete `entregas/` (`dominio.py`, `ia.py`, `logistica.py`, `medios.py`, `registrar.py`); en Java, en el paquete `entregas` con una clase por responsabilidad.
- **`implementacion2`**: el propio README lo declara explícitamente como "mala práctica a propósito" — el mismo trámite resuelto en **un solo método** (`registrar_pedido` / `registrarPedido`) sin patrones, con lógica duplicada para cada proveedor de IA.

Ambas producen la **misma salida en pantalla**; lo que cambia es cuántos archivos/bloques hay que tocar cuando algo del negocio cambia.

---

## 2. Tabla comparativa

| Aspecto | `implementacion1` (con patrones) | `implementacion2` (sin patrones) |
|---|---|---|
| **Estructura general** | Multi-archivo/multi-clase por responsabilidad (dominio, adaptadores de IA, fábricas de logística, estrategias de medio, orquestador) | Un único método (`registrar_pedido`/`registrarPedido`) que hace todo: parseo del proveedor, selección de medio y cálculo del plan |
| **Acoplamiento con el proveedor de IA** | El dominio solo conoce `Sugerencia` (medio + motivo); nunca ve `route_hint`, `score`, XML ni JSON crudo | `route_hint`/`vehicle` se leen e interpretan *dentro* del mismo método que calcula el plan; el dominio y el formato externo están mezclados |
| **Agregar un nuevo proveedor de IA** | Se crea una clase que implemente `RecomendadorIA` (`sugerir`); nada más cambia | Hay que añadir otro bloque `elif`/`else if` completo, duplicando de nuevo toda la lógica de planeación |
| **Agregar un nuevo medio (p. ej. triciclo)** | Se crea una clase `MedioDeEntrega` + una `Logistica` que la fabrique, y se registra una entrada en `logistica_para`/`Logistica.para` | Hay que editar el `if/elif` de medios **dos veces** (una por cada proveedor), porque las reglas están copiadas y pegadas |
| **Duplicación de lógica de negocio** | Ninguna: cada regla de "cabe/tiempo/costo" vive en una sola clase (`EntregaDron`, `EntregaBicicleta`, etc.) | Las reglas de dron/bici/moto/van están **copiadas literalmente** en el bloque `openai` y en el bloque `xml` |
| **Testabilidad** | Cada pieza se prueba de forma aislada (se puede probar `EntregaDron.planear` sin tocar XML ni JSON; se puede inyectar un `ClienteOpenAI`/`ClienteXml` falso vía el constructor de los adaptadores) | Para probar el dron hay que pasar por todo el método, incluyendo el parseo del "proveedor" simulado; no hay forma de aislar una sola regla |
| **Legibilidad / longitud** | Archivos pequeños (10-40 líneas), cada uno con una sola razón para cambiar (Single Responsibility) | Un método de +100 líneas con anidamiento profundo de `if`, difícil de leer de corrido |
| **Manejo de errores** | La versión Java lanza excepciones explícitas (`IllegalArgumentException`, `IllegalStateException`) ante un medio o hint desconocido | Ante un "hint desconocido" o proveedor nuevo, solo se imprime un mensaje por consola (`print("hint desconocido...")`) y la ejecución continúa con datos a medias (`medio=""`, `cabe=False`) |
| **Inmutabilidad de datos** | `Pedido`, `ContextoViaje`, `Sugerencia`, `Plan` son `dataclass(frozen=True)` en Python / clases con campos `final` en Java | Todo son variables locales sueltas (`cabe`, `minutos`, `costo`, `medio`, `motivo`) reasignadas a lo largo del método |
| **Extensibilidad ante cambios de contrato externo** | Si el proveedor cambia `route_hint` por `vehicle`, solo se toca el `AdaptadorOpenAI`/`AdaptadorXml` correspondiente | Si el proveedor cambia el nombre del campo, hay que editar el único archivo/método que existe, arriesgando romper también el cálculo del plan |
| **Patrones de diseño usados** | **Strategy** (`MedioDeEntrega` y subclases), **Adapter** (`RecomendadorIA`, `AdaptadorOpenAI`, `AdaptadorXml`), **Factory Method** (`Logistica.crearMedio()` y subclases `LogisticaTerrestre/Urbana/Corta/Aerea`) | Ninguno (a propósito) |
| **Buenas prácticas presentes** | SRP por archivo/clase; inyección de dependencias en los adaptadores (constructor acepta un cliente opcional, facilita mocks); tipado (`typing`/tipos Java); dataclasses inmutables; separación dominio/infraestructura; nombres de dominio en español consistentes | Prints informativos para depuración rápida; el código es funcional y fácil de ejecutar de un tirón sin entender clases; comentarios explican honestamente por qué es "mala práctica" (documentación didáctica) |
| **Malas prácticas presentes** | Ninguna relevante para el alcance del ejercicio (posible mejora menor: falta manejo de excepción cuando `AdaptadorOpenAI`/`AdaptadorXml` reciben un hint no mapeado en Python, ya que `_HINTS[...]` lanzaría `KeyError` sin mensaje claro) | Duplicación de código (copy-paste) entre bloques `openai`/`xml`; función con demasiadas responsabilidades (God Method); mezcla de parseo, reglas de negocio y presentación (`print`) en un mismo lugar; "manejo de errores" solo por `print`, dejando el programa continuar en estado inconsistente; variables reutilizadas con distintos significados a lo largo del método; falta de tipado fuerte en los "hints" (comparaciones por string sin constantes) |
| **Mejoras posibles** | Levantar una excepción de dominio clara si `Sugerencia.medio` no está en el mapa de `logistica_para` (Python) para igualar el manejo de errores ya presente en Java; añadir pruebas unitarias explícitas por estrategia/adaptador; mover el mapa `_HINTS`/`MapaHints` a un Value Object o enum en vez de diccionario de strings sueltas | Extraer las reglas de "cabe/tiempo/costo" a funciones por medio (aunque sea sin clases) para eliminar la duplicación; separar el parseo del proveedor del cálculo del plan; sustituir los `print` de error por excepciones; como ejercicio de transición, podría refactorizarse gradualmente hacia Strategy/Adapter/Factory Method, que es justamente lo que demuestra `implementacion1` |

---

## 3. ¿Cuál es mejor?

**`implementacion1` es la mejor implementación.** Resuelve exactamente el mismo problema que `implementacion2`, pero:

1. **Aísla el cambio**: un proveedor de IA nuevo, un medio de entrega nuevo o un cambio de contrato externo se resuelven agregando una clase, no editando un método gigante en dos sitios a la vez.
2. **Elimina la duplicación**: las reglas de negocio (cabe/tiempo/costo por medio) existen en un solo lugar, evitando que un cambio de tarifa se aplique a un bloque y se olvide en el otro (bug clásico de copy-paste).
3. **Es más testeable**: cada estrategia y cada adaptador se puede probar de forma unitaria e inyectar dobles de prueba.
4. **Comunica intención**: los nombres (`RecomendadorIA`, `MedioDeEntrega`, `Logistica`) documentan el diseño mejor que un `if/elif` plano.

`implementacion2` cumple su propósito **pedagógico**: mostrar, de forma honesta y bien comentada, el costo real de no aplicar Strategy, Adapter y Factory Method. Como entregable de producción, sin embargo, es la opción a evitar — es exactamente el "código que copia, pega y reza" que el propio README de esa carpeta advierte.
