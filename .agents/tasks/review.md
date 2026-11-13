# Revisión de FUNCIONALIDAD — PodiumFit

Veredicto: **APPROVED**

## Alcance revisado
Revisión del diff no commiteado, del reporte entregable (`verify-funcionalidad.md`) y de los
archivos fuente relevantes. No se re-ejecutaron las suites; se juzgó a partir del diff, el reporte
y los resultados registrados, con spot-checks puntuales de código y estado del repo.

## Evidencia verificada

### Cambios en el diff (todos dentro del alcance de FUNCIONALIDAD)
- `requirements.txt`: `redis==5.0.8` → `redis==6.1.1`. Único cambio de versión de dependencia.
  Justificado por el reporte como incompatibilidad que impide arrancar (`kombu`/`celery` exige
  redis-py >= 6.1.0; el worker de Celery entraba en crash-loop con `VersionMismatch`). Entra en la
  excepción permitida.
- `nginx.conf`: migración de `upstream` estáticos a `resolver 127.0.0.11` con `proxy_pass` basado
  en variables y `rewrite` para despojar prefijo. Verifiqué equivalencia de enrutamiento:
  - `/api/v2/cuentas/` → `rewrite ^/api/v2/cuentas/(.*)$ /$1 break` + `proxy_pass http://$cuentas_backend:5000`
    reproduce el stripping de prefijo que antes hacía `proxy_pass http://cuentas_backend/`.
  - `/api/v2/datos/` → mismo patrón, equivalente.
  - `/api/v1/` y `/` → `proxy_pass http://$django_backend:8000` (sin stripping), equivalente al
    `proxy_pass http://django_backend` original.
  Los hostnames (`cuentas`, `datos`, `django`) coinciden con los nombres de servicio de
  `docker-compose.yml`. Es una corrección funcional (carrera de DNS al arranque), no un refactor de estilo.
- `db.sqlite3`: modificado como efecto colateral de las corridas (borrado de sesiones al arranque de
  Django y usuarios de prueba). No se commitea; es consistente con lo documentado.

### Restricciones de la tarea
- `.env` de PowerShell de la raíz: NO tocado (`LastWriteTime` del 2/09, previo al trabajo; ausente del
  `git status`). `.env.docker` tampoco aparece modificado.
- Sin commits ni push: `git log` sigue en `96bf397`; cambios solo en working tree.
- Sin archivos temporales/scripts de verificación en el repo: `git status --untracked-files=all` solo
  muestra `.agents/tasks/verify-funcionalidad.md`. Búsqueda de `_verify_flows.py`, `_verify_flask.py`,
  `_cleanup_testusers.py` no encontró archivos; las únicas coincidencias de texto están dentro del
  propio reporte documentando su eliminación.
- Sin refactors de estilo, renombres ni reorganizaciones en el diff.

### Cobertura del reporte
- Django: las 3 apps (Cuentas, Notificaciones, Reservas) cubiertas con `check`, `makemigrations
  --check`, `showmigrations`, arranque de servidor y 8/8 flujos principales (incluida liberación por
  vencimiento de espacio e indumentaria).
- Flask (`cuentas_service`): `/health`, `/registro`, `/login`, `/logout`, `/perfil` con los códigos
  201/200/400/401/409/404 y hashing interoperable con Django en ambos sentidos. Confirmé que
  `security.py` implementa el formato `pbkdf2_sha256$<iter>$<salt>$<hash>` compatible con Django.
- Docker: estaba disponible y se verificó config, build, stack y gateway nginx en `localhost:8080`.
  No quedó nada marcado como "no verificable".

### Spot-checks de soporte
- `PodiumFit/__init__.py` importa `from .celery import app as celery_app` al cargar el paquete, lo que
  confirma la causa reportada de que la falta de `celery` bloqueaba todo `manage.py`.
- `PodiumFit/celery.py` existe, por lo que la importación resuelve.

## Hallazgos
Ninguno. No se detectaron bloqueantes de correctitud, seguridad ni de datos introducidos por el
cambio. Los cambios se limitan a funcionalidad, dentro del alcance aprobado y respetando las reglas.
