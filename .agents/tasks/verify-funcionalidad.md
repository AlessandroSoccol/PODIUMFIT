# Reporte de verificación de FUNCIONALIDAD — PodiumFit

Rama: `main` · Commit base: `96bf397` · Verificación realizada sin worktree, directamente en el repo.
Intérprete usado: `venv\Scripts\python.exe` (Windows / PowerShell).

Alcance: solo FUNCIONALIDAD (que arranque, no rompa, responda con los códigos/flujos esperados).
No se hicieron refactors de estilo, renombres ni reorganizaciones.

---

## Resumen ejecutivo

| Parte | Estado | Comentario |
|---|---|---|
| Django — Cuentas | OK | Registro/login/logout funcionan; validación de dominio institucional OK. |
| Django — Notificaciones | OK | No leídas y marcar leída (200 / 404) OK. |
| Django — Reservas | OK | Reservar/liberar espacio, reservar/devolver indumentaria y liberación por vencimiento OK. |
| Microservicio Flask (cuentas_service) | OK | Rutas /health, /registro, /login, /logout, /perfil con códigos correctos; hashing interoperable con Django en ambos sentidos. |
| Microservicio Flask (datos_service) | OK | /health y /datos responden 200 (vía gateway). |
| Docker (compose + build + stack + nginx) | OK (tras correcciones) | Docker SÍ estaba disponible. Se detectaron y corrigieron 2 fallos de arranque. |

Se corrigieron **3 problemas de funcionalidad** (2 que impedían arrancar y 1 que impedía toda operación de Django vía `manage.py`).

---

## 1. Django (monolito)

### 1.1 Problema encontrado y corregido — `celery` no instalado (bloqueaba TODO `manage.py`)

- Síntoma: cualquier comando (`manage.py check`, `migrate`, `test`, `runserver`) fallaba con
  `ModuleNotFoundError: No module named 'celery'`. La causa: `PodiumFit/__init__.py` importa
  `from .celery import app as celery_app` al cargar el paquete de settings, y `celery`/`redis`
  (declarados en `requirements.txt`) no estaban instalados en el `venv`.
- Corrección: se instalaron las dependencias ya declaradas en `requirements.txt`
  (`celery==5.4.0`, `redis`, `requests==2.32.3`). No se inventó ninguna dependencia nueva.
- Confirmación: tras instalar, `manage.py check` pasa sin incidencias.

### 1.2 Comprobaciones de salud

```
venv\Scripts\python.exe manage.py check
  -> System check identified no issues (0 silenced).

venv\Scripts\python.exe manage.py makemigrations --check --dry-run
  -> No changes detected

venv\Scripts\python.exe manage.py showmigrations
  -> Todas aplicadas [X] (Notificaciones, Reservas 0001-0003, auth, admin, contenttypes, sessions).
     Cuentas: (no migrations) — usa el modelo User estándar de Django, es correcto.
```

### 1.3 Servidor de desarrollo

Arranca correctamente. `GET /cuentas/login/` devolvió HTTP 200.
Nota (no es fallo): al arrancar aparece un `RuntimeWarning: Accessing the database during app
initialization` originado por `Cuentas/apps.py` → `ready()` que borra sesiones al iniciar. Está
envuelto en `try/except (OperationalError, ProgrammingError)` y funciona; es comportamiento
intencional existente, no se modificó.

### 1.4 Suite de tests existente

```
venv\Scripts\python.exe manage.py test
  -> Ran 6 tests ... OK   (Reservas: reglas de límite de indumentaria/builder)
```

Notas:
- Las apps Cuentas y Notificaciones no traen tests propios (los archivos `tests.py` están vacíos).
- En una de las primeras corridas, `manage.py test` (descubrimiento en todo el árbol) falló una vez
  con `OSError: [Errno 22] Invalid argument` al leer un módulo; **no se reprodujo** en corridas
  posteriores (transitorio del sistema de archivos OneDrive/sincronización en la nube). Nombrando
  las apps explícitamente (`test Cuentas Notificaciones Reservas core`) siempre pasó.

### 1.5 Flujos principales (verificados con Django test client sobre BD de test)

