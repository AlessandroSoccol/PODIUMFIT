from abc import ABC, abstractmethod
import requests

class ProveedorExternoInterface(ABC):
    @abstractmethod
    def obtener_datos(self) -> dict:
        pass

class AdaptadorAPI(ProveedorExternoInterface):
    def __init__(self, url_base):
        self.url_base = url_base

    def obtener_datos(self) -> dict:
        try:
            response = requests.get(f"{self.url_base}/endpoint")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return {"error": "Servicio no disponible"}
