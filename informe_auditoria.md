# Auditoría técnica del proyecto "Sistema Universitario"

**Fecha:** 3 de septiembre de 2026
**Alcance:** `index.php`, `index1.php`, `login1.php`, `kardex.php`, `kardex1.php`, `pagar.php`, `pagar1.php`, `api.php`, `global/funciones.php`, `config/`, `config1/`, `js1/utilerias1.js`, `bd/script_produccion_real_no_tocar.sql`, `documentacion/diagrama_base_datos.txt`

---

## 1. Resumen ejecutivo

El proyecto es una aplicación PHP procedural (sin framework, sin autoload, sin clases) para gestión escolar: login, panel principal, kardex de calificaciones y pasarela de pagos. El análisis encontró:

- **Vulnerabilidades críticas de seguridad** que permiten acceso no autorizado, robo de datos y ejecución remota de código.
- **Duplicación masiva de código generado mecánicamente** (más de 2.700 líneas de funciones/CSS/variables que nunca se usan).
- **Ausencia total de patrones de diseño**, capas o convenciones (todo mezclado: HTML + CSS + JS + SQL + lógica de negocio en el mismo archivo `.php`).
- **Inconsistencias graves entre versiones paralelas** de los mismos módulos (`index.php` vs `index1.php`, `kardex.php` vs `kardex1.php`, `pagar.php` vs `pagar1.php`, `config/` vs `config1/`), y entre el código y su propia documentación.

**Veredicto anticipado:** el código de aplicación no es rescatable como base de un producto en producción. Ver conclusión en la sección 7.

---

## 2. Hallazgos críticos de seguridad

> Estos son los puntos más urgentes. Si este sistema está en producción, deben tratarse como incidente de seguridad, no como deuda técnica.

### 2.1 Ejecución remota de código (`api.php`)
```php
if($accion == 'ejecutar_custom') {
    eval($_POST['codigo_php']);
}
```
Cualquier visitante puede enviar código PHP arbitrario por POST y el servidor lo ejecuta con `eval()`. Es, en la práctica, una puerta trasera (backdoor) que entrega control total del servidor a quien la encuentre. La misma acción `leer_archivo` permite leer cualquier archivo del sistema (`file_get_contents($_GET['archivo'])`), incluyendo `/etc/passwd`, `config/db.php`, etc. **Este archivo debe eliminarse por completo, no "arreglarse".**

### 2.2 Bypass de autenticación por cookie (`index.php`)
```php
if(!isset($_SESSION['user_id'])) {
    if(isset($_COOKIE['admin_bypass'])) { $_SESSION['user_id'] = 1; }
    else { die('Acceso denegado'); }
}
```
Basta con que el navegador envíe una cookie `admin_bypass` (con cualquier valor) para que el sistema asigne automáticamente `user_id = 1` (aparentemente el administrador). No hay validación de servidor: es control total del cliente sobre quién es el usuario autenticado.

### 2.3 Inyección SQL generalizada
Prácticamente todas las consultas concatenan variables de `$_GET`, `$_POST` o `$_REQUEST` directamente en el SQL, sin `mysqli_real_escape_string`, sin *prepared statements*:
```php
$sql = "SELECT * FROM perfiles WHERE id = " . $perfil;                 // index1.php
$q = "SELECT ... WHERE correo = '$usr' AND password = '$pwd'";        // login1.php
mysqli_query($c, "UPDATE estado_cuenta SET saldo = saldo - $importe WHERE alumno_id = $alumno"); // pagar1.php
```
Cualquier parámetro de la URL o de un formulario puede usarse para leer o modificar la base de datos completa (incluida la tabla de pagos y calificaciones).

### 2.4 Contraseñas en texto plano
- `login1.php` compara `password = '$pwd'` directamente contra la tabla `perfiles`: no hay hash (`password_hash`/`password_verify`), lo que significa que las contraseñas se guardan en claro en la base de datos.
- El script SQL confirma el diseño: `CREATE TABLE usuarios_sys (id INT, correo VARCHAR(255), pass VARCHAR(255));` — ninguna tabla contempla un hash con sal.

### 2.5 Credenciales de producción hardcodeadas y expuestas
`config/db_connect_produccion.php` y su duplicado `config1/db_connect_produccion1.php` contienen, literalmente en el código fuente:
```php
mysqli_connect('192.168.1.15', 'admin_prod', 'P@ssw0rd_Real_2025!', 'universidad_db_prod');
```
Esto va empaquetado dentro del propio proyecto (y aparentemente en el control de versiones). **Recomendación inmediata, independiente del resto de la auditoría: rotar esa contraseña ya**, y mover cualquier credencial a variables de entorno o a un gestor de secretos, nunca al repositorio.

