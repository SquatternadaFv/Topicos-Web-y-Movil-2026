# Preguntas de discusión: patrones, arquitectura y Flutter

## Doce preguntas de patrones y microservicios

1. Un patrón busca separar una responsabilidad que cambia bajo fuerzas conocidas, haciendo explícitas consecuencias y costo.
2. Copiar código sin el problema puede añadir capas, confundir responsabilidades y dificultar cambiar lo que sí varía.
3. Strategy cambia algoritmo; Factory Method permite que un subtipo de creador redefina qué producto fabrica durante un trámite.
4. Adapter sirve al integrar JSON/XML o clases externas con un contrato que el dominio no debe conocer.
5. Observer permite redibujar widgets o notificar interesados al cambiar estado; no debe duplicar la autoridad del estado.
6. Repository reúne acceso a datos de un propósito, sin mezclarlo con HTML o HTTP.
7. Monolito es una unidad de despliegue; microservicios son procesos con responsabilidades y despliegues separados, comunicados por red/mensajería.
8. Microservicios es una decisión arquitectónica de distribución, no uno de los 23 patrones GoF.
9. Pocos usuarios/equipo pequeño pueden beneficiarse de un monolito modular y evitar redes, transacciones distribuidas y observabilidad extra.
10. Cada microservicio puede contener Strategy, Adapter y otros patrones internamente.
11. En una plataforma de video podrían existir reproducción, catálogo, perfiles y facturación. Es una hipótesis de límites de negocio, no una afirmación de la arquitectura privada de Netflix u otra empresa.
12. En pedidos de comida: Strategy para tarifa, Observer para progreso, Factory para crear un método de reparto y Adapter para la pasarela externa, si esos problemas realmente existen.

## Dieciocho preguntas Django, Flutter y distribución

1. Separar Flutter y Django es separar cliente y servidor; puede seguir existiendo un único backend monolítico.
2. En este repositorio Django importa el modelo en memoria; en microservicios Pedidos lo solicita a Recomendar por HTTP.
3. Tres endpoints del mismo Django no son tres microservicios: comparten proceso/despliegue.
4. Django conserva validación, autorización, reglas, persistencia y coordinación de los casos de uso.
5. Flutter no abre PostgreSQL: expondría credenciales y eludiría reglas/permisos del servidor.
6. Monolito modular separa responsabilidades lógicas dentro de una unidad de despliegue.
7. Monolito no implica desorden; la dependencia y el cambio importan más que contar contenedores.
8. Django permite comenzar con ORM, migraciones, middleware y plantillas antes de asumir el costo de distribuir.
9. Distribuir introduce latencia, cortes, duplicados, fallos parciales y coordinación de consistencia entre bases.
10. Una app Django es un módulo del mismo sistema; un servicio tiene ejecución y frontera propias.
11. Si IA cae: Pedidos puede usar respaldo explícito o error controlado; consultar datos guardados no debe volver a recomendar. En monolito se aíslan excepciones de la dependencia con el mismo criterio.
12. Extraer IA tiene sentido si cambia/escala por separado. Se lleva modelo y preparación; Pedidos conserva folios y persistencia. Las reglas deben tener dueño explícito para no divergir.
13. Un servicio por tabla distribuye detalles técnicos y obliga a hacer llamadas para una sola operación de negocio.
14. Django puede implementar un microservicio; el framework no determina la distribución.
15. Los límites del negocio evitan particiones con transacciones que necesiten cruzar la red para cada paso.
16. API separa **clientes** del servidor; microservicios separan **servidores** entre sí.
17. Tres réplicas repiten el mismo despliegue; Gateway, Pedidos y Recomendar tienen trabajos e imágenes diferentes.
18. Al detener Recomendar, Pedidos y Gateway siguen vivos. Se muestra fallo parcial; si solo se apaga todo Compose, no se demuestra ese aislamiento.

## Siete preguntas cortas de Flutter

1. Flutter reduce la duplicación de interfaz entre web y móvil mediante un código común; las diferencias de plataforma y red siguen existiendo.
2. Dibuja widgets con su motor para controlar aspecto y comportamiento entre plataformas; se usan integraciones nativas cuando corresponde.
3. StatelessWidget configura una representación; StatefulWidget tiene State que puede cambiar y solicitar reconstrucción con setState.
4. Con Chrome operativo puede empezarse aunque falle Android toolchain; no podrá ejecutarse/compilarse Android hasta resolverlo.
5. Un Column/List/Row puede exceder restricciones de espacio. Expanded reparte el espacio de un Flex; para contenido largo se necesita scroll. No todas las situaciones de desborde se arreglan envolviendo cualquier cosa en Expanded.
6. ListView/ListTile muestran muchos folios con scroll; SnackBar informa un resultado sin navegar.
7. El indicador muestra espera y evita repetición mientras carga. Sustituir Future.delayed por HTTP añade timeout, error y respuesta real; no garantiza por sí solo éxito del servidor.

## Cinco preguntas Flutter, contenedor y empaquetado

1. Web y APK son clientes del mismo contrato. No requieren un backend por plataforma; cambia configuración de URL/origen y empaquetado.
2. Docker sirve un build estático común y reproducible; flutter run sirve desarrollo local y hot reload. Una imagen de Flutter web no incluye un APK ejecutándose.
3. Meter .joblib en APK añade tamaño, expone lógica y dificulta actualizar. No equivale a una caché offline pública y versionada. El modelo se consulta por API.
4. 10.0.2.2 corresponde al emulador Android. El teléfono físico usa la IP LAN accesible de la computadora, el mismo WiFi y un puerto/firewall configurado por el propietario. No se desactiva el firewall globalmente.
5. El HTML y build/web son archivos estáticos servidos por nginx; Flutter requiere primero compilar Dart a los artefactos web. APK se instala y usa el runtime/integaciones Android; no se aloja detrás de nginx como aplicación web.

Fuentes: apartados de discusión de https://ealcaraz85.github.io/topicoswebmobil/ . Ejemplos ejecutables: `practicas_flutter/lib/laboratorio.dart`.
