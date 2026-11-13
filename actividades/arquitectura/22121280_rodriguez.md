# Monolito con API frente a microservicios

Nombre: Eduardo Osvaldo Rodríguez Gutiérrez. Matrícula: 22121280.
Equipo: Eduardo Rodríguez, Rodrigo Vega Espinoza, Diego Rivera Cisneros, Diego Soria Magos y Gonzalo García Chávez.
Documento asistido para revisión; se refiere a los archivos reales de esta carpeta.

## 1. Clasificar la plataforma actual

`Navegador / futuro Flutter → HTTP → Django → vistas → recomendador + reglas + estrategias → SQLite/PostgreSQL`.

`Actividad_Extra_Django/retos_django` es un **monolito con API**: `manage.py runserver` inicia el proceso y `entregas/modelo_views.py` importa el recomendador de `laboratorio/recomendadores.py`. `/entregas/recomendar/` no es un servidor independiente por tener otra URL.

## 2. La trampa de los endpoints

Tener hola, estado y recomendar no crea tres microservicios. API separa clientes del servidor; microservicios separan servidores entre sí. Mientras una función importe y llame al modelo dentro del mismo despliegue, siguen siendo módulos del monolito. Una carpeta, una app Django o un puerto del cliente no demuestra un límite de servicio.

## 3. La misma operación en dos mundos

**Monolito:** POST entra en modelo_views.recomendar, valida, llama obtener_recomendador().sugerir en memoria, construye DataFrame, ordena probabilidades, filtra con es_posible y devuelve el plan. A las 3:00 el dron no es viable aunque lidere el ranking.

**Microservicios de esta entrega:** navegador → gateway → pedidos por HTTP → recomendar por HTTP → Adapter + modelo + reglas en memoria. Si Recomendar no responde, Pedidos limita la espera y devuelve un plan B explícito/503. Un GET de un pedido ya guardado sigue dependiendo de Pedidos, no de volver a recomendar. La práctica guarda pedidos en memoria por alcance; en producción requieren base persistente.

## 4. Decisión de la empresa

Si el bosque cambia semanalmente y pedidos casi no cambia, extraería **solo IA**, siempre que el equipo pueda operar dos procesos. (1) Permite reconstruir y reiniciar su imagen sin redeplegar pedidos. (2) Su memoria y cómputo escalan por separado. (3) El costo de HTTP y la observabilidad se concentra en una frontera, en lugar de partir notificaciones y tablas sin necesidad. Para un equipo pequeño o pocas peticiones, mantener el monolito es razonable: un modelo de 50 MB por sí solo no obliga a distribuir.

## 5. Un solo corte

Recomendar se lleva los .joblib, preparación, ranking y reglas necesarias para garantizar una sugerencia viable. Pedidos conserva identidad, persistencia, estado, idempotencia y orquestación del alta. Si el plan usa reglas de negocio de Pedidos, ese servicio debe validar las restricciones críticas sin delegar su autoridad a un tercero; la práctica concentra el cálculo de transporte en Recomendar. No se crea un servicio por archivo: el límite es la responsabilidad de recomendar y su ciclo de despliegue. Se documenta y versiona el JSON para evitar copias de reglas que diverjan.

Fuente: https://ealcaraz85.github.io/topicoswebmobil/#actividad-monolito-api-microservicios