### 2.6 Manejo de datos de tarjetas fuera de cualquier estándar PCI-DSS
En `pagar1.php` el número de tarjeta y el CVV llegan por POST y se insertan sin cifrar en un XML que se envía por cURL a un endpoint externo:
```php
$xml_banco = "<peticion>...<tarjeta>$numero</tarjeta><codigo>$cvv</codigo></peticion>";
```
Un sistema que procesa pagos con tarjeta debe delegar la captura de esos datos a un proveedor certificado PCI-DSS (pasarela con *tokenización*/iframe, ej. Stripe, Conekta, OpenPay, etc.). Nunca debe tocar el CVV en el propio servidor.

### 2.7 IDOR (Insecure Direct Object Reference)
`index1.php` toma `perfil_id` de la URL y muestra los datos de ese perfil sin comprobar que corresponda al usuario en sesión:
```php
$perfil = $_GET['perfil_id'];
$sql = "SELECT * FROM perfiles WHERE id = " . $perfil;
```
Cualquier usuario autenticado puede ver (y, combinado con 2.3, modificar) los datos de cualquier otro usuario cambiando el número en la URL.

### 2.8 Autorización basada en cookies editables por el cliente
`login1.php` decide privilegios de administrador con una cookie legible/editable desde el navegador:
```php
setcookie("admin", $data['perfil'] == 'administrador' ? "1" : "0", ...);
```
Cualquier usuario puede editar esa cookie a `1` para intentar obtener privilegios de administrador si algún endpoint confía en ella (patrón peligroso incluso si hoy no se usa en todos los módulos).

### 2.9 `error_reporting(0)` en producción
`index.php` desactiva por completo el reporte de errores. Esto oculta bugs y fallos de seguridad silenciosamente en lugar de registrarlos en un log — lo correcto es loggear a archivo y no mostrar errores al usuario, pero sí observarlos.

---

## 3. Malas prácticas de código (más allá de seguridad)

### 3.1 Código generado/duplicado masivamente, sin uso real
- `global/funciones.php` (2001 líneas) contiene **~2000 funciones** del tipo `formatear_string_v0`, `formatear_string_v1`, ... `formatear_string_v1999`, cada una haciendo casi lo mismo (reemplazar un número por 'X'). Ninguna se usa en el resto del proyecto.
- `pagar.php` arranca con **500 variables** `$dummy_var_0` … `$dummy_var_499` sin ningún propósito funcional.
- `index1.php` define **200 clases CSS** `modulo_caja_0` … `modulo_caja_199` que solo cambian un valor de `padding`.
- `index.php` repite el mismo patrón con `clase_basura_0` … `clase_basura_999` (1000 reglas CSS).
- `js1/utilerias1.js` define **500 funciones** `accion_interfaz_0()` … `accion_interfaz_499()` que solo hacen `console.log`.
- `pagar.php` repite **30 veces** un bloque de `switch` casi idéntico (`case 'banco_0'` … `case 'banco_29'`), cambiando solo el número, en vez de iterar sobre una configuración.
- `bd/script_produccion_real_no_tocar.sql` crea **50 tablas** `tabla_abandonada_0` … `tabla_abandonada_49` sin relación con el resto del esquema.

