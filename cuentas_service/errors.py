class ErrorDeApi(Exception):
    status_code = 400

    def __init__(self, mensaje=None, *, campo=None, errores=None, status_code=None):
        super().__init__(mensaje or "Solicitud inválida.")
        self.mensaje = mensaje or "Solicitud inválida."
        if status_code is not None:
            self.status_code = status_code
        if errores is not None:
            self.errores = errores
        elif campo is not None:
            self.errores = {campo: [self.mensaje]}
        else:
            self.errores = {"detail": [self.mensaje]}

    def to_dict(self):
        return {"errores": self.errores}


class ErrorDeValidacion(ErrorDeApi):
    status_code = 400


class CredencialesInvalidas(ErrorDeApi):
    status_code = 401


class ConflictoDeRecurso(ErrorDeApi):
    status_code = 409