Se creó un módulo de verificación temporal (`_verify_flows.py`, **ya eliminado**) con
`django.test.TestCase` (BD de test en memoria, sin tocar la BD real). Resultado: **8/8 OK**.

- Cuentas: registro (302, usuario creado), logout (302), login correcto (302),
  login incorrecto (200 re-render), registro con dominio no institucional rechazado (200, sin crear usuario).
- Notificaciones: no leídas (200, cuenta correcta), marcar leída (200 + `ok:true`, marca en BD),
  marcar inexistente → 404.
- Reservas espacio: reservar (302, `cantidad_disponible` 1→0), liberar (302, vuelve a 1),
  liberación por vencimiento (GET dispara `liberar_vencidas()`; reserva vencida pasa a inactiva y libera stock).
- Reservas indumentaria: reservar (302, stock 1→0), devolver (302, vuelve a 1),
  devolución por vencimiento (`devolver_vencidas()` reintegra stock).

---

## 2. Microservicio Flask — `cuentas_service`

Verificado con el **test client de Flask** sobre una **BD SQLite temporal** que replica la tabla
`auth_user` (no se ensució la BD real). Script temporal `_verify_flask.py` **ya eliminado**.
Resultado: **todas las comprobaciones OK**.

Códigos de respuesta confirmados:

| Ruta | Caso | Código |
|---|---|---|
| GET /health | — | 200 |
| POST /registro | válido | 201 (devuelve token) |
| POST /registro | email duplicado | 409 |
| POST /registro | dominio inválido / password corta | 400 |
| POST /login | correcto | 200 (devuelve token) |
| POST /login | password incorrecta | 401 |
| POST /login | datos vacíos | 400 |
| POST /logout | — | 200 |
| GET /perfil | sin token | 401 |
| GET /perfil | token válido | 200 |
| GET /perfil | token inválido | 401 |

### Interoperabilidad de hashing con Django (ambos sentidos) — OK

- Django 6.1 usa PBKDF2 con **1.500.000 iteraciones** (confirmado:
  `PBKDF2PasswordHasher.iterations == 1500000`), exactamente lo que replica `cuentas_service`.
- Flask → Django: hash generado por `security.hacer_hash` (prefijo `pbkdf2_sha256$1500000$...`)
  verificado correctamente por `django.contrib.auth.hashers.check_password` (y rechaza password errónea).
- Django → Flask: hash generado por `django...make_password` verificado por
  `security.verificar_password` y login exitoso (200) en el microservicio.

---

## 3. Docker (compose + imágenes + stack + gateway nginx)

**Nota operativa de la tarea:** se indicaba que el daemon de Docker podría estar apagado.
En esta ejecución **Docker SÍ estaba disponible** (`docker version` devolvió sección Server;
`docker info` → ServerVersion 29.9.2), por lo que se verificó la pila completa.

### 3.1 Validación de configuración

```
docker compose --env-file .env.docker config --quiet   -> exit 0 (config válida)
```

### 3.2 Build de imágenes

```
docker compose --env-file .env.docker build
  -> Built: podiumfit-django, podiumfit-cuentas, podiumfit-datos, podiumfit-celery_worker  (exit 0)
```

### 3.3 Problemas encontrados al levantar la pila y correcciones

**Fallo A — `celery_worker` en crash-loop (no arrancaba).**
- Síntoma en logs: `kombu.exceptions.VersionMismatch: Redis transport requires redis-py
  versions 6.1.0 or later. You have 5.0.8`. El `redis==5.0.8` fijado en `requirements.txt` es
  incompatible con la versión de `celery`/`kombu` del proyecto, y el worker no podía conectar al broker.
- Corrección (cambio de versión justificado por incompatibilidad que impide arrancar):
  `requirements.txt` → `redis==5.0.8` cambiado a `redis==6.1.1` (primera versión compatible con el
  requisito `>=6.1.0` de kombu). También se actualizó el `venv` local a `redis==6.1.1`.
- Confirmación: tras reconstruir y levantar en frío, los logs muestran
  `celery@... ready.` y el contenedor queda `Up` de forma estable.

