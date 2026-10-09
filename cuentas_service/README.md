# Microservicio de Cuentas (Flask)

Migración de la app Django `Cuentas` a un microservicio REST independiente.
Expone registro, login, logout y perfil, y comparte la base de datos SQLite
(tabla `auth_user`) con el monolito Django, de modo que las cuentas son
interoperables en ambos sentidos (mismo hashing PBKDF2-SHA256 de Django).

## Arquitectura interna (mismas capas que el Django original)

| Capa          | Archivo          | Responsabilidad                                  |
|---------------|------------------|--------------------------------------------------|
| Rutas/HTTP    | `app.py`         | Orquesta: valida entrada, delega, serializa      |
| Validación    | `validators.py`  | Reglas de los serializers (correo, password, etc.) |
| Negocio       | `service.py`     | `AutenticacionService` + factory de usuario + JWT |
| Datos         | `repository.py`  | Acceso a `auth_user` (SQLite)                     |
| Seguridad     | `security.py`    | Hashing PBKDF2 compatible con Django             |
| Errores       | `errors.py`      | Errores de dominio -> respuestas JSON            |
| Config        | `config.py`      | Variables de entorno                             |

## API

Montada detrás de nginx en `/api/v2/cuentas/`.

| Método | Ruta        | Descripción                               | Códigos        |
|--------|-------------|-------------------------------------------|----------------|
| GET    | `/health`   | Healthcheck                               | 200            |
| POST   | `/registro` | Crea cuenta, devuelve usuario + token     | 201, 400, 409  |
| POST   | `/login`    | Autentica, devuelve usuario + token       | 200, 400, 401  |
| POST   | `/logout`   | Stateless; el cliente descarta el token   | 200            |
| GET    | `/perfil`   | Datos del usuario (header `Authorization: Bearer <token>`) | 200, 401 |

### Ejemplos

```bash
# Registro
curl -X POST http://localhost:8080/api/v2/cuentas/registro \
  -H "Content-Type: application/json" \
  -d '{"email":"juan@eafit.edu.co","password":"ClaveSegura123","password2":"ClaveSegura123","nombre":"Juan"}'

# Login
curl -X POST http://localhost:8080/api/v2/cuentas/login \
  -H "Content-Type: application/json" \
  -d '{"email":"juan@eafit.edu.co","password":"ClaveSegura123"}'

# Perfil
curl http://localhost:8080/api/v2/cuentas/perfil \
  -H "Authorization: Bearer <TOKEN>"
```

### Formato de error

Todas las respuestas de error usan el mismo contrato:

```json
{ "errores": { "email": ["Debes usar un correo institucional que termine en @eafit.edu.co."] } }
```

## Variables de entorno

| Variable                   | Default                            | Descripción                              |
|----------------------------|------------------------------------|------------------------------------------|
| `CUENTAS_DB_PATH`          | `/data/db.sqlite3`                 | Ruta a la BD SQLite compartida           |
| `CUENTAS_SECRET_KEY`       | (placeholder)                      | Clave para firmar los JWT                |
| `CUENTAS_JWT_EXPIRES_MIN`  | `60`                               | Minutos de vida del token                |
| `CUENTAS_DOMINIO`          | `@eafit.edu.co`                    | Dominio institucional permitido          |
| `CUENTAS_PBKDF2_ITERATIONS`| `1500000`                          | Debe coincidir con el default de Django  |

> Las iteraciones PBKDF2 deben ser las mismas que usa la versión de Django que
> creó los usuarios (Django 6.1 = 1 500 000). Si no coinciden, los hashes no se
> podrán verificar cruzados.

## Levantar todo (desde la raíz del repo)

```bash
docker compose up --build
# Gateway en http://localhost:8080
#   /                 -> Django (web, admin)
#   /api/v1/          -> Django
#   /api/v2/cuentas/  -> Flask
```
