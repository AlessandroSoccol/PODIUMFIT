from functools import wraps

from flask import Flask, g, jsonify, request

from config import Config
from errors import CredencialesInvalidas, ErrorDeApi
from repository import UsuarioRepository
from service import AutenticacionService
from validators import validar_login, validar_registro


def crear_app(config: Config | None = None) -> Flask:
    app = Flask(__name__)
    config = config or Config()
    app.config.from_object(config)

    repo = UsuarioRepository(config.DB_PATH)
    servicio = AutenticacionService(repo, config)

    @app.errorhandler(ErrorDeApi)
    def manejar_error_api(error: ErrorDeApi):
        return jsonify(error.to_dict()), error.status_code

    @app.errorhandler(404)
    def manejar_404(_error):
        return jsonify({"errores": {"detail": ["Recurso no encontrado."]}}), 404

    @app.errorhandler(405)
    def manejar_405(_error):
        return jsonify({"errores": {"detail": ["Método no permitido."]}}), 405

    @app.errorhandler(Exception)
    def manejar_inesperado(error):
        app.logger.exception("Error no controlado: %s", error)
        return jsonify({"errores": {"detail": ["Error interno del servidor."]}}), 500

    def _leer_json():
        if request.is_json:
            return request.get_json(silent=True) or {}
        if request.form:
            return request.form.to_dict()
        return {}

    def requiere_token(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            auth = request.headers.get("Authorization", "")
            if not auth.startswith("Bearer "):
                raise CredencialesInvalidas("Falta el token de autenticación.")
            token = auth[len("Bearer "):].strip()
            g.usuario = servicio.perfil_desde_token(token)
            return func(*args, **kwargs)

        return wrapper

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "service": "cuentas"}), 200

    @app.post("/registro")
    def registro():
        datos = validar_registro(_leer_json(), config.DOMINIO_PERMITIDO)
        resultado = servicio.registrar(
            email=datos["email"],
            password=datos["password"],
            nombre=datos["nombre"],
        )
        return jsonify(resultado), 201

    @app.post("/login")
    def login():
        datos = validar_login(_leer_json(), config.DOMINIO_PERMITIDO)
        resultado = servicio.autenticar(
            email=datos["email"], password=datos["password"]
        )
        return jsonify(resultado), 200

    @app.post("/logout")
    def logout():
        return jsonify({"ok": True}), 200

    @app.get("/perfil")
    @requiere_token
    def perfil():
        return jsonify({"usuario": g.usuario}), 200

    return app


app = crear_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
