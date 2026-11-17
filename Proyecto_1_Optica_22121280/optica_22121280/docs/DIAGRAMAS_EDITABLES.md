# Diagramas editables

Los PNG y SVG de `diagramas/` se generan desde los archivos `.dot` con Graphviz. Los siguientes Mermaid documentan las mismas relaciones para GitHub o un editor compatible.

## Arquitectura

```mermaid
flowchart TD
    F["Flutter: pantallas y ApiClient"] -->|HTTP JSON| U["Rutas y vistas Django"]
    U --> S["OpticaService"]
    S --> A["Adapter sklearn y .joblib"]
    S --> R["Reglas comerciales"]
    S --> P["Repositorios y ORM"]
    P --> D[(SQLite)]
```

## Confirmación y recuperación

```mermaid
sequenceDiagram
    participant F as Flutter
    participant V as API Django
    participant S as OpticaService
    participant D as SQLite
    F->>V: POST recomendaciones con perfil
    V->>S: validar, inferir y evaluar reglas
    S-->>F: JSON original, final, confianza y ranking
    F->>V: POST ordenes con perfil y clave UUID
    V->>S: confirmar
    S->>D: buscar clave de idempotencia
    alt clave existente y mismo perfil
        D-->>F: misma orden y folio
    else nueva operación
        S->>S: recalcular con catálogo vigente
        S->>D: transacción: guardar snapshot y precio
        D-->>F: orden creada y folio UUID
    end
    F->>V: GET ordenes por folio
    V->>D: recuperar snapshot
    D-->>F: resultado histórico
```

## Modelo de datos

```mermaid
erDiagram
    PAQUETE ||--o{ ORDEN : "se registra en"
    PAQUETE {
        bigint id PK
        string codigo UK
        decimal precio
        json tratamientos
        boolean fotocromatico
        boolean disponible
        boolean activo
    }
    ORDEN {
        bigint id PK
        uuid folio UK
        uuid clave_idempotencia UK
        bigint paquete_id FK
        json entradas
        json resultado
        decimal precio_confirmado
        datetime creada
        string estado
    }
```

Los diagramas describen el prototipo actual. El modelo entrenado se guarda como artefacto .joblib; las probabilidades de cada orden forman parte de su snapshot JSON. No son tablas separadas.
