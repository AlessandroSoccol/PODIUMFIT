# PodiumFit

Sistema web para la gestión de reservas de un centro deportivo: reserva de espacios (canchas, salas, etc.) y de indumentaria/equipamiento, con autenticación de usuarios y notificaciones multicanal de las operaciones realizadas.

Desarrollado con **Django** (+ **Django REST Framework**), aplicando una separación por capas inspirada en **Clean Architecture / arquitectura hexagonal ligera**, de modo que las reglas de negocio no dependan de Django ni de HTTP.

## Descripción del proyecto

PodiumFit está organizado como un **monolito modular por dominio**: cada app representa un límite de negocio claro (*bounded context*) y se comunica con las demás únicamente a través de interfaces explícitas (Factories/Services), nunca importando modelos de otras apps directamente.

### Apps principales

- **`PodiumFit/`** — Proyecto raíz de Django: `settings`, `urls`, `wsgi`/`asgi`.
- **`Cuentas/`** — Autenticación y gestión de usuarios (login/logout/registro), sobre el sistema estándar de Django (`authenticate`/`login`/`logout` y el modelo `User`).
- **`Reservas/`** — Núcleo del negocio: reserva de espacios deportivos y de indumentaria.
  - `domain/` — Reglas de negocio puras (sin Django ni HTTP):
    - `reglas.py` — Políticas centralizadas (duración máxima por espacio, límites de cantidad por tipo de indumentaria, regla de bloqueo global de reservas de espacio, etc.).
    - `builders.py` — Construcción paso a paso y validada de `ReservaEspacio` / `ReservaIndumentaria` (patrón *Builder*).
  - `infra/factories.py` — Adaptadores a infraestructura externa.
  - `models.py`, `views.py`, `services.py`, `serializers.py`, `factories.py`.
- **`Notificaciones/`** — Envío y persistencia de notificaciones a los usuarios.

### Principios de diseño

- **Views delgadas**: solo orquestan HTTP ↔ Service. Reciben el request, delegan la validación al `Serializer`, piden al `Factory` el `Service` ya ensamblado y renderizan el resultado. No contienen lógica de negocio.
- **Services (casos de uso)**: orquestan Builder, modelo y notificador; son reutilizables desde una vista HTML, una futura API o una tarea programada.
- **Domain**: reglas de negocio puras y testeables de forma aislada.
- **Serializers (DRF)**: desacoplan la forma de los datos de entrada/salida tanto del modelo como del HTML.
- **Factories**: ensamblan dependencias externas (por ejemplo, qué `Notificador` usar según la variable de entorno `NOTIFICADOR_MODE`), evitando que vistas y servicios instancien directamente sus dependencias.

### Flujo destacado: reserva de un espacio deportivo

Es el flujo más complejo del sistema:

1. **Validación en dos niveles**: el `Serializer` valida forma/tipo de datos (HTTP) y `domain/reglas.py` valida las reglas de negocio (duración máxima, bloqueo global).
2. **Bloqueo global**: mientras exista cualquier espacio reservado y vigente para un usuario, no puede reservar otro distinto (regla transversal, no un simple chequeo de disponibilidad puntual).
3. **Liberación automática**: antes de renderizar el formulario, `ReservaEspacioService.liberar_vencidas()` libera las reservas cuyo `fin <= ahora`, sin intervención del usuario.
4. **Notificación multicanal**: `NotificadorCompuesto` reenvía el mensaje a todas sus estrategias (web + email/consola) — patrón *Composite/Strategy* — sin que `ReservaEspacioService` conozca cuántos ni cuáles canales existen.

### Preparado para un futuro API Gateway

Aunque hoy se consume vía vistas basadas en templates, la arquitectura ya está pensada para exponerse detrás de un API Gateway con cambios mínimos:

- Django REST Framework ya está integrado (`rest_framework` en `INSTALLED_APPS`) y cada app tiene su `serializers.py`.
- Los mismos `Services` (por ejemplo `ReservaEspacioService.crear_reserva()`) pueden ser invocados tanto desde una vista HTML como desde un futuro endpoint REST, sin duplicar lógica.
- Cada app expone rutas versionables por prefijo (`/cuentas/`, `/notificaciones/`, `/` para Reservas), lo que facilita separar estas apps en microservicios el día de mañana.
- La autenticación por sesión de `Cuentas` puede convivir o migrar a JWT/token (soportado nativamente por DRF) sin afectar a `Reservas` ni `Notificaciones`.

## Tecnologías

- Python
- Django 6.1
- Django REST Framework 3.18.0
- asgiref 3.12.1
- sqlparse 0.6.0
- tzdata 2026.3

## Instalación y ejecución

> Los comandos abajo siguen el flujo estándar de un proyecto Django. Ajusta nombres de archivos/entorno si tu configuración real difiere (por ejemplo el nombre exacto de `requirements.txt` o del módulo de settings).

### 1. Clonar el repositorio

```bash
git clone https://github.com/AlessandroSoccol/PODIUMFIT.git
cd PODIUMFIT
```

### 2. Crear y activar un entorno virtual

```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crea un archivo `.env` (o exporta las variables en tu sistema) con al menos:

```bash
NOTIFICADOR_MODE=consola   # controla qué Notificador ensambla la Factory (p. ej. consola/email/mock)
```

Revisa `PodiumFit/settings.py` por si hay otras variables requeridas (clave secreta, base de datos, etc.).

### 5. Aplicar migraciones

```bash
python manage.py migrate
```

### 6. (Opcional) Crear un superusuario

```bash
python manage.py createsuperuser
```

### 7. Levantar el servidor de desarrollo

```bash
python manage.py runserver
```

La aplicación quedará disponible en `http://127.0.0.1:8000/`.

## Estructura del proyecto

```
PODIUMFIT/
├── PodiumFit/          # Proyecto raíz: settings, urls, wsgi/asgi
├── Cuentas/             # App: autenticación y gestión de usuarios
├── Reservas/            # App: núcleo del negocio (espacios e indumentaria)
│   ├── domain/          # Reglas de negocio puras
│   │   ├── reglas.py
│   │   └── builders.py
│   ├── infra/           # Adaptadores a infraestructura externa
│   │   └── factories.py
│   ├── models.py
│   ├── views.py
│   ├── services.py
│   ├── serializers.py
│   └── factories.py
└── Notificaciones/      # App: envío y persistencia de notificaciones
```
