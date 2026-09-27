# Día 3 — Strategy, Adapter y quién hace el `new`

Objetivo: el inconveniente 2 del enunciado, con las definiciones de
*Los problemas de esta plataforma*.

## Qué se agregó

1. **`entregas/medios.py`** — contrato `MedioDeEntrega.planear(peso_kg, ctx) → Plan` y una clase por medio: camioneta, motocicleta, bicicleta, dron. **Strategy**. Un `if` de dos casos estables no sustituye a cuatro medios que van a crecer.
2. **`entregas/ia.py`** — un `AdaptadorIAFalsa` que simula un proveedor devolviendo `route_hint`/`reason_code` (JSON crudo) y lo traduce a `Sugerencia(medio, motivo)`. **Adapter**. Si `route_hint` apareciera en la vista o en `planear()`, el idioma ajeno se habría colado.
3. **`entregas/fabrica.py`** — con el string que ya vino en la Sugerencia, una **fábrica simple** `crear_medio("dron")` es lo esperado.
4. **`entregas/services.py`** — `registrar_pedido` ahora orquesta: Adapter → crear medio → Strategy. La vista (`views.py`) no cambió ni una línea: sigue sin conocer `EntregaDron`.

## Una frase por patrón

- **Strategy** — resuelve *cómo se planea* cada medio sin que `registrar_pedido` conozca sus nombres concretos. Vecino que no es: **State** (el pedido no cambia de fase; se elige un algoritmo distinto).
- **Adapter** — resuelve que el proveedor hable un idioma ajeno mientras el dominio solo entiende `Sugerencia`. Vecino que no es: **Facade** (Facade simplifica algo *nuestro*; aquí traducimos algo ajeno).
- **Fábrica simple** — resuelve *quién hace el `new`*. No usamos Factory Method porque no hay familias de trámite (terrestre/aérea) que redefinan un gancho — solo cambia el medio, así que `crear_medio(tipo)` basta y es más claro.

## Por qué no Factory Method

Factory Method tiene sentido cuando una clase con oficio (p. ej. `Logistica.despachar`) tiene subclases que redefinen `crearMedio()` — logística terrestre frente a aérea. Aquí no hay esa familia: un único trámite recibe un string y pide el objeto. Montar `Logistica`/`LogisticaAerea` sería ceremonia para un solo algoritmo de creación.