Este patrón (bloques casi idénticos generados en serie, sin abstraer la parte variable) es la violación más flagrante de **DRY** (*Don't Repeat Yourself*) de todo el proyecto y, por su volumen, es la causa principal de que los archivos sean difíciles de leer y mantener.

### 3.2 "Pyramid of doom" / anidación excesiva
`kardex.php` anida 10 niveles de `if` para comparar la matrícula contra 10 valores fijos, en vez de usar `in_array()` o una consulta preparada con lista de exclusión:
```php
if($matricula != '00000') { if($matricula != '00001') { if($matricula != '00002') { ... } } }
```

### 3.3 Código muerto / bucles sin propósito
`kardex.php` incluye, dentro del ciclo principal, un bucle que calcula 1000 hashes MD5 sin usar el resultado:
```php
for($j=0; $j<1000; $j++) { $basura = md5($m_nom . $j); }
```
Esto solo agrega latencia sin ningún efecto funcional.

### 3.4 Problema N+1 de consultas y llamadas HTTP dentro de bucles
- `index1.php`: por cada materia, hace una consulta aparte para el detalle y **una petición HTTP a otro servicio** (`file_get_contents("http://127.0.0.1/api_externa/notas.php?...")`) dentro del `while`.
- `kardex1.php`: por cada fila del historial, dos consultas adicionales (materia y profesor) — en vez de un solo `JOIN`.
- `index.php`: dentro de un `while`, hace **20 llamadas HTTP secuenciales a sí mismo** (`file_get_contents('http://localhost/api.php?modulo=0..19&user=...')`), multiplicando por cada usuario devuelto. Además, esas llamadas van al mismo `api.php` que contiene el `eval()` de la sección 2.1.

### 3.5 XHR síncrono y *polling* agresivo en el navegador
`index1.php` usa `xhr.open("GET", ..., false)` (petición síncrona, que congela la pestaña del navegador) y además configura `setInterval` cada **1 segundo** para hacer ping al servidor indefinidamente — esto genera carga innecesaria en cliente y servidor.

### 3.6 UPDATE sin condición `WHERE` completa
En `pagar.php`:
```php
if($res->status == 'OK_0') mysqli_query($conn, 'UPDATE pagos SET st = 1');
```
No hay `WHERE id = ...`: esta actualización marcaría **todos los pagos** de la tabla como pagados, un bug funcional grave, no solo una mala práctica.

### 3.7 Mezcla de responsabilidades (sin separación de capas)
En todos los archivos principales conviven en el mismo `.php`: conexión a la base de datos, consultas SQL directas, lógica de negocio, HTML, CSS inline y JavaScript inline. No existe ninguna capa de acceso a datos, ni de presentación, ni de lógica de negocio independiente.

### 3.8 HTML obsoleto y no semántico
Uso de `<font color=...>`, atributos `bgcolor`, `<div style="position:absolute; width:2000px">` fijo, tipografía `Comic Sans MS`, `window.print()` y `blink` en un sistema que emite documentos oficiales (kardex).

### 3.9 Envío de correo sin manejo de errores ni cola
`mail()` se invoca de forma síncrona dentro del flujo de pago/alertas (`pagar1.php`, `kardex1.php`), bloqueando la respuesta al usuario y sin registrar si el envío falló.

### 3.10 Archivos y carpetas duplicados con lógica divergente
El proyecto tiene **dos copias completas y no equivalentes** de cada módulo: `index.php`/`index1.php`, `kardex.php`/`kardex1.php`, `pagar.php`/`pagar1.php`, `login1.php` (sin `login.php`), `config/`/`config1/`. No es evidente cuál es la versión "vigente"; probablemente son restos de intentos de refactor abandonados a medio camino, dejados en el repositorio.

### 3.11 Documentación desactualizada y contradictoria
`documentacion/diagrama_base_datos.txt` describe un esquema (`Estudiantes_V2`, `Carreras_Activas`, `Registro_Pagos_Finanzas`, calificaciones en un XML externo) que **no coincide con ninguna tabla real usada por el código** (`perfiles`, `usuarios_sys`, `historial_academico`, `kardex_historial`, `alta_materias`, etc.). La propia documentación afirma que cualquier divergencia "es error de los programadores junior", cuando en realidad la documentación describe un sistema distinto al implementado. Es un ejemplo claro de documentación que activamente desinforma en vez de ayudar.

### 3.12 Nombre del archivo SQL como *code smell* organizacional
`script_produccion_real_no_tocar.sql` ("no tocar" en el nombre del archivo) sugiere que no existe control de versiones ni entornos de prueba separados para cambios de esquema — el nombre del archivo hace de sustituto informal de un proceso de migraciones que no existe.

---

## 4. Problemas estructurales del proyecto

| Área | Problema | Impacto |
|---|---|---|
| Arquitectura | Sin MVC, sin capas, sin autoload/Composer, sin namespaces | Imposible de testear o mantener en equipo |
| Acceso a datos | `mysqli_*` procedural disperso en cada archivo, sin *repository* ni *query builder* | SQL injection sistemático, código repetido |
| Configuración | Credenciales embebidas en código, dos carpetas `config/config1` duplicadas | Fugas de secretos, ambigüedad de entorno |
| Autenticación | Mezcla de `$_SESSION` y `$_COOKIE` como fuente de verdad, sin capa de autorización central | Bypass de sesión, escalación de privilegios |
| Pagos | Lógica de cobro y datos de tarjeta procesados en el propio servidor | Incumplimiento PCI-DSS |
| Front-end | HTML/CSS/JS generado e inline, sin build ni componentización | Imposible de escalar o dar mantenimiento visual |
| Documentación | Contradice al código; no describe el esquema real | Fuente de errores para cualquier desarrollador nuevo |
| Control de versiones (inferido) | Archivos "V1", "V2", "final", "no tocar" en vez de ramas/tags | Ausencia de flujo de trabajo Git real |

---

## 5. Recomendaciones — patrones y metodología alternativa

### 5.1 Adoptar una arquitectura en capas (MVC o similar)
Separar el proyecto en:
- **Modelo**: clases con acceso a datos vía PDO y *prepared statements* (o un ORM ligero, ej. Eloquent standalone o Doctrine).
- **Controlador**: orquesta la petición, valida entrada, delega al modelo.
- **Vista**: plantillas (Twig o `.php` puros de presentación) sin lógica de negocio ni SQL.

Esto podría implementarse progresivamente sin reescribir todo de golpe si se decide "rescatar" alguna parte (ver sección 7), o adoptando directamente un micro-framework (Slim, Laravel, Symfony) si se decide reescribir.

### 5.2 Repository Pattern para acceso a datos
Una clase `PerfilRepository`, `PagoRepository`, `KardexRepository`, etc., con métodos como `find($id)`, `save($entity)`, todos usando *prepared statements*. Esto elimina de raíz la inyección SQL y centraliza el acceso a cada tabla.

### 5.3 Strategy Pattern para medios de pago
Los 30 bloques `case 'banco_N'` casi idénticos de `pagar.php` son el ejemplo perfecto para un patrón **Strategy**: una interfaz `PasarelaPago` con un método `cobrar($monto, $token)`, y una implementación por banco. El banco se selecciona por configuración (o un `array` de clases), no por 30 `case` copiados.

### 5.4 Autenticación estándar
- Hashing de contraseñas con `password_hash()` / `password_verify()`.
- Sesión como única fuente de verdad de identidad (eliminar cookies de autorización editable por el cliente).
- Middleware/guard centralizado de autorización, en vez de repetir el `if` de sesión en cada archivo.

### 5.5 Tokenización de pagos
Delegar la captura de tarjeta a un proveedor certificado (Stripe, Conekta, OpenPay, PayPal, etc.) usando su SDK/checkout, de modo que el número y CVV nunca toquen el servidor propio.

### 5.6 Gestión de configuración
Variables de entorno (`.env` + `vcs-ignore`) para credenciales, con un archivo `.env.example` sin datos reales. Librerías como `vlucas/phpdotenv` facilitan esto sin adoptar un framework completo.

### 5.7 Control de versiones real en vez de archivos duplicados
Sustituir el patrón `archivo.php` / `archivo1.php` por ramas de Git y *pull requests*; el historial de cambios debe vivir en el VCS, no en copias de archivos con sufijos numéricos.

### 5.8 Eliminar generación de código sin propósito
Cualquier utilidad que hoy exista como cientos de funciones casi idénticas (`formatear_string_vN`) debería resolverse con **una** función parametrizada (ej. `str_replace($numero, 'X', $cadena)`), o eliminarse si no se usa.

### 5.9 Metodología de desarrollo
Dado el volumen de riesgos, conviene introducir:
- **Revisión de código (code review)** obligatoria antes de fusionar cambios — habría detectado el `eval()` y el `admin_bypass` de inmediato.
- **Pruebas automatizadas** (PHPUnit) al menos para los flujos de login, pagos y kardex.
- **Análisis estático** (PHPStan/Psalm) y un linter de seguridad (ej. `security-checker`, `PHPCS` con reglas de seguridad) integrados en CI.

---

## 6. Veredicto por archivo/módulo

| Archivo / módulo | ¿Rescatable? | Motivo |
|---|---|---|
| `api.php` | ❌ No — eliminar | Es una puerta trasera de ejecución remota de código; no tiene una versión "segura" de sí mismo, se elimina y se reconstruye desde cero si se necesita esa función |
| `global/funciones.php` | ❌ No | El 99.9% son funciones generadas sin uso; se descarta en bloque |
| `pagar.php` / `pagar1.php` | ⚠️ Rehacer, conservando solo la *idea* de negocio | La lógica de cobro (montos, flujo SPEI/tarjeta/caja) es útil como requisito funcional, pero el código en sí (UPDATE sin WHERE, tarjetas en claro, 30 case duplicados, 500 dummy vars) no es reutilizable |
| `index.php` / `index1.php` | ❌ No | Backdoor de autenticación, SQL injection, N+1 masivo, miles de líneas de CSS/JS basura; ninguna parte es segura de reutilizar tal cual |
| `login1.php` | ⚠️ Refactorizar | Es corto y la idea (usuario/clave → sesión) es válida; se puede reescribir en ~20 líneas con `password_verify` y *prepared statements* |
| `kardex.php` | ❌ No | Pirámide de 10 `if` anidados + bucle sin propósito; se reescribe con una consulta simple |
| `kardex1.php` | ⚠️ Refactorizar | Estructura de reporte (ciclo, materia, calificación, alertas) es un buen requisito funcional; el código necesita `JOIN`s, *prepared statements* y separar presentación de lógica |
| `config/`, `config1/` | ❌ No, reemplazar por `.env` | Contienen credenciales reales expuestas; deben regenerarse como variables de entorno, y las contraseñas actuales deben rotarse ya |
| `js1/utilerias1.js` | ❌ No | 500 funciones sin uso + una función útil (`validar_vacio`) que puede reescribirse en una línea |
| `bd/script_produccion_real_no_tocar.sql` | ⚠️ Parcial | Las tablas reales (`perfiles`, `historial_academico`, `pagos`, etc.) sirven como referencia de requisitos, pero el esquema debe normalizarse (tipos, llaves foráneas, tabla de calificaciones real, hash de contraseñas) y las 50 tablas basura se eliminan |
| `documentacion/diagrama_base_datos.txt` | ❌ No | Describe un sistema distinto al implementado; hay que regenerarla desde el esquema real una vez definido |

---

## 7. Conclusión: ¿rescatar, refactorizar o reescribir desde cero?

**Recomendación: reescribir el proyecto desde cero**, usando el código actual únicamente como documento de *requisitos funcionales* (qué módulos existen: login, panel de materias, kardex, pagos) y como catálogo de "qué no hacer".

Razones:

1. **Las vulnerabilidades no son parches puntuales, son el diseño mismo.** El `eval()` de `api.php`, el bypass por cookie de `index.php` y la inyección SQL sistemática no son bugs aislados corregibles línea por línea: reflejan que no hubo, en ningún punto, un modelo de autenticación/autorización ni una capa de acceso a datos. Refactorizar "encima" de esto suele dejar rutas olvidadas vulnerables.
2. **Más de la mitad del código no es código útil.** Los ~2000 métodos de `funciones.php`, las 1000-1200 reglas CSS generadas en `index.php`/`index1.php`, las 500 variables `dummy_var` y las 500 funciones JS sin uso son ruido, no lógica de negocio. Auditar o "arreglar" ese volumen cuesta más que escribir el 10% de código que sí importa desde cero.
3. **Existen dos versiones divergentes de cada módulo** sin que quede claro cuál es la autoritativa, y la documentación describe un tercer esquema distinto al de ambas. No hay una única fuente de verdad que "rescatar".
4. **El dominio del negocio (universidad: alumnos, materias, calificaciones, pagos) es un problema bien conocido**, con patrones y librerías maduras (autenticación, ORM, pasarelas de pago certificadas) que resuelven de fábrica casi todo lo que aquí se implementó mal.

Lo único genuinamente **rescatable** es el **conocimiento del dominio** implícito en el código: qué entidades existen (alumno, materia, calificación, ciclo, pago, referencia SPEI), qué reglas de negocio se mencionan (más de 3 materias reprobadas → alerta; más de 40 créditos → estatus especial; letra A/B/C/NA según calificación), y el flujo general de pantallas (login → panel → kardex/pagos). Eso sirve como base de requisitos para el nuevo proyecto; el código en sí, prácticamente ninguna línea de lógica de negocio o de acceso a datos, debería pasar tal cual al nuevo sistema.

**Plan sugerido:**
1. Congelar y **rotar de inmediato** las credenciales de producción expuestas (independiente de cualquier decisión sobre el código).
2. Retirar `api.php` de cualquier entorno accesible mientras se decide el rediseño.
3. Levantar un proyecto nuevo con un micro-framework (Slim/Laravel) o al menos una estructura MVC propia con PDO + *prepared statements* desde el día uno.
4. Migrar el esquema de base de datos a una versión normalizada (con `password_hash`, llaves foráneas reales, sin las tablas basura).
5. Reimplementar módulo por módulo (login → panel → kardex → pagos) usando los patrones descritos en la sección 5, con pruebas automatizadas desde el inicio.