**Fallo B — `nginx` en crash-loop al arranque en frío.**
- Síntoma en logs: `[emerg] host not found in upstream "datos:5000"`. nginx con bloques
  `upstream { server datos:5000; }` resuelve todos los hostnames **una sola vez al iniciar**;
  si un backend aún no está registrado en el DNS de la red Docker en ese instante, nginx aborta
  y el `restart: unless-stopped` lo deja reiniciándose (condición de carrera de arranque).
- Corrección (sin cambiar el enrutamiento visible): se reescribió `nginx.conf` para usar el
  **resolver DNS embebido de Docker (`127.0.0.11`)** con `proxy_pass` basado en variables, de modo
  que los upstreams se resuelvan **en tiempo de petición** (perezosamente) y no al arrancar. Se
  preservaron exactamente las mismas rutas y el mismo despojo de prefijo:
  - `/api/v2/cuentas/` → `http://cuentas:5000/` (quita el prefijo, vía `rewrite`)
  - `/api/v2/datos/`   → `http://datos:5000/`   (quita el prefijo, vía `rewrite`)
  - `/api/v1/`         → `http://django:8000`   (sin quitar prefijo)
  - `/`                → `http://django:8000`
- Confirmación: tras `down` + `up -d` en frío, nginx queda `Up` sin reinicios y sin el `[emerg]`.

### 3.4 Pruebas a través del gateway nginx (http://localhost:8080) — tras correcciones

```
GET  /api/v2/cuentas/health   -> 200
GET  /api/v2/datos/health     -> 200
GET  /api/v2/datos/datos      -> 200
GET  /cuentas/login/          -> 200
POST /api/v2/cuentas/registro -> 201
POST /api/v2/cuentas/login    -> 200  (token válido)
GET  /api/v2/cuentas/perfil (Bearer token) -> 200
GET  /api/v2/cuentas/perfil (sin token)    -> 401
```

### 3.5 Interop a través del gateway: usuario creado por Flask inicia sesión en Django — OK

- Se registró un usuario vía `POST /api/v2/cuentas/registro` (Flask) y luego se hizo login en
  `/cuentas/login/` (Django, con CSRF + cookies). Resultado: **302 → Location `/`** (éxito).
- Control negativo: mismo usuario con password incorrecta en Django → **200** (re-render, rechazado).

Esto confirma que ambos servicios comparten `auth_user` en `db.sqlite3` y que el hashing es
interoperable también end-to-end a través del gateway.

---

## Correcciones aplicadas (archivos tocados)

1. `requirements.txt`: `redis==5.0.8` → `redis==6.1.1` (incompatibilidad con kombu/celery que
   impedía arrancar el worker de Celery).
2. `nginx.conf`: migrado de `upstream` estáticos a resolución DNS en tiempo de petición con el
   resolver de Docker (`127.0.0.11`), evitando el crash de arranque por carrera de DNS. Mismo
   enrutamiento y mismos prefijos que antes.
3. Dependencias faltantes instaladas en el `venv` según `requirements.txt` (`celery`, `redis`,
   `requests`). No es cambio de código; corrige que `manage.py` ni siquiera arrancaba.

## Limpieza realizada

- Scripts/módulos temporales de verificación eliminados: `_verify_flows.py`, `_verify_flask.py`,
  `_cleanup_testusers.py`.
- Usuarios de prueba creados en la BD real durante las pruebas por el gateway Docker: eliminados
  (5 usuarios con prefijos `docker/xdock/ydock/final/flog`). Usuarios reales intactos.
- Artefactos `__pycache__/*.pyc` generados por las corridas: eliminados (solo los no rastreados).
- Pila Docker detenida (`docker compose down`).
- No se hicieron commits ni push. No se tocó el `.env` de PowerShell de la raíz.

## No verificable / pendiente

- Nada quedó como "no verificable": Docker estaba disponible y se probó la pila completa.
- `db.sqlite3` aparece como modificado en git por efecto de la corrida Docker (borrado de sesiones
  al arranque de Django y escritura/borrado de usuarios de prueba). No se commitea. Los datos de
  usuarios reales siguen presentes.
